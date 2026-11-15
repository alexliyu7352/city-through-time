// The colour look, a second engine beside the white-model one: the coloured miniature, drawn in the period cities' viewer
// (play.html?city=<slug>&view&look=mini; &palette=roman|chinese|modern, &ground=land|modern, &card=<year>|<period>|<population>: the
// info on screen; &detail=0: without engine/detail.js's pieces). It leaves the studio's own scene and materials as they are and
// draws the same geometry its own way: daylight from a sun and the sky, each building in its own wall and roof colours, its
// windows, doors, cornices, posts, rows of tiles and copings, the city wall's courses, gates and flags, the town's trees, boats on
// the river (engine/detail.js, from the period city's records and the water; off on a touch screen), trees in the open land and the
// gardens (none against a city wall or in a gate's approach), fields and water, a landmark's detailed model
// (tools/blender) in place of the generator's, a hazy sky and a tilt-shift blur (sharp in a band across the middle, as a
// photograph of a model).
// Nothing of the film is changed: the studio draws with layer 0, this look with layer 1 alone.
// The film in this look (film.look, engine/main.js; film: true): the same colours drawn with the studio's own deformation
// (studio.js deformMaterial), so each period city rises at its station, falls and loses parts as the white model's does, today's
// city grows by year and steps aside where a period city stands, and their shadows follow (the studio's depth materials kept); a
// burning building charred and glowing; the detail rising and falling with its building (detail.js o.rise); today's city a pale
// unpainted card outside its own story (filmMaterial); the sun from the bearing of the film's key light (it turns
// with the shot, not the drift); the film's lens and depth of field, its ambient occlusion from the picture's own depth.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { HorizontalTiltShiftShader } from 'three/addons/shaders/HorizontalTiltShiftShader.js';
import { VerticalTiltShiftShader } from 'three/addons/shaders/VerticalTiltShiftShader.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { makePost } from './post.js';
import { FX_SKY, RELIEF_GLSL, LAND_PALETTES, landLookGLSL, landPalette, woodsFn, treeField, makeSky, fxLens, fxAoRadius } from './fx.js';
import { eraDetail, detailMeshes, gableEnds, boatsAt, STYLES, FLAT } from './detail.js';

const L = 1;   // the layer this look draws
// with the effects: a bright day, as bright and as coloured as the look without them (the low warm sun, the haze and the occlusion
// had greyed it): the sun and the sky's light raised, the air thinner (its distance times haze), the occlusion lighter
const MINI_LIFT = { sun: 1.5, sky: 1.45, haze: 3.5, ao: .3 };
const FILM_AO = .45;   // (the film without the effects: the occlusion of its own passes)
// a close shot's heights (the colour film): walls scaled about their ground toward real heights, a roof lifted with them and its
// rise as drawn, detail and shadows the same; k at `near` (model units of camera distance) and none from `far` on
const HSCALE = { value: 1 };
// a light pool on a material's plate (FILM_PIC pool: [the darkness it falls to, the shot distance from which it is whole]): x z its
// centre (the shot's target), z its radius, w the darkness, set each frame
// a city's green space (pipeline/greens.py data/green.png) and its finer streets (data/streets.json), when it has them
const GREEN = { value: null }, GREEN_ON = { value: 0 }, STREETS = { list: null }; let GREEN_D = null;
let GREEN_P = null;
function greenData(dir) {   // -> a promise the first frame waits on (both optional: a city without them draws none)
  if (GREEN_P || !dir || typeof document === 'undefined') return GREEN_P; const z = new THREE.DataTexture(new Uint8Array(4), 1, 1); z.needsUpdate = true; GREEN.value = z;
  const g = new Promise(res => new THREE.TextureLoader().load(dir + 'green.png', t => { t.colorSpace = THREE.NoColorSpace; t.flipY = false; GREEN.value = t; GREEN_ON.value = 1; res(); }, undefined, () => res()));
  const st = fetch(dir + 'streets.json').then(r => r.ok ? r.json() : null).then(j => { STREETS.list = j && j.streets || []; }).catch(() => { STREETS.list = []; });
  return GREEN_P = Promise.all([g, st]);
}
let SKY_C0 = null, GLB_DONE = false;
const SUN_DIR = { value: new THREE.Vector3(0, 1, 0) }, SUN_COL = { value: new THREE.Color() };   // (the sun's direction and light, for the water's sparkle)
const ROOF_PX = { value: 1 };   // (the model's metres a picture pixel spans at unit depth: the rims' fade, roofsMesh)
const REFL = { T: { value: null }, M: { value: new THREE.Matrix4() }, K: { value: 0 }, D: { value: new THREE.Vector2(1e9, 2e9) } }, GLASS_SKY = { value: new THREE.Color(.80, .86, .92) }, GLASS_K = { value: 1 }, DOME_R = { value: 25 };   // (GLASS_K: how much of it; DOME_R: how fast the dome turns from its horizon to its zenith)   // (GLASS_SKY: the sky glass reflects, the dome's horizon: gold at the golden hour)   // (today's water's reflection: its picture, its texture matrix, on)
// a landmark's own round plaza (a glb entry's plaza, todayLight roundPlaza): up to four, P: its centre x z (model units), its lawn
// ring's inner and outer radius m; Q: its inner disc's radius, its outer radius m, -, on
const RPLAZA = { P: { value: [0, 1, 2, 3].map(() => new THREE.Vector4()) }, Q: { value: [0, 1, 2, 3].map(() => new THREE.Vector4()) } };
const HSCALE_T = { value: 1 }, POOL = { value: new THREE.Vector4(0, 0, 1e9, 1) }, GEO_T = { value: new THREE.Vector4(0, 0, -1, 0) };   // (GEO_T: where the crowns drawn as geometry hand over to the ground's groves' tone, x from and y whole at these distances from the eye; z < 0: none)
// the built area of the period cities standing (a material's ground_in: its plaster inside it, the table beyond): their buildings'
// centres drawn over the plate, each `reach` m round, softened; made again when the cities standing change (builtMask)
// today's city as the year each place is first built (a material's ground_in: its plaster from that year on), drawn once: every
// building's footprint `reach` m round on a 4096 map (YEAR_W, the built-up area, its streets inside it) and 3 m round (YEAR_T, the
// blocks: a street is built-up ground off them), the earliest year on top; a texel holds the year - 1899 (0: never built)
let ROOFS = null, BAND_IX = [];
// today's buildings' extents in a 50 m grid (todayYears): a tree stands clear of every wall (walls(x, z, r): none within r)
let WALLS = null;
const walls = (x, z, r) => { if (!WALLS) return true; const { g, c } = WALLS, i0 = Math.floor((x - r) / c), i1 = Math.floor((x + r) / c), j0 = Math.floor((z - r) / c), j1 = Math.floor((z + r) / c);
  for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) { const L_ = g.get(i * 100003 + j); if (L_) for (const [a, b, cc, d] of L_) if (x > a - r && x < cc + r && z > b - r && z < d + r) return false; }
  return true; };
const BAND_C = [{ value: null }, { value: null }], BAND_HI = { value: new Array(6).fill(1e5) }, BAND_Y = { value: 1e4 }, ROOF_ON = { value: 1 }, STREET_K = { value: 1 }, DETAIL_FADE = 1.5;   // (BAND_Y: the year the bands' plaster has reached: the growth's own when it is told, the year counter's otherwise; ROOF_ON: no roof pieces while the growth raises the city)   // (BAND_HI: the year each band is done, the shader's)
const LANES = { value: null }, YEAR_W = { value: null }, YEAR_T = { value: null }, YEAR_C = { value: null }, TODAY_K = { value: new THREE.Vector3(1e4, 0, 0) }; let YEAR_D = null, YEAR_E = null;   // (TODAY_K: the film's year, whether today's city stands: x year, y on)
// today's rooftops' records (roofsMesh): each building's outline's centre and own axes (the corners' spread, a rectangle's half
// sides), top, year, height, its aCtr's x (its hash), its vertices [i0, i1) and their positions (pieces stand on those from 8 m,
// a pitched roof on any). split: a new record also where walls follow a roof under one aCtr (a replacement footprint's children
// share their parent's: buildTodayFootprints)
function roofScan(g, split = false) {
  const P = g.attributes.position, C = g.attributes.aCtr, D = g.attributes.aData, N = g.attributes.normal, out = []; if (!C || !D) return out;
  let lx = 1e9, lz = 1e9, top = false, yr = 0, y1 = -1e9, hm = 0, n_ = 0, sx_ = 0, sz_ = 0, sxx_ = 0, szz_ = 0, sxz_ = 0, ri0_ = 0;
  for (let i = 0; i <= C.count; i++) { const x = i < C.count ? C.getX(i) : NaN, z = i < C.count ? C.getY(i) : NaN, up = i < C.count && N.getY(i) > .6;
    if (x !== lx || z !== lz || (split && top && !up)) { if (n_) {
        const mx = sx_ / n_, mz = sz_ / n_, cxx = sxx_ / n_ - mx * mx, czz = szz_ / n_ - mz * mz, cxz = sxz_ / n_ - mx * mz, th = .5 * Math.atan2(2 * cxz, cxx - czz);
        const c = Math.cos(th), sn = Math.sin(th), va = c * c * cxx + 2 * c * sn * cxz + sn * sn * czz, vb = sn * sn * cxx - 2 * c * sn * cxz + c * c * czz;
        out.push([mx, mz, th, Math.sqrt(Math.max(va, 0)), Math.sqrt(Math.max(vb, 0)), y1, yr, hm, lx, ri0_, i, P]); }
      lx = x; lz = z; y1 = -1e9; n_ = sx_ = sz_ = sxx_ = szz_ = sxz_ = 0; ri0_ = i; if (i < C.count) { yr = D.getX(i); hm = D.getY(i); } }
    top = up; if (i < C.count) { const px = P.getX(i), pz = P.getZ(i); if (P.getY(i) > y1) y1 = P.getY(i); n_++; sx_ += px; sz_ += pz; sxx_ += px * px; szz_ += pz * pz; sxz_ += px * pz; } }
  return out;
}
// each vertex's record's top as built (aTop: the highest point of its record, a record as roofScan splits them), so a facade
// finds its wall's top where a part stands taller than its building's recorded height
function recordTops(g) {
  const P = g.attributes.position, C = g.attributes.aCtr, N = g.attributes.normal, n = P.count, out = new Float32Array(n); if (!C) return out;
  let i0 = 0, top = false, y1 = -1e9;
  for (let i = 0; i <= n; i++) { const up = i < n && N.getY(i) > .6;
    if (i === n || (i > i0 && (C.getX(i) !== C.getX(i - 1) || C.getY(i) !== C.getY(i - 1) || (top && !up)))) { out.fill(y1, i0, i); i0 = i; y1 = -1e9; }
    if (i < n) { top = up; if (P.getY(i) > y1) y1 = P.getY(i); } }
  return out; }
// each wall vertex's distance along its wall to the wall's two ends (aEdge, in cm plus one, 65535: none), an end counted only at a
// convex corner the next wall turns sharply from (a block's corner, not a round tower's facets): ends ordered along the wall's
// tangent (-nz, nx), so a shader knows which way the corner lies (todayLight bevel: a rounded edge catching the light)
function wallEdges(g, scale) {
  const P = g.attributes.position, N = g.attributes.normal, n = P.count, out = new Uint16Array(n * 2).fill(65535), q = [];
  for (let i = 0; i < n;) { if (Math.abs(N.getY(i)) > .3 || i + 5 >= n) { i += 3; continue; }
    const ax = P.getX(i), az = P.getZ(i); let bx = P.getX(i + 1), bz = P.getZ(i + 1); if (bx === ax && bz === az) { bx = P.getX(i + 2); bz = P.getZ(i + 2); }
    q.push([i, ax, az, bx, bz, N.getX(i), N.getZ(i)]); i += 6; }
  const cv = new Uint8Array(q.length * 2);   // (a convex corner at its start a, its end b)
  const turn = (P_, N_) => { const dx = N_[3] - N_[1], dz = N_[4] - N_[2], l = Math.hypot(dx, dz) || 1; return (dx * P_[5] + dz * P_[6]) / l < -.42; };   // (the next wall bends in, more than 25 degrees)
  let r0 = 0;
  for (let k = 0; k < q.length; k++) { const A = q[k], B = q[k + 1], on = B && B[1] === A[3] && B[2] === A[4];
    if (on) { if (turn(A, B)) { cv[k * 2 + 1] = 1; cv[(k + 1) * 2] = 1; } }
    else { const F = q[r0]; if (F[1] === A[3] && F[2] === A[4] && turn(A, F)) { cv[k * 2 + 1] = 1; cv[r0 * 2] = 1; } r0 = k + 1; } }   // (a ring's last wall and its first)
  q.forEach(([i, ax, az, bx, bz, nx, nz], k) => { const L = Math.hypot(bx - ax, bz - az) / scale, fw = (bx - ax) * -nz + (bz - az) * nx >= 0;   // (a to b along the tangent, or back)
    for (let v = i; v < i + 6; v++) { const atA = P.getX(v) === ax && P.getZ(v) === az, dA = atA ? 0 : L, dB = L - dA, s0 = fw ? dA : dB, s1 = fw ? dB : dA, c0 = cv[k * 2 + (fw ? 0 : 1)], c1 = cv[k * 2 + (fw ? 1 : 0)];
      out[v * 2] = c0 ? Math.min(65534, Math.round(s0 * 100) + 1) : 65535; out[v * 2 + 1] = c1 ? Math.min(65534, Math.round(s1 * 100) + 1) : 65535; } });
  return out; }
function todayYears(mesh, PW, PD, reach, scale, roads = null, bands = null, riseYear = null, lowH = 0) {   // (lowH: [the low fabric's height m, its largest footprint m2], its density map LANES)   // (riseYear(year, t): the growth's band a building rising at film time t (its own, when later than its year's) is shown with)
  if (YEAR_W.value || !mesh || typeof document === 'undefined') return;
  const P = mesh.geometry.attributes.position, C = mesh.geometry.attributes.aCtr, D = mesh.geometry.attributes.aData, GT = mesh.geometry.attributes.aGrowT; let gt_ = 0; if (!C || !D) return;
  const recs = []; let lx = 1e9, lz = 1e9, x0 = 1e9, z0 = 1e9, x1 = -1e9, z1 = -1e9, yr = 0, hm_ = 0; ROOFS = roofScan(mesh.geometry);
  for (let i = 0; i <= C.count; i++) { const x = i < C.count ? C.getX(i) : NaN, z = i < C.count ? C.getY(i) : NaN;
    if (x !== lx || z !== lz) { if (x1 > -1e9) recs.push([yr, x0, z0, x1, z1, gt_, hm_]); lx = x; lz = z; x0 = z0 = 1e9; x1 = z1 = -1e9; if (i < C.count) { yr = D.getX(i); gt_ = GT ? GT.getX(i) : 0; hm_ = D.getY(i); } }
    if (i < C.count) { const px = P.getX(i), pz = P.getZ(i); if (px < x0) x0 = px; if (px > x1) x1 = px; if (pz < z0) z0 = pz; if (pz > z1) z1 = pz; } }
  for (let i = recs.length - 1; i >= 0; i--) { const r = recs[i]; if (Math.max(r[3] - r[1], r[4] - r[2]) > 400 * scale) recs.splice(i, 1); }   // (a runway, a long embankment: no plaster round it, it is not a block)
  { const c = 50 * scale, g = new Map(); for (const [, a, b, cc, d] of recs) for (let i = Math.floor(a / c); i <= Math.floor(cc / c); i++) for (let j = Math.floor(b / c); j <= Math.floor(d / c); j++) { const k = i * 100003 + j; (g.get(k) || g.set(k, []).get(k)).push([a, b, cc, d]); }
    WALLS = { g, c }; }
  recs.sort((a, b) => b[0] - a[0]);   // (the latest first: the earliest drawn last, on top)
  const N = 4096, mk = e => { const c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, N, N);
    for (const [y, a, b, cc, d] of recs) { const v = Math.max(1, Math.min(255, Math.round((y > 1 ? y : 1900) - 1899))); g.fillStyle = `rgb(${v},${v},${v})`;
      const u0 = Math.floor((a - e) / PW * N + N / 2), v0 = Math.floor((b - e) / PD * N + N / 2), u1 = Math.ceil((cc + e) / PW * N + N / 2), v1 = Math.ceil((d + e) / PD * N + N / 2); g.fillRect(u0, v0, u1 - u0, v1 - v0); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.flipY = false; t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; return [t, g]; };
  const [w, gw] = mk(reach * scale), [tt, gt] = mk(130 * scale); YEAR_W.value = w; YEAR_T.value = tt;   // (YEAR_T: the year the urban extent reaches a place)
  // the cover: every footprint 18 m round, softened by about a block's street (so its edge runs along the blocks, round at their
  // corners, never in texels), read with a linear filter; the year still decides when (YEAR_W, wider)
  // the cover as whole blocks: every footprint 45 m round, softened, cut high (the shader's .6-.75): the gaps inside a block
  // filled, the edge some 15-25 m off the outer buildings (a closing); the streets (lines.json roads) in its green channel
  { const c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, N, N); g.fillStyle = '#f00'; const e = 45 * scale;
    for (const [, a, b, cc, d] of recs) g.fillRect((a - e) / PW * N + N / 2, (b - e) / PD * N + N / 2, (cc - a + 2 * e) / PW * N, (d - b + 2 * e) / PD * N);
    g.filter = `blur(${Math.max(1, 22 * scale / PW * N).toFixed(1)}px)`; g.drawImage(c, 0, 0); g.filter = 'none';
    // the urban extent in its blue channel (every footprint 130 m round, softened, cut high): the open ground inside it that is no
    // block (a park, a square, a campus's green) is the model's green, not the country's land
    { const c2 = document.createElement('canvas'); c2.width = c2.height = N; const g2 = c2.getContext('2d'); g2.fillStyle = '#000'; g2.fillRect(0, 0, N, N); g2.fillStyle = '#00f'; const e2 = 130 * scale;
      for (const [, a, b, cc, d] of recs) g2.fillRect((a - e2) / PW * N + N / 2, (b - e2) / PD * N + N / 2, (cc - a + 2 * e2) / PW * N, (d - b + 2 * e2) / PD * N);
      g2.filter = `blur(${Math.max(1, 110 * scale / PW * N).toFixed(1)}px)`;   // (wide: a village's scatter falls under the cut, a city's fabric stays)
      g2.drawImage(c2, 0, 0); g2.filter = 'none';
      g.globalCompositeOperation = 'lighter'; g.drawImage(c2, 0, 0); g.globalCompositeOperation = 'source-over'; }
    if (roads) { g.globalCompositeOperation = 'lighter'; g.strokeStyle = '#0f0'; g.lineCap = 'round';
      const W = { motorway: 30, trunk: 26, primary: 22, secondary: 13, tertiary: 10, residential: 7, unclassified: 7, living_street: 6 };   // (the arterials as wide grooves)
      for (const r of roads) { const w = W[(r.cls || '').replace('_link', '')] || 6; g.lineWidth = Math.max(1, w * scale / PW * N); g.beginPath();
        r.pts.forEach(([x, z], k) => { const u = (x / PW + .5) * N, v = (z / PD + .5) * N; k ? g.lineTo(u, v) : g.moveTo(u, v); }); g.stroke(); }
      g.globalCompositeOperation = 'source-over'; }
    if (STREETS.list && STREETS.list.length) {   // the finer streets (data/streets.json) at half: lines, not grooves
      g.globalCompositeOperation = 'lighter'; g.strokeStyle = '#007000'; g.lineCap = 'round';
      const W = { secondary: 12, tertiary: 9, residential: 6, unclassified: 6, living_street: 5 };
      for (const r of STREETS.list) { g.lineWidth = Math.max(.8, (W[r.cls] || 6) * scale / PW * N); g.beginPath();
        r.pts.forEach(([x, z], k) => { const u = (x / PW + .5) * N, v = (z / PD + .5) * N; k ? g.lineTo(u, v) : g.moveTo(u, v); }); g.stroke(); }
      g.globalCompositeOperation = 'source-over'; }
    // the fabric's density in its alpha: the share of the ground round a place its buildings' extents cover, softened some 40 m
    // (todayLight pave: a dense fabric's ground between its buildings is lanes and courts in asphalt, an open superblock's round
    // its towers paved plazas); the cover kept as data, so no canvas premultiplies its colours by that alpha
    const cv = document.createElement('canvas'); cv.width = cv.height = N; const gc = cv.getContext('2d'); gc.fillStyle = '#000'; gc.fillRect(0, 0, N, N); gc.fillStyle = '#fff';
    const LH_ = lowH ? lowH[0] : 0, LA_ = lowH ? lowH[1] * scale * scale : 0;   // (todayLight lanes [3], [4]: the low fabric's height and its largest footprint (extent) m2: its density in the green channel of a second canvas; a big low building, a hall in its open plot, not fabric)
    for (const [, a, b, cc, d, , h] of recs) { gc.fillStyle = LH_ && h < LH_ && (cc - a) * (d - b) < LA_ ? '#fff' : '#f00'; gc.fillRect((a / PW + .5) * N, (b / PD + .5) * N, Math.max(.5, (cc - a) / PW * N), Math.max(.5, (d - b) / PD * N)); }
    const cv2 = document.createElement('canvas'); cv2.width = cv2.height = N; const gc2 = cv2.getContext('2d'); gc2.fillStyle = '#000'; gc2.fillRect(0, 0, N, N);
    gc2.filter = `blur(${Math.max(1, 40 * scale / PW * N).toFixed(1)}px)`; gc2.drawImage(cv, 0, 0); gc2.filter = 'none';
    const id = g.getImageData(0, 0, N, N).data, dd = gc2.getImageData(0, 0, N, N).data; for (let i = 3; i < id.length; i += 4) id[i] = dd[i - 3];
    if (LH_) { const ld = new Uint8Array(N * N * 4); for (let i = 0; i < N * N; i++) ld[i * 4] = dd[i * 4 + 1];   // (the low fabric's density alone: lanes and courtyards between low buildings, not round towers)
      const lt = new THREE.DataTexture(ld, N, N, THREE.RGBAFormat); lt.colorSpace = THREE.NoColorSpace; lt.minFilter = lt.magFilter = THREE.LinearFilter; lt.generateMipmaps = false; lt.needsUpdate = true; LANES.value = lt; }
    const t = new THREE.DataTexture(id, N, N, THREE.RGBAFormat); t.colorSpace = THREE.NoColorSpace; t.minFilter = t.magFilter = THREE.LinearFilter; t.generateMipmaps = false; t.needsUpdate = true; YEAR_C.value = t; }
  // the cover by the film's bands of years (its growth): band k's channel holds every building older than its end, closed into
  // blocks as the cover is, so the plaster arrives band by band in block shapes, never in the year map's cells (BAND_C, BAND_HI)
  if (bands && bands.length) { const nb = Math.min(bands.length, 8), e = 45 * scale, chan = ['#f00', '#0f0', '#00f'];
    const tgt = [0, 1].map(() => { const c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, N, N); return [c, g]; });
    const cv = () => { const c = document.createElement('canvas'); c.width = c.height = N; return [c, c.getContext('2d')]; };
    const [one, go] = cv(), [one2, go2] = cv(), [ext2, gx2] = cv();
    BAND_IX = []; let slot = 0; const yMax = recs.reduce((m, r) => Math.max(m, r[0]), 0);   // (the data's latest year: the last band, open-ended, is done by then)
    for (let k = 0; k < nb && slot < 6; k++, slot++) { const [, gt_] = tgt[slot < 3 ? 0 : 1]; go.globalCompositeOperation = 'source-over'; go.filter = 'none'; go.fillStyle = '#000'; go.fillRect(0, 0, N, N); go.fillStyle = chan[slot % 3];
      go.fillStyle = '#fff'; for (const [y0_, a, b, cc, d, t_] of recs) { const y = riseYear ? riseYear(y0_, t_) : y0_; if ((y > 1 ? y : 1900) < bands[k][1]) go.fillRect((a - e) / PW * N + N / 2, (b - e) / PD * N + N / 2, (cc - a + 2 * e) / PW * N, (d - b + 2 * e) / PD * N); }   // (a building that rises later than its year (aGrowT: when the camera first sees it) brings its ground with it, not with its year)
      // its fabric: how much of the ground round it the cover holds (the cover softened 150 m): a city's fabric holds most of it, a
      // village's scattered houses a little, so the built ground keeps to the continuous fabric and a village's houses stand on the land
      gx2.globalCompositeOperation = 'source-over'; gx2.filter = `blur(${Math.max(1, 150 * scale / PW * N).toFixed(1)}px)`; gx2.drawImage(one, 0, 0); gx2.filter = 'none';
      go.filter = `blur(${Math.max(1, 22 * scale / PW * N).toFixed(1)}px)`; go2.globalCompositeOperation = 'source-over'; go2.filter = go.filter; go2.drawImage(one, 0, 0); go2.filter = 'none';
      go2.globalCompositeOperation = 'multiply'; go2.drawImage(ext2, 0, 0); go2.drawImage(ext2, 0, 0); go2.fillStyle = chan[slot % 3]; go2.fillRect(0, 0, N, N);   // (the cover times its fabric squared: the shader's cut keeps the fabric, its edge soft)
      gt_.globalCompositeOperation = 'lighter'; gt_.drawImage(one2, 0, 0); gt_.filter = 'none'; gt_.globalCompositeOperation = 'source-over'; BAND_IX.push(Math.min(bands[k][1], yMax + 1)); }   // (shown once the band is done, its buildings up: the growth counts a band done half way through its rise; the plaster never runs ahead of them)
    BAND_C.forEach((U_, i) => { const t2 = new THREE.CanvasTexture(tgt[i][0]); t2.colorSpace = THREE.NoColorSpace; t2.flipY = false; t2.minFilter = THREE.LinearFilter; t2.generateMipmaps = false; U_.value = t2; });
    for (let k = 0; k < 6; k++) BAND_HI.value[k] = k < BAND_IX.length ? BAND_IX[k] : 1e5; }
  { const ie = gt.getImageData(0, 0, N, N).data; YEAR_E = new Uint8Array(N * N); for (let i = 0; i < N * N; i++) YEAR_E[i] = ie[i * 4]; }
  const im = gw.getImageData(0, 0, N, N).data; YEAR_D = new Uint8Array(N * N); for (let i = 0; i < N * N; i++) YEAR_D[i] = im[i * 4];
}
const BUILT = { value: null }, TREES = { value: null }, PLATE = { value: new THREE.Vector2(1, 1) }, CANV = () => typeof document !== 'undefined' ? document.createElement('canvas') : null, BUILT_C = CANV(), TREES_C = CANV(); let BUILT_K = null; const BUILT_S = { sig: null, v: 0 };
// the trees' mask the same way: the generator's trees (part 4: gardens, horti, groves), each `tree` m round, the flock laid over them (baseGLSL)
function builtMask(eras, PW, PD, scale, reach, treeR) {   // (eras: S.eras; a building counts once its era's front has raised it halfway: uEraT past its rank's start)
  // (drawn again only when what it shows changes, BUILT_V: an era's clock moves on every frame, its buildings standing do not)
  const meshes = eras.map(e => e.mesh), up = e => e.u && e.u.uEraT ? e.u.uEraT.value : 1e9, span = e => e.u && e.u.uEraSpan ? e.u.uEraSpan.value : 0, grow = e => e.u && e.u.uEraGrow ? e.u.uEraGrow.value : 0;
  const key = eras.filter(e => e.mesh.visible).map(e => e.mesh.uuid + ':' + up(e).toFixed(2)).join(); if (key === BUILT_K) return; BUILT_K = key; PLATE.value.set(PW, PD);
  const N = 2048, mk = c => { c.width = c.height = N; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, N, N); g.fillStyle = '#fff'; return g; };
  const r = Math.max(1, reach * scale / PW * N), rt = Math.max(1, treeR * scale / PW * N), ops = []; let sig = 2166136261;   // (ops: what to draw; sig: its fingerprint)
  for (const e of eras) { const m = e.mesh; if (!m.visible) continue; const C = m.geometry.attributes.aCtr, D = m.geometry.attributes.aData; if (!C) continue;
    let lx = 1e9, lz = 1e9; const T_ = up(e), sp = span(e), gr = grow(e), u = e.u || {}, v_ = k => u[k] ? u[k].value : 0;
    const fO = u.uEraO ? u.uEraO.value : { x: 0, y: 0 }, fR = v_('uEraFallR'), fIn = v_('uEraFallIn'), fW = v_('uEraFallW'), LO = u.uLossO ? u.uLossO.value : [];
    const fall = (cx, cz, o, R, fin, R1) => { const dd = Math.hypot(cx - o.x, cz - o.y), a = fin > .5 ? (dd - R) / Math.max(R1 - R, 1e-5) : (R - dd) / Math.max(R - R1, 1e-5), t = Math.min(1, Math.max(0, a)); return t * t * (3 - 2 * t); };   // (studio.js fallK: a city taken back, a part lost)
    const P_ = m.geometry.attributes.position; let bx0 = 1e9, bz0 = 1e9, bx1 = -1e9, bz1 = -1e9, i0 = 0;
    const flush = (i) => {   // (the record that ended at vertex i: its footprint, if it stands)
      if (i0 >= i) return; const x = C.getX(i0), z = C.getY(i0);
      if (D && T_ < D.getZ(i0) * sp + gr * .5) return;   // (not risen yet)
      if (fall(x, z, fO, fR, fIn, fW) > .5) return;   // (taken back)
      if (D) { const w = D.getW(i0), k = Math.round(w - 4); if (k >= 0 && k < LO.length && fall(x, z, LO[k], u.uLossR.value[k], u.uLossIn.value[k], u.uLossW.value[k]) > .5) return; }   // (a part lost)
      const pt = D ? Math.round(D.getY(i0)) : 0, yr = D ? D.getX(i0) : 0;
      if (pt === 4) { ops.push([0, (x / PW + .5) * N, (z / PD + .5) * N]); sig = Math.imul(sig ^ i0, 16777619); return; }
      if (!(pt === 0 || pt === 1 || pt === 11 || (pt === 7 && !(yr > 9.5 && yr < 49.5)))) return;   // (buildings, platforms, plazas and yards: not walls, roads, earth or water)
      const e = reach * scale; ops.push([1, (bx0 - e) / PW * N + N / 2, (bz0 - e) / PD * N + N / 2, (bx1 - bx0 + 2 * e) / PW * N, (bz1 - bz0 + 2 * e) / PD * N]); sig = Math.imul(sig ^ (i0 + 7), 16777619); };
    for (let i = 0; i < C.count; i++) { const x = C.getX(i), z = C.getY(i);
      if (x !== lx || z !== lz) { flush(i); lx = x; lz = z; i0 = i; bx0 = bz0 = 1e9; bx1 = bz1 = -1e9; }
      const px_ = P_.getX(i), pz_ = P_.getZ(i); if (px_ < bx0) bx0 = px_; if (px_ > bx1) bx1 = px_; if (pz_ < bz0) bz0 = pz_; if (pz_ > bz1) bz1 = pz_; }
    flush(C.count); sig = Math.imul(sig ^ (C.count + 13), 16777619); }
  sig = String(sig) + ':' + eras.filter(e => e.mesh.visible).map(e => e.mesh.uuid).join() + ':' + PW + ':' + PD;
  if (sig === BUILT_S.sig && BUILT.value) return; BUILT_S.sig = sig; BUILT_S.v++;
  const gb = mk(BUILT_C), gt = mk(TREES_C);
  for (const o of ops) if (o[0]) gb.fillRect(o[1], o[2], o[3], o[4]); else { gt.beginPath(); gt.arc(o[1], o[2], rt, 0, 6.2832); gt.fill(); }
  for (const [g, c, b] of [[gb, BUILT_C, r * 1.1], [gt, TREES_C, rt * 1.2]]) { g.filter = `blur(${b.toFixed(1)}px)`; g.drawImage(c, 0, 0); g.filter = 'none'; }   // (wide: a lone building outside the city fades under the threshold, a quarter stays)
  for (const [U_, c] of [[BUILT, BUILT_C], [TREES, TREES_C]]) { if (!U_.value) { U_.value = new THREE.CanvasTexture(c); U_.value.colorSpace = THREE.NoColorSpace; U_.value.flipY = false; } U_.value.needsUpdate = true; }   // (flipY off: rows as drawn, z down the canvas, as the plate's uv)
}
// the base every material stands on: a grey slate plate, its grain and veins, a sheen where the light grazes it; the land's rise in
// stacked sheets (step m), each a little lighter, its edge a light line; the water a glossy resin; streets and plazas a lighter inlay
const SLATE = { slate: [.31, .31, .31], step: 6, edge: 1.45, resin: [.20, .14, .08] };
// the maquette's base: a photographed cleft slate (engine/tex/slate: Poly Haven dark_rock_02, CC0), its colour scaled to `slate`
// (linear) over its own mean, `size` m a repeat (and 6.3 times that, turned, over it), its normal `bump` strong; the sheets of the
// land's rise `step` m, their edges a faint `edge`; the water a glossy resin. In the sunny miniature the land is a fresh meadow
// (land olive and ochre: its two greens, fields faintly), the groves fresh greens (flock), a town's ground light warm paving (ground_in)
const SLATE_TEX = { tex: 'slate', slate: [.0068, .0068, .0068], mean: .032, size: 55, ground_in: { col: [.80, .76, .70], reach: 16, park: [.56, .72, .34] }, flock: { col: [.30, .48, .18], col2: [.44, .56, .22], town: { built: .6, cell: 11, share: .7, groves: [.35, .6], size: [4.5, 7], free: .3 }, tree: 16, bank: .9, slope: .8, edge: .7, land: .5, cell: 16, crown: [.42, 1.04, [1.06, 1.03, .84]], wall: 1.5,
    street: { off: 2.2, r: 2.5, vary: [.9, 1, 1.12], every: { secondary: 9, tertiary: 9 }, minor: 11, junction: 14, floor: 8.6, rows: true, px: 1.2, far: [.35, .5] }, px: 2, far: [3.5, 4.5] },
  land: { olive: [.56, .64, .36], ochre: [.68, .70, .44], field: 140, rock: [.5, .8], rockC: [.64, .60, .52], scrub: [.42, .54, .22] }, bump: 1.6, ground: '#cfc3a6', step: 6, edge: 1.12, resin: [.46, .64, .71], gloss: [.08, .55, [.80, .86, .92]] };   // (resin: clear tinted acrylic; gloss: its reflection of the room, [at a steep view, toward a grazing one, its colour])   // (land rock: only the steep faces, the slope as drawn)
// the colour film's picture, as a photograph of a model on a table: a warm key from a sun fixed in the world, low and to the side
// of where the film's camera mostly looks from (sunSide degrees round from it: shadows fall across the frame and toward the eye,
// where they read, and an orbit turns them as a real one would), a cool fill from the sky, the shadow fitted to the ground the
// frame shows (every house and tree on its own hard shadow at any range) and the ambient occlusion full (every crevice and the foot
// of every wall darker); a lens whose depth of field softens what is nearer as well as farther than the subject; no veil of air
// over the plate. The land a meadow with fields in strips and woods in clusters of big canopies; trees big enough to read
// a lens setting given as [close, wide]: eased between them by the shot's distance (fx.js fxLens: a close shot .03, a whole city .35), else as it is
const byD = (v, d) => Array.isArray(v) ? THREE.MathUtils.lerp(v[0], v[1], THREE.MathUtils.smoothstep(d, .03, .35)) : v;
const FILM_PIC = { sunEl: 30, sunSide: 75, sun: 1.05, sunC: '#ffdcae', sky: .8, skyC: '#d0d6e2', skyGround: '#9a9578', fogNear: 6, fogFar: 40,
  ao: 1.0, aoR: [.012, 4, 14], vignette: .12, sat: .9, contrast: .1, dof: { k: 1.6, max: 24, band: .375, two: true, at: 1.1, Ak: .0545 },   // (aoR: the occlusion's reach, a share of the distance, between these metres; dof band and Ak may be [close, wide], byD)
  land: { source: 'quiet', scrub: 14, earth: .18, meadow: true }, tree: { size: 1.1, woodSize: 1.2, keep: .06, wood: .97, grid: 16, hue: .06, facets: true, clearWood: 90, count: 150000, grow: true },
  // a region's land in the film, where its palette's own greens read olive under the sun (LAND_PALETTES): a clean blue-green meadow
  landTone: { loess: { grass0: [.22, .36, .16], grass1: [.28, .42, .19], straw: [.70, .64, .42], soil: [.58, .50, .36], wood: [.12, .25, .10] } },
  relief: 3.5,   // the land's slopes this many times as steep in the light (the terrain's own heights, exaggerated as drawn)
  projector: 0,   // the studio's projector light on the land by day (rings, washes, a standing city's edge light, the pick): none
  pathW: 16, pathC: '#d8c8a4',   // a route as a path drawn on the land: this many metres wide, its colour mixed with this earth
  town: .74,   // a standing city's ground: its palette's earth at this lightness, mostly grey, even (compacted earth, paving)
  garden: { chinese: true },   // ... or, a town of compounds in their gardens, its open ground grass, kitchen gardens and lanes (detail.js trees gardens)
  // a period city's colours as a model's: roof against wall against ground (dark tile over light rammed earth or plaster, deep
  // terracotta over varied washes), a court paved, a ditch's water dark
  tone: { chinese: { roofs: ['#737980', '#7d8389', '#6e747b', '#848a90', '#787e85'], walls: ['#e0d0ad', '#d6c39c', '#e8dcc2', '#cdb790', '#ddcba6'], parts: { 5: '#3f6e7a', 7: '#a39c8f', 9: '#4f5358' } },
    roman: { roofs: ['#a8553a', '#c46a45', '#8f4a36', '#c98a62', '#b0624a', '#9a5a48', '#cf9470', '#7d4535', '#b8705a'],   // (terracotta new, weathered, darker, paler: house by house)
             walls: ['#f0e6d2', '#e8cfa0', '#dcb48a', '#f3ece0', '#e6c4a6', '#d8a983', '#ecdcb6', '#cba486'] } },
  hscale: { k: .47, near: .06, far: .2 },
  // material: the model the film's picture is made of (null: painted, as above), a palette's own in looks[material][palette]
  // (walls, roofs, parts, detail, tree as PALETTES), and the base's (base: slate, step: a contour sheet's rise in metres, its
  // edge's light, resin: the water; sand: the ground's, grain), the light (pic: FILM_PIC keys)
  material: null,
  looks: {
    // a sunny pastel miniature (it was a museum's maquette of plaster, wood and slate; the name kept): every period city and today's
    // in soft mixed colours, under today's light (todayLight all)
    maquette: { pic: { sunEl: 50, rake: 22, relief: 3, sun: 1.12, dof: { k: 6, max: 40, band: [.08, .2], two: true, at: .95, Ak: .25, tilt: [.55, 1, 9, 1, .04, .3, .45, 1.2], tiltWide: [.62, 1, 8, .3, .5] }, aoR: [.02, 4, 14], sunC: '#ffe9cc', sky: .55, skyC: '#ece4d6', skyGround: '#6a645a', ao: .35, vignette: .45, pathW: 0, pool: [.12, .2], haze: [.7, 2.6], fogC: '#3a3530', tree: { keep: 0, wood: 0, count: 0 } }, base: SLATE_TEX,
      roman: { walls: ['#f2e2c8', '#ecd2ae', '#f5ece0', '#e6c7a8', '#f0dcc0'], roofs: ['#c47250', '#d0805c', '#b86a4c', '#d89470', '#c27a5c', '#cc8a66'],
        parts: { 1: '#f6f0e4', 2: '#e0cfae', 4: '#4f7a2a', 7: '#d6cfc2', 9: '#c47250', 10: '#d8c7a6', 11: '#ddd4c4' }, tree: { dark: 1.25, sat: 1.5 }, flags: false,
        detail: { floor: '#e6d5b6', joint: '#3c3e42', ridge: '#cfb184', shop: '#5a4a3a', base: '#d3c6ac' } },
      // a Chinese town: dark grey tile roofs over warm walls (cream, ochre, brick red), a city wall of light warm stone, its courts
      // and streets paved light, red columns
      chinese: { walls: ['#ecd9b4', '#e2c49a', '#cf9b78', '#f0e3c8', '#d8ae86'], roofs: ['#cdd0d4', '#d6d8db', '#c4c8cc', '#dadcde', '#cfd2d6'],
        parts: { 1: '#f0e6d2', 2: '#dcc7a0', 5: '#5fb8b0', 7: '#d2cbbf', 9: '#cdd0d4', 10: '#d8c7a6', 11: '#d6cdbd' }, tree: { dark: 1.25, sat: 1.5, town: 1 }, flags: false,
        faces: { earth: '#dcc59c', brick: '#cdb48e', stone: '#e0cfac', banded: '#d8c6a2' },
        detail: { floor: '#e8dcc6', joint: '#a8a092', base: '#c9c0b0', post: '#a85a44', column: '#b0503c', beam: '#6e6156', ridgeEnd: '#6f706e', coping: '#8f908f', cornice: '#6a6866',
          ridge: '#7e7f7d', lattice: '#86705f', leaf: '#5e4b3f', paving: '#bfbab1', well: '#77736d', patch: '#6f7a4a', archRing: '#b5afa4' } },
      // a detailed model's material roles (a glb's material names) as the model's: stone and glass a white acrylic, glass engraved as a
      // tower is (a fine floor line each storey, a mullion every 1.5 m, by pixels) with a sheen and the sky in it, metal a light grey;
      // a glb entry's own colours over them (swap colours: by role; parts: by its parts' names). In the sunny miniature: stone a
      // warm off-white, glass pale blue-silver, metal light silver; glbParts: a landmark's spheres, capsules and domes (by their
      // parts' names) in the look's rose accent
      glbC: { stone: '#ece6dc', glass: '#a2b6cc', metal: '#d3d9de', dark: '#8f9295', roof: '#d9d6cf' }, glbParts: [['sphere|capsule|dome', '#d68a98']], roofs: true, backdropH: .04,   // (backdropH: today's city behind a period city, its heights this share: a plan on the board)
      // today's rooftops (roofsMesh): the plant room (main: its share of the roof's sides, [from, more]; mainH: its height m [from, more]), small units on roofs from area m2
      // (n: how many [from, to], size and h: m [from, more]); mainK, unitK: a plant room's and a unit's paint, its roof's own times one of these (each its own).
      // With the roof kinds on (todayLight roofKinds), today.roofKinds units in their place
      roofUnits: { main: [.14, .1], mainH: [2.5, 1.5], mainK: [.86, .9, .94, .88, .92], area: 250, n: [1, 3], size: [2.5, 2.5], h: [1.4, 1], unitK: [.88, .92, .96, .9, .94] },
      // today's city the subject, a coloured miniature city in a clear warm day: a warm sun with soft-edged shadows (sunEl,
      // shadowR: the shadow's softening in its map's texels), a cool sky in the shade (sky, skyC), the whole picture's exposure, a
      // gentle filmic curve, no grain; edge: every edge catching the light as a bevel (a pale line, close only: afar it outlined
      // every roof into speckle); no bloom (it ringed the white towers); daylight, not a dark room (pool: the light pool's floor).
      // The air: a sky dome (dome: its horizon and its zenith) and a warm light haze toward its horizon colour (fogC, haze: where
      // it begins and where it is whole, times the shot's distance), so the far city fades into the sky and the board's edge is
      // never seen (air: [where it begins and its depth, times the shot's distance; the plate's last metres, whole at its edge],
      // drawn in the picture's own depth; fogC: the same as a fog, where the passes have no depth); sat, contrast: the grade.
      // The board: a model's painted ground between the buildings, a light warm grey paving (board: the block ground, courtyards
      // and lots light and warm as the paintings' are, yet under the roofs and the lit walls round them; the roads asphalt of
      // their own, streets); optionally the lanes and courtyards inside a densely built block of low buildings in a colour of
      // their own (lanes: [colour, the low fabric's density from which, whole, its height m, its largest footprint m2]);
      // optionally a light paving where the fabric is open, pave: [colour, density from
      // which asphalt, whole], e.g. [[.64, .62, .61], .05, .18]: round towers in their superblocks), its streets asphalt by
      // class (street: their colour, their share), squares and quays paved light
      // (plaza: a light warm paving, not cream; paving: [a slab m, its joint m, the joint's tone, the slabs' variation], its large
      // slabs), a kerb line close (kerb), parks lawn in two greens (park), mown (lawn: [its mottle's strength, size m, its grain's
      // strength, size m, a low border along its edge m, the border's tone]); a landmark's own round plaza (a glb entry's plaza,
      // roundPlaza: [its paving, its inner disc's, its rings' spacing m, radial joints, a joint m, the joints' tone]); the streets
      // as geometry with their materials (streets: see streetsMesh); the shade side of today's painted walls in their own paint, warmed
      // by the sunlit ground (wallShade: [the sky light's own colour kept, times, its tint, the shade's saturation]: a pastel in shade still a pastel); the water
      // (water: the shallows along the banks, the deep, how far from the bank the deep begins in metres, its roughness (the sun's
      // glint broad and soft), its gloss [at a steep view, toward a grazing one, the sky's colour in it]); trees: its street and
      // park trees (flockAt), natural greens; crown: today's crowns' shade side and sunlit cap (flock crown's), lighter and yellower than a
      // period grove's; streetTrees: today's street trees over the flock's street (crowns that touch along a planted strip); parkTrees:
      // the parks as the paintings' are, groves and clusters on open lawn, single trees between, their edges lined (flockAt plantTile),
      // in their own deeper mid-greens under the lawn's light green, a lit cap over a darker body (its trees and crown).
      // ?pic={"todayLight":{...}}: a still's own
      todayLight: { all: true, env: 0, footprintsR: [4, 3000], winFade: [.25, .8], wallSun: [1.42, 1.2, .84, .55], wallShade: [1, 1.08, [1.025, .995, .96], 1.3], bevel: [1.5, 1.4, .75, .85], walls: [.03, .8, 1, .04], roof: [.05, 2.5, 1, .06, 1.12], glassSky: [.22, [.86, .85, .84], [.60, .72, .86]], groundFill: [.45, 3.6, 1.75, [.6, 1.75]], glassK: .55, skyC: '#b4c4dc', skyGround: '#c8b8a0', sky: 4.8, sun: 2.3, sunC: '#ffdfbc', sunEl: 42, exposure: 1.06, ao: [.5, .45], parkTrees: { cell: 8, size: [3.1, 4.8], groves: [.42, .47], noise: [90, 28], dense: .95, lone: .05, edge: [12, .5], trees: [[.33, .50, .25], [.38, .54, .27], [.30, .47, .23], [.27, .43, .22]], crown: [.62, 1.1, [1.06, 1.05, .9]], far: [2.2, 3.2, .9, [.62, .76, .30]] }, bloom: [9, 0], dof: 1, band: 1,
        edge: .35, filmic: .5, grain: 0, pool: 1, sat: 1.12, contrast: .16, vignette: .08, shadowR: 3, air: [3.5, 10, 2500], fogC: '#dfe5ee', dome: ['#dfe5ee', '#4a90e0'], sunLeft: -70,
        far: [3, 8, .6, '#e2e8f0', [.85, 1.1, [.3, .5], [1.55, 1.85, .45, .8, 1.05, '#a4adb9'], [.85, '#a6b1bd', 1]], .5],   // (far: the far city softened, [from, whole, times the shot's distance; the share of its own contrast kept; the tint; a raking shot's from and whole as shares of its frame's top edge's distance, whichever nearer: the top of the frame pale and cool as the paintings' are; in a wide shot only cooled, its buildings still distinct; the share of its own chroma kept where it is whole: its colour goes before its definition])
        board: [.49, .44, .375], soft: [0, 8], street: [[.46, .46, .48], 0], plaza: [.535, .505, .48], paving: [7, .45, .2, .08], kerb: [.86, .85, .82],
        streets: { asphalt: '#505154', pavement: '#716c65', kerb: 2.5, w: { motorway: 30, trunk: 26, primary: 20, secondary: 13, tertiary: 10, residential: 7, unclassified: 7, living_street: 5, other: 6 }, grain: [.08, .8, .1, .05],
          marks: { minW: 9, lane: 3.5, most: 2, w: .45, dash: [6, 9], edge: 99, clear: 1.5, zebra: [1.5, 4, .9, .9], stop: .6, drive: 1, c: '#e6e3dc', k: .06, kerb: [.4, .4, '#cdc8bf', .45, .6], far: [.45, 1.2] } }, park: [[.49, .575, .22], [.44, .525, .195]], lawn: [.16, 2.5, .08, .7, 1.2, -.18], roundPlaza: [[.40, .39, .38], [.50, .49, .47], 7, 48, .35, .25],   // (streets: geometry, streetsMesh; the raster's share 0)
        water: { shallow: [.32, .61, .61], deep: [.22, .52, .52], reach: 15, rough: .45, ripple: .08, gloss: [.03, .4, [.62, .86, .88]], refl: [.2, .3], sparkle: [0, 2.5, .8, .58] },
        bank: { stone: [.74, .70, .66], w: 2.5, prom: [.50, .48, .47], pw: 14, line: .3 },
        trees: [[.48, .60, .30], [.56, .66, .33], [.42, .55, .28], [.37, .50, .27]], crown: [.58, 1.14, [1.14, 1.1, .72]],
        streetTrees: { r: 3.8, every: { secondary: 6, tertiary: 6 }, minor: 7, junction: 10 },
        massing: { storey: 3.2, min: [8, 5], tower: 50, podium: [14, .7, [4, 6], .3, [.22, 4, 10]], crown: [80, .5, 2, 2.5], set: [24, .55, [1, 2], [2, 3.5], .5], step: [.45, [.55, .75]], split: { area: 1000, maxH: 45, minW: 20, depth: [11, 17], width: [8, 15], lane: 1.6, h: [.7, 1] } },
        facade: { base: [4.5, .8, 9], cap: [.9, 1.1, .72, 1.8], piers: [2, 4, 1.4], rows: [.25, .38], mid: [.3, .42, .45, .8, .85, .7], reveal: [1.14, .72], glass: { pale: [.9, .92, .94], mull: .85, span: [.2, .45], top: 1.12, px: 1.2, coarse: 4, deep: [.74, .82, .95] }, brick: [.4, .55, .6] } },
      // light presets over todayLight (FILM_PIC todayPreset): golden, the golden hour for the opening and the return to today: a low
      // warm sun ahead of the camera and to its left (sunLeft), long soft shadows, blue-violet shade, its glow on the sky (dome[2])
      // and clouds (dome[3]), a warm haze, glass and water catching gold (the rippled water a glitter path toward the sun)
      presets: { golden: { sunEl: 10, sunLeft: -115, sun: 3.6, sunC: '#ffb066', sky: 2.8, skyC: '#9c9ad6', skyGround: '#d8b090', exposure: 1.18, groundFill: [.7, 1.4], glassSky: '#ffc890', glassK: 2.2, domeRate: 5, sat: 1.12, contrast: .18, bloom: [.95, .3],
        fogC: '#f2cfa6', dome: ['#ffc890', '#7c9ad4', '#ffa040', [1, 4.5, .48, '#ffe2cc']], air: [4.5, 14, 2500], far: [3, 8, .6, '#f0c9a4'],
        park: [[.64, .64, .30], [.56, .58, .26]], trees: [[.40, .46, .18], [.50, .52, .22], [.44, .48, .16]],
        water: { shallow: [.46, .62, .62], deep: [.20, .40, .48], reach: 90, rough: .14, ripple: .35, gloss: [.08, .5, [.88, .80, .84]], refl: [.3, .35], sparkle: [.2, 5] } } },
      // today's buildings painted by kind (colourToday kinds; FACADE_GLSL draws each kind's facade): the old low fabric (lower than
      // oldH, smaller than bigA m2) grey tile roofs over grey brick and red brick (oldRoofs: the only grey roofs the paintings
      // have); a large low building pale, its hall's roof a material of its own (bigRoofs); an office tower (from towerH m and
      // towerA m2 of footprint, or any from tallH m) in tinted glass, pale blue-green or silver, its top its own (towerRoofs); the
      // rest, most of the city, homes in soft paints (cream, ivory, sand, pale peach, salmon, light grey); stone, a civic or old
      // stone building (from the data's first stoneSpan years, stoneA m2 or more, its outline filling stoneC of its extent, lower
      // than stoneH), beige to off-white. A home's and a stone building's flat roof in its own wall's paint, lit as a top facing the
      // sky and the sun: light, about as bright as its lit walls, its warmth a step cooler under the sky (as the paintings' roofs
      // against their lit walls: the same L, a* kept, b* some 6 lower), so each building reads as one coloured block with a bright
      // top (a pink building a light pink roof, a cream one a light cream one; one grey for every roof made an aerial a grid of
      // grey squares); the walk-ups' (lower than tiledH) a share of them (tiled) in terracotta tile. Every roof by its building's
      // kind and height, never by the camera's distance (a roof would change colour as the camera moves)
      today: { long: ['#8d8a84', 400], roofs: ['#d9d6cf', '#cfccc5', '#e2dfd8'], flat: ['#dcd9d2', '#d2cfc8', '#e4e1da', '#cbc8c1'], flatShare: .85, walls: ['#ebe8e1', '#e3e0d9', '#f0ede6', '#dedbd4', '#e7e4dd'], tall: ['#e6e8ea', '#dde1e5', '#eceeef', '#d6dbe0'],
        kinds: { oldH: 13, bigA: 1500, towerH: 60, towerA: 900, tallH: 120, tiledH: 30, tiled: .12, stoneSpan: 12, stoneA: 1000, stoneC: .5, stoneH: 80,
          stone: ['#ece6dc', '#e6ded2', '#f2eee6', '#e0d8cc', '#ebe4d8'],
          homes: ['#f8d0c6', '#f6c8bc', '#f7d4cc', '#f8efe2', '#f6d2c2', '#d4dde8', '#f8dccf', '#f4cbc4', '#f5d6c6', '#f6cdc6'], tiles: ['#d08a6a', '#c98066', '#d89a78'],
          oldWalls: ['#dccfc2', '#d2c6b8', '#ecc8b6', '#e2d6c8', '#e6c2b2'], oldRoofs: ['#868c94', '#8c9199', '#80868e', '#90959c'],
          big: ['#ece2d4', '#f2d8ca', '#efe0cc'], bigRoofs: ['#9da3ab', '#979ea6', '#a3a8af'],
          glass: ['#adbed0', '#b4c3d4', '#bbc6d0', '#a9bacc', '#b8c6d4'], towerRoofs: ['#d6d4cf', '#cccbc7'] },
        // each building's roof kind (roofClass: the paintings' catalogue of roofs; drawn only with todayLight roofKinds on, a
        // specimen sheet's (tools/roofsheet.py) until every kind passes there), by its data alone: old: a building counts as
        // old up to this many years from the data's first; oldH: an old block's height below this m (3 to 7 storeys, as the
        // data's estimated heights read them), oldA: its footprint m2 [from, to]; rect: the share of its least rectangle a
        // footprint fills for a pitched roof; slab: [height m from, to, its length over its width from, its width at most m, the
        // share of its least rectangle it fills from]; point: a point tower [from m, its footprint at most m2, its length over its
        // width at most]; pink, grey: the shares of the old blocks hipped in pastel pink and in grey tile (the rest flat in their
        // own paint: grey stays a minority), drawn for a whole street block (cluster: roofClusters), and in any district (quota:
        // [its size m, its grey tile's share of its roofs' area at most]) no more; slabOchre: the share of the
        // estates under ochre gables, hallOchre: of the near-rectangular large halls under ochre hips; pitch: a pitched roof's
        // (roofsMesh; tiles: its courses [their spacing along the slope m, their shade, from this many courses a pixel toward their
        // mean, there by twice that], FACADE_GLSL); paint: the roofs' paints (roofPaint); units: the rooftop pieces by roof kind
        // (roofsMesh): one large low plant room on a mid- or high-rise's flat roof (main: its share of the roof's area [from, more];
        // mainH: its height m [from, more]); a point tower's round caps (caps: their diameter's share of the roof's width [from,
        // more], their height m [from, more]); a slab's long rounded plant room (capsule: its length's share of the roof's [from,
        // more], its width's, its height m); the old fabric's grey roof's dark hatch (slot: its share of the roof's area, its
        // paint's times); mainK, unitK: a plant room's and a small piece's paint, its roof's own times one of these (each its own)
        roofKinds: { old: 12, oldH: 26, oldA: [40, 3000], rect: .8, slab: [12, 30, 2.4, 18, .7], point: [40, 950, 1.5], pink: .3, grey: .35, slabOchre: .2, hallOchre: .1, cluster: [60, 8, 30, [5, .25], 15], quota: [500, .3],
          units: { main: [.2, .15], mainH: [2.4, .8], mainK: [.86, .9, .94, .88, .92], caps: [.25, .15, 1.2, .6], capsule: [.3, .3, .4, 1.8], slot: [.06, .55], unitK: [.94, .97, 1, .96, .98] },
          pitch: { deg: [30, 22], maxH: 5, share: .35, minW: 4, cover: .6, gable: .3, pieces: 6, tiles: [.9, .16, .35] },
          paint: { light: .3, slab: ['#fbf6f0'], slabK: .9, glass: ['#e7d8c5', '#e6dbd9', '#e0d8d4'], hall: ['#9da3ab', .7], grey: ['#8f9098', '#94959a', '#8a8b92'], tile: ['#8b8e96', '#94989f', '#8f9095'], lane: ['#8d888c', '#888588'],
            pink: ['#bf9c99', '#d6a49f', '#cca19c'], ochre: ['#ef916c', '#f19c6e'] } } } },
    // a clay diorama: terracotta tiles in relief, each its own, a sandy ground, cobbled streets, moss at the walls' feet
    clay: { pic: { sunEl: 38, sun: 1.1, sunC: '#ffd6a8', sky: .85, skyC: '#efe2cf', skyGround: '#6e6150', tree: { keep: 0, wood: 0, count: 0 } }, base: SLATE,
      soft: .6, tiles: 2.2, tufts: true,   // (soft: the share of a corner's averaged normal in each face's, a rounded edge; tiles: their rows' relief, times; tufts: moss at the walls' feet)
      roman: { roofs: ['#b8613f', '#c4704a', '#a65a3e', '#c97f57', '#b0573a', '#bd6a48'], parts: { 1: '#d9c7a6', 7: '#9a8f7c', 10: '#9a8f7c', 11: '#9a8f7c' }, flags: false,
        tree: { dark: .7, sat: .6 }, detail: { tuft: '#4f6a2a', joint: '#6e6556' } } } },   // a close shot's heights (HSCALE): walls this share as tall (a period city's x3 toward x1.4) nearer than `near` model units, none from `far`
  band: null };   // the tilt-shift band of screen blur (none: the lens's depth of field does it), else { mid, inner, outer, top, bottom }
// today's light (a material's todayLight, a still's own over it): see looks.maquette
// (a light preset over it, todayPreset: one of the material's presets, e.g. the golden hour; the film or ?pic= names it)
const todayL = () => MAT && MAT.todayLight ? { ...MAT.todayLight, ...((MAT.presets || {})[FILM_PIC.todayPreset] || {}), ...(FILM_PIC.todayLight || {}) } : null;
// (todayLight roofKinds: each building's roof by its kind (today.roofKinds: roofClass, roofsMesh); off, every flat roof in its
// building's paint with its plant room and units, the old fabric's grey tile in rows)
const kindsOn = () => !!(todayL() && todayL().roofKinds && MAT && MAT.today && MAT.today.roofKinds);
// (todayLight all: its light, air, lens and water are the look's in every shot, the period cities' too; else only while today's city is the subject)
const allDay = () => !!(todayL() && todayL().all), TS_GLSL = () => allDay() ? '1.' : 'uTodayK.y * (1. - smoothstep(.3, .6, uTodayK.z))';
// a still's own picture over the film's (?pic={json}: keys of FILM_PIC, an object merged into its own, e.g. pic={"dof":{"A":6}}):
// a lens, a light or a far field tried on one frame before it goes into FILM_PIC; the colour film only
const picMerge = o => { for (const [k, v] of Object.entries(o || {})) FILM_PIC[k] = v && typeof v === 'object' && !Array.isArray(v) && FILM_PIC[k] ? { ...FILM_PIC[k], ...v } : v; };
let PIC_Q = null;
try { const q = typeof location !== 'undefined' && new URLSearchParams(location.search).get('pic'); if (q) { PIC_Q = JSON.parse(q); picMerge(PIC_Q); } }
catch (e) { console.error(`pic=: ${e.message}`); }
const MAT = FILM_PIC.material && FILM_PIC.looks[FILM_PIC.material] || null;
if (MAT) { picMerge(MAT.pic); picMerge(PIC_Q); }   // (a material's light; a still's own picture over it)
// the tilt-shift band (the colour film): blur in one direction per pass, as wide as the distance from the band asks
const BAND_BLUR = {
  uniforms: { tDiffuse: { value: null }, dir: { value: new THREE.Vector2(1, 0) }, px: { value: new THREE.Vector2(1 / 1920, 1 / 1080) }, k: { value: 1 },
    mid: { value: .5 }, inner: { value: .1 }, outer: { value: .5 }, top: { value: 10 }, bottom: { value: 6 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }',
  fragmentShader: `varying vec2 vUv; uniform sampler2D tDiffuse; uniform vec2 dir, px; uniform float k, mid, inner, outer, top, bottom;
  void main(){ float y = vUv.y - mid, r = smoothstep(inner, outer, abs(y)) * (y > 0. ? top : bottom) * k;
    if (r < .3) { gl_FragColor = texture2D(tDiffuse, vUv); return; }
    vec4 c = vec4(0.); float w = 0.;
    for (int i = -7; i <= 7; i++) { float f = float(i) / 7., g = exp(-f * f * 2.2); c += texture2D(tDiffuse, vUv + dir * px * f * r) * g; w += g; }
    gl_FragColor = c / w; }` };
// the parts (pipeline/citygen.py): FAB 0, LMK 1, WALL 2, BRIDGE 3, TREE 4, WATER 5, DARK 6, PAVE 7, ROOF 8, LROOF 9, EARTH 10, PLINTH 11.
// A house (FAB walls, ROOF) takes one of the walls and one of the roofs by its building's centre; the other parts their colour.
// land: the fields' greens and straw (fx.js LAND_PALETTES, the white model's land under fx land too); glb: a detailed model's materials (tools/blender/kit.py); cypress: the share of tall
// narrow trees; detail: the colours of the pieces engine/detail.js puts on the houses and walls (its kinds), in the palette's region's way (detail.js STYLES);
// faces: a city wall's colour by what it is faced with (detail.js WALL_FACES), its courses a shade darker (a stone wall's bands of brick)
const PALETTES = {
  roman: {
    walls: ['#ebe1cc', '#e8d4ab', '#ddc196', '#f1eadc', '#e4c9b0', '#d6b78f', '#efdcc0'],
    roofs: ['#b65c3d', '#c26d45', '#a95d47', '#c47d57', '#a05848', '#ba684b', '#c98a63'],
    parts: { 1: '#e6dcc8', 2: '#cdb38c', 3: '#cbbd9f', 4: '#5a7340', 5: '#4f8aa3', 6: '#2f2620', 7: '#aaa59b', 9: '#a65d45', 10: '#c9b086', 11: '#bcae92' },
    land: LAND_PALETTES.mediterranean,
    glb: { stone: '#e8dfcc', dark: '#2b231d', roof: '#a85b43', sand: '#d2b98c' }, cypress: .3,
    detail: { joint: '#9c907c', shop: '#3b2b21', arcade: '#e3d9c6', ridge: '#8b4a34', patch: '#5e7a3a', window: '#33281f', door: '#4b3323', cornice: '#f4eee2', base: '#8f8a82', coping: '#b0603f', archRing: '#ebe3d2', flags: ['#a3262a', '#6e2a63'], sail: '#efe6d2' },
    faces: { earth: '#c9ad86', brick: '#b8805c', stone: '#ddd3c0', banded: '#e6dbc6' },
  },
  chinese: {
    walls: ['#ddcca8', '#d4bd94', '#e6d8bb', '#cdb38c', '#e0cfae'],
    roofs: ['#6c6863', '#78726b', '#625f5b', '#7f7970', '#5c5854'],
    parts: { 1: '#e2d5b8', 2: '#bfa070', 3: '#cbbd9f', 4: '#5f7d3c', 5: '#5d8fa8', 6: '#2f2620', 7: '#d8cbaa', 9: '#5d5955', 10: '#c9a978', 11: '#b8a58a' },
    land: LAND_PALETTES.loess,   // the loess plain: wheat, millet, bare earth
    glb: { stone: '#e3d6b8', dark: '#2b231d', roof: '#5f5b56', sand: '#c8a676' }, cypress: .08, tree: { size: .6, keep: .35, dark: .6, sat: .75 },   // (tree: its size, the share of places kept, its lightness)
    detail: { lattice: '#5b3526', leaf: '#3e271c', paving: '#76726b', well: '#4f4b46', patch: '#556a2e', base: '#97918a', post: '#7a3524', beam: '#4e3b2e', ridgeEnd: '#4f4b47', coping: '#5b5853', archRing: '#8f8b85', column: '#8a2e20', cornice: '#3a3431', ridge: '#a3a6a8', flags: ['#b3262c', '#d9a21b'], sail: '#a8764a' },
    faces: { earth: '#bfa070', brick: '#8f8b84', stone: '#cac2b3', banded: '#d9cdb6' },
  },
  modern: {
    walls: ['#e9dfcf', '#f1ebe0', '#ddd2bf'], roofs: ['#c0714c', '#9d6a52', '#a8a39b'],
    parts: { 1: '#f1ebe0', 2: '#cdb08a', 3: '#d4d0c8', 4: '#5f7d3c', 5: '#5d8fa8', 6: '#3a3a3c', 7: '#c9c6bf', 9: '#9d6a52', 10: '#cdb48c', 11: '#bdb6aa' },
    land: LAND_PALETTES.temperate,
    glb: { stone: '#efe9de', dark: '#2b2b2d', roof: '#9d6a52', sand: '#cdb48c' }, cypress: .1,
    detail: { window: '#33302c', door: '#4b3a2c', cornice: '#f4f0e8', base: '#b8b0a2', coping: '#9d6a52', archRing: '#efe9de', flags: ['#a3262a', '#2f4f7a'], sail: '#efe6d2' },
    faces: { earth: '#cdb08a', brick: '#b37e5e', stone: '#ddd6c8', banded: '#e6ddcc' },
  },
};
const hash = (x, z) => { const s = Math.sin(x * 127.1 + z * 311.7) * 43758.5453; return s - Math.floor(s); };

// a house's roof colour, by its building's centre (aCtr): one of the palette's, a little lighter or darker (its tiles' rows: detail.js)
const roofOf = (pal, x, z) => { const h = hash(x, z); return new THREE.Color(pal.roofs[Math.floor((h * 7.31) % 1 * pal.roofs.length)]).multiplyScalar(.9 + .18 * ((h * 13.7) % 1)); };
// a period city's colour per vertex: a house's walls and roof each one of the palette's, by its building; a little lighter or darker;
// with the detail (detail.js; wall: { face: the city's walls' (film.json wall_face) or null, upright: its region's for an upright
// wall }), a gable's end in its wall's colour and a city wall in the colour of what it is faced with (a battered side rammed earth)
// trees: { cell, dark } the generator's own trees (part TREE: a garden's, a park's) each its own green, as the look's trees are (a
// cell that wide holds one tree), not one flat dark green over a whole garden
function colourMesh(mesh, pal, detail, wall, trees = null, flatRoofs = false) {   // (flatRoofs, the film: a house body's flat top a roof, in the roofs' colours)
  const g = mesh.geometry, d = g.attributes.aData, c = g.attributes.aCtr, n = g.attributes.position.count, out = new Float32Array(n * 3), col = new THREE.Color(), P = g.attributes.position;
  const walls = pal.walls.map(v => new THREE.Color(v)), roofs = pal.roofs.map(v => new THREE.Color(v)), gable = detail ? gableEnds(g) : new Uint8Array(n);
  const parts = Object.fromEntries(Object.entries(pal.parts).map(([k, v]) => [k, new THREE.Color(v)]));
  const faces = detail && pal.faces ? Object.fromEntries(Object.entries(pal.faces).map(([k, v]) => [k, new THREE.Color(v)])) : null, N = g.attributes.normal;
  const faceAt = i => { if (wall.face) return faces[wall.face]; const ny = Math.abs(N.getY(i - i % 3) + N.getY(i - i % 3 + 1) + N.getY(i - i % 3 + 2)) / 3; return faces[ny > .02 && ny < .9 ? 'earth' : wall.upright]; };
  for (let i = 0; i < n; i++) {
    const part = d ? Math.round(d.getY(i)) : 0, h = c ? hash(c.getX(i), c.getY(i)) : .5, h2 = (h * 7.31) % 1, h3 = (h * 13.7) % 1;
    if (part === 0 && flatRoofs && N.getY(i) > .9) col.copy(roofs[Math.floor(h2 * roofs.length)]);   // (seen from above a light top among the roofs reads as a speck)
    else if (part === 0 || gable[i]) col.copy(walls[Math.floor(h * walls.length)]);
    else if (part === 8) col.copy(roofs[Math.floor(h2 * roofs.length)]);
    else if (part === 2 && faces) col.copy(faceAt(i));
    else if (part === 4 && trees) { const q = hash(Math.round(P.getX(i - i % 3) / trees.cell), Math.round(P.getZ(i - i % 3) / trees.cell)); col.setHSL(.2 + q * .09, .3 + (q * 7.31) % 1 * .16, (.25 + (q * 13.7) % 1 * .12) * trees.dark); }
    else col.copy(parts[part] || walls[0]);
    const k = part === 0 || part === 8 ? .9 + .18 * h3 : .96 + .08 * h3;
    out[i * 3] = col.r * k; out[i * 3 + 1] = col.g * k; out[i * 3 + 2] = col.b * k;
  }
  g.setAttribute('color', new THREE.BufferAttribute(out, 3));
  return new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .92, metalness: 0 });
}

// today's city: its records have no parts (year, height, an id), so a top is a roof and a side a wall; by its region (TODAY, the
// film's film.look today): roman, an old Mediterranean town's (roofs mostly tile, some flat and grey; walls in warm plasters, tall
// buildings in the pale tones of new ones); chinese, an old Chinese town's (grey tile, grey brick and whitewash); modern, a modern
// city's (flat concrete roofs, walls in concrete and render, tall buildings in glass and pale stone). flat: the share of roofs flat
const TODAY = {
  roman: { roofs: ['#9a5038', '#8c4b36', '#a6603f', '#7f4a3a'], flat: ['#9d9a94'], flatShare: .3, walls: ['#d9b57e', '#e3cc9e', '#cf9a6c', '#e8dcc2', '#c98f6a'], tall: ['#e6e3dc', '#cfd2d4', '#d9d2c4'] },
  chinese: { roofs: ['#5f5c58', '#6a6661', '#57544f', '#73706a'], flat: ['#9a9893', '#8c8a86'], flatShare: .35, walls: ['#cfc8bc', '#b9b2a6', '#e0dbd0', '#a8a197', '#d8d2c6'], tall: ['#e2e1dc', '#c9ced2', '#d8d4ca'] },
  modern: { roofs: ['#6d6e72', '#7d6a5e', '#5f6268'], flat: ['#a9a8a3', '#9b9a96', '#b8b6b0', '#8f8e8a'], flatShare: .85, walls: ['#dad6ce', '#c8c5bf', '#e6e2da', '#b9b6b0', '#d4ccbe', '#c2bfb8'], tall: ['#cdd4d9', '#b4c0ca', '#e3e3df', '#9eaebb', '#d6d3cb'] },
};
// a building's paint by its kind (colourToday's choice; the massing's split units take theirs the same way): [wall, roof]. A home's
// (but a tiled walk-up's) and a stone building's roof its own wall's paint (the light does the rest); the old fabric's, a tower's
// and a hall's their kind's own (oldRoofs, towerRoofs, bigRoofs)
function kindPaint(K, k, hm, q, q2, pick) {
  const wall = pick(['oldWalls', 'homes', 'glass', 'big', 'stone'][k], q);
  const roof = k === 1 && hm < K.tiledH && q2 < K.tiled ? pick('tiles', (q2 * 7.7) % 1)
    : k === 1 || k === 4 ? wall : pick({ 0: 'oldRoofs', 2: 'towerRoofs', 3: 'bigRoofs' }[k], q2);
  return [wall, roof]; }
// a footprint's least rectangle (along one of its outline's edges: one of them is the hull's that bounds it least), from its walls'
// ring points (each wall's first vertex: studio.js prism, walls before the top): its area, long and short side, centre and the
// bearing of its long side, in the model's units; null for fewer than three points
const LR_ = { x: new Float64Array(256), z: new Float64Array(256) };
function leastRect(P, N, i0, i1) {
  let n = 0; const pa = P.array, na = N.array;   // (positions and normals: three floats a vertex, as studio.js makes them)
  for (let j = i0; j + 5 < i1 && Math.abs(na[j * 3 + 1]) < .3; j += 6) { if (n === LR_.x.length) { const x = new Float64Array(n * 2), z = new Float64Array(n * 2); x.set(LR_.x); z.set(LR_.z); LR_.x = x; LR_.z = z; }
    LR_.x[n] = pa[j * 3]; LR_.z[n] = pa[j * 3 + 2]; n++; }
  if (n < 3) return null; const X = LR_.x, Z = LR_.z; let A = Infinity, b = null;
  for (let e = 0; e < n; e++) { const e1 = e + 1 < n ? e + 1 : 0, dx = X[e1] - X[e], dz = Z[e1] - Z[e], l = Math.hypot(dx, dz); if (!(l > 0)) continue;
    const ux = dx / l, uz = dz / l; let u0 = Infinity, u1 = -Infinity, v0 = Infinity, v1 = -Infinity;
    for (let m = 0; m < n; m++) { const u = X[m] * ux + Z[m] * uz, v = Z[m] * ux - X[m] * uz; if (u < u0) u0 = u; if (u > u1) u1 = u; if (v < v0) v0 = v; if (v > v1) v1 = v; }
    if ((u1 - u0) * (v1 - v0) < A) { A = (u1 - u0) * (v1 - v0); b = [ux, uz, u0, u1, v0, v1]; } }
  if (!b) return null; const [ux, uz, u0, u1, v0, v1] = b, um = (u0 + u1) / 2, vm = (v0 + v1) / 2, du = u1 - u0, dv = v1 - v0;
  return { A, L: Math.max(du, dv), W: Math.min(du, dv), cx: um * ux - vm * uz, cz: um * uz + vm * ux, th: du >= dv ? Math.atan2(uz, ux) : Math.atan2(ux, -uz) }; }
// a building's roof (today.roofKinds R; the paintings' catalogue of roofs), by its data alone, the same from any camera: its kind,
// or the neighbourhood whose choice it takes (-1 an old block: its street block's, -2 a slab: its estate's; roofClusters). From
// its kind of building k (colourToday: 2 a glass tower, 3 a large low hall), height hm m, footprint ar m2, old (from the data's
// first years), q its own hash, and form(): its least rectangle's long and short side L, W m and the share fill of it the
// footprint covers (asked only where a rule needs it).
// The kinds: 1 flat in its own paint, one large plant room (the default: mid- and high-rise); 2 a point tower's, round caps; 3 a
// slab's, one long plant room; 4 a glass tower's, warm white; 5 a large low hall's; 6 the old fabric's soft grey, flat; 7 grey
// tile, hipped or gabled; 8 a lane house's small gable (an old block's courtyard units, roofsMesh); 9 a pastel pink hip; 10 an
// ochre gable (an estate's slabs) or hip (a hall); 11 setbacks (the massing's podiums and setbacks, roofsMesh); 12 the detailed
// models' own. A pitched kind (7, 9, 10) is drawn on a footprint that fills its least rectangle and carries no massing; any
// other takes its family's flat kind (roofFlat)
function roofClass(R, { k, hm, ar, old, q }, form) {
  if (k === 2) return 4;
  if (k === 3) return q < R.hallOchre && form().fill >= R.rect ? 10 : 5;
  const slab = hm >= R.slab[0] && hm < R.slab[1], oldB = old && hm < R.oldH && ar >= R.oldA[0] && ar <= R.oldA[1], point = hm >= R.point[0] && ar <= R.point[1];
  if (!slab && !oldB && !point) return 1;
  const { L, W, fill } = form(), asp = L / Math.max(W, 1e-9);
  if (slab && fill >= R.slab[4] && asp >= R.slab[2] && W <= R.slab[3]) return -2;
  if (oldB) return -1;
  if (point && asp <= R.point[2]) return 2;
  return 1; }
// a neighbourhood's roof by its hash q: an old block's pastel pink hips (9), grey tiles (7) or flat roofs in its own paints (1),
// in the shares pink, grey and the rest; an estate's ochre gables (10) or flat slabs (3), in the share slabOchre
const roofOfCluster = (R, cat, q) => cat === -2 ? (q < R.slabOchre ? 10 : 3) : q < R.pink ? 9 : q < R.pink + R.grey ? 7 : 1;
// a kind's flat member, where its pitch cannot stand (a footprint far from a rectangle, a building with massing): grey tile the
// old fabric's grey flat (6), a pink hip a flat roof in its own paint (1), an ochre gable a slab's (3) or a hall's (5) flat
const roofFlat = (kind, kd) => kind === 7 ? 6 : kind === 9 ? 1 : kind === 10 ? (kd === 3 ? 5 : 3) : kind;
// today's buildings' neighbourhoods (roofKinds cluster [the cell m, the greatest gap m between two old blocks, between two slabs,
// the heights' difference at most m or this share of the taller, the bearings' at most degrees]): two old blocks of about one
// height, square to each other and a lane apart, are one street block; two slabs of about one height, parallel, a row's spacing
// apart, are one estate; each takes its whole neighbourhood's choice, by the least hash of its members, so a block reads as one
// patch of roofs, an estate as rows of one roof (no building its own draw among its neighbours). M: [x, z, bearing, L, W, height
// m, -1 or -2, hash] each, in the model's units; s: the model's scale. Returns each member's neighbourhood hash and its
// neighbourhood (one member's index)
function roofClusters(R, M, s) {
  const C = R.cluster, cell = C[0] * s, grid = new Map(), up = new Int32Array(M.length), q = new Float64Array(M.length);
  for (let i = 0; i < M.length; i++) { up[i] = i; const k = Math.floor(M[i][0] / cell) * 100003 + Math.floor(M[i][1] / cell); (grid.get(k) || grid.set(k, []).get(k)).push(i); }
  const root = i => { while (up[i] !== i) { up[i] = up[up[i]]; i = up[i]; } return i; };
  const reach = (m, ax, az) => m[3] / 2 * Math.abs(Math.cos(m[2]) * ax + Math.sin(m[2]) * az) + m[4] / 2 * Math.abs(-Math.sin(m[2]) * ax + Math.cos(m[2]) * az);
  const gap = (a, b) => { const dx = b[0] - a[0], dz = b[1] - a[1]; let g = -Infinity;   // (their separation along the four sides' axes: the gap between two rectangles)
    for (const t of [a[2], a[2] + Math.PI / 2, b[2], b[2] + Math.PI / 2]) { const ax = Math.cos(t), az = Math.sin(t); g = Math.max(g, Math.abs(dx * ax + dz * az) - reach(a, ax, az) - reach(b, ax, az)); }
    return g; };
  const turn = C[4] * Math.PI / 180;
  for (let i = 0; i < M.length; i++) { const a = M[i], gx = Math.floor(a[0] / cell), gz = Math.floor(a[1] / cell);   // (its cell and the eight round it)
    for (let ox = -1; ox <= 1; ox++) for (let oz = -1; oz <= 1; oz++) { const L2 = grid.get((gx + ox) * 100003 + gz + oz); if (!L2) continue;
      for (const j of L2) { if (j <= i) continue; const b = M[j]; if (a[6] !== b[6]) continue;
        if (Math.abs(a[5] - b[5]) > Math.max(C[3][0], C[3][1] * Math.max(a[5], b[5]))) continue;
        const per = a[6] === -2 ? Math.PI : Math.PI / 2; let dt = Math.abs(a[2] - b[2]) % per; dt = Math.min(dt, per - dt); if (dt > turn) continue;
        if (gap(a, b) > (a[6] === -2 ? C[2] : C[1]) * s) continue;
        const ra = root(i), rb = root(j); if (ra !== rb) up[Math.max(ra, rb)] = Math.min(ra, rb); } } }
  const lo = new Float64Array(M.length).fill(Infinity); for (let i = 0; i < M.length; i++) { const r = root(i); lo[r] = Math.min(lo[r], M[i][7]); }
  const top = new Int32Array(M.length); for (let i = 0; i < M.length; i++) { top[i] = root(i); const t = Math.sin(lo[top[i]] * 1e4 + 91.7) * 43758.5453; q[i] = t - Math.floor(t); }
  return { q, root: top }; }
// a flat roof's paint by its kind (today.roofKinds paint): its wall's own (1, 11), its wall's lighter (2: light, toward white), a
// near-white cream with its wall's tint (3: slab, slabK: the cream, its share), warm white (4: glass), its wall's toward a light
// warm grey (5: hall [the grey, its share]),
// a soft warm grey (6: grey); a pitched roof's (7 tile, 8 lane, 9 pink, 10 ochre) its own; x its own draw
function roofPaint(R, kind, wall, x) {
  const P = R.paint, pick = a => (R._pc ||= {})[a] ||= P[a].filter(c => typeof c === 'string').map(c => new THREE.Color(c)), one = a => pick(a)[Math.floor(x * pick(a).length) % pick(a).length];
  return kind === 2 ? wall.clone().lerp(new THREE.Color(1, 1, 1), P.light) : kind === 3 ? wall.clone().lerp(pick('slab')[0], P.slabK) : kind === 4 ? one('glass') : kind === 5 ? wall.clone().lerp(pick('hall')[0], P.hall[1])
    : kind === 6 ? one('grey') : kind === 7 ? one('tile') : kind === 8 ? one('lane') : kind === 9 ? one('pink') : kind === 10 ? one('ochre') : wall; }
// a drawn record's form, its vertices [i0, i1): its top's area ar (model units) and its least rectangle's sides L, W m and fill
function recordForm(P, N, i0, i1, ar, s) { const lr = leastRect(P, N, i0, i1); return { L: lr ? lr.L / s : 0, W: lr ? lr.W / s : 0, fill: lr && lr.A > 0 ? ar / lr.A : 0, lr }; }
// a record's top's area in the model's units (its triangles facing up)
function topArea(P, N, i0, i1) { const pa = P.array, na = N.array; let ar = 0;
  for (let j = i0; j + 2 < i1; j += 3) if (na[j * 3 + 1] > .6) { const o = j * 3; ar += Math.abs((pa[o + 3] - pa[o]) * (pa[o + 8] - pa[o + 2]) - (pa[o + 6] - pa[o]) * (pa[o + 5] - pa[o + 2])) / 2; }
  return ar; }
// the roof kinds' map (todayLight roofMap: a check of the assignment, each roof tinted by its kind, the walls one light grey):
// [the walls, kind 1, .., kind 11]; the grey kinds (6, 7, 8) dark
const ROOF_MAP = ['#d8d8d8', '#f2c200', '#8e44ad', '#40b0ff', '#30e0a0', '#8a5a2e', '#4040a0', '#101010', '#a0206a', '#ff7fa8', '#ff6a00', '#e02020'].map(c => new THREE.Color(c));
const roofMapOn = () => kindsOn() && !!todayL().roofMap;
// (todayLight roofMap a colour, '#rrggbb': every roof that one colour, its pieces and pitched roofs with it: two renders that differ
// only there give a frame's roof pixels, a mask for a check that nothing else changed)
// (todayLight roofMap "parts": each roof's parts apart, unlit, for a measure of each on the lit frame of the same camera
// (tools/roofsheet.py): roofs red, parapets green, plant rooms (and caps) blue, small units yellow, the pieces' sides half as bright,
// the walls the map's grey)
const ROOF_PARTS = { roof: new THREE.Color('#ff0000'), rim: new THREE.Color('#00ff00'), plant: new THREE.Color('#0000ff'), unit: new THREE.Color('#ffff00') };
const partsOn = () => roofMapOn() && todayL().roofMap === 'parts';
const ROOF_MAP1 = {}, roofMapC = k => { const v = todayL() && todayL().roofMap; return v === 'parts' ? ROOF_PARTS.roof : typeof v === 'string' ? (ROOF_MAP1[v] ||= new THREE.Color(v)) : ROOF_MAP[k]; };
function colourToday(mesh, T = TODAY.roman) {
  const g = mesh.geometry, d = g.attributes.aData, nrm = g.attributes.normal, n = g.attributes.position.count, out = new Float32Array(n * 3), col = new THREE.Color();
  const C = a => a.map(c => new THREE.Color(c)), roofs = C(T.roofs), flats = C(T.flat), walls = C(T.walls), tall = C(T.tall);
  // T.long: [colour, metres] a record whose footprint runs longer than this (a runway, an embankment) in that colour, not a building's white
  const lng = new Uint8Array(n), LC = T.long ? new THREE.Color(T.long[0]) : null;
  if (LC) { const P = g.attributes.position, A = g.attributes.aCtr, lim = T.long[1] * (T.scale || 1e-4); let i0 = 0;
    const end = i => { let x0 = 1e9, z0 = 1e9, x1 = -1e9, z1 = -1e9; for (let j = i0; j < i; j++) { const x = P.getX(j), z = P.getZ(j); if (x < x0) x0 = x; if (x > x1) x1 = x; if (z < z0) z0 = z; if (z > z1) z1 = z; }
      if (Math.max(x1 - x0, z1 - z0) > lim) lng.fill(1, i0, i); i0 = i; };
    for (let i = 1; i <= n; i++) if (i === n || A.getX(i) !== A.getX(i - 1) || A.getY(i) !== A.getY(i - 1)) end(i); }
  // T.kinds (a material's, looks.maquette today): each building painted by its kind, read from its height and its footprint's
  // area, and stone (a civic or old stone building) by its year, size and compact outline; aKind the facade FACADE_GLSL draws on it
  // (0 the old fabric, 1 a home, 2 an office tower's glass, 3 a large low building, 4 stone), from the same choice
  // T.roofKinds: each building's roof kind (roofClass; an old block's and a slab's its neighbourhood's, roofClusters), a byte a
  // vertex in g.userData.roofKind (read on the CPU only: a replacement footprint's children take their parent's, todayFootprints;
  // roofsMesh draws it, or its flat member, on each record), its top in the paint of the kind it shows flat (roofPaint, roofFlat)
  const K = T.kinds, kind = K ? new Float32Array(n) : null, paint = K ? new Float32Array(n * 3) : null, RK = K && kindsOn() && T.roofKinds, rkind = RK ? new Uint8Array(n) : null, map = !!RK && roofMapOn();
  if (K) { const P = g.attributes.position, A = g.attributes.aCtr, s2 = (T.scale || 1e-4) ** 2, s1 = T.scale || 1e-4, KC = {}, pick = (a, x) => (KC[a] ||= C(K[a]))[Math.floor(x * K[a].length) % K[a].length];
    let i0 = 0, y0 = 1e9; for (let i = 0; i < n; i++) { const y = d.getX(i); if (y > 1 && d.getW(i) < .5 && y < y0) y0 = y; } g.userData.y0 = y0;   // (y0: the data's first year)
    const recs = [], mem = [], cellA = new Map(), QC = RK ? RK.quota[0] * s1 : 1, cellOf = (x, z) => Math.floor(x / QC) * 100003 + Math.floor(z / QC);   // (each record [i0, i1, its kind of building, wall, roof, roof kind or neighbourhood, its hash]; the neighbourhoods' members; each district's roofs' m2)
    const end = i1 => { let ar = 0, x0 = 1e9, z0 = 1e9, x1 = -1e9, z1 = -1e9;   // (its footprint: the area of its roof's triangles; its extent)
      for (let j = i0; j + 2 < i1; j += 3) if (nrm.getY(j) > .6) ar += Math.abs((P.getX(j + 1) - P.getX(j)) * (P.getZ(j + 2) - P.getZ(j)) - (P.getX(j + 2) - P.getX(j)) * (P.getZ(j + 1) - P.getZ(j))) / 2;
      for (let j = i0; j < i1; j++) { const x = P.getX(j), z = P.getZ(j); if (x < x0) x0 = x; if (x > x1) x1 = x; if (z < z0) z0 = z; if (z > z1) z1 = z; }
      const cmp = ar / Math.max((x1 - x0) * (z1 - z0), 1e-12), arm = ar / s2, hm = d.getY(i0), h = d.getZ(i0), q = (h * 7.13) % 1, q2 = (h * 3.31) % 1, yr = d.getX(i0);
      // (stone: a civic or old stone building, by the data: there from the data's first years, large, compact, not a tower)
      const k = K.stoneA && yr > 1 && yr <= y0 + K.stoneSpan && arm >= K.stoneA && cmp >= K.stoneC && hm < K.stoneH ? 4
        : hm < K.oldH && arm < K.bigA ? 0 : hm < 24 && arm >= K.bigA ? 3 : (hm >= K.towerH && arm >= K.towerA) || hm >= K.tallH ? 2 : 1;
      const [wall, roof] = kindPaint(K, k, hm, q, q2, pick); let rk = 0;
      if (RK) { let f_ = null; const t = Math.sin(h * 1e4 + 17.3) * 43758.5453, form = () => f_ ||= recordForm(P, nrm, i0, i1, ar, s1);
        rk = roofClass(RK, { k, hm, ar: arm, old: yr > 1 && yr <= y0 + RK.old, q: t - Math.floor(t) }, form);
        if (rk < 0) { const { lr } = form(); if (lr) mem.push([lr.cx, lr.cz, lr.th, lr.L, lr.W, hm, rk, h, recs.length, arm]); else rk = 1; }
        const c_ = cellOf((x0 + x1) / 2, (z0 + z1) / 2); cellA.set(c_, (cellA.get(c_) || 0) + arm); }
      recs.push([i0, i1, k, wall, roof, rk, h]); i0 = i1; };
    for (let i = 1; i <= n; i++) if (i === n || A.getX(i) !== A.getX(i - 1) || A.getY(i) !== A.getY(i - 1)) end(i);
    if (RK) { const { q: cq, root } = roofClusters(RK, mem, s1), CL = new Map();
      mem.forEach((m, i) => { let c = CL.get(root[i]); if (!c) CL.set(root[i], c = { kind: roofOfCluster(RK, m[6], cq[i]), q: cq[i], a: new Map(), m: [] });
        const k = cellOf(m[0], m[1]); c.a.set(k, (c.a.get(k) || 0) + m[9]); c.m.push(m[8]); });
      // (roofKinds quota [the district m, its grey's share at most]: a district's grey tile blocks no more than this share of all
      // its roofs' area; a neighbourhood that would take any district it lies in past it, in their hashes' order, flat in its own
      // paints: grey stays a minority in every district, not only on the whole)
      const grey = new Map(); for (const c of [...CL.values()].filter(c => c.kind === 7).sort((a, b) => a.q - b.q)) {
        if ([...c.a].some(([k, a]) => (grey.get(k) || 0) + a > RK.quota[1] * (cellA.get(k) || 0))) { c.kind = 1; continue; }
        for (const [k, a] of c.a) grey.set(k, (grey.get(k) || 0) + a); }
      for (const c of CL.values()) for (const r of c.m) recs[r][5] = c.kind; }
    for (const [j0, j1, k, wall, roof0, rk, h] of recs) { let w = wall, roof = roof0;
      if (RK) { const fk = roofFlat(rk, k); roof = map ? roofMapC(fk) : roofPaint(RK, fk, wall, (h * 5.31) % 1); if (map) w = ROOF_MAP[0]; rkind.fill(rk, j0, j1); }
      for (let j = j0; j < j1; j++) { const c = nrm.getY(j) > .6 ? roof : w; paint[j * 3] = c.r; paint[j * 3 + 1] = c.g; paint[j * 3 + 2] = c.b; kind[j] = k; } } }
  for (let i = 0; i < n; i++) {
    const h = d.getZ(i), hm = d.getY(i), top = nrm.getY(i) > .6, mound = d.getW(i) > .5;
    if (mound) col.set('#9a8f6a');
    else if (lng[i]) col.copy(LC);
    else if (K) col.setRGB(paint[i * 3], paint[i * 3 + 1], paint[i * 3 + 2]);
    else if (top) col.copy(hm > 24 || h < T.flatShare ? flats[Math.floor(h * 41) % flats.length] : roofs[Math.floor(h * 97) % roofs.length]);
    else col.copy(hm > 30 ? tall[Math.floor(h * 31) % tall.length] : walls[Math.floor(h * 53) % walls.length]);
    const k = K ? .95 + .1 * ((h * 7.13) % 1) : .9 + .2 * ((h * 7.13) % 1); out[i * 3] = col.r * k; out[i * 3 + 1] = col.g * k; out[i * 3 + 2] = col.b * k;   // (painted: a gentle variation)
  }
  g.setAttribute('color', new THREE.BufferAttribute(out, 3)); if (rkind) g.userData.roofKind = rkind;
  if (K) { g.setAttribute('aKind', new THREE.BufferAttribute(kind, 1)); g.setAttribute('aTop', new THREE.BufferAttribute(recordTops(g), 1)); if (todayL() && todayL().bevel) g.setAttribute('aEdge', new THREE.BufferAttribute(wallEdges(g, T.scale || 1e-4), 2)); }
  return new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .92, metalness: 0 });
}

// the land: fx.js's (a patchwork of fields, straw and bare earth, woods in patches and, with the relief, on the slopes: the white
// model's land under fx land is the same code, muted); the water (the studio's water map) turquoise in the shallows and deeper blue
// away from the shore, with the sun's glint. o: the land's settings (fx land, else the palette's fields alone, no woods).
// S (the film): the fields calming with distance into the same land's soft large areas (fx.js 'quiet': a patchwork seen from
// afar read as rags sewn together; a close shot keeps its fields), the water as it was (the studio's wThen), the plate lowered in
// a dug pool (the studio's deformation); far: the land beyond the plate (no water, no pools)
function landMaterial(U, PW, PD, kind, land, relief, o, ex, scale, S = null, far = false, fu = null) {   // (fu: the film's uniforms, the pall)
  const m = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .97, metalness: 0, side: far ? THREE.DoubleSide : THREE.FrontSide });
  const then = !!(S && S.wThenGLSL && !far), wr = then ? 'wThen(vXZ / uPlateM + .5, vXZ)' : far ? '0.' : 'texture2D(uWaterM, vXZ / uPlateM + .5).r';
  // (the film's meadow: a standing period city's ground dressed as a town's, yards and plots, from where its rise has reached:
  // studio.js's hide maps, rank by rank as its buildings rise; and the water's banks and depths)
  const town = !!(S && o && o.meadow && !far), H = S ? S.slots : 0, H3 = !!(S && S.slots3), p3 = a => `vec3(${a.map(x => x.toFixed(3)).join(', ')})`;
  m.onBeforeCompile = sh => {
    sh.uniforms.uWaterM = U.uWater; sh.uniforms.uPlateM = { value: new THREE.Vector2(PW, PD) }; sh.uniforms.uKind = { value: kind === 'modern' ? 1 : 0 };
    if (then) for (const k of ['uWater', 'uWT', 'uWTF', 'uWTE']) sh.uniforms[k] = U[k];
    if (town) for (const k of ['uHide', 'uHide2', ...(H3 ? ['uHide3'] : []), 'uHideT', 'uHideG']) sh.uniforms[k] = U[k];
    if (fu) Object.assign(sh.uniforms, fu);
    if (S && MAT && MAT.base && MAT.base.tex) Object.assign(sh.uniforms, slateMaps());
    if (relief) { for (const k of ['uFxHgt', 'uFxRect', 'uFxSun', 'uFxR', 'uFxRA', 'uFxLitC', 'uFxShadeC', 'uFxFlat']) sh.uniforms[k] = U[k]; sh.uniforms.uFxAdd = { value: 0 }; }   // (a bright ground: no light added on top)
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vXZ; varying vec3 vFxW;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvXZ = (modelMatrix * vec4(position, 1.)).xz; vFxW = (modelMatrix * vec4(transformed, 1.)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec2 vXZ; varying vec3 vFxW; uniform sampler2D uWaterM; uniform vec2 uPlateM; uniform float uKind;${S && MAT && MAT.base && MAT.base.tex ? ' uniform vec3 uSunDir, uSunCol; uniform sampler2D uRefl; uniform mat4 uReflM; uniform float uReflK; uniform vec2 uReflD; uniform sampler2D uSlateC, uSlateN, uSlateR, uBuilt, uTrees, uYearW, uYearT, uYearC, uLanes, uGreen, uBandC0, uBandC1; uniform float uGreenOn, uBandHi[6], uBandY; uniform vec3 uTodayK; uniform vec4 uPool, uGeoT, uRp[4], uRq[4]; vec3 slateN_ = vec3(0., 0., 1.); float slateR_ = .7, todayG_ = 0.;' : ''}${fu ? ' uniform vec2 uPallC; uniform float uPallR, uPallK;' : ''}${town ? `
uniform sampler2D uHide, uHide2${H3 ? ', uHide3' : ''}; uniform float uHideT[${H}], uHideG[${H}];
float townAt(vec2 uv){ vec4 h1 = texture2D(uHide, uv), h2 = texture2D(uHide2, uv)${H3 ? ', h3 = texture2D(uHide3, uv)' : ''};
  float hm[${H}]; hm[0] = h1.r; hm[1] = h1.g; hm[2] = h1.b; hm[3] = h1.a; hm[4] = h2.r; hm[5] = h2.g; hm[6] = h2.b; hm[7] = h2.a;${H3 ? ' hm[8] = h3.r; hm[9] = h3.g; hm[10] = h3.b; hm[11] = h3.a;' : ''}
  float t = 0.; for (int i = 0; i < ${H}; i++) { if (uHideT[i] < -.5 || hm[i] < .02) continue; float r = (hm[i] - .04) / .96;
    t = max(t, smoothstep(.02, .06, hm[i]) * smoothstep(r - uHideG[i] * .7, r + uHideG[i] * .15, uHideT[i])); }
  return t; }` : ''}${relief ? RELIEF_GLSL : ''}${landLookGLSL(land, relief, o || null, ex, scale, 'mini')}${S ? farLandGLSL(land, o) : ''}${then ? '\nuniform sampler2D uWater;' + S.wThenGLSL : ''}`)
      .replace('#include <color_fragment>', `#include <color_fragment>${S ? '\n// (look: mini)' : ''}
  vec2 m_ = vXZ / ${scale.toFixed(6)};   // metres
  float wr_ = ${wr}, wMask = smoothstep(.35, .65, wr_);${S && !far && MAT && MAT.base && MAT.base.tex && todayL() && todayL().bank ? `
  float bkT_ = uTodayK.y * (1. - smoothstep(.3, .6, uTodayK.z)), bkW_ = max(fwidth(wr_), 1e-4), bkP_ = 0., bkC_ = 0.;   // (todayLight bank: today's river embanked where today's city stands and is the subject: the water meets its wall in a line a pixel crisp, not a soft beach)
  wMask = mix(wMask, smoothstep(.5 - .7 * bkW_, .5 + .7 * bkW_, wr_), bkT_);` : ''}
{ vec3 land = fxLandAt(vFxW);${S ? `
  ${o && o.meadow ? '' : 'land = mix(land, fxLandFar(m_), smoothstep(1.2, 5., length(fwidth(m_))));   // (afar: the fields calm into soft large areas once one is under about 40 pixels of the drawn picture, gone by about 12)'}
  ${o && o.toned ? '' : 'land *= vec3(.5, .93, .98);   // (the film\'s land a clean meadow green, a sunlit model\'s: not olive, not lime)'}` : ''}
  if (uKind > .5) land = mix(land, vec3(.29, .27, .23), .55);   // a city's ground: paved, dusty${town ? `
  { vec2 uv_ = vXZ / uPlateM + .5, o_ = vec2(${(9).toFixed(1)} * ${scale.toFixed(8)}) / uPlateM;   // a town's ground: beaten-earth yards and lanes, plots in rows (its edge softened over a few cells of the map)
    float tn_ = (townAt(uv_) * 2. + townAt(uv_ + vec2(o_.x, 0.)) + townAt(uv_ - vec2(o_.x, 0.)) + townAt(uv_ + vec2(0., o_.y)) + townAt(uv_ - vec2(0., o_.y))) / 6.;
    if (tn_ > .001) {${o.garden ? `   // (a town of compounds in their gardens: its open ground grass, kitchen gardens in rows, lanes worn into the earth; its
      // streets and squares are the city's own paving, drawn over it)
      vec2 w_ = m_ + vec2(fxLn(m_ / 90.), fxLn(m_ / 90. + 5.)) * 14.;   // (no ruled grid)
      float pw_ = length(fwidth(m_)), fr_ = smoothstep(.7, 1.6, pw_);
      vec2 pc_ = w_ / vec2(34., 14.), pe_ = min(fract(pc_), 1. - fract(pc_)) * vec2(34., 14.);
      float ph_ = fract(sin(dot(floor(pc_), vec2(127.1, 311.7))) * 43758.5453);
      vec3 grass_ = ${p3(land.grass1)} * (.93 + .1 * fxLn(m_ / 17.)), soil_ = mix(${p3(land.soil)}, ${p3(land.straw)}, .3);
      vec3 plot_ = mix(mix(soil_, ${p3(land.grass0)} * .9, smoothstep(.3, .7, .5 + .5 * sin(w_.y * 3.93))), mix(soil_, ${p3(land.grass0)} * .9, .55), fr_);   // (rows 1.6 m apart; afar their mean)
      vec3 g_ = mix(grass_, plot_, step(ph_, .42) * smoothstep(.8, 1.8, min(pe_.x, pe_.y)) * (.5 + .5 * smoothstep(.35, .6, fxLn(m_ / 160. + 2.))));
      vec2 v_ = m_ + vec2(fxLn(m_ / 230. + 1.), fxLn(m_ / 230. + 8.)) * 46.;   // (lanes: a few, wandering, broken, mostly one way)
      vec2 l_ = abs(fract(v_ / vec2(95., 210.)) - .5) * vec2(95., 210.);
      float ln_ = (1. - smoothstep(1.3, 1.3 + pw_ * 1.5, l_.x)) * smoothstep(.4, .55, fxLn(v_ / 140. + 3.)) + (1. - smoothstep(1.3, 1.3 + pw_ * 1.5, l_.y)) * smoothstep(.55, .7, fxLn(v_ / 140. + 6.));
      g_ = mix(g_, mix(${p3(land.soil)}, ${p3(land.straw)}, .55) * 1.05, clamp(ln_, 0., 1.) * .75);
      land = mix(land, pow(g_, vec3(2.2)), smoothstep(.15, .85, tn_));` : `   // (an even, light compacted earth: its grain only, at the scale of the material, never in patches)
      vec3 e_ = mix(${p3(land.soil)}, ${p3(land.straw)}, .5); float l_ = dot(e_, vec3(.2126, .7152, .0722));
      vec3 yard_ = pow(mix(vec3(l_), e_, .45) * ${(o.town || FILM_PIC.town).toFixed(3)} / l_ * (.97 + .06 * fxLn(m_ / 2.3) + .03 * fxLn(m_ / 7. + 3.)), vec3(2.2));
      land = mix(land, yard_, smoothstep(.15, .85, tn_));`} } }` : ''}
  float deep = smoothstep(.4, .98, wr_);
  vec3 water = mix(vec3(.38, .68, .70), vec3(.17, .42, .56), deep) * (.95 + .1 * fxLn(m_ / 40.));${S && o && o.meadow ? `
  water = mix(vec3(.42, .70, .68), vec3(.09, .30, .46), smoothstep(.45, .95, wr_)) * (.95 + .1 * fxLn(m_ / 40.));   // (shallows by the bank, the deep dark)
  land = mix(land, pow(vec3(.78, .72, .58), vec3(2.2)), smoothstep(.12, .3, wr_) * (1. - wMask) * .85);   // (the bank: sand and gravel)` : ''}
  diffuseColor.rgb = mix(land, pow(water, vec3(2.2)), wMask);${S && MAT && MAT.base ? baseGLSL(MAT.base, scale, town, far, then) : ''}${fu ? `
  diffuseColor.rgb *= 1. - uPallK * .55 * smoothstep(uPallR, uPallR * .3, length(vXZ - uPallC));   // (under a burning city's pall)` : ''}
  }`)   // (the water's colours are sRGB; the shading is linear)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = mix(roughnessFactor, .32, wMask);' + (S && MAT && MAT.base && MAT.base.tex ? '\n  roughnessFactor = mix(clamp(slateR_ * .9, .3, 1.), .15, wMask);   // (the slate\'s own roughness, the resin\'s gloss)' + (todayL() && todayL().water ? `\n  roughnessFactor = mix(roughnessFactor, ${todayL().water.rough.toFixed(2)}, wMask * ${TS_GLSL()});   // (today's water: its own)` : '') : S && MAT && MAT.base && MAT.base.slate ? '\n  roughnessFactor = mix(.55, .18, wMask);   // (the slate\'s sheen, the resin\'s gloss)' : ''))
      .replace('#include <normal_fragment_begin>', `#include <normal_fragment_begin>${o && o.meadow ? `
  { vec3 up_ = normalize((viewMatrix * vec4(0., 1., 0., 0.)).xyz); float a_ = dot(normal, up_);   // (the film: the land's slopes drawn steeper in the light, a terrace or a plateau read; buildings keep their seat)
    normal = normalize(a_ * up_ + (normal - a_ * up_) * ${(FILM_PIC.relief).toFixed(2)}); }` : ''}${S && MAT && MAT.base && MAT.base.tex ? `
  { vec3 tb_ = normalize(vec3(slateN_.x, slateN_.z, -slateN_.y) * vec3(${MAT.base.bump.toFixed(2)}, 1., ${MAT.base.bump.toFixed(2)}));   // (the slate's cleft, its tangent space laid on the plate: x east, y north)
    vec3 up_ = normalize((viewMatrix * vec4(0., 1., 0., 0.)).xyz), ex_ = normalize((viewMatrix * vec4(1., 0., 0., 0.)).xyz), ez_ = normalize((viewMatrix * vec4(0., 0., 1., 0.)).xyz);
    normal = normalize(mix(normal, normalize(normal + ex_ * tb_.x + ez_ * tb_.z), 1. - wMask));${todayL() && todayL().water && todayL().water.ripple ? `
    float tw_ = wMask * ${TS_GLSL()};   // today's water: small ripples, the sun sparkling on them (todayLight water ripple), gone where a pixel spans them
    if (tw_ > .01) { vec2 q_ = m_ / 7.; float e_ = .3, fd_ = 1. - smoothstep(.4, 1.5, length(fwidth(q_)));
      float n0_ = fxLn(q_) + .5 * fxLn(q_ * 2.3 + 7.1), nx_ = fxLn(q_ + vec2(e_, 0.)) + .5 * fxLn((q_ + vec2(e_, 0.)) * 2.3 + 7.1) - n0_, nz_ = fxLn(q_ + vec2(0., e_)) + .5 * fxLn((q_ + vec2(0., e_)) * 2.3 + 7.1) - n0_;
      normal = normalize(normal - (ex_ * nx_ + ez_ * nz_) / e_ * ${todayL().water.ripple.toFixed(2)} * tw_ * fd_); }` : ''} }` : ''}`)
      .replace('#include <lights_fragment_end>', `#include <lights_fragment_end>${S && MAT && MAT.base && MAT.base.tex && todayL() && todayL().groundFill ? `
  { float gk_ = (1. - wMask) * ${TS_GLSL()}; vec3 id_ = reflectedLight.indirectDiffuse;   // (todayLight groundFill: today's ground's sky light [the share of its blue kept, times, a lawn's times, [the same beyond today's city]]: its cast shadows a soft neutral grey, light as the painting's, the walls' shade still cool)
    float gn_ = smoothstep(.02, .06, diffuseColor.g - max(diffuseColor.r, diffuseColor.b));   // (a lawn keeps its own fill, groundFill[2]: lifted with the paving it washed pale)
    ${(G_ => `float gs_ = mix(${G_[3][0].toFixed(2)}, ${G_[0].toFixed(2)}, todayG_), gt_ = mix(${G_[3][1].toFixed(2)}, mix(${G_[1].toFixed(2)}, ${(G_[2] ?? G_[1]).toFixed(2)}, gn_), todayG_);   // (groundFill[3]: [share, times] for the land beyond today's city: the countryside and a period city's ground as they were)
    reflectedLight.indirectDiffuse = mix(id_, mix(vec3(dot(id_, vec3(.2126, .7152, .0722))), id_, gs_) * gt_, gk_); }`)(todayL().groundFill.length > 3 ? todayL().groundFill : [...todayL().groundFill.slice(0, 3), todayL().groundFill.slice(0, 2)])}` : ''}`)
      .replace('#include <opaque_fragment>', `${relief ? 'outgoingLight = mix(outgoingLight, fxReliefLight(vFxW, outgoingLight, diffuseColor.rgb), 1. - wMask);   // the relief (fx.js)\n' : ''}${S && MAT && MAT.base && MAT.base.gloss ? `{ float cv_ = max(normalize(cameraPosition - vFxW).y, 0.);   // the resin's gloss: the room and its sky reflected, more as the view grazes it
    outgoingLight = mix(outgoingLight, pow(vec3(${MAT.base.gloss[2].map(x => x.toFixed(3)).join(', ')}), vec3(2.2)), wMask * (${MAT.base.gloss[0].toFixed(2)} + ${MAT.base.gloss[1].toFixed(2)} * pow(1. - cv_, 3.))${todayL() && todayL().water ? ` * (1. - ${TS_GLSL()})` : ''});${todayL() && todayL().water ? (G_ => `
    float tw_ = ${TS_GLSL()};   // (today's water: its own gloss, the sky in it)
    outgoingLight = mix(outgoingLight, pow(vec3(${G_[2].map(x => x.toFixed(3)).join(', ')}), vec3(2.2)), wMask * tw_ * (${G_[0].toFixed(2)} + ${G_[1].toFixed(2)} * pow(1. - cv_, 3.)));
    if (uReflK > 0. && wMask * tw_ > .01) { vec4 rc_ = uReflM * vec4(vFxW, 1.); vec2 ru_ = rc_.xy / rc_.w + (vec2(fxLn(m_ / 5.), fxLn(m_ / 5. + 3.7)) - .5) * vec2(.006, .014);   // (the banks and towers mirrored, broken by the ripples, in the water's own hue: the sky's blue in it turns turquoise)
      // the reflected scene in its own colours, softened and a shade darker, never brighter than the water round it (no bright
      // bars where a pale wall is mirrored); faded out toward the edges of the reflection's picture and with distance, where its
      // picture holds nothing reliable (no patches cut off)
      vec3 rf_ = mix(vec3(dot(texture2D(uRefl, ru_).rgb, vec3(.2126, .7152, .0722))), texture2D(uRefl, ru_).rgb, .7) * .78;
      float lw_ = dot(outgoingLight, vec3(.2126, .7152, .0722)), lr_ = dot(rf_, vec3(.2126, .7152, .0722)); rf_ *= min(1., lw_ / max(lr_, 1e-4));
      vec2 eu_ = min(ru_, 1. - ru_); float fe_ = smoothstep(0., .08, min(eu_.x, eu_.y)) * (1. - smoothstep(uReflD.x, uReflD.y, length(cameraPosition - vFxW)));
      outgoingLight = mix(outgoingLight, rf_, fe_ * wMask * tw_ * uReflK * (${(todayL().water.refl || [0, 0])[0].toFixed(2)} + ${(todayL().water.refl || [0, 0])[1].toFixed(2)} * pow(1. - cv_, 2.))); }${todayL().water.sparkle ? `
    if (wMask * tw_ > .01) {   // the sun's sparkle (todayLight water sparkle: [everywhere, toward the sun, the glints' threshold away from the sun and on its path: higher, sparser]): glints fixed on the water (world space: steady in a move), more on the path toward the sun, gone where a pixel spans them
      vec3 v_ = normalize(cameraPosition - vFxW), rv_ = reflect(-v_, vec3(0., 1., 0.)); float pth_ = pow(max(dot(rv_, normalize(uSunDir)), 0.), 6.);
      vec2 q_ = m_ / 2.3; float n_ = fxLn(q_) * fxLn(q_ * 1.7 + 4.1), px_ = length(fwidth(q_)), th_ = mix(${(todayL().water.sparkle[2] ?? .6).toFixed(2)}, ${(todayL().water.sparkle[3] ?? .34).toFixed(2)}, pth_);
      float sp_ = smoothstep(th_, th_ + .06, n_) * (1. - smoothstep(.35, 1.2, px_)) * (${todayL().water.sparkle[0].toFixed(2)} + ${todayL().water.sparkle[1].toFixed(2)} * pth_);
      outgoingLight += uSunCol * sp_ * wMask * tw_; }` : ''}`)(todayL().water.gloss) : ''} }
` : ''}#include <opaque_fragment>`);
  };
  m.customProgramCacheKey = () => 'mini-land' + (relief ? ' fx' : '') + (o ? ' land' : '') + (S ? ' film' : '') + (then ? ' then' : '') + (far ? ' far' : '') + (fu ? ' pall' : '') + (town ? ' town' : '') + (o && o.meadow ? ' meadow' : '') + (o && o.garden ? ' garden' : '');
  if (S && !far) { const own = m.onBeforeCompile; S.deformMaterial(m, { uPlateTop: { value: 1 } }); const d = m.onBeforeCompile; m.onBeforeCompile = sh => { d(sh); own(sh); }; }   // (a dug pool lowers it)
  return m;
}

// the colour film's marks: an area the story names (an epoch, compile's layer maps: a bombed district, a burnt zone) laid over the
// land in its colour and its glowing edge, as clearly as the white film shows it (its buildings take the colour too: filmMaterial)
function marksMesh(S, plate) {
  const U = S.U, E = S.marksN(), uniforms = {}; for (const k of ['uEpA', 'uEpB', 'uEpR', 'uEpRim', 'uEpW', 'uEpC', 'cEp', 'uL1', 'uL2', 'uL3', 'uPlate']) uniforms[k] = U[k];
  const mat = new THREE.ShaderMaterial({ uniforms, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `// (look: mini)
${S.marksGLSL()}
varying vec3 vW;
void main(){ vec2 uv = vW.xz / uPlate + .5; vec3 c = vec3(0.); float a = 0.;
  for (int i = 0; i < ${E}; i++) { if (uEpA[i] <= 0.) continue; float m = layerAt(uv, i);
    float rv = smoothstep(.08, -.08, length(vW.xz - uEpC[i]) - uEpR[i]);
    float w = clamp(uEpA[i] * m * rv * .55 * uEpW[i], 0., .75), rim = clamp((abs(dFdx(m)) + abs(dFdy(m))) * 14. * uEpRim[i], 0., 1.) * uEpA[i] * rv * .9;
    c = c * (1. - w) + cEp[i] * w; a = a * (1. - w) + w; c += cEp[i] * rim; a = min(1., a + rim * (1. - a)); }
  if (a < .003) discard; gl_FragColor = vec4(c, a); }` });
  const mesh = new THREE.Mesh(plate.geometry, mat); mesh.layers.set(L); mesh.renderOrder = .7; mesh.frustumCulled = false; S.scene.add(mesh);
  return mesh;
}

// the colour film's land seen from afar (landMaterial S): the palette's grass, woods and earth in soft areas a kilometre or two
// wide, a little structure inside them, no grain (the fields' patchwork read from afar as rags sewn together, a finer noise as
// smudged felt, one even tone as a featureless smear)
function farLandGLSL(p, o = null) {
  const v3 = a => `vec3(${a.map(x => x.toFixed(3)).join(', ')})`;
  if (o && o.meadow) return `
vec3 fxLandFar(vec2 m_){ float n1 = fxLn(m_ / 2300.), n2 = fxLn(m_ / 610. + 3.1);   // (the colour film's meadow, as fxLand draws it close, its grain averaged out: the same woods in the same places)
  vec3 land = mix(mix(${v3(p.grass0)}, ${v3(p.grass1)}, n2), mix(${v3(p.soil)}, ${v3(p.straw)}, .35), smoothstep(.2, .9, n1) * ${(o.earth ?? .5).toFixed(3)});
  land = mix(land, ${v3(p.wood)}, smoothstep(.6, .655, fxMeadowWoods(m_)) * .75);
  return pow(land, vec3(2.2)); }`;
  return `
vec3 fxLandFar(vec2 m){ float a = fxLn(m / 2400.), b = fxLn(m / 900. + 3.1), c = fxLn(m / 380. + 7.7), t = a * .55 + b * .3 + c * .15;
  vec3 col = mix(${v3(p.grass0)}, ${v3(p.grass1)}, smoothstep(.35, .65, t));
  col = mix(col, ${v3(p.wood)}, smoothstep(.62, .78, b) * .4);                          // (darker areas: copses, orchards)
  col = mix(col, mix(${v3(p.straw)}, ${v3(p.soil)}, .4), smoothstep(.62, .82, a) * .4);   // (drier ones)
  return pow(col * (.93 + .14 * c), vec3(2.2)); }`;   // (a little structure inside each)
}

// the colour film's land to the horizon (no cliff at the land's edge against the sky): rings of land out from the edge of the plate,
// or of the land beyond it (ctx: its relief, studio.js addContext), at the heights along that edge, levelling to their mean
// outward, in the far land's material
function skirtMesh(S, mat, ctx = null) {
  let x0 = -S.PW / 2, x1 = S.PW / 2, z0 = -S.PD / 2, z1 = S.PD / 2, height = (x, z) => S.ground(x, z);
  if (ctx) { const P = ctx.geometry.attributes.position, bb = (ctx.geometry.computeBoundingBox(), ctx.geometry.boundingBox), e = 1e-6, rim = [];
    ({ x: x0, z: z0 } = bb.min); ({ x: x1, z: z1 } = bb.max);
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), z = P.getZ(i); if (x - x0 < e || x1 - x < e || z - z0 < e || z1 - z < e) rim.push([x, z, P.getY(i)]); }
    height = (x, z) => { let b = rim[0], bd = Infinity; for (const r of rim) { const d = (r[0] - x) ** 2 + (r[1] - z) ** 2; if (d < bd) { bd = d; b = r; } } return b[2]; }; }
  const PW = x1 - x0, PD = z1 - z0, cx = (x0 + x1) / 2, cz = (z0 + z1) / 2, N = 128, ring = [0, .004, .02, .06, .15, .35, .8, 2, 5], edge = [];
  for (let i = 0; i < 4 * N; i++) { const side = Math.floor(i / N), f = i / N - side;
    const [x, z] = side === 0 ? [-PW / 2 + f * PW, -PD / 2] : side === 1 ? [PW / 2, -PD / 2 + f * PD] : side === 2 ? [PW / 2 - f * PW, PD / 2] : [-PW / 2, PD / 2 - f * PD];
    edge.push([x, z, height(cx + x, cz + z)]); }
  const mean = edge.reduce((a, e) => a + e[2], 0) / edge.length, D = Math.max(PW, PD), M_ = edge.length, pos = [], idx = [];
  ring.forEach(r => { const sx = 1 + 2 * r * D / PW, sz = 1 + 2 * r * D / PD, k = THREE.MathUtils.smoothstep(r, 0, .3);
    for (const [x, z, y] of edge) pos.push(cx + x * sx, THREE.MathUtils.lerp(y, mean, k) - (r > 0 ? .0003 : 0), cz + z * sz); });
  for (let k = 0; k + 1 < ring.length; k++) for (let i = 0; i < M_; i++) { const a = k * M_ + i, b = k * M_ + (i + 1) % M_, c = a + M_, d = b + M_; idx.push(a, b, c, b, d, c); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const mesh = new THREE.Mesh(g, mat); mesh.receiveShadow = true; mesh.frustumCulled = false; mesh.layers.set(L); S.scene.add(mesh);
  return mesh;
}

// the info on screen: the period bottom left, the year big bottom right, the population top right (white, on a soft shade at the foot)
function infoPanel(card) {
  const [year, era, pop] = card.split('|'), el = document.createElement('div');
  const shade = '0 1px 2px rgba(0,0,0,.45), 0 2px 18px rgba(0,0,0,.35)';
  el.innerHTML = `<div style="position:absolute;left:0;right:0;bottom:0;height:260px;background:linear-gradient(to top,rgba(20,16,10,.38),rgba(20,16,10,0))"></div>
<div style="position:absolute;left:72px;bottom:58px;font:500 42px/1.3 'Noto Sans TC',sans-serif;text-shadow:${shade}"><div style="width:56px;height:3px;background:#f3e3c0;margin-bottom:16px"></div>${era || ''}</div>
<div style="position:absolute;right:72px;bottom:46px;font:600 100px/1 'Noto Serif TC',serif;letter-spacing:.01em;text-shadow:${shade}">${year || ''}</div>
${pop ? `<div style="position:absolute;right:72px;top:60px;font:500 34px/1 'Noto Sans TC',sans-serif;text-shadow:${shade};display:flex;align-items:center;gap:14px"><svg width="30" height="30" viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="7" r="4.2"/><path d="M3.5 21c.8-4.6 4.2-7 8.5-7s7.7 2.4 8.5 7z"/></svg>${pop}</div>` : ''}`;
  Object.assign(el.style, { position: 'absolute', inset: '0', color: '#fff', pointerEvents: 'none', zIndex: 50 });
  (document.getElementById('stage') || document.body).appendChild(el);
  return el;
}

// prims: id -> (a promise of) that period city's records, for its detail (none: no detail); hex: id -> that city's height
// exaggeration (city.yaml era `exaggeration`, which film.json does not carry: the generator's default 2)
// face: id -> what that city's walls are faced with where they say (film.json era wall_face), else null
// film: the film's look (main.js; above); lost: id -> (a promise of) that period city's loss per record (film.json era file's lost),
// or null; paletteOf: id -> that period city's palette (its own, else the film's); today: today's city's colours (TODAY; none: an
// old Mediterranean town's); fadeAt: the white film's dimming of today's city at which it is gone in colour (film.era_look dim)
export function miniLook({ S, roads = null, dataDir = null, grow = null, bands = null, cityMesh, scale, lens = null, palette = 'roman', ground = 'land', card = null, prims = null, hex = () => 2, face = () => null, film = false, lost = null,
  paletteOf = () => palette, today = null, fadeAt = .8, phone = false, backdropFrom = 1800, dataFrom = 1e4, camAz = null, paths = null, camPath = null }) {   // (paths: the film's routes drawn as paths on the land, main.js QUIET)   // (camPath(): every place the film's camera looks at, [[x, z, distance], ..], or null for a fixed camera (a still's): today's replacement footprints are chosen round all of them)   // (camAz: the bearing the film's camera mostly looks from, degrees: the sun's is fixed from it)   // (phone: the film on a phone, main.js: no ambient occlusion, a smaller shadow map; the caller leaves the detail out)
  const { scene, camera, renderer, U } = S, PW = S.PW, PD = S.PD;
  const tone = p => { const T0 = film && !S.fx && FILM_PIC.tone[p], M_ = film && !S.fx && MAT && MAT[p], T = T0 || M_ ? { ...(T0 || {}), ...(M_ || {}), parts: { ...((T0 || {}).parts || {}), ...((M_ || {}).parts || {}) } } : null;
    return T ? { ...PALETTES[p], ...T, parts: { ...PALETTES[p].parts, ...T.parts }, detail: { ...PALETTES[p].detail, ...(T.detail || {}) } } : PALETTES[p]; };   // (the film's colours, FILM_PIC; a material's over them)   // (the film's colours, FILM_PIC)
  const TONED = Object.fromEntries(Object.keys(PALETTES).map(k => [k, tone(k)]));
  const pal = TONED[palette] || TONED.roman, palOf = id => TONED[paletteOf(id)] || pal;
  // the meshes this look draws: the period cities, today's city, the plate
  const eraMeshes = Object.values(S.eras).map(e => e.mesh);
  let plate = null;
  scene.traverse(o => { if (o.isMesh && o.material && o.material.customProgramCacheKey && /^proj1/.test(o.material.customProgramCacheKey()) && o.geometry.attributes.position.count > 1000) plate = o; });
  const FX = S.fx, relief = !!(FX && FX.relief && U.uFxRA && U.uFxRA.value);   // the effects (fx.js), as the studio has them
  // the film's own uniforms: when the modern section begins and the data's earliest epoch (filmMaterial), the pall of a burning
  // city's smoke shading the ground beneath it (its centre, reach and strength: render)
  const BACK = { uBackdropY: { value: backdropFrom }, uDataY0: { value: dataFrom }, uPallC: { value: new THREE.Vector2() }, uPallR: { value: 1 }, uPallK: { value: 0 } };
  const landName = Object.keys(LAND_PALETTES).find(k => LAND_PALETTES[k] === pal.land), LT = film && !S.fx && FILM_PIC.landTone[landName];
  const LANDO = FX && FX.land ? FX.land : film ? { ...FILM_PIC.land, toned: !!LT, garden: !!FILM_PIC.garden[palette] } : null;   // (the film: a meadow and woods, not the palette's patchwork of fields)
  const LANDP = FX && FX.land ? landPalette(FX.land) : LT || pal.land;
  if (plate) plate.userData.mini = landMaterial(U, PW, PD, ground, LANDP, relief, LANDO, S.terrainEx, scale, film ? S : null, false, BACK);
  U.__ground = S.ground;
  // the film: the ruins' uniforms (filmMaterial; main.js sets their values each frame), the land beyond the plate (its context relief,
  // else a skirt of land to the horizon), the light the studio lays on the plate (S.colourLight: more of it at night)
  const RUIN_T = { value: Array(S.slots).fill(-1) };
  if (film) for (const [id, E] of Object.entries(S.eras)) Object.assign(E.u, { uRuinLater: { value: Array(S.slots).fill(0) }, uRuinT: RUIN_T, uRuinH: { value: 1.4 * hex(id) * scale },
    uLossBurnt: { value: Array(E.u.uLossBurn.value.length).fill(0) } });
  if (film) S.colourGround.value.set(pal.parts[7]);
  if (film && MAT && MAT.base && MAT.base.ground) S.colourGround.value.set(MAT.base.ground);   // (a material's plate: open ground as near the plate as its flat colour can be)   // (a city's open ground in its paving's colour: studio.js lightMaterial ground)
  const far = film ? landMaterial(U, PW, PD, 'land', LANDP, false, LANDO, S.terrainEx, scale, S, true, BACK) : null;
  const ctx = film ? S.context() : null, skirt = film ? skirtMesh(S, far, ctx) : null, marks = film && plate ? marksMesh(S, plate) : null;
  // the film's routes as paths drawn on the land (main.js QUIET): a ribbon along each route's course on the ground, drawn from its
  // start as the route draws and faded out with it, in the route's colour mixed with an earth (a route the water as it was comes
  // with is that water, and main.js leaves it out)
  const sm = (a, b, x) => THREE.MathUtils.smoothstep(x, a, b);
  const PATHS = film && paths && paths.length ? paths.map(r => {
    const raw = r.pts.map(p => [p[0], p[2]]), pts = [raw[0]], step = 40 * scale;
    for (let i = 1; i < raw.length; i++) { const [a, b] = [raw[i - 1], raw[i]], n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step));
      for (let k = 1; k <= n; k++) pts.push([a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n]); }
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    const Lt = cum[cum.length - 1] || 1, w = FILM_PIC.pathW * scale / 2, pos = [], al = [], idx = [];
    pts.forEach(([x, z], i) => { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)], dx = b[0] - a[0], dz = b[1] - a[1], l = Math.hypot(dx, dz) || 1;
      for (const sg of [-1, 1]) { const X = x - dz / l * w * sg, Z = z + dx / l * w * sg; pos.push(X, S.ground(X, Z) + 1.5 * scale, Z); al.push(cum[i] / Lt); } });
    for (let i = 0; i + 1 < pts.length; i++) { const a = i * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aAlong', new THREE.Float32BufferAttribute(al, 1)); g.setIndex(idx); g.computeVertexNormals();
    const u = { uP: { value: 0 } }, mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(r.col || '#ffffff').lerp(new THREE.Color(FILM_PIC.pathC), .6), roughness: 1, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
    mat.onBeforeCompile = sh => { sh.uniforms.uP = u.uP;
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float aAlong; varying float vAlong;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvAlong = aAlong;');
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform float uP; varying float vAlong;').replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\n  if (vAlong > uP) discard;'); };
    mat.customProgramCacheKey = () => 'mini-path';
    const mesh = new THREE.Mesh(g, mat); mesh.layers.set(L); mesh.receiveShadow = true; mesh.frustumCulled = false; mesh.visible = false; mesh.renderOrder = .6; scene.add(mesh);
    return { r, mesh, u };
  }) : [];
  // the land's woods where trees stand close (fx land: fx.js woodsFn)
  const woods = LANDO ? woodsFn(LANDO, S.terrainEx, scale, S.ground, relief) : null;
  // the light of a clear day: the sun to one side behind the eye, 40 degrees up, soft shadows; the sky's blue from above, the land's from below
  // (fx light: a lower, warmer sun, as in the late afternoon, as bright on flat ground as the higher one; the sky's light a little bluer)
  const warm = FX && FX.light ? FX.light.warm : 0, SUN_EL = film && !(FX && FX.light) ? FILM_PIC.sunEl : THREE.MathUtils.lerp(40, 28, warm), SUN_SIDE = relief ? 95 : 55;   // (fx relief: the sun more to the side, so the slopes facing the eye show light and shade)
  const FP_ = film && !FX;   // (the film's own picture, FILM_PIC; with the effects, theirs)
  const sun = new THREE.DirectionalLight(new THREE.Color(FP_ ? FILM_PIC.sunC : '#ffeed4').lerp(new THREE.Color('#ffd09a'), warm), 2.7 * (FX ? MINI_LIFT.sun : FP_ ? FILM_PIC.sun : 1) * Math.sin(THREE.MathUtils.degToRad(40)) / Math.sin(THREE.MathUtils.degToRad(SUN_EL))), sky = new THREE.HemisphereLight(new THREE.Color(FP_ ? FILM_PIC.skyC : '#c3d8ee').lerp(new THREE.Color('#a9c4ea'), warm), FP_ ? FILM_PIC.skyGround : '#6b7550', .9 * (FX ? MINI_LIFT.sky : FP_ ? FILM_PIC.sky : 1));
  sun.castShadow = true; sun.shadow.mapSize.set(phone ? 2048 : 4096, phone ? 2048 : 4096); sun.shadow.bias = -.0004; sun.shadow.normalBias = .00002; sun.shadow.radius = FP_ ? 1 : 2;
  for (const o of [sun, sun.target, sky]) { o.layers.set(L); scene.add(o); }
  // a model photographer's softbox (todayLight soft: [its intensity, its elevation in degrees]): from the camera's side, low, no
  // shadow; it lifts the walls toward the lens and barely the board; the sun keeps the shadows' direction
  const soft = film && MAT && MAT.todayLight ? new THREE.DirectionalLight('#f4f6fa', 0) : null; if (soft) for (const o of [soft, soft.target]) { o.layers.set(L); scene.add(o); }
  const bg = new THREE.Color('#c4d8ea'), fog = new THREE.Fog('#cfdde8', 1, 3), FOG = fog.color.clone(), SUN0 = sun.intensity, SKY0 = sky.intensity;
  const NIGHT = { bg: new THREE.Color('#16223a'), fog: new THREE.Color('#1c2a44'), sun: new THREE.Color('#9fb4e0') }, SUNC = sun.color.clone(), bgNow = bg.clone();   // (the film at night: film.night)
  const PALL = { sun: new THREE.Color('#ffb070'), sky: new THREE.Color('#8f8273') };   // (under a burning city's smoke)
  const landmarks = [], FOOTS = [];   // detailed models drawn in place of the generator's (swap); FOOTS: today's ones' footprints, no tree planted in them
  // each period city's detail (engine/detail.js), made the first time it is shown: era id -> a promise of its group
  const DET = prims ? new Map() : null;
  const colsOf = pal => {   // the detail's colours in a palette
    const dcols = { ...(pal.detail || PALETTES.roman.detail), hallroof: (x, z) => roofOf(pal, x, z).multiplyScalar(.93), eaveslab: (x, z) => roofOf(pal, x, z).multiplyScalar(.93),
      hip: (x, z) => roofOf(pal, x, z), gableZ: (x, z) => roofOf(pal, x, z), lean: (x, z) => roofOf(pal, x, z).multiplyScalar(.96), pent: (x, z) => roofOf(pal, x, z).multiplyScalar(.9),
      upper: (x, z) => new THREE.Color(pal.walls[Math.floor(hash(x * 3.7, z * 1.3) * pal.walls.length) % pal.walls.length]), tile: (x, z) => roofOf(pal, x, z).multiplyScalar(FLAT.tile), verge: (x, z) => roofOf(pal, x, z).multiplyScalar(FLAT.verge),
      eave: (x, z) => roofOf(pal, x, z), ridge: (pal.detail || {}).ridge || '#9a9da0' };   // (the eaves in the roof's own tile; the ridge a lighter grey)   // (a roof's tiles in its own colour, lighter, its gable ridges darker: detail.js FLAT)
    for (const [f, v] of Object.entries(pal.faces || PALETTES.roman.faces)) {   // (a wall's face: its courses a shade darker, a stone wall's bands brick; a gate's parts the wall's)
      dcols['course_' + f] = f === 'banded' ? (pal.faces || PALETTES.roman.faces).brick : new THREE.Color(v).multiplyScalar(FLAT.course);
      dcols['spandrel_' + f] = dcols['parapet_' + f] = dcols['merlon_' + f] = v; }
    // the town's trees as the land's (fx.js plantTrees' colours), flags in the palette's colours (one or the other by the flag's
    // building), the boats' wood, sails and mat roofs
    const tdark = (pal.tree && pal.tree.dark) || 1, H3 = (x, z) => { const h = hash(x, z); return [h, (h * 7.31) % 1, (h * 13.7) % 1]; }, D_ = pal.detail || PALETTES.roman.detail;
    const th = film ? FILM_PIC.tree.hue : 0;   // (the film's greens a little bluer: FILM_PIC)
    const tsat = (pal.tree && pal.tree.sat) || 1;   // (a palette's town trees this much as saturated: a model's painted foliage, not a lawn's)
    Object.assign(dcols, { crown: (x, z) => { const [a, b, c] = H3(x, z); return new THREE.Color().setHSL(.2 + th + a * .09, (.32 + b * .16) * tsat, (.24 + c * .1) * tdark); },
      cone: (x, z) => { const [a, , c] = H3(x, z); return new THREE.Color().setHSL(.27 + th + a * .05, .4, (.18 + c * .06) * tdark); }, trunk: '#6b5440', pole: '#5b4a3a',
      flag: (x, z) => new THREE.Color(D_.flags[Math.floor(H3(x, z)[1] * D_.flags.length)]), hull: '#7a5236', mast: '#5b4a3a', sail: D_.sail, cabin: '#4a4038' });
    if (pal.flags === false) { delete dcols.flag; delete dcols.pole; }   // (a material without the painted flags)
    return dcols; };
  const dcols = colsOf(pal), DCOLS = new Map([[pal, dcols]]), dcolsOf = p => DCOLS.get(p) || DCOLS.set(p, colsOf(p)).get(p);
  const pxK = { value: 1 }, idOf = new Map(Object.entries(S.eras).map(([id, E]) => [E.mesh, id])), uprightOf = id => (STYLES[paletteOf(id)] || STYLES[palette] || STYLES.roman).wall;   // (the fade's scale: detail.js FADE_PX)
  // (the film: each piece rises and falls with its building, and burns away as its building chars: filmMaterial)
  const riseOf = async id => { if (!film) return null; const lo = lost ? await lost(id) : null, u = S.eras[id].u, nL = u.uLossBurn.value.length, fire = S.fires[id] && S.fires[id].day ? S.fires[id] : null;
    const glsl = S.eraRiseGLSL().replace('float eraRiseK(){', 'float eraRiseK0(){') + `
  uniform float uNow, uEraBurn, uLossBurn[${nL}];${fire ? ' uniform vec2 uO;' + S.fireGLSL : ''}
  float eraRiseK(){ float c = uEraBurn; for (int k = 0; k < ${nL}; k++) if (abs(iW - 4. - float(k)) < .5) c = max(c, uLossBurn[k]);${fire ? '\n    if (uEraBurn > 0.) c = smoothstep(.3, 2., uNow - ign(iCtr, fireHash(iCtr)));' : ''}
    return eraRiseK0() * (1. - c); }`;
    return { glsl, uniforms: { ...u, uHScale: HSCALE, uNow: U.uNow, ...(fire ? { ...fire.day.F, uO: fire.u.uO } : {}) }, w: lo ? Float32Array.from(lo, v => 3 + v) : null }; };
  const detailOf = async id => { const D = eraDetail(await prims(id), { scale, hex: hex(id), style: paletteOf(id), face: face(id), tiles: film && MAT && MAT.tiles || 1, tufts: !!(film && MAT && MAT.tufts) }), g = detailMeshes(D, dcolsOf(palOf(id)), { layer: L, pxK, rise: await riseOf(id), shadowAlso: film && MAT && MAT.tiles > 1 ? ['tile', 'verge'] : null });
    g.userData.count = D.count; g.userData.treeOK = D.treeOK; scene.add(g); return g; };
  // where trees may stand: off every shown city's wall bands and gate approaches (detail.js eraDetail treeOK)
  let clearNow = [];
  const TF = treeField(scene, renderer, U, PW, PD, scale, { size: 1, keep: 1, dark: 1, ...pal.tree, ...(film ? FILM_PIC.tree : {}), ...(film && phone ? { count: 40000 } : {}), cypress: pal.cypress, woods, ground: S.ground, layer: L, tone: 'mini',
    clear: (x, z) => clearNow.every(f => f(x, z)) });
  // boats on the water (detail.js boatsAt): the whole plate's, planted in the world once (again when the water as it was changes),
  // the same wherever the camera goes; a far one fades by its size (detailMeshes)
  let wpx = null; const water = () => { if (wpx) return wpx; const img = U.uWater.value && U.uWater.value.image; if (!img) return null;
    const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height; const g = cv.getContext('2d'); g.drawImage(img, 0, 0); return wpx = { d: g.getImageData(0, 0, img.width, img.height).data, w: img.width, h: img.height }; };
  const chan = () => film && S.wThenGLSL ? Math.round(U.uWT.value.x) : 0;   // (the film's water as it was: the state's channel, studio.js WTHEN; else today's, R)
  const wet = (x, z) => { const W_ = water(); if (!W_) return false; const u = Math.floor((x / PW + .5) * W_.w), v = Math.floor((z / PD + .5) * W_.h); return u >= 0 && v >= 0 && u < W_.w && v < W_.h && W_.d[(v * W_.w + u) * 4 + chan()] > 90; };
  const BF = { g: null, ch: null };
  const boats = () => { if (BF.g && BF.ch === chan()) return; BF.ch = chan();
    if (BF.g) { scene.remove(BF.g); BF.g.traverse(o => { if (o.isMesh) { o.geometry.dispose(); o.material.dispose(); } }); }
    BF.g = detailMeshes(boatsAt(wet, -PW / 2, -PD / 2, PW / 2, PD / 2, { scale, style: palette, ground: S.ground }), dcols, { layer: L, pxK }); scene.add(BF.g); };
  // a material's groves (base flock): round crowns, a cell of `cell` m, the same near and afar (a cell grown with the distance would
  // thin the crowns where they are still seen as the camera moves; col2 a second green by grove), there by the groves' density: the generator's
  // trees (its mask), the banks, the steep slopes, the open ground at the city's edge and a few in the country; never in the built blocks.
  // Every tree (the groves; today's street and park trees, flockAt) is planted in the world, never round the eye, so nothing jumps or
  // pops as the camera moves: the plate in tiles of TILE m, each tile's trees made once, as far down their ranks as a frame has
  // needed them (a grove's or a park's tree a rank at random, a street's by its place in its row: every other one first), made again
  // only where what decides them changes (the year, today's city standing, the period cities standing, a detailed model, the water
  // as it was). Each frame draws the trees of the tiles it sees, each by its own distance from the eye: a crown drawn smaller than
  // `px` pixels round stands for several, fewer and larger, the canopy's share kept (a street's: its crowns at least street.px
  // pixels round, every other one going as they grow); a tree fades in and out over a band of its rank, never at once; afar a
  // grove whose cell is under far[1] pixels hands over to the ground's own groves' tone (whole by far[0]), a street's crown under
  // street.far[1] of a pixel fades (gone by far[0]). The same camera draws the same trees, whatever frame came before it
  const FL = { tiles: new Map(), key: null, built: undefined, bv: 0, mesh: [], cap: 0, seg: null, out: null }, TILE = 256;
  // the streets (data/streets.json) and arterials (roads) as carriageways and junctions, built once: each segment in a 60 m grid
  // with its half width; the nodes where three or more arms meet. clear(x, z, way, r): off every other way's carriageway (its half
  // width and 1.5 m) and r from every junction
  let SIX = null;
  const streetIndex = () => { if (SIX) return SIX;
    const HW = { motorway: 15, trunk: 13, primary: 11, secondary: 6, tertiary: 4.5, residential: 3, unclassified: 3, living_street: 2.5 }, hw = c => (HW[(c || '').replace('_link', '')] || 3) * scale;
    const cell = 60 * scale, grid = new Map(), arms = new Map(), junc = new Map(), gk = (i, j) => i * 100003 + j;
    const add = (r, w) => { const P = r.pts, h = hw(r.cls); P.forEach(([x, z], k) => { const kk = x.toFixed(6) + ',' + z.toFixed(6); arms.set(kk, (arms.get(kk) || 0) + (k === 0 || k === P.length - 1 ? 1 : 2)); });
      for (let k = 1; k < P.length; k++) { const [ax, az] = P[k - 1], [bx, bz] = P[k], sg = [ax, az, bx, bz, h, w];
        for (let i = Math.floor(Math.min(ax, bx) / cell); i <= Math.floor(Math.max(ax, bx) / cell); i++) for (let j = Math.floor(Math.min(az, bz) / cell); j <= Math.floor(Math.max(az, bz) / cell); j++) { const g = gk(i, j); (grid.get(g) || grid.set(g, []).get(g)).push(sg); } } };
    (STREETS.list || []).forEach((r, w) => add(r, w)); (roads || []).forEach((r, w) => add(r, -1 - w));
    for (const [kk, n] of arms) if (n >= 3) { const [x, z] = kk.split(',').map(Number), g = gk(Math.floor(x / cell), Math.floor(z / cell)); (junc.get(g) || junc.set(g, []).get(g)).push([x, z]); }
    const sd = (x, z, ax, az, bx, bz) => { const dx = bx - ax, dz = bz - az, l2 = dx * dx + dz * dz, t = l2 > 0 ? Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / l2)) : 0; return Math.hypot(x - ax - t * dx, z - az - t * dz); };
    const clear = (x, z, w, r) => { const i0 = Math.floor(x / cell), j0 = Math.floor(z / cell);
      for (let i = i0 - 1; i <= i0 + 1; i++) for (let j = j0 - 1; j <= j0 + 1; j++) { const g = gk(i, j), L_ = grid.get(g), J_ = junc.get(g);
        if (L_) for (const [ax, az, bx, bz, h, ww] of L_) if (ww !== w && sd(x, z, ax, az, bx, bz) < h + 1.5 * scale) return false;
        if (J_) for (const [jx, jz] of J_) if (Math.hypot(x - jx, z - jz) < r) return false; }
      return true; };
    return SIX = { hw, clear }; };
  const flockKey = () => [Math.floor(TODAY_K.value.x), STREET_K.value > 0 ? 1 : 0, FOOTS.length, chan()].join(':');   // (what decides every tile's trees; the period cities standing, BUILT, tile by tile: FL.sums)
  const FH = (i, j, k) => { const t = Math.sin(i * 127.1 + j * 311.7 + k * 74.7) * 43758.5453; return t - Math.floor(t); };
  const fvn = (x, y) => { const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j, a = FH(i, j, 9), b = FH(i + 1, j, 9), c = FH(i, j + 1, 9), e = FH(i + 1, j + 1, 9), sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy); return a + (b - a) * sx + (c - a) * sy + (a - b - c + e) * sx * sy; };
  const fsm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  // one tile's trees down to rank p (T: its record, made the first time it is seen): its groves' cells, its parks' cells, its streets'
  // places, each looked at only once its rank is under p (a far tile needs few); a tree: [x, y, z, r, h, kind (0 a grove's, 1 a
  // park's, 2 a street's), rank]
  const plantTile = (T, p, M) => { const F = M.F, c = F.cell * scale, T0 = TILE * scale, x0 = T.i * T0, z0 = T.j * T0, out = T.list, q0 = T.p;
    if (p <= q0) return; T.p = p;
    const i0 = Math.floor(x0 / c), i1 = Math.floor((x0 + T0) / c), j0 = Math.floor(z0 / c), j1 = Math.floor((z0 + T0) / c);
    for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {   // the groves: a crown a cell of flock cell m, there by the groves' density
      const rk = FH(i, j, 21); if (rk < q0 || rk >= p) continue;
      const x = (i + .2 + .6 * FH(i, j, 1)) * c, z = (j + .2 + .6 * FH(i, j, 2)) * c;
      if (x < x0 || x >= x0 + T0 || z < z0 || z >= z0 + T0 || Math.abs(x) > PW / 2 || Math.abs(z) > PD / 2 || wet(x, z)) continue;
      const tw0 = M.px(M.bd, x, z), tw1 = Math.max(tw0, M.ty(x, z)); if (tw0 > .8) continue;   // (never on a block; today's: tw1, the same grove while today's city is the subject)
      const m = [x / scale, z / scale], cl = fsm(.42, .56, fvn(m[0] / 52, m[1] / 52) * .65 + fvn(m[0] / 17, m[1] / 17) * .35);
      const e = 2 * c, g0 = S.ground(x, z), sl = Math.hypot(S.ground(x + e, z) - g0, S.ground(x, z + e) - g0) / e;
      const bank = (wet(x + 3 * c, z) || wet(x - 3 * c, z) || wet(x, z + 3 * c) || wet(x, z - 3 * c)) ? 1 : 0;
      const kOf = (tw, ty_) => { const k = Math.max(M.px(M.td, x, z) * (.5 + .5 * cl), F.bank * bank * (.55 + .45 * cl), cl * Math.max(F.slope * fsm(.12, .3, sl), F.edge * fsm(.08, .25, tw) * (1 - fsm(.72, .9, tw))), F.land * (1 - .75 * ty_) * fsm(.75, .9, cl) * (1 - fsm(.2, .4, tw)));   // (groves with clearings; the banks lined; in the open country only the heart of a grove)
        return fsm(.3, .62, k) * (1 - fsm(.7, .8, tw)); };   // (a grove's density sharpened: crowns close in its heart, none in its thin edge, so the country reads as woods, not dots)
      const hk = FH(i, j, 3), in0 = hk < kOf(tw0, 0), in1 = tw1 <= .8 && hk < kOf(tw1, M.ycT >= 0 ? 1 : 0); if (!in0 && !in1) continue;
      const tw = in1 ? tw1 : tw0;   // (today's state a grove keeps: its size where today's blocks are near)
      out.push([x, g0, z, Math.min(F.cell * .42 * (.6 + 1. * Math.pow(FH(i, j, 4), 1.4)) * (.8 + .4 * cl), tw > .25 ? 4.5 : 1e9) * scale, FH(i, j, 5), in0 && in1 ? 0 : in0 ? -1 : -2, rk]); }   // (kind 0 a grove's; -1 one only while today's city is not the subject, -2 only while it is: each fades with today's city, STREET_K)   // (inside a town no bigger than a courtyard house)   // (a crown .6 to 1.6 times, the bigger in a grove's heart)
    // a period town's own trees (flock town): its courtyards and lanes planted, where a period city stands (the built-up mask over
    // town.built), where its region plants them (its palette's tree town: a share of town.share), a cell of town.cell m, town.share
    // of them a tree in its leafy quarters (a slow noise passing groves[0], whole by groves[1]; a quarter of that between them), its
    // trunk and `free` of its crown off every roof (townFree: the standing cities' roofs drawn in the tile, 1.5 m a cell), never on a
    // city wall's band or a gate's approach; a crown size[0] to size[1] m round. Any period city's, by its own buildings
    const TW = F.town; if (TW && townPrep(T)) { const c3 = TW.cell * scale, ti0 = Math.floor(x0 / c3), ti1 = Math.floor((x0 + T0) / c3), tj0 = Math.floor(z0 / c3), tj1 = Math.floor((z0 + T0) / c3);
      for (let i = ti0; i <= ti1; i++) for (let j = tj0; j <= tj1; j++) { const rk = FH(i, j, 24); if (rk < q0 || rk >= p) continue;
        const x = (i + .2 + .6 * FH(i, j, 25)) * c3, z = (j + .2 + .6 * FH(i, j, 26)) * c3; if (x < x0 || x >= x0 + T0 || z < z0 || z >= z0 + T0) continue;
        if (M.px(M.bd, x, z) < TW.built) continue;
        const m = [x / scale, z / scale], g = fsm(TW.groves[0], TW.groves[1], fvn(m[0] / 40, m[1] / 40) * .6 + fvn(m[0] / 13 + 5.1, m[1] / 13) * .4);
        const r = (TW.size[0] + (TW.size[1] - TW.size[0]) * FH(i, j, 28)) * scale; if (!townFree(T, x, z, r * (TW.free ?? .8))) continue;   // (free: the share of its crown kept off the roofs: the rest may lean over them)
        if (FH(i, j, 27) >= TW.share * T.townK * (.25 + .75 * g) || wet(x, z) || !clearNow.every(f => f(x, z))) continue;
        out.push([x, S.ground(x, z), z, r, FH(i, j, 29), 0, rk]); } }
    if (M.yc < 0) return;
    // today's street trees (data/streets.json, the finer streets: plane trees along both kerbs, a class's own spacing, sparser along
    // the minor streets): a row's every other tree the first to go afar (its rank by its place), never in a carriageway (any
    // street's or arterial's half width and a little) nor near a junction (a node where three or more arms meet)
    const ST_ = M.ST, IX = M.IX, WC_ = (F.wall || 0) * scale;
    for (const [w, k] of (FL.seg && FL.seg.get(T.i * 100003 + T.j)) || []) { const r = STREETS.list[w], hw = IX.hw(r.cls), off = (hw / scale + ST_.off) * scale, ev = Math.max(ST_.every[r.cls] || ST_.minor, ST_.floor || 0) * scale;   // (floor: no row closer than this)
      const [ax, az] = r.pts[k - 1], [bx, bz] = r.pts[k], L_ = Math.hypot(bx - ax, bz - az), nx = -(bz - az) / L_, nz = (bx - ax) / L_;
      for (let n = 0, u = ev / 2; u < L_; n++, u += ev) { let tz = 0; if (n) while (!((n >> tz) & 1)) tz++; const rk = n ? Math.pow(2, -tz - 1) : 0; if (rk < q0 || rk >= p) continue;   // (n's trailing zeros: 1, 3, 5.. go first, then 2, 6, 10..; the row's first stays)
        for (const sd of [-1, 1]) { const x = ax + (bx - ax) * u / L_ + nx * off * sd, z = az + (bz - az) * u / L_ + nz * off * sd;
          if (x < x0 || x >= x0 + T0 || z < z0 || z >= z0 + T0) continue;
          if (!M.ty(x, z) || wet(x, z) || FOOTS.some(f => f(x, z)) || !IX.clear(x, z, w, ST_.junction * scale)) continue; const hh = FH(Math.floor(z / scale), Math.floor(x / scale), 7);
          const rs = ST_.r * (ST_.vary || [.75, 1, 1.25])[Math.floor(hh * (ST_.vary || [0, 0, 0]).length)] * (.9 + .2 * FH(Math.floor(x / scale), Math.floor(z / scale), 6)) * scale;
          if (WC_ && !walls(x, z, rs + WC_)) continue;
          out.push([x, S.ground(x, z), z, rs, hh, 2, rk]); } } }
    // its parks (data/green.png) as the paintings' are: groves on open lawn (todayLight parkTrees: a crown a cell of `cell` m;
    // groves where a slow noise of `noise` m passes groves[0], whole by groves[1], `dense` of their cells a crown, the larger in a
    // grove's heart; on the open lawn `lone` of the cells; within edge[0] m of a park's edge edge[1], its trees lining it; a crown
    // size[0] to size[1] m round, each with two smaller beside it)
    if (!GREEN_D) return; const PT_ = M.PT, c2 = PT_.cell * scale, gi0 = Math.floor(x0 / c2), gi1 = Math.floor((x0 + T0) / c2), gj0 = Math.floor(z0 / c2), gj1 = Math.floor((z0 + T0) / c2);
    const park = (x, z) => { const u = Math.floor((x / PW + .5) * GREEN_D.w), v = Math.floor((z / PD + .5) * GREEN_D.h); return u >= 0 && v >= 0 && u < GREEN_D.w && v < GREEN_D.h && GREEN_D.d[(v * GREEN_D.w + u) * 4] >= 128; };
    for (let i = gi0; i <= gi1; i++) for (let j = gj0; j <= gj1; j++) { const rk = FH(i, j, 22); if (rk < q0 || rk >= p) continue;
      const x = (i + .2 + .6 * FH(i, j, 11)) * c2, z = (j + .2 + .6 * FH(i, j, 12)) * c2; if (x < x0 || x >= x0 + T0 || z < z0 || z >= z0 + T0 || !park(x, z)) continue;
      const m = [x / scale, z / scale], N_ = PT_.noise, gv = fsm(PT_.groves[0], PT_.groves[1], fvn(m[0] / N_[0], m[1] / N_[0]) * .65 + fvn(m[0] / N_[1] + 17.3, m[1] / N_[1]) * .35);
      const e = PT_.edge[0] * scale, rim = !park(x + e, z) || !park(x - e, z) || !park(x, z + e) || !park(x, z - e);
      if (FH(i, j, 13) >= Math.max(PT_.dense * gv, PT_.lone, rim ? PT_.edge[1] : 0) || !M.ty(x, z) || wet(x, z) || FOOTS.some(f => f(x, z))) continue;
      const rp = (PT_.size[0] + (PT_.size[1] - PT_.size[0]) * FH(i, j, 14) * (.55 + .45 * gv)) * scale;
      if (WC_ && !walls(x, z, rp * 1.6 + WC_)) continue;   // (its cluster's reach)
      out.push([x, S.ground(x, z), z, rp, FH(i, j, 15), 1, rk]); }
  };
  // the period cities' roofs by tile (each era mesh's roof and top triangles of its buildings, parts 0 1 8 9, in every tile they
  // touch), made once a mesh; townFree(T, x, z, r): no roof of a standing city at x z or r round it, from the tile's own raster
  // (its roofs drawn at 1.5 m, made when a town tree first asks, again with the tile)
  const ROOF_IX = new WeakMap();
  const roofIndex = m => { let ix = ROOF_IX.get(m.geometry); if (ix) return ix; ix = new Map(); ROOF_IX.set(m.geometry, ix);
    const g = m.geometry, P = g.attributes.position, N = g.attributes.normal, D = g.attributes.aData, I = g.index, n = I ? I.count : P.count, T0 = TILE * scale; if (!D || !N) return ix;
    for (let t = 0; t + 2 < n; t += 3) { const a = I ? I.getX(t) : t, b = I ? I.getX(t + 1) : t + 1, c = I ? I.getX(t + 2) : t + 2, pt = Math.round(D.getY(a));
      if (!(pt === 0 || pt === 1 || pt === 8 || pt === 9) || N.getY(a) + N.getY(b) + N.getY(c) < .6) continue;
      const xs = [P.getX(a), P.getX(b), P.getX(c)], zs = [P.getZ(a), P.getZ(b), P.getZ(c)];
      for (let i = Math.floor(Math.min(...xs) / T0); i <= Math.floor(Math.max(...xs) / T0); i++) for (let j = Math.floor(Math.min(...zs) / T0); j <= Math.floor(Math.max(...zs) / T0); j++) {
        const k = i * 100003 + j; (ix.get(k) || ix.set(k, []).get(k)).push(xs[0], zs[0], xs[1], zs[1], xs[2], zs[2]); } }
    return ix; };
  // townPrep(T): the share of town trees the tile's standing cities plant (their palettes' tree town, the largest), and their roofs
  // drawn, only where it is above 0 (a city that plants none, Rome's, costs nothing as it rises and falls)
  const townPrep = T => { if (T.townK !== undefined) return T.townK; const k = T.i * 100003 + T.j; T.townK = 0;
    for (const m of eraMeshes) { const t_ = m.visible ? (palOf(idOf.get(m)).tree || {}).town || 0 : 0; if (t_ > T.townK && roofIndex(m).get(k)) T.townK = t_; }
    return T.townK; };
  const townFree = (T, x, z, r) => { const T0 = TILE * scale, cs = 1.5 * scale, NC = Math.ceil(TILE / 1.5), x0 = T.i * T0, z0 = T.j * T0;
    if (!T.occ) { const o = T.occ = new Uint8Array(NC * NC), k = T.i * 100003 + T.j;
      for (const m of eraMeshes) { if (!m.visible) continue; const L_ = roofIndex(m).get(k); if (!L_) continue;
        for (let q = 0; q < L_.length; q += 6) { const ax = L_[q], az = L_[q + 1], bx = L_[q + 2], bz = L_[q + 3], cx = L_[q + 4], cz = L_[q + 5], d_ = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz); if (Math.abs(d_) < 1e-20) continue;
          const u0 = Math.max(0, Math.floor((Math.min(ax, bx, cx) - x0) / cs)), u1 = Math.min(NC - 1, Math.floor((Math.max(ax, bx, cx) - x0) / cs)), v0 = Math.max(0, Math.floor((Math.min(az, bz, cz) - z0) / cs)), v1 = Math.min(NC - 1, Math.floor((Math.max(az, bz, cz) - z0) / cs));
          for (let v = v0; v <= v1; v++) for (let u = u0; u <= u1; u++) { const px_ = x0 + (u + .5) * cs, pz_ = z0 + (v + .5) * cs, l1 = ((bz - cz) * (px_ - cx) + (cx - bx) * (pz_ - cz)) / d_, l2 = ((cz - az) * (px_ - cx) + (ax - cx) * (pz_ - cz)) / d_;
            if (l1 >= -.05 && l2 >= -.05 && l1 + l2 <= 1.05) o[v * NC + u] = 1; } } } }
    for (let a = 0; a < 9; a++) { const sx = a ? x + Math.cos(a * Math.PI / 4) * r : x, sz = a ? z + Math.sin(a * Math.PI / 4) * r : z, u = Math.floor((sx - x0) / cs), v = Math.floor((sz - z0) / cs);
      if (u >= 0 && v >= 0 && u < NC && v < NC && T.occ[v * NC + u]) return false; }
    return true; };
  // the street index by tile (each street segment in every tile its trees may stand in), made once
  const segIndex = () => { if (FL.seg) return FL.seg; const T0 = TILE * scale, m = new Map(), IX = streetIndex();
    (STREETS.list || []).forEach((r, w) => { const e = (IX.hw(r.cls) / scale + 12) * scale;
      for (let k = 1; k < r.pts.length; k++) { const [ax, az] = r.pts[k - 1], [bx, bz] = r.pts[k]; if (Math.hypot(bx - ax, bz - az) < 1e-9) continue;
        for (let i = Math.floor((Math.min(ax, bx) - e) / T0); i <= Math.floor((Math.max(ax, bx) + e) / T0); i++) for (let j = Math.floor((Math.min(az, bz) - e) / T0); j <= Math.floor((Math.max(az, bz) + e) / T0); j++) {
          const g = i * 100003 + j; (m.get(g) || m.set(g, []).get(g)).push([w, k]); } } });
    return FL.seg = m; };
  const FR = { fr: new THREE.Frustum(), pm: new THREE.Matrix4(), box: new THREE.Box3(), ray: new THREE.Vector3(), cp: new THREE.Vector3() };
  const flockAt = (target, d) => { const t0_ = performance.now(); flockDraw(target, d); FL.ms = performance.now() - t0_; };
  const flockDraw = (target, d) => { const F = MAT && MAT.base && MAT.base.flock; if (!film || !F || !BUILT_C || !BUILT.value) return;
    const key = flockKey(), PX0 = F.px || 1.5, FAR = F.far || [2, 3], SPX = (F.street && F.street.px) || 0, SFAR = (F.street && F.street.far) || [.35, .5], B_ = .35;
    if (key !== FL.key) { FL.key = key; FL.tiles.clear(); }   // (the year, today's city standing, a detailed model, the water: every tile again)
    if (BUILT_S.v !== FL.built) { FL.built = BUILT_S.v; const N = 1024;   // (the period cities standing changed: each tile looks at its own share of the masks again; read through a copy kept for reading, never
      // from the masks themselves: a canvas read back again and again is moved off the graphics card, and its blur and its upload slow every frame)
      FL.rd ||= [0, 1].map(() => { const c = document.createElement('canvas'); c.width = c.height = N; return c.getContext('2d', { willReadFrequently: true }); });
      [FL.bd, FL.td] = [BUILT_C, TREES_C].map((c, k) => { const g = FL.rd[k]; g.clearRect(0, 0, N, N); g.drawImage(c, 0, 0, N, N); return g.getImageData(0, 0, N, N).data; }); FL.N = N; FL.bv = (FL.bv || 0) + 1; }
    const N = FL.N, bd = FL.bd, td = FL.td, px = (D_, x, z) => { const u = Math.floor((x / PW + .5) * N), v = Math.floor((z / PD + .5) * N); return u < 0 || v < 0 || u >= N || v >= N ? 0 : D_[(v * N + u) * 4] / 255; };
    const tileSum = (i, j) => { const T0 = TILE * scale, u0 = Math.max(0, Math.floor((i * T0 / PW + .5) * N)), u1 = Math.min(N - 1, Math.floor(((i + 1) * T0 / PW + .5) * N)), v0 = Math.max(0, Math.floor((j * T0 / PD + .5) * N)), v1 = Math.min(N - 1, Math.floor(((j + 1) * T0 / PD + .5) * N));
      let s = 0; for (let v = v0; v <= v1; v++) for (let u = u0; u <= u1; u++) { const o = (v * N + u) * 4; s = (s * 31 + bd[o] * 7 + td[o]) % 1000000007; } return s; };
    const YN = 4096, yc = STREET_K.value > 0 ? TODAY_K.value.x - 1899 : -1,   // (today's ground as the year has it, where today's city is coming or is the subject: its trees fade in and out with it, STREET_K; behind a period city it is a plan on the board, the period's groves stand over it)
      ty = (x, z) => { if (!YEAR_D || yc < 0) return 0; const u = Math.floor((x / PW + .5) * YN), v = Math.floor((z / PD + .5) * YN); if (u < 0 || v < 0 || u >= YN || v >= YN) return 0; const y = YEAR_D[v * YN + u], ye = GREEN_ON.value && YEAR_E && TODAY_K.value.z < .3 ? YEAR_E[v * YN + u] : 0; return (y > 0 && y <= yc) || (ye > 0 && ye <= yc) ? 1 : 0; };   // (with green data the urban extent is plaster: no country groves on it)
    const today = yc >= 0 && (STREETS.list || GREEN_ON.value);
    if (today && GREEN_ON.value && !GREEN_D && GREEN.value && GREEN.value.image) { const im_ = GREEN.value.image, c_ = document.createElement('canvas'); c_.width = im_.width; c_.height = im_.height; const g_ = c_.getContext('2d'); g_.drawImage(im_, 0, 0); GREEN_D = { w: im_.width, h: im_.height, d: g_.getImageData(0, 0, im_.width, im_.height).data }; }
    const M = { F, bd, td, px, ty, yc: today ? yc : -1, ycT: yc, IX: today ? streetIndex() : null, ST: { ...(F.street || { off: 2.5, r: 3.6, every: { secondary: 13, tertiary: 14 }, minor: 18, junction: 14 }), ...((todayL() && todayL().streetTrees) || {}) }, PT: { cell: 10, size: [3, 4.5], groves: [.5, .62], noise: [60, 20], dense: .9, lone: .04, edge: [12, .4], ...((todayL() && todayL().parkTrees) || {}) } };
    if (today && STREETS.list) segIndex();
    // the tiles the frame sees: its ground as far as the frame reaches (the plate's edge at most), the tiles there inside the view
    // (with a margin for a tree's shadow falling into it), nearest first
    // (the eye the trees are sized from: the camera's own, snapped to a grid of 0.4 % of its distance from the target, that distance
    // in steps of 1.5 %: a crown's size moves by less than that, unseen, and a frame whose eye and tiles are the frame before's
    // (a hold, a hand-held drift) takes the trees as they are, not all of them made and sent again)
    camera.updateMatrixWorld(); const dq_ = Math.pow(2, Math.round(Math.log2(Math.max(camera.position.distanceTo(target), 1e-9)) * 48) / 48) * .004;
    const cp = FR.cp.set(Math.round(camera.position.x / dq_) * dq_, Math.round(camera.position.y / dq_) * dq_, Math.round(camera.position.z / dq_) * dq_), kp = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) / 1080;   // (kp: model units a picture pixel spans at unit distance)
    FR.fr.setFromProjectionMatrix(FR.pm.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse));
    const rS = (M.ST.r || 3.6) * 1.25 * scale, Dg = F.cell * scale / (FAR[0] * kp), Ds = today ? rS / (SFAR[0] * kp) : 0, Dmax = Math.max(Dg, Ds);   // (nothing of a tree beyond these: a grove's crowns gone into the ground's tone, a row's under a third of a pixel)
    const T0 = TILE * scale, gy = target.y, far = Math.min(Math.hypot(PW, PD), Dmax);
    let bx0 = cp.x, bx1 = cp.x, bz0 = cp.z, bz1 = cp.z;
    for (const [sx, sy] of [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1], [-1, .5], [1, .5], [-1, .2], [1, .2]]) {
      const ray = FR.ray.set(sx, sy, .5).unproject(camera).sub(cp).normalize(); const k = Math.min(ray.y < -1e-5 ? (gy - cp.y) / ray.y : far, far);
      const x = cp.x + ray.x * k, z = cp.z + ray.z * k; bx0 = Math.min(bx0, x); bx1 = Math.max(bx1, x); bz0 = Math.min(bz0, z); bz1 = Math.max(bz1, z); }
    const mg = 150 * scale, tiles = [];
    for (let i = Math.floor((Math.max(bx0, -PW / 2) - mg) / T0); i <= Math.floor((Math.min(bx1, PW / 2) + mg) / T0); i++) for (let j = Math.floor((Math.max(bz0, -PD / 2) - mg) / T0); j <= Math.floor((Math.min(bz1, PD / 2) + mg) / T0); j++) {
      const xa = i * T0, za = j * T0, gc = S.ground(xa + T0 / 2, za + T0 / 2);
      FR.box.min.set(xa - mg, gc - 400 * scale, za - mg); FR.box.max.set(xa + T0 + mg, gc + 400 * scale, za + T0 + mg); if (!FR.fr.intersectsBox(FR.box)) continue;
      const dx = Math.max(xa - cp.x, 0, cp.x - xa - T0), dz = Math.max(za - cp.z, 0, cp.z - za - T0), D0 = Math.max(Math.hypot(dx, dz, cp.y - gc), 1e-6);
      if (D0 < Dmax) tiles.push([i, j, D0]); }
    tiles.sort((a, b) => a[2] - b[2]);
    { let h_ = 0; for (const t_ of tiles) { const gk = t_[0] * 100003 + t_[1]; let T = FL.tiles.get(gk);   // (each tile as this frame has it: planted again where the period cities standing changed in it)
        if (T && T.bv !== FL.bv) { const s_ = tileSum(t_[0], t_[1]); if (s_ !== T.sum) { FL.tiles.delete(gk); T = null; } else T.bv = FL.bv; }
        if (!T) { T = { i: t_[0], j: t_[1], p: 0, list: [], sum: tileSum(t_[0], t_[1]), bv: FL.bv, id: FL.ids = (FL.ids || 0) + 1 }; FL.tiles.set(gk, T); }
        h_ = (h_ * 31 + gk * 7 + T.id) % 1000000007; }
      const sig = [cp.x, cp.y, cp.z, kp, h_, tiles.length, FL.key, FL.mesh.length].join();
      if (sig === FL.sig) { GEO_T.value.set(F.cell * scale / (FAR[1] * kp), F.cell * scale / (FAR[0] * kp), 1, 0); return; } FL.sig = sig; }   // (the same eye, the same tiles: the trees as they stand)
    // each tile's trees as far down their ranks as its nearest point needs (the largest crown's density there), then each tree by
    // its own distance: its density, its share of the canopy, its fade
    const rMax = F.cell * .42 * 1.6 * 1.2 * scale, rMaxP = M.PT.size[1] * scale, out = FL.out || (FL.out = []);
    let n = 0; const put = (x, y, z, r, h, t, w) => { const o = out[n] || (out[n] = new Float32Array(7)); o[0] = x; o[1] = y; o[2] = z; o[3] = r; o[4] = h; o[5] = t; o[6] = w; n++; };
    for (const [i, j, D0] of tiles) {
      const T = FL.tiles.get(i * 100003 + j);   // (made above, as this frame has it)
      const pa = (r_) => Math.min(1, (r_ / (D0 * kp * PX0)) ** 2), ps = SPX ? Math.min(1, M.ST.r * 1.25 * scale / (D0 * kp * SPX)) : 1;
      const pN = Math.min(1, Math.max(pa(rMax), today ? Math.max(pa(rMaxP), ps) : 0) * (1 + B_)); plantTile(T, pN, M);
      for (const tr of T.list) { const [x, y, z, r, h, t, rk] = tr; if (rk >= pN) continue;
        const D = Math.hypot(x - cp.x, y - cp.y, z - cp.z), mpp = D * kp;
        let w, rd;
        if (t === 2) { rd = Math.max(r, SPX * mpp); const p = r / rd; w = (rk ? Math.min(1, Math.max(0, (p - rk) / rk)) : 1) * fsm(SFAR[0], SFAR[1], r / mpp); }   // (a row: its trees at least street px pixels round, every other one going as they grow; gone where a crown would be under far[0] of a pixel)
        else { const p = Math.min(1, (r / (mpp * PX0)) ** 2); rd = r / Math.sqrt(p); w = Math.min(1, Math.max(0, (p * (1 + B_) - rk) / (B_ * p))) * fsm(FAR[0], FAR[1], F.cell * scale / mpp); }   // (a grove's or a park's: fewer, larger, whole under rank p, gone from p (1 + B_); afar the ground's groves' tone)
        w *= t > 0 || t === -2 ? STREET_K.value : t === -1 ? 1 - STREET_K.value : 1;   // (today's trees, and the groves only today's city keeps or drops, fading with it)
        if (w > .002) put(x, y, z, rd * w, h, Math.max(t, 0), rd); } }
    // the crowns: a finer sphere where a crown is 6 pixels round or more, the coarsest (20 faces) under 3: afar a row's or a grove's
    // crowns are a few pixels each, their facets never seen, and there are most of them; the parks' in their own paint (parkTrees crown, trees)
    const CR_ = (yc >= 0 && todayL() && todayL().crown) || F.crown, CRP_ = (yc >= 0 && M.PT.crown) || CR_;   // (todayLight crown: today's own, while today's city is the subject; a period city's groves keep the flock's)
    // (each crown 9 numbers sent, not an instance matrix's 16 and its colour: iT its foot and radius, iS its turn and its height's
    // share, its colour; turned and placed in the vertex shader, its shadow's alike)
    const crownGLSL = sh => { sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec4 iT; attribute vec2 iS;')
        .replace('#include <beginnormal_vertex>', '#include <beginnormal_vertex>\n  { float c_ = cos(iS.x), s_ = sin(iS.x); objectNormal = vec3(c_ * objectNormal.x + s_ * objectNormal.z, objectNormal.y, -s_ * objectNormal.x + c_ * objectNormal.z); }')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\n  { float c_ = cos(iS.x), s_ = sin(iS.x); vec3 p_ = position * vec3(iT.w, iT.w * iS.y, iT.w); transformed = vec3(c_ * p_.x + s_ * p_.z, p_.y + iT.w * .7 * iS.y, -s_ * p_.x + c_ * p_.z) + iT.xyz; }'); };
    const mk = (detail, CR_) => { const base_ = new THREE.IcosahedronGeometry(1, detail).scale(1, .82, 1), geo = new THREE.InstancedBufferGeometry(), cap = Math.max(1024, FL.cap);
      geo.setAttribute('position', base_.attributes.position); geo.setAttribute('normal', base_.attributes.normal);
      for (const [k, w] of [['iT', 4], ['iS', 2], ['color', 3]]) geo.setAttribute(k, new THREE.InstancedBufferAttribute(new Float32Array(cap * w), w).setUsage(THREE.DynamicDrawUsage));
      geo.instanceCount = 0;
      const mat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .95, vertexColors: true }), depth = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking });
      depth.onBeforeCompile = crownGLSL; depth.customProgramCacheKey = () => 'mini-crown-depth';
      mat.onBeforeCompile = sh => { crownGLSL(sh); if (!CR_) return;   // a crown painted as a model's foliage (flock crown: [its underside's share, its cap's, the cap's warmth]): a darker shade side, a lighter, yellower sunlit cap
        const [cd_, cc_, cw_] = CR_;
        sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying float vCrownY;').replace('#include <beginnormal_vertex>', '#include <beginnormal_vertex>\n  vCrownY = normal.y;');
        sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vCrownY;').replace('#include <color_fragment>', `#include <color_fragment>
  diffuseColor.rgb *= mix(${cd_.toFixed(3)}, ${cc_.toFixed(3)}, smoothstep(-.6, .9, vCrownY)); diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(${cw_.map(v => v.toFixed(3)).join(', ')}), smoothstep(.35, 1., vCrownY));`); };
      mat.customProgramCacheKey = () => 'mini-crown2' + (CR_ || []).flat().join();
      const mesh = new THREE.Mesh(geo, mat); mesh.customDepthMaterial = depth;
      mesh.castShadow = mesh.receiveShadow = true; mesh.layers.set(L); mesh.frustumCulled = false; scene.add(mesh); mesh.userData.crown = (CR_ || []).flat().join(); mesh.userData.cap = cap; return mesh; };
    let nAll = n; for (let k = 0; k < n; k++) if (out[k][5] === 1) nAll += 2;   // (today's park crowns as a model maker's clusters: two smaller balls beside each)
    if (nAll > FL.cap || !FL.mesh[5] || FL.mesh[0].userData.crown !== (CR_ || []).flat().join() || FL.mesh[3].userData.crown !== (CRP_ || []).flat().join()) { FL.cap = Math.max(FL.cap, Math.ceil(nAll * 1.3)); for (const m of FL.mesh) if (m) { scene.remove(m); m.geometry.dispose(); m.material.dispose(); m.customDepthMaterial.dispose(); } FL.mesh = [mk(0, CR_), mk(1, CR_), mk(2, CR_), mk(0, CRP_), mk(1, CRP_), mk(2, CRP_)]; }   // (a street's or a grove's, a park's; each coarsest, coarse and fine)
    const base = new THREE.Color().setRGB(...F.col.map(v => Math.pow(v, 2.2))), base2 = new THREE.Color().setRGB(...(F.col2 || F.col).map(v => Math.pow(v, 2.2))), col = new THREE.Color();
    const lin = L_ => L_.map(c_ => new THREE.Color().setRGB(...c_.map(v => Math.pow(v, 2.2)))), TT_ = MAT.todayLight && todayL().trees, tb = TT_ ? lin(TT_) : [base, base2], tp = M.PT.trees ? lin(M.PT.trees) : tb;   // (today's trees: todayLight.trees, each tree one of its greens; a park's its own, parkTrees trees)
    const PL_ = M.PT.far, PLC_ = PL_ ? new THREE.Color().setRGB(...PL_[3].map(v => Math.pow(v, 2.2))) : null;
    const cnt = [0, 0, 0, 0, 0, 0], AT = FL.mesh.map(m => m.geometry.attributes.iT.array), AS = FL.mesh.map(m => m.geometry.attributes.iS.array), C = FL.mesh.map(m => m.geometry.attributes.color.array);
    const one = (x, y, z, r, h, t) => { const px_ = r / (Math.hypot(x - cp.x, y - cp.y, z - cp.z) * kp), s = (px_ >= 6 ? 2 : px_ >= 3 ? 1 : 0) + (t === 1 ? 3 : 0), q = cnt[s]++, sy_ = t ? .8 + .4 * ((h * 13.7) % 1) : 1;   // (today's: taller or flatter crowns, not identical balls)
      AT[s][q * 4] = x; AT[s][q * 4 + 1] = y; AT[s][q * 4 + 2] = z; AT[s][q * 4 + 3] = r; AS[s][q * 2] = h * 6.28; AS[s][q * 2 + 1] = sy_;
      if (t) { const T_ = t === 1 ? tp : tb; col.copy(T_[Math.floor(((h * 7.31) % 1) * T_.length)]).multiplyScalar(.9 + .2 * h); if (t === 1 && PL_) { const k_ = 1 - fsm(PL_[0], PL_[1], px_); col.lerp(PLC_, k_ * PL_[2]); } } else col.copy(base).lerp(base2, fvn(x / scale / 40, z / scale / 40) * .7 + h * .3).multiplyScalar(.8 + .4 * h);   // (col2: a second green, by groves more than by tree)   // (a park's crown afar takes its sunlit cap's light green: parkTrees far [from px, whole by px, share, colour]; close, the deeper mid-greens)
      C[s][q * 3] = col.r; C[s][q * 3 + 1] = col.g; C[s][q * 3 + 2] = col.b; };
    for (let k = 0; k < n; k++) { const [x, y, z, r, h, t] = out[k]; one(x, y, z, r, h, t);
      if (t === 1) for (let j = 0; j < 2; j++) { const a_ = h * 40 + j * 2.6; one(x + Math.cos(a_) * r * .62, y, z + Math.sin(a_) * r * .62, r * (.55 + .15 * j), (h * 3.7 + j * .31) % 1, 1); } }   // (beside each crown, lower: the group lit on top, shaded below)
    FL.mesh.forEach((m, s) => { const g_ = m.geometry; g_.instanceCount = cnt[s]; for (const [k, w_] of [['iT', 4], ['iS', 2], ['color', 3]]) { const B_ = g_.attributes[k]; B_.clearUpdateRanges(); if (cnt[s]) B_.addUpdateRange(0, cnt[s] * w_); B_.needsUpdate = true; } });   // (only the crowns drawn are sent)
    FL.stat = { tiles: tiles.length, trees: n, crowns: cnt.reduce((a_, b_) => a_ + b_, 0), planted: [...FL.tiles.values()].reduce((s_, T) => s_ + T.list.length, 0) };
    GEO_T.value.set(F.cell * scale / (FAR[1] * kp), F.cell * scale / (FAR[0] * kp), 1, 0);   // (the ground's groves' tone from where a grove's cell is far[1] pixels, whole by far[0]: the crowns' own fade, by the eye's distance)
  };
  const info = card ? infoPanel(card) : null;
  // the tilt-shift: sharp in a band through the middle, blurred above and below
  // with the effects: the film's own passes (post.js: ambient occlusion, haze toward a sky dome, the stronger depth of field),
  // in place of the tilt-shift band
  // (the film: always the film's passes, its ambient occlusion from the picture's own depth: the geometry the passes would draw
  // themselves is the city as built, not as it stands at that moment)
  const FP = FX || film ? makePost(renderer, scene, camera, S.post.dof.rt.width / S.post.dof.s, S.post.dof.rt.height / S.post.dof.s,
    { ssaa: S.post.dof.s, ao: !phone, aoAmt: FX ? MINI_LIFT.ao : FP_ ? FILM_PIC.ao : FILM_AO, aoDepth: film, ...S.gpu.targets, ...(FX && FX.haze ? { haze: FX_SKY.mini } : {}), ...(FX && FX.dof || FP_ && FILM_PIC.dof.two ? { dof2: true } : {}) }) : null;
  const dome = FX && FX.haze ? makeSky(FX_SKY.mini) : null;
  // today's sky (a material's todayLight dome: [horizon, zenith, the sun's glow on it, clouds: [amount, scale, threshold, colour]]): a dome from the haze's colour at the horizon up to a soft blue,
  // no sun's glow on it (the haze's one colour meets it at the horizon without a seam); shown while today's city is the subject
  const domeT = film && !FX && MAT && MAT.todayLight && MAT.todayLight.dome ? makeSky({ horizon: '#ffffff', zenith: '#ffffff', sun: '#000000' }) : null;
  if (domeT) { domeT.mesh.layers.set(L); domeT.mesh.visible = false; scene.add(domeT.mesh);
    const dm_ = domeT.mesh.material; Object.assign(dm_.uniforms, { uCloud: { value: new THREE.Vector4() }, uCloudC: { value: new THREE.Color() }, uDomeR: DOME_R });
    dm_.fragmentShader = dm_.fragmentShader.replace('pow(max(up, 1e-4), .4)', '(1. - exp(-up * uDomeR))').replace('uniform float uI;', `uniform float uI, uDomeR; uniform vec4 uCloud; uniform vec3 uCloudC;
float cH_(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float cN_(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f); return mix(mix(cH_(i), cH_(i + vec2(1., 0.)), f.x), mix(cH_(i + vec2(0., 1.)), cH_(i + vec2(1., 1.)), f.x), f.y); }
float cF_(vec2 p){ return .5 * cN_(p) + .25 * cN_(p * 2.1 + 3.1) + .125 * cN_(p * 4.3 + 7.7) + .0625 * cN_(p * 8.9 + 1.3); }`)
      .replace('gl_FragColor = vec4(fxSky(normalize(vD), uHor, uZen, uSunC, uSunD) * uI, 1.); }', `vec3 d_ = normalize(vD); vec3 c_ = fxSky(d_, uHor, uZen, uSunC, uSunD) * uI;
  if (uCloud.x > 0. && d_.y > 0.) { vec2 p_ = d_.xz / (d_.y + .3) * uCloud.y; float n_ = cF_(p_), cl_ = smoothstep(uCloud.z, uCloud.z + .12, n_) * smoothstep(.0, .025, d_.y);   // soft clouds (todayLight dome[3]: [amount, scale, threshold, colour]), lit from below by a low sun
    c_ = mix(c_, uCloudC * (.5 + .7 * cF_(p_ * 1.7 + 5.)) + uSunC * .25 * pow(max(dot(d_, normalize(uSunD)), 0.), 4.), cl_ * uCloud.x); }
  gl_FragColor = vec4(c_, 1.); }`); }   // (its blue begins close above the horizon, smoothly: a low view's sky blue, not the haze's, and no kink at the horizon)
  if (FP) { FP.bloom.strength = .1; FP.bloom.threshold = 2.2;   // (a bright day: only the sun's glints glow, not every lit wall)
    FP.vig.uniforms.amt.value = .22;
    if (FP_ && MAT && MAT.todayLight) {   // today's light (todayLight edge, exposure, filmic, grain): the colour film's own passes only
      const cm = FP.dof.coc.material; Object.assign(cm.uniforms, { uEdge: { value: 0 }, uPx: { value: new THREE.Vector2() }, uPxK: { value: 1 } });
      cm.fragmentShader = cm.fragmentShader.replace('uniform float aoAmt,', 'uniform float uEdge, uPxK; uniform vec2 uPx;\n    uniform float aoAmt,').replace('gl_FragColor = vec4(col, c);', `if (uEdge > 0. && d < .99999) {   // an edge catches the light like a bevel: where the surface turns away (the centre nearer than its neighbours' mean, in 1/z, flat at any slope),
        // a pale line a picture's pixel wide afar, wider close (about 0.6 m, at most 3 pixels): sized by pixels, nothing finer to shimmer
        float o_ = clamp(.6 / (z * uPxK), 2., 6.), w0 = 1. / z, wl = -1. / perspectiveDepthToViewZ(texture2D(tDepth, vUv - vec2(uPx.x * o_, 0.)).x, near, far), wr = -1. / perspectiveDepthToViewZ(texture2D(tDepth, vUv + vec2(uPx.x * o_, 0.)).x, near, far);
        float wu = -1. / perspectiveDepthToViewZ(texture2D(tDepth, vUv + vec2(0., uPx.y * o_)).x, near, far), wd = -1. / perspectiveDepthToViewZ(texture2D(tDepth, vUv - vec2(0., uPx.y * o_)).x, near, far);
        float e_ = smoothstep(.0006, .006, max(w0 - .5 * (wl + wr), w0 - .5 * (wu + wd)) / w0);
        col = mix(col, col * 1.5 + .05, uEdge * e_); }
      gl_FragColor = vec4(col, c);`); cm.needsUpdate = true;
      const vm = FP.vig.material; Object.assign(vm.uniforms, { uGrain: { value: 0 }, uFilmic: { value: 0 }, uExpo: { value: 1 } });
      vm.fragmentShader = vm.fragmentShader.replace('uniform float amt,', 'uniform float uGrain, uFilmic, uExpo, amt,').replace('gl_FragColor = c; }', `c.rgb *= uExpo;
        if (uFilmic > 0.) { vec3 x_ = c.rgb; vec3 f_ = x_ * x_ / (x_ + .045) * 1.06; f_ = f_ / (1. + .3 * f_) * 1.234;   // a filmic curve: a toe for the deep shadows, a soft shoulder (the lit walls' engraving kept), mid grey (.18) kept
          c.rgb = mix(c.rgb, f_, uFilmic); }
        if (uGrain > 0.) { vec2 g_ = gl_FragCoord.xy; float n_ = fract(sin(dot(g_, vec2(12.9898, 78.233))) * 43758.5453) + fract(sin(dot(g_ + 3.7, vec2(39.35, 11.13))) * 24634.63) - 1.; c.rgb *= 1. + uGrain * n_; }   // (a trace of grain)
        gl_FragColor = c; }`); vm.needsUpdate = true; }
    if (FP_ && FILM_PIC.dof.tilt && FP.dof.smooth) {   // a tilt lens over a miniature (FILM_PIC dof tilt: [where the soft bands begin and where they
      // are whole, from the frame's middle (0) to its top and bottom edge (1); the largest blur in pixels of a 1080 picture; the
      // near side's share; the depth's distance from the focus, 1 - focus / z, from which a thing in a band begins to soften and
      // is whole, farther, then nearer (the near side wider: a subject in the frame's lower part, nearer than the target, stays sharp)]): sharp over most of the frame, soft only toward its top (the far) and its bottom (the near), gradually; in a
      // band what stands at the subject's depth (a tower's top) stays sharp, as with a real lens
      const cm = FP.dof.coc.material; cm.uniforms.uTilt = { value: new THREE.Vector4() }; cm.uniforms.uTiltR = { value: new THREE.Vector4(1, 1, 1, 1) };
      cm.fragmentShader = cm.fragmentShader.replace('uniform float aoAmt,', 'uniform vec4 uTilt, uTiltR;\n    uniform float aoAmt,').replace('c = clamp(c < 0. ? c * .7 : c, -maxCoc, maxCoc);', `c = clamp(c < 0. ? c * .7 : c, -maxCoc, maxCoc);
      if (uTilt.x > 0.) { float x_ = 1. - focus / zc; c = sign(x_) * maxCoc * smoothstep(uTilt.y, uTilt.z, abs(vUv.y - .5) * 2.) * (x_ < 0. ? smoothstep(uTiltR.z, uTiltR.w, -x_) : smoothstep(uTiltR.x, uTiltR.y, x_)) * (x_ < 0. ? uTilt.w : 1.); }`); cm.needsUpdate = true;
      // a soft edge smoothed only from what is about as blurred as it: a sharp tower beside a blurred ground spreads no light into it (no halo)
      const sm = FP.dof.smooth.material; sm.fragmentShader = sm.fragmentShader.replace('vec4 acc = c0; const int N = 24;', 'float ca_ = abs(texture2D(tCoc, vUv).a) / uS; vec4 acc = c0; float ws_ = 1.; const int N = 24;')
        .replace('acc += texture2D(tIn, vUv + vec2(cos(th), sin(th)) * rr / res); }', 'vec2 o_ = vUv + vec2(cos(th), sin(th)) * rr / res; float w_ = smoothstep(.3, .6, abs(texture2D(tCoc, o_).a) / uS / max(ca_, .75)); acc += texture2D(tIn, o_) * w_; ws_ += w_; }')
        .replace('gl_FragColor = acc / float(N + 1);', 'gl_FragColor = acc / ws_;'); sm.needsUpdate = true; }
    if (FP_ && MAT && MAT.todayLight && MAT.todayLight.air) {   // today's air (todayLight air), in the picture's own depth before the lens: every
      // surface, trees and detailed models too, toward the sky's horizon colour by its distance from the eye (slowly near, whole
      // afar), and whole at the end of the model (the plate's last stretch: no board's edge, no land beyond it seen)
      const cm = FP.dof.coc.material; Object.assign(cm.uniforms, { uAirIP: { value: new THREE.Matrix4() }, uAirCW: { value: new THREE.Matrix4() }, uAir: { value: new THREE.Vector4() }, uAirR: { value: new THREE.Vector4(-PW / 2, -PD / 2, PW / 2, PD / 2) }, uAirC: { value: new THREE.Color() }, uAirF: { value: new THREE.Vector4() }, uAirFC: { value: new THREE.Color() }, uAirFS: { value: 1 } });
      cm.fragmentShader = cm.fragmentShader.replace('uniform float aoAmt,', 'uniform mat4 uAirIP, uAirCW; uniform vec4 uAir, uAirR, uAirF; uniform vec3 uAirC, uAirFC; uniform float uAirFS;\n    uniform float aoAmt,').replace('gl_FragColor = vec4(col, c);', `if (uAir.w > 0. && d < .99999) { vec4 vh_ = uAirIP * vec4(vUv * 2. - 1., d * 2. - 1., 1.); vec3 vp_ = vh_.xyz / vh_.w, wp_ = (uAirCW * vec4(vp_, 1.)).xyz;
        float fw_ = smoothstep(uAirF.x, uAirF.y, length(vp_)) * uAirF.w; col = mix(col, vec3(dot(col, vec3(.2126, .7152, .0722))), (1. - uAirFS) * fw_);   // (its colour first: the far city paler in hue before it is softer)
        col = mix(col, mix(uAirFC, col, uAirF.z), fw_);   // (the far city first softened: its contrast and colour toward a pale tint)
        float x_ = max(length(vp_) - uAir.x, 0.) / uAir.y, f_ = 1. - exp(-x_ * x_), sd_ = max(max(uAirR.x - wp_.x, wp_.x - uAirR.z), max(uAirR.y - wp_.z, wp_.z - uAirR.w));
        col = mix(col, uAirC, max(f_, smoothstep(-uAir.z, 0., sd_)) * uAir.w); }
      gl_FragColor = vec4(col, c);`); cm.needsUpdate = true; }
    if (FP.dof.haze) { const ex = S.terrainEx; FP.dof.haze.uHazeD.value = 1 / (FX.haze.dist_km * 1000 * scale * MINI_LIFT.haze); FP.dof.haze.uHazeB.value = 1 / (FX.haze.height_m * scale * ex); FP.dof.haze.uHazeK.value = FX.haze.k; FP.dof.haze.uHazeS.value = FX.haze.start_km * 1000 * scale; FP.dof.haze.uHazeRect.value.copy(S.post.dof.haze ? S.post.dof.haze.uHazeRect.value : new THREE.Vector4(-PW / 2, -PD / 2, PW / 2, PD / 2)); FP.dof.haze.uHazeRect2.value.copy(S.post.dof.haze ? S.post.dof.haze.uHazeRect2.value : FP.dof.haze.uHazeRect.value); FP.dof.haze.uHazeEdge.value = FX.haze.edge_km * 1000 * scale; } }
  if (dome) { dome.mesh.layers.set(L); scene.add(dome.mesh); }
  // the film: the tilt-shift band after the bloom (in place of the depth of field by distance), a lighter vignette, the colours clean
  const BAND = FP && FP_ && FILM_PIC.band ? [1, 0].map(v => { const b = new ShaderPass(BAND_BLUR); b.uniforms.dir.value.set(1 - v, v); for (const k of ['mid', 'inner', 'outer', 'top', 'bottom']) b.uniforms[k].value = FILM_PIC.band[k]; FP.composer.insertPass(b, 2); return b; }) : null;
  if (FP && FP_) { FP.vig.uniforms.amt.value = FILM_PIC.vignette; FP.vig.uniforms.sat.value = FILM_PIC.sat; FP.vig.uniforms.contrast.value = FILM_PIC.contrast; }
  if (FP && film && FP.dof.ao) FP.dof.ao.updatePdMaterial({ radius: 4 * S.post.dof.s });   // (its denoise a little tighter: the depth's own normals are noisier than a rendered normal pass)
  // the ambient occlusion passes leave out what detail.js marks noAO (they draw the scene with their own material, unfaded)
  const noAO = p => { if (!p) return; const o = p.overrideVisibility.bind(p); p.overrideVisibility = () => { o(); p.scene.traverse(x => { if (x.userData.noAO) x.visible = false; }); }; };
  if (FP) noAO(FP.dof.ao);
  const composer = new EffectComposer(renderer), rp = new RenderPass(scene, camera);
  const ht = new ShaderPass(HorizontalTiltShiftShader), vt = new ShaderPass(VerticalTiltShiftShader);
  const ao = new GTAOPass(scene, camera, 1920, 1080); ao.updateGtaoMaterial({ radius: .0012, distanceExponent: 1, thickness: 1, scale: 1.2 }); ao.blendIntensity = 1; noAO(ao);
  composer.addPass(rp); composer.addPass(ao); composer.addPass(ht); composer.addPass(vt); composer.addPass(new OutputPass());
  const size = new THREE.Vector2();

  // a landmark's detailed model (a museum page's glb: x east, y up, z south, metres, unturned) in place of the generator's: the
  // generator's landmark is the building whose centre most landmark vertices near `near` share; its vertices are folded away, and
  // the model stands at that centre, turned by theta_deg, as tall as the generator's (the film's height exaggeration)
  async function swap({ url, theta_deg = 0, near, r_m = 120, today = false, colours = null, parts = null }) {   // (today: a building of today's city, any part, in place of an era's landmark)
    // (colours: {role: colour} the model's own colours by material role; parts: [[a pattern of its parts' names, colour], ...] by part, first match)
    const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js'), { DRACOLoader } = await import('three/addons/loaders/DRACOLoader.js');
    const map = (() => { try { return JSON.parse(document.querySelector('script[type=importmap]').textContent).imports['three/addons/']; } catch (e) { return null; } })();
    const draco = new DRACOLoader().setDecoderPath((map || 'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/') + 'libs/draco/gltf/');
    const g = await new GLTFLoader().setDRACOLoader(draco).loadAsync(url); draco.dispose();
    const votes = new Map(), r = r_m * scale;
    const pool = today ? [cityMesh] : eraMeshes;
    for (const m of pool) { if (!m.visible) continue; const P = m.geometry.attributes.position, D = m.geometry.attributes.aData, C = m.geometry.attributes.aCtr;
      for (let i = 0; i < P.count; i++) { if ((!today && Math.round(D.getY(i)) !== 1) || Math.hypot(P.getX(i) - near[0], P.getZ(i) - near[1]) > r) continue;
        const k = C.getX(i).toFixed(7) + ',' + C.getY(i).toFixed(7); votes.set(k, (votes.get(k) || 0) + 1); } }
    if (!votes.size) throw new Error(`mini: no landmark near ${near}`);
    const [key] = [...votes].sort((a, b) => b[1] - a[1])[0], [cx, cz] = key.split(',').map(Number);
    let y0 = Infinity;   // (the building's own base, aBase: it stands on its own levelled ground; the terrain sampled again counted that ground's rise as height)
    for (const m of pool) { const C = m.geometry.attributes.aCtr, B = m.geometry.attributes.aBase; for (let i = 0; i < C.count; i++) if (Math.abs(C.getX(i) - cx) < 2e-7 && Math.abs(C.getY(i) - cz) < 2e-7) y0 = Math.min(y0, B ? B.getX(i) : S.ground(cx, cz)); }
    if (!(y0 < Infinity)) y0 = S.ground(cx, cz);
    let top = -Infinity, folded = 0; const box = new THREE.Box3().setFromObject(g.scene), th_ = THREE.MathUtils.degToRad(theta_deg), co_ = Math.cos(th_), si_ = Math.sin(th_);
    // today's: every building whose centre stands inside the model's footprint goes too (a tower inside a stadium's bowl, a block cut by it)
    const inFoot = (x, z) => { if (!today) return false; const dx = (x - cx) / scale, dz = (z - cz) / scale, lx = dx * co_ - dz * si_, lz = dx * si_ + dz * co_; return lx > box.min.x && lx < box.max.x && lz > box.min.z && lz < box.max.z; };
    for (const m of pool) { const P = m.geometry.attributes.position, C = m.geometry.attributes.aCtr; let hit = false;
      for (let i = 0; i < P.count; i++) if (Math.abs(C.getX(i) - cx) < 2e-7 && Math.abs(C.getY(i) - cz) < 2e-7 || inFoot(C.getX(i), C.getY(i))) { top = Math.max(top, P.getY(i)); P.setXYZ(i, C.getX(i), S.ground(C.getX(i), C.getY(i)) - 1e-4, C.getY(i)); hit = true; folded++; }
      if (hit) P.needsUpdate = true; }
    const H = box.max.y - Math.max(box.min.y, 0), k = today ? (S.U.uScaleH ? S.U.uScaleH.value / scale : 1) : THREE.MathUtils.clamp((top - y0) / (H * scale), 1, 3);   // (today's: the model's own exaggeration)
    const M = new THREE.Matrix4().makeTranslation(cx, y0, cz).multiply(new THREE.Matrix4().makeScale(scale, scale * k, scale)).multiply(new THREE.Matrix4().makeRotationY(THREE.MathUtils.degToRad(theta_deg)));
    const root = new THREE.Group(); root.matrixAutoUpdate = false; root.matrix.copy(M); root.add(g.scene);
    const mats = {};
    g.scene.traverse(o => { if (!o.isMesh) return; const nm = (o.material && o.material.name) || 'stone';
      const pc = (parts || (film && MAT && MAT.glbParts) || []).find(([re]) => new RegExp(re).test(o.name)), col = pc ? pc[1] : colours && colours[nm] || null;
      o.material = mats[nm + (col || '')] ||= film && MAT && MAT.glbC ? glbMaterial(nm, k, scale, col) : new THREE.MeshStandardMaterial({ color: col || pal.glb[nm] || pal.glb.stone, roughness: .9, metalness: 0, side: THREE.DoubleSide });
      o.castShadow = o.receiveShadow = true; o.layers.set(L); });
    scene.add(root); root.updateMatrixWorld(true); landmarks.push(root); TF.reset(); if (today) FOOTS.push(inFoot);   // (today's trees planted again round it: flockKey)
    if (today) { const f_ = { cx, cz, inFoot, rr: Math.max(r * .5, 30 * scale) }; FOLDS.push(f_); if (FPT.mesh) foldIn(FPT.mesh.geometry, f_); }   // (a replacement footprint there folded too, and any loaded later: todayFootprints)
    if (today && ROOF_MESH) for (const RM of ROOF_MESH) { const M_ = new THREE.Matrix4(), p_ = new THREE.Vector3(), Z_ = new THREE.Matrix4().makeScale(0, 0, 0), rr = Math.max(r * .5, 30 * scale);   // (its roof pieces go with it)
      for (let n = 0; n < RM.count; n++) { RM.getMatrixAt(n, M_); p_.setFromMatrixPosition(M_); if (Math.hypot(p_.x - cx, p_.z - cz) < rr || inFoot(p_.x, p_.z)) RM.setMatrixAt(n, Z_); } RM.instanceMatrix.needsUpdate = true; }
    if (today && MASS_MESH) for (const m_ of MASS_MESH) { const B_ = m_.geometry.attributes.iBox, D_ = m_.geometry.attributes.iDim, rr = Math.max(r * .5, 30 * scale);   // (the massing's parts: flat on their base)
      for (let n = 0; n < B_.count; n++) if (Math.hypot(B_.getX(n) - cx, B_.getY(n) - cz) < rr || inFoot(B_.getX(n), B_.getY(n))) D_.setXYZW(n, 0, 0, D_.getZ(n), D_.getZ(n)); D_.needsUpdate = true; }
    if (today && RIM_MESH) { const P_ = RIM_MESH.geometry.attributes.position, rr = Math.max(r * .5, 30 * scale);   // (and the rims: folded to the ground)
      for (let i = 0; i < P_.count; i++) if (Math.hypot(P_.getX(i) - cx, P_.getZ(i) - cz) < rr || inFoot(P_.getX(i), P_.getZ(i))) P_.setY(i, S.ground(P_.getX(i), P_.getZ(i)) - 1e-4); P_.needsUpdate = true; }
    return { centre: [cx, cz], folded, height_k: +k.toFixed(3) };
  }

  // a city's colours, made the first time it is shown (or warmed)
  function colour(m) {
    if (m.userData.mini) return; const id = idOf.get(m);
    m.userData.mini = m === cityMesh ? colourToday(m, today ? (film && MAT && MAT.today ? { ...TODAY[today], ...MAT.today, scale } : TODAY[today]) : undefined) : colourMesh(m, palOf(id), !!DET, { face: face(id), upright: uprightOf(id) }, { cell: 12 * scale, dark: (palOf(id).tree && palOf(id).tree.dark) || 1 }, film);
    if (film && MAT && MAT.soft && m !== cityMesh) softNormals(m.geometry);
    if (film) { const u = m === cityMesh ? null : S.eras[id].u, ruin = m === cityMesh ? null : new THREE.Color(palOf(id).parts[11]);
      const sk_ = m === cityMesh && (!!FPT.mesh || FPT.skipNow);   // (today's city with replacement footprints: its replaced buildings hidden, in its colours and its shadows alike)
      filmMaterial(S, m.userData.mini, u, ruin, fadeAt, u && S.fires[id] && S.fires[id].day ? S.fires[id] : null, BACK, FP_ && !!u, sk_); m.userData.miniDepth = filmMaterial(S, new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), u, null, fadeAt, null, BACK, false, sk_); }
  }
  // today's replacement footprints (a city's build/data/today_footprints.json, pipeline/footprints.py: opt-in, for this look only):
  // studio.js buildTodayFootprints's sparse geometry, its buildings in today's colours (each child its parent's paint and kind,
  // their aCtr shared), drawn on this look's layer alone; the replaced parents hidden in this look's colours and shadows (aSkip),
  // the white film's geometry and pictures untouched; loaded once, the first time today's city stands (it is large: the whole
  // city's). Their rooftops join today's (roofScan, split by child); a detailed model's fold reaches them too (FOLDS). A batch of
  // stills (nextShot) chooses them again for each shot, as the shot's own page would: the sidecar kept once read again, the
  // replacements made again where the choice differs from the shot before's
  const BATCH = typeof location !== 'undefined' && new URLSearchParams(location.search).has('shots');   // (a page that takes a batch of stills, render/still.mjs --shots: it keeps what a next shot takes again)
  const FPT = { tried: false, mesh: null, skip: 0, ms: 0, bytes: 0, side: null, keep: BATCH, sel: null, roofs0: null, skipNow: false }, FOLDS = [];
  const sidecar = () => FPT.side ||= fetch(dataDir + 'today_footprints.json').then(r => r.ok ? r.json() : null).catch(() => null);   // (its promise: kept while a batch of stills chooses again)
  const footprintsWait = () => !FPT.tried && film && MAT && dataDir && cityMesh && S.buildTodayFootprints && !(todayL() && todayL().footprints === false) && cityMesh.visible && TODAY_K.value.y > .002;
  // whether today's replacement footprints come in this frame (render): its rooftops are then made once, after them, not made
  // before them and dropped again
  const footprintsDue = async () => { if (!footprintsWait()) return false; const s_ = await sidecar(); return !!s_ && s_.enabled === true; };
  // today's materials as colour() makes them (colourToday's, on the film's deformation), [colour, shadow]: a replacement
  // footprint's, or today's city's own with its replaced buildings hidden (skip). The footprints' are made first and today's city's
  // after them, after whatever was made round the view before them, as on a page of its own: the renderer draws the objects in the
  // order their materials were made, and where two surfaces meet exactly that order decides a pixel
  const todayMats = (skip = false) => [filmMaterial(S, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .92, metalness: 0 }), null, null, fadeAt, null, BACK, false, skip),
    filmMaterial(S, new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), null, null, fadeAt, null, BACK, false, skip)];
  const cityMats = () => { const u_ = cityMesh.userData; if (u_.mini) { u_.mini.dispose(); u_.miniDepth.dispose(); } [u_.mini, u_.miniDepth] = todayMats(true); };
  async function todayFootprints(target, d) {
    if (!footprintsWait()) return; FPT.tried = true;
    const t0 = performance.now(); let side = await sidecar(); if (!FPT.keep) FPT.side = null;   // (a page of one shot lets it go)
    if (!side || side.enabled !== true) return;
    // (todayLight footprintsR: only the replacements within this many metres of where the camera looks, or [times the shot's
    // distance, at least metres]; none: the whole city. A still's: round its own target; the film's: round every place its camera
    // looks at (camPath), so the same replacements stand in every frame whichever frame a page begins on: a render's workers, a seek)
    const F_ = todayL() && todayL().footprintsR, at_ = (camPath && camPath()) || [[target.x, target.z, d]], R_ = p => Array.isArray(F_) ? Math.max(F_[1], F_[0] * p[2] / scale) : F_;
    let rep = side.replacements;
    if (F_) rep = rep.filter(r => { const g = r.children[0].rings[0], x = g.reduce((a_, p) => a_ + p[0], 0) / g.length, z = g.reduce((a_, p) => a_ + p[1], 0) / g.length; return at_.some(p => (x - p[0]) ** 2 + (z - p[1]) ** 2 < (R_(p) * scale) ** 2); });
    const sel = rep.map(r => r.bi).join(), same = sel === FPT.sel && !!FPT.mesh;   // (the parents replaced: a batch's shot that chooses the same keeps the shot before's)
    if (FPT.sel !== null) dropFootprints(same); FPT.sel = sel;
    const [mat, depth] = todayMats();
    if (same) { FPT.mesh.material = mat; FPT.mesh.customDepthMaterial = depth; cityMats(); return; }
    const { geometry, skipCentres, protectCentres } = await S.buildTodayFootprints({ ...side, replacements: rep }); if (!geometry) return;
    FPT.osm = new Set(skipCentres.filter((_, i) => rep[i].source !== 'regularized').map(([x, z]) => Math.fround(x) + ',' + Math.fround(z))); side = rep = null;   // (the parents whose children are OpenStreetMap's single buildings: never split, roofsMesh)
    FPT.protect = new Set((protectCentres || []).map(([x, z]) => Math.fround(x) + ',' + Math.fround(z)));   // (the reviewed parents: no massing on them, roofsMesh)
    geometry.deleteAttribute('aBi');   // (this look does not read it)
    const key = (x, z) => Math.fround(x) + ',' + Math.fround(z), skip = new Set(skipCentres.map(([x, z]) => key(x, z)));
    const G_ = cityMesh.geometry, C = G_.attributes.aCtr, n = C.count, A_ = G_.attributes.aSkip, a = A_ ? A_.array : new Uint8Array(n);   // (a byte a vertex; a shot after another: the same one written again)   // (the parents: their aCtr is the mean of their outer ring, as the sidecar's)
    for (let i = 0, lx = NaN, lz = NaN, v = 0; i < n; i++) { const x = C.getX(i), z = C.getY(i); if (x !== lx || z !== lz) { lx = x; lz = z; v = skip.has(key(x, z)) ? 1 : 0; if (v) FPT.skip++; } a[i] = v; }
    if (A_) A_.needsUpdate = true; else G_.setAttribute('aSkip', new THREE.BufferAttribute(a, 1));
    const fresh_ = !cityMesh.userData.mini; if (fresh_) { FPT.skipNow = true; colour(cityMesh); FPT.skipNow = false; }   // (today's city painted first: its kinds and paints, by each building's own record, its replaced buildings hidden at once)
    // each child in its parent's paint and kind exactly, read from the parent's own record (its wall's and its roof's colour, its
    // kind), never from the child's outline: a split or squared footprint changes no building's class
    const PC = G_.attributes.color, PK = G_.attributes.aKind, PN = G_.attributes.normal, PR = G_.userData.roofKind, par = new Map();
    for (let i = 0; i < n; i++) { if (!a[i]) continue; const k = key(C.getX(i), C.getY(i)); let e = par.get(k); if (!e) par.set(k, e = { w: null, r: null, kd: PK ? PK.getX(i) : 1, rk: PR ? PR[i] : 0 });
      if (PN.getY(i) > .6) { if (!e.r) e.r = [PC.getX(i), PC.getY(i), PC.getZ(i)]; } else if (!e.w) e.w = [PC.getX(i), PC.getY(i), PC.getZ(i)]; }
    { const FC = geometry.attributes.aCtr, FN = geometry.attributes.normal, m_ = FC.count, col = new Float32Array(m_ * 3), kd = new Float32Array(m_), rk = PR ? new Uint8Array(m_) : null; FPT.miss = 0;
      for (let i = 0; i < m_; i++) { const e = par.get(key(FC.getX(i), FC.getY(i))), c = e ? (FN.getY(i) > .6 ? e.r || e.w : e.w || e.r) : null;
        if (c) { col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2]; } else { col.fill(.9, i * 3, i * 3 + 3); FPT.miss++; } kd[i] = e ? e.kd : 1; if (rk) rk[i] = e ? e.rk : 1; }   // (miss: a child whose parent was not found: none expected)
      // (and its roof kind, its parent's: whether the sidecar stands or not, one kind; roofsMesh draws it, or its flat member, by the child's own outline)
      geometry.setAttribute('color', new THREE.BufferAttribute(col, 3)); if (rk) geometry.userData.roofKind = rk; geometry.setAttribute('aKind', new THREE.BufferAttribute(kd, 1)); geometry.setAttribute('aTop', new THREE.BufferAttribute(recordTops(geometry), 1)); if (todayL() && todayL().bevel) geometry.setAttribute('aEdge', new THREE.BufferAttribute(wallEdges(geometry, scale), 2)); }
    const mesh = new THREE.Mesh(geometry, mat); mesh.customDepthMaterial = depth;
    mesh.castShadow = mesh.receiveShadow = true; mesh.frustumCulled = false; mesh.layers.set(L); scene.add(mesh); FPT.mesh = mesh;
    if (!fresh_) cityMats();   // (its materials again, with aSkip, where it was painted before)
    for (const f of FOLDS) foldIn(geometry, f);   // (a detailed model already in place)
    if (ROOFS) { FPT.roofs0 ||= ROOFS; ROOFS = FPT.roofs0.filter(r => !(r[11] === G_.attributes.position && a[r[9]] > .5)).concat(roofScan(geometry, true)); dropRoofs(); }
    FPT.ms = performance.now() - t0; FPT.bytes = Object.values(geometry.attributes).reduce((s_, at) => s_ + at.array.byteLength, 0) + a.byteLength;
    console.log('footprints', JSON.stringify({ parents: FPT.skip, unmatched: FPT.miss, vertices: geometry.attributes.position.count, MB: +(FPT.bytes / 1e6).toFixed(1), ms: Math.round(FPT.ms) }));
  }
  function dropFootprints(same) {   // (the shot before's replacements gone, their parents standing again; same: kept, their materials made again) and today's rooftops made again after them
    if (FPT.mesh) { FPT.mesh.material.dispose(); FPT.mesh.customDepthMaterial.dispose(); if (!same) { scene.remove(FPT.mesh); FPT.mesh.geometry.dispose(); FPT.mesh = null; } }
    const A_ = cityMesh.geometry.attributes.aSkip; if (A_ && !same) { A_.array.fill(0); A_.needsUpdate = true; FPT.skip = 0; }
    if (FPT.roofs0) { ROOFS = same ? ROOFS : FPT.roofs0; dropRoofs(); }
  }
  // a batch of stills on one page (render/still.mjs --shots, main.js SHOT): the next shot as its own page would draw it. What the
  // look made round the first frame's view is made again round the next frame's (the trees, the boats, the groves, today's
  // replacement footprints), and the built-up mask as on a page's first frame (the groves come in the frame after it, flockAt);
  // STILL_KEYS, the picture's keys (?pic=) read only as a frame is drawn, take the shot's values (a shot that differs from the page in
  // any other key needs a page of its own: main.js SHOT.fits)
  const STILL_KEYS = ['sunSide', 'todayLight.sunLeft'];
  function nextShot(pic = {}) {
    for (const k of STILL_KEYS) { const [a, b] = k.split('.'), v = b ? pic[a] && pic[a][b] : pic[a]; if (v === undefined) continue;
      if (b) FILM_PIC[a] = { ...FILM_PIC[a], [b]: v }; else FILM_PIC[a] = v; }
    TF.reset(); FPT.tried = false; FPT.keep = true;   // (the trees and the boats stand in the world: nothing to plant again)
    for (const U_ of [BUILT, TREES]) if (U_.value) { U_.value.dispose(); U_.value = null; } BUILT_K = null;
  }
  // the programs of every city's colours made before playback (main.js warm-up: else the first frame a city shows stalls; and
  // tools/phonecheck.mjs sees them all)
  function warmUp() {
    const keep = [...eraMeshes, cityMesh, plate].filter(Boolean).map(m => [m, m.visible, m.material, m.layers.mask]), lay0 = camera.layers.mask;
    for (const [m] of keep) { colour(m); m.visible = true; m.material = m.userData.mini || m.material; m.layers.enable(L); }
    camera.layers.set(L); renderer.compile(scene, camera); camera.layers.mask = lay0;
    for (const [m, v, mat, mask] of keep) { m.visible = v; m.material = mat; m.layers.mask = mask; }
  }
  // the sun's shadow fitted to the ground the frame shows (the frame's corners and edges where they meet the ground, the far edge
  // held within a few distances of the target, raised by a tall building): the whole shadow map's texels on what is seen
  const SH = { ray: new THREE.Vector3(), cam: new THREE.OrthographicCamera(), p: new THREE.Vector3(), q: [] };   // (a camera: its lookAt turns -z to the target, as the shadow's own camera does; an Object3D turned +z, so the fitted depth range came out behind the light and no shadow was cast)
  function fitShadow(c, light, target, d) {
    camera.updateMatrixWorld(); const pts = [], H = 150 * scale;   // (H: a tall building, exaggerated)
    for (const [x, y] of [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]) {
      const ray = SH.ray.set(x, y, .5).unproject(camera).sub(camera.position).normalize();
      const k = Math.min(ray.y < -1e-4 ? (target.y - camera.position.y) / ray.y : Infinity, d * 3.5);
      const g = camera.position.clone().addScaledVector(ray, k); pts.push(g, g.clone().setY(g.y + H)); }
    SH.cam.position.copy(light.position); SH.cam.lookAt(target); SH.cam.updateMatrixWorld(); const inv = SH.cam.matrixWorld.clone().invert();
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (const g of pts) { const v = SH.p.copy(g).applyMatrix4(inv); x0 = Math.min(x0, v.x); x1 = Math.max(x1, v.x); y0 = Math.min(y0, v.y); y1 = Math.max(y1, v.y); z0 = Math.min(z0, v.z); z1 = Math.max(z1, v.z); }
    const m = (x1 - x0 + y1 - y0) * .02;
    c.left = x0 - m; c.right = x1 + m; c.bottom = y0 - m; c.top = y1 + m; c.near = Math.max(1e-5, -z1 - H * 3); c.far = -z0 + H * 3;
  }
  // today's city's state for the base and the groves (TODAY_K), and its year maps (todayYears): before the groves are planted
  // today's rooftops (a material's): a parapet (a rim a metre high) round every simple flat roof from 8 m, a plant room on those from 20 m; they follow the
  // year and stand only while today's city is the subject (TODAY_K)
  let ROOF_MESH = null;
  const ROOF_KEEP = { n: -1, m: null };   // (roofsMesh, a batch of stills: each record's pieces as last made, while the detailed models stand as they did)
  let RIM_MESH = null;   // (the convex roofs' rims, one mesh)
  let MASS_MESH = null;   // (the massing's parts: today's material on instanced boxes and cylinders, one mesh each)
  const dropRoofs = () => { for (const m of [...(ROOF_MESH || []), ...(RIM_MESH ? [RIM_MESH] : [])]) { scene.remove(m); m.geometry.dispose(); }
    for (const m of MASS_MESH || []) { scene.remove(m); m.geometry.dispose(); m.material.dispose(); m.customDepthMaterial.dispose(); } ROOF_MESH = RIM_MESH = MASS_MESH = null; };   // (made again by roofsMesh)
  // a massing part on today's material (todayMats): each instance a box or a cylinder (iBox: its centre x z, its bearing; iDim: its
  // half sides, its bottom and top), its building's own attributes per instance, its top in its roof's paint (aRoofC); folded away
  // while the growth raises the city (uRoofOn): drawn whole inside their building's full mass, revealed as it is cut
  const massMat = (m, depth) => { const ob = m.onBeforeCompile, ck = m.customProgramCacheKey;
    m.onBeforeCompile = (sh, r) => { ob(sh, r);
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec4 iBox, iDim; attribute vec3 aRoofC;')
        .replace('#include <beginnormal_vertex>', `#include <beginnormal_vertex>
  { float c_ = cos(iBox.z), s_ = sin(iBox.z); vec3 n_ = normalize(vec3(objectNormal.x / max(iDim.x, 1e-9), objectNormal.y, objectNormal.z / max(iDim.y, 1e-9))); objectNormal = vec3(c_ * n_.x - s_ * n_.z, n_.y, s_ * n_.x + c_ * n_.z); }`)
        .replace('#include <begin_vertex>', `#include <begin_vertex>
  { float c_ = cos(iBox.z), s_ = sin(iBox.z); vec2 l_ = position.xz * 2. * iDim.xy; transformed = vec3(iBox.x + c_ * l_.x - s_ * l_.y, mix(iDim.z, iDim.w, position.y), iBox.y + s_ * l_.x + c_ * l_.y); }`);   // (whole inside its building's full mass: revealed as that mass is cut, uRoofOn)
      if (!depth) sh.vertexShader = sh.vertexShader.replace('#include <color_vertex>', '#include <color_vertex>\n  if (normal.y > .6) vColor.rgb = aRoofC;'); };
    m.customProgramCacheKey = () => (ck ? ck.call(m) : '') + ' mass'; return m; };
  // today's buildings in schematic massing (todayLight massing), inside the data's envelope only: nothing outside the footprint, nothing
  // above the building's height; deterministic by the building's centre, by its height and its footprint's size, for any city:
  // tower: from this height m a podium, on a box-like or round footprint only (a faceted tower keeps its own shaft, only its crown set in; podium: [its footprint's least half side m, the share of towers, its storeys [from, to], at most
  // this share of the height, the shaft's inset [share of the least half side, at least m, at most m]]) and a crown (crown: [always from
  // this height m, else the share, its storeys, its inset m]); set: a mid-rise's upper setback ([from this height m, the share, its
  // storeys [from, to], the inset [from, to] m, the share set in all round; else stepped back from one end]); step: a low building's
  // roof stepped ([the share, the stepped part's share of the long side [from, to]]); min: [height m, least half side m]; storey m.
  // Never on the reviewed parents (FPT.protect), a detailed model's footprint, or a roof too small; the colour look only.
  // whether a box (centre x z, half sides hu hv along the footprint's axes, a margin mg; sh: a cylinder) lies inside a footprint's outline
  const insideOf = ({ c, sn, fits, hull }) => (x, z, hu, hv, sh, mg) => { if (!sh && hull) return fits(x, z, hu, hv, mg);   // (a convex outline: its corners inside it, the box is)
    if (!sh) { for (const [p, q] of MASS_GRID) { const u = p * (hu + mg), v = q * (hv + mg); if (!fits(x + c * u - sn * v, z + sn * u + c * v, 0, 0, 0)) return false; } return true; }   // (a concave one: its corners, its sides' middles and its centre on its own top, no box over a courtyard)
    for (let k = 0; k < 12; k++) { const t = k * Math.PI / 6, u = Math.cos(t) * (hu + mg), v = Math.sin(t) * (hv + mg), X = x + c * u - sn * v, Z = z + sn * u + c * v; if (hull ? hullIn(hull, X, Z) < 0 : !fits(X, Z, 0, 0, 0)) return false; } return true; };
  // a large footprint split into buildings (massing split: the data records a whole block, or a merged plot, as one footprint):
  // rows of units along its long sides (bands of depth[0] to depth[1] m, as many as its depth holds, lane m between them), each
  // band cut across into frontages of width[0] to width[1] m, the last one taking a short remainder (tools/parcels.py's rows of
  // shop-houses along a street front, in the footprint's own frame); every unit inside the outline, its own height in whole
  // storeys (h[0] to all of the data's, never above it), its own paint by its own kind (kindPaint: the old fabric under oldH,
  // else a home; a stone block's units `stone` of them stone), lanes between them on the footprint's own mass cut to its base.
  // Not a tower's glass (kind 2) nor anything from maxH m up. By the footprint's hash: any camera, the same
  const splitPlan = (MS, R0, h0) => { const SP = MS.split, { cx, cz, c, sn, a, b, y1, yb, hm } = R0, m = scale, inside = insideOf(R0);
    const hq = k => { const t = Math.sin(h0 * 1e5 + k * 78.233) * 43758.5453; return t - Math.floor(t); };
    const lu = a >= b, A = lu ? a : b, B = lu ? b : a, ln = SP.lane * m, D0 = (SP.depth[0] + (SP.depth[1] - SP.depth[0]) * hq(1)) * m;
    const nb = Math.max(1, Math.floor((2 * B + ln) / (D0 + ln))), Db = (2 * B + ln) / nb - ln, st = (y1 - yb) / hm * MS.storey, ns = Math.max(1, Math.floor(hm / MS.storey)), parts = [];
    for (let j = 0; j < nb; j++) { const v = -B + Db / 2 + j * (Db + ln); let u = -A;
      for (let k = 0; u < A - 2 * m && k < 400; k++) { let u1 = Math.min(A, u + (SP.width[0] + (SP.width[1] - SP.width[0]) * hq(10 + j * 37 + k)) * m); if (A - u1 < SP.width[0] * m * .6) u1 = A;
        const hu = (u1 - u - ln) / 2, hv = Db / 2, um = (u + u1) / 2, U_ = lu ? um : v, V_ = lu ? v : um, x = cx + c * U_ - sn * V_, z = cz + sn * U_ + c * V_, ha = lu ? hu : hv, hb = lu ? hv : hu;
        let f_ = 1; while (f_ > .6 && !(hu * f_ > 2 * m && hv * f_ > 2 * m && inside(x, z, ha * f_, hb * f_, 0, .3 * m))) f_ -= .15;   // (where the outline bends: the unit smaller, its centre kept)
        if (f_ > .6) { const ha_ = ha * f_, hb_ = hb * f_, n = Math.max(1, Math.min(ns, Math.round(ns * (SP.h[0] + (1 - SP.h[0]) * hq(200 + j * 41 + k)))));
          parts.push([x, z, 0, ha_, hb_, yb, Math.min(y1, yb + n * st), { q: hq(300 + j * 43 + k), q2: hq(400 + j * 47 + k), hm: Math.min(hm, n * MS.storey), inner: j > 0 && j < nb - 1 && k > 0 && u1 < A - 2 * m }]); }   // (inner: off every side of the footprint, a block's courtyard)
        u = u1; } }
    return parts.length >= 2 ? { cut: yb, parts, kind: 'split' } : null; };
  const massPlan = (MS, R0) => { const { cx, cz, c, sn, y1, yb, hm, round, fits, hull } = R0; let { a, b } = R0;
    const hq = k => { const t = Math.sin(cx * 9.731e4 + cz * 3.173e4 + k * 78.233) * 43758.5453; return t - Math.floor(t); };
    const st = (y1 - yb) / hm * MS.storey, m = scale, L = (f, x) => f[0] + (f[1] - f[0]) * x;
    const inside = insideOf(R0);
    const sh = round ? 1 : 0, parts = []; let cut = null, kind = '';
    { let k = 0; for (; k < 12 && !inside(cx, cz, a, b, sh, 0); k++) { a *= .93; b *= .93; } if (k === 12) return null; }   // (the footprint's own box shrunk till it lies inside the outline: its extent's box pokes out of any outline not square to its axes)
    const R = { ...R0, a, b };
    const within = () => true;   // (every part lies in that box: tested once, above)
    if (hm >= MS.tower) {
      const P = MS.podium, C = MS.crown, pod = ((round && hull.length >= 10) || R0.fill >= .85) && Math.min(a, b) >= P[0] * m && hq(1) < P[1], cro = hm >= C[0] || hq(3) < C[1];
      let ha = a, hb = b, top = y1;
      const hc = cro ? (C[2] + (hq(4) < .5 ? 1 : 0)) * st : 0;
      if (pod) { const hp = Math.min((P[2][0] + Math.floor(hq(2) * (P[2][1] - P[2][0] + 1))) * st, P[3] * (y1 - yb)), d = THREE.MathUtils.clamp(P[4][0] * Math.min(a, b), P[4][1] * m, P[4][2] * m);
        if (a - d >= 4 * m && b - d >= 4 * m && within(cx, cz, a - d, b - d, sh, .3 * m)) { ha = a - d; hb = b - d; cut = yb + hp; kind = 'podium'; parts.push([cx, cz, sh, ha, hb, yb + hp, cro ? y1 - hc : y1]); } }
      if (cro && ha - C[3] * m >= 3 * m && hb - C[3] * m >= 3 * m && within(cx, cz, ha - C[3] * m, hb - C[3] * m, sh, .3 * m)) {
        if (cut === null) cut = y1 - hc; kind += 'crown'; parts.push([cx, cz, sh, ha - C[3] * m, hb - C[3] * m, y1 - hc, y1]); }
      else if (parts.length) parts[0][6] = y1; }
    if (!parts.length && hm >= MS.set[0] && hq(5) < MS.set[1]) {   // an upper setback, all round or stepped back from one end
      const S_ = MS.set, ns = S_[2][0] + Math.floor(hq(6) * (S_[2][1] - S_[2][0] + 1)), d = L(S_[3], hq(8)) * m;
      if (y1 - ns * st - yb >= st) { cut = y1 - ns * st;
        if (round || hq(7) < S_[4]) { kind = 'setback'; if (a - d >= 3 * m && b - d >= 3 * m && within(cx, cz, a - d, b - d, sh, .3 * m)) parts.push([cx, cz, sh, a - d, b - d, cut, y1]); }
        else { kind = 'setback-end'; parts.push(...stepPart(R, L(MS.step[1], hq(10)), hq(11), cut, within)); } } }
    if (!parts.length && hm < MS.set[0] && hq(9) < MS.step[0] && y1 - st - yb >= st && !round) { cut = y1 - st; kind = 'step'; parts.push(...stepPart(R, L(MS.step[1], hq(10)), hq(11), cut, within)); }
    return parts.length ? { cut, parts, kind } : null; };
  // what roofsMesh makes of a record's roof, by its geometry and first vertex: { k: the kind it shows (its own, pitched; its flat
  // member; 11 over the massing's podium or under its setback), plan: its massing plan (massPlan's kind), units: a split
  // footprint's units [x, top, z, kind, m2, height m, its block's year, long and short side m, 1, '', its block's height m,
  // whether inner, its block's roof kind, its block's centre x z] }. roofList: every building of today's standing [its centre x,
  // top, z, the roof kind it shows, footprint m2, height m, year, least rectangle's long and short side m, the share of it filled,
  // its massing plan, 0, 0, its roof kind (its parent's: roofClass), its parent's centre x z] and the units in their place (a
  // script's check of the kinds and their shares in a frame, window.__MINI.roofs)
  const ROOF_K = new Map();
  const roofList = (near = null) => { const out = [];   // (near [x, z, r]: only the buildings whose centre lies within r of x, z)
    for (const G_ of [cityMesh && cityMesh.geometry, FPT.mesh && FPT.mesh.geometry]) { const rk = G_ && G_.userData.roofKind; if (!rk) continue; const sk = G_.attributes.aSkip, P = G_.attributes.position;
      const C_ = G_.attributes.aCtr;
      for (const [x, z, , , , y1, yr, hm, , i0, i1] of roofScan(G_, G_ !== cityMesh.geometry)) { if ((sk && sk.array[i0]) || (near && Math.hypot(x - near[0], z - near[1]) > near[2])) continue; const o = ROOF_K.get(G_.uuid + ':' + i0) || {};
        if (o.units) { out.push(...o.units); continue; }
        let ar = 0; for (let i = i0; i + 2 < i1; i += 3) if (Math.abs(P.getY(i) - y1) + Math.abs(P.getY(i + 1) - y1) + Math.abs(P.getY(i + 2) - y1) < 1e-7)
          ar += Math.abs((P.getX(i + 1) - P.getX(i)) * (P.getZ(i + 2) - P.getZ(i)) - (P.getX(i + 2) - P.getX(i)) * (P.getZ(i + 1) - P.getZ(i))) / 2;
        const f = recordForm(P, G_.attributes.normal, i0, i1, ar, scale);
        out.push([x, y1, z, o.k || rk[i0], ar / scale / scale, hm, yr, f.L, f.W, f.fill, o.plan || '', 0, 0, rk[i0], C_.getX(i0), C_.getY(i0)]); } }
    return out; };
  // the parts as meshes and the main masses cut (aCut: a byte a vertex, 0 none, else the share of its height, of 255, where it ends)
  const MASS = { parts: 0, bytes: 0, kinds: {}, kept: 0 }, MASS_GRID = [[-1, -1], [1, 1], [1, -1], [-1, 1], [0, 0], [-1, 0], [1, 0], [0, -1], [0, 1]];   // (the corners first: most boxes that fail, fail there)
  const massMesh = (parts, cuts) => {
    const MS = todayL() && todayL().massing;
    for (const G_ of [cityMesh && cityMesh.geometry, FPT.mesh && FPT.mesh.geometry]) { if (!G_) continue; let A_ = G_.attributes.aCut;
      if (!A_ && (MS || cuts.length)) G_.setAttribute('aCut', A_ = new THREE.BufferAttribute(new Uint8Array(G_.attributes.position.count), 1));
      if (A_) { A_.array.fill(0); A_.needsUpdate = true; } }
    for (const [G_, i0, i1, v] of cuts) if (G_.attributes.aCut) G_.attributes.aCut.array.fill(v, i0, i1);
    MASS.parts = parts.length; MASS.bytes = 0; if (!parts.length) return;
    MASS_MESH = [];
    for (const shp of [0, 1]) { const ps = parts.filter(q => q[2] === shp), n = ps.length; if (!n) continue;
      const base = shp ? new THREE.CylinderGeometry(.5, .5, 1, 20, 1).translate(0, .5, 0) : new THREE.BoxGeometry(1, 1, 1).translate(0, .5, 0), g = new THREE.InstancedBufferGeometry();
      g.index = base.index; g.setAttribute('position', base.attributes.position); g.setAttribute('normal', base.attributes.normal); g.instanceCount = n;
      const F = k => new Float32Array(n * k), at = { iBox: F(4), iDim: F(4), aData: F(4), aBase: F(1), aCtr: F(2), aGrowH: F(3), aGrowT: F(1), color: F(3), aRoofC: F(3), aKind: F(1), aTop: F(1), aEdge: F(2) };
      ps.forEach(([x, z, , hu, hv, y0, y1, th, G_, i0, wi, ri, own], j) => { const A = G_.attributes;
        at.iBox.set([x, z, th, shp], j * 4); at.iDim.set([hu, hv, y0, y1], j * 4);
        for (const [k, w] of [['aData', 4], ['aBase', 1], ['aCtr', 2], ['aGrowH', 3], ['aGrowT', 1], ['aKind', 1]]) if (A[k]) for (let e = 0; e < w; e++) at[k][j * w + e] = A[k].array[i0 * w + e];
        for (let e = 0; e < 3; e++) { at.color[j * 3 + e] = A.color.array[wi * 3 + e]; at.aRoofC[j * 3 + e] = A.color.array[ri * 3 + e]; }
        if (own) { const kv = .95 + .1 * ((own.h * 7.13) % 1); at.color.set([own.wall.r * kv, own.wall.g * kv, own.wall.b * kv], j * 3); at.aRoofC.set([own.roof.r * kv, own.roof.g * kv, own.roof.b * kv], j * 3);   // (a split unit: a building of its own, its paint, its kind, its centre and hash)
          at.aKind[j] = own.k; at.aCtr.set([x, z], j * 2); at.aData[j * 4 + 1] = own.hm; at.aData[j * 4 + 2] = own.h; }
        at.aTop[j] = y1; at.aEdge[j * 2] = at.aEdge[j * 2 + 1] = 65535; });
      for (const [k, v] of Object.entries(at)) { g.setAttribute(k, new THREE.InstancedBufferAttribute(v, v.length / n)); MASS.bytes += v.byteLength; }
      const [mat, depth] = todayMats(); const mesh = new THREE.Mesh(g, massMat(mat, false)); mesh.customDepthMaterial = massMat(depth, true);
      mesh.castShadow = mesh.receiveShadow = true; mesh.frustumCulled = false; mesh.layers.set(L); scene.add(mesh); MASS_MESH.push(mesh); }
    for (const G_ of [cityMesh && cityMesh.geometry, FPT.mesh && FPT.mesh.geometry]) if (G_ && G_.attributes.aCut) MASS.bytes += G_.attributes.aCut.array.byteLength;
    console.log('massing', JSON.stringify({ parts: MASS.parts, cut: cuts.length, kinds: MASS.kinds, large: MASS.why, protected: MASS.kept, MB: +(MASS.bytes / 1e6).toFixed(1) })); };
  // the pitched roofs (roofsMesh pitch) as meshes, today's material on two instanced unit roofs, hips and gables (pitchGeo): the
  // eaves' corners at (+-1, 0, +-1), the ridge's ends at (+-1, 1, 0), stretched per roof (iBox: its centre x z, its bearing, the
  // ridge's half length; iDim: its half length and width, its eaves and its ridge), each face's normal from its own pitch (its
  // normal attribute a code: a slope over a long side (0, 1, +-1), over an end (+-1, 1, 0), a gable's end (+-1, 0, 0), upright
  // and in its wall's paint); its building's own attributes per instance (its year, rise and growth; a lane house's its own
  // centre, height and hash), the slopes in their roof's paint (aRoofC), their tiles drawn by FACADE_GLSL (aKind 5); whole inside
  // its building's full mass while the growth raises the city, as the walls stand uncut again (uRoofOn)
  const pitchGeo = gable => { const pos = [], nrm = [], R = gable ? 2 : 1, at = ([u, y, v]) => y > .5 ? [u * R, 1, 0] : [u * 2, 0, v];   // (a stand-in roof, 4 by 2 by 1, to wind each face outward)
    const face = (P, n) => { for (let i = 0; i + 2 < P.length; i++) { let [p0, p1, p2] = [P[0], P[i + 1], P[i + 2]]; const A = at(p0), B = at(p1), C = at(p2);
        const e1 = [B[0] - A[0], B[1] - A[1], B[2] - A[2]], e2 = [C[0] - A[0], C[1] - A[1], C[2] - A[2]], cr = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]];
        if (cr[0] * n[0] + cr[1] * n[1] + cr[2] * n[2] < 0) [p1, p2] = [p2, p1];
        for (const q of [p0, p1, p2]) { pos.push(...q); nrm.push(...n); } } };
    face([[-1, 0, 1], [1, 0, 1], [1, 1, 0], [-1, 1, 0]], [0, 1, 1]); face([[1, 0, -1], [-1, 0, -1], [-1, 1, 0], [1, 1, 0]], [0, 1, -1]);
    face([[1, 0, 1], [1, 0, -1], [1, 1, 0]], [1, gable ? 0 : 1, 0]); face([[-1, 0, -1], [-1, 0, 1], [-1, 1, 0]], [-1, gable ? 0 : 1, 0]);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3)); return g; };
  const pitchMat = (m, depth) => { const ob = m.onBeforeCompile, ck = m.customProgramCacheKey;
    m.onBeforeCompile = (sh, r) => { ob(sh, r);
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec4 iBox, iDim; attribute vec3 aRoofC;')
        .replace('#include <beginnormal_vertex>', `#include <beginnormal_vertex>
  { float c_ = cos(iBox.z), s_ = sin(iBox.z), hr_ = iDim.w - iDim.z; vec3 o_ = objectNormal;
    vec3 n_ = normalize(o_.y > .5 ? (abs(o_.z) > .5 ? vec3(0., iDim.y, o_.z * hr_) : vec3(o_.x * hr_, max(iDim.x - iBox.w, 1e-9), 0.)) : vec3(o_.x, 0., 0.));
    objectNormal = vec3(c_ * n_.x - s_ * n_.z, n_.y, s_ * n_.x + c_ * n_.z); }`)
        .replace('#include <begin_vertex>', `#include <begin_vertex>
  { float c_ = cos(iBox.z), s_ = sin(iBox.z); vec2 l_ = position.y > .5 ? vec2(position.x * iBox.w, 0.) : position.xz * iDim.xy;
    transformed = vec3(iBox.x + c_ * l_.x - s_ * l_.y, mix(iDim.z, iDim.w, position.y), iBox.y + s_ * l_.x + c_ * l_.y); }`);
      if (!depth) sh.vertexShader = sh.vertexShader.replace('#include <color_vertex>', '#include <color_vertex>\n  if (normal.y > .5) vColor.rgb = aRoofC;'); };
    m.customProgramCacheKey = () => (ck ? ck.call(m) : '') + ' pitch'; return m; };
  const pitchMesh = pitch => { if (!pitch.length) return; MASS_MESH ||= [];
    for (const gable of [false, true]) { const ps = pitch.filter(e => e[0].gable === gable), n = ps.length; if (!n) continue;
      const base = pitchGeo(gable), g = new THREE.InstancedBufferGeometry(); g.setAttribute('position', base.attributes.position); g.setAttribute('normal', base.attributes.normal); g.instanceCount = n;
      const F = k => new Float32Array(n * k), at = { iBox: F(4), iDim: F(4), aData: F(4), aBase: F(1), aCtr: F(2), aGrowH: F(3), aGrowT: F(1), color: F(3), aRoofC: F(3), aKind: F(1), aTop: F(1), aEdge: F(2) };
      ps.forEach(([pr, G_, i0, wall, roof], j) => { const A = G_.attributes;
        at.iBox.set([pr.cx, pr.cz, pr.th, pr.ridge], j * 4); at.iDim.set([pr.hl, pr.hw, pr.y0, pr.y1], j * 4);
        for (const [k, w] of [['aData', 4], ['aBase', 1], ['aCtr', 2], ['aGrowH', 3], ['aGrowT', 1]]) if (A[k]) for (let e = 0; e < w; e++) at[k][j * w + e] = A[k].array[i0 * w + e];
        if (pr.unit) { at.aCtr.set([pr.unit.x, pr.unit.z], j * 2); at.aData[j * 4 + 1] = pr.unit.hm; at.aData[j * 4 + 2] = pr.unit.h; }
        const kv = .95 + .1 * ((at.aData[j * 4 + 2] * 7.13) % 1); at.color.set([wall.r, wall.g, wall.b], j * 3); at.aRoofC.set([roof.r * kv, roof.g * kv, roof.b * kv], j * 3);
        at.aKind[j] = 5; at.aTop[j] = pr.y1; at.aEdge[j * 2] = at.aEdge[j * 2 + 1] = 65535; });
      for (const [k, v] of Object.entries(at)) { g.setAttribute(k, new THREE.InstancedBufferAttribute(v, v.length / n)); MASS.bytes += v.byteLength; }
      const [mat, depth] = todayMats(); const mesh = new THREE.Mesh(g, pitchMat(mat, false)); mesh.customDepthMaterial = pitchMat(depth, true);
      mesh.castShadow = mesh.receiveShadow = true; mesh.frustumCulled = false; mesh.layers.set(L); scene.add(mesh); MASS_MESH.push(mesh); }
    console.log('pitched roofs', JSON.stringify({ n: pitch.length, gables: pitch.filter(e => e[0].gable).length })); };
  const stepPart = ({ cx, cz, c, sn, a, b, y1 }, f, side, y0, inside) => {   // (the higher part over f of the long side, from one end, a hair in from its walls)
    const lu = a >= b, A = lu ? a : b, B = lu ? b : a, i = .3 * scale, hl = f * A - i, hs = B - i, o = (side < .5 ? -1 : 1) * (A - f * A), u = lu ? o : 0, v = lu ? 0 : o;
    const x = cx + c * u - sn * v, z = cz + sn * u + c * v, hu = lu ? hl : hs, hv = lu ? hs : hl;
    return hl > 2 * scale && hs > 2 * scale && inside(x, z, hu, hv, 0, 0) ? [[x, z, 0, hu, hv, y0, y1]] : []; };
  const foldIn = (g, f) => { const P = g.attributes.position, C = g.attributes.aCtr; let hit = false;   // (a detailed model's fold, swap: what stands at its centre or inside its footprint to the ground)
    for (let i = 0; i < P.count; i++) { const x = C.getX(i), z = C.getY(i); if (Math.abs(x - f.cx) < 2e-7 && Math.abs(z - f.cz) < 2e-7 || f.inFoot(x, z)) { P.setXYZ(i, x, S.ground(x, z) - 1e-4, z); hit = true; } }
    if (hit) P.needsUpdate = true; };
  // a top's triangles (the record's own, at its roof's height): a concave roof's outline
  const topTris = (i0, i1, P_, y1, tol) => { const t = []; for (let i = i0; i + 2 < i1; i += 3) if (Math.abs(P_.getY(i) - y1) + Math.abs(P_.getY(i + 1) - y1) + Math.abs(P_.getY(i + 2) - y1) < tol) t.push([P_.getX(i), P_.getZ(i), P_.getX(i + 1), P_.getZ(i + 1), P_.getX(i + 2), P_.getZ(i + 2)]); return t; };
  // a concave top, whether a point is on it: its triangles tested, or for a larger top (more than 4 triangles: testing every one
  // for every point cost seconds on the whole city's large outlines) a raster in its own axes, cells of half a metre (at most 256
  // a side), drawn once
  const topGrid = (T, cx, cz, c, sn, a, b, R = null) => { if (T.length <= 4) return (x, z) => T.some(([ax, az, bx, bz, qx, qz]) => { const d1 = (x - bx) * (az - bz) - (ax - bx) * (z - bz), d2 = (x - qx) * (bz - qz) - (bx - qx) * (z - qz), d3 = (x - ax) * (qz - az) - (qx - ax) * (z - az);
      return !((d1 < 0 || d2 < 0 || d3 < 0) && (d1 > 0 || d2 > 0 || d3 > 0)); });
    const { g, nu, nv, cs, lu, lv } = R || topRaster(T, cx, cz, c, sn, a, b);   // (R: the raster, drawn already)
    return (x, z) => { const i = Math.floor((lu(x, z) + a) / cs), j = Math.floor((lv(x, z) + b) / cs); return i >= 0 && j >= 0 && i < nu && j < nv && g[j * nu + i] === 1; }; };
  // a top's raster in its own axes (cell i, j: u from -a + i cs, v from -b + j cs; a cell set where its centre lies on the top)
  const topRaster = (T, cx, cz, c, sn, a, b) => {
    const cs = Math.max(.5 * scale, 2 * Math.max(a, b) / 256), nu = Math.ceil(2 * a / cs) + 2, nv = Math.ceil(2 * b / cs) + 2, g = new Uint8Array(nu * nv);
    const lu = (x, z) => (x - cx) * c + (z - cz) * sn, lv = (x, z) => -(x - cx) * sn + (z - cz) * c;
    for (const [ax, az, bx, bz, qx, qz] of T) { const P3 = [[lu(ax, az), lv(ax, az)], [lu(bx, bz), lv(bx, bz)], [lu(qx, qz), lv(qx, qz)]];   // (row by row: each row's span of the triangle)
      const j0 = Math.max(0, Math.ceil((Math.min(P3[0][1], P3[1][1], P3[2][1]) + b) / cs - .5)), j1 = Math.min(nv - 1, Math.floor((Math.max(P3[0][1], P3[1][1], P3[2][1]) + b) / cs - .5));
      for (let j = j0; j <= j1; j++) { const v = -b + (j + .5) * cs; let u0 = Infinity, u1 = -Infinity;
        for (let e = 0; e < 3; e++) { const [p0, p1] = [P3[e], P3[(e + 1) % 3]]; if ((v < p0[1]) === (v < p1[1]) && v !== p0[1]) continue; const t = p1[1] === p0[1] ? 0 : (v - p0[1]) / (p1[1] - p0[1]), u = p0[0] + (p1[0] - p0[0]) * t; if (u < u0) u0 = u; if (u > u1) u1 = u; }
        if (!(u1 >= u0)) continue; const i0 = Math.max(0, Math.ceil((u0 + a) / cs - .5)), i1 = Math.min(nu - 1, Math.floor((u1 + a) / cs - .5)); for (let i = i0; i <= i1; i++) g[j * nu + i] = 1; } }
    return { g, nu, nv, cs, lu, lv }; };
  // a raster's largest rectangles of set cells, each at least k cells a side, one after another (the cells each takes cleared),
  // at most n, till they cover this share of its cells: [i0, i1, j0, j1] each (the largest rectangle under each row's histogram)
  const RECT_ = { s: new Int32Array(0), h: new Int32Array(0), H: new Int32Array(0) };   // (rectsOf's stacks and histogram, kept)
  // a raster f times coarser (a cell set where all of its f x f are): the same origin
  const coarse = (R, f) => { if (f <= 1) return R; const nu = Math.floor(R.nu / f), nv = Math.floor(R.nv / f), g = new Uint8Array(nu * nv);
    for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) { let all = 1; for (let y = 0; y < f && all; y++) for (let x = 0; x < f; x++) if (!R.g[(j * f + y) * R.nu + i * f + x]) { all = 0; break; } g[j * nu + i] = all; }
    return { g, nu, nv, cs: R.cs * f }; };
  const rectsOf = ({ g, nu, nv }, k, n, enough = 1) => { const G = g.slice(), out = []; let left = 0; for (let i = 0; i < G.length; i++) left += G[i]; const stop = (1 - enough) * left;
    if (RECT_.H.length < nu + 1) RECT_.s = new Int32Array(nu + 1), RECT_.h = new Int32Array(nu + 1), RECT_.H = new Int32Array(nu + 1);
    const S_ = RECT_.s, Sh = RECT_.h, H = RECT_.H;
    for (let r = 0; r < n && left >= k * k && left > stop; r++) { H.fill(0, 0, nu); let best = 0, bi = null;   // (none left that could hold one, or enough covered)
      for (let j = 0; j < nv; j++) { const o = j * nu; for (let i = 0; i < nu; i++) H[i] = G[o + i] ? H[i] + 1 : 0;
        let t = 0; for (let i = 0; i <= nu; i++) { const h = i < nu ? H[i] : 0; let s0 = i;
          while (t > 0 && Sh[t - 1] >= h) { t--; const si = S_[t], sh = Sh[t]; if (sh >= k && i - si >= k && sh * (i - si) > best) { best = sh * (i - si); bi = [si, i - 1, j - sh + 1, j]; } s0 = si; }
          S_[t] = s0; Sh[t] = h; t++; } }
      if (!bi) break; out.push(bi); left -= best; for (let j = bi[2]; j <= bi[3]; j++) G.fill(0, j * nu + bi[0], j * nu + bi[1] + 1); }
    return out; };
  const roofsMesh = () => { if (ROOF_MESH || !ROOFS || !ROOFS.length) return; const ex = S.U.uScaleH ? S.U.uScaleH.value / scale : 1, list = [], lips = [], rims = [], units = [], caps = [], parts = [], cuts = [], pitch = [];
    const MS = todayL() && todayL().massing; MASS.kinds = {}; MASS.why = {}; MASS.list = []; MASS.kept = 0; if (MS && cityMesh && !cityMesh.geometry.attributes.color) colour(cityMesh);   // (the massing's parts take their building's paint)
    const geoOf = P => cityMesh && cityMesh.geometry.attributes.position === P ? cityMesh.geometry : FPT.mesh && FPT.mesh.geometry.attributes.position === P ? FPT.mesh.geometry : null;
    const roofC = (P_, i0, i1) => { const G_ = geoOf(P_), A_ = G_ && G_.attributes.color, N_ = G_ && G_.attributes.normal; if (A_) for (let i = i0; i < i1; i++) if (N_.getY(i) > .6) return new THREE.Color().fromArray(A_.array, i * 3); return null; };   // (a record's roof paint, its top's vertex colour: its pieces take it)
    const RKS = film && kindsOn() && cityMesh ? MAT.today.roofKinds : null, RY0 = cityMesh ? cityMesh.geometry.userData.y0 : 0, ROOF_MAPON = !!RKS && roofMapOn(), PARTS_ = ROOF_MAPON && partsOn();   // (today's roof kinds: roofClass; their map, its parts)
    const RU = (RKS ? RKS.units : MAT.roofUnits) || null;   // (the rooftop pieces, by roof kind with the kinds on: below)
    const TK = (film && MAT && MAT.today ? { ...TODAY[today], ...MAT.today } : TODAY[today] || {}).kinds, KC_ = {}, pickK = (a_, x) => (KC_[a_] ||= TK[a_].map(c_ => new THREE.Color(c_)))[Math.floor(x * TK[a_].length) % TK[a_].length];   // (today's kinds and paints: a split unit's, kindPaint)
    // a pitched roof (roofKinds pitch: [its pitch in degrees, a slab's], its height at most m and at most this share of the
    // building's, the least width m it stands on, the least share of the rectangle it covers, the share of grey tile roofs
    // gabled, not hipped): over a footprint's least rectangle where the footprint fills it (rect), shrunk along its length and
    // width till it lies on the footprint's own top, a hair inside the outline; its ridge at the data's height, the walls
    // stopping at its eaves (aCut, as the massing cuts them), so nothing stands above the data or outside the footprint. pitch:
    // [x, z, bearing, half length, half width, ridge's half length, eaves, ridge, gable, the record's geometry, first vertex, a
    // wall vertex, its roof's paint, its kind]
    const PT = RKS && RKS.pitch;
    const pitchOf = (G_, i0, i1, P_, y1, hm, kind, kd, h0, inTop) => { const N_ = G_.attributes.normal, lr = leastRect(P_, N_, i0, i1); if (!lr) return null;
      const yb = G_.attributes.aBase ? G_.attributes.aBase.getX(i0) : 0, fill = topArea(P_, N_, i0, i1) / lr.A; if (fill < RKS.rect || lr.W / scale < PT.minW || y1 - yb < 1e-7) return null;
      const cu = Math.cos(lr.th), su = Math.sin(lr.th), m = .25 * scale; let fu = 0, fv = 0;   // (shrunk along its length and its width, the most of it that lies on its own top: its corners and sides' middles there)
      for (let a_ = 1; a_ >= .69; a_ -= .05) for (let b_ = 1; b_ >= .69; b_ -= .05) { if (a_ * b_ <= fu * fv) continue; const hl = lr.L / 2 * a_ - m, hw = lr.W / 2 * b_ - m;
        if ([[-1, -1], [1, -1], [1, 1], [-1, 1], [0, -1], [0, 1], [-1, 0], [1, 0]].every(([p, q]) => inTop(lr.cx + cu * hl * p - su * hw * q, lr.cz + su * hl * p + cu * hw * q))) { fu = a_; fv = b_; } }
      if (fu * fv < PT.cover) return null;
      const slab = kind === 10 && kd !== 3, gable = slab || kind === 8 || (kind === 7 && (((h0 * 1e4) % 1 + 1) % 1) < PT.gable), hl = lr.L / 2 * fu, hw = lr.W / 2 * fv;
      const hr = Math.min(hw / scale * Math.tan((slab ? PT.deg[1] : PT.deg[0]) * Math.PI / 180), PT.maxH, PT.share * hm), v = Math.max(1, Math.min(254, Math.floor(255 * (1 - hr / hm))));   // (its eaves where the walls' cut falls: aCut's own steps)
      return { cx: lr.cx, cz: lr.cz, th: lr.th, hl, hw, ridge: gable ? hl : Math.max(0, hl - hw), y0: yb + (y1 - yb) * v / 255, y1, gable, cut: v, yb }; };
    // a footprint that fills no rectangle (an L, a T, a stepped or ragged block): its pieces, rectangles along its own main axes
    // cut from its top's raster, the largest first (rectsOf; roofKinds pitch pieces: at most this many, each at least minW m a
    // side), a hair inside its outline; a pitched roof on each, their eaves at one height and their ridges at the data's (a
    // narrower piece the steeper), so one building carries the paintings' many ridges; only where the pieces cover cover of its
    // top (else its flat member)
    const piecesOf = (R0, h0, kind, kd, Ra) => { const { cx, cz, c, sn, a, b, y1, yb, hm, th } = R0, m = .25 * scale;
      const R2 = coarse(Ra, Math.ceil(scale / Ra.cs - 1e-6)), tot = R2.g.reduce((s_, v) => s_ + v, 0), rs = rectsOf(R2, Math.ceil(PT.minW * scale / R2.cs), PT.pieces, .9);   // (on cells of a metre or more: a piece never needs finer)
      if (!rs.length || y1 - yb < 1e-7 || rs.reduce((s_, [i0, i1, j0, j1]) => s_ + (i1 - i0 + 1) * (j1 - j0 + 1), 0) < PT.cover * tot) return null;
      const ps = rs.map(([i0, i1, j0, j1]) => { const u0 = -a + i0 * R2.cs + m, u1 = -a + (i1 + 1) * R2.cs - m, v0 = -b + j0 * R2.cs + m, v1 = -b + (j1 + 1) * R2.cs - m, U = (u0 + u1) / 2, V = (v0 + v1) / 2, hu = (u1 - u0) / 2, hv = (v1 - v0) / 2;
        return { cx: cx + c * U - sn * V, cz: cz + sn * U + c * V, th: hu >= hv ? th : th + Math.PI / 2, hl: Math.max(hu, hv), hw: Math.min(hu, hv) }; });
      const slab = kind === 10 && kd !== 3, gable = slab || (kind === 7 && (((h0 * 1e4) % 1 + 1) % 1) < PT.gable);
      const hr = Math.min(Math.max(...ps.map(p => p.hw)) / scale * Math.tan((slab ? PT.deg[1] : PT.deg[0]) * Math.PI / 180), PT.maxH, PT.share * hm), v = Math.max(1, Math.min(254, Math.floor(255 * (1 - hr / hm)))), y0 = yb + (y1 - yb) * v / 255;
      return ps.map(p => ({ ...p, ridge: gable ? p.hl : Math.max(0, p.hl - p.hw), y0, y1, gable, cut: v, yb })); };
    const wallOf = (G_, i0, i1) => { const NN = G_.attributes.normal; for (let i = i0; i < i1; i++) if (Math.abs(NN.getY(i)) < .3) return i; return i0; };
    // a batch of stills: a record made again takes its pieces as they were made (today's rooftops after the replacement footprints
    // chosen for the next shot), while the detailed models stand as they did (FOLDS: they fold records and take their pieces)
    if (BATCH && ROOF_KEEP.n !== FOLDS.length) { ROOF_KEEP.n = FOLDS.length; ROOF_KEEP.m = new WeakMap(); }
    const L_ = [list, lips, rims, units, caps, parts, cuts, pitch];
    let rec_ = null; const kept_ = () => { if (rec_) ROOF_KEEP.m.set(rec_[0], L_.map((l, k) => l.slice(rec_[k + 1]))); rec_ = null; };
    for (const r_ of ROOFS) { kept_(); const k_ = BATCH && ROOF_KEEP.m.get(r_); if (k_) { L_.forEach((l, k) => l.push(...k_[k])); continue; }
      rec_ = BATCH ? [r_, ...L_.map(l => l.length)] : null; let [cx, cz, th, a, b, y1, yr, hm, h0, i0, i1, P_] = r_, rc = roofC(P_, i0, i1);   // (P_: the record's own positions, today's city's or a replacement footprint's)
      const G0 = geoOf(P_), rk = RKS && G0 && G0.userData.roofKind ? G0.userData.roofKind[i0] : 0, kd0 = G0 && G0.attributes.aKind ? Math.round(G0.attributes.aKind.getX(i0)) : 1;
      const RO_ = rk ? { k: roofFlat(rk, kd0) } : null; if (RO_) ROOF_K.set(G0.uuid + ':' + i0, RO_);   // (the kind it shows: its flat member until a pitch or the massing makes it another)
      const c = Math.cos(th), sn = Math.sin(th);
      { let u0 = 1e9, u1 = -1e9, v0 = 1e9, v1 = -1e9;   // (its outline's exact extent along its own axes)
        for (let i = i0; i < i1; i++) { const x = P_.getX(i), z = P_.getZ(i), u = x * c + z * sn, v = -x * sn + z * c; if (u < u0) u0 = u; if (u > u1) u1 = u; if (v < v0) v0 = v; if (v > v1) v1 = v; }
        const um = (u0 + u1) / 2, vm = (v0 + v1) / 2; cx = um * c - vm * sn; cz = um * sn + vm * c; a = (u1 - u0) / 2; b = (v1 - v0) / 2; }
      if (FOLDS.some(f => Math.hypot(cx - f.cx, cz - f.cz) < f.rr || f.inFoot(cx, cz))) continue;   // (none where a detailed model stands)
      let tops = null, tri_ = null, ras_ = null; const triOf = () => tri_ ||= topTris(i0, i1, P_, y1, .1 * ex * scale), rasOf = () => ras_ ||= topRaster(triOf(), cx, cz, c, sn, a, b);   // (its top: triangles, raster, a point's test, each made once)
      const inTop = (x, z) => (tops ||= topGrid(triOf(), cx, cz, c, sn, a, b, triOf().length > 4 ? rasOf() : null))(x, z);
      const pitched_ = (rk === 7 || rk === 9 || rk === 10) && PT && G0 && G0.attributes.aData.getW(i0) < .5;
      const pitchIt = () => { const one = pitchOf(G0, i0, i1, P_, y1, hm, rk, kd0, h0, inTop);   // (its pitched roof, over its least rectangle or over its pieces: no parapet, no plant room)
        const prs = one ? [one] : PT.pieces && G0.attributes.aBase ? piecesOf({ cx, cz, c, sn, a, b, y1, yb: G0.attributes.aBase.getX(i0), hm, th }, h0, rk, kd0, rasOf()) : null; if (!prs) return false;
        const w = G0.attributes.color, wi = wallOf(G0, i0, i1), wall = new THREE.Color().fromArray(w.array, wi * 3);
        const rp = ROOF_MAPON ? roofMapC(rk) : roofPaint(RKS, rk, wall, ((h0 * 7.7e3) % 1 + 1) % 1); cuts.push([G0, i0, i1, prs[0].cut]); for (const pr of prs) pitch.push([pr, G0, i0, ROOF_MAPON ? (PARTS_ ? ROOF_MAP[0] : rp) : wall, rp, rk]); RO_.k = rk; return true; };
      if (hm < 8 || Math.min(a, b) < 4 * scale) { if (pitched_) pitchIt(); continue; }   // (a low or a narrow building: a pitched roof, or nothing on its flat one)
      let ar_ = 0; for (let i = i0; i + 2 < i1; i += 3) if (Math.abs(P_.getY(i) - y1) + Math.abs(P_.getY(i + 1) - y1) + Math.abs(P_.getY(i + 2) - y1) < .1 * ex * scale)   // (its roof's area)
        ar_ += Math.abs((P_.getX(i + 1) - P_.getX(i)) * (P_.getZ(i + 2) - P_.getZ(i)) - (P_.getX(i + 2) - P_.getX(i)) * (P_.getZ(i + 1) - P_.getZ(i))) / 2;
      let hull = null; const nl0 = lips.length, nr0 = rims.length, rect = i1 - i0 <= 36 && ar_ > .95 * 4 * a * b;   // (its roof's outline when convex: what stands on it is tested against it)
      if (rect) { lips.push([cx, y1, cz, 2 * a * .995, ex * scale, 2 * b * .995, yr, th, null, rc]);   // (a rectangle: its roof fills its own box; a triangle or a trapezoid's box rim stood in the air)
        hull = hull2([[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([p, q]) => [cx + c * a * p - sn * b * q, cz + sn * a * p + c * b * q])); }
      else {   // any other convex roof (a triangle, an octagon, a round tower): the rim along its own hull, 0.6 m wide; a concave roof (a corner left inside the hull) none
        const pts = []; for (let i = i0; i < i1; i++) if (Math.abs(P_.getY(i) - y1) < .2 * ex * scale) pts.push([P_.getX(i), P_.getZ(i)]);
        const H_ = hull2(pts); if (H_.length >= 3 && pts.every(([x, z]) => hullIn(H_, x, z) < .4 * scale)) { rims.push([H_, y1, yr, rc]); hull = H_; } }   // (the parapet, on a rectangular roof only: a rim a metre high round its own outline, a hair in)
      // whatever stands on the roof stands wholly on it, a margin inside its parapet (on a concave roof: on its own top's triangles),
      // never over its edge or in the air beside it
      const fits = (x, z, hu, hv, m) => { for (const [p, q] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const X = x + c * (hu + m) * p - sn * (hv + m) * q, Z = z + sn * (hu + m) * p + c * (hv + m) * q; if (hull ? hullIn(hull, X, Z) < 0 : !inTop(X, Z)) return false; } return true; };
      let at = (u, v) => [cx + c * u - sn * v, cz + sn * u + c * v], placed = [], split_ = false, massed_ = false;
      if (MS && hm >= MS.min[0] && Math.min(a, b) >= MS.min[1] * scale) { const G_ = G0, C_ = G_ && G_.attributes.aCtr;   // the massing (massPlan): its parts, its main mass cut
        const pr_ = FPT.protect && FPT.protect.has(Math.fround(C_.getX(i0)) + ',' + Math.fround(C_.getY(i0))); if (pr_) MASS.kept++;
        if (G_ && G_.attributes.color && G_.attributes.aBase && G_.attributes.aData.getW(i0) < .5 && !pr_) {   // (a building of today's, not a mound, not a reviewed parent)
          const yb = G_.attributes.aBase.getX(i0), round = !rect && !!hull && hull.length >= 6 && hull.every(([x, z]) => { const u = ((x - cx) * c + (z - cz) * sn) / a, v = (-(x - cx) * sn + (z - cz) * c) / b; return Math.abs(Math.hypot(u, v) - 1) < .1; });   // (an ellipse: every point of its outline on it)
          const R_ = { cx, cz, c, sn, a, b, y1, yb, hm, rect, round, fits, hull, fill: ar_ / (4 * a * b) }, SP = MS.split, kd = G_.attributes.aKind ? G_.attributes.aKind.getX(i0) : 1;
          const big_ = SP && TK && ar_ / scale / scale >= SP.area, why_ = !big_ ? null : G_ !== cityMesh.geometry && FPT.osm && FPT.osm.has(Math.fround(C_.getX(i0)) + ',' + Math.fround(C_.getY(i0))) ? 'osm' : hm >= SP.maxH ? 'tall' : kd === 2 ? 'kind' : 2 * Math.min(a, b) < SP.minW * scale ? 'narrow' : null;
          const sp_ = big_ && !why_ ? splitPlan(MS, R_, h0) : null; if (big_) { MASS.why[why_ || (sp_ ? 'split' : 'unfit')] = (MASS.why[why_ || (sp_ ? 'split' : 'unfit')] || 0) + 1; (MASS.list ||= []).push([cx, y1, cz, why_ || (sp_ ? 'split' : 'unfit'), ar_ / scale / scale, hm]); }   // (MASS large, list: each large footprint, whether it was split and why not; window.__MINI.mass for a check)
          const M_ = y1 - yb > 1e-7 && (sp_ || massPlan(MS, R_));   // (split: today's data's own footprints, a squared one's too, never an OpenStreetMap building (the sidecar's osm sources: single buildings), a tower's glass or a stone civic building)
          if (M_ && M_.kind === 'step' && pitched_ && pitchIt()) { lips.length = nl0; rims.length = nr0; continue; }   // (a low-rise's step, one end a storey higher, is a roof's variety: a pitched roof in its place)
          if (M_) { cuts.push([G_, i0, i1, Math.max(1, Math.min(254, Math.round(255 * (M_.cut - yb) / (y1 - yb))))]); MASS.kinds[M_.kind] = (MASS.kinds[M_.kind] || 0) + 1; massed_ = true;
            if (M_.kind === 'split') { lips.length = nl0; rims.length = nr0; split_ = true; }   // (its own roof gone to its base: no parapet of its own)
            else { for (let k = nl0; k < lips.length; k++) lips[k][1] = M_.cut; for (let k = nr0; k < rims.length; k++) rims[k][1] = M_.cut; }   // (its parapet round the main mass's roof)
            let wi = i0, ri = i0; const NN = G_.attributes.normal; for (let i = i0; i < i1; i++) { if (Math.abs(NN.getY(i)) < .3 && wi === i0) wi = i; if (NN.getY(i) > .6) { ri = i; break; } }
            // the roof kinds the massing makes: a building with massing keeps a flat roof (its kind's flat member); over a podium or
            // under a setback a flat roof is 11 (its levels each a flat roof); a split footprint's units each their own: an old low
            // grey-tiled block's inner units lane houses' small gables (8) in a ring of flat roofs in their own paints (1), as the
            // paintings' perimeter blocks, any other block's units flat in their own paints; the roof map's tints on them
            const big_o = ar_ / scale / scale > RKS?.oldA?.[1] || kd0 === 3, old_ = !!RKS && yr > 1 && yr <= RY0 + RKS.old && hm < RKS.oldH && (rk === 7 || (big_o && rk !== 9 && rk !== 10 && ((h0 * 3.7e3) % 1 + 1) % 1 < RKS.grey)), unitK = [];   // (a lane-house block: an old low block of grey tile, or a large old low one (a hall's footprint, one past an old block's size: no neighbourhood draws for it) by its own draw)
            if (RO_) RO_.plan = M_.kind;
            if (RO_ && !split_ && RO_.k <= 5 && /^(podium|setback)/.test(M_.kind)) { RO_.k = 11;
              if (ROOF_MAPON) { const M11 = roofMapC(11); for (let i = i0; i < i1; i++) if (NN.getY(i) > .6) G_.attributes.color.setXYZ(i, M11.r, M11.g, M11.b); G_.attributes.color.needsUpdate = true; rc = M11;
                for (let k = nl0; k < lips.length; k++) lips[k][9] = M11; for (let k = nr0; k < rims.length; k++) rims[k][3] = M11; } }
            for (const q of M_.parts) { const o_ = q[7] ? (() => { const k_ = kd === 4 && q[7].q2 < (SP.stone ?? .35) ? 4 : q[7].hm < TK.oldH ? 0 : 1; let [w_, r_] = kindPaint(TK, k_, q[7].hm, q[7].q, q[7].q2, pickK);   // (a split unit: its own paint and kind)
                let rk_ = 0;
                if (RKS) { const u_ = 2 * q[3] / scale, v_ = 2 * q[4] / scale; rk_ = old_ && q[7].inner ? 8 : 1;
                  if (rk_ === 8 && PT) { const hr_ = Math.min(Math.min(q[3], q[4]) / scale * Math.tan(PT.deg[0] * Math.PI / 180), PT.maxH, PT.share * q[7].hm) * (q[6] - q[5]) / q[7].hm, lu_ = q[3] >= q[4];   // (its gable over it, its walls that much lower)
                    const kv_ = .95 + .1 * ((q[7].q * 7.13) % 1), rp_ = ROOF_MAPON ? roofMapC(8) : roofPaint(RKS, 8, w_, q[7].q2);
                    q[6] -= hr_; pitch.push([{ cx: q[0], cz: q[1], th: lu_ ? th : th + Math.PI / 2, hl: Math.max(q[3], q[4]), hw: Math.min(q[3], q[4]), ridge: Math.max(q[3], q[4]), y0: q[6], y1: q[6] + hr_, gable: true, unit: { x: q[0], z: q[1], hm: q[7].hm, h: q[7].q } }, G_, i0, ROOF_MAPON ? (PARTS_ ? ROOF_MAP[0] : rp_) : w_.clone().multiplyScalar(kv_), rp_, 8]); }
                  else if (rk_ === 1) r_ = w_;   // (a ring's flat roof in its own paint)
                  unitK.push([q[0], q[6], q[1], rk_, u_ * v_, q[7].hm, yr, Math.max(u_, v_), Math.min(u_, v_), 1, '', hm, q[7].inner ? 1 : 0, rk, C_.getX(i0), C_.getY(i0)]); if (ROOF_MAPON) { w_ = ROOF_MAP[0]; r_ = roofMapC(rk_); } }
                return { wall: w_, roof: r_, k: k_, h: q[7].q, hm: q[7].hm, rk: rk_ }; })() : null;
              parts.push([q[0], q[1], q[2], q[3], q[4], q[5], q[6], th, G_, i0, wi, ri, o_]); if (!q[2] && !(o_ && o_.rk === 8)) lips.push([q[0], q[6], q[1], 2 * q[3] * .995, ex * scale, 2 * q[4] * .995, yr, th, null, o_ ? o_.roof : rc]); }
            if (unitK.length && RO_) RO_.units = unitK;
            if (!split_) { const T_ = M_.parts[M_.parts.length - 1];   // (its rooftops on its highest part)
            cx = T_[0]; cz = T_[1]; a = T_[3]; b = T_[4]; y1 = T_[6]; tops = tri_ = ras_ = null; at = (u, v) => [cx + c * u - sn * v, cz + sn * u + c * v];
            hull = hull2(T_[2] ? Array.from({ length: 12 }, (_, k) => at(Math.cos(k * Math.PI / 6) * a, Math.sin(k * Math.PI / 6) * b)) : [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([p, q]) => at(a * p, b * q))); } } } }
      if (split_) continue;   // (a split footprint's roof pieces: none; its units carry their parapets)
      if (pitched_ && !massed_ && pitchIt()) { lips.length = nl0; rims.length = nr0; continue; }
      if (!RKS) {   // the roof kinds off (todayLight roofKinds): from 20 m a plant room or two, each its own size, height and step of its
        // roof's paint, and on a large roof a few small units (roofUnits), by the roof's hash
        if (hm >= 20) { const q_ = ((h0 * 1e4) % 1 + 1) % 1, k = RU ? RU.main[0] + RU.main[1] * q_ : .2 + .16 * q_, mH = RU ? RU.mainH : [3, 2.5];   // (plant rooms: one or two, each its own size, height and step of its roof's paint)
          const w1 = 2 * a * k, d1 = 2 * b * k * (.7 + .5 * ((q_ * 3.1) % 1));   // (where it fits: a curved slab's box centre may lie outside it)
          for (const [u1, v1] of RU ? [[.15, 0], [0, 0], [-.3, 0], [.4, 0], [-.5, 0], [0, .3], [0, -.3]] : [[.15, 0]]) { const P1 = at(a * u1, b * v1);
            if (!RU || fits(P1[0], P1[1], w1 / 2, d1 / 2, .8 * scale)) { list.push([P1[0], y1, P1[1], w1, (mH[0] + mH[1] * ((q_ * 7.3) % 1)) * ex * scale, d1, yr, th, q_, rc]); placed.push([a * u1, b * v1, w1 / 2, d1 / 2]); break; } }
          const P2 = [cx - c * a * .45, cz - sn * a * .45 + b * .3 * c], w2 = 2 * a * .12, d2 = 2 * b * .16;
          if (a * b > 150 * scale * scale && q_ > .3 && (!RU || fits(P2[0], P2[1], w2 / 2, d2 / 2, .8 * scale))) list.push([P2[0], y1, P2[1], w2, 2.4 * ex * scale, d2, yr, th, (q_ * 5.7) % 1, rc]); }
        if (RU && 4 * a * b >= RU.area * scale * scale) {   // small units (the look's roofUnits): a few boxes, each its own size and place, by the roof's hash
          const hh = k => { const t = Math.sin(h0 * 1e5 + k * 78.233) * 43758.5453; return t - Math.floor(t); }, n = RU.n[0] + Math.floor(hh(1) * (RU.n[1] - RU.n[0] + 1));
          for (let k = 0, tries = 0; k < n && tries < 4 * n; tries++) { const s_ = (RU.size[0] + RU.size[1] * hh(10 + tries)) * scale, hu = s_ / 2, hv = s_ * (.6 + .5 * hh(20 + tries)) / 2;
            const u = (hh(30 + tries) * 2 - 1) * Math.max(0, a - hu - 1.4 * scale), v = (hh(40 + tries) * 2 - 1) * Math.max(0, b - hv - 1.4 * scale), [x, z] = at(u, v);
            if (placed.some(([pu, pv, ph, pw]) => Math.abs(u - pu) < ph + hu + .6 * scale && Math.abs(v - pv) < pw + hv + .6 * scale) || !fits(x, z, hu, hv, .8 * scale)) continue;
            units.push([x, y1, z, 2 * hu, (RU.h[0] + RU.h[1] * hh(50 + tries)) * ex * scale, 2 * hv, yr, th, hh(60 + tries), rc]); placed.push([u, v, hu, hv]); k++; } }
        continue; }
      // the pieces on a flat roof, by the kind it shows (roofUnits; the paintings' catalogue): one large low plant room on a mid- or
      // high-rise's roof (1, 4, 11; main: its share of the roof's area [from, more], mainH: its height m [from, more]), at times a
      // small one in a corner; on a point tower's one or two round caps (2; caps: their diameter's share of the roof's width [from,
      // more], their height m [from, more]); along a slab's one long low plant room, rounded (3; capsule: its length's share of the
      // roof's [from, more], its width's, its height m); on the old fabric's grey roof no parapet, one dark hatch (6; slot: its share
      // of the roof's area, its paint's times); a hall's roof bare. Each by the roof's hash, the same from any camera
      const kf = RO_ ? RO_.k : 1, q_ = ((h0 * 1e4) % 1 + 1) % 1;
      if (kf === 6) { lips.length = nl0; rims.length = nr0; if (RU && RU.slot) { const s_ = Math.sqrt(RU.slot[0]), w1 = 2 * a * s_, d1 = 2 * b * s_ * .5, P1 = at(a * (q_ - .5) * .6, b * .3);
        if (fits(P1[0], P1[1], w1 / 2, d1 / 2, .5 * scale)) units.push([P1[0], y1 - .05 * ex * scale, P1[1], w1, .2 * ex * scale, d1, yr, th, q_, rc, RU.slot[1]]); } continue; }
      if (kf === 2 && RU && RU.caps) { const C_ = RU.caps, n_ = q_ < .5 ? 1 : 2;   // (round caps: one in the middle or two side by side)
        for (let k = 0; k < n_; k++) { const dm = 2 * Math.min(a, b) * (C_[0] + C_[1] * ((q_ * (3.1 + k)) % 1)), u1 = n_ === 1 ? 0 : (k ? .35 : -.35), P1 = at(a * u1, b * .1);
          if (fits(P1[0], P1[1], dm / 2, dm / 2, .5 * scale)) caps.push([P1[0], y1, P1[1], dm, (C_[2] + C_[3] * ((q_ * 5.3) % 1)) * ex * scale, dm, yr, th, (q_ * 7.1 + k) % 1, rc]); }
        continue; }
      if (kf === 3 && RU && RU.capsule) { const C_ = RU.capsule, lu = a >= b, A = lu ? a : b, B = lu ? b : a, l1 = 2 * A * (C_[0] + C_[1] * q_), w1 = 2 * B * C_[2];   // (one long rounded plant room down the slab's length)
        const P1 = at(lu ? A * .1 * (q_ - .5) : 0, lu ? 0 : A * .1 * (q_ - .5)); if (fits(P1[0], P1[1], (lu ? l1 : w1) / 2, (lu ? w1 : l1) / 2, .6 * scale)) caps.push([P1[0], y1, P1[1], lu ? l1 : w1, C_[3] * ex * scale, lu ? w1 : l1, yr, th, q_, rc]);
        continue; }
      if (kf === 5) continue;   // (a hall: its roof bare)
      if (hm >= 20) { const k = RU ? Math.sqrt(RU.main[0] + RU.main[1] * q_) : .2 + .16 * q_, mH = RU ? RU.mainH : [3, 2.5];   // (one large low plant room, its own size, height and step of its roof's paint; at times a small one in a corner)
        const w1 = 2 * a * k, d1 = 2 * b * k * (.85 + .3 * ((q_ * 3.1) % 1));   // (where it fits: a curved slab's box centre may lie outside it)
        for (const [u1, v1] of RU ? [[.18, .12], [.1, 0], [-.18, .12], [0, 0], [.3, 0], [-.3, 0], [0, .25], [0, -.25]] : [[.15, 0]]) { const P1 = at(a * u1, b * v1);
          if (!RU || fits(P1[0], P1[1], w1 / 2, d1 / 2, .8 * scale)) { list.push([P1[0], y1, P1[1], w1, (mH[0] + mH[1] * ((q_ * 7.3) % 1)) * ex * scale, d1, yr, th, q_, rc]); placed.push([a * u1, b * v1, w1 / 2, d1 / 2]); break; } }
        const P2 = [cx - c * a * .7 + sn * b * .55, cz - sn * a * .7 - c * b * .55], w2 = 2 * a * .12, d2 = 2 * b * .16;
        if (a * b > 150 * scale * scale && q_ > .55 && (!RU || fits(P2[0], P2[1], w2 / 2, d2 / 2, .8 * scale)) && !placed.some(([pu, pv, ph, pw]) => Math.abs(-a * .7 - pu) < ph + w2 / 2 && Math.abs(-b * .55 - pv) < pw + d2 / 2)) list.push([P2[0], y1, P2[1], w2, 2.4 * ex * scale, d2, yr, th, (q_ * 5.7) % 1, rc]); } }
    kept_();
    massMesh(parts, cuts); pitchMesh(pitch);
    const ring = (() => { const w = .035, o = new THREE.Shape([[-.5, -.5], [.5, -.5], [.5, .5], [-.5, .5]].map(([x, y]) => new THREE.Vector2(x, y))), h = new THREE.Path([[-.5 + w, -.5 + w], [-.5 + w, .5 - w], [.5 - w, .5 - w], [.5 - w, -.5 + w]].map(([x, y]) => new THREE.Vector2(x, y)));
      o.holes.push(h); return new THREE.ExtrudeGeometry(o, { depth: 1, bevelEnabled: false }).rotateX(-Math.PI / 2); })();   // (a parapet: the roof's rim, 3.5 % of each side wide)
    const mat = new THREE.MeshStandardMaterial({ color: '#e9e6df', roughness: .9 }); mat.onBeforeCompile = sh => { sh.uniforms.uTodayK = TODAY_K; sh.uniforms.uRoofOn = ROOF_ON;
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float iYear; uniform vec3 uTodayK; uniform float uRoofOn;').replace('#include <begin_vertex>', `#include <begin_vertex>
  if (iYear > uTodayK.x + .5 || uRoofOn < .002) transformed *= 0.;
#ifdef USE_INSTANCING
  else transformed.y -= (1. - uRoofOn) * 1.05;   // (coming or going: sunk into its roof, its own height and a little, rising out of it as uRoofOn comes)
#else
  else transformed.y -= (1. - uRoofOn) * ${(1.05 * ex * scale).toExponential(4)};
#endif`);
      if (PARTS_) sh.fragmentShader = sh.fragmentShader.replace('#include <opaque_fragment>', `outgoingLight = diffuseColor.rgb * (dot(normalize(vNormal), normalize((viewMatrix * vec4(0., 1., 0., 0.)).xyz)) > .9 ? 1. : .5);   // (the parts mask: unlit, a side half as bright)
#include <opaque_fragment>`); };
    // a parapet's rim (the rectangular roofs' rings, the convex roofs' rims) sinks into its roof as it shrinks: whole while a metre
    // spans 2 picture pixels, gone below 0.8 (afar a light rim a pixel wide outlined every roof, as a wireframe); drop: how far it sinks
    const RT_ = todayL() && todayL().roof && todayL().roof[4];   // (todayLight roof [4]: a parapet's top this much lighter than its wall's paint: a lit coping round the roof)
    const rimMat = (m0, drop, key) => { const m = m0.clone(); m.onBeforeCompile = sh => { mat.onBeforeCompile(sh); sh.uniforms.uRoofPx = ROOF_PX;
        if (RT_ && key !== 'unit' && !PARTS_) sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>\n  if (dot(normalize(vNormal), normalize((viewMatrix * vec4(0., 1., 0., 0.)).xyz)) > .9) diffuseColor.rgb *= ${(+RT_).toFixed(3)};`);
        sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nuniform float uRoofPx;').replace('#include <begin_vertex>', `#include <begin_vertex>
  {
#ifdef USE_INSTANCING
    vec4 mv_ = modelViewMatrix * instanceMatrix * vec4(transformed, 1.);
#else
    vec4 mv_ = modelViewMatrix * vec4(transformed, 1.);
#endif
    transformed.y -= (1. - smoothstep(.8, 2., 1. / max(-mv_.z * uRoofPx, 1e-9))) * ${drop}; }`); };
      m.customProgramCacheKey = () => 'mini-roof-rim ' + key; return m; };
    const M4 = new THREE.Matrix4(), R4 = new THREE.Matrix4();
    // every piece in its roof's paint (rc: a quiet step of its building's own family, never a grey of its own): a parapet its roof's,
    // its top lighter (todayLight roof [4]), plant rooms and units a step of it each (roofUnits mainK, unitK); a roof without a
    // painted top (rc null) the light rim and the grey they had
    const RIM0 = new THREE.Color('#e9e6df'), C0 = new THREE.Color('#c4bfb6');
    if (rims.length) {   // the hull rims as one mesh: outer wall, inner wall, top, a metre high
      const pos = [], yrs = [], cols = [], w = .6 * scale, h = ex * scale;
      for (const [H_, y0, yr, rc] of rims) { const cr = PARTS_ ? ROOF_PARTS.rim : rc || RIM0; const cx_ = H_.reduce((a_, p_) => a_ + p_[0], 0) / H_.length, cz_ = H_.reduce((a_, p_) => a_ + p_[1], 0) / H_.length;
        const inn = H_.map(([x, z]) => { const dx = x - cx_, dz = z - cz_, l = Math.hypot(dx, dz) || 1; return [x - dx / l * w, z - dz / l * w]; });
        const quad = (a_, b_, c_, d_) => { for (const q of [a_, b_, c_, a_, c_, d_]) { pos.push(...q); yrs.push(yr); cols.push(cr.r, cr.g, cr.b); } };
        for (let k = 0; k < H_.length; k++) { const k2 = (k + 1) % H_.length, [ox, oz] = H_[k], [px, pz] = H_[k2], [ix, iz] = inn[k], [jx, jz] = inn[k2];
          quad([ox, y0, oz], [px, y0, pz], [px, y0 + h, pz], [ox, y0 + h, oz]); quad([jx, y0, jz], [ix, y0, iz], [ix, y0 + h, iz], [jx, y0 + h, jz]); quad([ox, y0 + h, oz], [px, y0 + h, pz], [jx, y0 + h, jz], [ix, y0 + h, iz]); } }
      const g_ = new THREE.BufferGeometry(); g_.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g_.setAttribute('iYear', new THREE.Float32BufferAttribute(yrs, 1)); g_.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3)); g_.computeVertexNormals();
      const m_ = new THREE.Mesh(g_, rimMat(Object.assign(mat.clone(), { color: new THREE.Color(1, 1, 1), vertexColors: true }), (1.5 * ex * scale).toExponential(4), 'hull')); m_.material.side = THREE.DoubleSide; m_.castShadow = m_.receiveShadow = true; m_.layers.set(L); m_.frustumCulled = false; scene.add(m_); RIM_MESH = m_; }
    // (the small pieces sink into the roof as they shrink, as the rims do: afar they were speckle; caps and long plant rooms round)
    ROOF_MESH = [[new THREE.BoxGeometry(1, 1, 1).translate(0, .5, 0), list], [ring, lips], [new THREE.BoxGeometry(1, 1, 1).translate(0, .5, 0), units], [new THREE.CylinderGeometry(.5, .5, 1, 16, 1).translate(0, .5, 0), caps]].filter(([, l]) => l.length).map(([geo, l]) => { const W_ = Object.assign(mat.clone(), { color: new THREE.Color(1, 1, 1) }), mesh = new THREE.InstancedMesh(geo, l === list ? Object.assign(W_, { onBeforeCompile: mat.onBeforeCompile }) : rimMat(W_, '1.5', l === units || l === caps ? 'unit' : 'ring'), l.length), yA = new Float32Array(l.length);
      const K_ = l === list ? (RU ? RU.mainK : [.62, .74, .86, .7, .8]) : l === units || l === caps ? RU.unitK : null, c_ = new THREE.Color();
      const P_ = PARTS_ ? (l === lips ? ROOF_PARTS.rim : l === units ? ROOF_PARTS.unit : ROOF_PARTS.plant) : null;   // (the parts mask: each list its part's colour)
      l.forEach(([x, y, z, sx, sy, sz, yr, th, q, rc, f], n) => { M4.makeRotationY(-th).multiply(R4.makeScale(sx, sy, sz)).setPosition(x, y, z); mesh.setMatrixAt(n, M4); yA[n] = yr;
        mesh.setColorAt(n, P_ ? P_ : c_.copy(rc || (K_ ? C0 : RIM0)).multiplyScalar(f ?? (K_ ? K_[Math.floor(q * K_.length) % K_.length] : 1))); });   // (each plant room and unit its own step of its roof's paint, a hatch its own (f); a parapet its roof's)
      geo.setAttribute('iYear', new THREE.InstancedBufferAttribute(yA, 1)); mesh.castShadow = mesh.receiveShadow = true; mesh.layers.set(L); mesh.frustumCulled = false; scene.add(mesh); return mesh; }); };   // (plant rooms; parapets)
  // today's streets as geometry (todayLight streets: { asphalt, pavement colours, kerb: the pavement's metres each side, w: full
  // widths by class }): a ribbon along every street and arterial (data/streets.json, lines.json roads) at its class's width, an
  // asphalt carriageway on a lighter pavement band, crisp at any range (the ground's raster of them, some 7 m a texel, frays close);
  // shown where today's city stands and is the subject, as the urban extent's year reaches it (YEAR_T)
  // The materials (each fine pattern box-filtered by its own coordinate's pixel footprint, so it averages to its mean as it shrinks
  // and never crawls): grain: [the asphalt's fine grain's strength, its size m, its wear's (lighter and darker patches some 9 to 23 m)
  // strength, the pavement's grain's strength]; marks: the road markings, light paint at k of its colour c, w m wide (a model's,
  // wider than life, to read; paint on asphalt, well short of the kerb's light): a carriageway from minW m wide carries them, its
  // lanes some lane m wide, at most most a side (a few dashes, never a highway's); the centre line solid from four lanes, dashed
  // below (dash: [paint, gap] m), lane lines dashed, edge lines from edge m wide (the kerb is the edge); half of a dual
  // carriageway its median line, one for both halves, and a way between two parallel ones none of its own (one road, one set); at a junction of two marked ways a crossing (zebra: [from the junction m, its depth, bar, gap])
  // and a stop line stop m wide on the lanes approaching it (drive: 1 right-hand traffic, -1 left); kerb: [its lit top m, the
  // gutter's shade m, the top's colour, the shade's strength, the top's], along every carriageway's edge, the shade where the kerb's face
  // turns from the sun; far: [from, whole] m a pixel, the paint toward its mean share of the carriageway (no lattice of
  // single-pixel lines afar)
  let STREET_MESH = null;
  const streetsMesh = () => { const T_ = todayL() && todayL().streets; if (STREET_MESH || !T_ || !YEAR_T.value || !STREETS.list) return;
    const W = T_.w, MK = T_.marks, GR = T_.grain, cw = c => W[(c || '').replace('_link', '')] || W.other, RD = [...STREETS.list, ...(roads || [])].map(r => ({ pts: r.pts, w: cw(r.cls), link: /_link$/.test(r.cls || '') }));
    const NET = MK ? streetNet(RD, T_.kerb, MK, scale) : null;
    STREET_MESH = (MK ? [0, 1, 2] : [0, 1]).map(layer => { const pos = [], idx = [], nrm = [], mid = [], rd = [], jn = [], sg = [], nr = [];
      (layer === 2 ? NET.R : RD).forEach((r, ri) => { const pts = r.pts, hw = (r.w / 2 + (layer === 1 ? 0 : T_.kerb)) * scale, A_ = layer === 2 ? NET.at(ri) : null;   // (the markings' ways with their crossings as vertices)
        for (let k = 1; k < pts.length; k++) { const [ax, az] = pts[k - 1], [bx, bz] = pts[k], l = Math.hypot(bx - ax, bz - az); if (l < 1e-9) continue;
          if (wet(ax, az) || wet(bx, bz) || wet((ax + bx) / 2, (az + bz) / 2)) continue;   // (none over the water: a tunnel under the river, a bridge above it, are not paving on its surface)
          const ux = (bx - ax) / l, uz = (bz - az) / l, nx = -uz * hw, nz = ux * hw, ex = ux * hw * .6, ez = uz * hw * .6, i0 = pos.length / 3;   // (each end carried on: the joints closed)
          for (const [x, z] of [[ax - ex + nx, az - ez + nz], [bx + ex + nx, bz + ez + nz], [bx + ex - nx, bz + ez - nz], [ax - ex - nx, az - ez - nz]]) { pos.push(x, S.ground(x, z) + [.3, .45, .5][layer] * scale, z); nrm.push(0, 1, 0); mid.push((ax + bx) / 2, (az + bz) / 2); }
          idx.push(i0, i0 + 1, i0 + 2, i0, i0 + 2, i0 + 3);
          if (A_) { const L_ = l / scale, s0 = A_.s[k - 1], e_ = hw * .6 / scale, h_ = hw / scale, jb = A_.J.filter(j => j[0] <= k - 1).pop(), jf = A_.J.find(j => j[0] >= k), ca = NET.clip(ri, ax, az, ux, uz), cb = NET.clip(ri, bx, bz, ux, uz);   // (the junctions behind and ahead; the parallel ways at each end)
            for (const [t, c, kk] of [[-e_, h_, ca], [L_ + e_, h_, cb], [L_ + e_, -h_, cb], [-e_, -h_, ca]]) { const s = s0 + t;
              rd.push(s, c, r.w / 2, r.link ? 0 : Math.floor(r.w / MK.lane)); jn.push(jb ? s - jb[1] - jb[2] : 1e4, jf ? jf[1] - jf[2] - s : 1e4, jb ? jb[3] : 0, jf ? jf[3] : 0); sg.push(t, L_, kk[0], kk[1]); nr.push(-uz, ux); } } } });
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3)); g.setAttribute('aMid', new THREE.Float32BufferAttribute(mid, 2)); g.setIndex(idx);
      if (layer === 2) { g.setAttribute('aRd', new THREE.Float32BufferAttribute(rd, 4)); g.setAttribute('aJn', new THREE.Float32BufferAttribute(jn, 4)); g.setAttribute('aSg', new THREE.Float32BufferAttribute(sg, 4)); g.setAttribute('aNr', new THREE.Float32BufferAttribute(nr, 2)); }
      const m = new THREE.MeshStandardMaterial({ color: [T_.pavement, T_.asphalt, '#ffffff'][layer], roughness: .95, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: [-2, -4, -6][layer], polygonOffsetUnits: [-2, -4, -6][layer], ...(layer === 2 ? { transparent: true, depthWrite: false } : {}) });
      m.onBeforeCompile = sh => { Object.assign(sh.uniforms, { uTodayK: TODAY_K, uYearT: YEAR_T, uPlateS: { value: new THREE.Vector2(PW, PD) }, uSunDir: SUN_DIR, uStreetK: STREET_K });
        const GF_ = todayL().groundFill; if (GF_) sh.fragmentShader = sh.fragmentShader.replace('#include <lights_fragment_end>', `#include <lights_fragment_end>
  { vec3 id_ = reflectedLight.indirectDiffuse; reflectedLight.indirectDiffuse = mix(vec3(dot(id_, vec3(.2126, .7152, .0722))), id_, ${GF_[0].toFixed(2)}) * ${GF_[1].toFixed(2)}; }`);   // (the ground's sky light, as the plate's)
        sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>
uniform vec3 uTodayK; uniform sampler2D uYearT; uniform vec2 uPlateS; attribute vec2 aMid; varying vec2 vWm;${layer === 2 ? ' attribute vec4 aRd, aJn, aSg; attribute vec2 aNr; varying vec4 vRd, vJn, vSg; varying vec2 vNr;' : ''}`).replace('#include <begin_vertex>', `#include <begin_vertex>
  vWm = (modelMatrix * vec4(transformed, 1.)).xz / ${scale.toExponential(4)};${layer === 2 ? ' vRd = aRd; vJn = aJn; vSg = aSg; vNr = aNr;' : ''}   // (metres)
  { float yt_ = texture2D(uYearT, aMid / uPlateS + .5).r * 255.; if (yt_ < .5 || yt_ > uTodayK.x - 1899. + .5) transformed = vec3(aMid.x, -1., aMid.y); }`);   // (by its segment's middle: a segment goes whole, its four corners to one point, never stretched to the origin)
        sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
uniform vec3 uSunDir; uniform float uStreetK; varying vec2 vWm;${layer === 2 ? ' varying vec4 vRd, vJn, vSg; varying vec2 vNr;' : ''}
float sbH(vec2 p){ vec3 q = fract(vec3(p.xyx) * .1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float sbN(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f); return mix(mix(sbH(i), sbH(i + vec2(1, 0)), f.x), mix(sbH(i + vec2(0, 1)), sbH(i + vec2(1, 1)), f.x), f.y); }
float sbBox(float x, float h, float f){ return clamp((x + h) / f + .5, 0., 1.) - clamp((x - h) / f + .5, 0., 1.); }   // (a band |x| < h: its share of a pixel f wide)
float sbDashI(float x, float on, float per){ return floor(x / per) * on + min(mod(x, per), on); }
float sbDash(float s, float on, float per, float f){ return (sbDashI(s + f * .5, on, per) - sbDashI(s - f * .5, on, per)) / f; }   // (dashes on of every per: their share of a pixel f long)
vec4 sbOver(vec4 d, vec3 c, float a){ return vec4(c * a + d.rgb * (1. - a), a + d.a * (1. - a)); }`);
        if (GR && layer < 2) sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
  { float px_ = length(fwidth(vWm));   // the ${layer ? 'asphalt' : 'pavement'}'s grain${layer ? ' and its wear' : ''}, each gone as a pixel outgrows it
    diffuseColor.rgb *= 1. + ${(+GR[layer ? 0 : 3]).toFixed(3)} * 2. * (sbN(vWm / ${(+GR[1]).toFixed(2)}) - .5) * (1. - smoothstep(.3, 1., px_ / ${(+GR[1]).toFixed(2)}))${layer ? `
      + ${(+GR[2]).toFixed(3)} * 2. * (.6 * sbN(vWm / 9. + 3.7) + .4 * sbN(vWm / 23. + 8.1) - .5) * (1. - smoothstep(4., 12., px_))` : ''}; }`);
        if (layer === 2) { const v3_ = c => `vec3(${new THREE.Color(c).toArray().map(v => v.toFixed(4)).join(', ')})`, f_ = v => (+v).toFixed(3), Z = MK.zebra, KB = MK.kerb;
          sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
  { float x_ = vRd.y, s_ = vRd.x, hw_ = vRd.z, n_ = vRd.w, fx_ = max(fwidth(x_), 1e-4), fs_ = max(fwidth(s_), 1e-4), fj_ = max(fwidth(vJn.y), 1e-4);   // a way's markings and kerbs (todayLight streets marks)
    if (vSg.x < 0. || vSg.x > vSg.y) discard;   // (each segment its own stretch: a bend's overlap painted once)
    float cl_ = vSg.z, cr_ = vSg.w, el_ = -min(hw_, cl_), er_ = min(hw_, cr_), db_ = vJn.x, df_ = vJn.y, out_ = step(0., min(db_, df_)) * step(0., cl_);   // (out_: off the junctions, not under a wider way)
    bool one_ = cl_ < hw_ - .5 || cr_ < hw_ - .5;   // (half of a dual carriageway: one way, its median on its clipped side)
    float W2 = ${f_(MK.w / 2)}, mk_ = 0., sh_ = 0., kt_ = 0., in_ = sbBox(x_ - (el_ + er_) * .5, (er_ - el_) * .5, fx_), dash_ = sbDash(s_, ${f_(MK.dash[0])}, ${f_(MK.dash[0] + MK.dash[1])}, fs_);
    float nl_ = clamp(one_ ? floor((er_ - el_) / ${f_(MK.lane)} + .2) : floor(n_ * .5), 1., ${f_(MK.most || 9)}), lw_ = one_ ? (er_ - el_) / nl_ : hw_ / nl_, xl_ = one_ ? x_ - el_ : abs(x_);   // (lanes a side, at most most: a few dashes, never a highway's)
    float k_ = floor(xl_ / lw_ + .5), share_ = 0.;
    if (n_ >= 2. && hw_ * 2. >= ${f_(MK.minW)} && !(cl_ < hw_ - .5 && cr_ < hw_ - .5)) {   // (a way between two parallel ones: their median lines bound it, its own unmarked: one road, one set of lines)
      if (k_ >= 1. && k_ <= nl_ - 1.) mk_ = max(mk_, sbBox(xl_ - k_ * lw_, W2, fx_) * dash_);   // lane lines, dashed
      if (!one_) mk_ = max(mk_, sbBox(x_, W2, fx_) * (n_ >= 4. ? 1. : dash_));   // the centre line
      if (cr_ < hw_ - .5) mk_ = max(mk_, sbBox(x_ - er_, W2, fx_));   // a dual carriageway's median line, midway: its other half paints the same one
      if (cl_ < hw_ - .5) mk_ = max(mk_, sbBox(x_ - el_, W2, fx_));
      if (hw_ * 2. >= ${f_(MK.edge)}) { if (cr_ >= hw_ - .5) mk_ = max(mk_, sbBox(x_ - hw_ + .6, W2, fx_)); if (cl_ >= hw_ - .5) mk_ = max(mk_, sbBox(x_ + hw_ - .6, W2, fx_)); }   // edge lines
      share_ = (W2 * 2. * ((nl_ - 1.) * (one_ ? 1. : 2.) * ${f_(MK.dash[0] / (MK.dash[0] + MK.dash[1]))} + (one_ ? 1. : (n_ >= 4. ? 1. : ${f_(MK.dash[0] / (MK.dash[0] + MK.dash[1]))})) + (hw_ * 2. >= ${f_(MK.edge)} ? 2. : 0.))) / max(er_ - el_, 1.);   // (their mean share of the carriageway)
      mk_ = mix(mk_, share_ * in_, smoothstep(${f_(MK.far[0])}, ${f_(MK.far[1])}, fx_));
      float zx_ = in_ * sbDash(x_ - el_ - .3, ${f_(Z[2])}, ${f_(Z[2] + Z[3])}, fx_);   // crossings at junctions of two marked ways: bars along the way, across its carriageway
      mk_ = max(mk_, zx_ * (step(.5, vJn.w) * step(0., db_) * sbBox(df_ - ${f_(Z[0] + Z[1] / 2)}, ${f_(Z[1] / 2)}, fj_) + step(.5, vJn.z) * step(0., df_) * sbBox(db_ - ${f_(Z[0] + Z[1] / 2)}, ${f_(Z[1] / 2)}, fj_)));
      if (!one_) { float d_ = ${f_(MK.drive || 1)} * x_, so_ = ${f_(Z[0] + Z[1] + 1 + MK.stop / 2)};   // stop lines on the lanes approaching each junction
        mk_ = max(mk_, sbBox(d_ - hw_ * .5, hw_ * .5 - .3, fx_) * step(.5, vJn.w) * step(0., db_) * sbBox(df_ - so_, ${f_(MK.stop / 2)}, fj_) + sbBox(d_ + hw_ * .5, hw_ * .5 - .3, fx_) * step(.5, vJn.z) * step(0., df_) * sbBox(db_ - so_, ${f_(MK.stop / 2)}, fj_)); }
      mk_ *= out_; }
    ${KB ? `{ float ax_ = abs(x_), sd_ = x_ > 0. ? step(hw_ - .5, cr_) : step(hw_ - .5, cl_), kn_ = step(0., min(db_, df_)) * sd_;   // the kerb along each edge (not where a parallel way's carriageway meets this one)
      vec2 fc_ = -sign(x_) * vNr; float sl_ = dot(fc_, normalize(uSunDir.xz + 1e-5));   // (its face toward the road, and whether that face turns to the sun)
      kt_ = kn_ * (sbBox(ax_ - hw_ - ${f_(KB[0] / 2)}, ${f_(KB[0] / 2)}, fx_) + max(sl_, 0.) * sbBox(ax_ - hw_ + ${f_(KB[1] / 4)}, ${f_(KB[1] / 4)}, fx_));   // (its lit top; its face when lit)
      sh_ = kn_ * clamp(-sl_ * 1.5, 0., 1.) * sbBox(ax_ - hw_ + ${f_(KB[1] / 2)}, ${f_(KB[1] / 2)}, fx_);   // (the gutter in its shade)
      float kf_ = smoothstep(${f_(KB[0] * 2)}, ${f_(KB[0] * 6)}, fx_); kt_ *= 1. - kf_; sh_ *= 1. - kf_; }` : ''}   // (gone as a pixel outgrows it: afar no lattice of outlined streets)
    vec4 o_ = sbOver(vec4(0.), ${v3_(MK.c)}, mk_ * ${f_(MK.k)});${KB ? `
    o_ = sbOver(o_, ${v3_(KB[2])}, min(kt_, 1.) * ${f_(KB[4] == null ? 1 : KB[4])}); o_ = sbOver(o_, vec3(.02), min(sh_, 1.) * ${f_(KB[3])});` : ''}
    if (o_.a < .004) discard;
    diffuseColor = vec4(o_.rgb / o_.a, o_.a); }`); } };
      { const ob_ = m.onBeforeCompile; m.onBeforeCompile = sh => { ob_(sh);   // (coming or going with today's city as the subject: dissolving by half-metre cells of the ground, never at once)
        sh.fragmentShader = sh.fragmentShader.replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\n  if (uStreetK < .999 && sbH(floor(vWm * 2.) + 3.7) > uStreetK) discard;'); }; }
      m.customProgramCacheKey = () => 'mini-streets ' + layer + (GR ? ' grain' : '');
      const mesh = new THREE.Mesh(g, m); mesh.receiveShadow = true; mesh.layers.set(L); mesh.frustumCulled = false; mesh.renderOrder = .5 + layer * .01; scene.add(mesh); return mesh; }); };
  const todayNow = () => {
      if (film && !S.fx && MAT && MAT.base && MAT.base.ground_in && cityMesh) { todayYears(cityMesh, S.PW, S.PD, MAT.base.ground_in.reachToday || 45, scale, roads, bands, grow ? (y, t) => { if (!(t > 0)) return y; const b = [...grow.bands].sort((p, q) => p.t - q.t).find(b => b.t + b.spread * .5 >= t); return b ? Math.max(y, b.hi - .5) : 1e4; } : null, todayL() && todayL().lanes ? [todayL().lanes[3], todayL().lanes[4] || 1e9] : 0);
        const by_ = BACK.uBackdropY.value, yr_ = U.uYear.value, sm_ = THREE.MathUtils.smoothstep; let yg_ = Infinity; const now_ = U.uNow ? U.uNow.value : 0;   // (the film's growth raises today's city band by band at its own times: the plaster arrives with them, not with the counter)
        if (grow && now_ >= grow.on) { yg_ = -Infinity; for (const b of grow.bands) if (now_ >= b.t + b.spread * .5) yg_ = Math.max(yg_, b.hi - .5); }
        TODAY_K.value.set(Math.min(Math.max(yr_, BACK.uDataY0.value), yg_), cityMesh.visible ? Math.max(U.uGrowRise ? U.uGrowRise.value : 0, sm_(yr_, by_ - 5, by_ + 5)) : 0, S.U.uDimTodayC ? S.U.uDimTodayC.value : 0);   // (y: today's city the subject, 0 to 1 with the modern section's own ramp: its ground, water and light come with its buildings, never in one frame)
        BAND_Y.value = grow && now_ >= grow.on ? yg_ : TODAY_K.value.x;   // (the growth's bands raise the city by their own clock, ahead of or behind the counter: their plaster with them)
        // today's details (rooftop pieces, massing, split buildings; streets: STREET_K) come and go over DETAIL_FADE s, never in one
        // frame: out before the growth begins and in after its last band (they stand still while it raises the city), in and out
        // with today's city becoming the subject (the modern section's own ramp, the white film's dim of it)
        const F_ = DETAIL_FADE, end_ = grow ? Math.max(...grow.bands.map(b => b.t + b.spread)) : 0, gk_ = !grow ? 1 : Math.max(1 - sm_(now_, grow.on - F_, grow.on), sm_(now_, end_, end_ + F_));
        const sk_ = (cityMesh.visible ? Math.max(U.uGrowRise ? U.uGrowRise.value : 0, sm_(yr_, by_ - 5, by_ + 5)) : 0) * (1 - sm_(TODAY_K.value.z, .2, .35));   // (with today's buildings as they come, the modern section's own ramp)
        STREET_K.value = sk_; ROOF_ON.value = sk_ * gk_; }
  };
  // today's water's reflection (todayLight water refl: [its share at a steep view, more toward a grazing one]): the scene drawn
  // from the eye mirrored in the water's plane (the ground under the shot's target), a quarter of the picture's size, clipped at
  // the plane (an oblique near plane, three.js Reflector's), without the plate and the land; the water samples it through REFL.M
  const RF = film && !FX && MAT && MAT.todayLight && todayL().water && todayL().water.refl ? { rt: new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType }), cam: new THREE.PerspectiveCamera(),
    n: new THREE.Vector3(0, 1, 0), p0: new THREE.Vector3(), cp: new THREE.Vector3(), rot: new THREE.Matrix4(), v: new THREE.Vector3(), lk: new THREE.Vector3(), pl: new THREE.Plane(), c4: new THREE.Vector4(), q: new THREE.Vector4() } : null;
  function reflect(target) {
    const L_ = todayL(), k_ = L_.all ? 1 : TODAY_K.value.y * (1 - THREE.MathUtils.smoothstep(TODAY_K.value.z, .3, .6)); REFL.K.value = k_; if (k_ < .002) return; REFL.D.value.set(camera.position.distanceTo(target) * 1.6, camera.position.distanceTo(target) * 4);   // (the reflection gone by four times the shot's distance)
    const W_ = Math.max(4, Math.round(size.x / renderer.getPixelRatio() / 4)), H_ = Math.max(4, Math.round(size.y / renderer.getPixelRatio() / 4)); if (RF.rt.width !== W_ || RF.rt.height !== H_) RF.rt.setSize(W_, H_);
    const { n, p0, cp, rot, v, lk, pl, c4, q } = RF, rc = RF.cam; p0.set(target.x, S.ground(target.x, target.z), target.z);
    camera.updateMatrixWorld(); cp.setFromMatrixPosition(camera.matrixWorld); rot.extractRotation(camera.matrixWorld);
    v.copy(p0).sub(cp).reflect(n).negate().add(p0); lk.set(0, 0, -1).applyMatrix4(rot).add(cp); lk.copy(p0).sub(lk).reflect(n).negate().add(p0);
    rc.copy(camera); rc.position.copy(v); rc.up.set(0, 1, 0).applyMatrix4(rot).reflect(n); rc.lookAt(lk); rc.updateMatrixWorld(); rc.projectionMatrix.copy(camera.projectionMatrix);
    REFL.M.value.set(.5, 0, 0, .5, 0, .5, 0, .5, 0, 0, .5, .5, 0, 0, 0, 1).multiply(rc.projectionMatrix).multiply(rc.matrixWorldInverse);
    pl.setFromNormalAndCoplanarPoint(n, p0).applyMatrix4(rc.matrixWorldInverse); c4.set(pl.normal.x, pl.normal.y, pl.normal.z, pl.constant);
    const P = rc.projectionMatrix.elements; q.set((Math.sign(c4.x) + P[8]) / P[0], (Math.sign(c4.y) + P[9]) / P[5], -1, (1 + P[10]) / P[14]); c4.multiplyScalar(2 / c4.dot(q));
    P[2] = c4.x; P[6] = c4.y; P[10] = c4.z + 1; P[14] = c4.w; rc.projectionMatrixInverse.copy(rc.projectionMatrix).invert();
    const hid = [plate, skirt, marks, ctx, ...(STREET_MESH || [])].filter(m => m && m.visible); for (const m of hid) m.visible = false; REFL.T.value = null;
    const rt0 = renderer.getRenderTarget(); renderer.setRenderTarget(RF.rt); renderer.clear(); renderer.render(scene, rc); renderer.setRenderTarget(rt0);
    for (const m of hid) m.visible = true; REFL.T.value = RF.rt.texture; }
  const builtNow = () => { if (FP_ && MAT && MAT.base && MAT.base.ground_in && BUILT_C) builtMask(Object.values(S.eras), S.PW, S.PD, scale, MAT.base.ground_in.reach, MAT.base.flock ? MAT.base.flock.tree : 15); };
  async function render({ target, d, sharp = 0, sunAz = null }) {   // (sunAz: { az, own } the film's sun for this moment, main.js SUN_AT)   // (sharp: 0..1, a living moment's picture up, sharp throughout)
    if (film && MAT && MAT.base && MAT.base.ground_in && dataDir) await greenData(dataDir);   // (a city's green and streets, before its first frame)
    todayNow(); if (film && MAT && MAT.roofs && !(await footprintsDue())) roofsMesh(); if (film && MAT && dataDir) streetsMesh();   // (the rooftops come after today's replacement footprints, when they come in this frame)
    { const on_ = ROOF_ON.value > .002;   // (today's rooftops not drawn at all while today's city is not the subject: hundreds of thousands of instances folded to nothing in the shader still cost a period city's frame)
      for (const m_ of [...(ROOF_MESH || []), ...(RIM_MESH ? [RIM_MESH] : []), ...(MASS_MESH || [])]) m_.visible = on_;
      for (const m_ of STREET_MESH || []) m_.visible = STREET_K.value > .002; }   // (nor today's streets: their vertices folded away in a period city's frames, as the rooftops')
    if (film && FILM_PIC.glb && !GLB_DONE) { GLB_DONE = true; for (const o of FILM_PIC.glb) { try { const r_ = await swap(o); console.log('glb', JSON.stringify(r_)); } catch (e) { console.error(`glb ${o.url}: ${e.message}`); } }
      // (a glb entry's plaza: { r: [its inner disc's, its lawn ring's inner and outer, its paving's outer radius] m, at: [x, z] m from near }: the landmark's own round plaza, todayLight roundPlaza)
      FILM_PIC.glb.filter(o => o.plaza && o.near).slice(0, 4).forEach((o, i) => { const r = o.plaza.r, at = o.plaza.at || [0, 0]; RPLAZA.P.value[i].set(o.near[0] + at[0] * scale, o.near[1] + at[1] * scale, r[1], r[2]); RPLAZA.Q.value[i].set(r[0], r[3], 0, 1); }); }   // (FILM_PIC glb: detailed models in place of buildings, ?pic= for a still)
    window.__MINI = { mass: () => MASS, roofs: roofList, scale, landmarks: () => landmarks.map(r => { const b = new THREE.Box3().setFromObject(r); return [b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z]; }), scene, camera, eraMeshes, cityMesh, plate, trees: () => TF.objs(), flock: () => ({ ms: FL.ms, ...FL.stat }), sun, target: target.clone(), d, swap, detail: DET };   // (for a script: tools that export the frame's geometry, swap)
    renderer.getDrawingBufferSize(size); pxK.value = camera.projectionMatrix.elements[5] * size.y / renderer.getPixelRatio() / 2; ROOF_PX.value = 2 / (camera.projectionMatrix.elements[5] * 1080) / scale;   // (the picture's pixels, not the drawing buffer's: it is drawn at twice their number and shrunk)
    const up = E => E.mesh.visible && !E.mesh.userData.gone;   // (the film: a city gone may still show its foundations, without its detail)
    if (DET) { for (const [id, E] of Object.entries(S.eras)) if (up(E) && !DET.has(id)) DET.set(id, detailOf(id));
      clearNow = [];
      for (const [id, g] of DET) { const G = await g; G.visible = up(S.eras[id]); if (G.visible) clearNow.push(G.userData.treeOK); }
      builtNow(); boats(); flockAt(target, d); }   // (the built-up mask as this frame has it before the trees read it: a frame drawn first, a render's worker's or a seek's, plants by its own)
    for (const P of PATHS) { const t = U.uNow.value, r = P.r, a = sm(r.on, r.on + .3, t) * (1 - sm(r.off - .6, r.off, t));   // (the routes' paths, as they draw and go)
      P.mesh.visible = a > .002; P.mesh.material.opacity = a; P.u.uP.value = sm(r.on, r.on + r.draw, t) * 1.0001; }
    if (film && MAT && cityMesh && cityMesh.visible && TODAY_K.value.y > .002) await todayFootprints(target, d);   // (as soon as today's city begins to come: they fade in with it)   // (today's replacement footprints, once: before its rooftops and the detailed models)
    if (FPT.mesh) FPT.mesh.visible = cityMesh.visible;
    const swapM = [];   // (the studio's materials back after the frame)
    for (const m of [...eraMeshes, cityMesh]) if (m.visible) colour(m);
    for (const m of [...eraMeshes, cityMesh, plate].filter(Boolean)) { if (!m.userData.mini) continue; swapM.push([m, m.material, m.customDepthMaterial]); m.material = m.userData.mini; m.customDepthMaterial = m.userData.miniDepth; m.layers.enable(L); m.castShadow = m.receiveShadow = true; }   // (the film: shadows deformed as the city stands)
    { const src = [...eraMeshes.filter(m => m.visible), ...(cityMesh.visible ? [cityMesh, ...(FPT.mesh ? [FPT.mesh] : [])] : [])]; for (const l of landmarks) l.traverse(o => { if (o.isMesh) src.push(o); });
      TF.update(target, d, src); }
    const LT_ = FP_ ? todayL() : null, tsE_ = LT_ ? (LT_.all ? 1 : TODAY_K.value.y * (1 - THREE.MathUtils.smoothstep(TODAY_K.value.z, .3, .6))) : 0;   // (today's city the subject: its own light)
    const kAir_ = FP_ && FILM_PIC.pool ? THREE.MathUtils.smoothstep(d, .06, FILM_PIC.pool[1]) : 0, elD_ = THREE.MathUtils.lerp(FP_ && FILM_PIC.rake ? THREE.MathUtils.lerp(SUN_EL, FILM_PIC.rake, kAir_) : SUN_EL, LT_ && LT_.sunEl ? LT_.sunEl : 0, LT_ && LT_.sunEl ? tsE_ : 0);   // (an aerial's raking sun, FILM_PIC rake)
    const v = camera.position.clone().sub(target), kd = U.uKeyDir.value, el = THREE.MathUtils.degToRad(elD_), r = d * 1.2;
    const az = film && sunAz && LT_ && LT_.sunLeft != null ? THREE.MathUtils.degToRad(sunAz.az + (sunAz.own ? 0 : LT_.sunLeft))   // (the look's sun per shot: behind and to the left of the camera, todayLight sunLeft; a node's own)
      : film ? (camAz != null ? THREE.MathUtils.degToRad(camAz + (FP_ ? FILM_PIC.sunSide + (LT_ && LT_.side || 0) * tsE_ : 55)) : Math.atan2(kd.x, kd.z)) : Math.atan2(v.x, v.z) + THREE.MathUtils.degToRad(SUN_SIDE);   // the sun: behind the eye, to its left, 40 degrees up (fx light: lower); the film: from the key light's bearing
    sun.position.set(target.x + r * Math.sin(az) * Math.cos(el), target.y + r * Math.sin(el), target.z + r * Math.cos(az) * Math.cos(el)); sun.target.position.copy(target);
    if (S.fxSun) sun.position.copy(target).addScaledVector(S.fxSun, r);   // (fx light: the sun fixed in the world, as the white model's)
    const c = sun.shadow.camera; c.left = c.bottom = -d * 1.6; c.right = c.top = d * 1.6; c.near = r * .2; c.far = r * 2.5;
    if (FP_) fitShadow(c, sun, target, d);   // (the film: the shadow over the ground the frame shows, its texels where they are seen)
    c.updateProjectionMatrix();
    const bg0 = scene.background, fog0 = scene.fog, lay0 = camera.layers.mask;
    const nt = film ? U.uNight.value : 0;   // the film at night: the sun down to a moon's light, the sky dark, the windows and the studio's light the brighter
    // a burning city's pall (its smoke: studio.js fireByDay) dims the light and warms it, by the fire's size
    let fk = 0, pall = null; if (film) for (const f of Object.values(S.fires)) if (f.day) { const k = f.u.uA.value * THREE.MathUtils.clamp(f.size / 1500, .15, 1); if (k > fk) { fk = k; pall = f; } }
    if (pall) { const F = pall.day.F, o = pall.u.uO.value; BACK.uPallC.value.set(o.x + 450 * scale, o.y + 135 * scale); BACK.uPallR.value = F.uMaxR.value * 1.15 + 600 * scale; }   // (the smoke drifts downwind: studio.js fireByDay)
    BACK.uPallK.value = fk;
    if (film) { sun.intensity = SUN0 * (1 - .9 * nt) * (1 - .2 * fk) * Math.sqrt(Math.sin(THREE.MathUtils.degToRad(SUN_EL)) / Math.sin(THREE.MathUtils.degToRad(elD_)));   // (a lower sun a little stronger: the lit faces bright, the ground darker)
      sun.color.copy(SUNC).lerp(NIGHT.sun, nt).lerp(PALL.sun, .4 * fk); sky.intensity = SKY0 * (1 - .78 * nt) * (1 - .15 * fk);   // (each frame from its own: a comment had swallowed this line, so the sky's and the sun's changes piled up frame by frame)
      bgNow.copy(bg).lerp(NIGHT.bg, nt).lerp(PALL.sky, .3 * fk); fog.color.copy(FILM_PIC.fogC ? new THREE.Color(FILM_PIC.fogC) : FOG).lerp(NIGHT.fog, nt).lerp(PALL.sky, .3 * fk);
      S.colourLight.value = FP_ ? FILM_PIC.projector + .6 * nt : .55 + .6 * nt;   // (the film's picture: none of the projector's light by day, main.js QUIET)
      if (FP) { FP.bloom.threshold = THREE.MathUtils.lerp(2.2, .9, nt); FP.bloom.strength = THREE.MathUtils.lerp(.1, .45, nt); }
      if (ctx) { swapM.push([ctx, ctx.material, ctx.customDepthMaterial]); ctx.material = far; ctx.userData.vis0 = ctx.visible; ctx.visible = true; ctx.layers.enable(L); ctx.receiveShadow = true; } }
    scene.background = film ? bgNow : bg; const kA_ = FP_ && FILM_PIC.pool ? THREE.MathUtils.smoothstep(d, .06, FILM_PIC.pool[1]) : 0;   // (an aerial's share: its pool and haze)
    fog.near = d * (FP_ && FILM_PIC.haze ? THREE.MathUtils.lerp(FILM_PIC.fogNear, FILM_PIC.haze[0], kA_) : FP_ ? FILM_PIC.fogNear : film ? 2.6 : 1.6); fog.far = d * (FP_ && FILM_PIC.haze ? THREE.MathUtils.lerp(FILM_PIC.fogFar, FILM_PIC.haze[1], kA_) : FP_ ? FILM_PIC.fogFar : film ? 14 : 8); scene.fog = FX && FX.haze ? null : fog; camera.layers.set(L);   // (the film: less haze over the plate)
    const sd = sun.position.clone().sub(target).normalize(); SUN_DIR.value.copy(sd); SUN_COL.value.copy(sun.color).multiplyScalar(sun.intensity * .25);
    if (relief) { U.uFxSun.value.copy(sd); if (FX.light) { U.uFxLitC.value.setRGB(1, 1, 1).lerp(new THREE.Color(1.1, .99, .84), warm); U.uFxShadeC.value.setRGB(1, 1, 1).lerp(new THREE.Color(.82, .9, 1.1), warm); } }
    if (dome) dome.u.uSunD.value.copy(sd);
    if (FP) {   // the film's lens for this distance (main.js lens), with the stronger depth of field
      if (lens) { if (!film) lens(d); FP.dof.focus = S.post.dof.focus; FP.dof.aper = FP_ ? S.post.dof.aper * FILM_PIC.dof.k : film || FX.dof ? S.post.dof.aper : 0; FP.dof.maxCoc = FP_ ? FILM_PIC.dof.max : S.post.dof.maxCoc; FP.dof.band = FP_ ? byD(FILM_PIC.dof.band, d) : S.post.dof.band; }   // (the film: as main.js set it for this frame, a living moment's sharp picture included)
      // a model's lens (FILM_PIC.dof.A: its opening in the city's metres, the model's own times its scale): the blur a camera that
      // close to a model that small gives, the same opening at every distance (a wide shot from afar blurs less, as a photograph
      // of the whole table does); at: the focus as a share of the shot's distance (beyond 1: the near ground the softer)
      const A_ = FILM_PIC.dof.A || byD(FILM_PIC.dof.Ak || 0, d) * d / scale;   // (Ak: the opening as a share of the shot's distance: every shot the same model seen as close)
      if (FP_ && lens && A_ && !(S.post.dof.aper < 1e-6)) { FP.dof.aper = 1080 * A_ * scale / (4 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2)); FP.dof.focus = S.post.dof.focus * (FILM_PIC.dof.at || 1); }   // (a living moment's sharp picture kept where its aperture is 0; its fade in and out not yet followed)
      if (FP_ && MAT && MAT.base && MAT.base.tex && U.uGroundN) U.uGroundN.value = 0;
      todayNow();   // (again: the lights and the dim as this frame has them)
      builtNow();   // (a material's plate: the period cities' open ground is the plate itself, not patches of earth and gravel on it)
      { const T_ = MAT && MAT.todayH, bex = S.U.uScaleH ? S.U.uScaleH.value / scale : 3; HSCALE_T.value = FP_ && T_ ? THREE.MathUtils.lerp(Math.min(1, T_.k / bex), 1, THREE.MathUtils.smoothstep(d, T_.near, T_.far)) : 1; if (FP_ && FILM_PIC.todayLift) HSCALE_T.value *= FILM_PIC.todayLift; }   // (todayLift: a shot's own constant lift of today's heights, ?pic=, its roof pieces not lifted)   // (today's city: the model's own heights, x k, nearer than `near`, its exaggeration back by `far`)
      if (FILM_PIC.pool) { const k_ = THREE.MathUtils.smoothstep(d, .06, FILM_PIC.pool[1]); POOL.value.set(target.x, target.z, d * .95, THREE.MathUtils.lerp(1, FILM_PIC.pool[0], k_)); } else POOL.value.set(0, 0, 1e9, 1);
      HSCALE.value = FP_ && FILM_PIC.hscale ? THREE.MathUtils.lerp(FILM_PIC.hscale.k, 1, THREE.MathUtils.smoothstep(d, FILM_PIC.hscale.near, FILM_PIC.hscale.far)) : 1;   // (a close shot's heights)
      if (FX && FX.dof && !S.post.dof.rtB) fxLens(FP.dof, FX.dof, d);   // (the studio's own pass applied it already where it has the stronger gather)
      if (FP.dof.haze) FP.dof.haze.uHazeSunD.value.copy(sd);
      if (FP.dof.ao) FP.dof.ao.updateGtaoMaterial({ radius: FP_ ? THREE.MathUtils.clamp(d * FILM_PIC.aoR[0], scale * FILM_PIC.aoR[1], scale * FILM_PIC.aoR[2]) : fxAoRadius(d) });   // (the film: contact, a few metres at a crevice, never a whole court in shade)
      if (FP_ && MAT && MAT.todayLight) {   // today's city the subject (a material's todayLight): a clear key, a cool sky fill, its street canyons darker, a mild bloom on glass
        const L_ = todayL(), ts_ = L_.all ? 1 : TODAY_K.value.y * (1 - THREE.MathUtils.smoothstep(TODAY_K.value.z, .3, .6));   // (todayLight all: every shot)
        if (soft) { const v_ = camera.position.clone().sub(target), h_ = Math.hypot(v_.x, v_.z) || 1, e_ = THREE.MathUtils.degToRad(L_.soft ? L_.soft[1] : 8);
          soft.position.set(target.x + v_.x / h_ * Math.cos(e_) * d, target.y + Math.sin(e_) * d, target.z + v_.z / h_ * Math.cos(e_) * d); soft.target.position.copy(target); soft.target.updateMatrixWorld();
          soft.intensity = (L_.soft ? L_.soft[0] : 0) * ts_ * SUN0 / 2.7; }
        if (L_.pool != null) POOL.value.w = THREE.MathUtils.lerp(POOL.value.w, Math.max(POOL.value.w, L_.pool), ts_);   // (daylight: the light pool's floor lifted, no dark surround)
        if (L_.fogC) fog.color.lerp(new THREE.Color(L_.fogC), ts_);
        if (L_.vignette != null) FP.vig.uniforms.amt.value = THREE.MathUtils.lerp(FILM_PIC.vignette, L_.vignette, ts_);
        for (const k_ of ['sat', 'contrast']) if (L_[k_] != null) FP.vig.uniforms[k_].value = THREE.MathUtils.lerp(FILM_PIC[k_], L_[k_], ts_);   // (its colour's saturation and contrast)
        if (!SKY_C0) SKY_C0 = [sky.color.clone(), sky.groundColor.clone()];
        sky.color.copy(SKY_C0[0]).lerp(new THREE.Color(L_.skyC), ts_); sky.groundColor.copy(SKY_C0[1]).lerp(new THREE.Color(L_.skyGround), ts_);
        sky.intensity *= THREE.MathUtils.lerp(1, L_.sky, ts_); sun.intensity *= THREE.MathUtils.lerp(1, L_.sun, ts_);
        FP.dof.aoAmt = THREE.MathUtils.lerp(FILM_PIC.ao, Array.isArray(L_.ao) ? THREE.MathUtils.lerp(L_.ao[0], byD(L_.ao, d), TODAY_K.value.y * (1 - THREE.MathUtils.smoothstep(TODAY_K.value.z, .3, .6))) : L_.ao, ts_);   // (todayLight ao: a number, or [close, wide] eased by the shot's distance while today's city is the subject: a wide shot's gaps between today's buildings not sunk in dark; a period city keeps the close one)
        FP.bloom.threshold = THREE.MathUtils.lerp(2.2, L_.bloom[0], ts_); FP.bloom.strength = THREE.MathUtils.lerp(.1, L_.bloom[1], ts_);   // (todayLight bloom: [threshold, strength]; this statement had sat inside the comment above, so a lit wall bloomed into a veil)
        if (L_.sunC) sun.color.lerp(new THREE.Color(L_.sunC), ts_);
        FP.vig.uniforms.uExpo.value = THREE.MathUtils.lerp(1, L_.exposure ?? 1, ts_);   // (the whole picture's exposure)
        if (FP.dof.coc.material.uniforms.uEdge) { const u_ = FP.dof.coc.material.uniforms, rt_ = FP.dof.rt; u_.uEdge.value = (L_.edge || 0) * ts_; u_.uPx.value.set(1 / rt_.width, 1 / rt_.height);
          u_.uPxK.value = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) / rt_.height / scale; }   // (metres a supersampled pixel spans at unit depth)
        FP.vig.uniforms.uGrain.value = (L_.grain || 0) * ts_; FP.vig.uniforms.uFilmic.value = (L_.filmic || 0) * ts_;
        FP.dof.aper *= THREE.MathUtils.lerp(1, L_.dof ?? 1, ts_); FP.dof.band *= THREE.MathUtils.lerp(1, L_.band ?? 1, ts_);
        if (L_.haze) { fog.near = THREE.MathUtils.lerp(fog.near, d * L_.haze[0], ts_); fog.far = THREE.MathUtils.lerp(fog.far, d * L_.haze[1], ts_); }   // (today's haze as a fog)
        const ua_ = FP.dof.coc.material.uniforms; if (ua_.uAir) { const A_ = L_.air; ua_.uAir.value.set(d * A_[0], d * A_[1], A_[2] * scale, ts_); ua_.uAirC.value.set(L_.dome ? L_.dome[0] : L_.fogC); const F_ = L_.far || [1, 2, 1, '#ffffff']; let f0_ = d * F_[0], f1_ = d * F_[1], fk_ = F_[2], fc_ = null, fs_ = F_[5] ?? 1; camera.updateMatrixWorld();
          if (F_[4] && TODAY_K.value.y > .5 && TODAY_K.value.z < .3) { const r_ = new THREE.Vector3(0, 1, .5).unproject(camera).sub(camera.position).normalize(), t_ = F_[4][2] ? 1 - THREE.MathUtils.smoothstep(d, F_[4][2][0], F_[4][2][1]) : 1;
            const W_ = F_[4][4], w_ = W_ ? 1 : t_;   // ([4]: a wide shot's top band, where [2] has faded the raking softening out: [the share of its own contrast kept, the tint, the share of its chroma kept]: cooled as the paintings' far city is, its buildings still distinct)
            if (r_.y < -.02 && w_ > 0) { const dt_ = (camera.position.y - target.y) / -r_.y, G_ = F_[4][3], g_ = G_ ? THREE.MathUtils.smoothstep(dt_ / d, G_[0], G_[1]) : 0;   // ([3]: [the top edge's depth over the shot's distance from, to which, the kept share then, from and whole then, the tint then]: the farther beyond the subject the top edge lies, the more air it is seen through)
              f0_ = THREE.MathUtils.lerp(f0_, Math.min(f0_, THREE.MathUtils.lerp(F_[4][0], G_ ? G_[3] : 0, g_) * dt_), w_); f1_ = THREE.MathUtils.lerp(f1_, Math.min(f1_, THREE.MathUtils.lerp(F_[4][1], G_ ? G_[4] : 0, g_) * dt_), w_); fk_ = THREE.MathUtils.lerp(F_[2], G_ ? G_[2] : F_[2], g_ * t_); if (G_ && G_[5]) fc_ = new THREE.Color(F_[3]).lerp(new THREE.Color(G_[5]), g_ * t_);
              if (W_) { fk_ = THREE.MathUtils.lerp(W_[0], fk_, t_); fc_ = new THREE.Color(W_[1]).lerp(fc_ || new THREE.Color(F_[3]), t_); fs_ = THREE.MathUtils.lerp(W_[2] ?? fs_, fs_, t_); } } }   // (far [4]: a raking shot of today's city whose frame ends on the city, not the sky, softens toward its own top edge's ground: from and whole by these shares of that distance, whichever is nearer, all of it in shots nearer than [2][0], from [2][1] only [4]'s cooling; a period city's shots as they were)
          ua_.uAirF.value.set(f0_, f1_, fk_, L_.far ? ts_ : 0); ua_.uAirFC.value.set(fc_ || F_[3]); ua_.uAirFS.value = fs_; camera.updateMatrixWorld(); ua_.uAirIP.value.copy(camera.projectionMatrixInverse); ua_.uAirCW.value.copy(camera.matrixWorld);
          fog.near = THREE.MathUtils.lerp(fog.near, 1e4, ts_); fog.far = THREE.MathUtils.lerp(fog.far, 2e4, ts_); }   // (today's air in the picture's depth (above): no fog)
        GLASS_SKY.value.setRGB(.80, .86, .92).lerp(new THREE.Color(L_.glassSky || '#e6edf4'), ts_); GLASS_K.value = THREE.MathUtils.lerp(1, L_.glassK ?? 1, ts_); DOME_R.value = L_.domeRate ?? 25;   // (glassSky, glassK: the sky in the glass; domeRate: the dome's blue, how soon above the horizon)
        if (domeT) { domeT.u.uSunC.value.set(L_.dome[2] || '#000000').multiplyScalar(ts_); domeT.u.uSunD.value.copy(sd);   // (dome[2]: the sun's glow on the sky, a low sun's)
          domeT.mesh.visible = ts_ > .002; const CL_ = L_.dome[3]; domeT.mesh.material.uniforms.uCloud.value.set(CL_ ? CL_[0] * ts_ : 0, CL_ ? CL_[1] : 1, CL_ ? CL_[2] : .5, 0); if (CL_) domeT.mesh.material.uniforms.uCloudC.value.set(CL_[3]); domeT.u.uHor.value.copy(bgNow).lerp(new THREE.Color(L_.dome[0]), ts_); domeT.u.uZen.value.copy(bgNow).lerp(new THREE.Color(L_.dome[1]), ts_); }
        sun.shadow.radius = THREE.MathUtils.lerp(1, L_.shadowR ?? 1, ts_); }   // (soft-edged shadows: PCF's own radius, in the map's texels)
      if (FP_ && FILM_PIC.dof.tilt && FP.dof.coc.material.uniforms.uTilt) { const T0_ = FILM_PIC.dof.tilt, TW_ = FILM_PIC.dof.tiltWide, kw_ = TW_ ? THREE.MathUtils.smoothstep(d, TW_[3], TW_[4]) : 0;   // the model photographer's lens (above)
        const T_ = T0_.map((v, i) => i < 3 && TW_ ? THREE.MathUtils.lerp(v, TW_[i], kw_) : v);   // (dof tiltWide: [where the soft bands begin, are whole, the largest blur] in a wide shot, from the shot's distance [3] whole by [4]: its far third legible)
        FP.dof.coc.material.uniforms.uTilt.value.set(1, T_[0], T_[1], T_[3] ?? 1);
        FP.dof.coc.material.uniforms.uTiltR.value.set(T_[4] ?? .05, T_[5] ?? .3, T_[6] ?? T_[4] ?? .05, T_[7] ?? T_[5] ?? .3);
        FP.dof.maxCoc = S.post.dof.aper < 1e-6 ? 0 : T_[2] * FP.dof.rt.height / FP.dof.s / 1080; }   // (a living moment's sharp picture kept)
    }
    if (BAND) { const rt = FP.composer.renderTarget1; for (const b of BAND) { b.uniforms.px.value.set(1 / rt.width, 1 / rt.height); b.uniforms.k.value = rt.height / 1080 * (1 - sharp); } }
    renderer.getDrawingBufferSize(size); composer.setSize(size.x / renderer.getPixelRatio(), size.y / renderer.getPixelRatio());
    ht.uniforms.h.value = 4 / size.x; vt.uniforms.v.value = 4 / size.y; ht.uniforms.r.value = vt.uniforms.r.value = .5;
    ao.setSize(size.x, size.y); ao.updateGtaoMaterial({ radius: d * .02 });
    renderer.shadowMap.needsUpdate = true;
    const env0 = scene.environmentIntensity; if (LT_ && LT_.env != null) scene.environmentIntensity = THREE.MathUtils.lerp(env0, LT_.env, tsE_);   // (todayLight env: the studio's room environment, an even fill that lifted every shade and shadow, at this share)
    if (RF) reflect(target);   // (today's water: the scene mirrored in it, first)
    (FP ? FP.composer : composer).render();
    scene.background = bg0; scene.fog = fog0; camera.layers.mask = lay0; scene.environmentIntensity = env0;
    for (const [m, mat, dm] of swapM) { m.material = mat; m.customDepthMaterial = dm; }
    if (ctx) ctx.visible = ctx.userData.vis0;
  }
  return { render, warm: warmUp, sun, sky, card: info, swap, ruinT: RUIN_T, still: { keys: STILL_KEYS, next: nextShot } };
}

// the modern section, for the colour film (the counter reaching film.look.backdrop_from, 1800 by default, or the modern growth
// begun): before it a city's present fabric did not stand, from it much of it did. Before it, today's city goes where the white
// film dims it, and a period city's foundations stay; from it, today's city stays there as a muted backdrop (none of it the data
// first sees after the year told: uDataY0, its earliest epoch, counts as standing before) and the foundations are cleared (main.js RUINS_TO)
const MODERN_GLSL = 'max(uGrowRise, smoothstep(uBackdropY - 5., uBackdropY + 5., uYear))';

// the film's materials (miniLook film): the look's colours on the studio's deformation (u: a period city's uniforms, studio.js
// addEra; null: today's city); mat a colour material, or a depth material for the shadows (the same shape); fire: the period
// city's own fire (studio.js addFire, a whole city burning), whose front chars it building by building.
// A period city: a building taken back or lost leaves its foundations (uRuinH as drawn, the palette's stone, charred after a fire)
// until a later period city rises on that ground or the modern section begins (main.js sets uRuinLater, the channels of later
// cities, and uRuinT, how far each channel's city has risen); a burning building chars as the fire reaches it, its walls glowing
// while it burns. Today's city: where the white film dims it under a period city, before the modern section it goes, building by
// building (gone at fadeAt: no pale card in a period's story), from it it stays as a muted backdrop (its own colours, less
// saturated, flatter); it goes only where the white film hides it; a building new in the modern growth warm while it is new, as
// the white film's. Both: an area the story marks (an epoch with buildings) tints the buildings in it; lit windows at night
// a corner's averaged normal on each vertex (aSoft), for a material whose edges are rounded (FILM_PIC.looks soft): every face
// takes a share of it toward its corners, shading as a soft, hand-made edge would
function softNormals(g) {
  if (g.attributes.aSoft) return; const P = g.attributes.position, N = g.attributes.normal, q = 1e7, acc = new Map(), key = i => Math.round(P.getX(i) * q) + ',' + Math.round(P.getY(i) * q) + ',' + Math.round(P.getZ(i) * q);
  for (let i = 0; i < P.count; i++) { const k = key(i), a = acc.get(k) || acc.set(k, [0, 0, 0]).get(k); a[0] += N.getX(i); a[1] += N.getY(i); a[2] += N.getZ(i); }
  const s = new Float32Array(P.count * 3);
  for (let i = 0; i < P.count; i++) { const a = acc.get(key(i)), l = Math.hypot(...a) || 1; s[i * 3] = a[0] / l; s[i * 3 + 1] = a[1] / l; s[i * 3 + 2] = a[2] / l; }
  g.setAttribute('aSoft', new THREE.Float32BufferAttribute(s, 3));
}
// the base's photographed surface (FILM_PIC.looks base tex: a folder of Diffuse, nor_gl and Rough maps), loaded once
let SLATE_MAPS = null;
function slateMaps() {
  if (SLATE_MAPS) return SLATE_MAPS; const L_ = new THREE.TextureLoader(), dir = new URL(`./tex/${MAT.base.tex}/`, import.meta.url).href;
  const t = (f, srgb) => { const x = L_.load(dir + f); x.wrapS = x.wrapT = THREE.RepeatWrapping; x.anisotropy = 8; if (srgb) x.colorSpace = THREE.SRGBColorSpace; return x; };
  return SLATE_MAPS = { uSunDir: SUN_DIR, uSunCol: SUN_COL, uRefl: REFL.T, uReflM: REFL.M, uReflK: REFL.K, uReflD: REFL.D, uBandC0: BAND_C[0], uBandC1: BAND_C[1], uBandHi: BAND_HI, uBandY: BAND_Y, uGreen: GREEN, uGreenOn: GREEN_ON, uRp: RPLAZA.P, uRq: RPLAZA.Q, uYearW: YEAR_W, uYearT: YEAR_T, uYearC: YEAR_C, uLanes: LANES, uTodayK: TODAY_K, uGeoT: GEO_T, uBuilt: BUILT, uTrees: TREES, uPool: POOL, uSlateC: { value: t('Diffuse.jpg', true) }, uSlateN: { value: t('nor_gl.jpg') }, uSlateR: { value: t('Rough.jpg') } };
}
// a material's base under the model (FILM_PIC.looks: maquette, clay), in place of the painted land: m_ the metres, vFxW the world
function baseGLSL(B, scale, town = false, far = false, then = false) {   // (then: the film's water as it was, studio.js wThen)
  const f3 = x => (+x).toFixed(3), v3 = c => `vec3(${c.map(x => (+x).toFixed(3)).join(', ')})`, TL = todayL(), wAt = uv => then ? `wThen(${uv}, (${uv} - .5) * uPlateM)` : `texture2D(uWaterM, ${uv}).r`;
  if (B.tex) return `
  { float y_ = vFxW.y / ${scale.toFixed(6)} / ${B.step.toFixed(2)}, c_ = fract(y_), w_ = max(fwidth(y_), 1e-4);   // the photographed slate, two scales of it turned against each other (no repeat afar), lit by its own normal and roughness (slateN_, slateR_)
    vec2 a_ = m_ / ${B.size.toFixed(1)}, b_ = mat2(.8, -.6, .6, .8) * m_ / ${(B.size * 6.3).toFixed(1)};
    vec3 c1_ = texture2D(uSlateC, a_).rgb, c2_ = texture2D(uSlateC, b_).rgb; float l1_ = dot(c1_, vec3(.2126, .7152, .0722)), l2_ = dot(c2_, vec3(.2126, .7152, .0722));
    float fd_ = smoothstep(.4, 2., length(fwidth(a_)) * 1024.);   // (texels a pixel: afar its pattern calms to its mean, no repeat)
    float sg_ = mix(l1_, ${B.mean.toFixed(3)}, fd_ * .75) / ${B.mean.toFixed(3)} * mix(1., l2_ / ${B.mean.toFixed(3)}, .35);   // (the slate's grain)
    vec3 sl_ = ${v3(B.slate)} * sg_;   // (its grey only: a neutral charcoal)
    sl_ *= 1. + .05 * clamp(floor(y_ - ${(20 / B.step).toFixed(2)}), 0., 4.);   // (each sheet up a little lighter)
    sl_ *= mix(1., ${B.edge.toFixed(2)}, (1. - smoothstep(w_ * .8, w_ * 1.6, c_)) * step(w_, .15));   // (its edge, faint, close only)
    slateN_ = texture2D(uSlateN, a_).xyz * 2. - 1.; slateR_ = texture2D(uSlateR, a_).r; vec3 sN0_ = slateN_; float sR0_ = slateR_;   // (kept: today's board is this slate)
    ${B.ground_in ? `{ vec2 pu_ = vXZ / uPlateM + .5; float in_ = step(0., pu_.x) * step(pu_.x, 1.) * step(0., pu_.y) * step(pu_.y, 1.);   // (the maps cover the plate: beyond it a clamped edge texel ran on as a long strip)
      float tw_ = in_ * texture2D(uBuilt, vXZ / uPlateM + .5).r, k_ = smoothstep(.5, .72, tw_), px_ = length(fwidth(m_));   // (px_: metres a pixel)
      float yw_ = in_ * texture2D(uYearW, vXZ / uPlateM + .5).r * 255., yt_ = in_ * texture2D(uYearT, vXZ / uPlateM + .5).r * 255., yc_ = uTodayK.x - 1899.;   // today's city: its built-up area once built (todayYears), its blocks
      vec4 yc4_ = in_ * texture2D(uYearC, vXZ / uPlateM + .5); float bc_ = -1.; { vec3 b0_ = texture2D(uBandC0, vXZ / uPlateM + .5).rgb, b1_ = texture2D(uBandC1, vXZ / uPlateM + .5).rgb; float yy_ = uBandY + .5;   // (the cover of the last band the year has completed)
        if (uBandHi[0] < 9e4) { bc_ = 0.; if (yy_ >= uBandHi[0]) bc_ = b0_.r; if (yy_ >= uBandHi[1]) bc_ = b0_.g; if (yy_ >= uBandHi[2]) bc_ = b0_.b; if (yy_ >= uBandHi[3]) bc_ = b1_.r; if (yy_ >= uBandHi[4]) bc_ = b1_.g; if (yy_ >= uBandHi[5]) bc_ = b1_.b; } }
      float kt_ = uTodayK.y * max(bc_ >= 0. && uTodayK.z < .3 ? smoothstep(.45, .8, bc_ * in_) : smoothstep(.6, .75, yc4_.r) * step(.5, yw_) * step(yw_, yc_ + .5), uGreenOn * (1. - smoothstep(.3, .6, uTodayK.z)) * smoothstep(.6, .75, yc4_.b) * step(.5, yt_) * step(yt_, yc_ + .5)),   // (a block's plaster when its buildings are built; the extent's when the extent reaches it)
       ft_ = uTodayK.y * step(.5, yt_) * step(yt_, yc_ + .5), st_ = kt_ * (.55 * smoothstep(.15, .38, yc4_.g) + .45 * smoothstep(.6, .85, yc4_.g));   // (st_: a street through the plaster)
      tw_ = max(tw_, kt_); k_ = max(k_, kt_);
      float hs_ = length(vec2(dFdx(vFxW.y), dFdy(vFxW.y))) / max(length(vec2(dFdx(vFxW.x), dFdy(vFxW.x)) + vec2(dFdx(vFxW.z), dFdy(vFxW.z))), 1e-6), rk_ = 0.;   // (the ground's slope as drawn; rk_ its rock)
      ${B.land ? `// the countryside: the model's own land, a muted olive and ochre flock, fields faintly; on the steep slopes the rock (the photo: its light grey, its own normal) with scrub
      { float fq_ = fxLn(floor(m_ / ${B.land.field.toFixed(1)}) * 1.7);   // (a field a cell, faint)
        float fa_ = smoothstep(3., 9., length(fwidth(m_)));   // (afar: fields faint strips, the grain gone)
        vec3 ld_ = pow(mix(${v3(B.land.olive)}, ${v3(B.land.ochre)}, smoothstep(.3, .75, fxLn(m_ / 310.) * mix(.6, .8, fa_) + mix(fq_ * .4, .1, fa_))), vec3(2.2)) * (.9 + .1 * mix(fq_, .5, fa_ * .6)) * (.9 + .14 * mix(fxLn(m_ / 3.1), .5, smoothstep(1., 3., length(fwidth(m_))))) * (.95 + .08 * fxLn(m_ / 37.));
        rk_ = smoothstep(${B.land.rock[0].toFixed(2)}, ${B.land.rock[1].toFixed(2)}, hs_ + .12 * (fxLn(m_ / 21.) - .5));
        vec3 rc_ = pow(${v3(B.land.rockC)}, vec3(2.2)) * mix(l1_, ${B.mean.toFixed(3)}, fd_ * .6) / ${B.mean.toFixed(3)};
        float sc_ = rk_ * smoothstep(.55, .7, fxLn(m_ / 4.3) * .7 + fxLn(m_ / 1.4) * .3);   // (scrub on the rock)
        ld_ = mix(ld_, rc_, rk_); ld_ = mix(ld_, pow(${v3(B.land.scrub)}, vec3(2.2)), sc_ * .8);${far ? `
        ld_ = pow(mix(${v3(B.land.olive)}, ${v3(B.land.ochre)}, .45 + .2 * (fxLn(m_ / 2600.) - .5)), vec3(2.2)) * (.96 + .05 * fxLn(m_ / 900.)); rk_ = 0.;   // (beyond the plate: the board calm, one land with a slow swell, no patches)` : ''}
        sl_ = ld_; slateN_ = normalize(mix(vec3(0., 0., 1.), slateN_, rk_)); slateR_ = mix(.95, slateR_, rk_); }   // (the photo's relief on the rock only: on open land its broad undulation read as cloud)` : ''}
      float tk_ = kt_ * (1. - smoothstep(.3, .6, uTodayK.z)); todayG_ = tk_;   // (today's city the subject: it stands on a honed slate, todayLight.board, matte with a little sheen; todayG_: its ground, for its own fill)${TL && TL.bank && !far ? `
      // today's embanked river (todayLight bank: { stone: the coping's colour, w: its width m, prom: the promenade's colour, pw: its
      // width m, line: the waterline's shade }): the land within pw of the water a promenade paved grey, within w a coping of light
      // stone, the water meeting it directly (the water map's own ramp a texel of some 7 m wide: these by the distance to the water)
      if (bkT_ > .01 && wMask < .99) { vec2 op_ = vec2(${(TL.bank.pw * scale).toExponential(4)}) / uPlateM, oc_ = vec2(${(TL.bank.w * scale).toExponential(4)}) / uPlateM, uv_ = vXZ / uPlateM + .5; float bp_ = 0., bc_ = 0.;
        for (int i = 0; i < 8; i++) { float a_ = float(i) * .7854; vec2 e_ = vec2(cos(a_), sin(a_)); bp_ = max(bp_, ${wAt('uv_ + op_ * e_')}); bc_ = max(bc_, ${wAt('uv_ + oc_ * e_')}); }
        float ci_ = smoothstep(.2, .6, tk_);   // (inside today's urban extent only: a village's or the country's banks stay as they are)
        bkP_ = ci_ * bkT_ * smoothstep(.35, .65, bp_) * (1. - wMask); bkC_ = ci_ * bkT_ * smoothstep(.35, .65, bc_) * (1. - wMask) * (1. - smoothstep(.5, 1., length(fwidth(m_)) / ${TL.bank.w.toFixed(2)})); }` : ''}   // (the coping gone as it shrinks under a pixel: no flickering line afar)
      float sv_ = .55 * smoothstep(.15, .38, yc4_.g) + .45 * smoothstep(.6, .85, yc4_.g);   // (a street here: the finer ones at half, the arterials whole)
      vec3 pl_ = pow(${v3(B.ground_in.col)}, vec3(2.2)) * (.96 + .05 * fxLn(m_ / 13.) + .03 * fxLn(m_ / 2.1)) * (1. - .28 * st_);   // (the plaster; today's streets fine lines a shade darker in it, the arterials wider and darker)${TL && TL.board ? `
      float rpI_ = 0., rpL_ = 0.;   // (inside a landmark's round plaza; its lawn ring)
      { vec3 bd_ = pow(${v3(TL.board)}, vec3(2.2)) * (.97 + .035 * fxLn(m_ / 1.1) + .02 * fxLn(m_ / 6.));   // today's board: a honed slate at its grey, its grain the material's own (no cleft, no cracks)${TL.pave ? `
        bd_ = mix(pow(${v3(TL.pave[0])}, vec3(2.2)) * (.98 + .03 * fxLn(m_ / 3.)), bd_, smoothstep(${TL.pave[1].toFixed(3)}, ${TL.pave[2].toFixed(3)}, yc4_.a));   // (todayLight pave: [its colour, the fabric's density from which the ground is asphalt, whole]: an open superblock's ground paved light)` : ''}${TL.lanes ? `
        bd_ = mix(bd_, pow(${v3(TL.lanes[0])}, vec3(2.2)) * (.97 + .04 * fxLn(m_ / 2.3)), smoothstep(${TL.lanes[1].toFixed(3)}, ${TL.lanes[2].toFixed(3)}, in_ * texture2D(uLanes, vXZ / uPlateM + .5).r));   // (todayLight lanes: [its colour, the low fabric's density from which, whole, the low fabric's height m]: inside a densely built block the ground between its buildings is lanes and courtyards in a warm mid grey under the roofs; the roads (streets mesh) and open plots stay as they are)` : ''}
        float pv_ = 1. - smoothstep(.45, .7, yc4_.r);   // (open ground off the blocks: a square, a plaza, a quay; paved pale as the streets, the parks over it)
        ${TL.plaza ? `${TL.paving ? `float pave_ = 1.; { vec2 t_ = m_ / ${f3(TL.paving[0])}, f_ = max(fwidth(m_), vec2(1e-4)), g_ = (fract(t_ + .5) - .5) * ${f3(TL.paving[0])}, q_ = smoothstep(.25, .5, f_ / ${f3(TL.paving[0])});   // (todayLight paving: [a slab m, its joint m, the joint's tone, the slabs' variation]: a square paved in large slabs, each its own shade, the joints a fine grid; each gone to its mean as a pixel outgrows it)
          vec2 j_ = mix(clamp((g_ + ${f3(TL.paving[1] / 2)}) / f_ + .5, 0., 1.) - clamp((g_ - ${f3(TL.paving[1] / 2)}) / f_ + .5, 0., 1.), vec2(${f3(TL.paving[1] / TL.paving[0])}), q_);
          pave_ = (1. + ${f3(TL.paving[3])} * 2. * (fxLh(floor(t_) + 17.) - .5) * (1. - max(q_.x, q_.y))) * (1. + ${f3(TL.paving[2])} * (1. - (1. - j_.x) * (1. - j_.y))); }
        ` : ''}bd_ = mix(bd_, pow(${v3(TL.plaza)}, vec3(2.2)) * (.98 + .03 * fxLn(m_ / 3.))${TL.paving ? ' * pave_' : ''}, .8 * pv_ * (1. - sv_));   // (a square, a quay: paved light)${TL.bank && !far ? `
        bd_ = mix(bd_, pow(${v3(TL.bank.prom)}, vec3(2.2)) * (.97 + .04 * fxLn(m_ / 4.)), bkP_);   // (the promenade along the river)` : ''}
        bd_ = mix(bd_, pow(${v3(TL.street[0])}, vec3(2.2)) * (.97 + .05 * fxLn(m_ / 5.)), ${TL.street[1].toFixed(2)} * sv_);   // (its streets by class)` : `bd_ = mix(bd_, pow(${v3(TL.street[0])}, vec3(2.2)) * (.97 + .05 * fxLn(m_ / 5.)), ${TL.street[1].toFixed(2)} * max(sv_, .8 * pv_));   // (its streets pale grooves, by class)`}
        ${TL.roundPlaza ? `for (int i = 0; i < 4; i++) { vec4 P_ = uRp[i], Q_ = uRq[i]; if (Q_.w < .5) continue;   // a landmark's round plaza (todayLight roundPlaza: [its paving, its inner disc's, the rings' spacing m, radial joints, a joint m, the joints' tone]): rings of paving
          float r_ = length(vXZ - P_.xy) / ${scale.toFixed(8)}; if (r_ > Q_.y + 10.) continue;   // round its lawn ring round a light inner disc, crisp at its edges, the joints each gone to its mean as a pixel outgrows it
          float f_ = max(fwidth(r_), 1e-4), o_ = clamp((Q_.y - r_) / f_ + .5, 0., 1.), d_ = clamp((Q_.x - r_) / f_ + .5, 0., 1.);
          float g_ = (fract(r_ / ${f3(TL.roundPlaza[2])} + .5) - .5) * ${f3(TL.roundPlaza[2])}, j_ = mix(clamp((g_ + ${f3(TL.roundPlaza[4] / 2)}) / f_ + .5, 0., 1.) - clamp((g_ - ${f3(TL.roundPlaza[4] / 2)}) / f_ + .5, 0., 1.), ${f3(TL.roundPlaza[4] / TL.roundPlaza[2])}, smoothstep(.25, .5, f_ / ${f3(TL.roundPlaza[2])}));
          vec2 v_ = (vXZ - P_.xy) / ${scale.toFixed(8)}; float a_ = atan(v_.y, v_.x) / 6.2832 * ${f3(TL.roundPlaza[3])}, fa_ = min(fwidth(a_), fwidth(fract(a_ + .5))) * 6.2832 * r_ / ${f3(TL.roundPlaza[3])}, ga_ = (fract(a_ + .5) - .5) * 6.2832 * r_ / ${f3(TL.roundPlaza[3])};
          float ja_ = mix(clamp((ga_ + ${f3(TL.roundPlaza[4] / 2)}) / fa_ + .5, 0., 1.) - clamp((ga_ - ${f3(TL.roundPlaza[4] / 2)}) / fa_ + .5, 0., 1.), 0., smoothstep(.25, .5, fa_ / max(6.2832 * r_ / ${f3(TL.roundPlaza[3])}, 1e-3))) * (1. - d_);   // (radial joints in the outer paving)
          float c_ = clamp((Q_.x * .55 + .3 - r_) / f_ + .5, 0., 1.) - clamp((Q_.x * .55 - .3 - r_) / f_ + .5, 0., 1.) + clamp((Q_.x * .2 - r_) / f_ + .5, 0., 1.) * .6;   // (the inner disc's ring line and its centre)
          vec3 pc_ = mix(pow(${v3(TL.roundPlaza[0])}, vec3(2.2)), pow(${v3(TL.roundPlaza[1])}, vec3(2.2)) * (1. + .08 * c_ * (1. - smoothstep(.3, 1., f_ / 2.))), d_) * (1. + ${f3(TL.roundPlaza[5])} * max(j_, ja_));
          bd_ = mix(bd_, pc_, o_); rpI_ = max(rpI_, o_); rpL_ = max(rpL_, clamp((r_ - P_.z) / f_ + .5, 0., 1.) * clamp((P_.w - r_) / f_ + .5, 0., 1.)); }
        ` : ''}float kb_ = (1. - smoothstep(.0, 1.5, abs(sv_ - .25) / max(fwidth(sv_), 1e-4))) * step(.02, sv_) * (1. - smoothstep(.35, .8, px_));   // (a kerb line along each street's edge, close)
        bd_ = mix(bd_, pow(${v3(TL.kerb)}, vec3(2.2)), .7 * kb_);
        pl_ = mix(pl_, bd_, tk_); }` : ''}
      float gr_ = uGreenOn * in_ * smoothstep(.35, .65, texture2D(uGreen, vXZ / uPlateM + .5).r);   // (the city's green space, from the data: pipeline/greens.py)
      float pk_ = uTodayK.y * (1. - smoothstep(.3, .6, uTodayK.z)) * smoothstep(.6, .75, yc4_.b) * step(.5, yt_) * step(yt_, yc_ + .5) * gr_ * (1. - wMask);   // (inside the urban extent: a park, a garden, a lawn, flat green; open land with no data stays plaster)
      ${TL && TL.board && TL.roundPlaza ? 'pk_ = mix(pk_, uTodayK.y * (1. - smoothstep(.3, .6, uTodayK.z)) * rpL_, rpI_);   // (a round plaza: its own lawn ring, crisp, in place of the data\'s)\n      ' : ''}kt_ *= 1. - pk_;   // (not while today's city is a backdrop behind a period city: uTodayK.z its dim)   // (inside the urban extent, off the blocks: the model's green)
      sl_ = mix(sl_, pl_, k_ * ${B.land ? '(1. - rk_ * (1. - smoothstep(.85, .97, tw_)))' : '1.'}); slateR_ = mix(slateR_, .9, k_); slateN_ = mix(slateN_, vec3(0., 0., 1.), k_ * ${B.land ? '(1. - rk_)' : '1.'});${TL && TL.board ? ' slateR_ = mix(slateR_, .8, tk_ * (1. - sv_));\n      ' : ''} ${TL && TL.park ? `${TL.lawn ? `float lawn_ = 1. + ${f3(TL.lawn[0])} * 2. * (fxLn(m_ / ${f3(TL.lawn[1])} + 3.3) - .5) * (1. - smoothstep(.3, .8, px_ / ${f3(TL.lawn[1])})) + ${f3(TL.lawn[2])} * 2. * (fxLn(m_ / ${f3(TL.lawn[3])} + 7.1) - .5) * (1. - smoothstep(.3, .8, px_ / ${f3(TL.lawn[3])}));   // (todayLight lawn: [its mottle's strength, size m, its mown grain's strength, size m, its border m, the border's tone]: a mown lawn, clumps and grain, each gone as a pixel outgrows it;
      { float g0_ = in_ * texture2D(uGreen, vXZ / uPlateM + .5).r, e_ = (g0_ - .5) / max(length(vec2(dFdx(g0_), dFdy(g0_))) / max(px_, 1e-4), 1e-5);   // a low border along its edge: e_ metres inside it)
        lawn_ *= 1. + ${f3(TL.lawn[5])} * (clamp((${f3(TL.lawn[4])} - e_) / px_ + .5, 0., 1.) - clamp(-e_ / px_ + .5, 0., 1.)) * (1. - smoothstep(${f3(TL.lawn[4])}, ${f3(TL.lawn[4] * 3)}, px_)); }
      ` : ''}sl_ = mix(sl_, pow(mix(${v3(TL.park[0])}, ${v3(TL.park[1])}, smoothstep(.3, .7, fxLn(m_ / 41.))), vec3(2.2)) * (.8 + .2 * fxLn(m_ / 23.) + .1 * fxLn(m_ / 6.))${TL.lawn ? ' * lawn_' : ''}, pk_); slateR_ = mix(slateR_, .95, pk_);   // (a park: lawn in two greens)` : B.ground_in.park ? `sl_ = mix(sl_, pow(${v3(B.ground_in.park)}, vec3(2.2)) * (.95 + .08 * fxLn(m_ / 29.)), pk_); slateR_ = mix(slateR_, .95, pk_);` : ''}${B.flock ? `
      { // trees: round crowns in groves (a crown a cell of ${B.flock.cell} m, there by the groves' density): where the generator's trees stand, on the banks, the slopes and the open ground at the city's edge
        float cl_ = smoothstep(.42, .56, fxLn(m_ / 52.) * .65 + mix(fxLn(m_ / 17.), .5, smoothstep(2., 5., px_)) * .35), tr_ = in_ * smoothstep(.12, .35, texture2D(uTrees, vXZ / uPlateM + .5).r);
        float bk_ = smoothstep(.01, .08, wr_) * (1. - smoothstep(.25, .4, wr_));   // (the banks: just off the water)
        float fl_ = max(tr_ * (.6 + .4 * cl_), cl_ * max(max(${B.flock.bank.toFixed(2)} * bk_, ${B.flock.slope.toFixed(2)} * smoothstep(.12, .3, hs_)), ${B.flock.edge.toFixed(2)} * smoothstep(.08, .25, tw_) * (1. - smoothstep(.72, .9, tw_))));
        fl_ = max(fl_, ${B.flock.land.toFixed(2)} * (1. - .75 * uTodayK.y * (1. - smoothstep(.3, .6, uTodayK.z))) * cl_ * (1. - smoothstep(.2, .4, tw_)));   // (a few groves in the country; round a modern city the plain is fields)
        fl_ *= (1. - smoothstep(.8, .92, tw_)) * (1. - wMask) * (1. - pk_);   // (a park of today's city: flat green, its trees not drawn as country groves)
        vec2 q_ = m_ / ${B.flock.cell.toFixed(1)}, ci_ = floor(q_), f_ = q_ - ci_ - .5; float h1_ = fract(sin(dot(ci_, vec2(12.99, 78.23))) * 43758.55), h2_ = fract(sin(dot(ci_, vec2(39.35, 11.13))) * 24634.63);
        vec2 o_ = f_ - (vec2(fract(h1_ * 7.31), fract(h2_ * 3.17)) - .5) * .34; float r_ = .36 + .16 * h2_, dd_ = length(o_) / r_, on_ = step(h1_, fl_);
        float sz_ = px_ / ${B.flock.cell.toFixed(1)};   // (cells a pixel: afar the crowns merge into their groves' tone)
        vec3 tg_ = pow(${v3(B.flock.col)}, vec3(2.2)) * (.8 + .4 * h2_);
        float crown_ = 0., shade_ = 0.;   // (the crowns are geometry: flockAt; the ground under the groves a little darker)
        sl_ *= 1. - .45 * shade_;   // (a crown's contact shadow round it)
        sl_ = mix(sl_, tg_, crown_); slateN_ = normalize(mix(slateN_, vec3(o_.x / r_ * .95, -o_.y / r_ * .95, sqrt(max(1. - dd_ * dd_, .05))), crown_)); slateR_ = mix(slateR_, .98, crown_);
        float far_ = uGeoT.z < 0. ? 0. : smoothstep(uGeoT.x, uGeoT.y, length(vFxW - cameraPosition));   // (where the crowns drawn as geometry fade by the eye's distance, flockAt: the groves' tone itself)
        vec3 gt_ = pow(mix(${v3(B.flock.col)}, ${v3(B.flock.col2 || B.flock.col)}, smoothstep(.3, .7, fxLn(m_ / 61.))), vec3(2.2)) * (.7 + .5 * mix(fxLn(m_ / 9.), .5, smoothstep(1.5, 4., px_))) * (.85 + .3 * mix(fxLn(m_ / 23.), .5, smoothstep(4., 10., px_)));   // (afar its grain calms: soft woods, not speckle)
        sl_ *= 1. - .3 * fl_ * (1. - far_); sl_ = mix(sl_, gt_, smoothstep(.2, .55, fl_) * far_ * .92); }` : ''} }` : ''}
    ${TL && TL.bank && !far ? `sl_ = mix(sl_, pow(${v3(TL.bank.stone)}, vec3(2.2)) * (.97 + .04 * fxLn(m_ / 3.)), bkC_); slateR_ = mix(slateR_, .85, bkC_);   // (the embankment's coping: a light stone line along the water)
    ` : ''}diffuseColor.rgb = mix(sl_, pow(${v3(B.resin)}, vec3(2.2)), wMask);${TL && TL.water ? `
    { float tw_ = ${TS_GLSL()};   // today's water (todayLight water): turquoise in the shallows along the banks, blue-green in the deep
      if (wMask > .01 && tw_ > 0.) { vec2 uv_ = vXZ / uPlateM + .5, o_ = vec2(${(TL.water.reach * scale).toExponential(4)}) / uPlateM; float s_ = 0.;
        for (int i = 0; i < 8; i++) { float a_ = float(i) * .7854; vec2 e_ = vec2(cos(a_), sin(a_)); s_ += ${wAt('uv_ + o_ * e_')} + ${wAt('uv_ + o_ * e_ * .45')}; }   // (the water round it: near a bank, less)
        vec3 wc_ = mix(pow(${v3(TL.water.shallow)}, vec3(2.2)), pow(${v3(TL.water.deep)}, vec3(2.2)), smoothstep(.6, .97, s_ / 16.)) * (.97 + .05 * fxLn(m_ / 70.));
        diffuseColor.rgb = mix(diffuseColor.rgb, wc_, wMask * tw_);${TL.bank && !far ? `
        diffuseColor.rgb *= 1. - ${f3(TL.bank.line)} * bkT_ * wMask * (1. - smoothstep(.5 + bkW_, .5 + 3.5 * bkW_, wr_));   // (the embankment wall's shade on the water along it)
` : ''} } }` : ''}
    diffuseColor.rgb *= mix(1., uPool.w, smoothstep(uPool.z * .35, uPool.z * 1.05, length(vXZ - uPool.xy)));   // (a light pool: the plate falls off into shadow away from the city, FILM_PIC pool)
  }`;
  if (B.slate) return `
  { float y_ = vFxW.y / ${scale.toFixed(6)} / ${B.step.toFixed(2)}, c_ = fract(y_), w_ = max(fwidth(y_), 1e-4);   // a slate plate, the land's rise in stacked sheets, its edges catching the light
    float vn_ = 1. - smoothstep(.0, .035, abs(fxLn(m_ / 23. + vec2(fxLn(m_ / 61.), 0.) * 1.6) - .5));   // (faint veins)
    vec3 sl_ = pow(${v3(B.slate)} * (.92 + .08 * fxLn(m_ / 1.3) + .05 * fxLn(m_ / 9.) + .04 * fxLn(m_ / 37.)) * (1. + .07 * vn_), vec3(2.2)) * (1. + .07 * min(floor(y_ - ${(20 / B.step).toFixed(2)}), 6.));
    sl_ *= mix(1., ${B.edge.toFixed(2)}, (1. - smoothstep(w_ * 1.5, w_ * 3., c_)) * step(w_, .3));
    diffuseColor.rgb = mix(sl_, pow(${v3(B.resin)}, vec3(2.2)), wMask); }`;
  return `
  { vec3 sd_ = pow(${v3(B.sand)} * (1. - ${B.grain.toFixed(2)} * .5 + ${B.grain.toFixed(2)} * fxLn(m_ / .7)) * (.94 + .08 * fxLn(m_ / 9.)), vec3(2.2));   // a sandy ground, its grain
    diffuseColor.rgb = mix(sd_, pow(${v3(B.water)}, vec3(2.2)), wMask); }`;
}
// a detailed model's part in a material's colours (MAT.glbC, by its material role): k its height's exaggeration (a storey's lines at
// its true height times k)
function glbMaterial(nm, k = 1, scale = 1e-4, col = null) {   // (col: the glb entry's own colour for this part or role, else the material's)
  const GF_ = todayL() && todayL().facade && todayL().facade.glass, v3 = c => `vec3(${c.map(x => (+x).toFixed(3)).join(', ')})`;
  const glass = nm === 'glass', m = new THREE.MeshStandardMaterial({ color: col || MAT.glbC[nm] || MAT.glbC.stone, roughness: glass ? .3 : nm === 'metal' ? .5 : .85, metalness: 0, side: THREE.DoubleSide });
  if (!glass && nm !== 'stone') return m;
  m.onBeforeCompile = sh => { sh.uniforms.uGlassSky = GLASS_SKY; sh.uniforms.uGlassK = GLASS_K;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vGW, vGN;').replace('#include <fog_vertex>', '#include <fog_vertex>\n vGW = (modelMatrix * vec4(transformed, 1.)).xyz; vGN = normalize(mat3(modelMatrix) * objectNormal);');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vGW, vGN; uniform vec3 uGlassSky; uniform float uGlassK;').replace('#include <color_fragment>', `#include <color_fragment>
  { vec3 n_ = normalize(vGN); float pxm_ = length(fwidth(vGW)) / ${scale.toExponential(4)};   // (metres a pixel)
    if (abs(n_.y) < .5) { float ym_ = vGW.y / ${scale.toExponential(4)} / ${k.toFixed(3)}, fy_ = fract(ym_ / 4.2), kS_ = 1. - smoothstep(.22, .45, pxm_ / 4.2);
      vec2 t_ = normalize(vec2(-n_.z, n_.x) + 1e-6); float fu_ = abs(fract(dot(vGW.xz, t_) / ${scale.toExponential(4)} / 1.5) - .5) * 2., kM_ = 1. - smoothstep(.22, .45, pxm_ / 1.5);
      float fl_ = mix(.08, 1. - smoothstep(.05, .1, fy_), kS_), ml_ = mix(.1, smoothstep(.86, .94, fu_), kM_);   // (afar: their shares of the wall)${glass && GF_ ? `
      diffuseColor.rgb = mix(diffuseColor.rgb * mix(vec3(1.), ${v3(GF_.deep || [1, 1, 1])}, max(kM_, kS_)), pow(${v3(GF_.pale)}, vec3(2.2)), ${(GF_.mull).toFixed(3)} * max(ml_, .6 * fl_));   // (todayLight facade glass: pale mullions over deeper panes, as today's towers)` : `
      diffuseColor.rgb *= 1. - ${glass ? '.45 * max(ml_, fl_)' : '.12 * fl_'};`}${glass ? `
      float fr_ = pow(1. - max(dot(n_, normalize(cameraPosition - vGW)), 0.), 3.); diffuseColor.rgb = mix(diffuseColor.rgb, uGlassSky, min(1., uGlassK * (.1 + .45 * fr_)));   // (the sky in the glass, more as the view grazes)
` : ''} } }`); };
  m.customProgramCacheKey = () => 'mini-glb ' + nm + k.toFixed(3) + scale + (GF_ ? ' pale' : '');
  return m;
}
// a convex hull of points [x, z] (monotone chain, counter-clockwise), and a point's signed distance inside it (negative: outside)
// today's street network, for its markings (todayLight streets marks): R the ways ([{ pts, w: the carriageway's width m, link: a
// ramp }]). Where three or more ways meet (a vertex they share) a junction: each way's markings and kerbs stop short of it by the
// widest other way's half-width and pavement (and mk.clear more), and its crossing (zebra) is painted there when the other way is
// marked too (a ramp is not). Where two ways cross without a shared vertex (one over the other) the narrower stops short of the
// wider, which keeps its paint, and no crossing is painted. Beside a parallel way whose carriageway overlaps its own (a dual
// carriageway mapped as two one-way ways, a road over a road) a way keeps its own side up to the median midway between their
// centre lines; the narrower of two on one line unmarked
function streetNet(R0, kerb, mk, scale) {   // -> { R: the ways with their crossings as vertices, at(i): the way's along metres at each vertex and its junctions [vertex, along, clearance m, zebra], clip(i, x, z, ux, uz): [left, right] m kept (-1: unmarked) }
  const GC = 60 * scale, grid = (RR, ok) => { const G = new Map(); RR.forEach((r, i) => { if (!ok(r)) return; for (let k = 1; k < r.pts.length; k++) { const [ax, az] = r.pts[k - 1], [bx, bz] = r.pts[k];   // (the ways' segments in a 60 m grid)
    for (let gx = Math.floor(Math.min(ax, bx) / GC); gx <= Math.floor(Math.max(ax, bx) / GC); gx++) for (let gz = Math.floor(Math.min(az, bz) / GC); gz <= Math.floor(Math.max(az, bz) / GC); gz++) { const kk = gx * 100003 + gz; (G.get(kk) || G.set(kk, Object.assign([], { gx, gz })).get(kk)).push([i, ax, az, bx, bz, r.w, k]); } } }); return G; };
  const marked = r => r.w >= mk.minW && !r.link;
  // the crossings without a shared vertex, each made a vertex of both ways
  const G0 = grid(R0, () => true), ins = R0.map(() => []), X = new Set();
  for (const L_ of G0.values()) for (let a = 0; a < L_.length; a++) for (let b = a + 1; b < L_.length; b++) { const [i, ax, az, bx, bz, , k] = L_[a], [j, cx, cz, dx, dz, , k2] = L_[b]; if (i === j) continue;
    const rx = bx - ax, rz = bz - az, sx = dx - cx, sz = dz - cz, dn = rx * sz - rz * sx, lr = Math.hypot(rx, rz), ls = Math.hypot(sx, sz); if (Math.abs(dn) < .2 * lr * ls) continue;   // (alongside, or nearly: the parallel ways' clip)
    const t = ((cx - ax) * sz - (cz - az) * sx) / dn, u = ((cx - ax) * rz - (cz - az) * rx) / dn; if (t <= 1e-3 || t >= 1 - 1e-3 || u <= 1e-3 || u >= 1 - 1e-3) continue;
    const x = ax + t * rx, z = az + t * rz; if (Math.floor(x / GC) !== L_.gx || Math.floor(z / GC) !== L_.gz) continue;   // (each crossing once: in the cell it lies in)
    ins[i].push([k, t, x, z]); ins[j].push([k2, u, x, z]); X.add(x + ',' + z); }
  const R = R0.map((r, i) => { if (!ins[i].length) return r; const I = ins[i].sort((p, q) => p[0] - q[0] || p[1] - q[1]), pts = [r.pts[0]]; let n = 0;
    for (let k = 1; k < r.pts.length; k++) { while (n < I.length && I[n][0] === k) { pts.push([I[n][2], I[n][3]]); n++; } pts.push(r.pts[k]); }
    return { ...r, pts }; });
  const key = p => p[0] + ',' + p[1], N = new Map();
  R.forEach((r, i) => r.pts.forEach((p, k) => { const kk = key(p); let n = N.get(kk); if (!n) N.set(kk, n = { d: 0, a: 0, ai: -1, aw: 0, am: 0, b: 0, bw: 0, bm: 0 });
    n.d += k === 0 || k === r.pts.length - 1 ? 1 : 2; const h = r.w / 2 + kerb, m = marked(r) ? 1 : 0;   // (the ways at a node, a way through it twice; the two widest pavements, a different way each)
    if (i === n.ai) return; if (h > n.a) { n.b = n.a; n.bw = n.aw; n.bm = n.am; n.a = h; n.ai = i; n.aw = r.w; n.am = m; } else if (h > n.b) { n.b = h; n.bw = r.w; n.bm = m; } }));
  const G = grid(R, marked);   // (the marked ways: the parallel ones' clip)
  const clip = (i, x, z, ux, uz) => { const hw = R[i].w / 2, gx = Math.floor(x / GC), gz = Math.floor(z / GC); let cl = 1e4, cr = 1e4;
    for (let a = gx - 1; a <= gx + 1; a++) for (let b = gz - 1; b <= gz + 1; b++) for (const [j, ax, az, bx, bz, w2] of G.get(a * 100003 + b) || []) { if (j === i) continue;
      const vx = bx - ax, vz = bz - az, l2 = vx * vx + vz * vz; if (l2 < 1e-18 || Math.abs(ux * vx + uz * vz) < .9 * Math.sqrt(l2)) continue;   // (not alongside: a crossing)
      const t = ((x - ax) * vx + (z - az) * vz) / l2; if (t < 0 || t > 1) continue;
      const qx = ax + t * vx - x, qz = az + t * vz - z, sd = (qz * ux - qx * uz) / scale;   // (its centre line's offset, + to the right)
      if (Math.abs(sd) >= hw + w2 / 2) continue;   // (the carriageways apart)
      if (Math.abs(sd) < Math.min(hw, w2 / 2)) { if (hw * 2 < w2 || (hw * 2 === w2 && i > j)) return [-1, -1]; continue; }   // (one over the other: the wider one's markings)
      if (sd > 0) cr = Math.min(cr, sd / 2); else cl = Math.min(cl, -sd / 2); }
    return [cl, cr]; };
  const at = i => { const p = R[i].pts, s = [0]; for (let k = 1; k < p.length; k++) s.push(s[k - 1] + Math.hypot(p[k][0] - p[k - 1][0], p[k][1] - p[k - 1][1]) / scale);
    const J = []; p.forEach((q, k) => { const kk = key(q), n = N.get(kk); if (!n || n.d < 3) return; const o = n.ai === i, c = o ? n.b : n.a, w = o ? n.bw : n.aw, m = o ? n.bm : n.am, x = X.has(kk);
      if (c > 0 && !(x && R[i].w > w)) J.push([k, s[k], c + mk.clear, !x && marked(R[i]) && m ? 1 : 0]); });   // (over a narrower way: the wider keeps its paint)
    return { s, J }; };
  return { R, at, clip };
}
function hull2(P) { const p = P.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]), lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (let i = p.length - 1; i >= 0; i--) { const q = p[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  lo.pop(); up.pop(); return lo.concat(up); }
function hullIn(H, x, z) { let m = Infinity; for (let k = 0; k < H.length; k++) { const [ax, az] = H[k], [bx, bz] = H[(k + 1) % H.length], l = Math.hypot(bx - ax, bz - az) || 1; m = Math.min(m, ((bx - ax) * (z - az) - (bz - az) * (x - ax)) / l); } return m; }
// today's buildings as a model maker paints and engraves them (a material's): each in its paint (colourToday kinds, the vertex
// colour) with the facade of its kind (vKind): an office tower a curtain wall of tinted glass, a fine mullion every 1.5 m and a floor
// line each storey, the sky in it as the view grazes; a home from 18 m a balcony band each floor, its windows set back; the low
// fabric and a large low building small windows; the old fabric's roofs in rows of grey tile. Storeys at their true height (times
// the model's own exaggeration, so the count stays right). Every line fades by its size in pixels into the wall's own colour, a
// shade of it (afar a facade is its paint, evenly: no grime, no speckle, no moire)
function FACADE_GLSL(S) {
  const EX = (S.U.uScaleH ? S.U.uScaleH.value / S.U.uScaleM.value : 3).toFixed(3), F_ = todayL() && todayL().facade, f = v => (+v).toFixed(3), v3 = c => `vec3(${c.map(f).join(', ')})`;
  // todayLight walls: [a wall's grain's strength, its size m, its courses' spacing m, their seam's shade]: a model's painted board,
  // a faint grain and fine horizontal seams, close only; roof: [a flat roof's mottle, its size m, its membrane's rolls m, their
  // seam's shade, the parapet's top (times)]: a membrane in rolls, its parapet's top lighter; glassSky: [its strength, low, high
  // (sRGB)]: a tower's glass the sky's gradient, paler low, bluer high. Each by pixels, gone to its mean as a pixel outgrows it
  const WM_ = todayL() && todayL().walls, RM_ = todayL() && todayL().roof, GS_ = todayL() && todayL().glassSky, KO_ = kindsOn(), TL_ = KO_ && MAT.today.roofKinds.pitch && MAT.today.roofKinds.pitch.tiles;   // (KO_: the roof kinds on, todayLight roofKinds)
  // todayLight facade: a facade's architecture, crisp close and simpler with distance, never speckle: base [the ground floor's
  // height m, its tone (times), from which height m]: a taller storey in a greyer, darker stone, its openings wide; cap [its
  // height m, its light (times), the shadow line under it (times), its least height in fwidth's metres]: a parapet's coping
  // along the wall's top, a bright band at mid range; piers [fewest, most windows a group, the pier's width m]: the windows in
  // groups between wider piers; rows [their fade, from and gone, in fwidth's metres a storey]; mid [the columns' fade, from and gone, in fwidth's metres a column; the coarser strips' the
  // same, in fwidth's metres two columns; a column strip's strength, a coarser strip's]: past the grid's rows the columns as
  // continuous vertical strips, then a strip every two columns, then the plain wall; reveal [the sill's light, the head's shade (times)]: each window's sill catching the
  // sun, its head in the lintel's shadow; glass {pale: the mullions' and spandrels' silver (sRGB), mull: their share, span: [a
  // spandrel's share of a storey, its strength], top: the glass this much lighter toward the top, px: a coarse mullion at least
  // this many of fwidth's metres wide, coarse: the coarse mullions' spacing m, deep: the panes between them (times)}; brick
  // [the paint's saturation from which, whole, the windows' contrast kept]: a salmon or brick wall's windows quieter (else red
  // with white dots)
  const wallTop = F_ ? `float top_ = (vTop > vBase + 1e-7 ? (vTop - vBase) / uScaleM / ${EX} : hm_) * uHScaleT * max(vUp, .001), dt_ = top_ - ym_;   // (the wall's top in these metres, as drawn: its record's own top (aTop), times today's own height scale and its rise)` : '';
  const tower = F_ ? `
          ${wallTop}
          float tf_ = clamp(ym_ / max(top_, 1.), 0., 1.), sp_ = (1. - smoothstep(${f(F_.glass.span[0] - .03)}, ${f(F_.glass.span[0] + .03)}, fy_)) * kS_;   // (a spandrel band each storey)
          c_ *= mix(1., ${f(F_.glass.top)}, smoothstep(.25, 1., tf_));   // (lighter toward the top, as the sky in it)${GS_ ? `
          if (show_ > .01) c_ = mix(c_, pow(mix(${v3(GS_[1])}, ${v3(GS_[2])}, smoothstep(0., 1., tf_)), vec3(2.2)) * dot(c_, vec3(.2126, .7152, .0722)) / dot(pow(mix(${v3(GS_[1])}, ${v3(GS_[2])}, smoothstep(0., 1., tf_)), vec3(2.2)), vec3(.2126, .7152, .0722)), ${f(GS_[0])});   // (todayLight glassSky: the sky's gradient in it, its light kept)` : ''}
          c_ *= mix(vec3(1.), ${v3(F_.glass.deep || [1, 1, 1])}, min(1., kM_ + kM2_) * (1. - ml_));   // (the panes a deeper blue between the pale mullions, where the mullions read)
          c_ = mix(c_, pow(${v3(F_.glass.pale)}, vec3(2.2)), max(${f(F_.glass.mull)} * ml_, ${f(F_.glass.span[1])} * max(sp_, (1. - smoothstep(.1, .18, fy2_)) * kS2_)));   // (pale silver mullions and spandrels)
          glass_ = (1. - max(ml_, sp_)) * show_; eng_ = 0.;` : `
          c_ = mix(c_, pt_ * .62, .55 * ln_); glass_ = (1. - ln_) * show_; eng_ = 0.;`;
  // the walls (a home, the low fabric, a large low building, stone): the window rows with the facade's architecture
  const wall = (rows, cols, home) => F_ ? `
          ${wallTop}
          float bH_ = hm_ >= ${f(F_.base[2])} ? ${f(F_.base[0])} : 0., inB_ = (1. - smoothstep(bH_ - .12, bH_ + .12, ym_)) * step(.5, bH_), yu_ = ym_ - bH_, fyU_ = fract(yu_ / sh_);
          float hb_ = fract(sin(dot(aCtrV, vec2(127.1e3, 311.7e3))) * 43758.5453), G_ = floor(mix(${f(F_.piers[0])}, ${f(F_.piers[1] + .999)}, hb_)), gP_ = G_ * wu_ + ${f(F_.piers[2])}, pp_ = mod(um_, gP_);
          // the ramp, near to far: the window grid (rows: kR_, by pixels a storey), then the window columns in their groups as
          // continuous vertical strips (kC_, by pixels a column), then a strip every two columns (kD_, by pixels two columns: one
          // octave coarser, fixed on the wall, so it never crawls), then the plain wall (long lines stay clean where dots speckle)
          float kR_ = pow(1. - smoothstep(${f(F_.rows[0])}, ${f(F_.rows[1])}, pxm_ / sh_), 1.5), kC_ = pow(1. - smoothstep(${f(F_.mid[0])}, ${f(F_.mid[1])}, pxm_ / wu_), 1.5), kD_ = (1. - kC_) * pow(1. - smoothstep(${f(F_.mid[2])}, ${f(F_.mid[3])}, pxm_ / (2. * wu_)), 1.5), kG_ = max(kC_, kD_);
          float cH_ = max(${f(F_.cap[0])}, ${f(F_.cap[3])} * pxm_);   // (the coping: its own height close, at least about a pixel and a half afar: a bright band along the top at mid range)
          float aw_ = .5 * pxm_;   // (a pier's edge softened over half a pixel: no stair-stepping in the strips)
          float fq_ = fract((pp_ - ${f(F_.piers[2])}) / wu_), pier_ = smoothstep(${f(F_.piers[2])} - aw_, ${f(F_.piers[2])} + aw_, pp_) * (1. - smoothstep(gP_ - aw_, gP_, pp_)), bay_ = smoothstep(-.1, .1, yu_) * smoothstep(cH_ + .5, cH_ + .9, dt_);   // (no window on a pier, in the base or under the coping)
          float fD_ = fract(um_ / (2. * wu_)), a2_ = .5 * pxm_ / (2. * wu_), wd_ = smoothstep(.2 - a2_, .2 + a2_, fD_) * (1. - smoothstep(.8 - a2_, .8 + a2_, fD_));   // (the coarser strips: 60 % of each pair of columns, edges softened over half a pixel)
          float sat_ = (max(pt_.r, max(pt_.g, pt_.b)) - min(pt_.r, min(pt_.g, pt_.b))) / max(max(pt_.r, max(pt_.g, pt_.b)), 1e-3), wk_ = mix(1., ${f(F_.brick[2])}, smoothstep(${f(F_.brick[0])}, ${f(F_.brick[1])}, sat_));
          float wc_ = smoothstep(${f(cols[0])}, ${f(cols[0] + .04)}, fq_) * (1. - smoothstep(${f(cols[1])}, ${f(cols[1] + .04)}, fq_)), wr_ = smoothstep(${f(rows[0])}, ${f(rows[0] + .04)}, fyU_) * (1. - smoothstep(${f(rows[1])}, ${f(rows[1] + .04)}, fyU_));
          float win_ = mix(${f(F_.mid[4])}, wr_, kR_) * (wc_ * pier_ * kC_ + ${f(F_.mid[5])} * wd_ * kD_) * bay_, head_ = wr_ * wc_ * pier_ * bay_ * kR_ * kC_ * smoothstep(${f(rows[1] - .14)}, ${f(rows[1] - .06)}, fyU_);   // (its head in the lintel's shadow)
          float sill_ = wc_ * pier_ * bay_ * kR_ * kC_ * smoothstep(${f(rows[0] - .07)}, ${f(rows[0] - .04)}, fyU_) * (1. - smoothstep(${f(rows[0] - .01)}, ${f(rows[0] + .02)}, fyU_));   // (a lit sill under it)
          ${home ? `float band_ = (1. - smoothstep(.12, .2, fyU_)) * kS_ * kR_ * smoothstep(-.1, .1, yu_) * smoothstep(cH_, cH_ + .3, dt_);   // (a balcony band each floor, a shade lighter)
          ` : 'float band_ = 0.; '}vec3 wg_ = mix(pt_ * .5, vec3(.30, .35, .44), .45);   // (a window: cool glass set into the paint, no darker than the wall's own shade side)
          c_ = pt_ * (1. + .08 * band_ + (${f(F_.reveal[0])} - 1.) * sill_);
          c_ = mix(c_, wg_ * mix(1., ${f(F_.reveal[1])}, head_), ${home ? '.9' : '.88'} * wk_ * win_ * (1. - band_));
          { vec3 st_ = mix(pt_, vec3(dot(pt_, vec3(.2126, .7152, .0722))), .4) * ${f(F_.base[1])}; float fs_ = fract(um_ / 6.);   // (the base: stone, greyer and darker; shop fronts wide and dark)
            float op_ = smoothstep(.12, .16, fs_) * (1. - smoothstep(.84, .88, fs_)) * smoothstep(.35, .5, ym_) * (1. - smoothstep(bH_ - 1.1, bH_ - .9, ym_));
            c_ = mix(c_, mix(st_, wg_ * .9, .85 * wk_ * op_ * kR_), inB_ * pow(1. - smoothstep(KW0_, KW1_, pxm_ / max(bH_, 1.)), 1.5)); }   // (the base on its own ramp, by its height: a band, never speckle; its openings on the windows')
          { float cap_ = (1. - smoothstep(cH_ - .06, cH_ + .06, dt_)) * smoothstep(-.3, 0., dt_) * kG_, ln_ = smoothstep(cH_ - .02, cH_ + .06, dt_) * (1. - smoothstep(cH_ + .22, cH_ + .34, dt_)) * kR_;   // (the coping, a shadow line under it close)
            c_ *= mix(1., ${f(F_.cap[1])}, cap_) * mix(1., ${f(F_.cap[2])}, ln_); }
          c_ *= 1. - ${home ? '.04' : '.03'} * (1. - kG_); eng_ = ${home ? '.35' : '.3'} * win_ * wk_ * (1. - band_) * show_;` : home ? `
          float band_ = (1. - smoothstep(.12, .2, fy_)) * kS_, win_ = smoothstep(.30, .34, fy_) * (1. - smoothstep(.84, .88, fy_)) * smoothstep(.10, .14, fu_) * (1. - smoothstep(.78, .82, fu_)) * kW_;
          c_ = mix(pt_ * (1. + .08 * band_), mix(pt_ * .5, vec3(.30, .35, .44), .45), .9 * win_ * (1. - band_)) * (1. - .04 * (1. - kW_)); eng_ = .35 * win_ * (1. - band_) * show_;   // (a window no darker than the wall's own shade side)   // (its windows cool glass set into the paint; afar the paint a shade deeper, their share)` : `
          float win_ = smoothstep(.36, .40, fy_) * (1. - smoothstep(.76, .80, fy_)) * smoothstep(.30, .34, fu_) * (1. - smoothstep(.64, .68, fu_)) * kW_;
          c_ = mix(pt_, mix(pt_ * .5, vec3(.30, .35, .44), .45), .88 * win_) * (1. - .03 * (1. - kW_)); eng_ = .3 * win_ * show_;`;
  return `
  { vec3 n_ = normalize(vWN); float hm_ = vData.y, kd_ = floor(vKind + .5), KW0_ = ${((todayL() && todayL().winFade) || [.125, .5])[0].toFixed(3)}, KW1_ = ${((todayL() && todayL().winFade) || [.125, .5])[1].toFixed(3)};   // (todayLight winFade: the windows' contrast ramp, in fwidth's metres a pixel over a storey)
    if (vData.w < .5 && hm_ > 2.5) {
      float pxm_ = length(fwidth(vWP)) / uScaleM, show_ = 1. - vMute;   // (metres a pixel; none on today's plan behind a period city)
      vec3 pt_ = diffuseColor.rgb;   // (its paint)
      bool tower_ = abs(kd_ - 2.) < .5, res_ = (abs(kd_ - 1.) < .5 || abs(kd_ - 4.) < .5) && hm_ >= 18.;
      if (abs(n_.y) < .3 && kd_ < 4.5) {   // (a wall; a pitched roof's gable end (kind 5) plain)
        float ym_ = (vWP.y - vBase) / uScaleM / ${EX}; vec2 t_ = normalize(vec2(-n_.z, n_.x) + 1e-6); float um_ = dot(vWP.xz, t_) / uScaleM;
        float sh_ = tower_ ? 4. : 3.;   // (a storey)
        float fy_ = fract(ym_ / sh_), kS_ = 1. - smoothstep(.3, .55, pxm_ / sh_);
        vec3 c_ = pt_;
        if (tower_) {   // tinted glass in a grid of mullions and floor lines: fine close (every 2 m, each storey), coarser as it shrinks
          // (every 6 m, every second storey), so the grid reads as far as a curtain wall's does
          float mu_ = 2., fu_ = abs(fract(um_ / mu_) - .5) * 2., kM_ = 1. - smoothstep(.3, .55, pxm_ / mu_);
          float GC_ = ${F_ && F_.glass.coarse ? f(F_.glass.coarse) : '6.'}, fu2_ = abs(fract(um_ / GC_) - .5) * 2., kM2_ = (1. - kM_) * (1. - smoothstep(.3, .55, pxm_ / GC_)), fy2_ = fract(ym_ / 8.), kS2_ = (1. - kS_) * (1. - smoothstep(.3, .55, pxm_ / 8.));
          float mw2_ = ${F_ ? `max(.1, ${f(F_.glass.px || 0)} * pxm_ / GC_)` : '.1'};   // (todayLight facade glass px: the coarse mullion at least this many of fwidth's metres wide, so it reads at mid range)
          float ml_ = max(smoothstep(.84, .92, fu_) * kM_, smoothstep(1. - 2. * mw2_, 1. - mw2_, fu2_) * kM2_), fl_ = max((1. - smoothstep(.08, .14, fy_)) * kS_, (1. - smoothstep(.1, .18, fy2_)) * kS2_), ln_ = max(ml_, fl_);   // (afar: none, the glass's own tone)
          vec3 v_ = normalize(cameraPosition - vWP); float fr_ = pow(1. - max(dot(n_, v_), 0.), 3.);
          c_ = mix(pt_, uGlassSky, min(1., uGlassK * (.12 + .5 * fr_)));   // (the sky in it, more as the view grazes)${tower}
        } else if (res_) {   // a home: a balcony band at each floor, a shade lighter; its windows set back, a shade darker
          float wu_ = 3., fu_ = fract(um_ / wu_), kW_ = pow(1. - smoothstep(KW0_, KW1_, max(pxm_ / sh_, pxm_ / wu_)), 1.5);   // (a contrast ramp: pxm_ from fwidth's length runs about 1.5 times a pixel, so whole from some 12 picture pixels a storey, about 40 % at 5, none by 3: window rows close, a quiet wall afar, never a speckle)${wall([.30, .84], [.10, .78], true)}
        } else {   // the low fabric, a large low building: small windows
          float wu_ = 3., fu_ = fract(um_ / wu_), kW_ = pow(1. - smoothstep(KW0_, KW1_, max(pxm_ / sh_, pxm_ / wu_)), 1.5);${wall([.36, .76], [.30, .64], false)}
        }
        ${WM_ ? `if (!tower_ && show_ > .01) { c_ *= 1. + ${f(WM_[0])} * 2. * (mtN(vec2(um_, ym_ * ${EX}) / ${f(WM_[1])}) - .5) * (1. - smoothstep(.3, 1., pxm_ / ${f(WM_[1])}));   // (todayLight walls: its grain)
          float sy_ = (fract(ym_ / ${f(WM_[2])} + .5) - .5) * ${f(WM_[2])}, fy0_ = max(fwidth(ym_), 1e-4);   // (its courses' seams, box-filtered, their mean afar)
          c_ *= 1. - ${f(WM_[3])} * mix(clamp((sy_ + .04) / fy0_ + .5, 0., 1.) - clamp((sy_ - .04) / fy0_ + .5, 0., 1.), ${f(.08 / WM_[2])}, smoothstep(.25, .5, fy0_ / ${f(WM_[2])})); }
        ` : ''}diffuseColor.rgb = mix(diffuseColor.rgb, c_, show_);${RM_ ? `
      } else if (n_.y > .9 && ${KO_ ? 'kd_ < 4.5' : 'kd_ > .5'} && show_ > .01) {   // a flat roof's membrane (the old fabric's too with the roof kinds on) (todayLight roof; none on today's plan behind a period city: nothing to see, nothing to pay): mottled, in rolls along one of the building's axes
        vec2 m_ = vWP.xz / uScaleM, rd_ = fract(sin(dot(aCtrV, vec2(127.1e3, 311.7e3))) * 43758.5453) < .5 ? vec2(1., 0.) : vec2(0., 1.); float v_ = dot(m_, rd_), fv_ = max(fwidth(v_), 1e-4), g_ = (fract(v_ / ${f(RM_[2])} + .5) - .5) * ${f(RM_[2])};
        float mo_ = 1. + ${f(RM_[0])} * 2. * (mtN(m_ / ${f(RM_[1])} + 5.3) - .5) * (1. - smoothstep(.3, 1., pxm_ / ${f(RM_[1])}));
        float sm_ = mix(clamp((g_ + .05) / fv_ + .5, 0., 1.) - clamp((g_ - .05) / fv_ + .5, 0., 1.), ${f(.1 / RM_[2])}, smoothstep(.25, .5, fv_ / ${f(RM_[2])}));
        diffuseColor.rgb *= mix(1., mo_ * (1. - ${f(RM_[3])} * sm_), show_);` : ''}
      }${KO_ ? '' : ` else if (n_.y > .9 && kd_ < .5) {   // the old fabric's roof (the roof kinds off): grey tile in rows, close
        float px_ = pxm_ / 1.2, r_ = abs(fract(dot(vWP.xz, normalize(vec2(1., .2))) / uScaleM / 1.2) - .5) * 2.;
        diffuseColor.rgb *= 1. - show_ * (.14 * smoothstep(.6, .95, r_) * (1. - smoothstep(.3, .6, px_)) + .025 * smoothstep(.3, .6, px_));   // (afar: their share)
      }`}${TL_ ? `
      if (kd_ > 4.5 && n_.y > .3 && n_.y < .99 && show_ > .01) {   // a pitched roof's tiles (roofKinds pitch tiles): courses along its eaves, lines of one height on the slope, box-filtered, their mean afar
        float t_ = (vWP.y - vBase) / uScaleM / ${EX} / (${f(TL_[0])} * sqrt(max(1. - n_.y * n_.y, 1e-4))), ft_ = max(fwidth(t_), 1e-4), g_ = fract(t_ + .5) - .5;
        float ln_ = mix(clamp((g_ + .1) / ft_ + .5, 0., 1.) - clamp((g_ - .1) / ft_ + .5, 0., 1.), .2, smoothstep(${f(TL_[2])}, ${f(2 * TL_[2])}, ft_));
        diffuseColor.rgb *= 1. - show_ * ${f(TL_[1])} * ln_;
      }` : ''}
    } }`;
}
function filmMaterial(S, mat, u, ruin, fadeAt, fire = null, back = null, surf = false, skip = false) {   // (surf: a model's surfaces, the film's picture: FILM_PIC; skip: today's city, its buildings marked aSkip hidden: a replacement footprint stands in their place, todayFootprints)
  S.deformMaterial(mat, u); const deform = mat.onBeforeCompile, nL = u ? u.uLossBurn.value.length : 0, H = S.slots, depth = !!mat.isMeshDepthMaterial, E = S.marksN();
  const hm = `vec2 huv_ = aCtr / uPlateV + .5; vec4 h1_ = texture2D(uHide, huv_), h2_ = texture2D(uHide2, huv_)${S.slots3 ? ', h3_ = texture2D(uHide3, huv_)' : ''};
     float hm_[${H}]; hm_[0] = h1_.r; hm_[1] = h1_.g; hm_[2] = h1_.b; hm_[3] = h1_.a; hm_[4] = h2_.r; hm_[5] = h2_.g; hm_[6] = h2_.b; hm_[7] = h2_.a;${S.slots3 ? ' hm_[8] = h3_.r; hm_[9] = h3_.g; hm_[10] = h3_.b; hm_[11] = h3_.a;' : ''}`;
  const dim = 'clamp(max(mix(uDimToday0, uDimToday, smoothstep(uNodeR + .004, uNodeR - .025, length(aCtr - uNodeC))), uDimTodayC) / uFadeAt, 0., 1.)';   // (uDimTodayC: main.js, the colour film's, past the lights too)
  const vert = u ? `
   if (aData.w > 2.5) { float ry; ${S.eraRy('aData.z', 'aData.w')}
     float up_ = smoothstep(st, st + uEraGrow, uEraT), clr_ = ${MODERN_GLSL};   // (risen; cleared: the modern section, or a later city risen here)
     ${hm}
     for (int i = 0; i < ${H}; i++) if (uRuinLater[i] > .5 && hm_[i] > .02) { float r_ = (hm_[i] - .04) / .96, g_ = uHideG[i]; clr_ = max(clr_, smoothstep(r_ - g_ * .7, r_ + g_ * .15, uRuinT[i])); }
     if (aData.w > 3.5) { float bt_ = 0.; for (int k = 0; k < ${Math.max(nL, 1)}; k++) if (abs(aData.w - 4. - float(k)) < .5) bt_ = uLossBurntV[k]; if (bt_ < .5) clr_ = 1.; }   // (a part a city loses in its own course goes whole, as a model's piece lifted off; one a fire took leaves its charred footing, as a whole city taken back does)
     float hh_ = tr0_.y - aBase, fd_ = min(hh_, uRuinH) * up_ * (1. - clr_);
     vRuin = up_ * (1. - clr_) * (1. - max(ry, 0.));
     if (fd_ > hh_ * max(ry, 0.) && fd_ > 1e-7) transformed.y = aBase + fd_;
     if (uHScale < .999 && transformed.y > aBase) transformed.y = aY0 > -1e8 ? transformed.y + (uHScale - 1.) * max(aY0 - aBase, 0.) : aBase + (transformed.y - aBase) * uHScale; }` : `
   if (aData.w > -.5 && aData.w < .5) {   // (by its building: a building goes whole, the ring passing it as the white film's dimming does)
     float dm_ = ${dim}, mod_ = ${MODERN_GLSL}; vMute = dm_ * mod_;${skip ? '\n     if (aSkip > .5) transformed.y = aBase - .02;   // (a replacement footprint stands here: todayFootprints)' : ''}
     if (fract(sin(dot(aCtr, vec2(127.1e3, 311.7e3))) * 43758.5453) < (1. - mod_) * 1.001 - .001) transformed.y = aBase - .02;   // (before the modern section none of it stood: building by building as it begins)
     if (vMute > .02 && aData.x > max(uYear, uDataY0) + .5) transformed.y = aBase - .02;   // (the backdrop: not built yet in the year told)${MAT ? `
     if (transformed.y > aBase) transformed.y = aBase + (transformed.y - aBase) * mix(1., ${(MAT.backdropH ?? .12).toFixed(2)}, vMute) * uHScaleT;   // (uHScaleT: today's heights toward true in a district or a close shot)
       // (a material's backdrop: today's city laid flat as a plan on the board while a period city stands, whatever the data first saw it in)` : ''}
     float e_ = uNow - (aGrowT > 0. ? aGrowT : tOfYear(aData.x - .5));   // (new: the white film's warm while new, uGrowWarm)
     vFresh = aData.x > 0. && uYLn > 1.5 && uGrowRise > .5 ? smoothstep(0., .22, e_) * (1. - smoothstep(.15, max(uGrowWarm, .5), e_)) : 0.; }`;
  const night = `
  if (uNight > .01 && abs(vWN.y) < .3) {   // lit windows at night: a grid of them on the walls, some houses lit, some windows dark
    float st_ = (vWP.y - vBase) / (uScaleM * 7.), al_ = dot(vWP.xz, vec2(-vWN.z, vWN.x)) / (uScaleM * 3.2), hb_ = fract(sin(dot(aCtrV, vec2(127.1e3, 311.7e3))) * 43758.5453);
    float w_ = smoothstep(.3, .36, fract(st_)) * smoothstep(.72, .66, fract(st_)) * smoothstep(.25, .32, fract(al_)) * smoothstep(.75, .68, fract(al_)) * step(.6, st_);
    float on_ = step(hb_, .55) * step(fract(sin(dot(floor(vec2(al_, st_)), vec2(12.9898, 78.233)) + hb_ * 91.) * 43758.5453), .6);
    totalEmissiveRadiance += vec3(1., .7, .36) * w_ * on_ * uNight * 2.2; }`;
  const marks = `
  { vec2 uv_ = vWP.xz / uPlate + .5; float l_ = dot(diffuseColor.rgb, vec3(.2126, .7152, .0722));   // an area the story marks: its buildings in its colour
    for (int i = 0; i < ${E}; i++) { if (uEpA[i] <= 0. || uEpB[i] < .5) continue; float m_ = layerAt(uv_, i); if (m_ <= 0.) continue;
      float rv_ = smoothstep(.08, -.08, length(vWP.xz - uEpC[i]) - uEpR[i]); vec3 ec_ = cEp[i] / max(max(cEp[i].r, cEp[i].g), max(cEp[i].b, .001));
      diffuseColor.rgb = mix(diffuseColor.rgb, ec_ * (.18 + 1.1 * l_), clamp(uEpA[i] * m_ * rv_ * 1.6, 0., 1.) * .8); } }`;
  mat.onBeforeCompile = (sh, r) => { deform(sh, r);
    Object.assign(sh.uniforms, back);   // (uBackdropY, uDataY0)
    if (u) { sh.uniforms.uHScale = HSCALE; sh.uniforms.uPool = POOL; sh.uniforms.uBuilt = BUILT; sh.uniforms.uPlateB = PLATE; }
    if (u) Object.assign(sh.uniforms, { uRuinLater: u.uRuinLater, uRuinT: u.uRuinT, uRuinH: u.uRuinH, uLossBurnt: u.uLossBurnt, uLossBurntV: u.uLossBurnt, uRuinC: { value: ruin || new THREE.Color('#bcae92') } },
      fire ? { ...fire.day.F, uO: fire.u.uO } : {});
    else { sh.uniforms.uFadeAt = { value: fadeAt }; sh.uniforms.uGlassSky = GLASS_SKY; sh.uniforms.uGlassK = GLASS_K; sh.uniforms.uDimTodayC = S.U.uDimTodayC || { value: 0 }; sh.uniforms.uHScaleT = HSCALE_T; sh.uniforms.uRoofOn = ROOF_ON; }
    if (u && MAT && MAT.soft && sh.vertexShader.includes('#include <beginnormal_vertex>')) sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec3 aSoft;')
      .replace('#include <beginnormal_vertex>', `#include <beginnormal_vertex>\n  objectNormal = normalize(mix(objectNormal, aSoft, ${MAT.soft.toFixed(2)}));   // (a rounded edge: the material's)`);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>\nvarying float vRuin, vMute, vFresh; uniform float uBackdropY, uDataY0;${u ? ` attribute float aY0; uniform float uHScale; uniform float uLossBurntV[${Math.max(nL, 1)}]; uniform float uRuinLater[${H}], uRuinT[${H}], uRuinH;` : ' uniform float uDimToday, uDimToday0, uDimTodayC, uHScaleT, uNodeR, uFadeAt, uGrowWarm; uniform vec2 uNodeC; attribute float aKind, aTop, aCut; uniform float uRoofOn; varying float vKind, vTop;' + (skip ? ' attribute float aSkip;' : '') + ((MAT && todayL() && todayL().bevel) && !depth ? ' attribute vec2 aEdge; varying vec2 vEdge;' : '')}`)
      .replace('#include <begin_vertex>', '#include <begin_vertex>\n vec3 tr0_ = transformed; vRuin = 0.; vMute = 0.; vFresh = 0.;' + (u ? '' : '\n if (aCut > .5) transformed.y = min(transformed.y, mix(aTop, aBase + (aTop - aBase) * aCut / 255., uRoofOn));   // (massing: its main mass ends at this share of its height, the parts above it stand on it, roofsMesh; coming down to it as the rooftop details come, uRoofOn)'))   // (as built, before the studio's deformation)
      .replace('#include <project_vertex>', vert + '\n#include <project_vertex>')
      .replace('#include <fog_vertex>', '#include <fog_vertex>\n vData = aData; vWP = (modelMatrix * vec4(transformed, 1.)).xyz;' + (depth ? '' : ' vWN = normalize(mat3(modelMatrix) * objectNormal);') + (u ? '' : ' vKind = aKind; vTop = aCut > .5 ? mix(aTop, aBase + (aTop - aBase) * aCut / 255., uRoofOn) : aTop;' + ((MAT && todayL() && todayL().bevel) && !depth ? ' vEdge = aEdge;' : '')));
    if (depth) return;
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>\n// (look: mini)\nfloat glass_ = 0., eng_ = 0.;\nvarying vec4 vData; varying vec3 vWP, vWN; varying float vUp, vBase, vRuin, vMute, vFresh; varying vec2 aCtrV;${u ? '' : ' varying float vKind, vTop; uniform vec3 uGlassSky; uniform float uGlassK, uHScaleT;' + ((MAT && todayL() && todayL().bevel) ? ' varying vec2 vEdge;' : '') + (MAT ? '\nfloat mtH(vec2 p){ vec3 q = fract(vec3(p.xyx) * .1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }\nfloat mtN(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f); return mix(mix(mtH(i), mtH(i + vec2(1, 0)), f.x), mix(mtH(i + vec2(0, 1)), mtH(i + vec2(1, 1)), f.x), f.y); }' : '')} uniform float uNow, uNight, uScaleM, uPallR, uPallK; uniform vec2 uPallC;${S.marksGLSL()}${u ? ` uniform float uEraBurn, uLossBurn[${nL}], uLossBurnt[${nL}]; uniform vec3 uRuinC;${fire ? ' uniform vec2 uO;' + S.fireGLSL : ''}` : ''}`)
      .replace('#include <color_fragment>', '#include <color_fragment>' + marks + '\n  diffuseColor.rgb *= 1. - uPallK * .55 * smoothstep(uPallR, uPallR * .3, length(vWP.xz - uPallC));   // (under a burning city\'s pall)')
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>' + night);
    if (u && surf) sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
  { float pt_ = vData.y; vec3 n_ = normalize(vWN); float px_ = length(fwidth(vWP.xz)) / uScaleM;   // (a model's surfaces: metres a pixel)
    if ((pt_ > 7.5 && pt_ < 9.5) || (n_.y > .25 && n_.y < .97)) {   // a roof's slope: its tiles in ribs down it and courses across
      vec2 nh_ = normalize(n_.xz + 1e-5); float u_ = dot(vWP.xz, vec2(-nh_.y, nh_.x)) / uScaleM, v_ = dot(vWP.xz, nh_) / uScaleM;
      diffuseColor.rgb *= 1. - .24 * smoothstep(.5, .9, abs(fract(u_ / 1.5) - .5) * 2.) * (1. - smoothstep(.3, .7, px_ / 1.5));
      diffuseColor.rgb *= 1. - .1 * smoothstep(.82, .96, fract(v_ / 2.4)) * (1. - smoothstep(.3, .7, px_ / 2.4));${FILM_PIC.material === 'clay' ? `
      { vec2 t_ = floor(vec2(u_ / 1.5, v_ / 1.2)); float h_ = fract(sin(dot(t_, vec2(12.99, 78.23))) * 43758.55);   // (clay: each tile its own, in relief)
        diffuseColor.rgb *= (.86 + .24 * h_) * (1. - .22 * smoothstep(.75, .95, fract(v_ / 1.2)) * (1. - smoothstep(.3, .7, px_ / 1.2))); }` : FILM_PIC.material === 'maquette' ? `
      diffuseColor.rgb *= .95 + .05 * sin(v_ * 23. + sin(u_ * 1.7) * 3.) * (1. - smoothstep(.2, .5, px_));   // (maquette: the wood's grain along the courses)
` : ''} }
    else if (abs(n_.y) < .3) { diffuseColor.rgb *= mix(.7, 1., smoothstep(0., 3.5, (vWP.y - vBase) / uScaleM));   // a wall darker at its foot
${FILM_PIC.material === 'clay' ? `
      float mo_ = 1. - smoothstep(0., 1.2, (vWP.y - vBase) / uScaleM), nz_ = fract(sin(dot(floor(vWP.xz / uScaleM * 2.), vec2(7.1, 3.3))) * 43758.5);
      diffuseColor.rgb = mix(diffuseColor.rgb, vec3(.09, .14, .04), mo_ * (.35 + .4 * nz_));   // (clay: moss where the wall meets the ground)
` : ''} }
    else if (${MAT ? 'true' : 'false'} && n_.y > .97 && (abs(pt_ - 1.) < .5 || abs(pt_ - 11.) < .5) && (vWP.y - vBase) / uScaleM < 9.) {   // (a material's: a landmark's open ground, a plaza, paved in stone slabs)
      vec2 e_ = abs(fract(vWP.xz / uScaleM / 3.2) - .5) * 2.; float h_ = fract(sin(dot(floor(vWP.xz / uScaleM / 3.2), vec2(12.99, 78.23))) * 43758.55);
      diffuseColor.rgb = ${FILM_PIC.material === 'clay' ? 'mix(vec3(dot(diffuseColor.rgb, vec3(.2126, .7152, .0722))), diffuseColor.rgb, .45) * .62' : 'vec3(.55, .53, .49)'} * (.95 + .08 * h_) * (1. - ${FILM_PIC.material === 'clay' ? '.35' : '.12'} * smoothstep(.965, .995, max(e_.x, e_.y)) * (1. - smoothstep(.3, .7, px_ / 3.2))); }
    else if (pt_ > 6.5 && pt_ < 7.5 && ${FILM_PIC.material === 'clay' ? 'true' : 'false'}) { vec2 q_ = vWP.xz / uScaleM / .55, c_ = floor(q_ + .5 * vec2(0., mod(floor(q_.x), 2.)));   // (clay: cobbles)
      vec2 f_ = fract(q_ + .5 * vec2(0., mod(floor(q_.x), 2.))) - .5; float h_ = fract(sin(dot(c_, vec2(12.99, 78.23))) * 43758.55);
      diffuseColor.rgb *= (.8 + .3 * h_) * (1. - .45 * smoothstep(.32, .5, max(abs(f_.x), abs(f_.y))) * (1. - smoothstep(.3, .7, px_ / .55))) * (1.1 - 1.2 * dot(f_ + vec2(.12, .12), f_ + vec2(.12, .12)));   // (each stone domed, lit from one side)
    }
    else if (pt_ > 6.5 && pt_ < 7.5) { vec2 e_ = abs(fract(vWP.xz / uScaleM / 3.) - .5) * 2.;   // paving in slabs
      diffuseColor.rgb *= 1. - .16 * smoothstep(.86, .97, max(e_.x, e_.y)) * (1. - smoothstep(.3, .7, px_ / 3.)); } }`);
    if (u) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform vec4 uPool; uniform sampler2D uBuilt; uniform vec2 uPlateB;').replace('#include <color_fragment>', `#include <color_fragment>
  diffuseColor.rgb *= mix(1., uPool.w, smoothstep(uPool.z * .35, uPool.z * 1.05, length(vWP.xz - uPool.xy)));   // (the light pool, FILM_PIC pool)${MAT && MAT.base && MAT.base.ground_in ? `
  { float bt_ = smoothstep(.3, .55, texture2D(uBuilt, vWP.xz / uPlateB + .5).r), pv_ = abs(vData.y - 7.) < .5 || abs(vData.y - 10.) < .5 || abs(vData.y - 11.) < .5 ? 1. : 0.;   // (roads, earth and the platforms of lots: out of the built area they are the land)
    diffuseColor.rgb = mix(diffuseColor.rgb, pow(${MAT.base.land ? 'vec3(' + MAT.base.land.olive.map(v => v.toFixed(3)).join(', ') + ')' : 'vec3(' + MAT.base.slate.map(v => Math.pow(v, 1 / 2.2).toFixed(3)).join(', ') + ')'}, vec3(2.2)) * ${MAT.base.land ? '.92' : '1.3'}, pv_ * (1. - bt_)); }   // (a road out in the country laid in the land, not a line on it)` : ''}
  float burn_ = uEraBurn, burnt_ = uEraBurn, char_ = uEraBurn; for (int k = 0; k < ${nL}; k++) if (abs(vData.w - 4. - float(k)) < .5) { burn_ = max(burn_, uLossBurn[k]); char_ = max(char_, uLossBurn[k]); burnt_ = max(burnt_, uLossBurnt[k]); }   // (studio.js eraBurnK; burnt: a part a fire took)${fire ? `
  if (uEraBurn > 0.) { float e_ = uNow - ign(aCtrV, fireHash(aCtrV)); char_ = smoothstep(0., 2.5, e_); burn_ = smoothstep(0., .6, e_) * (1. - .7 * smoothstep(2.5, 5., e_)); }   // (the fire's front: studio.js fireByDay)` : ''}
  diffuseColor.rgb *= 1. - .88 * char_;
  diffuseColor.rgb = mix(diffuseColor.rgb, uRuinC * (1. - .8 * burnt_), vRuin);   // foundations`)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
  { float h_ = fract(sin(dot(aCtrV, vec2(127.1e3, 311.7e3))) * 43758.5453), fl_ = .5 + .5 * sin(uNow * (6. + 5. * h_) + h_ * 40.);   // a burning building's walls glow, flickering (its flames: studio.js)
    totalEmissiveRadiance += vec3(1., .34, .06) * burn_ * vUp * (abs(vWN.y) < .5 ? .15 + .55 * fl_ : .04); }`);
    else sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
  { float l_ = dot(diffuseColor.rgb, vec3(.2126, .7152, .0722)); diffuseColor.rgb = mix(diffuseColor.rgb, mix(vec3(l_), diffuseColor.rgb, .35) * .8 + .1 * l_ + .03, .8 * vMute);   // a muted backdrop
    diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(1.22, 1.1, .88) + vec3(.07, .045, 0.), vFresh);${MAT ? '\n    diffuseColor.rgb *= 1. - .4 * vMute;   // (a material: today\'s city dimmed further behind a period city standing, the period city the subject)\n' : ''}${MAT && !depth ? FACADE_GLSL(S) : ''} }   // new: warm while new`);
    const BV_ = !u && MAT && !depth && todayL() && todayL().bevel, EXB_ = (S.U.uScaleH ? S.U.uScaleH.value / S.U.uScaleM.value : 3).toFixed(3);   // (todayLight bevel: [the rounding's radius m, its least size in fwidth's metres, a corner's turn, the roof line's (shares of a right angle)]:
    // every wall's top edge and its convex corners rounded as a model's are, in the light: the normal turns across a band of that
    // radius toward the roof (up) and round the corner, so the edge catches the sun and the sky; at least about a pixel wide afar,
    // a lit rim along each roof line and down each sunlit corner, never finer to shimmer; the silhouette the data's)
    if (BV_) sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
  { vec3 nw_ = normalize(vWN);
    if (abs(nw_.y) < .3 && vData.w < .5 && vData.y > 2.5 && vMute < .5) {
      float pxm_ = length(fwidth(vWP)) / uScaleM, r_ = max(${(+BV_[0]).toFixed(3)}, ${(+BV_[1]).toFixed(3)} * pxm_), ym_ = (vWP.y - vBase) / uScaleM / ${EXB_};
      float top_ = (vTop > vBase + 1e-7 ? (vTop - vBase) / uScaleM / ${EXB_} : vData.y) * uHScaleT * max(vUp, .001), br_ = clamp(1. - (top_ - ym_) * ${EXB_} / r_, 0., 1.);   // (the roof line: metres below the wall's top, as drawn)
      float dA_ = vEdge.x > 65534.5 ? 1e4 : (vEdge.x - 1.) * .01, dB_ = vEdge.y > 65534.5 ? 1e4 : (vEdge.y - 1.) * .01;   // (a convex corner at either end: metres to it)
      vec3 tw_ = vec3(normalize(vec2(-nw_.z, nw_.x) + 1e-6), 0.).xzy, cd_ = dB_ < dA_ ? tw_ : -tw_; float bc_ = clamp(1. - min(dA_, dB_) / r_, 0., 1.);
      vec3 nb_ = normalize(nw_ * cos(bc_ * ${(BV_[2] * Math.PI / 4).toFixed(4)}) + cd_ * sin(bc_ * ${(BV_[2] * Math.PI / 4).toFixed(4)}));
      nb_ = normalize(nb_ * cos(br_ * ${(BV_[3] * Math.PI / 2).toFixed(4)}) + vec3(0., 1., 0.) * sin(br_ * ${(BV_[3] * Math.PI / 2).toFixed(4)}));
      normal = normalize((viewMatrix * vec4(nb_, 0.)).xyz); } }`);
    if (!u && MAT && !depth) sh.fragmentShader = sh.fragmentShader.replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = mix(roughnessFactor, .22, glass_);   // (glass: the sun\'s sheen on it)');
    const WS_ = !u && MAT && !depth && todayL() && todayL().wallSun;   // (todayLight wallSun: the sun on today's painted walls this much brighter and warmer (rgb, times), its direct light only: a lit wall a warm cream, the shade side as it was; [3]: a warm paint's share of that warmth and the sun's own withheld)
    if (WS_) sh.fragmentShader = sh.fragmentShader.replace('#include <lights_fragment_end>', `#include <lights_fragment_end>
  if (abs(normalize(vWN).y) < .3) { vec3 ws_ = vec3(${WS_.slice(0, 3).map(v => v.toFixed(3)).join(', ')}); float wg_ = dot(ws_, vec3(.2126, .7152, .0722));${WS_[3] ? `
    ws_ = wg_ * mix(ws_ / wg_, vec3(${(c_ => { const l_ = .2126 * c_.r + .7152 * c_.g + .0722 * c_.b; return [l_ / c_.r, l_ / c_.g, l_ / c_.b].map(v => v.toFixed(3)).join(', '); })(new THREE.Color(todayL().sunC || '#ffffff'))}), ${WS_[3].toFixed(3)} * smoothstep(.15, .45, (diffuseColor.r - diffuseColor.b) / max(diffuseColor.r, 1e-3)));   // ([3]: a warm paint's (a pink's, a peach's) share of the warmth withheld, its brightness kept: in the sun a cream glows golden, a pink stays pink, not orange)` : ''}
    reflectedLight.directDiffuse *= mix(vec3(1.), ws_, (1. - glass_) * (1. - vMute)); }`);
    const WD_ = !u && MAT && !depth && todayL() && todayL().wallShade;   // (todayLight wallShade: [the sky light's own colour kept, times, [rgb], the shade's saturation]: the shade side of today's painted walls lit by a neutral (or this tinted) sky light and its paint's chroma this many times, hue kept, so a pastel in shade stays a pastel; the lit side as it was)
    if (WD_) sh.fragmentShader = sh.fragmentShader.replace('#include <lights_fragment_end>', `float wd_ = abs(normalize(vWN).y) < .3 ? (1. - glass_) * (1. - vMute) : 0.;
  irradiance = mix(irradiance, mix(vec3(dot(irradiance, vec3(.2126, .7152, .0722))), irradiance, ${(+WD_[0]).toFixed(3)}) * ${(+WD_[1]).toFixed(3)} * vec3(${(WD_[2] || [1, 1, 1]).map(v => (+v).toFixed(3)).join(', ')}), wd_);
#include <lights_fragment_end>${WD_[3] ? `
  { vec3 id_ = reflectedLight.indirectDiffuse; float l_ = dot(id_, vec3(.2126, .7152, .0722)); reflectedLight.indirectDiffuse = mix(id_, max(vec3(0.), l_ + (id_ - l_) * ${(+WD_[3]).toFixed(3)}), wd_); }` : ''}`);
    if (!u && MAT && !depth) sh.fragmentShader = sh.fragmentShader.replace('#include <opaque_fragment>', `{ float lw_ = dot(outgoingLight, vec3(.2126, .7152, .0722));   // the engraving on a lit wall: a groove keeps its shade however strong the light (on glass the sun's sheen had washed it out)
    outgoingLight *= 1. - .45 * eng_ * smoothstep(.35, 1., lw_); }${roofMapOn() ? `
  outgoingLight = diffuseColor.rgb;   // (the roof kinds' map: each surface its own tint, unlit, so a script can read the kinds back from the picture)` : ''}
#include <opaque_fragment>`); };
  mat.customProgramCacheKey = () => 'mini-film ' + (u ? 'era ' + nL + (fire ? ' fire' : '') : 'today') + (depth ? ' depth' : '') + (surf ? ' surf' : '') + (skip ? ' skip' : '');
  return mat;
}
