// The page's sound events: node render/events.mjs <city> [--q 'k=v'] [--out <file>] [--size 1920x1080]
// (adapted from lemo-opuscar core/render/events.mjs, MIT; see NOTICE). Writes { dur, ev: window.EV } to cities/<city>/build/events.json
// (the mix and compile's sound effects read it).
import fs from 'fs'; import path from 'path';
import { openFilm, closeServer, takeSize } from './page.mjs';
import { buildDir } from './local.mjs';

const args = process.argv.slice(2), { w, h } = takeSize(args), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const city = args[0];
if (!city || city.startsWith('--')) { console.error('usage: node render/events.mjs <city> [--q k=v] [--out file] [--size WxH]'); process.exit(2); }
const out = opt('--out', buildDir(city, 'events.json'));
const { browser, page } = await openFilm(city, { w, h, q: opt('--q', '') });
const ev = await page.evaluate(() => ({ dur: window.DUR, ev: window.EV || [] }));
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
fs.writeFileSync(out, JSON.stringify(ev, null, 0));
console.log('events', ev.ev.length, 'dur', ev.dur, '→', out);
await browser.close(); closeServer();
