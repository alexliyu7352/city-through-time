// Reading-time check for pages whose window.render(t) / window.TEXTS(t) are async (this project's footage seeks make them so).
// Same rules and output as lemo-opuscar's core/render/readcheck.mjs: every text block must stay fully in frame for at least
// (CJK chars / 4.5 + other chars / 15 + 1.5) s, never less than 1.5 s. Subtitles are checked by compile (reading hold) instead.
// Beyond the library's: every pin of film.json in the stretch must be drawn whole at some point (one never drawn is in no list),
// and no text may lie on another (the letters' bands of any two texts drawn opaque, named or not: e.g. a readout's
// legend over the counters).
// usage: node tools/readcheck.mjs <city_slug> [--step 0.08] [--from s] [--to s]     exit 0 ok, 1 too short, 2 not checked
// --from/--to: only that stretch (batch checks: a text that starts before --from or runs past --to is judged on what is inside)
import fs from 'fs';
import { openFilm, closeServer } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const city = args[0], STEP = +opt('--step', 0.08), FROM = +opt('--from', 0), TO = opt('--to', null), CJK = 4.5, LATIN = 15, PAD = 1.5, MIN = 1.5;
const { browser, page } = await openFilm(city);
const res = await page.evaluate(async ({ STEP, FROM, TO }) => {
  if (typeof window.TEXTS !== 'function' || !(window.DUR > 0)) return { none: true };
  const W = innerWidth, H = innerHeight, seen = {}, partial = {}, low = {}, over = {};
  const end = TO == null ? window.DUR : Math.min(window.DUR, +TO);
  for (let t = FROM; t <= end; t += STEP) {
    const vis = new Set();
    for (const b of (await window.TEXTS(t)) || []) {
      const id = String(b.id), key = id + '\u0000' + b.text;
      if (!(b.x0 >= 0 && b.y0 >= 0 && b.x1 <= W && b.y1 <= H)) { partial[key] ??= { id, text: b.text, t0: t }; continue; }
      if (b.y1 > H - 140 && !id.startsWith('end_')) low[key] ??= { id, text: b.text, t0: t };   // on the subtitle strip
      vis.add(key);
      const s = seen[key] ??= { id, text: b.text, t0: t, run: 0, done: false };
      if (!s.done) s.run = Math.min(t + STEP, window.DUR) - s.t0;
    }
    for (const k in seen) if (!vis.has(k)) seen[k].done = true;
    const D = window.DRAWN ? window.DRAWN() : [];   // (the frame TEXTS just drew)
    for (let i = 0; i < D.length; i++) for (let j = i + 1; j < D.length; j++) {
      const a = D[i], b = D[j], w = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), h = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
      if (w <= 2 || h <= 2) continue;
      const o = over[(a.id ?? a.text) + '\u0000' + (b.id ?? b.text)] ??= { a: a.text, b: b.text, t0: t, t1: t }; o.t1 = t;   // (a counter's text changes, its id stays)
    }
  }
  for (const k in partial) if (seen[k]) delete partial[k];
  if (FROM > 0 || TO != null) for (const k in seen) { const s = seen[k]; if (s.t0 <= FROM + STEP / 2 || s.t0 + s.run >= end - STEP / 2) s.edge = true; }   // cut by the range: not judged
  return { seen: Object.values(seen), partial: Object.values(partial), low: Object.values(low), over: Object.values(over) };
}, { STEP, FROM, TO });
await browser.close(); closeServer();
if (res.none || (!res.seen.length && !res.partial.length)) { console.error('readcheck: NOT CHECKED (no window.TEXTS / DUR, or no text at all). This is not a pass.'); process.exit(2); }
const isCJK = ch => /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]/u.test(ch);
const need = text => { let c = 0, o = 0; for (const ch of text) { if (/\s/.test(ch)) continue; isCJK(ch) ? c++ : o++; } return Math.max(MIN, c / CJK + o / LATIN + PAD); };
let bad = 0;
for (const s of res.seen) {
  if (s.edge) { console.log(`--  ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  runs past the checked range: not judged`); continue; }
  const n = need(s.text), ok = s.run >= n - STEP; if (!ok) bad++;   // one step of slack for the sampling grid
  console.log(`${ok ? 'OK ' : 'BAD'} ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  need ${n.toFixed(2)}s  got ${s.run.toFixed(2)}s  ${JSON.stringify(s.text.slice(0, 24))}`);
}
for (const s of res.partial) { bad++; console.log(`BAD ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  never fully visible  ${JSON.stringify(s.text.slice(0, 24))}`); }
for (const s of res.low || []) { bad++; console.log(`BAD ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  sits on the subtitle strip  ${JSON.stringify(s.text.slice(0, 24))}`); }
for (const o of res.over || []) { bad++; console.log(`BAD overlap            at ${o.t0.toFixed(2)}-${o.t1.toFixed(2)}s  ${JSON.stringify(o.a.slice(0, 24))} on ${JSON.stringify(o.b.slice(0, 24))}`); }
// a pin never drawn whole and opaque (no room for its box above its anchor, off screen or under a clip all its time) is in none
// of the lists above, so it would pass unseen. A pin that crosses --from/--to may show outside: not judged
const FILM = JSON.parse(fs.readFileSync(buildDir(city, 'film.json'), 'utf8'));
const drawn = new Set([...res.seen, ...res.partial].map(s => s.id)), last = TO == null ? FILM.dur : Math.min(FILM.dur, +TO);
for (const p of FILM.pins || []) {
  if (drawn.has(String(p.id)) || p.t0 < FROM || Math.min(p.t1, FILM.dur) > last) continue;
  if (p.unseen_ok) { console.log(`--  ${String(p.id).padEnd(18)} at ${p.t0.toFixed(2)}s  never drawn: accepted (unseen_ok)`); continue; }
  bad++; console.log(`BAD ${String(p.id).padEnd(18)} at ${p.t0.toFixed(2)}s  never drawn  ${JSON.stringify(String(p.text || '').slice(0, 24))}`);
}
process.exit(bad ? 1 : 0);
