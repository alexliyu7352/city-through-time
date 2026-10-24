// The entry page: reads cities.json (the index CI builds from every cities/<slug>/entry.json: tools/registry.mjs); the globe
// (site/globe.js), the search, the language menu, the collection, and a city opened in a drawer (a sheet from below on a phone),
// its full entry read when it opens.
import { LANGS, pick, words } from './i18n.js';

const $ = id => document.getElementById(id);
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const narrow = matchMedia('(max-width: 760px)');
const store = { get: k => { try { return localStorage.getItem(k); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };
const REG = await fetch('cities.json').then(r => r.json());
const CITIES = REG.cities || [], REPO = REG.repo;
let lang = new URLSearchParams(location.search).get('lang') || store.get('lang') || pick(navigator.languages);
if (!LANGS.some(([k]) => k === lang)) lang = 'en';
let W = words(lang), open = null, globe = null;

// an element: props are set as properties, `attrs` as attributes (role, aria-*)
const el = (tag, { attrs, ...props } = {}, ...kids) => {
  const e = Object.assign(document.createElement(tag), props);
  for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
  e.append(...kids.filter(k => k != null && k !== '')); return e;
};
const icon = (id, cls = 'ico') => { const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('class', cls); s.setAttribute('aria-hidden', 'true'); s.innerHTML = `<use href="#${id}"/>`; return s; };
const sourceURL = e => /^https?:/.test(e.source || '') ? e.source : `${REPO}/tree/main/cities/${e.slug}`;
const ENTRY = new Map();   // the full entries read so far
const entry = slug => ENTRY.get(slug) || ENTRY.set(slug, fetch(`cities/${slug}/entry.json`).then(r => { if (!r.ok) throw new Error(slug); return r.json(); })).get(slug);
const PAGE = 24;           // the collection shows this many at a time
// a film on a video site, played inside the page: YouTube (privacy-enhanced: no cookies before play) and Bilibili; other sites open in a tab
function embed(url) {
  let u; try { u = new URL(url); } catch { return null; }
  const h = u.hostname.replace(/^(www|m)\./, '');
  const yt = h === 'youtu.be' ? u.pathname.slice(1) : h === 'youtube.com' ? (u.searchParams.get('v') || (u.pathname.match(/^\/(embed|shorts|live)\/([\w-]{11})/) || [])[2]) : null;
  if (yt && /^[\w-]{11}$/.test(yt)) return `https://www.youtube-nocookie.com/embed/${yt}?autoplay=1&rel=0&playsinline=1`;
  const bv = h === 'bilibili.com' && (u.pathname.match(/\/video\/(BV\w+)/) || [])[1];
  if (bv) return `https://player.bilibili.com/player.html?bvid=${bv}&autoplay=1&high_quality=1&danmaku=0`;
  return null;
}
const player = $('player');
// the film on one of its sites; when it is on several, the others are a click away in the player (a site can be out of reach in some countries)
function watch(c, sites, i) {
  const tabs = sites.length < 2 ? [] : sites.map((v, k) => {
    const b = el('button', { type: 'button', className: 'player-tab', textContent: v.site, attrs: { 'aria-pressed': String(k === i) } });
    b.onclick = () => watch(c, sites, k); return b;
  });
  $('player-sites').replaceChildren(...tabs); $('player-sites').setAttribute('aria-label', W.t('videoSites'));
  $('player-frame').replaceChildren(el('iframe', { src: sites[i].src, title: `${W.of(c.name)} · ${sites[i].site}`, allowFullscreen: true, attrs: { allow: 'autoplay; fullscreen; picture-in-picture; encrypted-media', referrerpolicy: 'strict-origin-when-cross-origin' } }));
  if (!player.open) player.showModal();
}
player.addEventListener('close', () => $('player-frame').replaceChildren());   // (the film stops with the window)
player.addEventListener('click', e => { if (e.target === player) player.close(); });
let shown = PAGE;
const guideURL = kind => `${REPO}/blob/main/${W.guide(kind)}`;
const alt = c => lang !== 'en' && c.name.en && c.name.en !== W.of(c.name) ? c.name.en : '';
// a poster from wherever the city keeps it (shown as an image, so another host needs no cross-origin permission); one that cannot
// be loaded gives way to the city's title card
const card = c => el('span', { className: 'ex-card', textContent: W.of(c.name) });
function poster(c, src, alt, fallback) {
  if (!src) return fallback();
  const img = el('img', { src, alt, loading: 'lazy' });
  img.onerror = () => { img.parentElement?.classList.add('noimg'); img.replaceWith(fallback()); };
  return img;
}

// a film as a bar: its chapters side by side, as long as they last, in their colours on screen
function filmBar(c, node) {
  node.replaceChildren();
  const ch = c.chapters || [], d = c.duration || (ch.length ? ch[ch.length - 1].t + 10 : 1);
  ch.forEach((x, i) => { const w = ((i + 1 < ch.length ? ch[i + 1].t : d) - x.t) / d; if (w > 0) node.append(el('span', { style: `flex-grow:${w};background:${x.color}`, title: W.year(x.year) })); });
  node.setAttribute('aria-label', `${W.t('chapters')}: ${W.span(c.years)}`);
  return node;
}

// ---------------------------------------------------------------- the language menu
const langBtn = $('lang-btn'), langList = $('lang-list');
let langActive = 0;
function renderLangs() {
  const now = LANGS.find(([k]) => k === lang)[1];
  $('lang-now').textContent = now; langBtn.setAttribute('aria-label', `${W.t('language')}: ${now}`);
  langList.replaceChildren(...LANGS.map(([k, name]) => el('li', { id: `lang-${k}`, lang: k, attrs: { role: 'option', 'aria-selected': String(k === lang) } }, el('span', { textContent: name }), icon('i-check'))));
  for (const li of langList.children) li.onclick = () => choose(li.lang);
}
function mark() {
  [...langList.children].forEach((li, i) => li.classList.toggle('active', i === langActive));
  langList.setAttribute('aria-activedescendant', `lang-${LANGS[langActive][0]}`);
}
function menu(show) {
  langList.hidden = !show; langBtn.setAttribute('aria-expanded', String(show));
  if (show) { langActive = LANGS.findIndex(([k]) => k === lang); mark(); langList.focus(); }
}
function choose(k) { lang = k; store.set('lang', k); W = words(lang); menu(false); langBtn.focus(); paint(); }
langBtn.onclick = () => menu(langList.hidden);
langBtn.onkeydown = e => { if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); menu(true); } };
langList.onkeydown = e => {
  const n = LANGS.length, keys = { ArrowDown: i => (i + 1) % n, ArrowUp: i => (i + n - 1) % n, Home: () => 0, End: () => n - 1 };
  if (keys[e.key]) { langActive = keys[e.key](langActive); mark(); e.preventDefault(); }
  else if (e.key === 'Enter' || e.key === ' ') { choose(LANGS[langActive][0]); e.preventDefault(); }
  else if (e.key === 'Escape') { menu(false); langBtn.focus(); }
  else if (e.key === 'Tab') menu(false);
};
addEventListener('pointerdown', e => { if (!langList.hidden && !e.target.closest('.lang')) menu(false); });

