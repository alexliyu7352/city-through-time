// 《一城春秋》 A City Through Time: a generic white-model film driven by cities/<city>/build/film.json (compiled from city.yaml).
// render(t) is a pure function of t: camera from keys, projection state from the film's timeline, numbers from stats.json.
import * as THREE from 'three';
import { clamp, lerp, seg, ss, eio, eo, ei, track } from './lib.js';
import { makeStudio, NMAX, EMAX } from './studio.js';
import { makeOverlay, W, H, SUB, font, setFonts, setUI, REPO } from './overlay.js';
import * as L from './load.js';
import { moments as eraMoments, whole as standsWhole } from './eralife.js';

const QS = new URLSearchParams(location.search);
const CITY = QS.get('city');
if (!CITY) throw new Error('pass --q city=<slug>');
// the city's files: cities/<slug>/ beside this page, or a published bundle (?bundle=<url>: tools/web.py lays it out the same way,
// on any server that allows cross-origin reads, e.g. a Hugging Face dataset or a GitHub Pages site); the fonts always come from here
const BUNDLE = QS.get('bundle');
const base = BUNDLE ? BUNDLE.replace(/\/?$/, '/') : `cities/${CITY}/`, B = base + 'build/';   // what the city brings (assets) / what was made from it (pipeline/layout.py)
const newImage = () => Object.assign(new Image(), { crossOrigin: 'anonymous' });   // (a bundle on another server must not taint the canvases)
// every file is asked for at once (engine/load.js counts them for the loading screen, and none waits for the one before); a
// bundle's bundle.json (tools/web.py) gives their sizes
const PLAY = QS.has('play');
L.want(['film.json', 'data/model.json', 'data/stats.json', 'data/lines.json', 'data/water.png', 'data/layers1.png', 'data/layers2.png', 'data/layers3.png',
  'data/hide.png', 'data/hide2.png', 'data/edge.png', 'data/edge2.png'].map(f => B + f));
L.want([B + 'data/locator.png'], { optional: true });
if (BUNDLE) L.take(base + 'bundle.json', { optional: true }).then(b => b && b.text()).then(t => t && L.sizes(Object.fromEntries(JSON.parse(t).files.map(f => [base + f.path, f.bytes])))).catch(() => {});
const FILM = await L.json(B + 'film.json');
L.want([...(FILM.decals || []).map(d => B + d.file), FILM.satellite && B + FILM.satellite.file, FILM.grow && FILM.grow.tfile && B + FILM.grow.tfile,
  ...(FILM.eras || []).map(e => B + e.file), ...(FILM.footage || []).map(f => base + f.file)]);
if (FILM.context && !QS.has('flat')) L.want([B + FILM.context.file], { optional: true });
L.want((FILM.living || []).map(v => base + v.file), { optional: true });   // (a living moment's picture: missing until tools/living.py has made it)
L.sizes(Object.fromEntries(FILM.fonts.faces.filter(f => f.bytes).map(f => [f.file, f.bytes])));   // (the fonts come from this page's server)
L.want(FILM.fonts.faces.map(f => f.file));
const SOUND = PLAY ? [FILM.voice && FILM.voice.file, FILM.score && FILM.score.file, FILM.sfx && FILM.sfx.file, FILM.score && FILM.score.loop].map(f => f && B + f) : [];
L.want(SOUND, { optional: true });   // (the live page plays them: the loading screen waits for them too, so ▶ never plays silent)
L.plan();
const [M, ST, LN] = await Promise.all([L.json(B + 'data/model.json'), L.json(B + 'data/stats.json'), L.json(B + 'data/lines.json')]);
if (M.terrain && !QS.has('flat')) L.want([B + 'data/terrain16.png'], { optional: true });   // (16-bit relief; terrain.png is asked for only without it)
// a picture from its file: a texture, or an image (null for an optional one that is missing)
const tex = async u => { const o = await L.address(u); try { return await TL.loadAsync(o); } finally { URL.revokeObjectURL(o); } };
const image = async (u, optional = false) => {
  const o = await L.address(u, { optional }); if (!o) return null;
  const im = newImage(); im.src = o;
  try { await new Promise((res, rej) => { im.onload = res; im.onerror = () => rej(new Error('image: ' + u)); }); return im; }
  catch (e) { if (optional) return null; throw e; } finally { URL.revokeObjectURL(o); }
};
const DUR = FILM.dur; window.DUR = DUR;
// a year as the film's language writes it (compile: FILM.years from i18n/<code>.yaml), else the older zh / en switch
const yearAs = (y, tick) => { const Y = FILM.years; if (!Y) return null; const r = Math.round(y); return (r < 0 ? (tick ? Y.tick_bce || Y.bce : Y.bce) : (tick ? Y.tick_ce || Y.ce : Y.ce)).replace('{y}', Math.abs(r)); };
if (FILM.bar) for (const tk of FILM.bar.ticks) tk.yearLabel = yearAs(tk.year, true) ?? (FILM.yearFmt === 'en' ? (tk.year < 0 ? `${-tk.year} BCE` : `${tk.year}`) : (tk.year < 0 ? `前${-tk.year}` : `${tk.year}`));

const LOW = QS.get('quality') === 'low' || QS.has('play');
const S = makeStudio(W, H, M, FILM.palette, { low: LOW && QS.get('quality') !== 'high' });
const { U, camera, post, renderer, house, hemi, scene } = S;
const TL = new THREE.TextureLoader();
const decalTex = await Promise.all((FILM.decals || []).map(d => tex(B + d.file)));
const photoTex = FILM.satellite ? await tex(B + FILM.satellite.file) : null;
let terrain = null;
if (M.terrain && !QS.has('flat')) {
  let img = await image(B + 'data/terrain16.png', true); const sixteen = !!img;   // 16-bit relief in R/G; the 8-bit file is the fallback
  if (!img) img = await image(B + 'data/terrain.png');
  img.sixteen = sixteen;
  terrain = { img, info: M.terrain };
}
if (FILM.change) S.setRenew(FILM.change.renew, FILM.change.early);
if (FILM.grow && FILM.grow.tfile) S.setGrowT(await L.json(B + FILM.grow.tfile));   // buildings that wait until the camera sees them
if (FILM.grow && FILM.grow.yl) {   // the modern year line: today's buildings rise when the counter first reaches their year
  FILM.grow.yl.forEach(([t, y], i) => { S.U.uYLt.value[i] = t; S.U.uYLy.value[i] = y; }); S.U.uYLn.value = FILM.grow.yl.length;
}
const CITYMESH = S.build(await tex(B + 'data/water.png'), await tex(B + 'data/layers1.png'), await tex(B + 'data/layers2.png'), await tex(B + 'data/layers3.png'), decalTex, photoTex, terrain);
// the land beyond the plate (terrain.context): relief for a mountain or river off the plate, shown in the nodes that ask for it
if (FILM.context && !QS.has('flat')) {
  const im = await image(B + FILM.context.file, true);
  if (im) S.addContext(im, FILM.context);
}
const CTXK = FILM.context && FILM.context.keys.length ? track(FILM.context.keys) : null;
// props: schematic models per node
for (const p of FILM.props || []) S.addProp(p);
for (const r of FILM.routes || []) S.addRoute(r.id, r.pts, r.col, r.w);
// era cities: one generated city per period
const ERABOX = {};   // each period city's extent on the plate [x0, z0, x1, z1]; for the viewer (?view) the moments it is shown at (engine/eralife.js), each with its densest 200 m square [x, z] then
for (const e of FILM.eras || []) {
  const J = await L.json(B + e.file); S.addEra(e.id, J.prims, e.col, J.lost || null);
  const b = J.prims.reduce((b, p) => [Math.min(b[0], p[1]), Math.min(b[1], p[2]), Math.max(b[2], p[1]), Math.max(b[3], p[2])], [Infinity, Infinity, -Infinity, -Infinity]);
  ERABOX[e.id] = { box: b };
  if (QS.has('view')) ERABOX[e.id].moments = eraMoments(e, J.prims, J.lost).map(t => {
    const cell = 200 * M.scale, n = new Map(); let top = null, kt = null;   // (aimed at a building there, the one nearest its buildings' centre: not the
    const up = (p, i) => standsWhole(e, p[10], J.lost ? J.lost[i] : 0, t);                    //  square's middle, nor a gap between two rows)
    J.prims.forEach((p, i) => { if (!up(p, i)) return;
      const k = `${Math.floor(p[1] / cell)},${Math.floor(p[2] / cell)}`, c = n.get(k) || [0, 0, 0]; c[0]++; c[1] += p[1]; c[2] += p[2]; n.set(k, c); if (!top || c[0] > top[0]) { top = c; kt = k; } });
    if (!top) return { t, dense: [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2] };
    const cx = top[1] / top[0], cz = top[2] / top[0]; let best = null, bd = Infinity;
    J.prims.forEach((p, i) => { if (!up(p, i) || `${Math.floor(p[1] / cell)},${Math.floor(p[2] / cell)}` !== kt) return; const d = Math.hypot(p[1] - cx, p[2] - cz); if (d < bd) { bd = d; best = [p[1], p[2]]; } });
    return { t, dense: best }; });
  if (e.sinkStyle === 'burn') { const seen = new Set(), cs = [];   // one spark source per building
    for (const p of J.prims) { const k = `${p[15] ?? p[1]},${p[16] ?? p[2]}`; if (p[11] === 4 || p[11] === 5 || p[11] === 7 || seen.has(k)) continue; seen.add(k); cs.push([p[15] ?? p[1], p[16] ?? p[2]]); }
    S.addFire(e.id, cs, S.ground); }
}
const LOOK = FILM.era_look || {}; S.U.uEdgeGain.value = LOOK.edge ?? 1; S.U.uEdgeLight.value = (LOOK.light_m ?? 45) * M.scale; S.U.uEdgeHalo.value = (LOOK.halo_m ?? 14) * M.scale;
for (const e of FILM.eras || []) {   // each standing city's edge: its distance field crop, and the neon line on its outline
  if (e.hide != null && e.edgeRect && !e.occupy) { S.U.uEdgeRect.value[e.hide].set(...e.edgeRect); S.U.uEdgeD.value[e.hide] = e.edgeD; }   // (a shared channel: set by the city it holds)
  const sc = (e.fronts || []).find(f => f.mode === 'scan');   // a small place: its outline draws itself from where the scan starts
  if (e.boundary && e.boundary.length) S.addEdge(e.id, e.boundary, e.col, sc ? sc.dir : null);
}
// a period city takes the colour of the node being told: its own colour in its own node, a paler node colour in a later one
const WHITE = new THREE.Color(1, 1, 1), ownNode = e => (FILM.nodes || []).find(n => n.id === e.id);
const ringT0 = n => n.ring ? n.ring.t0 : n.t0;   // a node's colour arrives with its ring (at its beam's landing when it has one)
const later = (e, n) => n && n.id !== e.id && n.tint > 0 && ringT0(n) >= e.on - .01;   // a node told after this city rose, that recolours it
const eraTint = (e, n) => later(e, n) ? new THREE.Color(n.col).lerp(WHITE, .12) : S.eras[e.id].base;
const eraInk = (e, n) => later(e, n) ? n.ink || 0 : (ownNode(e) || {}).ink || 0;
const DIMK = FILM.dim && FILM.dim.length ? track(FILM.dim) : null;
// how far a period city stands at t: as it rises, or with stages as its first stage rises (compile up), so a part built
// later does not keep today's city bright and the city unlit until it is up; it goes with its contracting ring
const upAt = (e, t) => { const FR = e.fallR; if (FR != null && t > FR.gone) return 0;
  const [a, b] = e.up || [e.on, e.on + e.span + e.grow];
  return ss(seg(t, a, b)) * (FR ? 1 - ss(seg(t, FR.hit, FR.gone)) : 1); };
