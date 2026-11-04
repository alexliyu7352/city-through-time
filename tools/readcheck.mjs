// Reading-time check for pages whose window.render(t) / window.TEXTS(t) are async (this project's footage seeks make them so).
// Same rules and output as lemo-opuscar's core/render/readcheck.mjs: every text block must stay fully in frame for at least
// (CJK chars / 4.5 + other chars / 15 + 1.5) s, never less than 1.5 s. Subtitles follow the narration instead (compile: on screen while heard).
// Beyond the library's: every pin of film.json in the stretch must be drawn whole at some point (one never drawn is in no list),
// and no text may lie on another (the letters' bands of any two texts drawn opaque, named or not: e.g. a readout's
// legend over the counters).
// usage: node tools/readcheck.mjs <city_slug> [--step 0.08] [--from s --to s ..] [--json file]     exit 0 ok, 1 too short, 2 not checked
// --from/--to: only that stretch (batch checks: a text that starts before --from or runs past --to is judged on what is inside).
// Given more than once (in pairs): every stretch on one page load, each judged on its own as if checked alone (its own edges, its
// own pins); --json writes each one's result, [{from, to, code, ok, lines}] (tools/rangecheck.py)
import fs from 'fs';
import { openFilm, closeServer } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; }, all = k => args.flatMap((a, i) => a === k ? [args[i + 1]] : []);
const city = args[0], STEP = +opt('--step', 0.08), FROMS = all('--from'), TOS = all('--to'), CJK = 4.5, LATIN = 15, PAD = 1.5, MIN = 1.5;
if (FROMS.length > 1 && FROMS.length !== TOS.length) { console.error('readcheck: give --from and --to in pairs, one pair a stretch'); process.exit(2); }
const SPANS = FROMS.length > 1 ? FROMS.map((a, i) => [+a, TOS[i]]) : [[+opt('--from', 0), opt('--to', null)]];
const { browser, page } = await openFilm(city);
const RES = [];
for (const [FROM, TO] of SPANS) RES.push(await page.evaluate(async ({ STEP, FROM, TO }) => {
  if (typeof window.TEXTS !== 'function' || !(window.DUR > 0)) return { none: true };
  const W = innerWidth, H = innerHeight, seen = {}, partial = {}, low = {}, over = {}; let drew = 0;
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
    if (D.length) drew++;
    for (let i = 0; i < D.length; i++) for (let j = i + 1; j < D.length; j++) {
      const a = D[i], b = D[j], w = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), h = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
      if (w <= 2 || h <= 2) continue;
      const o = over[(a.id ?? a.text) + '\u0000' + (b.id ?? b.text)] ??= { a: a.text, b: b.text, t0: t, t1: t }; o.t1 = t;   // (a counter's text changes, its id stays)
    }
  }
  for (const k in partial) if (seen[k]) delete partial[k];
  if (FROM > 0 || TO != null) for (const k in seen) { const s = seen[k]; if (s.t0 <= FROM + STEP / 2 || s.t0 + s.run >= end - STEP / 2) s.edge = true; }   // cut by the range: not judged
  return { seen: Object.values(seen), partial: Object.values(partial), low: Object.values(low), over: Object.values(over), drew };
}, { STEP, FROM, TO }));
await browser.close(); closeServer();
const FILM = JSON.parse(fs.readFileSync(buildDir(city, 'film.json'), 'utf8'));
const isCJK = ch => /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]/u.test(ch);
const need = text => { let c = 0, o = 0; for (const ch of text) { if (/\s/.test(ch)) continue; isCJK(ch) ? c++ : o++; } return Math.max(MIN, c / CJK + o / LATIN + PAD); };
function judge(res, FROM, TO) {   // one stretch: [exit code, the lines it prints]
  // nothing drawn at all: the page draws no text (no window.TEXTS / DUR, or an overlay that never drew); a stretch whose only
  // text is the subtitles (a prologue with no picture) has nothing to time, and is still checked for texts over texts and pins
  if (res.none || (!res.seen.length && !res.partial.length && !res.drew)) return [2, ['readcheck: NOT CHECKED (no window.TEXTS / DUR, or no text at all). This is not a pass.']];
  let bad = 0; const L = [];
  if (!res.seen.length && !res.partial.length) L.push('--  no named text in this stretch (its words are the subtitles, which follow the narration): nothing to time');
  for (const s of res.seen) {
    if (s.edge) { L.push(`--  ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  runs past the checked range: not judged`); continue; }
    const n = need(s.text), ok = s.run >= n - STEP; if (!ok) bad++;   // one step of slack for the sampling grid
    L.push(`${ok ? 'OK ' : 'BAD'} ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  need ${n.toFixed(2)}s  got ${s.run.toFixed(2)}s  ${JSON.stringify(s.text.slice(0, 24))}`);
  }
  for (const s of res.partial) { bad++; L.push(`BAD ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  never fully visible  ${JSON.stringify(s.text.slice(0, 24))}`); }
  for (const s of res.low || []) { bad++; L.push(`BAD ${s.id.padEnd(18)} at ${s.t0.toFixed(2)}s  sits on the subtitle strip  ${JSON.stringify(s.text.slice(0, 24))}`); }
  for (const o of res.over || []) { bad++; L.push(`BAD overlap            at ${o.t0.toFixed(2)}-${o.t1.toFixed(2)}s  ${JSON.stringify(o.a.slice(0, 24))} on ${JSON.stringify(o.b.slice(0, 24))}`); }
  // a pin never drawn whole and opaque (no room for its box above its anchor, off screen or under a clip all its time) is in none
  // of the lists above, so it would pass unseen. A pin that crosses --from/--to may show outside: not judged
  const drawn = new Set([...res.seen, ...res.partial].map(s => s.id)), last = TO == null ? FILM.dur : Math.min(FILM.dur, +TO);
  for (const p of FILM.pins || []) {
    if (drawn.has(String(p.id)) || p.t0 < FROM || Math.min(p.t1, FILM.dur) > last) continue;
    if (p.unseen_ok) { L.push(`--  ${String(p.id).padEnd(18)} at ${p.t0.toFixed(2)}s  never drawn: accepted (unseen_ok)`); continue; }
    bad++; L.push(`BAD ${String(p.id).padEnd(18)} at ${p.t0.toFixed(2)}s  never drawn  ${JSON.stringify(String(p.text || '').slice(0, 24))}`);
  }
  return [bad ? 1 : 0, L];
}
const OUT = SPANS.map(([FROM, TO], i) => { const [code, lines] = judge(RES[i], FROM, TO); return { from: FROM, to: TO == null ? null : +TO, code, ok: code === 0, lines }; });
for (const o of OUT) {
  if (OUT.length > 1) console.log(`readcheck ${o.from}-${o.to} s:`);
  for (const l of o.lines) (o.code === 2 ? console.error : console.log)(l);
}
const jf = opt('--json', null); if (jf) fs.writeFileSync(jf, JSON.stringify(OUT, null, 1));
process.exit(Math.max(...OUT.map(o => o.code)));   // (several stretches: the worst)
