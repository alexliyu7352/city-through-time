// Effects shared by both looks (the white model: studio.js, post.js, main.js; the coloured miniature: mini.js): the ground's relief
// in the light, the light's warmth, the haze and the sky, the depth of field's strength, and light that moves: glowing lines with
// light flowing along them, a column of light, a flare, sparks. All of them are off unless a film asks (film.fx, compile) or the
// page's address does (?fx=1: every effect at its default; ?fx=relief,haze: those alone; ?fx={json}: as film.fx; ?fx=0: none), so a film made before them
// draws exactly as it did: no shader of the film's own changes while they are off.
// The haze and the depth of field's gather live in post.js (the pass that already reads the picture's depth); the sky dome, the
// relief texture and its shader code, and the light effects' objects here. (The sky's horizon brighter toward the sun after
// lemo-opuscar styles/tilt-shift/demo/sky.js, MIT; see NOTICE.)
import * as THREE from 'three';

// the default of each effect (film.fx gives any of these keys; a key given as true takes its default)
//   relief: { k: how many times as steep the slopes look in their light (the city's own terrain.exaggeration included: k 6 on a x3
//             plate shades its slopes twice as steep again; the slopes' light, not the ground's height: buildings stay seated); [close, wide]: by
//             the shot's distance (span_m), so a close shot brings out the hills a city stands on and a wide one keeps the land's
//             own proportions (a strong k over a whole plate read as swells, a sea); shadow and ao take a pair the same way,
//             el: the low sun's height in degrees, side: its bearing in degrees round from the eye's (negative: to the left; across
//             the picture, so the slopes facing the eye show light and shade), shadow: 0..1 (the land's own cast shadows), ao: 0..1
//             (hollows and valley floors darker), light: 0..1 (sunlit slopes lit in the ground's own hue on top: a dark ground's
//             relief reads only so), flat: a slope in percent under which the ground is shaded as flat, fading in over twice that
//             (0: every slope as it is), span_m: [close, wide] the shot's distances in metres between which a pair goes from its first
//             value to its second }
//   light:  { az, el: a sun fixed in the world (compass bearing toward it, height, degrees; unset: the terrain's own side light,
//             terrain.shade, else from the north-west, 28 up), the key light in its place: every building and slope modelled by
//             one low sun and its shadows, whichever way the eye looks; warm: 0..1 (that sun warm, the sky's fill cool, sunlit
//             slopes warm and shaded ones cool), ao: 0..1 (ambient occlusion in the white model; none in the live preview) }
//   haze:   { dist_km: the distance at which the air takes 63 % of what is behind it at the ground, height_m: the air's thickness
//             (it thins upward), k: 0..1, start_km: none nearer than this (what is near keeps its colour), edge_km: in a low view the
//             land's last this many km before the end of the model fade wholly into the haze (no step against the sky) }
//   dof:    { k: the aperture times the film's own, max: the largest blur in pixels of a 1080 picture, band: [close, wide] the
//             sharp band's half-depth round the focus as a share of its distance, for a close shot and a wide one }
//   glow:   { lines: glowing lines (a hot core, a halo, light flowing along them), column: a column of light where a beam lands
//             (a beam's own column: false in staging leaves it out for that beam), flare: a flare where it lands and at the
//             line's head, sparks: a burst of sparks where it lands }
//   land:   { source: 'quiet' (one soil-and-grass ground, soft variation, no field blocks) or 'fields' (a patchwork of fields),
//             palette: the land's colours (LAND_PALETTES), mute: 0..1 the white model's land toward grey, warm: 0..1 toward a
//             warm sepia, dark: its lightness (the white models stay the subject), scrub: a slope in percent from which the land
//             is scrub and woods (with the relief), trees: trees standing in the woods and open ground in the white model too (the
//             miniature's planting; the period cities' viewer) }: the plate as land, soil and vegetation, in place of the white
//             model's one plate colour; the miniature's ground drawn by the same code
export const FX_DEFAULT = {
  relief: { k: [7, 2.2], el: 22, side: -105, shadow: [.85, .4], ao: [.75, .4], light: .6, flat: 0, span_m: [600, 3000] },
  light: { warm: .5, ao: .5, az: null, el: 28 },
  haze: { dist_km: 9, height_m: 200, k: 1, start_km: 1, edge_km: 6 },
  dof: { k: 1.4, max: 11, band: [.16, .45] },
  glow: { lines: true, column: true, flare: true, sparks: true },
  land: { source: 'quiet', palette: 'temperate', mute: .35, dark: .85, warm: 0, scrub: 6, trees: false },
};
// the sky and the haze by look: the white model's a luminous grey-blue band at the horizon, brighter than the ground and warmer
// toward the sun, up into the dark room's black; the miniature's a hazy day
export const FX_SKY = {
  film: { horizon: '#8d9aab', zenith: '#0a0d13', sun: '#b8916a' },
  mini: { horizon: '#e2e5e1', zenith: '#7aa5d6', sun: '#f6dcb4' },
};

// film.fx and the page's ?fx= -> the effects on, each with its settings filled in (null: none)
export function fxSettings(film, qs) {
  const q = qs.get('fx');
  let want = film || null;
  if (q === '0') want = null;
  else if (q === '1') want = Object.fromEntries(Object.keys(FX_DEFAULT).map(k => [k, true]));
  else if (q && q.startsWith('{')) want = JSON.parse(q);   // (?fx={"relief":{"k":3},"haze":true}: as film.fx would write it)
  else if (q) want = Object.fromEntries(q.split(',').filter(k => k in FX_DEFAULT).map(k => [k, (film && film[k]) || true]));
  if (!want) return null;
  const out = {};
  for (const [k, v] of Object.entries(want)) if (v && k in FX_DEFAULT) out[k] = { ...FX_DEFAULT[k], ...(v === true ? {} : v) };
  return Object.keys(out).length ? out : null;
}

