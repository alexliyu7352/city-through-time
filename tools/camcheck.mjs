// Camera path dump for tools/camcheck.py: the camera the film really uses (keys, drift, near plane) every --step seconds.
// usage: node tools/camcheck.mjs <city_slug> [--step 0.1] [--from s] [--to s]     writes cities/<city>/build/logs/cam.json
// --from/--to: only that stretch of the film (batch checks); the full film when the whole film is being fixed
import fs from 'fs';
import { openFilm, closeServer } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const city = args[0], STEP = +opt('--step', 0.1), FROM = +opt('--from', 0), TO = opt('--to', null);
const { browser, page } = await openFilm(city);
const rows = await page.evaluate(({ STEP, FROM, TO }) => {
  const out = [], end = TO == null ? window.DUR : Math.min(window.DUR, +TO);
  for (let t = Math.round(FROM / STEP) * STEP; t <= end + 1e-9; t += STEP) { const c = window.CAMAT(t); out.push([+t.toFixed(3), ...c.p, ...c.tg, c.near, c.d, c.fov]); }
  return out;
}, { STEP, FROM, TO });
await browser.close(); closeServer();
const f = buildDir(city, 'logs', 'cam.json');
fs.writeFileSync(f, JSON.stringify({ cols: ['t', 'px', 'py', 'pz', 'tx', 'ty', 'tz', 'near', 'd', 'fov'], step: STEP, from: rows.length ? rows[0][0] : 0, rows }));
console.log(`camcheck: ${rows.length} camera samples -> ${f}`);
