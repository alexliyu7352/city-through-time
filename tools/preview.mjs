// Live preview: serves the project and prints the URLs to open in Chrome (the film, and the site: the entry page and the cities'
// own pages, generated into _site/ as CI does for GitHub Pages, tools/site.mjs).
//   node tools/preview.mjs <city_slug> [port]
// The page runs the real render(t) with a transport bar: space = play/pause, ←/→ = one frame, shift+←/→ = 5 s.
// quality=low (default in play mode) renders without supersampling and ambient occlusion; add &quality=high to compare.
import path from 'path';
import { serve, pageURL } from '../render/serve.mjs';
import { ROOT } from './registry.mjs';
import { site } from './site.mjs';
const city = process.argv[2] || 'xianyang', port = +(process.argv[3] || 8765);
const { reg } = site({ origin: `http://127.0.0.1:${port}` });   // cities.json and the pages, from every cities/<slug>/entry.json
const { server } = await serve(port, { overlay: path.join(ROOT, '_site') });
console.log(`preview: ${pageURL(port, `city=${city}&play=1`)}`);
console.log(`entry page: http://127.0.0.1:${port}/  (${reg.cities.length} cities; each has its page, e.g. http://127.0.0.1:${port}/${reg.cities[0]?.slug || city}/)`);
console.log('press Ctrl+C to stop');
process.on('SIGINT', () => { server.close(); process.exit(0); });
