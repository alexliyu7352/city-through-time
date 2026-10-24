// Static server for the page (adapted from lemo-opuscar core/render/serve.mjs, MIT; see NOTICE): ES modules do not load over
// file://. It serves the project root, listens on 127.0.0.1 only, answers only Host 127.0.0.1 / localhost (against DNS
// rebinding) and never a file outside the root. An address ending in / is its folder's index.html; with `overlay`, a folder of
// generated files (tools/site.mjs) is looked in first.
import http from 'http'; import fs from 'fs'; import path from 'path';
import { ROOT } from './local.mjs';

// text is always declared UTF-8
const T = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.map': 'application/json',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf',
  '.wav': 'audio/wav', '.m4a': 'audio/mp4', '.mp3': 'audio/mpeg', '.mp4': 'video/mp4', '.webm': 'video/webm' };

export const pageURL = (port, q = '') => `http://127.0.0.1:${port}/play.html${q ? '?' + q : ''}`;

// URL path -> file on disk; { status } when it leaves the root, does not decode, or holds a NUL
export function resolveRequest(url, root = ROOT) {
  let u; try { u = decodeURIComponent(url.split('?')[0].split('#')[0]); } catch { return { status: 400 }; }
  if (u.includes('\0')) return { status: 400 };
  const p = path.resolve(root, '.' + path.sep + u.replace(/^\/+/, ''));
  if (p !== root && !p.startsWith(root + path.sep)) return { status: 403 };
  return { path: u.endsWith('/') ? path.join(p, 'index.html') : p };
}

export function serve(port = 0, { overlay } = {}) {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      const send = (code, body) => { r.writeHead(code, { 'Content-Type': 'text/plain' }); r.end(body); };
      try {
        if (!/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(q.headers.host || '')) return send(403, 'bad host');
        const x = resolveRequest(q.url);
        if (x.status) return send(x.status, x.status === 403 ? 'outside root' : 'bad request');
        const o = overlay && resolveRequest(q.url, overlay), file = o && o.path && fs.existsSync(o.path) ? o.path : x.path;
        if (fs.existsSync(file) && fs.statSync(file).isDirectory()) { r.writeHead(301, { Location: q.url.split('?')[0] + '/' }); return r.end(); }
        fs.readFile(file, (e, d) => {
          if (e) return send(404, 'not found');
          r.writeHead(200, { 'Content-Type': T[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': d.length }); r.end(d);   // (the length: the player's loading screen)
        });
      } catch { send(400, 'bad request'); }
    });
    s.listen(port, '127.0.0.1', () => res({ server: s, port: s.address().port }));
  });
}