const eraUpAt = t => Math.max(0, ...(FILM.eras || []).map(e => upAt(e, t)));
const dimAt = (t, up = eraUpAt(t)) => Math.max((LOOK.dim ?? .8) * up, DIMK ? DIMK(t)[0] : 0);
const DIM0 = new Map(); const dimBefore = n => { if (!DIM0.has(n.id)) DIM0.set(n.id, dimAt(ringT0(n) - .01)); return DIM0.get(n.id); };
// a node's colour ring: radius at time t (the plate's far corner from its origin is reached after wave_dur seconds)
// sampled curves from compile (pipeline/stagecraft.py): ring radius over time; linear between samples, clamped at the ends
const curveAt = (c, t) => { if (!c || !c.length) return -1; if (t <= c[0][0]) return c[0][1]; const n = c.length; if (t >= c[n - 1][0]) return c[n - 1][1];
  let lo = 0, hi = n - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (c[m][0] <= t) lo = m; else hi = m; } return c[lo][1] + (c[hi][1] - c[lo][1]) * (t - c[lo][0]) / ((c[hi][0] - c[lo][0]) || 1e-9); };
const ringR = (n, t) => n.ring && t < n.ring.curve[n.ring.curve.length - 1][0] ? curveAt(n.ring.curve, t) : 99;
S.setHide(...await Promise.all(['hide', 'hide2', 'edge', 'edge2'].map(f => tex(B + `data/${f}.png`))));
// cities apart in time share a channel (compile: era channels): a shared channel holds, at any moment, the city in use then
// (its intervals in `occupy`), drawn in from its own files when it takes the channel over (studio shareChannels); the
// files hold each channel's first city. Only the city a channel holds sets that channel's uniforms.
const SHARE = (FILM.eras || []).filter(e => e.occupy && e.hide != null), holding = {};
let CH = null;
if (SHARE.length) {
  CH = S.shareChannels();
  for (const e of SHARE) e._own = await Promise.all([tex(B + `data/hide_${e.id}.png`), tex(B + `data/edge_${e.id}.png`)]);
  for (const e of [...SHARE].sort((a, b) => b.occupy[0][0] - a.occupy[0][0])) holding[e.hide] = e;   // (the earliest last: it wins)
  for (const e of Object.values(holding)) if (e.edgeRect) { S.U.uEdgeRect.value[e.hide].set(...e.edgeRect); S.U.uEdgeD.value[e.hide] = e.edgeD; }
}
if (FILM.basinMap) S.setBasins(await tex(B + FILM.basinMap.file), FILM.basinMap);   // dug pools: the plate lowered in them while they stand
// a basin follows its pool: up as the pool rises (its rank in its city's rise), taken back with its city's ring or its loss's
const ringK = (c, q, t, sd) => { if (!q) return 0; const R = curveAt(q.curve, t), R1 = curveAt(q.curve, t - sd), d = Math.hypot(c[0] - q.o[0], c[1] - q.o[1]);
  const a = q.mode === 'in' ? (d - R) / Math.max(R1 - R, 1e-5) : (R - d) / Math.max(R - R1, 1e-5); return ss(Math.min(1, Math.max(0, a))); };   // (studio fallK)
const takeChannel = e => { if (!CH || !e.occupy || holding[e.hide] === e) return; CH.put(e.hide, ...e._own); holding[e.hide] = e;
  if (e.edgeRect) { S.U.uEdgeRect.value[e.hide].set(...e.edgeRect); S.U.uEdgeD.value[e.hide] = e.edgeD; } };
const inChannel = e => !e.occupy || holding[e.hide] === e;
{ const cols = Array(8).fill('#ffffff'); for (const e of FILM.eras || []) if (e.hide != null) cols[e.hide] = e.col; S.setHideCols(cols); }
S.U.uScaleH.value = M.scale * (M.bex || (M.terrain && M.terrain.exaggeration) || 3);   // window floors follow the buildings' own exaggeration
S.U.uScaleM.value = M.scale;   // model units per metre (textures drawn at their real size)
// terrain.shade: a fixed low sun on the plate: the slopes turned to it lighter in the plate's own colour, those turned away darker,
// so the relief reads in any light of the room; flat ground and water keep the plate's colour
if (FILM.shade) { const a = THREE.MathUtils.degToRad(FILM.shade.az), e = THREE.MathUtils.degToRad(FILM.shade.el);
  S.U.uShadeL.value.set(Math.sin(a) * Math.cos(e), Math.sin(e), -Math.cos(a) * Math.cos(e)); S.U.uShadeK.value = FILM.shade.k; S.U.uShadeC.value.set(FILM.shade.col || (FILM.palette || {}).plate || '#3a4757'); }
