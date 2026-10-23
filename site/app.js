// The entry page: reads cities.json, lists the cities, opens one, and turns the globe (site/globe.js) to it.
import { LANGS, pick, words } from './i18n.js';

const $ = id => document.getElementById(id);
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const store = { get: k => { try { return localStorage.getItem(k); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };
const REG = await fetch('cities.json').then(r => r.json());
const CITIES = REG.cities || [];
const REPO = REG.repo;
let lang = new URLSearchParams(location.search).get('lang') || store.get('lang') || pick(navigator.languages);
if (!LANGS.some(([k]) => k === lang)) lang = 'en';
let W = words(lang), open = null, globe = null;

const el = (tag, props = {}, ...kids) => { const e = Object.assign(document.createElement(tag), props); e.append(...kids.filter(k => k != null)); return e; };
const sourceURL = c => /^https?:/.test(c.source || '') ? c.source : `${REPO}/tree/main/${c.source}`;
const mb = c => c.bundle && c.bundle.mb ? Math.round(c.bundle.mb) : null;

// a film as a bar: its chapters side by side, as long as they last, in their colours on screen
function bar(c, node) {
  node.replaceChildren();
  const ch = c.chapters || [], d = c.duration || (ch.length ? ch[ch.length - 1].t + 10 : 1);
  ch.forEach((x, i) => {
    const w = ((i + 1 < ch.length ? ch[i + 1].t : d) - x.t) / d;
    if (w > 0) node.append(el('span', { style: `flex-grow:${w};background:${x.color}`, title: W.year(x.year) }));
  });
  node.setAttribute('aria-label', `${W.t('chapters')}: ${W.span(c.years)}`);
  return node;
}

function renderLangs() {
  const nav = document.querySelector('.langs'); nav.replaceChildren();
  for (const [k, name] of LANGS) {
    const b = el('button', { type: 'button', lang: k, textContent: name });
    if (k === lang) b.setAttribute('aria-current', 'true');
    b.onclick = () => { lang = k; store.set('lang', k); W = words(lang); paint(); };
    nav.append(b);
  }
}

function renderList() {
  const ul = $('labels'); ul.replaceChildren();
  for (const c of CITIES) {
    const b = el('button', { type: 'button', className: 'label' },
      el('span', { className: 'name', textContent: W.of(c.name) }),
      lang !== 'en' && c.name.en && c.name.en !== W.of(c.name) ? el('span', { className: 'also', textContent: c.name.en }) : null,
      el('span', { className: 'years', textContent: W.span(c.years) }),
      el('span', { className: 'by', textContent: (c.authors || []).map(a => a.name).join(', ') }),
      bar(c, el('span', { className: 'bar' })));
    b.onclick = () => { show(c.slug, b); document.querySelector('.hero').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); };
    ul.append(el('li', {}, b));
  }
  ul.append(el('li', { className: 'empty' },
    el('a', { href: `${REPO}/blob/main/${W.guide('making')}`, target: '_blank', rel: 'noopener' },
      el('span', { className: 'name', textContent: W.t('emptyTitle') }),
      el('span', { className: 'text', textContent: W.t('emptyText') }),
      el('span', { className: 'go', textContent: W.t('emptyLink') }))));
}

let opener = null;
function show(slug, from) {
  const c = CITIES.find(x => x.slug === slug); if (!c) return;
  open = slug; opener = from || opener;
  $('poster').src = c.poster; $('poster').alt = W.of(c.name);
  $('panel-name').textContent = W.of(c.name);
  $('panel-also').textContent = lang !== 'en' && c.name.en !== W.of(c.name) ? c.name.en : '';
  bar(c, $('panel-bar'));
  const facts = [[W.t('years'), W.span(c.years)], [W.t('length'), c.duration ? W.length(c.duration) : null],
    [W.t('narration'), c.narration ? W.langName(c.narration) : null], [W.t('subtitles'), (c.subtitles || []).length ? W.join(c.subtitles.map(W.langName)) : null]];
  $('facts').replaceChildren(...facts.filter(f => f[1]).flatMap(([k, v]) => [el('dt', { textContent: k }), el('dd', { textContent: v })]),
    el('dt', { textContent: W.t('by') }), el('dd', {}, ...(c.authors || []).flatMap((a, i) => [i ? ', ' : null, a.url ? el('a', { href: a.url, target: '_blank', rel: 'noopener', textContent: a.name }) : a.name])));
  $('summary').textContent = W.of(c.summary);
  const acts = [];
  if (c.bundle && c.bundle.url) {
    const u = `play.html?city=${encodeURIComponent(c.slug)}&play=1&bundle=${encodeURIComponent(c.bundle.url)}`;
    acts.push(el('a', { className: 'act main', href: u, target: '_blank', rel: 'noopener' }, el('span', { textContent: W.t('play') })),
      mb(c) ? el('p', { className: 'small', textContent: W.fmt('playNote', { mb: mb(c) }) }) : null);
  }
  for (const v of c.watch || []) acts.push(el('a', { className: 'act' + (acts.length ? '' : ' main'), href: v.url, target: '_blank', rel: 'noopener', textContent: W.fmt('watchOn', { site: v.site }) }));
  if (c.download && c.download.url) acts.push(el('a', { className: 'act', href: c.download.url, target: '_blank', rel: 'noopener', textContent: W.t('download') }));
  if (!acts.length) acts.push(el('p', { className: 'pending', textContent: W.t('pending') }));
  $('actions').replaceChildren(...acts.filter(Boolean));
  const ai = (c.ai || []).map(k => ({ narration: W.t('aiNarration'), music: W.t('aiMusic'), imagined: W.t('aiImagined') })[k] || k);
  $('ai').textContent = ai.length ? W.fmt('ai', { list: W.join(ai) }) : '';
  $('source').href = sourceURL(c);
  $('panel').hidden = false; document.body.classList.add('opened');
  if (globe) { globe.focus(slug); globe.hold(true); }
  $('close').focus({ preventScroll: true });
}
function hide() {
  open = null; $('panel').hidden = true; document.body.classList.remove('opened');
  if (globe) globe.hold(false);
  if (opener) opener.focus({ preventScroll: true });
}
$('close').onclick = hide;
addEventListener('keydown', e => { if (e.key === 'Escape' && open) hide(); });

function paint() {
  document.documentElement.lang = lang;
  for (const n of document.querySelectorAll('[data-t]')) n.textContent = W.t(n.dataset.t);
  for (const a of document.querySelectorAll('[data-guide]')) a.href = `${REPO}/blob/main/${W.guide(a.dataset.guide)}`;
  $('repo').href = REPO;
  renderLangs(); renderList();
  if (open) show(open);
}
paint();

// the name tag that follows a city on the globe while the pointer is over it
const tag = $('tag');
function follow(slug) {
  if (!slug || !globe) { tag.hidden = true; return; }
  const c = CITIES.find(x => x.slug === slug), p = globe.screenOf(slug);
  if (!p || !p.front) { tag.hidden = true; return; }
  tag.textContent = `${W.of(c.name)}　${W.span(c.years)}`; tag.style.transform = `translate(${p.x}px, ${p.y}px)`; tag.hidden = false;
}
let hovering = null;
try {
  const { makeGlobe } = await import('./globe.js');
  globe = await makeGlobe($('globe'), CITIES, { reduced, onPick: slug => show(slug), onHover: slug => { hovering = slug; follow(slug); } });
  const loop = () => { if (hovering) follow(hovering); requestAnimationFrame(loop); }; loop();
} catch (e) {
  console.warn('globe:', e);
  document.body.classList.add('no-gl');
  const h = document.querySelector('.hint'); h.dataset.t = 'noGL'; h.textContent = W.t('noGL');
}
