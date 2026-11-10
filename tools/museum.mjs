// A museum page's stills (museum.html, docs/MUSEUM.md), after tools/museum.py has built it.
// usage: node tools/museum.mjs still <city> <page> <viewpoint>[,<viewpoint>..] [--out <dir>] [--name <file.jpg>]
//          the model alone at the viewpoint, 1920 x 1080, the reference look (what tools/living.py ref gives the image tool)
//        node tools/museum.mjs shots <city> <page> [--out <dir>] [--lang zh|en]
//          the page as a visitor sees it: at the main viewpoint (its picture), turned 3, 5 and 10 degrees (the picture full, fading, gone),
//          the white model with its sourced and estimated parts, a part's note open; at desktop size (1600 x 1000) and at a
//          phone's (390 x 844, 3 pixels to each); default cities/<city>/build/review/museum/<page>/
import fs from 'fs'; import path from 'path';
import { openFilm, closeServer, shot } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
const out = opt('--out', null), name = opt('--name', null), lang = opt('--lang', 'zh');
const [cmd, city, page, vp] = args;
if (!['still', 'shots'].includes(cmd) || !city || !page || (cmd === 'still' && !vp)) {
  console.error('usage: node tools/museum.mjs still <city> <page> <viewpoint> [--out <dir>] [--name <file.jpg>] | shots <city> <page> [--out <dir>] [--lang zh|en]'); process.exit(2); }
const dir = out || buildDir(city, 'review', 'museum', page); fs.mkdirSync(dir, { recursive: true });
const q = `id=${encodeURIComponent(page)}&lang=${lang}`;

if (cmd === 'still') {   // (several viewpoints, a,b,c: one page, each in turn)
  const vps = vp.split(','), { browser, page: P } = await openFilm(city, { q: `${q}&clean&vp=${encodeURIComponent(vps[0])}`, html: 'museum.html', warnings: true });
  for (const v of vps) {
    if (v !== vps[0]) await P.evaluate(v => window.MUSEUM({ vp: v }), v);
    const f = path.join(dir, vps.length === 1 && name ? name : `${v}_ref.jpg`);
    await shot(P, { path: f, type: 'jpeg', quality: 92 }, true); console.log(f);
  }
  await browser.close(); closeServer();
} else {
  const at = async (P, f, o) => { if (o) await P.evaluate(o => window.MUSEUM(o), o); await P.waitForTimeout(250); await shot(P, { path: path.join(dir, f), type: 'jpeg', quality: 88 }, true); console.log(path.join(dir, f)); };
  for (const [tag, view, dpr] of [['desktop', { width: 1600, height: 1000 }, 1], ['phone', { width: 390, height: 844 }, 3]]) {
    const { browser, page: P } = await openFilm(city, { q, html: 'museum.html', view, dpr, warnings: true });
    await at(P, `${tag}_0_picture.jpg`);
    // each viewpoint at its own camera shows its picture as made: the projector's test of what its camera saw (engine/studio.js
    // pdSeen) changes next to nothing there (sampled at one texel it left a white dash along every eave and post). The share of
    // pixels it changes by more than 40 of 255, against the same frame drawn without it
    for (const r of await P.evaluate(() => {
      const M = window.MUSEUM.m, U = M.studio.U, gl = M.studio.renderer.getContext(), out = [];
      if (!U.uPD || !U.uPD.value) return out;
      const read = () => { M.redraw(); const a = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4); gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, gl.RGBA, gl.UNSIGNED_BYTE, a); return a; };
      for (const id of M.viewpoints) {
        M.view({ vp: id }); const a = read(), n = U.uPN.value.clone(); U.uPN.value.set(1e6, 1e6 + 1); const b = read(); U.uPN.value.copy(n); M.redraw();
        let k = 0; for (let i = 0; i < a.length; i += 4) if (Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2])) > 40) k++;
        out.push({ id, share: k / (a.length / 4) });
      }
      M.view({}); return out; })) {
      const bad = r.share > .0005; if (bad) process.exitCode = 1;
      console.log(`museum shots ${page} ${tag}: ${r.id} at its own camera: ${(r.share * 100).toFixed(3)}% of the picture changed by what its camera saw${bad ? ' FAULT (over 0.05%: the picture no longer shows as made; engine/studio.js pdSeen)' : ''}`);
    }
    await at(P, `${tag}_3deg.jpg`, { turn: 3 });   // (the far land behind the model still shows here: a copy of the building in it, beside the model, was missed further off)
    await at(P, `${tag}_5deg.jpg`, { turn: 5 });   // (the picture fading: engine/museum.js FULL_DEG, GONE_DEG)
    await at(P, `${tag}_10deg.jpg`, { turn: 10 });
    if (tag === 'desktop') {
      await P.click('#tones'); await at(P, `${tag}_tones.jpg`, { turn: 25, up: 15 });
      // a click on the model itself: the middles of its faces on screen, the part named main first (else every part), nearest the
      // eye first, until one opens a part's note (the middle of the model can be an empty court); the part list's button if none does
      const pts = await P.evaluate(() => {
        const S = window.MUSEUM.m.studio, cam = S.camera, r = S.renderer.domElement.getBoundingClientRect(), V = cam.position.constructor;
        const ids = Object.keys(S.eras).filter(k => k !== '_stand' && S.eras[k].mesh), order = ids.includes('main') ? ['main'] : ids, out = [];
        for (const id of order) {
          const g = S.eras[id].mesh.geometry, pos = g.attributes.position, ix = g.index, mw = S.eras[id].mesh.matrixWorld;
          const nt = (ix ? ix.count : pos.count) / 3, step = Math.max(1, Math.floor(nt / 400)), vi = k => ix ? ix.getX(k) : k;
          for (let t = 0; t < nt; t += step) {
            const c = new V(); for (let j = 0; j < 3; j++) c.add(new V(pos.getX(vi(3 * t + j)), pos.getY(vi(3 * t + j)), pos.getZ(vi(3 * t + j))));
            c.multiplyScalar(1 / 3).applyMatrix4(mw); const d = c.distanceTo(cam.position), q = c.clone().project(cam);
            if (Math.abs(q.x) < .9 && Math.abs(q.y) < .9 && q.z < 1) out.push([d, r.left + (q.x * .5 + .5) * r.width, r.top + (-q.y * .5 + .5) * r.height]);
          }
        }
        return out.sort((a, b) => a[0] - b[0]).slice(0, 40).map(q => [q[1], q[2]]); });
      let opened = false;
      for (const [x, y] of pts) {
        await P.mouse.click(x, y); await P.waitForTimeout(60);
        if (await P.evaluate(() => !!document.querySelector('[data-part][aria-pressed="true"]'))) { opened = true; break; }
      }
      if (!opened) { console.warn(`museum shots ${page}: no click on the model opened a part's note: the part list's button instead`);
        await P.evaluate(() => (document.querySelector('[data-part="main"]') || document.querySelector('[data-part]')).click()); }
      await at(P, `${tag}_part.jpg`);
    } else {
      await P.evaluate(() => { const t = document.getElementById('tones'); t.click(); }); await at(P, `${tag}_tones.jpg`, { turn: 25, up: 15 });
      await P.evaluate(() => (document.querySelector('[data-part="main"]') || document.querySelector('[data-part]')).click()); await at(P, `${tag}_part.jpg`);
      await P.evaluate(() => scrollTo(0, 0)); await P.screenshot({ path: path.join(dir, `${tag}_label.jpg`), type: 'jpeg', quality: 85, fullPage: true }); console.log(path.join(dir, `${tag}_label.jpg`));
    }
    await browser.close();
  }
  closeServer();
}
