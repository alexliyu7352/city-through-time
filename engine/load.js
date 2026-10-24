// The film's files: every download started at once and counted, and on the live page (?play) the screen that says how far they
// are and when the film is ready (play.html #load). play.html loads this module on its own before main.js, so a page whose engine
// cannot start (three.js from the CDN, WebGL, a missing file) says so instead of staying black.
// A file's size comes from a manifest where there is one (a bundle's bundle.json, compile's fonts.faces bytes), else from its
// Content-Length when the body arrives as sent. A host that gzips gives the packed size while the body arrives unpacked: such a
// file weighs its Content-Length and counts when it is done. The bar never moves back, and reaches the end only when all are in.
import { LANGS, pick, words } from '../site/i18n.js';

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
  addEventListener('error', e => { if (e.target instanceof HTMLScriptElement) fail(short(e.target.src)); else if (e instanceof ErrorEvent) fail(e.error?.message || e.message); }, true);
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

function start(url, optional) {
  const f = { size: known.get(url) || 0, exact: known.has(url), got: 0, done: false };
  f.p = (async () => {
    const r = await fetch(url).catch(() => { throw new Error(short(url)); });
    if (!r.ok) throw new Error(`${short(url)} (${r.status})`);
    if (!f.size) { const n = +r.headers.get('content-length'); if (n) { f.size = n; f.exact = !r.headers.get('content-encoding'); } }
    const rd = r.body.getReader(), parts = [];
    for (;;) { const { done, value } = await rd.read(); if (done) break; parts.push(value); f.got += value.length; tick(); }
    return new Blob(parts, { type: r.headers.get('content-type') || '' });
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
