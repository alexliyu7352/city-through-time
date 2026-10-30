// A city's own site on Cloudflare Pages, for anyone with a free Cloudflare account and no domain of their own (docs/PUBLISH.md):
// that city alone (tools/site.mjs --city --copy: its page in each language at the site's root, the player, the walk-round, the
// museum pages, its posters and its web bundle, from cities/<slug>/dist/web/ where the repository does not have it, published at
// cities/<slug>/web/), with Pages' _headers, checked against Pages' limits and the bundle's own list, and uploaded with
// Cloudflare's wrangler. The gallery (the entry page, the globe, every city) is the project's own site: a user publishes their
// city, not a copy of the gallery. --all builds the gallery as CI does (tools/site.mjs --copy), with every city's entry.json and
// bundle where the repository does not have them, for the project's own site. The site is https://<project>.pages.dev/
// (Cloudflare adds a suffix when another account has the name: the address printed at the end).
//   node tools/deploy.mjs [--city <slug>|auto | --all] [--project <name>] [--dry-run] [--out <folder>]
// --city: the city to publish, else local/config.json cloudflare.city; auto (tools/site.mjs pickCity): the one city in cities/
// that is not the example (with none, the example, as a demo; with several it stops). With no city and no --all it stops.
// --project: the Pages project, created when the account has none of that name; else cloudflare.project when the city is
// cloudflare.city (a project holds one city's site: another city gets its own, never replacing it), else the city's slug; --all
// takes it only from --project. --dry-run: build and check, upload nothing; --out: build into this folder and keep it (else a
// temporary one, removed after), to look at it with `npx wrangler@<WRANGLER> pages dev <folder>`.
// The account: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID from the environment, else cloudflare.api_token and
// cloudflare.account_id in local/config.json (this machine's, never in git). The token needs one permission: Account, Cloudflare
// Pages, Edit.
import fs from 'fs'; import os from 'os'; import path from 'path'; import { execFileSync, spawnSync } from 'child_process';
import { ROOT } from './registry.mjs';
import { site, bundles, pickCity, HEADERS } from './site.mjs';
import { local } from '../render/local.mjs';

const WRANGLER = '4.150.0';   // Cloudflare's upload tool, the exact version npx fetches (it needs Node 22 or newer)
const MiB = 2 ** 20, FILE_MAX = 25 * MiB, FILES_MAX = 20000;   // what Pages takes: no file over 25 MiB, at most 20,000 files

const args = process.argv.slice(2), arg = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
const dry = args.includes('--dry-run'), keep = arg('--out') && path.resolve(arg('--out'));
const cf = local('cloudflare', {}) || {};
const all = args.includes('--all'), named = all ? null : arg('--city') || cf.city;
const token = process.env.CLOUDFLARE_API_TOKEN || cf.api_token, account = process.env.CLOUDFLARE_ACCOUNT_ID || cf.account_id;