// ---------------------------------------------------------------- the search: any of a city's names, its slug, its makers
const norm = s => String(s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '');
const INDEX = CITIES.map(c => ({ c, text: norm([c.slug, ...Object.values(c.name || {}), ...(c.authors || [])].join(' ')) }));
const matches = s => { s = norm(s).trim(); return s ? INDEX.filter(x => s.split(/\s+/).every(w => x.text.includes(w))).map(x => x.c) : CITIES; };
function combobox(input, list, { onPick, always }) {
  let items = [], active = -1;
  const render = reset => {
    const s = input.value.trim(); items = matches(s).slice(0, 8);
    if (reset) active = items.length ? 0 : -1;
    list.replaceChildren(...items.map((c, i) => el('li', { id: `${list.id}-${i}`, attrs: { role: 'option', 'aria-selected': String(i === active) } },
      poster(c, c.poster, '', () => filmBar(c, el('span', { className: 'bar-film thumb' }))),
      el('div', {}, el('div', { className: 'r-name', textContent: W.of(c.name) }), el('div', { className: 'r-sub', textContent: [alt(c), W.span(c.years)].filter(Boolean).join('　') })))));
    [...list.children].forEach((li, i) => { li.onpointerdown = e => e.preventDefault(); li.onclick = () => onPick(items[i]); });
    if (s && !items.length) list.replaceChildren(el('li', { className: 'none' }, el('div', { textContent: W.fmt('searchNone', { q: s }) }),
      el('a', { href: guideURL('making'), target: '_blank', rel: 'noopener', textContent: W.t('searchMake') })));
    const shown = always || !!s; list.hidden = !shown;
    input.setAttribute('aria-expanded', String(shown && items.length > 0));
    input.setAttribute('aria-activedescendant', active >= 0 && items.length ? `${list.id}-${active}` : '');
  };
  input.addEventListener('input', () => render(true));
  input.addEventListener('focus', () => render(true));
  input.addEventListener('blur', () => { if (!always) setTimeout(() => { list.hidden = true; input.setAttribute('aria-expanded', 'false'); }, 150); });
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' && items.length) { active = Math.min(items.length - 1, active + 1); render(); e.preventDefault(); }
    else if (e.key === 'ArrowUp' && items.length) { active = Math.max(0, active - 1); render(); e.preventDefault(); }
    else if (e.key === 'Enter' && items.length) { onPick(items[Math.max(0, active)]); e.preventDefault(); }
    else if (e.key === 'Escape' && !always) { input.value = ''; render(true); input.blur(); }
  });
  return { render };
}
const q = $('q'), q2 = $('q2'), sheet = $('search-sheet');
combobox(q, $('results'), { onPick: c => { q.value = ''; q.blur(); show(c.slug, q); } });
const inSheet = combobox(q2, $('results2'), { always: true, onPick: c => { sheet.close(); q2.value = ''; show(c.slug, $('search-open')); } });
$('search-open').onclick = () => { sheet.showModal(); inSheet.render(true); q2.focus(); };
$('sheet-close').onclick = () => sheet.close();
addEventListener('keydown', e => {   // "/" starts a search from anywhere
  if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey || /input|textarea|select/i.test(document.activeElement.tagName)) return;
  e.preventDefault();
  if (getComputedStyle($('search-open')).display !== 'none') $('search-open').click(); else q.focus();
});

