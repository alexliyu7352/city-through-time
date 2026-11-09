// Live preview: serves the project and prints the URLs to open in Chrome (the film, and the site: the entry page and the cities'
// own pages, generated into _site/ as Cloudflare's build does, tools/site.mjs).
//   node tools/preview.mjs <city_slug> [port] [--film <file>] [--at s,s:label,...]
// The finished film to review (review.html: the second it is at, notes, given moments): --film, or cities/<slug>/dist/<slug>.mp4.
// The page runs the real render(t) with a transport bar: space = play/pause, ←/→ = one frame, shift+←/→ = 5 s.
// quality=low (default in play mode) renders without supersampling and without the period cities' shadows; add &quality=high to compare.
// &view instead of &play: the period cities alone, to turn round with the mouse (engine/view.js).
import fs from 'fs'; import path from 'path';
import { serve, pageURL } from '../render/serve.mjs';
import { ROOT } from './registry.mjs';
import { site } from './site.mjs';
const args = process.argv.slice(2), opt = k => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const filmArg = opt('--film'), at = opt('--at');
const city = args[0] || 'xianyang', port = +(args[1] || 8765);
const film = path.resolve(filmArg || path.join(ROOT, 'cities', city, 'dist', `${city}.mp4`));
const { reg } = site({ origin: `http://127.0.0.1:${port}` });   // cities.json and the pages, from every cities/<slug>/entry.json
const { server } = await serve(port, { overlay: path.join(ROOT, '_site'), files: fs.existsSync(film) ? { '/review/film.mp4': film } : {} });
console.log(`preview: ${pageURL(port, `city=${city}&play=1`)}`);
console.log(`period cities from every side: ${pageURL(port, `city=${city}&view`)}`);
if (fs.existsSync(film)) console.log(`review the finished film: http://127.0.0.1:${port}/review.html?title=${encodeURIComponent(city)}${at ? '&at=' + encodeURIComponent(at) : ''}`);
else if (filmArg) console.log(`no film at ${film}`);
console.log(`entry page: http://127.0.0.1:${port}/  (${reg.cities.length} cities; each has its page, e.g. http://127.0.0.1:${port}/${reg.cities[0]?.slug || city}/)`);
console.log('press Ctrl+C to stop');
process.on('SIGINT', () => { server.close(); process.exit(0); });
