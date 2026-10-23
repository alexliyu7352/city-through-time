// One command per city: data -> film.json (fonts resolved) -> events -> [code score] -> checks -> picture -> mix -> the film -> subtitles -> checks -> poster
//   node tools/build.mjs <city_slug> [--no-data] [--no-video] [--no-mix] [--workers N]
//   --no-video reuses build/video/video.mp4, --no-mix reuses build/audio/mix.wav (the mix takes minutes of CPU: run it alone on a desktop)
// Layout (pipeline/layout.py): sources in cities/<slug>/, everything made in build/, the deliverables in dist/. Python runs through
// uv (pyproject.toml); this machine's Chrome and worker count come from local/config.json (SKILL.md 第一次使用).
import fs from 'fs'; import os from 'os'; import path from 'path'; import { spawnSync } from 'child_process';
import { ROOT, local, cityDir, buildDir } from '../render/local.mjs';

const args = process.argv.slice(2), has = k => args.includes(k), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const slug = args[0];
if (!slug || slug.startsWith('--')) { console.error('usage: node tools/build.mjs <city_slug> [--no-data] [--no-video] [--no-mix] [--workers N]'); process.exit(2); }
const CITY = cityDir(slug), B = buildDir(slug), DIST = cityDir(slug, 'dist'), WORKERS = String(opt('--workers', local('workers')));
if (!fs.existsSync(path.join(CITY, 'city.yaml'))) { console.error(`no ${CITY}/city.yaml`); process.exit(2); }
for (const d of ['data', 'logs', 'export', 'audio', 'video', 'review']) fs.mkdirSync(path.join(B, d), { recursive: true });
fs.mkdirSync(DIST, { recursive: true });

// run a step: its output, or stop the build when it fails (unless soft); a live step prints as it goes (the render's progress)
function run(cmd, a, { soft = false, env, live = false } = {}) {
  const r = spawnSync(cmd, a, { cwd: ROOT, encoding: 'utf8', maxBuffer: 1 << 28, stdio: ['ignore', live ? 'inherit' : 'pipe', 'inherit'], env: env ? { ...process.env, ...env } : process.env });
  if (r.error) { console.error(`${cmd}: ${r.error.code === 'ENOENT' ? 'not installed (or not on PATH)' : r.error.message}`); process.exit(1); }
  if (r.status && !soft) { if (r.stdout) process.stdout.write(r.stdout); console.error(`build: ${[cmd, ...a].join(' ')} failed`); process.exit(r.status); }
  return { ok: !r.status, out: r.stdout || '' };
}
const py = (a, o) => run('uv', ['run', 'python', ...a], o);
const node = (a, o) => run(process.execPath, a, o);
const tail = (s, n) => s.trimEnd().split('\n').slice(-n).join('\n');
const head = (s, n) => s.split('\n').slice(0, n).join('\n');
try { os.setPriority(10); } catch {}   // the whole build at nice 10: the desktop stays usable (the steps inherit it)

if (!has('--no-data') || !fs.existsSync(path.join(B, 'data', 'model.json'))) {
  const r = py(['-I', 'pipeline/prep.py', CITY]); fs.writeFileSync(path.join(B, 'logs', 'prep.log'), r.out); console.log(tail(r.out, 3));
}
console.log(head(py(['-I', 'pipeline/compile.py', CITY]).out, 1));
console.log(tail(node(['render/events.mjs', slug]).out, 1));
const CODE = (JSON.parse(fs.readFileSync(path.join(B, 'film.json'), 'utf8')).music || {}).source === 'code';   // film.music.source
if (CODE) console.log(tail(py(['-I', 'audio/codescore.py', CITY]).out, 2));   // (it reads the events, and lays itself)
console.log(tail(node(['tools/subcheck.mjs', slug], { soft: true }).out, 1));
console.log(tail(py(['-I', 'tools/clipcheck.py', CITY], { soft: true }).out, 1));
if (node(['tools/camcheck.mjs', slug]).ok) console.log(tail(py(['-I', 'tools/camcheck.py', CITY], { soft: true }).out, 3));
if (!has('--no-video')) node(['render/video.mjs', slug, '--fps', '24', '--workers', WORKERS], { live: true });
if (!has('--no-mix') || !fs.existsSync(path.join(B, 'audio', 'mix.wav'))) console.log(tail(py(['-I', 'audio/mix.py', CITY]).out, 2));
const FILM = path.join(DIST, `${slug}.mp4`);
console.log(tail(node(['render/mux.mjs', path.join(B, 'video', 'video.mp4'), path.join(B, 'audio', 'mix.wav'), FILM, '--fps', '24', '--grain', '1']).out, 4));
for (const f of fs.readdirSync(path.join(B, 'export'))) if (f.startsWith(slug + '.') && /\.(srt|vtt)$/.test(f)) fs.copyFileSync(path.join(B, 'export', f), path.join(DIST, f));   // both languages and each (pipeline/subtitles.py)

// checks
const rc = node(['tools/readcheck.mjs', slug], { soft: true }); fs.writeFileSync(path.join(B, 'logs', 'readcheck.txt'), rc.out);
console.log(rc.ok ? 'readcheck ok' : `readcheck: see ${path.join(B, 'logs', 'readcheck.txt')}\n${tail(rc.out, 5)}`);
console.log(tail(py(['-I', 'tools/motioncheck.py', FILM], { soft: true }).out, 2));
const bd = spawnSync('ffmpeg', ['-v', 'error', '-i', FILM, '-vf', 'blackdetect=d=0.3:pix_th=0.02', '-an', '-f', 'null', '-'], { encoding: 'utf8', maxBuffer: 1 << 28 });
console.log(`black stretches: ${(bd.stderr.match(/black_start/g) || []).length}`);
// poster: the turn, a little after the pick-out; written bitexact, so no encoder comment
const film = JSON.parse(fs.readFileSync(path.join(B, 'film.json'), 'utf8')), pick = film.pick || [];
const at = pick.length ? pick[0].on + 4 : film.dur * 0.6;
run('ffmpeg', ['-v', 'error', '-y', '-ss', String(at), '-i', FILM, '-frames:v', '1', '-q:v', '2', '-fflags', '+bitexact', '-flags:v', '+bitexact', path.join(DIST, 'poster.jpg')]);
const credits = path.join(B, 'audio', 'instrument_credits.txt'), CR = path.join(CITY, 'CREDITS');   // the code score's samples (audio/codescore.py)
if (CODE && fs.existsSync(credits) && fs.readFileSync(credits, 'utf8').trim() && !fs.readFileSync(CR, 'utf8').includes('SAMPLED INSTRUMENTS'))
  fs.appendFileSync(CR, '\nSAMPLED INSTRUMENTS (appended by the build)\n' + fs.readFileSync(credits, 'utf8'));
console.log(`done: ${FILM}`);
