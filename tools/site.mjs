// The site as GitHub Pages serves it: the entry page in each language and every city's own page in each language, each with its
// own title, description, link preview (Open Graph) and video data, its words already in the HTML (search engines and link
// previews do not run the page's script), and sitemap.xml, robots.txt, 404.html. Generated, never committed: CI writes it on every
// push (.github/workflows/pages.yml), tools/preview.mjs for the local preview.
//   node tools/site.mjs [--out _site] [--origin https://cities.go5.si] [--copy] [--city <slug>|auto]
// --origin is where the site is served (CI passes what Pages reports); --copy also copies the repository's files (git ls-files)
// into --out, the whole site in one folder as CI publishes it.
// Addresses: <origin>/ and <origin>/<slug>/ in English, <origin>/<lang>/ and <origin>/<lang>/<slug>/ in the others (ja, zh-hant,
// zh-hans, es); site/app.js reads them the same way. A city's slug may not take a name the site already uses (tools/registry.mjs).
// --city: a site of that one city alone, a user's own (tools/deploy.mjs): the gallery is the project's site, not one to copy. The
// city's page is the site's root, <origin>/ in English and <origin>/<lang>/ in the others, with its player, walk-round, museum
// pages and posters, and with --copy its web bundle (bundles()); no entry page, globe, search, collection or other city, and a
// credit to the project. index.html marks the parts of each kind of site (<!-- gallery --> … <!-- /gallery -->, <!-- city -->
// … <!-- /city -->). The pages, play.html and museum.html carry <html data-city="<slug>">: their links to the city's page lead to
// the root (site/app.js, engine/view.js, site/museum.js). --origin defaults to https://<slug>.pages.dev, the address
// tools/deploy.mjs gives it by default. --city auto (pickCity): the city in cities/ that is not the example; with none, the
// example itself, as a demo; with several, it stops: name one.
import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process'; import { fileURLToPath } from 'url';
import { ROOT, EXAMPLE, build, entries } from './registry.mjs';
import { LANGS, words, credit } from '../site/i18n.js';
import { embed } from '../site/video.js';

const LOCALE = { en: 'en_US', ja: 'ja_JP', 'zh-Hant': 'zh_TW', 'zh-Hans': 'zh_CN', es: 'es_ES' };
const prefix = l => l === 'en' ? '' : l.toLowerCase() + '/';
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const MARK = '.generated';   // (a folder holding it was written here, and may be cleared)
// the repository's files a single city's site leaves out besides the other cities: the gallery's own (the globe and the land it is
// drawn from, the stills of how a film is made, the gallery's share picture)
const GALLERY_ONLY = ['site/globe.js', 'site/land.bin', 'site/img/'];

// --city auto: the user's own city, the one folder in cities/ that is not the example's; with none, the example (a demo)
export function pickCity(city) {
  if (city !== 'auto') return city;
  const dir = path.join(ROOT, 'cities');   // (a city's folder may be a link to another disk: stat follows it)
  const own = fs.readdirSync(dir).filter(n => !n.startsWith('.') && n !== EXAMPLE && fs.existsSync(path.join(dir, n)) && fs.statSync(path.join(dir, n)).isDirectory()).sort();
  if (own.length > 1) throw new Error(`--city auto: cities/ has ${own.length} cities besides the example (${own.join(', ')}): name one, --city <slug>`);
  return own[0] || EXAMPLE;
}

