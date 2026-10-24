// The site as GitHub Pages serves it: the entry page in each language and every city's own page in each language, each with its
// own title, description, link preview (Open Graph) and video data, its words already in the HTML (search engines and link
// previews do not run the page's script), and sitemap.xml, robots.txt, 404.html. Generated, never committed: CI writes it on every
// push (.github/workflows/pages.yml), tools/preview.mjs for the local preview.
//   node tools/site.mjs [--out _site] [--origin https://cities.go5.si] [--copy]
// --origin is where the site is served (CI passes what Pages reports); --copy also copies the repository's files (git ls-files)
// into --out, the whole site in one folder as CI publishes it.
// Addresses: <origin>/ and <origin>/<slug>/ in English, <origin>/<lang>/ and <origin>/<lang>/<slug>/ in the others (ja, zh-hant,
// zh-hans, es); site/app.js reads them the same way. A city's slug may not take a name the site already uses (tools/registry.mjs).
import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process'; import { fileURLToPath } from 'url';
import { ROOT, build } from './registry.mjs';
import { LANGS, words } from '../site/i18n.js';
import { embed } from '../site/video.js';

const LOCALE = { en: 'en_US', ja: 'ja_JP', 'zh-Hant': 'zh_TW', 'zh-Hans': 'zh_CN', es: 'es_ES' };
const prefix = l => l === 'en' ? '' : l.toLowerCase() + '/';
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const MARK = '.generated';   // (a folder holding it was written here, and may be cleared)

export function site({ out = path.join(ROOT, '_site'), origin = 'https://cities.go5.si', copy = false } = {}) {
  origin = origin.replace(/\/+$/, '');
  const base = new URL(origin + '/').pathname;   // '/' on the site's own domain
  out = path.resolve(out);
  if (out === ROOT || ROOT.startsWith(out + path.sep)) throw new Error(`--out ${out}: the site is written to a folder of its own (it is cleared on the next run)`);
  if (fs.existsSync(path.join(out, MARK))) fs.rmSync(out, { recursive: true });
  fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(path.join(out, MARK), '');
  const put = (rel, body) => { const f = path.join(out, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, body); };
  if (copy) for (const f of execFileSync('git', ['-C', ROOT, 'ls-files', '-z'], { encoding: 'utf8' }).split('\0')) {
    if (f && fs.existsSync(path.join(ROOT, f))) put(f, fs.readFileSync(path.join(ROOT, f)));
  }

  const reg = build(); put('cities.json', JSON.stringify(reg) + '\n');
  const template = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const blocks = fs.readFileSync(path.join(ROOT, 'site/land.bin')).readUInt32LE(0);
  const entry = slug => JSON.parse(fs.readFileSync(path.join(ROOT, 'cities', slug, 'entry.json'), 'utf8'));
  const url = (l, slug) => `${origin}/${prefix(l)}${slug ? slug + '/' : ''}`;
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
      `<base href="${base}">`,
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
    let h = template
      .replace(/<!-- head:[^]*?<!-- \/head -->/, head)
      .replace('<html lang="en">', `<html lang="${l}">`)
      .replace(/(<([a-z][a-z0-9]*)\b[^>]*\bdata-t="(\w+)"[^>]*>)[^<]*(<\/\2>)/g, (_, open, tag, k, close) => open + esc(W.t(k)) + close)
      .replace(/alt="" data-alt="(\w+)"/g, (_, k) => `alt="${esc(W.t(k))}" data-alt="${k}"`)
      .replace(/ data-guide="(\w+)"/g, (_, k) => ` href="${guide(k)}" data-guide="${k}"`)
      .replace(/ id="(gh|repo|repo-cta)"/g, (_, id) => ` id="${id}" href="${repo}"`)
      .replace(/ id="(q2?)" /g, (_, id) => ` id="${id}" placeholder="${esc(W.t('searchPlaceholder'))}" aria-label="${esc(W.t('searchLabel'))}" `);
    h = fill(h, 'caption-text', esc(W.fmt('exhibitText', { n: W.num(blocks) })));
    h = fill(h, 'lang-now', esc(LANGS.find(([k]) => k === l)[1]));
    if (e) {   // the city's panel, written out (the page's script opens it, and rebuilds it as it is used)
      const alt = l !== 'en' && e.name.en && e.name.en !== name ? e.name.en : '';
      h = fill(h, 'poster', `<img src="${esc(e.poster)}" alt="${esc(name)}">`);
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
    put(`${prefix(l)}index.html`, page(l, null)); pages.push({ l, slug: null });
    for (const c of reg.cities) { const e = entry(c.slug); put(`${prefix(l)}${c.slug}/index.html`, page(l, e)); pages.push({ l, slug: c.slug, added: e.added }); }
  }
  put('404.html', page('en', null, { missing: true }));
  const alts = slug => LANGS.map(([k]) => `<xhtml:link rel="alternate" hreflang="${k}" href="${url(k, slug)}"/>`).join('');
  put('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' +
    pages.map(p => `<url><loc>${url(p.l, p.slug)}</loc>${p.added ? `<lastmod>${p.added}</lastmod>` : ''}${alts(p.slug)}</url>`).join('\n') + '\n</urlset>\n');
  put('robots.txt', `User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap.xml\n`);
  return { reg, pages: pages.length, out };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2), arg = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
  const r = site({ out: arg('--out') ? path.resolve(arg('--out')) : undefined, origin: arg('--origin') || undefined, copy: args.includes('--copy') });
  console.log(`site: ${r.pages} pages (the entry page and ${r.reg.cities.length} cit${r.reg.cities.length === 1 ? "y" : "ies"}, in ${LANGS.length} languages) -> ${path.relative(ROOT, r.out) || '.'}`);
}