// ---------------------------------------------------------------- the collection: each city a poster and its label; the empty plinth last
const PLINTH = '<svg viewBox="0 0 200 150" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M100 6 66 96M100 6l34 90" stroke-opacity=".45"/><ellipse cx="100" cy="98" rx="58" ry="11"/><path d="M42 98v24c0 6 26 11 58 11s58-5 58-11V98"/></svg>';
function renderCollection() {
  $('count').textContent = W.count(CITIES.length);
  const ul = $('exhibits'); ul.replaceChildren();
  for (const c of CITIES.slice(0, shown)) {
    const act = c.play === 'watch' ? W.t('watchFilm') : c.play === 'bundle' ? W.t('play') : null;
    const b = el('button', { type: 'button', className: 'ex' },
      el('figure', { className: 'ex-poster' + (c.poster ? '' : ' noimg') },
        poster(c, c.poster, W.of(c.name), () => card(c)),
        act ? el('span', { className: 'ex-play' }, icon('i-play'), el('span', { textContent: act })) : null),
      el('div', { className: 'ex-cap' },
        el('h3', { className: 'ex-name', textContent: W.of(c.name) }), alt(c) ? el('p', { className: 'ex-alt', textContent: alt(c) }) : null,
        el('p', { className: 'ex-line', textContent: [W.span(c.years), c.duration ? W.length(c.duration) : ''].filter(Boolean).join('　') }),
        el('p', { className: 'ex-by', textContent: W.fmt('by', { who: (c.authors || []).join(', ') }) }),
        filmBar(c, el('span', { className: 'bar-film' }))));
    b.onclick = () => show(c.slug, b);
    ul.append(el('li', {}, b));
  }
  ul.append(el('li', { className: 'empty' }, el('a', { className: 'ex', href: guideURL('making'), target: '_blank', rel: 'noopener' },
    el('figure', { className: 'ex-poster', innerHTML: PLINTH }),
    el('div', { className: 'ex-cap' }, el('h3', { className: 'ex-name', textContent: W.t('emptyTitle') }), el('p', { className: 'ex-line', textContent: W.t('emptyText') }),
      el('span', { className: 'more', textContent: W.t('emptyLink') })))));
  $('more-cities').hidden = shown >= CITIES.length;
}
$('more-cities').onclick = () => { const first = shown; shown += PAGE; renderCollection(); $('exhibits').children[first]?.querySelector('.ex')?.focus(); };

