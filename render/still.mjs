// Stills: node render/still.mjs <city> <t> [<t> ...] [--range a:b:step] [--q 'k=v&..'] [--prefix t_] [--out dir] [--size 1920x1080] [--format jpg|png] [--seed N] [--shots shots.json]
// A time is seconds or a moment of the film by name (build/film.json), with an offset: cue:<line id>[+-s] (the line's start),
// node:<id>[.end][+-s], loss:<era id>/<loss id>[.gone][+-s] (its ring starting, or every part gone), year:<y>[+-s] (the
// counter first reaching y, BCE negative); each prints the second it stands for, and the still is named by that second.
// (adapted from lemo-opuscar core/render/still.mjs, MIT; see NOTICE). One page, every time in turn; default JPEG at quality 92.
// Default folder: cities/<city>/build/review/stills. --out more than once: each folder takes the times and ranges given before it
// (since the --out before), all on one page load (tools/rangecheck.py: every stretch's stills into its own folder); --range may repeat.
// --shots shots.json: many shots on one page load, each taken at every time given and each the picture its own run of this tool
// would give (the city loads once, not once a shot: a look round of a few hundred stills at fixed cameras). The file is a list of
// { "q": "<the shot's own page query, over --q: e.g. cam=tx,ty,tz,az,el,d,fov&pic={..}>", "prefix": "<its files' prefix (--prefix)>",
// "out": "<its folder (--out)>" }. A page takes the shots whose query is its own but for the camera (cam) and the look's per-shot
// picture keys (engine/mini.js STILL_KEYS, e.g. the sun's side); the others open a page of their own, in turn (engine/main.js SHOT).
// --seed N: the page's Math.random seeded (the ambient occlusion's noise is drawn at random on every page load: two runs of a still
// agree pixel for pixel only with the same seed, a shot of a batch and its own run alike).
import fs from 'fs'; import path from 'path';
import { openFilm, closeServer, takeSize, shot } from './page.mjs';
import { buildDir } from './local.mjs';

