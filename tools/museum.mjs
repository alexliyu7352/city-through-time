// A museum page's stills (museum.html, docs/MUSEUM.md), after tools/museum.py has built it.
// usage: node tools/museum.mjs still <city> <page> <viewpoint>[,<viewpoint>..] [--out <dir>] [--name <file.jpg>]
//          the model alone at the viewpoint, 1920 x 1080, the reference look (what tools/living.py ref gives the image tool)
//        node tools/museum.mjs shots <city> <page> [--out <dir>] [--lang zh|en]
//          the page as a visitor sees it: at the main viewpoint (its picture), turned 15 and 30 degrees (the picture fading),
//          the white model with its sourced and estimated parts, a part's note open; at desktop size (1600 x 1000) and at a
//          phone's (390 x 844, 3 pixels to each); default cities/<city>/build/review/museum/<page>/
import fs from 'fs'; import path from 'path';
import { openFilm, closeServer, shot } from '../render/page.mjs';
import { buildDir } from '../render/local.mjs';

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
const out = opt('--out', null), name = opt('--name', null), lang = opt('--lang', 'zh');
const [cmd, city, page, vp] = args;
if (!['still', 'shots'].includes(cmd) || !city || !page || (cmd === 'still' && !vp)) {
  console.error('usage: node tools/museum.mjs still <city> <page> <viewpoint> [--out <dir>] [--name <file.jpg>] | shots <city> <page> [--out <dir>] [--lang zh|en]'); process.exit(2); }
const dir = out || buildDir(city, 'review', 'museum', page); fs.mkdirSync(dir, { recursive: true });
const q = `id=${encodeURIComponent(page)}&lang=${lang}`;

if (cmd === 'still') {   // (several viewpoints, a,b,c: one page, each in turn)
  const vps = vp.split(','), { browser, page: P } = await openFilm(city, { q: `${q}&clean&vp=${encodeURIComponent(vps[0])}`, html: 'museum.html', warnings: true });
  for (const v of vps) {
    if (v !== vps[0]) await P.evaluate(v => window.MUSEUM({ vp: v }), v);
    const f = path.join(dir, vps.length === 1 && name ? name : `${v}_ref.jpg`);
    await shot(P, { path: f, type: 'jpeg', quality: 92 }, true); console.log(f);
  }
  await browser.close(); closeServer();
} else {
  const at = async (P, f, o) => { if (o) await P.evaluate(o => window.MUSEUM(o), o); await P.waitForTimeout(250); await shot(P, { path: path.join(dir, f), type: 'jpeg', quality: 88 }, true); console.log(path.join(dir, f)); };
  for (const [tag, view, dpr] of [['desktop', { width: 1600, height: 1000 }, 1], ['phone', { width: 390, height: 844 }, 3]]) {
    const { browser, page: P } = await openFilm(city, { q, html: 'museum.html', view, dpr, warnings: true });
    await at(P, `${tag}_0_picture.jpg`);
    await at(P, `${tag}_15deg.jpg`, { turn: 15 });
    await at(P, `${tag}_30deg.jpg`, { turn: 30 });
    if (tag === 'desktop') {
      await P.click('#tones'); await at(P, `${tag}_tones.jpg`, { turn: 40, up: 8 });
      await P.click('[data-part="main"]'); await at(P, `${tag}_part.jpg`);
    } else {
      await P.evaluate(() => { const t = document.getElementById('tones'); t.click(); }); await at(P, `${tag}_tones.jpg`, { turn: 40, up: 8 });
      await P.evaluate(() => document.querySelector('[data-part="main"]').click()); await at(P, `${tag}_part.jpg`);
      await P.evaluate(() => scrollTo(0, 0)); await P.screenshot({ path: path.join(dir, `${tag}_label.jpg`), type: 'jpeg', quality: 85, fullPage: true }); console.log(path.join(dir, `${tag}_label.jpg`));
    }
    await browser.close();
  }
  closeServer();
}
