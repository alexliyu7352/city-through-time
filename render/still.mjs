// Stills: node render/still.mjs <city> <t> [<t> ...] [--range a:b:step] [--q 'k=v&..'] [--prefix t_] [--out dir] [--size 1920x1080]
// A time is seconds or a moment of the film by name (build/film.json), with an offset: cue:<line id>[+-s] (the line's start),
// node:<id>[.end][+-s], loss:<era id>/<loss id>[.gone][+-s] (its ring starting, or every part gone), year:<y>[+-s] (the
// counter first reaching y, BCE negative); each prints the second it stands for, and the still is named by that second.
// (adapted from lemo-opuscar core/render/still.mjs, MIT; see NOTICE). One page, every time in turn; JPEG at quality 92.
// Default folder: cities/<city>/build/review/stills. --out more than once: each folder takes the times and ranges given before it
// (since the --out before), all on one page load (tools/rangecheck.py: every stretch's stills into its own folder); --range may repeat.
import fs from 'fs'; import path from 'path';
import { openFilm, closeServer, takeSize, shot } from './page.mjs';
import { buildDir } from './local.mjs';

const args = process.argv.slice(2);
const take = k => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const { w, h } = takeSize(args), q = take('--q') || '', prefix = take('--prefix') || 't_';
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
for (const [d] of jobs) fs.mkdirSync(d, { recursive: true });
const { browser, page } = await openFilm(city, { w, h, q, warnings: true });
for (const [outDir, ts_] of jobs) for (const ts of ts_) {
  const t0 = Date.now();
  await page.evaluate(t => window.render(t), parseFloat(ts));
  const f = path.join(outDir, `${prefix}${ts}.jpg`);
  await shot(page, { path: f, type: 'jpeg', quality: 92 }, true); console.log(f, Date.now() - t0 + 'ms');
}
await browser.close(); closeServer();
