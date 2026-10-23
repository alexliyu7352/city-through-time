// Stills: node render/still.mjs <city> <t> [<t> ...] [--range a:b:step] [--q 'k=v&..'] [--prefix t_] [--out dir] [--size 1920x1080]
// (adapted from lemo-opuscar core/render/still.mjs, MIT; see NOTICE). One page, every time in turn; JPEG at quality 92.
// Default folder: cities/<city>/build/review/stills.
import fs from 'fs'; import path from 'path';
import { openFilm, closeServer, takeSize } from './page.mjs';
import { buildDir } from './local.mjs';

const args = process.argv.slice(2);
const take = k => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const { w, h } = takeSize(args), out = take('--out'), q = take('--q') || '', prefix = take('--prefix') || 't_', rg = take('--range');
const [city, ...times] = args;
if (rg) {
  const [a, b, st] = rg.split(':').map(Number);
  if (![a, b, st].every(Number.isFinite) || !(st > 0) || b < a) { console.error(`bad --range "${rg}": use a:b:step with step > 0 (e.g. 0:50:2.5)`); process.exit(2); }
  for (let x = a; x <= b + 1e-9; x += st) times.push(x.toFixed(2));
}
if (!city || !times.length || times.some(t => !Number.isFinite(parseFloat(t)))) { console.error('usage: node render/still.mjs <city> <t> [<t> ...] [--range a:b:step] [--q k=v] [--prefix t_] [--out dir] [--size WxH]'); process.exit(2); }
const outDir = out || buildDir(city, 'review', 'stills'); fs.mkdirSync(outDir, { recursive: true });
const { browser, page } = await openFilm(city, { w, h, q, warnings: true });
for (const ts of times) {
  const t0 = Date.now();
  await page.evaluate(t => window.render(t), parseFloat(ts));
  const f = path.join(outDir, `${prefix}${ts}.jpg`);
  await page.screenshot({ path: f, type: 'jpeg', quality: 92 }); console.log(f, Date.now() - t0 + 'ms');
}
await browser.close(); closeServer();
