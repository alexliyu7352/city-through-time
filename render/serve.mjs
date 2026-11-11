// Static server for the page (adapted from lemo-opuscar core/render/serve.mjs, MIT; see NOTICE): ES modules do not load over
// file://. It serves the project root, listens on 127.0.0.1 only, answers only Host 127.0.0.1 / localhost (against DNS
// rebinding) and never a file outside the root. An address ending in / is its folder's index.html; with `overlay`, a folder of
// generated files (tools/site.mjs) is looked in first; `files` maps an address to one file anywhere (a finished film kept on another
// disk, review.html). A request for part of a file (Range: a video seeked into) gets that part: a long film plays from anywhere.
import http from 'http'; import fs from 'fs'; import path from 'path';
import { ROOT } from './local.mjs';

// text is always declared UTF-8
const T = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.map': 'application/json',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf',
  '.wav': 'audio/wav', '.m4a': 'audio/mp4', '.mp3': 'audio/mpeg', '.mp4': 'video/mp4', '.webm': 'video/webm' };

export const pageURL = (port, q = '', html = 'play.html') => `http://127.0.0.1:${port}/${html}${q ? '?' + q : ''}`;   // (html: another page of the project, museum.html)

// URL path -> file on disk; { status } when it leaves the root, does not decode, or holds a NUL
export function resolveRequest(url, root = ROOT) {
  let u; try { u = decodeURIComponent(url.split('?')[0].split('#')[0]); } catch { return { status: 400 }; }
  if (u.includes('\0')) return { status: 400 };
  const p = path.resolve(root, '.' + path.sep + u.replace(/^\/+/, ''));
  if (p !== root && !p.startsWith(root + path.sep)) return { status: 403 };
  return { path: u.endsWith('/') ? path.join(p, 'index.html') : p };
}

export function serve(port = 0, { overlay, files = {} } = {}) {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      const send = (code, body) => { r.writeHead(code, { 'Content-Type': 'text/plain' }); r.end(body); };
      try {
        if (!/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(q.headers.host || '')) return send(403, 'bad host');
        const named = files[decodeURIComponent(q.url.split('?')[0])];
        const x = named ? { path: named } : resolveRequest(q.url);
        if (x.status) return send(x.status, x.status === 403 ? 'outside root' : 'bad request');
        const o = overlay && resolveRequest(q.url, overlay);
        // (a city's packed bundle, cities/<slug>/dist/web/, answers for cities/<slug>/web/ where the folder is not: where the site has it, tools/registry.mjs)
        const p = !fs.existsSync(x.path) && resolveRequest(q.url.replace(/^\/(cities\/[^/]+\/)web\//, '/$1dist/web/'));
        const file = named || (o && o.path && fs.existsSync(o.path) ? o.path : p && p.path && fs.existsSync(p.path) ? p.path : x.path);
        if (fs.existsSync(file) && fs.statSync(file).isDirectory()) { r.writeHead(301, { Location: q.url.split('?')[0] + '/' }); return r.end(); }
        const type = T[path.extname(file).toLowerCase()] || 'application/octet-stream', size = fs.existsSync(file) ? fs.statSync(file).size : 0;
        const rg = /^bytes=(\d*)-(\d*)$/.exec(q.headers.range || '');
        if (size && (rg || size > 32 << 20)) {   // a part of the file, or a big one streamed whole
          let a = 0, b = size - 1;
          if (rg) { a = rg[1] ? +rg[1] : size - +rg[2]; b = rg[1] && rg[2] ? Math.min(+rg[2], size - 1) : size - 1; }
          if (!(a >= 0 && a <= b)) { r.writeHead(416, { 'Content-Range': `bytes */${size}` }); return r.end(); }
          r.writeHead(rg ? 206 : 200, { 'Content-Type': type, 'Content-Length': b - a + 1, 'Accept-Ranges': 'bytes', ...(rg ? { 'Content-Range': `bytes ${a}-${b}/${size}` } : {}) });
          return fs.createReadStream(file, { start: a, end: b }).on('error', () => r.destroy()).pipe(r);
        }
        fs.readFile(file, (e, d) => {
          if (e) return send(404, 'not found');
          r.writeHead(200, { 'Content-Type': type, 'Content-Length': d.length, 'Accept-Ranges': 'bytes' }); r.end(d);   // (the length: the player's loading screen)
        });
      } catch { send(400, 'bad request'); }
    });
    s.once('error', e => {   // (another preview, of this checkout or another, holds the port: say so rather than a stack)
      if (e.code !== 'EADDRINUSE') throw e;
      console.error(`port ${port} is in use (another preview?): give a free one, node tools/preview.mjs <slug> <port>`); process.exit(1);
    });
    s.listen(port, '127.0.0.1', () => res({ server: s, port: s.address().port }));
  });
}
