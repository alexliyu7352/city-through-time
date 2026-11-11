// Stills of the period cities' viewer (play.html?view) at named cameras, in either look, and the time a frame takes.
// usage: node tools/lookshots.mjs <city> <out_prefix> <cams.json> [--q 'look=mini&palette=chinese&...'] [--time] [--size WxH] [--seed N] [--pan <q2>]
//   cams.json: { "<name>": { "eras": [...], "today": false, "at": <film second, optional>, "land": { "at": [x, z], "t": <s since it landed>, "col" } (fx: a column of light there), "route": { "pts": [[x, z], ..], "t", "prog", "col" } (fx: a glowing line on the ground), "target": [x, z] | [x, y, z], "az": .., "el": .., "d": .., "swap": {..} } }
//   (swap: the colour-miniature look only, engine/mini.js: a landmark's detailed model in place of the generator's, before the first still)
//   writes <out_prefix>_<name>.png; --time: the milliseconds a frame takes at 2560 x 1440, the graphics' work included (a pixel read
//   back after each draw), five frames per camera after one to warm up, printed as one line per camera; --seed: the page's
//   Math.random seeded (the trees the effects and the colour look plant at random stand where they stood: two stills compare
//   pixel for pixel); --pan <q2>: shimmer, what --q adds against the same page with q2 added (detail=0: without the colour look's
//   detail): each camera turned 0.02 degrees a frame over five frames (a fraction of a pixel at a mid shot), once with --q and
//   once with q2 too; for each, the mean change of a pixel's lightness between frames over the picture's middle band (the city,
//   not the sky and the near blur) divided by its sideways edges, and their ratio, printed as one line per camera: near 1, what
//   --q adds is drawn steadily (its edges move as edges do); well over 1, it shimmers (pieces too small to draw cleanly crawl
//   from frame to frame). Give --seed with it (the land's trees the same in both)
// node tools/lookshots.mjs --film <city> <t1,t2,..> [--q ..]: the time a film frame takes at 2560 x 1440 (window.render), the same way
import fs from 'fs';
import { openFilm, closeServer, shot, takeSize } from '../render/page.mjs';

