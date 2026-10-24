// The registry of cities: every cities/<slug>/entry.json -> cities.json, the small index the entry page reads at load (each city's
// full entry is read only when it is opened). cities.json is generated, never committed: CI writes it when it publishes GitHub
// Pages (.github/workflows/pages.yml), tools/preview.mjs writes it for the local preview.
//   node tools/registry.mjs                          write cities.json
//   node tools/registry.mjs --check [--base <ref>]   check every entry (CONTRIBUTING.md has the fields); with --base, also
//                                                    the files a pull request adds under cities/: text only (the films, their
//                                                    pictures, music and footage live on outside hosts, not in this repository;
//                                                    the example city, EXAMPLE, keeps its pictures)
import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process'; import { fileURLToPath } from 'url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LANGS = ['en', 'ja', 'zh-Hant', 'zh-Hans', 'es'];
const AI = ['narration', 'music', 'imagined'];
const TEXT = new Set(['.json', '.yaml', '.yml', '.md', '.txt', '.csv', '.geojson', '.py', '.sh']);   // what a city may bring
const NAMED = new Set(['CREDITS', 'LICENSE']);
const EXAMPLE = 'xianyang';   // the project's own example: kept whole, pictures and poster included
// a city's page is <site>/<slug>/ (tools/site.mjs): a slug may not be a name the site already has at its root, nor a language's
const RESERVED = new Set([...fs.readdirSync(path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')).map(n => n.toLowerCase()), ...LANGS.map(l => l.toLowerCase()), 'en']);
const https = u => typeof u === 'string' && /^https:\/\/\S+$/.test(u);
const local = u => typeof u === 'string' && !u.startsWith('/') && !u.includes('..') && fs.existsSync(path.join(ROOT, u));   // (a path in this repository: the example city's)
const image = u => https(u) || local(u);

function repoURL() {
  if (process.env.GITHUB_REPOSITORY) return `https://github.com/${process.env.GITHUB_REPOSITORY}`;
  try {
    const u = execFileSync('git', ['-C', ROOT, 'remote', 'get-url', 'origin'], { encoding: 'utf8' }).trim();
    const m = /github\.com[:/](.+?)(\.git)?$/.exec(u); if (m) return `https://github.com/${m[1]}`;
  } catch {}
  return 'https://github.com/alexliyu7352/city-through-time';
}

// one entry's problems (an empty list when it is fine)
export function problems(slug, e) {
  const p = [], is = (ok, msg) => { if (!ok) p.push(msg); };
  is(/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug), 'the folder name: lowercase letters, digits and hyphens');
  is(!RESERVED.has(slug), `the folder name "${slug}" is taken by the site itself (its page would be <site>/${slug}/); add the country or region, e.g. ${slug}-cn`);
  is(e.slug === slug, `slug must be "${slug}" (the folder's name)`);
  is(e.name && typeof e.name.en === 'string' && e.name.en, 'name.en is required');
  for (const k of Object.keys(e.name || {})) is(LANGS.includes(k), `name.${k}: languages are ${LANGS.join(', ')}`);
  is(Array.isArray(e.location) && e.location.length === 2 && Math.abs(e.location[0]) <= 180 && Math.abs(e.location[1]) <= 90, 'location: [longitude, latitude]');
  is(Array.isArray(e.years) && e.years.length === 2 && e.years.every(Number.isInteger) && e.years[0] < e.years[1], 'years: [from, to], whole years, BCE negative');
  is(typeof e.duration === 'number' && e.duration > 0, 'duration: the film\'s length in seconds');
  is(Array.isArray(e.authors) && e.authors.length && e.authors.every(a => a && a.name && (a.url == null || https(a.url))), 'authors: [{ "name": "...", "url": "https://..." }]');
  is(e.summary && typeof e.summary.en === 'string' && e.summary.en, 'summary.en is required');
  is(image(e.poster), 'poster: an https address of the poster (1280 wide), e.g. in the web bundle');
  is(e.thumb == null || image(e.thumb), 'thumb: an https address of a smaller poster (640 wide)');
  is(Array.isArray(e.watch) && e.watch.every(v => v && v.site && https(v.url)), 'watch: [{ "site": "YouTube", "url": "https://..." }] (may be empty)');
  is(e.bundle == null || ((https(e.bundle.url) || local(e.bundle.url)) && e.bundle.url.endsWith('/') && typeof e.bundle.mb === 'number'), 'bundle: null, or { "url": "https://.../", "mb": 120 }');
  is(e.download == null || https(e.download.url), 'download: null, or { "url": "https://..." }');
  is(Array.isArray(e.ai) && e.ai.every(k => AI.includes(k)), `ai: what was made with AI, from ${AI.join(', ')}`);
  is(e.license === 'CC BY-SA 4.0', 'license: "CC BY-SA 4.0"');
  is(Array.isArray(e.chapters) && e.chapters.length && e.chapters.every(c => typeof c.t === 'number' && Number.isInteger(c.year) && /^#[0-9a-fA-F]{6}$/.test(c.color)), 'chapters: [{ "t": seconds, "year": ..., "color": "#rrggbb" }] (tools/web.py --entry writes them)');
  is(/^\d{4}-\d{2}-\d{2}$/.test(e.added || ''), 'added: the date it was added, YYYY-MM-DD');
  return p;
}

export function entries() {
  const dir = path.join(ROOT, 'cities'), out = [];
  for (const slug of fs.readdirSync(dir).sort()) {
    const f = path.join(dir, slug, 'entry.json');
    if (!fs.existsSync(f)) continue;
    let e; try { e = JSON.parse(fs.readFileSync(f, 'utf8')); } catch (x) { out.push({ slug, error: `cities/${slug}/entry.json is not valid JSON: ${x.message}` }); continue; }
    out.push({ slug, e });
  }
  return out;
}

// the index: what the globe, the collection and the search need; the newest first
export function build() {
  const list = entries().filter(x => x.e && !problems(x.slug, x.e).length).map(({ e }) => ({
    slug: e.slug, name: e.name, location: e.location, years: e.years, duration: e.duration, added: e.added,
    authors: e.authors.map(a => a.name), poster: e.thumb || e.poster,
    play: e.watch.length ? 'watch' : e.bundle ? 'bundle' : null, site: e.watch.length ? e.watch[0].site : null,
    chapters: e.chapters.map(c => ({ t: c.t, year: c.year, color: c.color })),
  })).sort((a, b) => b.added.localeCompare(a.added) || a.name.en.localeCompare(b.name.en));
  const reg = { version: 2, repo: repoURL(), cities: list };
  fs.writeFileSync(path.join(ROOT, 'cities.json'), JSON.stringify(reg) + '\n');
  return reg;
}

function check(base) {
  let bad = 0;
  for (const { slug, e, error } of entries()) {
    const p = error ? [error] : problems(slug, e);
    for (const m of p) { console.error(`cities/${slug}/entry.json: ${m}`); bad++; }
  }
  if (base) {
    const files = execFileSync('git', ['-C', ROOT, 'diff', '--name-only', '--diff-filter=AMR', `${base}...HEAD`, '--', 'cities/'], { encoding: 'utf8' }).split('\n').filter(Boolean);
    for (const f of files) {
      const name = path.basename(f);
      if (f.startsWith(`cities/${EXAMPLE}/`)) continue;
      if (!(TEXT.has(path.extname(name).toLowerCase()) || NAMED.has(name))) { console.error(`${f}: only text belongs here (entry.json, city.yaml, script.yaml, CREDITS, the .md files, research notes); the film, its pictures, music and footage go on an outside host`); bad++; }
    }
    console.log(`${files.length} changed file(s) under cities/`);
  }
  console.log(bad ? `${bad} problem(s)` : `ok: ${entries().length} entr${entries().length === 1 ? 'y' : 'ies'}`);
  return bad;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  if (args.includes('--check')) { const i = args.indexOf('--base'); process.exit(check(i >= 0 ? args[i + 1] : null) ? 1 : 0); }
  const r = build(); console.log(`cities.json: ${r.cities.length} cit${r.cities.length === 1 ? 'y' : 'ies'}, ${fs.statSync(path.join(ROOT, 'cities.json')).size} bytes`);
}