// ---------------------------------------------------------------- a city, opened
const panel = $('panel'), scrim = $('scrim');
let opener = null;
async function show(slug, from) {
  const i = CITIES.find(x => x.slug === slug); if (!i) return;
  open = slug; if (from) opener = from;
  let c; try { c = await entry(slug); } catch { c = { ...i, authors: i.authors.map(name => ({ name })), watch: [], ai: [], summary: {} }; }   // (the index alone, if the entry cannot be read)
  if (open !== slug) return;
  $('poster').replaceChildren(poster(c, c.poster, W.of(c.name), () => card(c)));
  $('panel-name').textContent = W.of(c.name); $('panel-alt').textContent = alt(c);
  $('panel-years').textContent = W.span(c.years);
  filmBar(c, $('panel-bar'));
  // the finished film first: its first site is the default (inside the page when that site allows it, else a link to it); then the
  // model played live; then every site the film is on
  const acts = [], sites = c.watch || [], playable = sites.map(v => ({ ...v, src: embed(v.url) })).filter(v => v.src);
  const inPage = sites.length > 0 && playable[0] && playable[0].url === sites[0].url;
  if (inPage) { const b = el('button', { type: 'button', className: 'btn btn-main' }, icon('i-play'), el('span', { textContent: W.t('watchFilm') })); b.onclick = () => watch(c, playable, 0); acts.push(b); }
  else if (sites.length) acts.push(el('a', { className: 'btn btn-main', href: sites[0].url, target: '_blank', rel: 'noopener' }, icon('i-play'), el('span', { textContent: W.fmt('watchOn', { site: sites[0].site }) })));
  if (c.bundle && c.bundle.url) {
    acts.push(el('a', { className: 'btn ' + (acts.length ? 'btn-line' : 'btn-main'), href: `play.html?city=${encodeURIComponent(c.slug)}&play=1&bundle=${encodeURIComponent(c.bundle.url)}`, target: '_blank', rel: 'noopener' }, el('span', { textContent: W.t('play') })));
    if (c.bundle.mb) acts.push(el('p', { className: 'small', textContent: W.fmt('playNote', { mb: Math.round(c.bundle.mb) }) }));
  }
  const links = (inPage ? sites : sites.slice(1)).map(v => el('a', { href: v.url, target: '_blank', rel: 'noopener', textContent: W.fmt('watchOn', { site: v.site }) }));
  if (links.length) acts.push(el('p', { className: 'sites' }, ...links));
  if (c.download && c.download.url) acts.push(el('a', { className: 'btn btn-line', href: c.download.url, target: '_blank', rel: 'noopener', textContent: W.t('download') }));
  if (!acts.length) acts.push(el('p', { className: 'pending', textContent: W.t('pending') }));
  $('actions').replaceChildren(...acts);
  $('summary').textContent = W.of(c.summary);
  const facts = [[W.t('length'), c.duration ? W.length(c.duration) : null], [W.t('narration'), c.narration ? W.langName(c.narration) : null],
    [W.t('subtitles'), (c.subtitles || []).length ? W.join(c.subtitles.map(W.langName)) : null]];
  $('facts').replaceChildren(...facts.filter(f => f[1]).flatMap(([k, v]) => [el('dt', { textContent: k }), el('dd', { textContent: v })]),
    el('dt', { textContent: W.t('made') }), el('dd', {}, ...(c.authors || []).flatMap((a, i) => [i ? ', ' : null, a.url ? el('a', { href: a.url, target: '_blank', rel: 'noopener', textContent: a.name }) : a.name])));
  const ai = (c.ai || []).map(k => ({ narration: W.t('aiNarration'), music: W.t('aiMusic'), imagined: W.t('aiImagined') })[k] || k);
  $('ai').textContent = ai.length ? W.fmt('ai', { list: W.join(ai) }) : '';
  $('source').href = sourceURL(c);
  panel.hidden = false; panel.removeAttribute('inert'); panel.scrollTop = 0; panel.style.removeProperty('--drag');
  requestAnimationFrame(() => panel.classList.add('open'));
  if (narrow.matches) { scrim.hidden = false; requestAnimationFrame(() => scrim.classList.add('on')); document.documentElement.style.overflow = 'hidden'; }
  if (globe) { globe.focus(slug); globe.hold(true, narrow.matches ? 0 : panel.offsetWidth); }
  setTimeout(() => $('close').focus({ preventScroll: true }), 60);
}
function hide() {
  if (!open) return; open = null;
  panel.classList.remove('open'); panel.setAttribute('inert', ''); scrim.classList.remove('on');
  setTimeout(() => { if (!open) scrim.hidden = true; }, 350);
  document.documentElement.style.overflow = '';
  if (globe) globe.hold(false);
  if (opener && opener.isConnected) opener.focus({ preventScroll: true });
}
panel.setAttribute('inert', '');
$('close').onclick = hide; scrim.onclick = hide;
addEventListener('keydown', e => { if (e.key === 'Escape' && open && langList.hidden && !sheet.open && !player.open) hide(); });
{   // on a phone: drag the sheet down to put it away
  const grab = $('grab'); let y0 = null, dy = 0;
  grab.addEventListener('pointerdown', e => { y0 = e.clientY; dy = 0; panel.classList.add('dragging'); grab.setPointerCapture(e.pointerId); });
  grab.addEventListener('pointermove', e => { if (y0 == null) return; dy = Math.max(0, e.clientY - y0); panel.style.setProperty('--drag', `${dy}px`); });
  grab.addEventListener('pointerup', () => { if (y0 == null) return; y0 = null; panel.classList.remove('dragging'); panel.style.removeProperty('--drag'); if (dy > 110) hide(); });
}