// ---------------------------------------------------------------- relief
// a heightfield as a texture (R height in model units, G its openness to the sky, B A its slope along x and z), at full float
// precision where the graphics can filter it (else half), from the 16-bit relief (data/terrain16.png, ~3 mm steps); the shading
// exaggeration k is the shader's. field: { w, h, data (model units, row 0 at the rect's z0) }, cx cz: a texel's size (model
// units), scale: model units per metre. An elevation model is a surface model: a lone tower or tree is a spike k times as steep,
// so first an opening and a closing over three texels (the lowest of each 3 x 3, the highest of those, then the reverse: what
// stands up or cuts in narrower than ~90 m goes, every landform stays), then a light smoothing (~1 texel) for the slopes and a
// little more (~2 texels) for the shadows' and the openness' heights. Openness: eight directions, the highest horizon within
// ~2 km (k times as steep), 1 on open ground, less in a hollow or at a cliff's foot
export function reliefTexture(field, cx, cz, k, scale, float = true) {
  const { w, h } = field, out = new Float32Array(w * h * 4);
  const grnd = Float32Array.from(field.data);
  for (const pick of [Math.min, Math.max, Math.max, Math.min]) { const t = new Float32Array(w * h);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { let m = grnd[j * w + i]; for (let d = -1; d <= 1; d++) { const x = i + d; if (x >= 0 && x < w) m = pick(m, grnd[j * w + x]); } t[j * w + i] = m; }
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { let m = t[j * w + i]; for (let d = -1; d <= 1; d++) { const y = j + d; if (y >= 0 && y < h) m = pick(m, t[y * w + i]); } grnd[j * w + i] = m; } }
  const smooth = R => { const a = Float32Array.from(grnd), t = new Float32Array(w * h);
    for (let pass = 0; pass < 2; pass++) {
      for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { let s = 0, n = 0; for (let d = -R; d <= R; d++) { const x = i + d; if (x >= 0 && x < w) { s += a[j * w + x]; n++; } } t[j * w + i] = s / n; }
      for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { let s = 0, n = 0; for (let d = -R; d <= R; d++) { const y = j + d; if (y >= 0 && y < h) { s += t[y * w + i]; n++; } } a[j * w + i] = s / n; }
    }
    return a; };
  const cell = Math.max(cx, cz) / scale, fine = smooth(1), broad = smooth(2);
  const at = (a, i, j) => a[Math.max(0, Math.min(h - 1, j)) * w + Math.max(0, Math.min(w - 1, i))];
  const dirs = Array.from({ length: 8 }, (_, a) => [Math.cos(a * Math.PI / 4), Math.sin(a * Math.PI / 4)]);
  const reach = Math.max(4, Math.round(2000 / cell));   // (texels in ~2 km)
  const steps = []; for (let s = 1; s <= reach; s = Math.ceil(s * 1.6)) steps.push(s);
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
    const h0 = at(broad, i, j); let occ = 0;
    for (const [dx, dz] of dirs) {
      let m = 0;
      for (const s of steps) { const q = (at(broad, Math.round(i + dx * s), Math.round(j + dz * s)) - h0) * k / (s * Math.hypot(dx * cx, dz * cz)); if (q > m) m = q; }
      occ += m / Math.sqrt(1 + m * m);   // (sin of the horizon's angle)
    }
    const o = (j * w + i) * 4;
    out[o] = h0; out[o + 1] = 1 - occ / dirs.length; out[o + 2] = (at(fine, i + 1, j) - at(fine, i - 1, j)) / (2 * cx); out[o + 3] = (at(fine, i, j + 1) - at(fine, i, j - 1)) / (2 * cz);
  }
  let t;
  if (float) t = new THREE.DataTexture(out, w, h, THREE.RGBAFormat, THREE.FloatType);
  else { const half = new Uint16Array(out.length); for (let n = 0; n < out.length; n++) half[n] = THREE.DataUtils.toHalfFloat(out[n]); t = new THREE.DataTexture(half, w, h, THREE.RGBAFormat, THREE.HalfFloatType); }
  t.magFilter = t.minFilter = THREE.LinearFilter; t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; t.colorSpace = THREE.NoColorSpace; t.needsUpdate = true;
  return t;
}
// the relief's uniforms: rect [x0, z0, x1, z1] (model units) the field covers, cell a texel's size; shared (the sun, the tints)
// passed in from another set where one exists (the land beyond the plate shares the plate's sun)
export function reliefUniforms(tex, rect, cell, o, ex = 3, shared = null) {
  return { uFxHgt: { value: tex }, uFxRect: { value: new THREE.Vector4(rect[0], rect[1], 1 / (rect[2] - rect[0]), 1 / (rect[3] - rect[1])) },
    uFxR: { value: new THREE.Vector4(fxAt(o.k, 0) / ex, fxAt(o.shadow, 0), fxAt(o.ao, 0), cell) }, uFxRA: { value: tex ? 1 : 0 }, uFxFlat: { value: (o.flat || 0) / 100 * ex },
    ...(shared ? { uFxSun: shared.uFxSun, uFxLitC: shared.uFxLitC, uFxShadeC: shared.uFxShadeC, uFxAdd: shared.uFxAdd }
      : { uFxSun: { value: new THREE.Vector3(0, 1, 0) }, uFxLitC: { value: new THREE.Color(1, 1, 1) }, uFxShadeC: { value: new THREE.Color(1, 1, 1) }, uFxAdd: { value: o.light ?? 0 } }) };   // (slopes in the model's own exaggeration)
}
// the ground's light by its relief, at a point p on it: (the sun's light on the slope k times as steep, its cast shadow, openness),
// and the factor the ground's own light takes from it (1 on open flat ground in the sun). Off the heightfield: 1
export const RELIEF_GLSL = /* glsl */`
uniform sampler2D uFxHgt; uniform vec4 uFxRect, uFxR; uniform vec3 uFxSun, uFxLitC, uFxShadeC; uniform float uFxRA, uFxAdd, uFxFlat;
vec2 fxUv(vec2 xz){ return (xz - uFxRect.xy) * uFxRect.zw; }
vec4 fxHg(vec2 xz){ return texture2D(uFxHgt, fxUv(xz)); }
vec3 fxRelief(vec3 p){
  vec4 g = fxHg(p.xz); float k = uFxR.x, e = uFxR.w;
  vec2 sl = uFxFlat > 0. ? g.zw * smoothstep(uFxFlat, 2. * uFxFlat, length(g.zw)) : g.zw;   // (flat: a plain's gentlest slopes shaded as flat, if asked)
  vec3 n = normalize(vec3(-sl.x * k, 1., -sl.y * k));
  vec2 dl = normalize(uFxSun.xz + 1e-6); float rise = uFxSun.y / max(length(uFxSun.xz), 1e-3);
  float sh = 1., t = e;
  for (int i = 0; i < 20; i++) {   // (out along the sun's bearing, each step 1.35 times the last, ~10 km at 30 m texels)
    float d = (g.r + t * rise / k - fxHg(p.xz + dl * t).r) * k / t;   // (the ray's height over the land, as an angle)
    sh = min(sh, smoothstep(-.035, .035, d)); t *= 1.35; }
  return vec3(max(dot(n, uFxSun), 0.), sh, g.g);
}
// light: the ground's light (outgoingLight), hue: its own colour -> the light with the relief in it: times the slope's light against
// flat ground's, its openness and the light's tint, plus (uFxAdd) the sunlit slopes in the ground's own hue
// (past the field's edge: its edge's light, so the plate's skirt and rim carry on as the land beside them)
vec3 fxReliefLight(vec3 p, vec3 light, vec3 hue){
  if (uFxRA <= 0.) return light;
  vec3 r = fxRelief(vec3(clamp(p.xz, uFxRect.xy, uFxRect.xy + 1. / uFxRect.zw), p.y).xzy);
  float flat_ = max(uFxSun.y, .05), lam = r.x * mix(1., r.y, uFxR.y);
  float lit = (lam + .3) / (flat_ + .3), ao = mix(1., pow(max(r.z, 1e-4), 1.5), uFxR.z);
  vec3 tint = mix(uFxShadeC, uFxLitC, smoothstep(.55, 1.25, lit));
  vec3 h = hue / max(max(hue.r, hue.g), max(hue.b, .001));
  return light * mix(vec3(1.), lit * ao * tint, uFxRA) + h * uFxLitC * uFxAdd * uFxRA * .5 * max(lam - flat_ * .6, 0.) * ao;
}`;
// the relief's sun: a unit vector toward it, `side` degrees round from the eye's bearing, `el` up
export const sunVector = (v, az, el) => { const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el); return v.set(Math.sin(a) * Math.cos(e), Math.sin(e), -Math.cos(a) * Math.cos(e)); };   // (compass bearing; x east, z south)
export function reliefSun(v, eyeAz, o) {   // eyeAz: the eye's bearing from what it looks at (radians, as main.js's az)
  const az = eyeAz + THREE.MathUtils.degToRad(o.side), e = THREE.MathUtils.degToRad(o.el);
  return v.set(Math.sin(az) * Math.cos(e), Math.sin(e), Math.cos(az) * Math.cos(e));
}