const TK = FILM.tally && FILM.tally.keys && FILM.tally.keys.length ? track(FILM.tally.keys) : null;
for (const d of FILM.decals || []) U.uDrect.value[d.i].set(d.uv[0], d.uv[1], d.uv[2], d.uv[3]);
U.uNightDeep.value = (FILM.night_look && FILM.night_look.deep) || 0;   // film.night_look.deep: the night city (docs/STAGING.md)
// living moments (film.living, docs/STAGING.md "Living moments"): a picture of the period made from this very shot of the model and
// projected back onto it from the shot's own camera. The camera arrives and stops (the projection is exact only from there: it may
// zoom, never move), today's city sinks, a ring of light spreads from the viewer and turns the white model into the living town,
// the sky and the far land come with it; it holds (a slow zoom, weather), dissolves back to the model, and the camera goes on
const LIVING = FILM.living || [], LIVETEX = {}, PCAM = new THREE.PerspectiveCamera();
for (const v of LIVING) { try { const t_ = await tex(base + v.file); t_.colorSpace = THREE.SRGBColorSpace; t_.anisotropy = 8; LIVETEX[v.id] = t_; } catch { /* no picture yet: compile said so */ } }
let LV = null;   // this frame's moment: { L, cam: the shot's share of the camera, k: the scene's (today sunk, lines out), pa: the picture, r: the ring, sky, zoom }
function liveAt(t) {
  for (const L of LIVING) {
    const a0 = L.on - L.arrive, r1 = L.on + L.reveal, h1 = r1 + L.hold, o1 = h1 + L.out, b1 = o1 + L.back;
    if (t < a0 || t > b1) continue;
    const cam = t < L.on ? ss(seg(t, a0, L.on)) : t <= o1 ? 1 : 1 - ss(seg(t, o1, b1));
    const k = t < L.on ? ss(seg(t, a0 + L.arrive * .3, L.on)) : t <= o1 ? 1 : 1 - ss(seg(t, o1, b1));
    const rk = seg(t, L.on, r1), e = ss(Math.min(1, rk / .82)), tail = Math.max(0, (rk - .82) / .18);   // the ring crosses the town, then runs out to the horizon
    return { L, cam, k, pa: t < L.on ? 0 : 1 - ss(seg(t, h1, o1)), r: t < L.on ? 0 : 6 * L.cam[5] * e + 2 * tail * tail, sky: ss(seg(rk, .35, .85)), zoom: lerp(1, L.zoom, ss(seg(t, r1, h1))) };
  }
  return null;
}
function setLiving(t) {
  const Wp = post.weather, L = LV && LV.L, tx_ = L && LIVETEX[L.id];
  U.uLiveSink.value = LV ? LV.k : 0; U.uEdgeGain.value = (LOOK.edge ?? 1) * (1 - (LV ? LV.k : 0));
  if (!tx_) { U.uPA.value = 0; S.liveSky.visible = false; Wp.enabled = false; return; }   // (no moment now, or its picture is not made yet: the white model holds the shot)
  const [px, py, pz, paz, pel, pd, pfov] = L.cam, a = THREE.MathUtils.degToRad(paz), e = THREE.MathUtils.degToRad(pel);   // the projector: the shot's camera, no drift, no zoom
  PCAM.fov = pfov; PCAM.aspect = W / H; PCAM.near = Math.min(.02, Math.max(.0003, pd * .04)); PCAM.far = camera.far;
  PCAM.position.set(px + pd * Math.sin(a) * Math.cos(e), py + pd * Math.sin(e), pz + pd * Math.cos(a) * Math.cos(e)); PCAM.lookAt(px, py, pz);
  PCAM.updateProjectionMatrix(); PCAM.updateMatrixWorld(); U.uPM.value.multiplyMatrices(PCAM.projectionMatrix, PCAM.matrixWorldInverse); U.uPI.value = tx_;
  U.uPA.value = LV.pa; U.uPRC.value.set(L.origin[0], L.origin[1]); U.uPRR.value = LV.r; U.uPF.value = LV.sky; U.uPF0.value = 5 * pd; U.uPF1.value = 8 * pd;
  const dist = .3, hh = 2 * dist * Math.tan(THREE.MathUtils.degToRad(pfov / 2)), fwd = new THREE.Vector3(); PCAM.getWorldDirection(fwd);   // the sky card behind the town
  S.liveSky.position.copy(PCAM.position).addScaledVector(fwd, dist); S.liveSky.quaternion.copy(PCAM.quaternion); S.liveSky.scale.set(hh * PCAM.aspect * 1.6, hh * 1.6, 1);
  S.liveSky.material.uniforms.uA.value = LV.sky * LV.pa; S.liveSky.visible = LV.sky * LV.pa > 0;
  const wk = LV.sky * LV.pa; Wp.enabled = wk > 0 && (L.rain > 0 || L.mist > 0);
  Wp.uniforms.uRain.value = L.rain * wk; Wp.uniforms.uMist.value = L.mist * wk; Wp.uniforms.uMistY.value = L.mistY; Wp.uniforms.uT.value = t;
}
// real footage: one <video> per clip, seeked deterministically to the frame's time
const VID = {};
for (const f of FILM.footage || []) {
  if (/\.(jpe?g|png|webp)$/i.test(f.file)) { VID[f.id] = await image(base + f.file); continue; }
  const v = document.createElement('video'); v.src = await L.address(base + f.file); v.muted = true; v.preload = 'auto';   // (the whole clip in memory: seeks never wait on the network)
  await new Promise((res, rej) => { v.onloadeddata = res; v.onerror = () => rej(new Error('footage: ' + f.file)); v.load(); });
  VID[f.id] = v;
}
const LOC = await image(B + 'data/locator.png', true) || newImage();
const seekTo = (v, time) => new Promise(res => { if (Math.abs(v.currentTime - time) < 1 / 60) return res(); const done = () => { v.removeEventListener('seeked', done); res(); }; v.addEventListener('seeked', done); v.currentTime = time; });
const OV = makeOverlay(document.getElementById('ov'));

// projected lines: groups of OSM / custom polylines
const lineA = {};
for (const L of FILM.lines || []) {
  let pls;
  if (L.src === 'custom') pls = L.pts;
  else {
    const re = L.filter ? new RegExp(L.filter) : null;
    pls = (LN[L.src] || []).filter(w => !re || re.test(JSON.stringify(w.tags || {}) + (w.name || '') + (w.cls || ''))).map(w => w.pts);
  }
  lineA[L.id] = S.addLines(L.id, pls, L.col, L.width || .0015, L.flow || 0, L.screen ? 3 : 1);
}

const proj3 = (x, y, z) => { const v = new THREE.Vector3(x, y, z).project(camera); return v.z < 1 ? [(v.x * .5 + .5) * W, (-v.y * .5 + .5) * H] : null; };
const at = p => proj3(p[0], p[2] || 0, p[1]);   // [x, z, h] -> screen

// ------------------------------------------------------------------ year line: t -> year (piecewise linear)
const YL = FILM.yearline;
function yearAt(t) {
  if (t <= YL[0][0]) return YL[0][1];
  for (let i = 0; i < YL.length - 1; i++) if (t < YL[i + 1][0]) return lerp(YL[i][1], YL[i + 1][1], seg(t, YL[i][0], YL[i + 1][0]));
  return YL[YL.length - 1][1];
}
const fmtYear = y => { const r = Math.round(y); return yearAs(y, false) ?? (FILM.yearFmt === 'en' ? (r < 0 ? `${-r} BCE` : `${r}`) : (r < 0 ? `前 ${-r}` : `${r}`)); };

// ------------------------------------------------------------------ camera
const CAM = track(FILM.camera);
const tgt = new THREE.Vector3();
const CAMQ = QS.has('cam') ? QS.get('cam').split(',').map(Number) : null;   // stills: a fixed camera "tx,ty,tz,az,el,d"
let camDist = 1, camElev = 30;
function setCamera(t) {
  let [tx, ty, tz, az, el, d, fov] = CAMQ || CAM(t);
  const lb = LV && !CAMQ ? LV.cam : 0;   // a living moment's shot takes over: the camera arrives, stops (it may only zoom), and leaves
  if (lb > 0) { const s_ = LV.L.cam, daz = ((s_[3] - az) % 360 + 540) % 360 - 180;
    tx = lerp(tx, s_[0], lb); ty = lerp(ty, s_[1], lb); tz = lerp(tz, s_[2], lb); az += daz * lb; el = lerp(el, s_[4], lb); d = lerp(d, s_[5], lb); fov = lerp(fov || FILM.fov || 30, s_[6] * LV.zoom, lb); }
  camDist = d; camElev = el; const az0 = az;   // (the key light turns with the shot, not the drift)
  // a breath of hand-held drift so holds never freeze (deterministic in t, scaled to the shot's distance; none on a living moment's shot)
  const DF = (FILM.drift ?? 1) * (1 - lb), dr = DF * d * .012; az += Math.sin(t * .37) * .9 * DF; el += Math.sin(t * .23 + 1.2) * .5 * DF;
  tx += Math.sin(t * .29 + .4) * dr; tz += Math.cos(t * .19 + 2.1) * dr; ty += Math.sin(t * .31 + .9) * dr * .3;
  tgt.set(tx, ty, tz); S.followShadow(tx, ty, tz, d, az0);
  const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el);
  camera.position.set(tx + d * Math.sin(a) * Math.cos(e), ty + d * Math.sin(e), tz + d * Math.cos(a) * Math.cos(e));
  camera.fov = fov || FILM.fov || 30;
  camera.near = Math.min(.02, Math.max(.0003, d * .04));   // close shots fly through the streets: the near plane follows the distance
  camera.updateProjectionMatrix(); camera.lookAt(tgt); camera.updateMatrixWorld();
  lens(d); if (LV) post.dof.aper *= 1 - LV.k;   // (no depth of field over a living moment: the picture is sharp throughout)
}
// depth of field: blur in pixels goes as aperture / distance, so close shots get a proportionally smaller aperture
function lens(d) { post.dof.focus = d; post.dof.aper = d < .15 ? lerp(1.6, 3.2, seg(d, .04, .15)) * Math.max(.2, d / .15) : lerp(3.2, 1.6, seg(d, .15, 2.2)); post.dof.maxCoc = d < .15 ? 7 : 10; }

