// A museum page (museum.html?city=<slug>&id=<page>[&lang=zh|en][&bundle=<url>]; docs/MUSEUM.md): the page's words and its first
// picture at once, then the model (engine/museum.js), which takes over from the picture on the same camera. Built by
// tools/museum.py into build/museum/<page>.json (the words, the parts' notes, the viewpoints and their pictures).
// ?clean&vp=<viewpoint>: the model alone at that viewpoint, the whole window, the reference look (tools/museum.mjs still, for
// tools/living.py ref); window.READY once drawn, window.MUSEUM(o) turns it for the report's stills (engine/museum.js view).
import { words } from './i18n.js';
import { frameOf } from '../engine/lib.js';
import { REPO } from '../engine/overlay.js';

const QS = new URLSearchParams(location.search);
const CITY = QS.get('city'), ID = QS.get('id'), BUNDLE = QS.get('bundle'), CLEAN = QS.has('clean');
const base = BUNDLE ? BUNDLE.replace(/\/?$/, '/') : `cities/${CITY}/`;
// the page's languages: the text is written in Chinese (Simplified, as the film) and English
const LANG = (QS.get('lang') || navigator.language || 'en').toLowerCase().startsWith('zh') ? 'zh' : 'en';
const W = words(LANG === 'zh' ? 'zh-Hans' : 'en'), of = o => (o && (o[LANG] || o.en)) || '';
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
document.documentElement.lang = LANG === 'zh' ? 'zh-Hans' : 'en';
if (CLEAN) document.documentElement.classList.add('clean');

const meta = await (await fetch(base + `build/museum/${ID}.json`)).json();
const main = meta.viewpoints.find(v => v.id === QS.get('vp')) || meta.viewpoints.find(v => v.main);
const stage = $('stage'), first = $('first');

// the first picture, at once, where the model's camera will show it (frameOf: the same rule as the model's lens)
function placeFirst() {
  const p = main.picture; if (!p) return;
  const f = frameOf(stage.clientWidth, stage.clientHeight, p.w / p.h);
  Object.assign(first.style, { left: f.x + 'px', top: f.y + 'px', width: f.w + 'px', height: f.h + 'px' });
  first.classList.toggle('band', f.h < stage.clientHeight - 1);   // (narrower than the picture: a band, its edges feathered as on the model)
}
if (!CLEAN && main.picture) { first.src = base + main.picture.file; first.alt = of(meta.name); placeFirst(); addEventListener('resize', placeFirst); }

// the words
const cite = list => list && list.length ? `<p class="cite">${esc(W.fmt('museumCite', { list: '' }))}${list.map(k => `<a href="#src-${k}">${esc(of(meta.sources[k].short))}</a>`).join(W.cjk ? '、' : ', ')}</p>` : '';
const fig = q => q ? `<figure><img src="${esc(base + q.file)}" alt="${esc(of(q.caption))}" loading="lazy"><figcaption>${esc(of(q.caption))}<small>${esc(of(q.credit))}</small></figcaption></figure>` : '';
function words_() {
  document.title = `${of(meta.name)} · 一城春秋`;
  stage.setAttribute('aria-label', W.fmt('museumStage', { name: of(meta.name) }));
  $('back').href = `${LANG === 'zh' ? 'zh-hans/' : ''}${meta.city}/`; $('back-text').textContent = W.fmt('museumFilm', { city: of(meta.cityName) });
  $('tones-text').textContent = W.t('museumTones'); $('fly-text').textContent = W.t('museumFly'); $('hint').textContent = W.t('museumHint');
  $('lg-s').textContent = `${W.t('museumSourced')}: ${W.t('museumSourcedNote')}`; $('lg-e').textContent = `${W.t('museumEstimated')}: ${W.t('museumEstimatedNote')}`;
  $('ai-text').textContent = W.t('museumAi'); $('part-x').setAttribute('aria-label', W.t('close'));
  if (!ready) $('wait').textContent = W.t('museumLoading');
  for (const b of document.querySelectorAll('.langs button')) b.setAttribute('aria-pressed', String(b.dataset.lang === LANG));
  const alt = LANG === 'zh' ? meta.name.en : meta.name.zh;
  const walk = `play.html?city=${encodeURIComponent(meta.city)}&view&free&era=${encodeURIComponent(meta.node)}&lang=${LANG}${BUNDLE ? '&bundle=' + encodeURIComponent(BUNDLE) : ''}`;
  const [what, how, ...rest] = meta.label;
  $('label').innerHTML = `<h1>${esc(of(meta.name))}</h1><p class="alt">${esc(alt)}</p>
    <div class="facts"><p>${esc(of(meta.era))}</p><p>${esc(of(meta.where))}</p></div>
    ${[what, how].filter(Boolean).map((s, i) => `<h2>${esc(of(s.head))}</h2><p class="t">${esc(of(s.text))}</p>${cite(s.cite)}${i === 1 && meta.life && meta.life.photo ? fig(meta.life.photo) : ''}`).join('')}
    ${meta.life ? `<h2>${esc(W.t('museumLife'))}</h2><p class="t">${esc(of(meta.life.text))}</p>${cite(meta.life.cite)}${meta.life.pictures.map(fig).join('')}` : ''}
    ${rest.map(s => `<h2>${esc(of(s.head))}</h2><p class="t">${esc(of(s.text))}</p>${cite(s.cite)}`).join('')}
    <h2>${esc(W.t('museumParts'))}</h2><ul class="parts">${meta.parts.map(p => `<li><button type="button" data-part="${esc(p.id)}" aria-pressed="false"><span>${esc(of(p.name))}</span><span class="chip ${p.status}">${esc(W.t(p.status === 'sourced' ? 'museumSourced' : 'museumEstimated'))}</span></button></li>`).join('')}</ul>
    <h2>${esc(W.t('museumSources'))}</h2><ul class="sources">${Object.entries(meta.sources).map(([k, s]) => `<li id="src-${esc(k)}"><b>${esc(of(s.short))}</b>${esc(of(s))}${s.url ? `<br><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a>` : ''}</li>`).join('')}</ul>
    <p class="foot"><a href="${esc(walk)}">${esc(W.t('museumWalk'))}</a> · <a href="${REPO}" target="_blank" rel="noopener">一城春秋 · A City Through Time</a> · CC BY-SA 4.0</p>`;
  showPart(picked);
}

