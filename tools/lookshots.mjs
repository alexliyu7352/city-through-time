// Stills of the period cities' viewer (play.html?view) at named cameras, in either look, and the time a frame takes.
// usage: node tools/lookshots.mjs <city> <out_prefix> <cams.json> [--q 'look=mini&palette=chinese&...'] [--time] [--size WxH]
//   cams.json: { "<name>": { "eras": [...], "today": false, "at": <film second, optional>, "land": { "at": [x, z], "t": <s since it landed>, "col" } (fx: a column of light there), "route": { "pts": [[x, z], ..], "t", "prog", "col" } (fx: a glowing line on the ground), "target": [x, z] | [x, y, z], "az": .., "el": .., "d": .., "swap": {..} } }
//   (swap: the colour-miniature look only, engine/mini.js: a landmark's detailed model in place of the generator's, before the first still)
//   writes <out_prefix>_<name>.png; --time: the milliseconds a frame takes at 2560 x 1440, the graphics' work included (a pixel read
//   back after each draw), five frames per camera after one to warm up, printed as one line per camera
// node tools/lookshots.mjs --film <city> <t1,t2,..> [--q ..]: the time a film frame takes at 2560 x 1440 (window.render), the same way
import fs from 'fs';
import { openFilm, closeServer, shot, takeSize } from '../render/page.mjs';

const args = process.argv.slice(2);
const take = k => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const flag = k => { const i = args.indexOf(k); return i >= 0 ? (args.splice(i, 1), true) : false; };
const q = take('--q') || '', timing = flag('--time'), film = flag('--film');
const ms = list => list.map(v => v.toFixed(0)).join(' ') + `  (median ${[...list].sort((a, b) => a - b)[list.length >> 1].toFixed(0)})`;
const readBack = () => { const gl = document.querySelector('#stage canvas').getContext('webgl2'), px = new Uint8Array(4); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };

if (film) {
  const [city, times] = args;
  if (!city || !times) { console.error('usage: node tools/lookshots.mjs --film <city> <t1,t2,..> [--q ..]'); process.exit(2); }
  const { browser, page } = await openFilm(city, { w: 2560, h: 1440, q });
  for (const t of times.split(',').map(Number)) {
    const out = await page.evaluate(async ([t, rb]) => { const read = new Function(`return (${rb})`)(), o = [];
      for (let i = 0; i < 6; i++) { const t0 = performance.now(); await window.render(t + i / 24); read(); o.push(performance.now() - t0); }
      return o.slice(1); }, [t, readBack.toString()]);
    console.log(`film ${city} t=${t}: ms per frame (2560x1440): ${ms(out)}`);
  }
  await browser.close(); closeServer(); process.exit(0);
}

const [city, out, camsFile] = args, { w, h } = takeSize(args);
if (!city || !out || !camsFile) { console.error('usage: node tools/lookshots.mjs <city> <out_prefix> <cams.json> [--q ..] [--time] [--size WxH]'); process.exit(2); }
const cams = JSON.parse(fs.readFileSync(camsFile, 'utf8')), mini = /(^|&)look=mini(&|$)/.test(q);
const { browser, page } = await openFilm(city, { w: timing ? 2560 : w, h: timing ? 1440 : h, q: `view&bare&${q}`, warnings: true });
let swapped = false;
for (const [name, c] of Object.entries(cams)) {
  const view = { eras: c.eras, today: !!c.today, target: c.target, az: c.az, el: c.el, d: c.d, ...(c.at != null ? { at: c.at } : {}), ...(c.land !== undefined ? { land: c.land } : {}), ...(c.route ? { route: c.route } : {}) };
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