// ------------------------------------------------------------------ light and projection state
const LT = FILM.light;
// the prologue (film.prologue, docs/SCRIPT.md): a passage before the opening with its own camera, words and pictures over the
// film's own city. From each scene key on, the city (light, layers, the sky) shows the film at that moment and plays on; the
// camera and the words keep the film's own clock. It closes on a short black.
const PRO = FILM.prologue;
const sceneAt = t => { if (!PRO || t >= PRO.dur) return t; let s = t; for (const [k, at] of PRO.scene) if (t >= k) s = at + (t - k); return s; };
const darkAt = t => (LT.darks || []).some(([a, b]) => t >= a && t < b);
const NTRACK = FILM.night && FILM.night.length ? track(FILM.night) : null; const nightAt = t => NTRACK ? NTRACK(t)[0] : 0;
const darkK = t => { let k = 0; for (const [a, b] of (LT.darks || [])) k = Math.max(k, ss(seg(t, a, a + .35)) * (1 - ss(seg(t, b - .1, b + .4)))); return k; };
function setLight(t) {
  const off = ss(seg(t, LT.lightsOut, LT.lightsOut + .25));
  const back = ss(seg(t, LT.lights, LT.lights + 1.0));
  const houseK = lerp(1, LT.base ?? .28, off) * (1 - back) + .9 * back;   // the room light comes back on the white city at the end
  const nt = nightAt(t);
  house.intensity = 2.0 * houseK * (1 - .82 * nt); hemi.intensity = (.3 * houseK + .015) * (1 - .6 * nt);
  scene.environmentIntensity = lerp(.03, .32, houseK) * (1 - .7 * nt);   // a neutral studio environment, kept low: its light panels mirror on the flat plate
  scene.backgroundIntensity = lerp(.5, 1, houseK);
  post.bloom.threshold = lerp(1.6, 1.1, Math.min(off, 1 - back));
  U.uFootM.value = Math.max(4, 3 * camDist / M.scale * 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) / 1080);   // the walls' dark foot: 4 m, or 3 pixels' worth at the target
  post.dof.coc.material.uniforms.edgeAmt.value = QS.has('noedge') ? 0 : (FILM.edges ?? .55) * (1 - ss(seg(camDist, .25, .9))) * (1 - (LV ? LV.k : 0));   // fine lines on the close shots
  const strike = seg(t, LT.lamp, LT.lamp + .12), flick = t > LT.lamp && t < LT.lamp + .25 ? .75 + .25 * Math.sin((t - LT.lamp) * 90) : 1;
  U.uProj.value = strike * flick * (1 - darkK(t)) * (1 - ss(seg(t, LT.lights, LT.lights + .8)));
  S.setBeam(U.uProj.value, ((FILM.epochs || []).some(e => e.offStyle === 'burn' && t >= e.off && t < e.off + (e.offDur ?? 1.2) + 1.5) || (FILM.eras || []).some(e => e.sinkStyle === 'burn' && t >= e.off - e.burn * .6 && t < e.off + e.sink)) ? 1 : 0, t);
  U.uNow.value = t; U.uYear.value = yearAt(t);
  U.uBase.value = ss(seg(t, LT.lamp, LT.lamp + 1.2));
  // the century rings around the old town: one ring per century of the counter, drawn by the projector
  if (FILM.rings_motif) { const R = FILM.rings_motif; U.uRingC.value.set(R.centre[0], R.centre[1]); U.uRingS.value = R.spacing; U.uRingN.value = Math.max(0, (yearAt(t) - R.from) / 100) * ss(seg(t, LT.lamp + .5, LT.lamp + 2)) * (1 - ss(seg(t, LT.lights - .5, LT.lights + .5))); U.uRingA.value = R.gain ?? .5; }
  // a pulse of light when a node begins
  let pulse = 0; for (const nd of FILM.nodes || []) pulse = Math.max(pulse, Math.exp(-Math.max(0, t - nd.t0) / .9) * (t >= nd.t0 ? 1 : 0));
  U.uPulse.value = pulse;
}
// an epoch's alpha over time: fade in at `on`, out at `off` (burn = a flicker then dark)
function epochAlpha(t, e) {
  let a = ss(seg(t, e.on, e.on + (e.fade ?? 1.2)));
  if (e.off != null) {
    if (e.offStyle === 'burn') {
      const k = seg(t, e.off, e.off + (e.offDur ?? 1.2));
      const fl = k > 0 && k < 1 ? .55 + .45 * Math.abs(Math.sin(k * 41 + Math.sin(k * 17) * 3)) : 1;
      a *= (1 - ei(k)) * fl;
    } else a *= 1 - ss(seg(t, e.off, e.off + (e.offDur ?? 1.0)));
  }
  return a;
}
// a period city's own shape at a moment of the film: each building's rise (its stage), its pools, the parts it has lost
// (setLayers; the viewer, ?view, at the moment it shows the city)
function eraShape(e, t) {
  const E = S.eras[e.id], SD = e.fallDur || 1.4, FR = e.fallR;
  E.u.uEraT.value = t - e.on; E.u.uEraSpan.value = e.span; E.u.uEraGrow.value = e.grow;
  for (const b of e.basins || []) { const st = e.on + b.rank * e.span, q = b.lost ? e.losses[b.lost - 1] : null;
    U.uBasinA.value[b.k] = ss(seg(t, st, st + e.grow)) * (1 - ringK(b.c, FR, t, SD)) * (1 - (q && !b.draped ? ringK(b.c, q, t, SD) : 0));
    if (b.draped && q) {   // a draped pool is the plate: its water goes point by point as its loss's ring passes (studio wmask)
      const R = curveAt(q.curve, t), R1 = curveAt(q.curve, t - SD);
      U.uBasinL.value[b.k].set(q.o[0], q.o[1], R, q.mode === 'in' ? Math.max(R1, R + 1e-5) : Math.min(R1, R - 1e-5)); } }   // (which side of R tells the ring's way)
  (e.losses || []).forEach((q, j) => {   // a part of the city lost while the rest stands (compile lose:): its own ring, its own fire
    E.u.uLossR.value[j] = curveAt(q.curve, t); E.u.uLossW.value[j] = curveAt(q.curve, t - SD); E.u.uLossIn.value[j] = q.mode === 'in' ? 1 : 0;
    E.u.uLossO.value[j].set(q.o[0], q.o[1]); E.u.uLossBurn.value[j] = q.burn && t < q.gone ? ss(seg(t, q.burn[0], q.burn[1])) : 0; });
}
function setLayers(t) {
  { let sk = 0, sp = null;   // spot (film.spots): the light falls on one subject, the rest of the room goes dark
    for (const q of FILM.spots || []) { const a = ss(seg(t, q.t0, q.t0 + q.fade)) * (1 - ss(seg(t, q.t1 - q.fade, q.t1))); if (a > sk) { sk = a; sp = q; } }
    U.uSpotK.value = sp ? lerp(1, sp.k, sk) : 1; U.uSpotB.value = sp ? lerp(1, sp.b, sk) : 1; if (sp) { U.uSpotC.value.set(sp.c[0], sp.c[1]); U.uSpotR.value = sp.r; } }
  for (let i = 0; i < EMAX; i++) { U.uEpA.value[i] = 0; U.uEpY0.value[i] = 1e9; U.uEpY1.value[i] = -1e9; U.uEpB.value[i] = 0; U.uEpR.value[i] = 9; U.uEpW.value[i] = 1; }
  for (const e of FILM.epochs || []) {   // (masks that share a channel never overlap in time: the one showing sets it)
    const fl = (e.flash || []).reduce((m, tf) => Math.max(m, Math.exp(-(((t - tf) / .45) ** 2))), 0);   // an area flares as it is named
    const a = epochAlpha(t, e) * (e.gain ?? 1) * (e.dimAt != null && t > e.dimAt ? lerp(1, e.dimTo ?? .5, ss(seg(t, e.dimAt, e.dimAt + .8))) : 1) * (1 + 1.4 * fl);
    if (a <= 0 && U.uEpA.value[e.i] > 0) continue;
    U.uEpA.value[e.i] = a;
    if (e.yr) { U.uEpY0.value[e.i] = e.yr[0]; U.uEpY1.value[e.i] = e.yr[1]; }
    U.uEpB.value[e.i] = e.bld ? 1 : 0;
    if (e.centre) { U.uEpC.value[e.i].set(e.centre[0], e.centre[1]); U.uEpR.value[e.i] = lerp(0, e.reach || 1, eo(seg(t, e.on, e.on + (e.fade ?? 1.2) * 1.6))); }
    U.uEpRim.value[e.i] = e.rim ?? 1; U.uEpW.value[e.i] = e.wash ?? 1;
    if (e.col) U.cEp.value[e.i].set(e.col);
  }
  for (const d of FILM.decals || []) { U.uDA.value[d.i] = epochAlpha(t, d) * (d.gain ?? 1); U.uDG.value[d.i] = d.glow ?? 1; }
  let pdim = 1;
  for (const d of FILM.decals || []) if (d.photo_dim) pdim *= 1 - d.photo_dim * epochAlpha(t, d);
  const roomBack = ss(seg(t, LT.lights - .2, LT.lights + 1.2));
  const SAT = FILM.satellite;
  let satOn = 0;
  if (SAT && SAT.sweep) {   // a line crosses the plate west to east over the fade time; the photo replaces the model behind it; a second line gives the model back
    const k = seg(t, SAT.on, SAT.on + (SAT.fade ?? 4)), k2 = SAT.back != null ? seg(t, SAT.back, SAT.back + (SAT.backFade ?? 4)) : 0;
    satOn = k > 0 && k2 < 1 ? 1 : 0;
    U.uPhotoA.value = satOn * (1 - roomBack); U.uPhotoSweep.value = k >= 1 ? 2 : eo(k) * 1.02 - .01; U.uPhotoSweep0.value = k2 <= 0 ? -1 : eo(k2) * 1.02 - .01;
  } else { satOn = SAT ? epochAlpha(t, SAT) : 0; U.uPhotoA.value = satOn * (1 - roomBack); U.uPhotoSweep.value = 2; U.uPhotoSweep0.value = -1; }
  U.uPhotoK.value = (SAT?.gain ?? 1) * pdim;
  for (const L of FILM.lines || []) if (lineA[L.id]) {   // (an area's outline flares as it is named)
    const fl = (L.flash || []).reduce((m, tf) => Math.max(m, Math.exp(-(((t - tf) / .45) ** 2))), 0);
    lineA[L.id].value = epochAlpha(t, L) * (L.gain || 1) * (1 + 2.2 * fl) * (1 - (LV ? LV.k : 0));
  }
  const G = FILM.grow;
  if (G) {
    U.uGrowOn.value = t >= G.on - .01 ? 1 : 0; U.uGrowMono.value = G.mono ? 1 : 0; U.uGrowWarm.value = G.warm || 0;
    U.uNB.value = FILM.bands.length;
    FILM.bands.forEach((b, i) => { U.uBLo.value[i] = b.lo; });
    for (const b of G.bands) { U.uGT.value[b.band] = b.t; U.uGS.value[b.band] = b.spread; }
    U.uGrowDim.value = (G.dim ? lerp(1, G.dim.to, ss(seg(t, G.dim.t, G.dim.t + .8))) : 1) * (1 - .6 * nightAt(t)) * (1 - satOn);
  } else U.uGrowOn.value = 0;
  const Hh = FILM.height;
  if (Hh) {
    U.uHgtOn.value = t > Hh.t0 && (Hh.off == null || t < Hh.off) ? 1 : 0;
    U.uHgtMax.value = Hh.max_m;
    U.uHgtF.value = lerp(-.003, Hh.top + .005, eo(seg(t, Hh.t0, Hh.t1)) * .5 + ss(seg(t, Hh.t0, Hh.t1)) * .5);
    U.uHgtBand.value = ss(seg(t, Hh.t0, Hh.t0 + .4)) * (1 - ss(seg(t, Hh.t1 - .1, Hh.t1 + .4)));
  }
  // the model's height: full "today" (house light), sunk after the lamp, then rising by year from the growth node
  const R = FILM.rise || {};
  const today = Math.max(1 - ss(seg(t, R.sinkAt ?? LT.lamp, (R.sinkAt ?? LT.lamp) + (R.sinkDur ?? 2.0))), ss(seg(t, LT.lights - .2, LT.lights + 1.2)));
  U.uToday.value = today; U.uGrowRise.value = FILM.grow ? ss(seg(t, FILM.grow.on - .5, FILM.grow.on + .5)) : 0;
  U.uGhost.value = (R.ghost ?? .05) * ss(seg(t, LT.lamp + 1.5, LT.lamp + 4));
  for (const p of FILM.props || []) {
    const mesh = S.props[p.id]; if (!mesh) continue;
    const a = epochAlpha(t, p); mesh.visible = a > 0.002; mesh.scale.y = Math.max(.002, a);
  }
  { // today's white city takes the colour of the age being told: the new colour spreads as a ring of light from the node's
    // origin (its beam's landing point, at the landing, with a flash and a shock ring) on a curve paced on screen (compile)
    const nodes = FILM.nodes || []; let cur = -1;
    for (let i = 0; i < nodes.length; i++) if (t >= ringT0(nodes[i])) cur = i;
    const gain = (1 - today) * U.uProj.value;
    U.uShockA.value = 0;
    if (cur < 0) { U.uNodeA.value = U.uNodeA0.value = 0; U.uNodeR.value = 99; U.uNodeFront.value = 0; }
    else {
      const n = nodes[cur], p = cur ? nodes[cur - 1] : null, c = n.ring.curve, t1 = c[c.length - 1][0], k = seg(t, n.ring.t0, t1);
      U.uNodeCol.value.set(n.col); U.uNodeA.value = (n.tint || 0) * gain;
      U.uNodeCol0.value.set(p ? p.col : n.col); U.uNodeA0.value = (p ? p.tint || 0 : 0) * gain;
      U.uNodeC.value.set(n.ring.o[0], n.ring.o[1]); U.uNodeR.value = ringR(n, t);
      U.uNodeFront.value = k >= 1 || n.ring.silent ? 0 : ss(seg(t, n.ring.t0, n.ring.t0 + .3)) * (1 - ss(seg(k, .75, 1))) * U.uProj.value * (1 - satOn);
    }
    for (const n of nodes) {   // the beam lands: a fast shock ring where it hits (the colour ring follows, or comes once the camera has turned to the city)
      if (!n.ring.impact) continue;
      const [ts, sx, sz, sr] = n.ring.shock || [n.ring.t0, n.ring.o[0], n.ring.o[1], n.ring.curve[n.ring.curve.length - 1][1]], u = t - ts, k = u / 1.6;
      if (k >= 0 && k < 1) { U.uShockA.value = (1 - k) ** 1.5 * U.uProj.value; U.uShockR.value = sr * (1 - (1 - k) ** 2.2); U.uShockC.value.set(sx, sz); }   // 1.6 s, easing out to about the landing shot's width: the blast is seen spreading
    }
    // a reset node: inside its ring today's buildings newer than `reset` go back down (they grow again with the year counter)
    const ri = nodes.findIndex(n => n.reset != null);
    if (ri >= 0 && t >= ringT0(nodes[ri])) { const n = nodes[ri]; U.uResetY.value = n.reset; U.uResetC.value.set(n.ring.o[0], n.ring.o[1]); U.uResetR.value = ringR(n, t); }
    else { U.uResetY.value = 0; U.uResetR.value = -1; }
  }
  // period cities: each building rises at its own start (compile: stages, settle); the stage's front is lit as a ring, a line
  // or a band scanning inside the outline; a ring takes the city back (fallR: contracting from its edge, or the next node's
  // colour ring), each building going within fallDur of the ring passing it. While a city changes only the rings glow; once
  // it stands, a thin edge line.
  let eraUp = 0;
  const nodes_ = FILM.nodes || []; let ci = -1; for (let i = 0; i < nodes_.length; i++) if (t >= ringT0(nodes_[i])) ci = i;
  for (const e of SHARE) if (e.occupy.some(([a, b]) => t >= a && t < b)) takeChannel(e);   // the city in use takes its shared channel
  for (const e of FILM.eras || []) {
    const E = S.eras[e.id]; if (!E) continue;
    const tE = t - e.on, full = e.span + e.grow, SD = e.fallDur || 1.4, FR = e.fallR, fin = FR && FR.mode === 'in';
    const fo = FR ? FR.o : [0, 0];
    const fr = FR ? curveAt(FR.curve, t) : (fin ? 1e3 : -1), fr1 = FR ? curveAt(FR.curve, t - SD) : fr;
    const gone = FR != null && t > FR.gone;
    E.mesh.visible = tE > -.01 && !gone;
    eraShape(e, t);
    E.u.uEraFallR.value = fr; E.u.uEraFallIn.value = fin ? 1 : 0; E.u.uEraFallW.value = fr1; E.u.uEraO.value.set(fo[0], fo[1]);
    E.u.uEraA.value = Math.max(e.tint, later(e, nodes_[ci]) ? (nodes_[ci].era_tint ?? nodes_[ci].tint) : 0) * (1 - .5 * today);   // a later node recolours at its own strength
    const burn = e.sinkStyle === 'burn' && e.off != null ? ss(seg(t, e.off - e.burn, e.off - e.burn * .55)) : 0;   // the city catches fire, then falls
    const up = upAt(e, t);
    E.u.uEraBurn.value = burn; E.u.uEraGlow.value = up * (LOOK.glow ?? 1);
    eraUp = Math.max(eraUp, up);
    E.u.uEraCol.value.copy(eraTint(e, nodes_[ci])); E.u.uEraCol0.value.copy(ci > 0 ? eraTint(e, nodes_[ci - 1]) : E.base);
    E.u.uEraInk.value = eraInk(e, nodes_[ci]); E.u.uEraInk0.value = ci > 0 ? eraInk(e, nodes_[ci - 1]) : eraInk(e, null);
    const offStart = !FR ? Infinity : e.sinkStyle === 'burn' ? e.off - e.burn : FR.hit;
    const scf = (e.fronts || []).find(f => f.mode === 'scan'), sc0 = scf ? scf.curve[0][0] : 0;
    const draw = scf ? eo(seg(t, sc0, sc0 + Math.max(1.4, .5 * (scf.curve[1][0] - sc0)))) : 1;   // a small place: the outline draws itself as it is scanned
    const edgeA = gone ? 0 : (scf ? ss(seg(t, sc0, sc0 + .3)) : ss(seg(t, e.on + full, e.on + full + 1.2)) * (1 - U.uNodeFront.value)) * (1 - ss(seg(t, offStart - .4, offStart))) * (1 - satOn);
    // a city long gone, drawn again as its outline (and the light along it on the ground) while a later node tells what stands
    // on it now (node `ghost`)
    let gA = 0, gD = 1;
    for (const n of nodes_) if ((n.ghost || []).includes(e.id)) { const a = OV.env(t, n.arrive, n.t1, .6, .8); if (a > gA) { gA = a; gD = eo(seg(t, n.arrive, n.arrive + 2.2)); } }
    if (e.hide != null && inChannel(e)) {
      const h = e.hide;
      U.uHideT.value[h] = tE < -.01 || gone ? -1 : tE / e.span; U.uHideG.value[h] = e.grow / e.span;
      U.uHideO.value[h].set(fo[0], fo[1]); U.uHideFR.value[h] = fr; U.uHideFI.value[h] = fin ? 1 : 0; U.uHideFW.value[h] = fr1;
      U.uHideFA.value[h] = FR && fin && t >= FR.hit && !gone ? ss(seg(t, FR.hit, FR.hit + .4)) * (1 - ss(seg(t, FR.gone - .5, FR.gone))) : 0;
      U.uHideCol.value[h].copy(gA > edgeA ? S.eras[e.id].base : E.u.uEraCol.value);
      U.uEdgeA.value[h] = Math.max(edgeA * ss(seg(draw, .85, 1)), gA * .9 * ss(seg(gD, .6, 1)));   // the light on the ground once the line has closed
      let F_ = null, fa = 0;   // the stage growing now: its front, faded in and out
      for (const q of e.fronts || []) { const a = ss(seg(t, q.a[0], q.a[0] + .4)) * (1 - ss(seg(t, q.a[1], q.a[1] + .4))); if (a > fa) { fa = a; F_ = q; } }
      U.uRiseA.value[h] = gone ? 0 : fa;
      if (F_) { U.uRiseR.value[h] = curveAt(F_.curve, t); U.uRiseO.value[h].set(F_.o[0], F_.o[1]); U.uRiseDir.value[h].set(...(F_.dir || [0, 0]));
        U.uRiseMode.value[h] = F_.mode === 'ring' ? 0 : F_.mode === 'line' ? 1 : 2; U.uRiseW.value[h] = F_.w || 0; }
    }
    if (S.edges[e.id]) S.edges[e.id].set(Math.max(edgeA, gA * .8) * (LOOK.line ?? 1) * (1 - (LV ? LV.k : 0)), gA > edgeA ? S.eras[e.id].base : E.u.uEraCol.value, gA > edgeA ? gD : draw);
    if (S.fires[e.id]) S.fires[e.id].set(burn * (gone ? 0 : 1) * U.uProj.value, t, fin ? fr : 1e3, fo);
  }
  // today's city steps back while a period city is told; the change travels with the node's ring: outside it, the level from
  // just before the ring started (docs/STAGING.md 1: a ring shows what changes inside it)
  U.uDimToday.value = dimAt(t, eraUp) * (1 - today);
  U.uDimToday0.value = ci >= 0 ? dimBefore(nodes_[ci]) * (1 - today) : U.uDimToday.value;
  for (const r of FILM.routes || []) { const R = S.routes[r.id]; const land = r.on + r.draw;   // a landing beam flashes where it lands
    if (R) R.set(ss(seg(t, r.on, r.on + r.draw)), ss(seg(t, r.on, r.on + .3)) * (1 - ss(seg(t, r.off - .6, r.off))) * (1 - (LV ? LV.k : 0)), r.impact && t >= land ? Math.exp(-(t - land) / .35) : 0); }
  const NT = FILM.night && FILM.night.length ? track(FILM.night)(t)[0] : 0; U.uNight.value = NT;
  S.setContext(CTXK ? Math.max(0, Math.min(1, CTXK(t)[0])) : 0);
  if (TK) { const [x, y, z, ry, sc, split, glow, vis] = TK(t); S.tally.visible = vis > .5; S.tally.position.set(x, y, z); S.tally.rotation.y = THREE.MathUtils.degToRad(ry); S.tally.scale.setScalar(sc); S.tally.setState(split, glow); S.tally.setLight(sc * sc * (vis > .5 ? 1 : 0)); }
  else S.tally.visible = false;
  let pk = 0;
  for (const p of FILM.pick || []) {
    const a = epochAlpha(t, p); if (a > pk) { pk = a; U.uPickPos.value.set(p.pos[0], p.pos[1]); U.uPickR.value = p.r || .02; }
  }
  U.uPickOn.value = pk;
}
const hgtFront = t => FILM.height ? U.uHgtF.value : 0;

