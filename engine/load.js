// The film's files: every download started at once and counted, and on the live page (?play) the screen that says how far they
// are and when the film is ready (play.html #load). play.html loads this module on its own before main.js, so a page whose engine
// cannot start (three.js from the CDN, WebGL, a missing file) says so instead of staying black.
// A file's size comes from a manifest where there is one (a bundle's bundle.json, compile's fonts.faces bytes), else from its
// Content-Length when the body arrives as sent. A host that gzips gives the packed size while the body arrives unpacked: such a
// file weighs its Content-Length and counts when it is done. The bar never moves back, and reaches the end only when all are in.
// A bundle's file over a host's size limit comes in parts (tools/web.py), joined here: the page gets it whole.
import { LANGS, pick, words, cityPage } from '../site/i18n.js';

const QS = new URLSearchParams(location.search);
const lang = LANGS.some(([k]) => k === QS.get('lang')) ? QS.get('lang') : pick(navigator.languages);
const W = words(lang);
const $ = id => document.getElementById(id);
const box = $('load'), live = !!box && !box.hidden;   // (play.html shows it with ?play: never in renders and checks)
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const files = new Map();   // address -> { size, exact, got, done, p }
const known = new Map();   // address -> its size in a manifest
let planned = false, over = false, shown = 0, frame = 0;
const short = u => { try { return decodeURI(new URL(u, location.href).pathname).split('/').slice(-2).join('/'); } catch { return String(u); } };

if (live) {
  box.lang = lang;
  $('ld-what').textContent = W.t('loading');
  $('ld-retry').textContent = W.t('loadRetry'); $('ld-retry').onclick = () => location.reload();
  // a failure while loading: a script that did not load, an error thrown, a promise refused
  addEventListener('error', e => { if (e.target instanceof HTMLScriptElement) fail(W.t('loadCode')); else if (e instanceof ErrorEvent) fail(e.error?.message || e.message); }, true);   // (a script: one of the modules it imports, three.js from the CDN or the engine's own, did not arrive)
  addEventListener('unhandledrejection', e => fail(e.reason?.message || String(e.reason)));
}

function paint() {
  frame = 0;
  if (over || !planned) return;
  let w = 0, g = 0, all = true;
  for (const f of files.values()) {
    if (!f.done) all = false;
    if (f.size) { w += f.size; g += f.done ? f.size : f.exact ? Math.min(f.got, f.size) : 0; }
  }
  shown = all ? 1 : Math.max(shown, w ? Math.min(g / w, .99) : 0);
  box.classList.remove('wait');
  $('ld-bar').style.transform = `scaleX(${shown})`;
  $('ld-pct').textContent = `${Math.floor(shown * 100)}%`;
  $('ld-what').textContent = W.t(all ? 'loadPrep' : 'loading');   // all in: the model is being put together
}
const tick = () => { if (live && !frame) frame = requestAnimationFrame(paint); };

// a bundle's file packed in parts (tools/web.py: a file over the host's size limit): at its address, a small index of its parts
// beside it, which starts with this
const SPLIT = '{"split": "tools/web.py"';
function index(chunks) {
  const n = chunks.reduce((s, c) => s + c.length, 0); if (n > 4096) return null;
  const all = new Uint8Array(n); let o = 0; for (const c of chunks) { all.set(c, o); o += c.length; }
  const t = new TextDecoder().decode(all); return t.startsWith(SPLIT) ? JSON.parse(t) : null;
}