// a setting given as one value or as [close, wide], at t (0 close .. 1 wide)
export const fxAt = (v, t) => Array.isArray(v) ? v[0] + (v[1] - v[0]) * t : v;
// the relief's strength for a shot d model units away (scale: model units per metre): k, shadow and ao from their close values
// to their wide ones over span_m; sets: [the relief uniforms, the exaggeration their heights already have] (the plate's, the land
// beyond's): k is the slopes' steepness as seen, whatever the city's own exaggeration
export function reliefSpan(sets, o, d, scale) {
  const sp = o.span_m || [500, 3500], t = THREE.MathUtils.smoothstep(d / scale, sp[0], sp[1]);
  for (const [u, ex] of sets) { const r = u.uFxR.value; r.x = fxAt(o.k, t) / ex; r.y = fxAt(o.shadow, t); r.z = fxAt(o.ao, t); }
}

// ---------------------------------------------------------------- the land
// the land's colours (sRGB) by kind: fields' two greens, straw, bare soil, woods and scrub; trees: how trees stand on it in the
// white model (fx land trees: their size, the share of open places kept, the share of the woods' places)
export const LAND_PALETTES = {
  mediterranean: { grass0: [.36, .45, .24], grass1: [.47, .51, .28], straw: [.66, .60, .40], soil: [.55, .47, .34], wood: [.21, .28, .15] },
  loess: { grass0: [.42, .47, .27], grass1: [.52, .53, .31], straw: [.74, .66, .44], soil: [.68, .58, .42], wood: [.27, .33, .18], trees: { size: .6, keep: .07, wood: .35 } },   // a loess plain: wheat, millet, bare earth; few trees
  temperate: { grass0: [.36, .45, .24], grass1: [.47, .51, .28], straw: [.66, .60, .40], soil: [.58, .56, .52], wood: [.2, .28, .15] },
};
// the land's colour (linear) at m (metres), by style: 'fields' a patchwork of fields (greens, straw, bare earth) under a soft
// noise; 'quiet' one soil-and-grass ground, varying softly at several scales (km, hundreds of metres, a hundred, twenty) with
// no edges and the fields at most a faint grain (the patchwork read as rags sewn together). Both: woods in soft patches, and
// scrub and woods where the ground is steep (steep 0..1: the caller's, from the relief; 0 without one); woods false: no woods.
// fxDetail(m): the quiet ground's own variation alone (1 on average)
export function landGLSL(p, woods = true, style = 'fields') {
  const v3 = a => `vec3(${a.map(x => x.toFixed(3)).join(', ')})`;
  const head = /* glsl */`
float fxLh(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float fxLn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(fxLh(i), fxLh(i + vec2(1, 0)), f.x), mix(fxLh(i + vec2(0, 1)), fxLh(i + vec2(1, 1)), f.x), f.y); }
// woods in patches on the flat (0..1): a value noise on a hash without sin, so woodsAt (JS) finds the same patches for the trees
float fxWh(vec2 p){ vec3 q = fract(vec3(p.xyx) * .1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float fxWn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(fxWh(i), fxWh(i + vec2(1, 0)), f.x), mix(fxWh(i + vec2(0, 1)), fxWh(i + vec2(1, 1)), f.x), f.y); }
float fxWoodsN(vec2 m){ return fxWn(m / 520.) * .7 + fxWn(m / 110.) * .3; }
float fxDetail(vec2 m){ return 1. + .2 * (fxLn(m / 610. + 3.1) - .5) + .16 * (fxLn(m / 140. + 7.7) - .5) + .12 * (fxLn(m / 23. + 1.3) - .5); }`;
  const wood = (lo, hi, k) => `
  float wood = max(steep, smoothstep(${lo}, ${hi}, fxWoodsN(m_)));
  land = mix(land, ${v3(p.wood)} * (.82 + .36 * fxLn(m_ / 26.)), wood * ${woods ? k : '0.'});`;
  if (style === 'quiet') return head + `
vec3 fxLand(vec2 m_, float steep){
  float n1 = fxLn(m_ / 2300.), n2 = fxLn(m_ / 610. + 3.1), n3 = fxLn(m_ / 140. + 7.7);
  vec3 grass = mix(${v3(p.grass0)}, ${v3(p.grass1)}, n2), earth = mix(${v3(p.soil)}, ${v3(p.straw)}, n3 * .7);
  vec3 land = mix(grass, earth, smoothstep(.2, .9, n1) * .5);   // (soil and grass shading into each other over kilometres)
  vec2 m = m_ + vec2(fxLn(m_ / 300.), fxLn(m_ / 300. + 7.)) * 60.;
  land *= fxDetail(m_) * (1. + .05 * (fxLh(floor(m / vec2(160., 105.) + vec2(.3, .7) * floor(m.y / 105.))) - .5));   // (the fields: a faint grain)${wood('.56', '.76', '.75')}
  return pow(land, vec3(2.2)); }`;
  return head + `
vec3 fxLand(vec2 m_, float steep){
  vec2 m = m_ + vec2(fxLn(m_ / 300.), fxLn(m_ / 300. + 7.)) * 60.;   // (the fields' edges not ruled straight)
  float field = fxLh(floor(m / vec2(160., 105.) + vec2(.3, .7) * floor(m.y / 105.)));
  float n = fxLn(m_ / 60.) * .6 + fxLn(m_ / 13.) * .4;
  vec3 land = mix(${v3(p.grass0)}, ${v3(p.grass1)}, smoothstep(.0, .55, field));
  land = mix(land, ${v3(p.straw)}, step(.62, field)); land = mix(land, ${v3(p.soil)}, step(.86, field));
  land *= .9 + .2 * n;${wood('.62', '.7', '.9')}
  return pow(land, vec3(2.2)); }`;
}
// the slopes (model units, the plate's exaggeration in them) over which the land turns from fields to scrub and woods
export const landSlopes = (o, ex) => { const s = (o.scrub ?? 14) / 100 * ex; return [s * .6, s * 1.5]; };
// the palette a land is drawn in (LAND_PALETTES by o.palette; temperate when it names none)
export const landPalette = o => LAND_PALETTES[o && o.palette] || LAND_PALETTES.temperate;
// the land in a look, fxLandAt(world position): o the land's settings (null: the palette's fields alone, no woods), ex the plate's
// exaggeration, scale model units per metre, look 'film' (muted toward grey by mute, warmed by warm, its lightness dark: the white
// city stays the subject) or 'mini'; hgt: the relief's heights are there (fxHg, RELIEF_GLSL), for the slope. Its settings are
// written into the code, not passed as uniforms: a phone's shaders have no room to spare (tools/phonecheck)
export function landLookGLSL(p, hgt, o, ex, scale, look) {
  const f = x => x.toFixed(6), [s0, s1] = o ? landSlopes(o, ex) : [1e3, 2e3], film = look !== 'mini' && !!o;
  const mute = film ? o.mute : 0, dark = film ? o.dark : 1, warm = film ? (o.warm ?? 0) : 0;
  const style = o && o.source !== 'fields' ? 'quiet' : 'fields';
  return landGLSL(p, !!o, style) + `
vec3 fxLandAt(vec3 w){ float st = ${hgt ? `smoothstep(${f(s0)}, ${f(s1)}, length(fxHg(w.xz).zw))` : '0.'};
  vec3 c = fxLand(w.xz / ${f(scale)}, st);
  c = mix(c, vec3(dot(c, vec3(.2126, .7152, .0722))), ${f(mute)}) * mix(vec3(1.), vec3(1.1, 1., .8), ${f(warm)});
  return c * ${f(dark)}; }`;
}
// fxWoods in JS (single precision, as the shader's), for what stands on the land: m metres -> 0..1
const f32 = Math.fround, fr = x => f32(x - Math.floor(x));
function woodsHash(x, y) { let a = fr(f32(x * f32(.1031))), b = fr(f32(y * f32(.1031))), c = fr(f32(x * f32(.1031)));
  const d = f32(f32(a * f32(b + f32(33.33))) + f32(f32(b * f32(c + f32(33.33))) + f32(c * f32(a + f32(33.33)))));
  a = f32(a + d); b = f32(b + d); c = f32(c + d); return fr(f32(f32(a + b) * c)); }