const args = process.argv.slice(2);
const take = k => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const flag = k => { const i = args.indexOf(k); return i >= 0 ? (args.splice(i, 1), true) : false; };
const q = take('--q') || '', timing = flag('--time'), film = flag('--film'), seed = take('--seed'), pan = take('--pan');
const seeded = seed == null ? null : p => p.addInitScript(s => { let a = s >>> 0; Math.random = () => { a = a + 0x6D2B79F5 >>> 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }, +seed);   // (mulberry32)
const ms = list => list.map(v => v.toFixed(0)).join(' ') + `  (median ${[...list].sort((a, b) => a - b)[list.length >> 1].toFixed(0)})`;
const readBack = () => { const gl = document.querySelector('#stage canvas').getContext('webgl2'), px = new Uint8Array(4); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };

if (film) {
  const [city, times] = args;
  if (!city || !times) { console.error('usage: node tools/lookshots.mjs --film <city> <t1,t2,..> [--q ..]'); process.exit(2); }
  const { browser, page } = await openFilm(city, { w: 2560, h: 1440, q, onPage: seeded });
  for (const t of times.split(',').map(Number)) {
    const out = await page.evaluate(async ([t, rb]) => { const read = new Function(`return (${rb})`)(), o = [];
      for (let i = 0; i < 6; i++) { const t0 = performance.now(); await window.render(t + i / 24); read(); o.push(performance.now() - t0); }
      return o.slice(1); }, [t, readBack.toString()]);
    console.log(`film ${city} t=${t}: ms per frame (2560x1440): ${ms(out)}`);
  }
  await browser.close(); closeServer(); process.exit(0);
}

const [city, out, camsFile] = args, { w, h } = takeSize(args);
if (!city || !out || !camsFile) { console.error('usage: node tools/lookshots.mjs <city> <out_prefix> <cams.json> [--q ..] [--time] [--size WxH] [--seed N] [--pan <q2>]'); process.exit(2); }
const cams = JSON.parse(fs.readFileSync(camsFile, 'utf8')), mini = /(^|&)look=mini(&|$)/.test(q);
const viewOf = c => ({ eras: c.eras, today: !!c.today, target: c.target, az: c.az, el: c.el, d: c.d, ...(c.at != null ? { at: c.at } : {}), ...(c.land !== undefined ? { land: c.land } : {}), ...(c.route ? { route: c.route } : {}) });

if (pan != null) {   // --pan: the shimmer of what --q adds (the usage above)
  // a camera's five frames -> [change between frames, sideways edges] over the middle band, in the frames' lightness (ITU-R 601,
  // as an image library's grey: (19595 r + 38470 g + 7471 b + 32768) >> 16)
  const measure = async qq => {
    const { browser, page } = await openFilm(city, { w, h, q: `view&bare&${qq}`, onPage: seeded }), res = {};
    for (const [name, c] of Object.entries(cams)) {
      const frames = [];
      for (let i = 0; i < 5; i++) { await page.evaluate(v => window.VIEW(v), { ...viewOf(c), az: c.az + i * .02 }); await page.evaluate(() => window.VIEW({}));
        frames.push((await shot(page, { type: 'png' }, true)).toString('base64')); }
      res[name] = await page.evaluate(async F => {
        const L = []; let W = 0, H = 0;
        for (const b64 of F) { const im = await createImageBitmap(await (await fetch('data:image/png;base64,' + b64)).blob()); W = im.width; H = im.height;
          const cv = new OffscreenCanvas(W, H), x = cv.getContext('2d'); x.drawImage(im, 0, 0); const d = x.getImageData(0, 0, W, H).data, g = new Float32Array(W * H);
          for (let k = 0; k < W * H; k++) g[k] = (d[k * 4] * 19595 + d[k * 4 + 1] * 38470 + d[k * 4 + 2] * 7471 + 32768) >> 16;
          L.push(g); }
        const r0 = Math.floor(H * .25), r1 = Math.floor(H * .8);
        let ch = 0, ed = 0;
        for (let f = 0; f + 1 < L.length; f++) { let s = 0; for (let k = r0 * W; k < r1 * W; k++) s += Math.abs(L[f + 1][k] - L[f][k]); ch += s / ((r1 - r0) * W); }
        for (const g of L) { let s = 0; for (let r = r0; r < r1; r++) for (let c = 0; c + 1 < W; c++) s += Math.abs(g[r * W + c + 1] - g[r * W + c]); ed += s / ((r1 - r0) * (W - 1)); }
        return [ch / (L.length - 1), ed / L.length];
      }, frames);
    }
    await browser.close(); return res;
  };
  const A = await measure(q), B = await measure(q + '&' + pan);
  for (const name of Object.keys(cams)) {
    const a = A[name][0] / A[name][1], b = B[name][0] / B[name][1];
    console.log(`${name}: change between frames over sideways edges ${a.toFixed(3)} (--q), ${b.toFixed(3)} (with ${pan}): ratio ${(a / b).toFixed(2)}`);
  }
  closeServer(); process.exit(0);
}
const { browser, page } = await openFilm(city, { w: timing ? 2560 : w, h: timing ? 1440 : h, q: `view&bare&${q}`, warnings: true, onPage: seeded });
let swapped = false;
for (const [name, c] of Object.entries(cams)) {
  const view = viewOf(c);
  await page.evaluate(v => window.VIEW(v), view);
  if (mini && c.swap && !swapped) { console.log('swap', JSON.stringify(await page.evaluate(s => window.__MINI.swap(s), c.swap))); swapped = true; }
  await page.evaluate(() => window.VIEW({}));
  if (timing) {
    const o = await page.evaluate(async ([c, rb]) => { const read = new Function(`return (${rb})`)(), o = [];
      for (let i = 0; i < 6; i++) { const t0 = performance.now(); await window.VIEW({ az: c.az + i * .2 }); read(); o.push(performance.now() - t0); }
      return o.slice(1); }, [c, readBack.toString()]);
    console.log(`${name}: ms per frame (2560x1440): ${ms(o)}`);
    continue;
  }
  await shot(page, { path: `${out}_${name}.png`, type: 'png' }, true);
  console.log('wrote', `${out}_${name}.png`);
}
await browser.close(); closeServer();
