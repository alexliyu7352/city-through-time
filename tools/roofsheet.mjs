// The pages of tools/roofsheet.py, a roof specimen sheet (read its header first). Two commands, one page open at a time
// (render/page.mjs), the page's Math.random seeded as render/still.mjs --seed does (the ambient occlusion's noise):
//   node tools/roofsheet.mjs list <city> <t> <job.json> <out.json>
//     job { q, seed, cams: [[name, "tx,ty,tz,az,el,d,fov"], ...] }: the page opened at the first camera, every camera in turn
//     (window.SHOT.go), the frame drawn at t; at each, every building of today's city the frame shows (engine/mini.js
//     window.__MINI.roofs: the roof kind it shows and the one it was given, footprint m2, height m, year, least rectangle and the
//     share of it filled, massing plan, its record's own id p: a replacement footprint's pieces share their parent's) with its
//     centre and top in the world and its pixel; the detailed models' boxes; the
//     model's scale (model units a metre)
//   node tools/roofsheet.mjs render <city> <t> <job.json> <out.json>
//     job { seed, pages: [{ q, shots: [{ q, file, probe: [[x, y, z], ...] }] }] }: each page opened at its first shot and the
//     others drawn on it in turn, each shot at t and saved as png; for each, its probe points' pixels (null: off the frame or
//     behind the eye) and the building drawn nearest the first probe within 30 m (the roof kind it shows there, its top, height)
// q: the page's query (look, palette, today, clean, cam, pic), as render/still.mjs takes it.
import fs from 'fs';
import { openFilm, closeServer, shot } from '../render/page.mjs';

const [cmd, city, t, jobFile, outFile] = process.argv.slice(2);
if (!['list', 'render'].includes(cmd) || !city || !Number.isFinite(+t) || !jobFile || !outFile) {
  console.error('usage: node tools/roofsheet.mjs list|render <city> <t> <job.json> <out.json>'); process.exit(2); }
const job = JSON.parse(fs.readFileSync(jobFile, 'utf8'));
const seeded = seed => seed == null ? null : p => p.addInitScript(s => { let a = s >>> 0; Math.random = () => { a = a + 0x6D2B79F5 >>> 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }, +seed);
const full = q => `city=${encodeURIComponent(city)}&${q}`;
const open = async q => { const T0 = Date.now(), r = await openFilm(city, { q: q + '&shots=1', warnings: true, onPage: seeded(job.seed) });
  console.log(`page loaded in ${((Date.now() - T0) / 1000).toFixed(1)} s`); return r; };
const draw = async (page, q, first) => { if (!first) await page.evaluate(q_ => window.SHOT.go(q_), full(q + '&shots=1')); await page.evaluate(t_ => window.render(t_), +t); };

// every building of today's city (near: [x, z, r] model units, only those within r of it), projected into the frame
const listed = (page, near = null) => page.evaluate(near => { const M = window.__MINI, cam = M.camera, mw = M.cityMesh.matrixWorld; cam.updateMatrixWorld();
  const v = cam.position.clone(), out = [];
  for (const [x, y, z, k, a, hm, yr, L, W, fill, plan, , , rk, px_, pz_] of M.roofs(near)) { v.set(x, y, z).applyMatrix4(mw); const wx = v.x, wy = v.y, wz = v.z; v.project(cam);
    const on = v.z > -1 && v.z < 1 && Math.abs(v.x) < 1 && Math.abs(v.y) < 1;
    out.push({ x: wx, y: wy, z: wz, k, rk, a: Math.round(a), hm: +(+hm).toFixed(1), yr, L: +(+L).toFixed(1), W: +(+W).toFixed(1), fill: +(+fill).toFixed(3), plan, p: px_.toFixed(6) + ',' + pz_.toFixed(6),
      px: on ? [+((v.x + 1) * 960).toFixed(1), +((1 - v.y) * 540).toFixed(1)] : null }); }
  return out; }, near);

if (cmd === 'list') {
  const { browser, page } = await open(job.q.replace(/(^|&)cam=[^&]*/, '') + '&cam=' + job.cams[0][1]); const out = { cams: {}, landmarks: null, scale: null };
  for (const [i, [name, cam]] of job.cams.entries()) { const T0 = Date.now();
    await draw(page, job.q.replace(/(^|&)cam=[^&]*/, '') + '&cam=' + cam, i === 0);
    const L = await listed(page); out.cams[name] = L.filter(b => b.px);
    console.log(`${name}: ${out.cams[name].length} buildings in frame (${L.length} listed), ${((Date.now() - T0) / 1000).toFixed(0)} s`); }
  Object.assign(out, await page.evaluate(() => ({ scale: window.__MINI.scale, landmarks: window.__MINI.landmarks() })));
  fs.writeFileSync(outFile, JSON.stringify(out)); await browser.close();
} else {
  const res = {};
  for (const P of job.pages) { const { browser, page } = await open(P.shots[0].q);
    for (const [i, s] of P.shots.entries()) { const T0 = Date.now(); await draw(page, s.q, i === 0);
      await shot(page, { path: s.file, type: 'png' }, true);
      const px = await page.evaluate(pts => { const M = window.__MINI, cam = M.camera, v = cam.position.clone(); cam.updateMatrixWorld();
        return pts.map(([x, y, z]) => { v.set(x, y, z).project(cam); return v.z > -1 && v.z < 1 ? [+((v.x + 1) * 960).toFixed(1), +((1 - v.y) * 540).toFixed(1)] : null; }); }, s.probe || []);
      let here = null;
      if (s.probe && s.probe.length) { const [x, , z] = s.probe[0], sc = await page.evaluate(() => window.__MINI.scale), L = await listed(page, [x, z, 30 * sc]);
        for (const b of L) { const d = Math.hypot(b.x - x, b.z - z) / sc; if (!here || d < here.d) here = { ...b, d: +d.toFixed(1) }; } }
      res[s.file] = { px, here }; console.log(`${s.file} ${Date.now() - T0}ms${here ? ` (kind ${here.k}, ${here.d} m off)` : ''}`); }
    await browser.close(); }
  fs.writeFileSync(outFile, JSON.stringify(res));
}
closeServer();
