// The picture: node render/video.mjs <city> [--fps 24] [--workers N] [--from s] [--to s] [--q 'k=v'] [--out file] [--size 1920x1080]
// (adapted from lemo-opuscar core/render/video.mjs, MIT; see NOTICE). Default out: cities/<city>/build/video/video.mp4; workers:
// this machine's `workers` (local/config.json). Each worker is its own browser over its share of the frames, its JPEG screenshots
// piped to ffmpeg; the shares are joined losslessly. --from/--to render a stretch only (a test). The render runs at nice 10 so the
// desktop stays usable. One render per --out: <out>.lock holds the pid (a lock whose pid is gone, or untouched for 12 h, is taken
// over); the segments sit in a hidden folder beside --out, removed when the render ends, fails or is stopped.
import fs from 'fs'; import os from 'os'; import path from 'path'; import { spawn, execFileSync } from 'child_process';
import { openFilm, closeServer, takeSize } from './page.mjs';
import { local, buildDir } from './local.mjs';

const args = process.argv.slice(2), { w: W, h: H } = takeSize(args), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const city = args[0];
if (!city || city.startsWith('--')) { console.error('usage: node render/video.mjs <city> [--fps 24] [--workers N] [--from s] [--to s] [--q k=v] [--out file] [--size WxH]'); process.exit(2); }
const FPS = +opt('--fps', 24), WK = +opt('--workers', local('workers')), Q = opt('--q', ''), FROM = opt('--from', null), TO = opt('--to', null);
if (!(FPS > 0) || !Number.isInteger(WK) || WK < 1) { console.error('bad --fps / --workers: fps must be > 0, workers an integer >= 1'); process.exit(2); }
try { os.setPriority(10); } catch {}
const out = path.resolve(opt('--out', buildDir(city, 'video', 'video.mp4')));
const outDir = path.dirname(out), base = path.basename(out, path.extname(out));
fs.mkdirSync(outDir, { recursive: true });

// one render writes a given --out
const alive = pid => { try { process.kill(pid, 0); return true; } catch (e) { return e.code === 'EPERM'; } };
const lock = out + '.lock', LOCK_MAX_AGE = 12 * 3600 * 1000;
try { fs.writeFileSync(lock, String(process.pid), { flag: 'wx' }); } catch {
  const other = Number(fs.readFileSync(lock, 'utf8')), age = Date.now() - fs.statSync(lock).mtimeMs;
  if (Number.isInteger(other) && other > 0 && alive(other) && age < LOCK_MAX_AGE) {
    console.error(`another render (pid ${other}) is already writing ${out}. Give this one its own --out.\n` +
      `If no render is running (a crashed one can leave its lock behind), delete ${lock} and run this again.`); process.exit(2);
  }
  fs.writeFileSync(lock, String(process.pid));
}
setInterval(() => { try { const n = new Date(); fs.utimesSync(lock, n, n); } catch {} }, 10 * 60 * 1000).unref();
for (const n of fs.readdirSync(outDir)) if (n.startsWith(`.${base}_segs-`)) {   // segments a crashed render left behind
  try { const p = Number(fs.readFileSync(path.join(outDir, n, 'pid'), 'utf8')); if (!alive(p)) fs.rmSync(path.join(outDir, n), { recursive: true, force: true }); } catch {}
}
let segDir = null, cleaned = false; const procs = new Set();   // running ffmpegs: stopped before their folder goes
const cleanup = () => { if (cleaned) return; cleaned = true; for (const p of procs) p.kill('SIGKILL'); if (segDir) fs.rmSync(segDir, { recursive: true, force: true }); try { fs.unlinkSync(lock); } catch {} };
process.on('exit', cleanup);
for (const sig of ['SIGINT', 'SIGTERM']) process.on(sig, () => { cleanup(); process.exit(128 + (sig === 'SIGINT' ? 2 : 15)); });
const fail = msg => { console.error(msg); cleanup(); process.exit(1); };

segDir = fs.mkdtempSync(path.join(outDir, `.${base}_segs-`)); fs.writeFileSync(path.join(segDir, 'pid'), String(process.pid));
const probe = await openFilm(city, { w: W, h: H, q: Q }); const DUR = await probe.page.evaluate(() => window.DUR); await probe.browser.close();
if (!(DUR > 0)) fail(`window.DUR must be a positive number of seconds (got ${DUR})`);
const F0 = FROM == null ? 0 : Math.max(0, Math.round(+FROM * FPS)), F1 = Math.min(Math.round(DUR * FPS), TO == null ? Infinity : Math.round(+TO * FPS));
if (!(F1 > F0)) fail(`nothing to render: frames ${F0}-${F1}`);
const TOTAL = F1 - F0, per = Math.ceil(TOTAL / WK), t0 = Date.now();
try { await Promise.all([...Array(WK)].map(async (_, w) => {
  const a = F0 + w * per, b = Math.min(F1, a + per); if (a >= b) return;
  const { browser, page } = await openFilm(city, { w: W, h: H, q: Q });
  // ffmpeg works in the segment folder on relative names: characters like # ? in a path are not read as protocol syntax
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', `seg_${w}.mp4`], { cwd: segDir, stdio: ['pipe', 'inherit', 'inherit'] });
  procs.add(ff); ff.on('close', () => procs.delete(ff));
  let dead = null;   // ffmpeg quit early (no encoder, disk full...): its own message is on stderr; stop feeding it
  let done; const closed = new Promise(r => { done = r; }); ff.on('close', code => done(code));
  ff.on('error', e => { dead = e.code === 'ENOENT' ? 'ffmpeg is not installed (or not on PATH)' : e.message; done(-1); });
  ff.stdin.on('error', () => { dead ??= 'ffmpeg closed its input early'; });
  for (let f = a; f < b && !dead; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (dead) break;
    if (!ff.stdin.write(buf)) await Promise.race([new Promise(r => ff.stdin.once('drain', r)), closed]);
    if ((f - a) % 60 === 0) console.log(`w${w} ${f - a}/${b - a}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); const code = await closed; await browser.close();
  if (dead || code !== 0) fail(`ffmpeg failed for worker ${w}: ${dead || 'exit code ' + code} (ffmpeg's own message, if any, is above)`);
})); } catch (e) { fail(`render stopped: ${String(e.message || e).split('\n')[0]}`); }   // e.g. the page's render(t) threw
fs.writeFileSync(path.join(segDir, 'segs.txt'), [...Array(WK)].map((_, w) => `file 'seg_${w}.mp4'`).filter((_, w) => w * per < TOTAL).join('\n'));
try { execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'segs.txt', '-c', 'copy', 'merged.mp4'], { cwd: segDir, stdio: ['ignore', 'inherit', 'inherit'] }); }
catch { fail('ffmpeg could not join the segments (its message is above)'); }
fs.renameSync(path.join(segDir, 'merged.mp4'), out);   // the final name never passes through ffmpeg
cleanup();
console.log('done', out, TOTAL, 'frames', ((Date.now() - t0) / 1000).toFixed(0) + 's');
closeServer();