// the part picked on the model (or in the list): its note
let picked = null, M = null, ready = false;
function showPart(id) {
  picked = id; const p = meta.parts.find(q => q.id === id);
  $('part').hidden = !p;
  for (const b of document.querySelectorAll('[data-part]')) b.setAttribute('aria-pressed', String(b.dataset.part === id));
  if (!p) return;
  $('part-name').textContent = of(p.name);
  const st = $('part-status'); st.className = `chip ${p.status}`; st.textContent = W.t(p.status === 'sourced' ? 'museumSourced' : 'museumEstimated');
  $('part-note').textContent = of(p.note);
  $('part-cite').innerHTML = p.cite.length ? esc(W.fmt('museumCite', { list: p.cite.map(k => of(meta.sources[k].short)).join(W.cjk ? '、' : ', ') })) : '';
}
$('part-x').onclick = () => { showPart(null); M && M.select(null); };
$('label').addEventListener('click', e => { const b = e.target.closest('[data-part]'); if (!b) return;
  const id = picked === b.dataset.part ? null : b.dataset.part; showPart(id); M && M.select(id);
  if (id && matchMedia('(max-width: 860px)').matches) $('hall').scrollIntoView({ behavior: 'smooth' }); });
$('tones').onchange = e => { $('legend').hidden = !e.target.checked; M && M.tones(e.target.checked); };
$('fly').onclick = () => M && M.flyToNearest();
for (const b of document.querySelectorAll('.langs button')) b.onclick = () => { const q = new URLSearchParams(location.search); q.set('lang', b.dataset.lang); location.search = q; };
words_();

// the model: it takes over from the first picture once it draws that same frame
try {
  const { startMuseum } = await import('../engine/museum.js');
  const model = await (await fetch(base + meta.model)).json();
  M = await startMuseum({ stage, base, meta, model, clean: CLEAN, vp: main.id, on: {
    picture: ({ vp, a }) => {   // a picture shows: the AI label stays up; none: the way back to the nearest one
      const v = meta.viewpoints.find(q => q.id === vp);
      $('ai').hidden = !v; if (v) $('ai-vp').textContent = of(v.name);
      $('fly').hidden = !!v || !ready || !meta.viewpoints.some(q => q.picture);
    },
    pick: id => showPart(id),
  } });
  ready = true; $('wait').hidden = true; first.classList.add('gone'); setTimeout(() => { first.hidden = true; }, 800);
  window.MUSEUM = Object.assign(o => M.view(o), { m: M });
} catch (e) {
  $('wait').textContent = W.fmt('museumFail', { what: e.message }); throw e;
} finally { window.READY = true; }