function woodsNoise(x, y) { const i = Math.floor(x), j = Math.floor(y); let u = x - i, v = y - j; u = u * u * (3 - 2 * u); v = v * v * (3 - 2 * v);
  const a = woodsHash(i, j), b = woodsHash(i + 1, j), c = woodsHash(i, j + 1), d = woodsHash(i + 1, j + 1);
  return (a + (b - a) * u) + ((c + (d - c) * u) - (a + (b - a) * u)) * v; }
export function woodsAt(mx, mz, lo = .62, hi = .7) { return THREE.MathUtils.smoothstep(woodsNoise(mx / 520, mz / 520) * .7 + woodsNoise(mx / 110, mz / 110) * .3, lo, hi); }

// ---------------------------------------------------------------- trees
// where something stands, seen from above round a centre: an orthographic render of the meshes' tops into a float target -> a test
// (x, z) -> true where the ground is open within r of it (trees go only there: the open land, the gardens and courtyards, not a street)
export function openTest(renderer, meshes, cx, cz, R, r) {
  const N = 2048, rt = new THREE.WebGLRenderTarget(N, N, { type: THREE.FloatType, depthBuffer: true });
  const mat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
    vertexShader: 'void main(){ gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.); }',
    fragmentShader: 'void main(){ gl_FragColor = vec4(1.); }' });
  const sc = new THREE.Scene();
  for (const m of meshes) { const o = new THREE.Mesh(m.geometry, mat); o.matrixAutoUpdate = false; o.matrix.copy(m.matrixWorld); o.frustumCulled = false; sc.add(o); }
  const cam = new THREE.OrthographicCamera(-R, R, R, -R, 1e-5, 50); cam.position.set(cx, 20, cz); cam.up.set(0, 0, -1); cam.lookAt(cx, 0, cz);
  const c0 = new THREE.Color(); renderer.getClearColor(c0); const a0 = renderer.getClearAlpha(), rt0 = renderer.getRenderTarget();
  renderer.setRenderTarget(rt); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(sc, cam);
  const px = new Float32Array(N * N * 4); renderer.readRenderTargetPixels(rt, 0, 0, N, N, px);
  renderer.setRenderTarget(rt0); renderer.setClearColor(c0, a0); rt.dispose(); mat.dispose();
  const cov = (x, z) => { const i = Math.floor((x - cx + R) / (2 * R) * N), j = Math.floor((cz + R - z) / (2 * R) * N); return i < 0 || j < 0 || i >= N || j >= N || px[(j * N + i) * 4 + 3] > .5; };
  return (x, z) => { if (cov(x, z)) return false; for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; if (cov(x + Math.cos(a) * r, z + Math.sin(a) * r)) return false; } return true; };
}