// ------------------------------------------------------------------ overlay
const cueAt = t => (FILM.cues || []).find(c => t >= c.t0 && t < c.t1);
function drawOverlay(t) {
  OV.begin();
  const { g } = OV;
  const skyA = FILM.sky ? OV.sky(sceneAt(t), FILM.sky, proj3) : 0;   // under everything else on the overlay (part of the city: the prologue's moment)
  let fa = LV ? LV.k : 0, ffull = fa, fcorner = 0;   // how much of the frame real footage (or a living moment's picture) covers (full mode hides the map, the other modes only quiet it); fcorner: a panel or a right-hand document over the locator's corner
  for (const f of FILM.footage || []) {
    if (t < f.on - .01 || t > f.on + f.dur + .01) continue;
    const e = { in: seg(t, f.on, f.on + f.fin), out: seg(t, f.on + f.dur - f.fout, f.on + f.dur), k: seg(t, f.on, f.on + f.dur) };
    const anc = f.anchor ? proj3(f.anchor[0], f.anchor[2], f.anchor[1]) : null;
    OV.footage(VID[f.id], e, f, anc);
    const v = ss(e.in) * (1 - ss(e.out)); fa = Math.max(fa, (f.mode || 'full') === 'full' ? v : .6 * v); if ((f.mode || 'full') === 'full') ffull = Math.max(ffull, v);
    if (f.mode === 'panel' || (f.mode === 'doc' && f.side !== 'left')) fcorner = Math.max(fcorner, v);
  }
  for (const r of FILM.routes || []) {
    if (!r.a) continue;
    const a = ss(seg(t, r.on + r.draw * .55, r.on + r.draw * .55 + .5)) * (1 - ss(seg(t, r.off - .6, r.off))) * (1 - fa);
    if (a > 0) OV.routeLabel(proj3(r.lab[0], r.lab[2], r.lab[1]), a, r.a, r.b, r.col);
  }
  // geography labels on wide shots
  for (const L of FILM.labels || []) {
    const kept = (L.keep || []).some(([k0, k1]) => t >= k0 - .3 && t <= k1 + .3);   // the place the camera is going to or showing
    const a = (L.dmin > 0 && !kept ? ss(seg(camDist, L.dmin, L.dmin + .3)) : 1) * (1 - fa) * (1 - skyA) * ss(seg(t, Math.max(LT.lamp + 1, L.t0), Math.max(LT.lamp + 2.5, L.t0 + 1.2))) * (1 - ss(seg(t, Math.min(LT.lights - .5, L.t1 - 1), Math.min(LT.lights, L.t1))));
    const lay = (L.lay || []).find(q => t >= q[0] - .5 && t <= q[1] + .5);
    if (a > 0) OV.placeLabel(proj3(L.pos[0], L.pos[2] + .004, L.pos[1]), a, L.a, L.b, lay ? [lay[2], lay[3]] : null);
  }
  // locator: plate in miniature, era footprint, camera footprint
  {
    const node = (FILM.nodes || []).find(nd => t >= nd.t0 && t < nd.t1);
    const era = node && (FILM.eras || []).find(e => e.id === node.id);
    const quad = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([x, y]) => { const v = new THREE.Vector3(x, y, .5).unproject(camera), d = v.sub(camera.position); if (d.y > -1e-4) return null; const k = -camera.position.y / d.y; return [(camera.position.x + d.x * k) / S.PW + .5, (camera.position.z + d.z * k) / S.PD + .5]; });
    const ok = quad.every(Boolean) && camDist < 1.6;
    const secOn = (FILM.sections || []).some(sc => t > sc.t0 - .3 && t < sc.t1 + .3);   // the terrain profile panel takes the same corner
    const la = (1 - fa) * (1 - fcorner) * (1 - skyA) * (secOn ? 0 : 1) * ss(seg(t, LT.lamp + 1.5, LT.lamp + 3)) * (1 - ss(seg(t, LT.lights - .5, LT.lights)));
    OV.locator(LOC, la, era ? era.outline : null, era ? era.col : '#ffffff', node ? node.label : '', ok ? quad.map(([u, v]) => [Math.max(0, Math.min(1, u)), Math.max(0, Math.min(1, v))]) : null);
  }
  if (LV && LIVETEX[LV.L.id]) OV.caption(LV.L, 96, 170, LV.sky * LV.pa);   // the living moment's label: AI-generated reconstruction, from the sources
  const left = Math.max(...(FILM.readouts || []).map(r => OV.env(t, r.t0 - .3, r.t1 + .2)), 0);
  OV.scrims(left, 1);
  OV.identity(t, (PRO ? PRO.dur : 0) + .3, FILM.end.t - .2, FILM.identity.l1, FILM.identity.l2);   // (not over the prologue)
  if (FILM.bar) {
    const node = (FILM.nodes || []).find(nd => t >= nd.t0 && t < nd.t1) || null;
    const ba = Math.min(ss(seg(t, LT.lamp + .4, LT.lamp + 1.4)), 1 - ss(seg(t, LT.lights - .2, LT.lights + .6)));
    OV.timelineBar(t, FILM.bar, fmtYear(yearAt(t)), node ? node.label : '', ba);
  }

  for (const sc of FILM.sections || []) {
    const a = OV.env(t, sc.t0, sc.t1, .5, .4); if (a <= 0) continue;
    if (!sc.profile) {   // sample once: relief in model units -> metres above the box minimum, plus the DEM minimum
      const n = 120, ex = (M.terrain && M.terrain.exaggeration) || 3, mn = (M.terrain && M.terrain.min_m) || 0;
      sc.profile = Array.from({ length: n }, (_, i) => { const k = i / (n - 1); return mn + S.ground(sc.a[0] + (sc.b[0] - sc.a[0]) * k, sc.a[1] + (sc.b[1] - sc.a[1]) * k) / M.scale / ex; });
      sc.lo = Math.min(...sc.profile) - 8; sc.hi = Math.max(...sc.profile) + 12;
    }
    OV.section(t, sc, a);
    // the cut line on the model
    const pts = Array.from({ length: 40 }, (_, i) => { const k = i / 39, x = sc.a[0] + (sc.b[0] - sc.a[0]) * k, z = sc.a[1] + (sc.b[1] - sc.a[1]) * k; return proj3(x, S.ground(x, z) + .004, z); });
    if (pts.every(Boolean)) { g.save(); g.globalAlpha = a * .9; g.strokeStyle = '#ffe3b0'; g.lineWidth = 1.5; g.setLineDash([6, 6]); g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.stroke(); g.restore(); }
  }
  for (const r of FILM.readouts || []) {
    const o = { ...r };
    if (!FILM.bar) {}
    if (r.big && typeof r.big === 'object' && r.big.year) { o.big = fmtYear(yearAt(t)); o.live = true; o.bigPx = 112; }
    if (r.legendBands) o.legend = FILM.bands.map((b, i) => ({ col: FILM.palette.bands[i], text: b.label, text2: `${b.n.toLocaleString('en-US')} ${r.legendBands.unit || ''}`, t0: (FILM.grow.bands.find(q => q.band === i) || {}).t }));
    OV.readout(t, o);
  }
  if (FILM.height && t > FILM.height.t0 && (FILM.height.off == null || t < FILM.height.off)) {   // the level's reading rides up the tallest building
    const Hh = FILM.height, h = Math.min(hgtFront(t), Hh.top), a = Math.min(seg(t, Hh.t0, Hh.t0 + .3), 1 - ss(seg(t, Hh.t1 + .2, Hh.t1 + .5)));
    const q = proj3(Hh.topPos[0], h, Hh.topPos[1]);
    if (q) { OV.txt(null, `${Math.round(h / M.scale)} m`, q[0] + 26, q[1] + 7, 'en_strong', 24, '#ffffff', a, { shadow: 10 }); g.save(); g.globalAlpha = a; g.fillStyle = '#fff'; g.fillRect(q[0] + 8, q[1] - 1, 12, 2); g.restore(); }
  }
  if (FILM.grow && FILM.grow.counters && FILM.change) {   // new and taller buildings so far (cumulative, by the year counter)
    const C = FILM.grow.counters, cs = FILM.change.counts, Y = yearAt(t), i = Math.max(0, Math.min(cs.length - 2, Math.floor(Y - cs[0][0]))), f = Math.max(0, Math.min(1, Y - cs[i][0]));
    const rdy = Math.max(0, ...(FILM.readouts || []).map(q => ((q.legend ? q.legend.length * 32 : 0) + (q.bar ? 50 : 0) + OV.noteDrop(q.note)) * OV.env(t, q.t0 - .6, q.t1 + .6, .6, .6)));   // (eased: no jump)
    OV.counters(t, C, [1, 2].map(j => cs[i][j] + (cs[i + 1][j] - cs[i][j]) * f), OV.env(t, C.t0, C.t1, .6, .6) * (1 - fa), rdy);
  }
  if (ffull < .99) for (const p of FILM.pins || []) OV.pin(t, at([p.pos[0], p.pos[1], (p.pos[2] || 0) + .002]), p, 1 - ffull);   // (no pins over a full-screen clip)
  for (const m of FILM.marks || []) OV.mark(t, at([m.pos[0], m.pos[1], (m.pos[2] || 0) + .001]), m);
  for (const r of FILM.ranges || []) {
    const pts = r.pts.map(([x, z]) => proj3(x, .0015, z));
    if (pts.every(Boolean)) {
      const tip = OV.rangeLine(t, r.t0, r.t1, r.tOut, pts, r);
      if (tip && t < r.t1 + .05 && r.len_m) OV.txt(null, `${Math.round(r.len_m * eo(seg(t, r.t0, r.t1)))} m`, tip[0] + 16, tip[1] - 12, 'en_strong', 26, '#ffffff', 1, { shadow: 10 });
    }
  }
  OV.subtitle(t, cueAt(t));
  OV.endCard(t, FILM.end);
  if (PRO) {   // the prologue's closing black, and the opening coming up out of it
    const k = ss(seg(t, PRO.dur - PRO.fade, PRO.dur)) * (1 - ss(seg(t, PRO.dur, PRO.dur + .5)));
    if (k > 0) { g.save(); g.globalAlpha = k; g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.restore(); }
  }
}