// a city's entry.json where the site does not have it (the page reads it when the city opens; a city not yet committed is not among
// the repository's files); and where the entry points into cities/<slug>/web/ (as a path, or as its full address on this site, the
// form a pull request to the shared portal takes), that folder when the repository does not have it: its packed bundle (tools/web.py),
// or with no player bundle (bundle null) only the posters, since the bundle may hold sound not cleared for the web. slugs: only these
export function bundles(out, origin, slugs) {
  for (const { slug, e } of entries()) {
    if (slugs && !slugs.includes(slug)) continue;
    const f = `cities/${slug}/entry.json`;
    if (!fs.existsSync(path.join(out, f))) fs.cpSync(path.join(ROOT, f), path.join(out, f));
    const web = `cities/${slug}/web/`, own = u => typeof u === 'string' ? (u.startsWith(`${origin}/`) ? u.slice(origin.length + 1) : u) : '';
    const used = [e.bundle?.url, e.poster, e.thumb].map(own).filter(u => u.startsWith(web)), whole = own(e.bundle?.url) === web;
    if (!used.length || fs.existsSync(path.join(out, web, 'bundle.json'))) continue;   // (on another host; or in the repository, the example city's)
    const from = [path.join(ROOT, web), path.join(ROOT, 'cities', slug, 'dist', 'web')].find(d => fs.existsSync(path.join(d, 'bundle.json')));
    if (!from) throw new Error(`cities/${slug}/entry.json points into ${web}, and there is no packed bundle: uv run python -I tools/web.py cities/${slug}`);
    for (const f of whole ? [''] : used.map(u => u.slice(web.length))) fs.cpSync(path.join(from, f), path.join(out, web, f), { recursive: true, dereference: true });
    console.log(`${web}: ${whole ? 'the web bundle' : 'the posters'}, from ${path.relative(ROOT, from)}`);
  }
}