// trees: round crowns and (by T.cypress) tall narrow cypresses, in groves and alone, on the open land and in the city's gardens;
// with fx land, also standing close in the land's woods (T.woods(x, z): 0..1, the ground's own woods, woodsFn). T: size, keep
// (the share of places kept), dark (lightness), layer (the look's), tone ('mini': greens; 'film': the white model's pale sage)
export function plantTrees(scene, renderer, sources, U, PW, PD, centre, R, count, scale, T) {
  const open = openTest(renderer, sources, centre.x, centre.z, R, 4.5 * scale);
  const img = U.uWater.value && U.uWater.value.image; let wpx = null, ww = 0, wh = 0;
  if (img) { const cv = document.createElement('canvas'); cv.width = ww = img.width; cv.height = wh = img.height; const g = cv.getContext('2d'); g.drawImage(img, 0, 0); wpx = g.getImageData(0, 0, ww, wh).data; }
  const wet = (x, z) => { if (!wpx) return false; const u = Math.floor((x / PW + .5) * ww), v = Math.floor((z / PD + .5) * wh); return u < 0 || v < 0 || u >= ww || v >= wh || wpx[(v * ww + u) * 4] > 90; };
  const h = 11 * scale, r = 3.8 * scale;
  const kinds = [
    { crown: new THREE.IcosahedronGeometry(r, 1).scale(1, .85, 1).translate(0, h * .62, 0), trunk: new THREE.CylinderGeometry(r * .16, r * .2, h * .45, 5).translate(0, h * .22, 0), hue: [.2, .09], l: [.24, .1] },
    { crown: new THREE.ConeGeometry(r * .42, h * 1.25, 7).translate(0, h * .72, 0), trunk: new THREE.CylinderGeometry(r * .1, r * .12, h * .2, 5).translate(0, h * .1, 0), hue: [.27, .05], l: [.18, .06] },
  ];
  const film = T.tone === 'film', tm = new THREE.MeshStandardMaterial({ color: film ? '#b5ae9f' : '#6b5440', roughness: 1 }), out = [];
  const M = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), p = new THREE.Vector3(), col = new THREE.Color(), up = new THREE.Vector3(0, 1, 0);
  const ins = kinds.map(k => { const ic = new THREE.InstancedMesh(k.crown, new THREE.MeshStandardMaterial({ roughness: .95, flatShading: true }), count), it = new THREE.InstancedMesh(k.trunk, tm, count); ic.count = it.count = 0; return [ic, it]; });
  for (let tries = 0, n = 0; n < count && tries < count * 10; tries++) {
    const a = Math.random() * Math.PI * 2, d = R * Math.sqrt(Math.random()), x = centre.x + Math.cos(a) * d, z = centre.z + Math.sin(a) * d;
    if (Math.abs(x) > PW / 2 || Math.abs(z) > PD / 2) continue;
    const grove = Math.sin(x * 900 + Math.sin(z * 400) * 2) * Math.sin(z * 700 + Math.sin(x * 300) * 2) > .2 || Math.random() < .07;   // in groves, a few alone
    const inWood = T.woods && Math.random() < T.woods(x, z) * (T.wood ?? .9);
    if ((!inWood && (!grove || Math.random() > T.keep)) || wet(x, z) || !open(x, z) || (T.clear && !T.clear(x, z))) continue;   // (T.clear: where the look keeps trees off, a city wall's band, a gate's approach)
    const ki = Math.random() < T.cypress ? 1 : 0, k = kinds[ki], [ic, it] = ins[ki], y = T.ground ? T.ground(x, z) : 0, sc = (.7 + Math.random() * .7) * T.size;
    M.compose(p.set(x, y, z), q.setFromAxisAngle(up, Math.random() * 6.28), s.set(sc, sc * (.85 + Math.random() * .4), sc));
    ic.setMatrixAt(ic.count, M); it.setMatrixAt(it.count, M); ic.setColorAt(ic.count, film ? col.setHSL(.2 + Math.random() * .07, .1 + Math.random() * .08, .72 + Math.random() * .12) : col.setHSL(k.hue[0] + Math.random() * k.hue[1], .32 + Math.random() * .16, (k.l[0] + Math.random() * k.l[1]) * T.dark));
    ic.count++; it.count++; n++;
  }
  for (const pair of ins) for (const o of pair) { o.castShadow = o.receiveShadow = true; o.layers.set(T.layer ?? 1); o.frustumCulled = false; scene.add(o); out.push(o); }
  return out;
}