// ------------------------------------------------------------------ events for the mix (window.EV) and checks
const EV = [];
const ev = (t, type, o = {}) => { if (t != null && t >= 0 && t <= DUR) EV.push({ t: +t.toFixed(4), type, ...o }); };
ev(LT.lightsOut, 'relay'); ev(LT.lamp, 'lamp'); ev(LT.lights, 'lights'); ev(FILM.end.t, 'end');
for (const [a, b] of LT.darks || []) { ev(a, 'dark', { dur: b - a }); ev(b, 'undark'); }
for (const e of FILM.epochs || []) { ev(e.on, 'wash', { id: e.id, dur: e.fade ?? 1.2 }); if (e.off != null) ev(e.off, e.offStyle === 'burn' ? 'burn' : 'fadeout', { id: e.id, dur: e.offDur ?? 1.2 }); }
for (const L of FILM.lines || []) ev(L.on, 'line', { id: L.id, dur: L.fade ?? 1 });
if (FILM.grow) for (const b of FILM.grow.bands) {
  ev(b.t, 'layer', { band: b.band });
  const lo = FILM.bands[b.band].lo, hi = FILM.bands[b.band].hi;
  const on = M.b.map(([y], i) => [y, i]).filter(([y]) => y >= lo && y < hi)
    .map(([, i]) => { const x = Math.sin((i * 1.37 + .5) * 127.1 + 311.7) * 43758.5453; return b.t + (x - Math.floor(x)) * b.spread; }).sort((p, q) => p - q);
  const n = Math.min(22, on.length);
  for (let k = 0; k < n; k++) ev(on[Math.floor((k + .5) * on.length / n)], 'pop', { band: b.band });
}
if (FILM.height) { ev(FILM.height.t0, 'climb', { dur: FILM.height.t1 - FILM.height.t0 }); ev(FILM.height.t1, 'top'); }
for (const p of FILM.pins || []) ev(p.t0, 'pin', { id: p.id });
for (const m of FILM.marks || []) ev(m.t0, 'mark', { id: m.id, k: m.k });
for (const p of FILM.pick || []) ev(p.on, 'pick', { id: p.id });
for (const r of FILM.ranges || []) { ev(r.t0, 'rangeline', { dur: r.t1 - r.t0 }); ev(r.t1, 'lineEnd'); }
for (const c of FILM.cues || []) ev(c.t0, 'cue', { id: c.id });
for (const d of FILM.decals || []) ev(d.on, 'decal', { id: d.id, dur: d.fade ?? 1.5 });
for (const p of FILM.props || []) { ev(p.on, 'prop', { id: p.id, kind: p.kind, dur: p.fade ?? 1.5 }); if (p.off != null) ev(p.off, p.offStyle === 'burn' ? 'burn' : 'prop_off', { id: p.id, dur: p.offDur ?? 1.2 }); }
for (const e of FILM.eras || []) { ev(e.on, 'wash', { id: 'era_' + e.id, dur: Math.min(3, e.rise) }); if (e.off != null) ev(e.sinkStyle === 'burn' ? e.off - e.burn : e.off, e.sinkStyle === 'burn' ? 'burn' : 'fadeout', { id: 'era_' + e.id, dur: e.sinkStyle === 'burn' ? e.burn : e.sink }); }
if (FILM.satellite) ev(FILM.satellite.on, 'satellite', { dur: FILM.satellite.fade ?? 2 });
for (const f of FILM.footage || []) { ev(f.on, 'footage', { id: f.id, dur: f.dur }); ev(f.on + f.dur, 'footage_end', { id: f.id }); }
for (const e of FILM.ev || []) ev(e.t, e.type, e);
EV.sort((a, b) => a.t - b.t);
window.EV = EV;

