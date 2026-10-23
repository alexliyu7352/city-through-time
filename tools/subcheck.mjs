// Subtitle single-line check, measured in the page with the real fonts: every line must be narrower than the safe width.
// usage: node tools/subcheck.mjs <city_slug>     exit 1 if any line is too wide
import { openFilm, closeServer } from '../render/page.mjs';
const city = process.argv[2];
const { browser, page } = await openFilm(city);
const r = await page.evaluate(() => window.SUBCHECK);
await browser.close(); closeServer();
console.log(`safe width ${r.safe}px (one line per language, measured with the burned-in fonts)`);
for (const c of r.cues) console.log(`${c.ok ? 'OK  ' : 'WIDE'} ${c.id.padEnd(4)} a ${String(c.wa).padStart(4)}px  b ${String(c.wb).padStart(4)}px   ${c.a} | ${c.b || ''}`);
console.log(r.ok ? 'all subtitle lines fit on one line' : 'some lines are too wide');
process.exit(r.ok ? 0 : 1);