const args = process.argv.slice(2);
const take = k => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const { w, h } = takeSize(args), q = take('--q') || '', prefix = take('--prefix') || 't_', format = take('--format') || 'jpg', seed = take('--seed'), shotsFile = take('--shots');
if (!['jpg', 'png'].includes(format)) throw new Error('still: --format jpg|png');
let city = null, times = [];
const jobs = [];   // [folder, times]
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--out') { jobs.push([args[++i], times]); times = []; continue; }
  if (args[i] !== '--range') { if (city == null) city = args[i]; else times.push(args[i]); continue; }
  const rg = args[++i] || '', [a, b, st] = rg.split(':').map(Number);
  if (![a, b, st].every(Number.isFinite) || !(st > 0) || b < a) { console.error(`bad --range "${rg}": use a:b:step with step > 0 (e.g. 0:50:2.5)`); process.exit(2); }
  for (let x = a; x <= b + 1e-9; x += st) times.push(x.toFixed(2));
}
// a moment by name -> its second (film.json); a plain number stays as written
let FILMJ = null;
function moment(s) {
  const m = /^(cue|node|loss|year):([^+]+?)(?:\.(end|gone))?([+-][\d.]+)?$/.exec(s); if (!m) return s;
  FILMJ ??= JSON.parse(fs.readFileSync(buildDir(city, 'film.json'), 'utf8'));
  const [, kind, name, edge, off] = m; let t = null;
  if (kind === 'cue') t = FILMJ.cues?.find(c => c.id === name)?.t0;
  if (kind === 'node') { const n = FILMJ.nodes?.find(n => n.id === name); t = n && (edge === 'end' ? n.t1 : n.t0); }
  if (kind === 'loss') { const [eid, lid] = name.split('/'), L = FILMJ.eras?.find(e => e.id === eid)?.losses?.find(l => l.id === lid); t = L && (edge === 'gone' ? L.gone : L.curve[0][0]); }
  if (kind === 'year') { const y = +name, yl = FILMJ.yearline || []; for (let i = 1; i < yl.length && t == null; i++) if (yl[i][1] >= y && yl[i - 1][1] < y) t = yl[i - 1][0] + (yl[i][0] - yl[i - 1][0]) * (y - yl[i - 1][1]) / (yl[i][1] - yl[i - 1][1]); }
  if (t == null) { console.error(`still.mjs: no ${kind} "${name}" in film.json`); process.exit(2); }
  const v = (t + (off ? parseFloat(off) : 0)).toFixed(2); console.log(`${s} = ${v} s`); return v;
}
for (const j of jobs) j[1] = j[1].map(moment); times = times.map(moment);
if (jobs.length <= 1) jobs.splice(0, 1, [jobs[0]?.[0] || buildDir(city || '', 'review', 'stills'), [...(jobs[0]?.[1] || []), ...times]]);   // (one folder: every time)
else if (times.length) { console.error('still.mjs: times after the last of several --out folders: give each folder after its times'); process.exit(2); }
if (!city || jobs.some(([, ts]) => !ts.length || ts.some(t => !Number.isFinite(parseFloat(t))))) { console.error('usage: node render/still.mjs <city> <t> [<t> ...] [--range a:b:step] [--q k=v] [--prefix t_] [--out dir] [--size WxH]'); process.exit(2); }
// --shots: the list, each shot's page query (--q with the shot's keys in place of its own), folder and prefix
let SHOTS = null;
if (shotsFile) {
  if (jobs.length > 1) { console.error('still.mjs: --shots takes one --out (the shots\' default folder); a shot names its own with "out"'); process.exit(2); }
  let list; try { list = JSON.parse(fs.readFileSync(shotsFile, 'utf8')); } catch (e) { console.error(`still.mjs: --shots ${shotsFile}: ${e.message}`); process.exit(2); }
  if (!Array.isArray(list) || !list.length || list.some(s => !s || typeof s !== 'object' || typeof (s.q ?? '') !== 'string' || ['prefix', 'out'].some(k => s[k] != null && typeof s[k] !== 'string'))) {
    console.error('still.mjs: --shots wants a list of { "q": "<page query>", "prefix": "<file prefix>", "out": "<folder>" }'); process.exit(2); }
  SHOTS = list.map(s => { const Q = new URLSearchParams(q); for (const [k, v] of new URLSearchParams(s.q || '')) Q.set(k, v);
    return { q: Q.toString(), prefix: s.prefix ?? prefix, out: s.out || jobs[0][0] }; });
}
for (const d of new Set([...jobs.map(([d]) => d), ...(SHOTS || []).map(s => s.out)])) fs.mkdirSync(d, { recursive: true });
const onPage = seed == null ? null : p => p.addInitScript(s => { let a = s >>> 0; Math.random = () => { a = a + 0x6D2B79F5 >>> 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }, +seed);
const take1 = async (page, outDir, pre, ts) => {   // one still: the frame at ts, its file
  const t0 = Date.now();
  await page.evaluate(t => window.render(t), parseFloat(ts));
  const f = path.join(outDir, `${pre}${ts}.${format}`);
  await shot(page, { path: f, type: format === 'png' ? 'png' : 'jpeg', ...(format === 'jpg' ? { quality: 92 } : {}) }, true); console.log(f, Date.now() - t0 + 'ms');
};
if (!SHOTS) {
  const { browser, page } = await openFilm(city, { w, h, q, warnings: true, onPage });
  for (const [outDir, ts_] of jobs) for (const ts of ts_) await take1(page, outDir, prefix, ts);
  await browser.close();
} else {   // a page for the first shot left, and every later one it can draw (main.js SHOT.fits); the rest on the next page
  const times = jobs[0][1], full = s => `city=${encodeURIComponent(city)}&${s.q}`;
  for (let rest = SHOTS, n = 1; rest.length; n++) {
    const T0 = Date.now(), { browser, page } = await openFilm(city, { w, h, q: rest[0].q, warnings: true, onPage }), here = [rest[0]];
    console.log(`page ${n}: loaded in ${((Date.now() - T0) / 1000).toFixed(1)} s`);
    for (const s of rest.slice(1)) if (await page.evaluate(q_ => window.SHOT.fits(q_), full(s))) here.push(s);
    for (const s of here) {
      if (s !== here[0]) { const t0 = Date.now(); await page.evaluate(q_ => window.SHOT.go(q_), full(s)); console.log(`  next shot ${Date.now() - t0}ms`); }
      for (const ts of times) await take1(page, s.out, s.prefix, ts);
    }
    await browser.close(); rest = rest.filter(s => !here.includes(s));
  }
}
closeServer();