// ------------------------------------------------------------------ render
// live preview playing (?play): videos play natively and are only nudged when they drift; while a full-screen clip covers the
// frame the 3D scene is not drawn. Stills, scrubbing and the offline render seek every frame exactly (deterministic).
let PLAYING = false;
const fullCover = t => (FILM.footage || []).some(f => (f.mode || 'full') === 'full' && t >= f.on + f.fin && t <= f.on + f.dur - f.fout);
const renderSync = t => { const s = sceneAt(t); LV = liveAt(t); setCamera(t); setLight(s); setLayers(s); setLiving(t); if (!(PLAY && PLAYING && fullCover(t))) { renderer.shadowMap.needsUpdate = true; post.composer.render(); } if (!QS.has('clean')) drawOverlay(t); else OV.begin(); };   // clean: the model alone (tools/living.py's reference)
window.render = (FILM.footage || []).length ? async t => {
  for (const f of FILM.footage) {
    const v = VID[f.id]; if (!(v instanceof HTMLVideoElement)) continue;
    const target = Math.max(0, Math.min(v.duration - .05, f.start + t - f.on));
    if (PLAY && PLAYING) {
      if (t < f.on - 2 || t > f.on + f.dur + .5) { if (!v.paused) v.pause(); v.__pre = null; continue; }
      if (t < f.on) { if (!v.paused) v.pause(); if (v.__pre !== f.id && !v.seeking) { v.__pre = f.id; v.currentTime = f.start; } continue; }   // pre-roll once: the first frame decoded before the cut
      if (v.paused) { if (Math.abs(v.currentTime - target) > .1) v.currentTime = target; v.play().catch(() => {}); }
      else if (!v.seeking) {   // keep in step by speed only: a seek while playing stalls the decoder (a slow machine falls behind, never stutters)
        v.playbackRate = Math.max(.75, Math.min(1.35, 1 + (target - v.currentTime) * .8));
      }
    } else {
      if (!v.paused) v.pause();
      if (t >= f.on - .5 && t <= f.on + f.dur + .5) await seekTo(v, target);
    }
  }
  renderSync(t);
} : renderSync;
window.TEXTS = async t => { await window.render(t); return OV.texts(); };
window.DRAWN = () => OV.drawn();   // every text of the frame TEXTS last drew (tools/readcheck.mjs: texts over texts)
// tools/camcheck.mjs: the camera at time t without drawing (position, target, near plane, distance)
window.CAMAT = t => { setCamera(t); return { p: camera.position.toArray(), tg: tgt.toArray(), near: camera.near, d: camDist, fov: camera.fov }; };

