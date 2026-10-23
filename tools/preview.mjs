// Live preview: serves the project and prints the URLs to open in Chrome (the film, and the entry page that reads cities.json).
//   node tools/preview.mjs <city_slug> [port]
// The page runs the real render(t) with a transport bar: space = play/pause, ←/→ = one frame, shift+←/→ = 5 s.
// quality=low (default in play mode) renders without supersampling and ambient occlusion; add &quality=high to compare.
import { serve, pageURL } from '../render/serve.mjs';
const city = process.argv[2] || 'xianyang', port = +(process.argv[3] || 8765);
const { server } = await serve(port);
console.log(`preview: ${pageURL(port, `city=${city}&play=1`)}`);
console.log(`entry page: http://127.0.0.1:${port}/index.html`);
console.log('press Ctrl+C to stop');
process.on('SIGINT', () => { server.close(); process.exit(0); });