// trees round where the eye looks, planted again when it moves away or the shot's distance changes much (trees made for a far
// first view lay thinly over the whole plate). update(target, d, sources): sources the meshes trees keep clear of
export function treeField(scene, renderer, U, PW, PD, scale, T) {
  let objs = null, at = null, dAt = 1;
  return { objs: () => objs, reset() { at = null; },
    update(target, d, sources) {
      if (at && at.distanceTo(target) <= d * .3 && Math.abs(Math.log(d / dAt)) <= .4) return;
      if (objs) for (const o of objs) { scene.remove(o); o.dispose(); }
      objs = plantTrees(scene, renderer, sources, U, PW, PD, target, d * 2.2, 90000, scale, T); at = target.clone(); dAt = d; } };
}
// the land's woods where trees stand close (fx land): its patches, and the slopes past its scrub (the shader's: landGLSL)
export function woodsFn(o, ex, scale, ground, relief) {
  const [s0, s1] = landSlopes(o, ex), h = 30 * scale, [lo, hi] = o.source === 'fields' ? [.62, .7] : [.56, .76];
  return (x, z) => { const sx = (ground(x + h, z) - ground(x - h, z)) / (2 * h), sz = (ground(x, z + h) - ground(x, z - h)) / (2 * h);
    return Math.max(woodsAt(x / scale, z / scale, lo, hi), relief ? THREE.MathUtils.smoothstep(Math.hypot(sx, sz), s0, s1) : 0); };
}

// ---------------------------------------------------------------- the sky
// a dome round the eye: the horizon's colour at the horizon and below, the zenith's above, brighter toward the sun's bearing;
// the haze (post.js) takes the same horizon, so far land fades into the sky with no seam. Drawn behind everything
export const SKY_GLSL = /* glsl */`
vec3 fxSky(vec3 d, vec3 hor, vec3 zen, vec3 sunC, vec3 sunD){
  float up = max(d.y, 0.), side = dot(normalize(d.xz + 1e-5), normalize(sunD.xz + 1e-5)) * .5 + .5;
  vec3 h = hor + sunC * pow(max(side, 1e-4), 3.) * .6;
  vec3 c = mix(h, zen, pow(max(up, 1e-4), .4));
  c += sunC * pow(max(dot(d, normalize(sunD)), 1e-4), 12.) * .5 * (1. - up);
  return c;
}`;
export function makeSky(cols) {
  const u = { uHor: { value: new THREE.Color(cols.horizon) }, uZen: { value: new THREE.Color(cols.zenith) }, uSunC: { value: new THREE.Color(cols.sun) },
    uSunD: { value: new THREE.Vector3(0, .3, 1) }, uI: { value: 1 } };
  const m = new THREE.ShaderMaterial({ uniforms: u, side: THREE.BackSide, depthWrite: false, fog: false,
    vertexShader: 'varying vec3 vD; void main(){ vD = normalize(position); vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.); gl_Position = p.xyww; }',
    fragmentShader: `varying vec3 vD; uniform vec3 uHor, uZen, uSunC, uSunD; uniform float uI;\n${SKY_GLSL}\nvoid main(){ gl_FragColor = vec4(fxSky(normalize(vD), uHor, uZen, uSunC, uSunD) * uI, 1.); }` });
  const sky = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), m);
  sky.frustumCulled = false; sky.renderOrder = -10;   // (each look its own sky, on its own layer)
  sky.onBeforeRender = (r, s, cam) => { sky.position.copy(cam.position); sky.scale.setScalar(cam.far * .9); sky.updateMatrixWorld(); };
  return { mesh: sky, u };
}

// ---------------------------------------------------------------- depth of field
// stronger than the film's own (main.js lens: the aperture by the shot's distance): its aperture k times, its largest blur `max`
// and a sharp band round the focus as deep as a share of its distance, deeper in a wide shot (a miniature lens: the subject
// sharp, what is well nearer and farther blurred), d: the shot's distance
export function fxLens(dof, o, d) { dof.aper *= o.k; dof.maxCoc = Math.max(dof.maxCoc, o.max); dof.band = THREE.MathUtils.lerp(o.band[0], o.band[1], THREE.MathUtils.smoothstep(d, .03, .35)); }
// ambient occlusion's reach (model units) for a shot d away: 2 % of it, kept between 8 and 40 m at 1:10000, a building's scale
// (a reach of hundreds of metres in a wide shot drew long dark smudges from each tall building across the ground)
export const fxAoRadius = d => Math.min(.004, Math.max(.0008, d * .02));

// ---------------------------------------------------------------- light that moves
// (every pow in these shaders has its base kept above 0: on some graphics pow(0, e) is NaN, not 0, and the bloom spreads it into a black square)
// drawn in both looks (the miniature draws layer 1 alone); a mesh of light also on layer 2, its own depth for the depth of field
// (post.js); every light on layer 3, drawn on its own after the haze where the haze is on (post.js); no ambient occlusion from light
const both = o => { o.layers.enable(1); o.layers.enable(3); if (o.isMesh) o.layers.enable(2); o.userData.fxGlow = true; return o; };
// a glowing line's material (a beam: studio addRoute): a hot near-white core, the line's colour round it, a head of light where it
// is drawing, and comets of light running along it (spaced `gap` model units, `speed` units a second). halo: the wide soft glow
// round the core, drawn as a second, wider tube
export function glowLineMaterial(col, w0, len, LREF, LKMIN, uNow, halo = false) {
  const u = { uProg: { value: 0 }, uA: { value: 0 }, uCol: { value: new THREE.Color(col) }, uNow, uW0: { value: w0 }, uRef: { value: LREF }, uKmin: { value: LKMIN },
    uLen: { value: len }, uGap: { value: Math.max(.03, len / 9) }, uSpeed: { value: Math.max(.08, len / 3.5) } };
  return { u, mat: new THREE.ShaderMaterial({ uniforms: u, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `uniform float uW0, uRef, uKmin; varying vec2 vUv; varying float vF;
      void main(){ vUv = uv; vec3 c = position - normal * uW0; vec4 wc = modelMatrix * vec4(c, 1.); float dc = distance(cameraPosition, wc.xyz);
        float r = max(uW0 * clamp(dc / uRef, uKmin, 1.), dc / projectionMatrix[1][1] * ${halo ? '16.' : '3.2'} / 1080.);   // (at least ${halo ? '8' : '1.6'} px of a 1080 picture: a line still reads, hot core and wide halo, in a wide shot)
        vec4 wp = modelMatrix * vec4(c + normal * r, 1.);
        vF = abs(dot(normalize(mat3(modelMatrix) * normal), normalize(cameraPosition - wp.xyz)));
        gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform float uProg, uA, uNow, uLen, uGap, uSpeed; uniform vec3 uCol; varying vec2 vUv; varying float vF;
      void main(){ float x = vUv.x; if (x > uProg) discard;
        float hq = (uProg - x) * uLen / .012, head = exp(-hq * hq);
        float u = fract((x * uLen - uNow * uSpeed) / uGap), comet = pow(max(u, 1e-4), uGap / .035) * smoothstep(1., .985, u) * step(.02, x) ;
        ${halo
          ? 'float a = pow(max(vF, 1e-4), 1.8); gl_FragColor = vec4(uCol * a * (.6 + 1.5 * comet + 1.4 * head) * uA, 1.);'
          : 'float core = pow(max(vF, 1e-4), 4.); vec3 c = mix(uCol, vec3(1., .97, .92), core * .85) * (1.1 + 1.9 * core); gl_FragColor = vec4((c + vec3(1., .96, .9) * (3.4 * comet + 3.5 * head)) * uA, 1.);'} }` }) };
}