// ---------------------------------------------------------------- the labels that follow the cities on the globe
const pins = $('pins');
function renderPins() {
  pins.replaceChildren(...CITIES.filter(c => c.location).map(c => {
    const b = el('button', { type: 'button', className: 'pin', tabIndex: -1 }, el('span', { className: 'p-name', textContent: W.of(c.name) }), el('span', { className: 'p-years', textContent: W.span(c.years) }));
    b.dataset.slug = c.slug; b.style.opacity = 0; b.style.visibility = 'hidden'; b.onclick = () => show(c.slug, b); return b;
  }));
}
function follow(list, t) {
  for (const p of list) {
    const b = pins.querySelector(`[data-slug="${p.slug}"]`); if (!b) continue;
    const o = Math.max(0, Math.min(1, (p.facing - .2) / .25)) * (reduced ? 1 : Math.min(1, Math.max(0, (t - 2.8) / .8)));
    b.style.transform = `translate(${p.x.toFixed(1)}px, ${p.y.toFixed(1)}px)`; b.style.opacity = o.toFixed(2); b.style.visibility = o < .05 ? 'hidden' : 'visible';
  }
}

// ---------------------------------------------------------------- the words, in the chosen language
function paint() {
  document.documentElement.lang = lang;
  for (const n of document.querySelectorAll('[data-t]')) n.textContent = W.t(n.dataset.t);
  for (const n of document.querySelectorAll('[data-alt]')) n.alt = W.t(n.dataset.alt);
  for (const a of document.querySelectorAll('[data-guide]')) a.href = guideURL(a.dataset.guide);
  q.placeholder = q2.placeholder = W.t('searchPlaceholder'); q.setAttribute('aria-label', W.t('searchLabel')); q2.setAttribute('aria-label', W.t('searchLabel'));
  $('gh').href = $('repo').href = $('repo-cta').href = REPO; $('gh').title = W.t('github');
  $('caption-text').textContent = W.fmt('exhibitText', { n: W.num(globe ? globe.blocks : 63253) });
  renderLangs(); renderCollection(); renderPins();
  if (open) show(open);
}

const bar = $('bar');
addEventListener('scroll', () => bar.classList.toggle('scrolled', scrollY > 8), { passive: true });
if (!reduced) document.documentElement.classList.add('intro');
paint();

try {
  const { makeGlobe } = await import('./globe.js');
  const small = narrow.matches || (navigator.hardwareConcurrency || 8) <= 4 || new URLSearchParams(location.search).has('lite');   // (?lite: the phone version, to compare)
  globe = await makeGlobe($('globe'), CITIES, { reduced, small, onPick: slug => show(slug), onHover: () => {}, onFrame: follow });
  const room = () => globe.setRoom(document.querySelector('.hero-copy').getBoundingClientRect().right + 32);   // (the globe keeps clear of the words)
  room(); new ResizeObserver(room).observe(document.querySelector('.hero-copy')); document.fonts.ready.then(room);
  $('caption-text').textContent = W.fmt('exhibitText', { n: W.num(globe.blocks) });
} catch (e) {
  console.warn('globe:', e);
  document.documentElement.classList.add('no-gl');
  $('hint').dataset.t = 'noGL'; $('hint').textContent = W.t('noGL');
}