// the Pages project of that name in the account (null: none yet)
async function api(method, p = '', body) {
  const r = await fetch(`https://api.cloudflare.com/client/v4/accounts/${account}/pages/projects${p}`, {
    method, headers: { Authorization: `Bearer ${token}`, ...(body ? { 'Content-Type': 'application/json' } : {}) }, body: body && JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (r.ok && j.success) return j.result;
  if (r.status === 404 && method === 'GET') return null;
  throw new Error(`Cloudflare answered ${r.status} to ${method} pages/projects${p}: ${(j.errors || []).map(e => `${e.message} (${e.code})`).join('; ') || r.statusText}` +
    ([400, 401, 403, 404].includes(r.status) ?'; the token needs the permission Account, Cloudflare Pages, Edit, and the account id is the one it was made in' : ''));
}

// what Pages would refuse, and a bundle missing a file its bundle.json lists
function check(out) {
  const p = [], files = fs.readdirSync(out, { recursive: true }).filter(f => fs.statSync(path.join(out, f)).isFile());
  if (files.length > FILES_MAX) p.push(`${files.length} files: Pages takes at most ${FILES_MAX}`);
  for (const f of files) {
    const n = fs.statSync(path.join(out, f)).size; if (n <= FILE_MAX) continue;
    p.push(`${f.split(path.sep).join('/')}: ${(n / MiB).toFixed(1)} MiB, and Pages takes no file over 25 MiB` +
      (/^cities\/[^/]+\/web\//.test(f.split(path.sep).join('/')) ? ' (pack the city again: tools/web.py writes a file over 20 MiB in parts)' : ''));
  }
  for (const f of files.map(f => f.split(path.sep).join('/')).filter(f => /^cities\/[^/]+\/web\/bundle\.json$/.test(f))) {
    const dir = path.dirname(path.join(out, f)), B = JSON.parse(fs.readFileSync(path.join(out, f), 'utf8'));
    const lost = B.files.flatMap(x => [x.path, ...(x.parts || [])]).filter(x => !fs.existsSync(path.join(dir, x)));
    if (lost.length) p.push(`${path.dirname(f)}/: bundle.json lists ${lost.length} file(s) it does not have, e.g. ${lost[0]}`);
  }
  return { p, files: files.length, bytes: files.reduce((s, f) => s + fs.statSync(path.join(out, f)).size, 0) };
}

const work = fs.mkdtempSync(path.join(os.tmpdir(), 'city-site-'));   // (the site unless --out; wrangler runs here, its .wrangler/ left here)
try {
  if (all && args.includes('--city')) throw new Error('--city publishes one city, --all the whole gallery: one of them');
  if (args.includes('--city') && !/^[^-]/.test(arg('--city') || '')) throw new Error('--city takes a city\'s folder name, or auto');
  if (!all && !named) throw new Error('name the city to publish: --city <slug>, or "city": "<slug>" under "cloudflare" in local/config.json (--city auto: the one city in cities/ besides the example); the site is that city alone. --all publishes the whole gallery, the project\'s own site');
  const city = all ? null : pickCity(named);
  const project = arg('--project') || (all ? null : (cf.city && [named, city].includes(cf.city) && cf.project) || city);
  if (!project) throw new Error('--all: name the Pages project, --project <name>; the site is then https://<name>.pages.dev/');
  if (!/^[a-z0-9][a-z0-9-]{0,57}$/.test(project)) throw new Error(`--project ${project}: lowercase letters, digits and hyphens, at most 58, not starting with a hyphen`);
  if (+process.versions.node.split('.')[0] < 22) throw new Error(`wrangler ${WRANGLER} needs Node 22 or newer (this is ${process.version})`);
  if (!(token && account) && !dry) throw new Error('no Cloudflare account: set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID (or cloudflare.api_token and cloudflare.account_id in local/config.json); docs/PUBLISH.md says how to make the token');
  let pages = token && account ? await api('GET', '/' + project) : null;
  if (!pages && !dry) { pages = await api('POST', '', { name: project, production_branch: 'main' }); console.log(`created the Pages project ${project}`); }
  if (!pages) console.log(token && account ? `the account has no Pages project ${project} yet: the deploy creates it (another account's name gets a suffix: the address may differ)`
    : 'no Cloudflare account set: built for the address the project would have, nothing asked of Cloudflare');
  const host = pages?.subdomain || `${project}.pages.dev`, origin = `https://${host}`;

  try { execFileSync(process.execPath, [path.join(ROOT, 'tools', 'registry.mjs'), '--check'], { stdio: 'inherit' }); }   // (as CI checks them: an entry with a problem would be left off the site)
  catch { throw new Error('the entries have problems (above): fix them first'); }
  const out = keep || path.join(work, 'site');
  const r = site({ out, origin, copy: true, city });   // (a city's: with its entry and bundle)
  if (all) bundles(out, origin);
  fs.writeFileSync(path.join(out, '_headers'), HEADERS);
  const c = check(out);
  console.log(`site: ${city ? `${city} alone` : 'the gallery'}, ${r.pages} pages, ${c.files} files, ${(c.bytes / MiB).toFixed(0)} MiB, for ${origin}/`);
  if (c.p.length) throw new Error(`Pages would not take this site:\n  ${c.p.join('\n  ')}`);
  if (dry) {
    console.log(`dry run: built and checked, nothing uploaded${keep ? `; the site is in ${keep} (npx wrangler@${WRANGLER} pages dev ${keep})` : ''}`);
  } else {
    const head = execFileSync('git', ['-C', ROOT, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
    const dirty = !!execFileSync('git', ['-C', ROOT, 'status', '--porcelain', '--untracked-files=no'], { encoding: 'utf8' }).trim();
    const win = process.platform === 'win32';   // (npx is a .cmd there, started through the shell: its arguments quoted)
    const w = spawnSync('npx', ['--yes', `wrangler@${WRANGLER}`, 'pages', 'deploy', out, '--project-name', project, '--branch', pages.production_branch || 'main',
      '--commit-hash', head, `--commit-dirty=${dirty}`].map(a => win ? `"${a}"` : a),
      { cwd: work, stdio: 'inherit', shell: win, env: { ...process.env, CLOUDFLARE_API_TOKEN: token, CLOUDFLARE_ACCOUNT_ID: account, WRANGLER_SEND_METRICS: 'false' } });
    if (w.status !== 0) throw new Error(`wrangler stopped (${w.error?.message || 'exit ' + w.status}; its message is above)`);
    console.log(`deployed: ${origin}/`);
  }
} catch (e) {
  console.error(`deploy: ${e.message}`); process.exitCode = 1;
} finally {
  fs.rmSync(work, { recursive: true, force: true });
}
