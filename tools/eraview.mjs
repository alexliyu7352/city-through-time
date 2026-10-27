// The period cities from every side, after any change to their models or to the look (docs/MODEL.md). Runs tools/geocheck.mjs
// first and stops on a face pointing the wrong way; then opens the viewer (play.html?view, engine/view.js) and takes, of each
// period city, a close-up of its houses (its densest 200 m square) from eight bearings at two heights, and the whole city from
// four bearings, in both looks: 成片 (film: its colour, glow, edge line, the key light beside the camera) and 檢查 (check: plain
// white, sharp, the key light fixed in the room). One sheet per city and look: cities/<slug>/build/review/eraview/<era>_<look>.jpg,
// rows top to bottom: close-up at 12 degrees up, close-up at 35 degrees up, the whole city at 30 degrees; left to right the camera's
// bearing 0, 45 .. 315, counted as the film's camera keys count it (0: the camera south of the city, 90 east, 180 north, 270
// west). The stills are kept in <era>/.
// usage: node tools/eraview.mjs <city_slug> [--eras a,b] [--look film|check] [--d .045] [--quality low]
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';
import { openFilm, closeServer } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';
import { geocheck } from './geocheck.mjs';

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const city = args[0];
if (!city) { console.error('usage: node tools/eraview.mjs <city_slug> [--eras a,b] [--look film|check] [--d .045] [--quality low]'); process.exit(2); }
const only = opt('--eras', null)?.split(','), looks = opt('--look', null) ? [opt('--look')] : ['film', 'check'], D = +opt('--d', .045);

const gc = geocheck(city, only);
console.log(gc.lines.join('\n'));
if (gc.failed) { console.error('eraview: geocheck failed, the faces above point the wrong way (engine/props.js Geo); fix them before looking'); process.exit(1); }

const AZ = [0, 45, 90, 135, 180, 225, 270, 315];
const { browser, page } = await openFilm(city, { q: 'view&bare' + (opt('--quality', '') === 'low' ? '&quality=low' : '') });
const eras = (await page.evaluate(() => window.VIEWINFO())).filter(e => !only || only.includes(e.id));
const root = buildDir(city, 'review', 'eraview');
for (const e of eras) {
  const dir = path.join(root, e.id); fs.mkdirSync(dir, { recursive: true });
  for (const look of looks) {
    const rows = [[`${e.id}:dense`, 12, D, AZ], [`${e.id}:dense`, 35, D, AZ], [e.id, 30, Math.min(1.2, Math.max(.04, e.r * 2.2)), [0, 90, 180, 270]]];
    const files = [];
    for (const [target, el, d, azs] of rows) for (const az of azs) {
      await page.evaluate(o => window.VIEW(o), { eras: [e.id], look, today: false, target, az, el, d });
      const f = path.join(dir, `${look}_${target.includes(':') ? 'close' : 'whole'}_el${el}_az${az}.jpg`);
      await page.screenshot({ path: f, type: 'jpeg', quality: 90 }); files.push(f);
    }
    // the sheet: 8 tiles a row (the whole city's four take two places each)
    const sheet = path.join(root, `${e.id}_${look}.jpg`), n = files.length;
    const f = files.map((_, i) => `[${i}]scale=${i < 16 ? 480 : 960}:-1[v${i}]`).join(';');
    const r1 = [...Array(8).keys()].map(i => `[v${i}]`).join(''), r2 = [...Array(8).keys()].map(i => `[v${i + 8}]`).join(''), r3 = [...Array(n - 16).keys()].map(i => `[v${i + 16}]`).join('');
    const ff = spawnSync('ffmpeg', ['-loglevel', 'error', '-y', ...files.flatMap(x => ['-i', x]), '-filter_complex', `${f};${r1}hstack=8[a];${r2}hstack=8[b];${r3}hstack=${n - 16}[c];[a][b][c]vstack=3`, '-frames:v', '1', sheet], { stdio: 'inherit' });
    if (ff.status) { console.error(`eraview: ffmpeg could not lay out ${sheet}`); process.exit(1); }
    console.log(`eraview: ${e.id} (${e.label}) ${look}: ${sheet}`);
  }
}
await browser.close(); closeServer();