// the film's fonts (FILM.fonts: the faces compile found in fonts/ for each job), all loaded before the first frame
for (const f of FILM.fonts.faces) document.fonts.add(await new FontFace(f.alias, await (await L.take(f.file)).arrayBuffer(), { weight: f.weight }).load());
await document.fonts.ready;
await Promise.all(Object.values(FILM.fonts.roles).map(r => document.fonts.load(r.replace('{}', 20), '城0')));
setFonts(FILM.fonts.roles); setUI(FILM.ui, FILM.sub);
{   // single-line subtitle check with the real fonts (tools/subcheck.mjs reads this)
  const c = document.createElement('canvas').getContext('2d'), m = (s, k) => { if (!s) return 0; c.font = font(...SUB[k]); return Math.ceil(c.measureText(s).width); };
  const cues = (FILM.cues || []).map(q => { const wa = m(q.a, 'a'), wb = m(q.b, 'b'); return { id: q.id, a: q.a, b: q.b, wa, wb, ok: wa <= SUB.safe && wb <= SUB.safe }; });
  window.SUBCHECK = { safe: SUB.safe, cues, ok: cues.every(q => q.ok) };
}
window.render(QS.has('t') ? +QS.get('t') : 0);
// warm-up: draw every era city once so its buffers and programs are on the GPU before playback (else the first frame it appears stalls)
{
  const keep = Object.values(S.eras).map(E => [E, E.mesh.visible, E.u.uEraT.value, E.u.uEraFallR.value]);
  for (const [E] of keep) { E.mesh.visible = true; E.u.uEraT.value = 1e6; E.u.uEraFallR.value = E.u.uEraFallIn.value > .5 ? 1e3 : -1; }
  S.renderer.render(S.scene, S.camera);
  for (const [E, v, r, f] of keep) { E.mesh.visible = v; E.u.uEraT.value = r; E.u.uEraFallR.value = f; }
}
// the period cities' viewer (?view, engine/view.js): this scene and light without the timeline, the camera the viewer's
if (QS.has('view')) {
  document.getElementById('ov').style.display = 'none';
  (await import('./view.js')).startView({ S, FILM, QS, W, H, scale: M.scale, setLight, setLayers, eraShape, lens, cityMesh: CITYMESH, eraBox: ERABOX, takeChannel,
    setDist: (d, el) => { camDist = d; camElev = el; },
    quiet: () => {   // what setLayers lays at a moment of the film that is not the period cities: off
      for (let i = 0; i < EMAX; i++) U.uEpA.value[i] = 0;
      for (let i = 0; i < 4; i++) U.uDA.value[i] = 0;
      for (let i = 0; i < 8; i++) { U.uRiseA.value[i] = 0; U.uHideFA.value[i] = 0; U.uEdgeA.value[i] = 0; U.uHideT.value[i] = -1; U.uHideFR.value[i] = -1; U.uHideFI.value[i] = 0; U.uHideFW.value[i] = -1; }
      U.uPhotoA.value = 0; U.uRingN.value = 0; U.uPulse.value = 0; U.uShockA.value = 0; U.uNodeFront.value = 0; U.uNodeR.value = 99;
      U.uNodeA.value = U.uNodeA0.value = 0; U.uPickOn.value = 0; U.uHgtOn.value = 0; U.uResetR.value = -1; U.uResetY.value = 0;
      for (const k in lineA) lineA[k].value = 0;
      for (const r of Object.values(S.routes)) r.set(0, 0);
      S.tally.visible = false;
    } });
}
window.READY = true;
if (!PLAY) L.done();

// ------------------------------------------------------------------ live preview: ?play=1 (a transport bar; space = play/pause, arrows = step, M = narration on/off, B = music on/off, N = sound effects on/off)
if (PLAY) {
  const bar = document.createElement('div');
  bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;height:56px;background:rgba(10,11,14,.92);color:#e8ecf2;font:14px/1.4 IBM Plex Mono,monospace;display:flex;align-items:center;gap:14px;padding:0 16px;z-index:9;user-select:none';
  bar.innerHTML = `<button id="pp" style="width:56px;height:30px;background:#1e222a;color:#fff;border:1px solid #444;border-radius:4px;cursor:pointer">▶</button>
    <span id="tm" style="min-width:150px"></span><input id="sc" type="range" min="0" max="${DUR}" step="0.02" value="0" style="flex:1">
    <span id="yr" style="min-width:90px;text-align:right"></span><span id="fps" style="min-width:60px;text-align:right;opacity:.6"></span>
    <a href="${REPO}" target="_blank" rel="noopener" style="color:#c9d2de;text-decoration:none;white-space:nowrap">一城春秋 · A City Through Time</a>`;   // (LICENSE, condition 2c)
  document.body.appendChild(bar);
  // fit the 1920x1080 picture above the bar, whatever the window size
  const fit = () => { const k = Math.min(innerWidth / W, (innerHeight - 56) / H); for (const id of ['stage', 'ov']) { const el = document.getElementById(id); el.style.transformOrigin = 'top left'; el.style.transform = `scale(${k})`; } };
  fit(); window.addEventListener('resize', fit);
  const sc = bar.querySelector('#sc'), pp = bar.querySelector('#pp'), tm = bar.querySelector('#tm'), yr = bar.querySelector('#yr'), fpsEl = bar.querySelector('#fps');
  // markers under the scrubber: every cue and the light events
  const marks = document.createElement('div'); marks.style.cssText = 'position:fixed;bottom:50px;height:6px;pointer-events:none;z-index:9';
  const under = () => { const r = sc.getBoundingClientRect(); marks.style.left = r.left + 'px'; marks.style.width = r.width + 'px'; };   // (the scrubber's own span, whatever else the bar holds)
  for (const c of FILM.cues || []) { const m = document.createElement('i'); m.style.cssText = `position:absolute;left:${c.t0 / DUR * 100}%;width:2px;height:6px;background:#ffd27a`; marks.appendChild(m); }
  for (const t of [LT.lightsOut, LT.lamp, LT.lights, FILM.end.t]) { const m = document.createElement('i'); m.style.cssText = `position:absolute;left:${t / DUR * 100}%;width:2px;height:6px;background:#6fdcff`; marks.appendChild(m); }
  document.body.appendChild(marks); under(); window.addEventListener('resize', under);
  let cur = QS.has('t') ? +QS.get('t') : 0, playing = false, t0 = 0, c0 = 0, frames = 0, ft = performance.now();
  const show = () => { sc.value = cur; tm.textContent = `${cur.toFixed(2)} s / ${DUR}`; yr.textContent = fmtYear(yearAt(cur)); };
  // the narration and the score (compile: film.voice, every voiced line laid at its time; film.score, the music laid by node and
  // dipped under the voice): each loaded whole (the preview server answers no range requests: seeking in a file still loading cut
  // the start of lines and clicked), heard while playing, kept in step by speed within half a second (a seek while playing drops
  // sound), seeked only past that; silent when paused, scrubbed or stepped. M mutes the narration, B the music, N the sound effects
  // (film.sfx: the few the mix keeps)
  const tracks = [], sound = [];
  for (const [f, key] of [[SOUND[0], 'KeyM'], [SOUND[1], 'KeyB'], [SOUND[2], 'KeyN']])
    if (f) sound.push(L.take(f, { optional: true }).then(b => { if (b) { tracks.push({ a: Object.assign(new Audio(URL.createObjectURL(b)), { preload: 'auto' }), key }); voSync(); } }));
  // after the film (film.score.loop): the end card stays and one cue plays on in a loop, rising over 3 s, until the viewer plays,
  // scrubs or steps again (a viewer of the web version may stay on the end card); B mutes it with the music
  let after = null, afterRise = 0;
  if (SOUND[3]) sound.push(L.take(SOUND[3], { optional: true }).then(b => { if (b) after = Object.assign(new Audio(URL.createObjectURL(b)), { loop: true, preload: 'auto' }); }));
  Promise.allSettled(sound).then(L.done);   // the picture and the sound are in: the loading screen goes
  const afterOn = on => {
    if (!after) return;
    clearInterval(afterRise);
    if (!on) { after.pause(); return; }
    after.currentTime = 0; after.volume = 0; after.muted = tracks.some(t => t.key === 'KeyB' && t.a.muted); after.play().catch(() => {});
    afterRise = setInterval(() => { after.volume = Math.min(1, after.volume + .05); if (after.volume >= 1) clearInterval(afterRise); }, 150);
  };
  const voSync = () => {
    for (const { a: vo } of tracks) {
      if (!playing) { if (!vo.paused) vo.pause(); vo.playbackRate = 1; continue; }
      const drift = vo.currentTime - cur;
      if (vo.paused || Math.abs(drift) > .5) { vo.currentTime = cur; vo.playbackRate = 1; }
      else vo.playbackRate = Math.min(1.04, Math.max(.96, 1 - drift));
      if (vo.paused && cur < vo.duration - .05) vo.play().catch(() => {});
    }
  };
  const draw = () => { window.render(cur); show(); voSync(); };
  let busy = false;   // one frame at a time: a new frame starts only when the last one is drawn (no pile-up of video seeks)
  const loop = () => {
    if (!playing) return;
    cur = Math.min(DUR, c0 + (performance.now() - t0) / 1000);
    if (!busy) { busy = true; Promise.resolve(window.render(cur)).finally(() => { busy = false; }); show(); }
    if (++frames % 12 === 0) { const n = performance.now(); fpsEl.textContent = `${(12000 / (n - ft)).toFixed(0)} fps`; ft = n; voSync(); }
    if (cur >= DUR) { playing = PLAYING = false; pp.textContent = '▶'; voSync(); afterOn(true); return; }
    requestAnimationFrame(loop);
  };
  const toggle = () => { afterOn(false); playing = !playing; PLAYING = playing; pp.textContent = playing ? '❚❚' : '▶'; if (playing) { if (cur >= DUR) cur = 0; t0 = performance.now(); c0 = cur; voSync(); requestAnimationFrame(loop); } else draw(); };
  pp.onclick = toggle;
  sc.oninput = () => { afterOn(false); playing = PLAYING = false; pp.textContent = '▶'; cur = +sc.value; draw(); };
  window.addEventListener('keydown', e => {
    if (e.code === 'Space') { e.preventDefault(); toggle(); }
    for (const t of tracks) if (e.code === t.key) { t.a.muted = !t.a.muted; if (t.key === 'KeyB' && after) after.muted = t.a.muted; }
    if (e.code === 'ArrowRight' || e.code === 'ArrowLeft') afterOn(false);
    if (e.code === 'ArrowRight') { playing = PLAYING = false; pp.textContent = '▶'; cur = Math.min(DUR, cur + (e.shiftKey ? 5 : 1 / 24)); draw(); }
    if (e.code === 'ArrowLeft') { playing = PLAYING = false; pp.textContent = '▶'; cur = Math.max(0, cur - (e.shiftKey ? 5 : 1 / 24)); draw(); }
  });
  draw();
}
