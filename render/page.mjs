// Opens a city's film in headless Chrome and waits for window.READY (adapted from lemo-opuscar core/render/page.mjs and
// browser.mjs, MIT; see NOTICE). Failures are loud: a JS error on the page, or a script or the page itself failing to load,
// exits non-zero at once; any other missing file (fetch, image, font) prints one warning, since the page has fallbacks.
// The browser: this machine's `chrome` (local/config.json) when set, else Playwright's own headless shell. The GPU is used
// when there is one; macOS asks for Metal (newer headless shells fall back to software GL with --use-angle=gl, ~6x slower).
import { chromium } from 'playwright-core';
import { serve, pageURL } from './serve.mjs';
import { localPath } from './local.mjs';

const ARGS = [...(process.platform === 'darwin' ? ['--use-angle=metal'] : []), '--enable-gpu', '--ignore-gpu-blocklist', '--font-render-hinting=none', '--force-color-profile=srgb'];
let srv = null;
export async function server() { if (!srv) srv = await serve(); return srv; }
export function closeServer() { if (srv) srv.server.close(); }

// --size WxH (default 1920x1080), taken out of args; even numbers from 16 to 8192 (H.264 yuv420p)
export function takeSize(args) {
  const i = args.indexOf('--size'); if (i < 0) return { w: 1920, h: 1080 };
  const v = args.splice(i, 2)[1] || '', m = /^(\d+)x(\d+)$/.exec(v), w = m && +m[1], h = m && +m[2];
  if (!m || [w, h].some(n => n < 16 || n > 8192 || n % 2)) { console.error(`bad --size "${v}": use WxH with even numbers from 16 to 8192, e.g. 1080x1920`); process.exit(2); }
  return { w, h };
}

let warnedGL = false;
async function warnIfSoftwareGL(page) {
  if (warnedGL) return; warnedGL = true;
  try {
    const r = await page.evaluate(() => {
      const c = document.createElement('canvas'), g = c.getContext('webgl2') || c.getContext('webgl'); if (!g) return null;
      const e = g.getExtension('WEBGL_debug_renderer_info'), name = e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : '';
      g.getExtension('WEBGL_lose_context')?.loseContext(); return String(name);
    });
    if (r && /swiftshader|llvmpipe|software/i.test(r)) console.error(`[note] WebGL runs on software rendering (${r.slice(0, 80)}): renders will be slow. Linux needs GPU drivers.`);
  } catch {}
}

const warned = new Set();   // each optional file warns once per process (video.mjs opens several pages)
const FATAL = new Set(['script', 'document']);   // module imports are scripts too
export async function openFilm(city, { w = 1920, h = 1080, q = '', warnings = false } = {}) {
  const { port } = await server();
  const browser = await chromium.launch({ executablePath: localPath('chrome') || undefined, args: ARGS });
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const log = [];   // the latest problems, printed with the hint when READY is slow
  const note = s => { log.push(s); if (log.length > 8) log.shift(); console.error(s); };
  page.on('console', m => {
    const t = m.text();
    if (m.type() === 'error' && /^Failed to load resource/.test(t)) return;   // the response handler prints it with its URL
    if (m.type() === 'error' || (warnings && m.type() === 'warning')) note('[page] ' + t.slice(0, 300));
  });
  page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exit(1); });   // stop rather than make a broken film
  page.on('response', r => {
    if (r.status() < 400) return;
    const u = r.url(), p = new URL(u).pathname, type = r.request().resourceType();
    if (p === '/favicon.ico') return;
    if (FATAL.has(type)) { note(`[page] ${r.status()} ${u}`); console.error(`the page needs ${p} (a ${type}) but the server answered ${r.status()}`); process.exit(1); }
    if (!warned.has(u)) { warned.add(u); note(`[page] optional file missing: ${u} (${r.status()}, ${type}; fine if the page has a fallback)`); }
  });
  page.on('requestfailed', r => { if (!/favicon/.test(r.url()) && r.failure()?.errorText !== 'net::ERR_ABORTED') note(`[page] request failed ${r.url()} (${r.failure()?.errorText})`); });
  await page.goto(pageURL(port, `city=${encodeURIComponent(city)}` + (q ? '&' + q : '')));
  const hint = setTimeout(() => console.error('still waiting for window.READY after 60 s' + (log.length ? '; problems so far:\n    ' + log.join('\n    ') : '')), 60000);
  const t0 = Date.now();
  try { await page.waitForFunction(() => window.READY === true, null, { timeout: 180000 }); }
  catch (e) { console.error(`window.READY never became true (waited ${((Date.now() - t0) / 1000).toFixed(0)} s): ${e.message.split('\n')[0]}`); process.exit(1); }
  finally { clearTimeout(hint); }
  await warnIfSoftwareGL(page);
  return { browser, page };
}
