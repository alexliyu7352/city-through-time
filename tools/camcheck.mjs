// Camera path dump for tools/camcheck.py: the camera the film really uses (keys, drift, near plane) every --step seconds.
// usage: node tools/camcheck.mjs <city_slug> [--step 0.1] [--from s --to s ..] [--out file]     writes cities/<city>/build/logs/cam.json (or --out)
// --from/--to: only that stretch of the film (batch checks); the full film when the whole film is being fixed. Given more than once
// (in pairs), every stretch on one page load, each sampled as if it were dumped alone: `ranges` holds each one's first and last
// sample and how many rows it has, in the order given (tools/camcheck.py checks each on its own)
import fs from 'fs';
import { openFilm, closeServer } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; }, all = k => args.flatMap((a, i) => a === k ? [args[i + 1]] : []);
const city = args[0], STEP = +opt('--step', 0.1), FROMS = all('--from'), TOS = all('--to');
if (FROMS.length > 1 && FROMS.length !== TOS.length) { console.error('camcheck: give --from and --to in pairs, one pair a stretch'); process.exit(2); }
const SPANS = FROMS.length > 1 ? FROMS.map((a, i) => [+a, TOS[i]]) : [[+opt('--from', 0), opt('--to', null)]];
const { browser, page } = await openFilm(city);
const rows = [], ranges = [];
for (const [FROM, TO] of SPANS) {
  const r = await page.evaluate(({ STEP, FROM, TO }) => {
    const out = [], end = TO == null ? window.DUR : Math.min(window.DUR, +TO);
    for (let t = Math.round(FROM / STEP) * STEP; t <= end + 1e-9; t += STEP) { const c = window.CAMAT(t); out.push([+t.toFixed(3), ...c.p, ...c.tg, c.near, c.d, c.fov]); }
    return out;
  }, { STEP, FROM, TO });
  rows.push(...r); ranges.push(r.length ? [r[0][0], r[r.length - 1][0], r.length] : [null, null, 0]);
}
await browser.close(); closeServer();
const f = opt('--out', null) || buildDir(city, 'logs', 'cam.json');
fs.writeFileSync(f, JSON.stringify({ cols: ['t', 'px', 'py', 'pz', 'tx', 'ty', 'tz', 'near', 'd', 'fov'], step: STEP, from: rows.length ? rows[0][0] : 0, ranges, rows }));
console.log(`camcheck: ${rows.length} camera samples${ranges.length > 1 ? ` in ${ranges.length} stretches` : ''} -> ${f}`);
