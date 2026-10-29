// The period cities from every side, after any change to their models or to the look (docs/MODEL.md). Runs tools/geocheck.mjs
// first and stops on a face pointing the wrong way; then opens the viewer (play.html?view, engine/view.js) and takes, of each
// period city, a close-up of its houses (its densest 200 m square) from eight bearings at two heights, its four largest landmarks
// (halls, terraces, palaces: where a stair, a tree or a road meets a big building) from four bearings each, and the whole city
// from four bearings, in both looks: 成片 (film: its colour, glow, edge line, the key light beside the camera) and 檢查 (check: plain
// white, sharp, the key light fixed in the room). One sheet per city and look: cities/<slug>/build/review/eraview/<era>_<look>.jpg,
// rows top to bottom: close-up at 12 degrees up, close-up at 35 degrees up, the landmarks (two rows, four bearings each), the whole
// city at 30 degrees; left to right the camera's bearing 0, 45 .. 315, counted as the film's camera keys count it (0: the camera south of the city, 90 east, 180 north, 270
// west). The stills are kept in <era>/. Each city is shown as it stands at a moment of the film (engine/eralife.js): a city that
// loses parts while it stands (lose:) at each of its moments, one set of sheets each, <era>_m<k>_<look>.jpg (stills in <era>_m<k>/),
// its close-up and landmarks those standing then; --at <seconds>: every city at that one moment, <era>_at<s>_<look>.jpg.
// usage: node tools/eraview.mjs <city_slug> [--eras a,b] [--look film|check] [--at <seconds>] [--d .045 (the close-up's distance; nearer for a small place)] [--quality low]
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';
import { openFilm, closeServer, shot } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';
import { geocheck } from './geocheck.mjs';
import { whole } from '../engine/eralife.js';

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const city = args[0];
if (!city) { console.error('usage: node tools/eraview.mjs <city_slug> [--eras a,b] [--look film|check] [--at <seconds>] [--d .045] [--quality low]'); process.exit(2); }
const only = opt('--eras', null)?.split(','), looks = opt('--look', null) ? [opt('--look')] : ['film', 'check'], D = +opt('--d', .045), AT = opt('--at', null);

const gc = geocheck(city, only);
console.log(gc.lines.join('\n'));
if (gc.failed) { console.error('eraview: geocheck failed, the faces above point the wrong way (engine/props.js Geo); fix them before looking'); process.exit(1); }

const AZ = [0, 45, 90, 135, 180, 225, 270, 315];
// an era's largest landmarks standing whole at film time t: its landmark, landmark-roof and earthwork pieces (citygen parts 1, 9,
// 10) grouped by the building they belong to, the four with the most ground under them, each with its centre and extent [x, z, size] (model units)
const FILM = JSON.parse(fs.readFileSync(buildDir(city, 'film.json'), 'utf8'));
function landmarks(id, t) {
  const e = FILM.eras.find(q => q.id === id), J = JSON.parse(fs.readFileSync(buildDir(city, e.file), 'utf8')), g = new Map();
  for (const [i, p] of J.prims.entries()) if ([1, 9, 10].includes(p[11]) && whole(e, p[10], J.lost ? J.lost[i] : 0, t)) {
    const k = `${(p[15] ?? p[1]).toFixed(4)},${(p[16] ?? p[2]).toFixed(4)}`, r = Math.max(p[5], p[6] || 0) / 2, v = g.get(k) || [1e9, 1e9, -1e9, -1e9, 0];
    v[0] = Math.min(v[0], p[1] - r); v[1] = Math.min(v[1], p[2] - r); v[2] = Math.max(v[2], p[1] + r); v[3] = Math.max(v[3], p[2] + r); v[4] += p[5] * (p[6] || p[5]); g.set(k, v);
  }
  return [...g.values()].sort((a, b) => b[4] - a[4]).slice(0, 4).map(v => [(v[0] + v[2]) / 2, (v[1] + v[3]) / 2, Math.hypot(v[2] - v[0], v[3] - v[1])]);
}
const { browser, page } = await openFilm(city, { q: 'view&bare' + (opt('--quality', '') === 'low' ? '&quality=low' : '') });
const eras = (await page.evaluate(() => window.VIEWINFO())).filter(e => !only || only.includes(e.id));
const root = buildDir(city, 'review', 'eraview');
for (const e of eras) for (const [mi, m] of (AT != null ? [{ t: +AT, dense: e.dense }] : e.moments).entries()) {
  const tag = AT != null ? `_at${+AT}` : e.moments.length > 1 ? `_m${mi + 1}` : '';   // (one moment: the names as they were)
  const dir = path.join(root, e.id + tag); fs.mkdirSync(dir, { recursive: true });
  for (const look of looks) {
    // the close-up nearer for a small place (a village a few hundred metres across); the whole city however large it is
    const dc = Math.min(D, Math.max(.012, e.r * .8)), dw = Math.min(2.8, Math.max(.04, e.r * 2.2));
    // the landmarks: 16 views, four bearings of each of the four largest (fewer landmarks: more bearings of each)
    const lm = landmarks(e.id, m.t), lmv = lm.length ? [...Array(16).keys()].map(i => { const k = i % lm.length, j = Math.floor(i / lm.length); return [lm[k], (30 + j * 360 / Math.ceil(16 / lm.length)) % 360, k]; }) : [];
    const rows = [[m.dense, 12, dc, AZ, 'close'], [m.dense, 35, dc, AZ, 'close'], ...lmv.map(([L, az, k]) => [[L[0], L[1]], 30, Math.min(.3, Math.max(.012, L[2] * 1.4)), [az], `landmark${k + 1}`]), [e.id, 30, dw, [0, 90, 180, 270], 'whole']];
    const files = [];
    for (const [target, el, d, azs, what] of rows) for (const az of azs) {
      await page.evaluate(o => window.VIEW(o), { eras: [e.id], look, today: false, at: m.t, target, az, el, d });
      const f = path.join(dir, `${look}_${what}_el${el}_az${Math.round(az)}.jpg`);
      await shot(page, { path: f, type: 'jpeg', quality: 90 }, true); files.push(f);
    }
    // the sheet: 8 tiles a row (the whole city's four take two places each)
    const sheet = path.join(root, `${e.id}${tag}_${look}.jpg`), n = files.length, nw = 4, nr = (n - nw) / 8;
    const f = files.map((_, i) => `[${i}]scale=${i < n - nw ? 480 : 960}:-1[v${i}]`).join(';');
    const row = (a, k) => [...Array(k).keys()].map(i => `[v${a + i}]`).join('');
    const rowsF = [...Array(nr).keys()].map(r => `${row(r * 8, 8)}hstack=8[r${r}]`).join(';') + `;${row(n - nw, nw)}hstack=${nw}[r${nr}]`;
    const ff = spawnSync('ffmpeg', ['-loglevel', 'error', '-y', ...files.flatMap(x => ['-i', x]), '-filter_complex', `${f};${rowsF};${[...Array(nr + 1).keys()].map(r => `[r${r}]`).join('')}vstack=${nr + 1}`, '-frames:v', '1', sheet], { stdio: 'inherit' });
    if (ff.status) { console.error(`eraview: ffmpeg could not lay out ${sheet}`); process.exit(1); }
    console.log(`eraview: ${e.id} (${e.label}) ${look}, at ${m.t} s: ${sheet}`);
  }
}
await browser.close(); closeServer();