export function site({ out = path.join(ROOT, '_site'), origin, copy = false, city = null } = {}) {
  city = city && pickCity(city);
  origin = (origin || (city ? `https://${city}.pages.dev` : 'https://cities.go5.si')).replace(/\/+$/, '');
  const base = new URL(origin + '/').pathname;   // '/' on the site's own domain
  out = path.resolve(out);
  if (out === ROOT || ROOT.startsWith(out + path.sep)) throw new Error(`--out ${out}: the site is written to a folder of its own (it is cleared on the next run)`);
  let reg = build();
  if (city) {   // the one city, as the gallery lists it (an entry with problems is left off the gallery: here it stops the site)
    const c = reg.cities.find(x => x.slug === city);
    if (!c) throw new Error(fs.existsSync(path.join(ROOT, 'cities', city, 'entry.json'))
      ? `cities/${city}/entry.json has problems, and a city's site is made only from an entry that passes: node tools/registry.mjs --check`
      : `--city ${city}: there is no cities/${city}/entry.json (cities with one: ${entries().map(x => x.slug).join(', ') || 'none'}; tools/web.py --entry writes a draft)`);
    reg = { ...reg, cities: [c] };
  }
  if (fs.existsSync(path.join(out, MARK))) fs.rmSync(out, { recursive: true });
  fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(path.join(out, MARK), '');
  const put = (rel, body) => { const f = path.join(out, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, body); };
  const left = f => city && (GALLERY_ONLY.some(g => f.startsWith(g)) || (f.startsWith('cities/') && !f.startsWith(`cities/${city}/`)));
  if (copy) for (const f of execFileSync('git', ['-C', ROOT, 'ls-files', '-z'], { encoding: 'utf8' }).split('\0')) {
    if (f && !left(f) && fs.existsSync(path.join(ROOT, f))) put(f, fs.readFileSync(path.join(ROOT, f)));
  }

  put('cities.json', JSON.stringify(reg) + '\n');
  // the template's parts for this kind of site, the marks taken out (whole lines: the pages do not depend on them)
  const kind = city ? 'city' : 'gallery';
  let template = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8')
    .replace(/^[ \t]*<!-- (gallery|city)\b.*?-->\n[^]*?^[ \t]*<!-- \/\1 -->\n/gm, (part, k) => k === kind ? part : '')
    .replace(/^[ \t]*<!-- \/?(gallery|city)\b.*?-->\n/gm, '');
  if (city) {   // the city's panel is the page itself: open, not a dialog, its name the page's heading
    const panel = '<aside class="panel" id="panel" hidden aria-labelledby="panel-name" role="dialog">';
    if (!template.includes(panel) || !template.includes('<h2 id="panel-name"></h2>')) throw new Error(`index.html: no ${panel} with its <h2 id="panel-name"> to make the city's page of`);
    template = template.replace(panel, '<main class="panel" id="panel" aria-labelledby="panel-name">').replace('</aside>', '</main>')
      .replace('<h2 id="panel-name"></h2>', '<h1 id="panel-name"></h1>');
  }
  const blocks = fs.readFileSync(path.join(ROOT, 'site/land.bin')).readUInt32LE(0);
  const entry = slug => JSON.parse(fs.readFileSync(path.join(ROOT, 'cities', slug, 'entry.json'), 'utf8'));
  const url = (l, slug) => `${origin}/${prefix(l)}${slug && !city ? slug + '/' : ''}`;   // (a single city's page: the root)
  const abs = u => /^https:/.test(u) ? u : `${origin}/${u}`;

  function page(l, e, { missing = false } = {}) {
    const W = words(l), name = e && W.of(e.name);
    const title = e ? `${name} · ${W.cjk ? '一城春秋' : W.t('tagline')}` : `一城春秋 · ${W.t('tagline')}`;
    const desc = e ? W.of(e.summary) : W.t('lede'), image = e ? abs(e.poster) : `${origin}/site/img/og.jpg`, here = url(l, e?.slug);
    const film = e && (e.watch || []).map(v => embed(v.url, false)).find(Boolean);
    const ld = e && { '@context': 'https://schema.org', '@type': 'VideoObject', name: title, description: desc, thumbnailUrl: [image], uploadDate: e.added,
      duration: `PT${Math.floor(e.duration / 60)}M${Math.round(e.duration % 60)}S`, url: here, ...(film ? { embedUrl: film } : {}), inLanguage: e.narration,
      creator: e.authors.map(a => ({ '@type': 'Person', name: a.name, ...(a.url ? { url: a.url } : {}) })), license: 'https://creativecommons.org/licenses/by-sa/4.0/' };
    const head = [
      `<title>${esc(title)}</title>`,
      `<meta name="description" content="${esc(desc)}">`,
      ...(missing ? ['<meta name="robots" content="noindex">'] : [`<link rel="canonical" href="${here}">`,
        ...LANGS.map(([k]) => `<link rel="alternate" hreflang="${k}" href="${url(k, e?.slug)}">`), `<link rel="alternate" hreflang="x-default" href="${url('en', e?.slug)}">`]),
      `<meta property="og:site_name" content="一城春秋 · A City Through Time">`,
      `<meta property="og:type" content="${e ? 'video.other' : 'website'}">`,
      `<meta property="og:title" content="${esc(title)}">`,
      `<meta property="og:description" content="${esc(desc)}">`,
      `<meta property="og:url" content="${here}">`,
      `<meta property="og:image" content="${esc(image)}">`,
      `<meta property="og:image:alt" content="${esc(e ? name : title)}">`,
      `<meta property="og:locale" content="${LOCALE[l]}">`,
      ...LANGS.filter(([k]) => k !== l).map(([k]) => `<meta property="og:locale:alternate" content="${LOCALE[k]}">`),
      '<meta name="twitter:card" content="summary_large_image">',
      ...(ld ? [`<script type="application/ld+json">${JSON.stringify(ld).replace(/</g, '\\u003c')}</script>`] : []),
    ].join('\n');
    const repo = reg.repo, guide = k => `${repo}/blob/main/${W.guide(k)}`;
    const fill = (h, id, inner) => h.replace(new RegExp(`(<([a-z][a-z0-9]*)\\b[^>]*\\bid="${id}"[^>]*>)[^<]*(</\\2>)`), (_, open, tag, close) => open + inner + close);
    // the page's own files by their path from the site's root (no <base>: it would turn every #link and the icons' #refs into the root page's)
    let h = template
      .replace(/<!-- head:[^]*?<!-- \/head -->/, head)
      .replace(/ href="\.\/"/g, ` href="${base}${prefix(l)}"`)
      .replace(/ (href|src)="(?!https?:|data:|#|\/)([^"]*)"/g, (_, a, u) => ` ${a}="${base}${u}"`)
      .replace('<html lang="en">', `<html lang="${l}"${city ? ` data-city="${city}"` : ''}>`)
      .replace(/(<([a-z][a-z0-9]*)\b[^>]*\bdata-t="(\w+)"[^>]*>)[^<]*(<\/\2>)/g, (_, open, tag, k, close) => open + esc(W.t(k)) + close)
      .replace(/alt="" data-alt="(\w+)"/g, (_, k) => `alt="${esc(W.t(k))}" data-alt="${k}"`)
      .replace(/ data-guide="(\w+)"/g, (_, k) => ` href="${guide(k)}" data-guide="${k}"`)
      .replace(/ id="(gh|repo|repo-cta)"/g, (_, id) => ` id="${id}" href="${repo}"`)
      .replace(/ id="(q2?)" /g, (_, id) => ` id="${id}" placeholder="${esc(W.t('searchPlaceholder'))}" aria-label="${esc(W.t('searchLabel'))}" `);
    h = fill(h, 'caption-text', esc(W.fmt('exhibitText', { n: W.num(blocks) })));
    h = fill(h, 'lang-now', esc(LANGS.find(([k]) => k === l)[1]));
    if (city) h = fill(h, 'credit', credit(W, repo));
    if (e) {   // the city's panel, written out (the page's script opens it, and rebuilds it as it is used)
      const alt = l !== 'en' && e.name.en && e.name.en !== name ? e.name.en : '';
      h = fill(h, 'poster', `<img src="${esc(/^https:/.test(e.poster) ? e.poster : base + e.poster)}" alt="${esc(name)}">`);
      h = fill(h, 'panel-name', esc(name)); h = fill(h, 'panel-alt', esc(alt)); h = fill(h, 'panel-years', esc(W.span(e.years)));
      h = fill(h, 'summary', esc(desc));
      const links = (e.watch || []).map(v => `<a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(W.fmt('watchOn', { site: v.site }))}</a>`);
      if (links.length) h = fill(h, 'actions', `<p class="sites">${links.join('')}</p>`);
      const source = /^https?:/.test(e.source || '') ? e.source : `${repo}/tree/main/cities/${e.slug}`;
      h = h.replace(' id="source" ', ` id="source" href="${esc(source)}" `);
    }
    return h;
  }

  const pages = [];
  for (const [l] of LANGS) {
    if (!city) { put(`${prefix(l)}index.html`, page(l, null)); pages.push({ l, slug: null }); }   // (the entry page: the gallery's alone)
    for (const c of reg.cities) { const e = entry(c.slug); put(`${prefix(l)}${city ? '' : c.slug + '/'}index.html`, page(l, e)); pages.push({ l, slug: c.slug, added: e.added }); }
  }
  put('404.html', page('en', city ? entry(city) : null, { missing: true }));
  const alts = slug => LANGS.map(([k]) => `<xhtml:link rel="alternate" hreflang="${k}" href="${url(k, slug)}"/>`).join('');
  put('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' +
    pages.map(p => `<url><loc>${url(p.l, p.slug)}</loc>${p.added ? `<lastmod>${p.added}</lastmod>` : ''}${alts(p.slug)}</url>`).join('\n') + '\n</urlset>\n');
  put('robots.txt', `User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap.xml\n`);
  if (city) {   // the player and the museum pages, marked as this city's site: their link back to the film is its root
    for (const f of ['play.html', 'museum.html']) put(f, fs.readFileSync(path.join(ROOT, f), 'utf8').replace(/<html\b/, `<html data-city="${city}"`));
    if (copy) bundles(out, origin, [city]);
  }
  return { reg, pages: pages.length, out, city, origin };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2), arg = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
  try {
    if (args.includes('--city') && !/^[^-]/.test(arg('--city') || '')) throw new Error('--city takes a city\'s folder name, or auto');
    const r = site({ out: arg('--out') ? path.resolve(arg('--out')) : undefined, origin: arg('--origin') || undefined, copy: args.includes('--copy'), city: arg('--city') });
    console.log(r.city ? `site: ${r.pages} pages (${r.city} alone, in ${LANGS.length} languages, for ${r.origin}/) -> ${path.relative(ROOT, r.out) || '.'}`
      : `site: ${r.pages} pages (the entry page and ${r.reg.cities.length} cit${r.reg.cities.length === 1 ? "y" : "ies"}, in ${LANGS.length} languages) -> ${path.relative(ROOT, r.out) || '.'}`);
  } catch (e) { console.error(`site: ${e.message}`); process.exitCode = 1; }
}