// a flare: a point of light seen through a lens: a hot round glow, a star of four long rays and two short, a thin horizontal streak.
// Sized in the picture (a share of its height), so it reads the same at any distance; drawn over everything
export function makeFlare(col) {
  const u = { uCol: { value: new THREE.Color(col) }, uA: { value: 0 }, uS: { value: .1 }, uAsp: { value: 16 / 9 } };
  const m = new THREE.ShaderMaterial({ uniforms: u, transparent: true, depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `uniform float uS, uAsp; varying vec2 vP; void main(){ vP = position.xy; vec4 c = projectionMatrix * modelViewMatrix * vec4(0., 0., 0., 1.);
      gl_Position = c + vec4(position.x * uS * 4. / uAsp, position.y * uS, 0., 0.) * c.w; }`,
    fragmentShader: `uniform vec3 uCol; uniform float uA; varying vec2 vP;
      void main(){ vec2 p = vP * vec2(4., 1.); float r = length(p);
        float glow = exp(-r * r * 60.) * 3. + exp(-r * 9.) * .5;
        float rays = (exp(-abs(p.y) * 260.) * exp(-abs(p.x) * 2.6) + exp(-abs(p.x) * 260.) * exp(-abs(p.y) * 3.)) * 2.;
        float diag = (exp(-abs(p.x - p.y) * 200.) + exp(-abs(p.x + p.y) * 200.)) * exp(-r * 14.) * .5;
        float streak = exp(-abs(vP.y) * 120.) * exp(-abs(vP.x) * 2.2) * .8;
        vec3 c = mix(uCol, vec3(1.), .55) * (glow + rays + diag) + uCol * streak;
        gl_FragColor = vec4(c * uA, 1.); }` });
  const mesh = both(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), m));
  mesh.frustumCulled = false; mesh.renderOrder = 20; mesh.visible = false; mesh.layers.disable(2);   // (a flare is a lens's, at no depth)
  return { mesh, u, set(p, a, size = .1) { mesh.visible = a > .003; if (!mesh.visible) return; mesh.position.copy(p); u.uA.value = a; u.uS.value = size; } };
}

