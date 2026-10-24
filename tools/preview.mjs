// Live preview: serves the project and prints the URLs to open in Chrome (the film, and the entry page that reads cities.json).
//   node tools/preview.mjs <city_slug> [port]
// The page runs the real render(t) with a transport bar: space = play/pause, ←/→ = one frame, shift+←/→ = 5 s.
// quality=low (default in play mode) renders without supersampling and ambient occlusion; add &quality=high to compare.
import { serve, pageURL } from '../render/serve.mjs';
import { build } from './registry.mjs';
const city = process.argv[2] || 'xianyang', port = +(process.argv[3] || 8765);
const reg = build();   // cities.json, the entry page's index, from every cities/<slug>/entry.json (CI does the same for GitHub Pages)
const { server } = await serve(port);
console.log(`preview: ${pageURL(port, `city=${city}&play=1`)}`);
console.log(`entry page: http://127.0.0.1:${port}/index.html  (${reg.cities.length} cities in cities.json)`);
console.log('press Ctrl+C to stop');
process.on('SIGINT', () => { server.close(); process.exit(0); });