function start(url, optional) {
  const f = { size: known.get(url) || 0, exact: known.has(url), got: 0, done: false };
  const body = async (u, first) => {   // an address's body, its chunks counted as they arrive
    const r = await fetch(u).catch(() => { throw new Error(short(u)); });
    if (!r.ok) throw new Error(`${short(u)} (${r.status})`);
    if (first && !f.size) { const n = +r.headers.get('content-length'); if (n) { f.size = n; f.exact = !r.headers.get('content-encoding'); } }
    const rd = r.body.getReader(), parts = [];
    for (;;) { const { done, value } = await rd.read(); if (done) break; parts.push(value); f.got += value.length; tick(); }
    return { parts, type: r.headers.get('content-type') || '' };
  };
  f.p = (async () => {
    let { parts, type } = await body(url, true);
    const ix = index(parts);
    if (ix) {   // the parts, all at once, joined in order: the page gets the file whole
      f.size = ix.bytes; f.exact = true; f.got = 0;
      const at = new URL(url, location.href);
      parts = (await Promise.all(ix.parts.map(p => body(new URL(p, at).href)))).flatMap(b => b.parts);
      const n = parts.reduce((s, c) => s + c.length, 0);
      if (n !== ix.bytes) throw new Error(`${short(url)} (${n} of ${ix.bytes} bytes in its parts)`);
    }
    return new Blob(parts, { type });
  })().then(b => { f.done = true; tick(); return b; },
            e => { if (!optional) throw e; f.size = 0; f.done = true; tick(); return null; });   // (an optional file that is not there: null)
  files.set(url, f); tick();
  return f;
}

// sizes from a manifest ({address: bytes}), for files asked for already or still to come
export function sizes(map) {
  for (const [u, n] of Object.entries(map)) { if (!n) continue; known.set(u, n); const f = files.get(u); if (f) { f.size = n; f.exact = true; } }
  tick();
}
// start these downloads now (optional: a file that may be missing, then null)
export function want(urls, { optional = false } = {}) { for (const u of urls) if (u && !files.has(u)) start(u, optional); }
// every file the film needs has been asked for: from now on the bar counts against the whole
export function plan() { planned = true; tick(); }
// a file's contents (a Blob, null for an optional file that is missing); each is handed over once and not kept here
export function take(url, { optional = false } = {}) {
  let f = files.get(url);
  if (!f || !f.p) { files.delete(url); f = start(url, optional); }
  const p = f.p; f.p = null; return p;
}
export const json = async url => JSON.parse(await (await take(url)).text());
export const address = async (url, opt) => { const b = await take(url, opt); return b && URL.createObjectURL(b); };   // an object URL

// the film is ready to play: the screen fades out
export function done() {
  if (!live || over) return;
  over = true; shown = 1; $('ld-bar').style.transform = 'scaleX(1)'; $('ld-pct').textContent = '100%';
  box.classList.add('gone'); setTimeout(() => { box.hidden = true; }, reduced ? 0 : 700);
}
function fail(what) {
  if (!live || over) return;
  over = true; box.classList.remove('wait'); box.classList.add('failed');
  $('ld-what').textContent = W.fmt('loadFail', { what }); $('ld-pct').textContent = ''; $('ld-retry').hidden = false;
}
// the film cannot be drawn here (i18n gpuNone, gpuWeak, gpuLost): what is missing, what to do (another browser, a computer) and
// the film's page, never a black page; at any time, the loading screen gone or not. detail: the technical cause, small.
// -> false on a page without the loading screen (renders and checks stop on the error instead)
export function unable(key, detail = '') {
  if (!live) return false;
  over = true; box.hidden = false; box.classList.remove('wait', 'gone'); box.classList.add('failed', 'unable');
  $('ld-what').textContent = W.t(key); $('ld-pct').textContent = '';
  $('ld-tip').textContent = W.t('gpuTry'); $('ld-tip').hidden = false;
  $('ld-why').textContent = detail; $('ld-why').hidden = !detail;
  const film = $('ld-film'); film.textContent = W.t('gpuFilm'); film.href = cityPage(lang, QS.get('city') || '', document.documentElement.dataset.city); film.hidden = false;
  $('ld-retry').hidden = false;
  return true;
}
// can this browser draw the film at all? Asked before anything is downloaded: a WebGL 2 context. What its graphics can draw
// into and link is tried once the scene is made (engine/studio.js gpu)
export function drawable() {
  if (!live) return true;
  let g = null; try { g = document.createElement('canvas').getContext('webgl2'); } catch { /* none */ }
  if (!g) { unable('gpuNone', 'WebGL 2'); return false; }
  g.getExtension('WEBGL_lose_context')?.loseContext();   // (the page's own context comes next: phones allow few at once)
  return true;
}