// a column of light standing on the ground where a beam lands: it shoots up (a bright front climbing, ~.5 s), stands with bands
// of light rising through it and motes drifting up inside, a soft pool of light at its foot; h its height, r its core's radius
// (model units). set(p, t, a): t seconds since it landed (none before), a its alpha
export function makeColumn(col, h, r) {
  const g = new THREE.Group(); g.visible = false;
  const uT = { value: 0 }, uA = { value: 0 }, uH = { value: h }, uC = { value: new THREE.Color(col) }, uRise = { value: 1 };
  const tube = (rad, core) => new THREE.Mesh(new THREE.CylinderGeometry(rad, rad, h, 32, 1, true).translate(0, h / 2, 0), new THREE.ShaderMaterial({
    uniforms: { uT, uA, uH, uC, uRise }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: `varying float vY, vF; void main(){ vY = position.y; vec4 wp = modelMatrix * vec4(position, 1.);
      vF = abs(dot(normalize(mat3(modelMatrix) * vec3(normal.x, 0., normal.z)), normalize(cameraPosition - wp.xyz))); gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform float uT, uA, uH, uRise; uniform vec3 uC; varying float vY, vF;
      void main(){ float y = vY / uH; if (y > uRise) discard;
        float fade = pow(max(1. - y, 1e-4), 1.6) * smoothstep(0., .02, y);
        float fq = (uRise - y) / .03, front = exp(-fq * fq) * step(uRise, .999);
        float bands = .55 + .45 * smoothstep(.55, 1., sin(y * 38. - uT * 7.));
        ${core ? 'float c = pow(max(vF, 1e-4), 3.); vec3 k = mix(uC, vec3(1., .97, .92), c * .8) * (1.2 + 2.4 * c) * bands;'
               : 'float c = pow(max(vF, 1e-4), 1.6); vec3 k = uC * c * .45 * (.6 + .4 * bands);'}
        gl_FragColor = vec4((k * fade + vec3(1., .95, .85) * front * ${core ? '3.' : '.25'} * c) * uA, 1.); }` }));   // (the rising front: bright in the core, faint in the halo, not a cap)
  const core = tube(r, true), halo = tube(r * 3.5, false);
  // the pool of light at its foot, and a ring that runs out from it at the landing
  const pool = new THREE.Mesh(new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2), new THREE.ShaderMaterial({ uniforms: { uT, uA, uC }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: 'varying vec2 vP; void main(){ vP = position.xz * 2.; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }',
    fragmentShader: `uniform float uT, uA; uniform vec3 uC; varying vec2 vP;
      void main(){ float d = length(vP); float pool = exp(-d * d * 18.) * .9 + exp(-d * 6.) * .25;
        float R = .9 * (1. - exp(-uT * 2.2)), q = (d - R) / .025, ring = exp(-q * q) * exp(-uT * 1.4) * 1.6;   // (no pow of a negative: undefined in GLSL)
        gl_FragColor = vec4(mix(uC, vec3(1.), .4) * (pool + ring) * uA * smoothstep(1., .8, d), 1.); }` }));
  pool.scale.setScalar(h * 1.1); pool.position.y = h * .004;
  // motes rising inside it
  const NM = 160, mp = new Float32Array(NM * 3), ms = new Float32Array(NM);
  for (let i = 0; i < NM; i++) { const a = i * 2.39996, rr = r * 3.5 * Math.sqrt((i * .618) % 1); mp[i * 3] = Math.cos(a) * rr; mp[i * 3 + 2] = Math.sin(a) * rr; ms[i] = (i * .7548) % 1; }
  const mg = new THREE.BufferGeometry(); mg.setAttribute('position', new THREE.BufferAttribute(mp, 3)); mg.setAttribute('aSeed', new THREE.BufferAttribute(ms, 1));
  const motes = new THREE.Points(mg, new THREE.ShaderMaterial({ uniforms: { uT, uA, uH, uC, uRise }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute float aSeed; uniform float uT, uH, uRise; varying float vA;
      void main(){ float y = fract(aSeed + uT * (.12 + .1 * aSeed)) * uH * .8; vec3 p = position; p.y = y;
        vec4 mv = modelViewMatrix * vec4(p, 1.); gl_Position = projectionMatrix * mv;
        vA = (1. - y / uH) * step(y / uH, uRise) * (.5 + .5 * sin(uT * 3. + aSeed * 40.));
        gl_PointSize = clamp(uH * 30. / -mv.z, 1., 4.); }`,
    fragmentShader: `uniform float uA; uniform vec3 uC; varying float vA; void main(){ float d = length(gl_PointCoord - .5); gl_FragColor = vec4(mix(uC, vec3(1.), .6) * smoothstep(.5, 0., d) * vA * uA * 1.5, 1.); }` }));
  for (const m of [halo, core, pool, motes]) { both(m); m.frustumCulled = false; m.renderOrder = 7; g.add(m); }
  both(g);
  return { group: g, set(p, t, a) {
    g.visible = t >= 0 && a > .003; if (!g.visible) return;
    g.position.copy(p); uT.value = t; uA.value = a; uRise.value = Math.min(1, 1 - Math.exp(-t / .16));
  } };
}

// sparks: a burst where a beam lands, flung out and up, falling back, each cooling from white through yellow to red; drawn as
// short streaks (each spark three points along its last few hundredths of a second). s: the burst's size (model units)
export function makeSparks(col, s, n = 900) {
  const N = n * 3, seed = new Float32Array(N * 3);
  let sd = 7; const rnd = () => { sd = (sd * 16807) % 2147483647; return sd / 2147483647; };
  for (let i = 0; i < n; i++) { const a = rnd() * 6.2832, up = .35 + rnd() * .9, sp = .35 + rnd() * .65, life = .7 + rnd() * 1.1;
    for (let k = 0; k < 3; k++) { const o = (i * 3 + k) * 3; seed[o] = a; seed[o + 1] = up * sp; seed[o + 2] = k * 10 + life; } }   // (z: its trail index times 10, plus its life in seconds)
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3)); g.setAttribute('aS', new THREE.BufferAttribute(seed, 3));
  const u = { uT: { value: -1 }, uA: { value: 0 }, uSz: { value: s }, uC: { value: new THREE.Color(col) } };
  const pts = both(new THREE.Points(g, new THREE.ShaderMaterial({ uniforms: u, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute vec3 aS; uniform float uT, uSz; varying float vK, vA;
      void main(){ float tr = floor(aS.z / 10.), life = aS.z - tr * 10.;
        float t = max(uT - tr * .022, 0.); float k = t / life;
        float out_ = (1. - exp(-t * 3.)) * (1. - aS.y * .4); vec3 p = vec3(cos(aS.x) * out_, aS.y * 3.2 * t - 1.6 * t * t, sin(aS.x) * out_) * uSz;
        p.y = max(p.y, 0.);
        vec4 mv = modelViewMatrix * vec4(p, 1.); gl_Position = projectionMatrix * mv;
        vK = k; vA = step(k, 1.) * step(0., uT) * (1. - tr * .3) * (1. - k);
        gl_PointSize = clamp(uSz * 60. / -mv.z, 1.5, 5.); }`,
    fragmentShader: `uniform float uA; uniform vec3 uC; varying float vK, vA;
      void main(){ float d = length(gl_PointCoord - .5); vec3 c = mix(vec3(1., .97, .85), mix(uC, vec3(.9, .25, .06), smoothstep(.4, 1., vK)), smoothstep(0., .35, vK));
        gl_FragColor = vec4(c * smoothstep(.5, .1, d) * vA * uA * 2.2, 1.); }` })));
  pts.frustumCulled = false; pts.renderOrder = 8; pts.visible = false;
  return { points: pts, set(p, t, a) { pts.visible = t >= 0 && t < 2.2 && a > .003; if (!pts.visible) return; pts.position.copy(p); u.uT.value = t; u.uA.value = a; } };
}

// where a beam lands, all three together: the column, its flare, its sparks (whichever the settings keep); set(p, t, a)
export function makeLanding(scene, col, size, o) {
  const parts = [];
  if (o.column) { const c = makeColumn(col, size, size * .01); scene.add(c.group); parts.push((p, t, a) => c.set(p, t, a)); }
  if (o.sparks) { const s = makeSparks(col, size * .22); scene.add(s.points); parts.push((p, t, a) => s.set(p, t, a)); }
  if (o.flare) { const f = makeFlare(col), q = new THREE.Vector3(); scene.add(f.mesh);
    parts.push((p, t, a) => f.set(q.copy(p).setY(p.y + size * .01), t < 0 ? 0 : a * (.35 + 1.4 * Math.exp(-t / .35)), .06 + .08 * Math.exp(-t / .5))); }
  return { set(p, t, a) { for (const f of parts) f(p, t, a); } };
}
