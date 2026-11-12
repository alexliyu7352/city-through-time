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
// the parts (pipeline/citygen.py): FAB 0, LMK 1, WALL 2, BRIDGE 3, TREE 4, WATER 5, DARK 6, PAVE 7, ROOF 8, LROOF 9, EARTH 10, PLINTH 11.
// A house (FAB walls, ROOF) takes one of the walls and one of the roofs by its building's centre; the other parts their colour.
// land: the fields' greens and straw (fx.js LAND_PALETTES, the white model's land under fx land too); glb: a detailed model's materials (tools/blender/kit.py); cypress: the share of tall
// narrow trees; detail: the colours of the pieces engine/detail.js puts on the houses and walls (its kinds), in the palette's region's way (detail.js STYLES);
// faces: a city wall's colour by what it is faced with (detail.js WALL_FACES), its courses a shade darker (a stone wall's bands of brick)
const PALETTES = {
  roman: {
    walls: ['#ebe1cc', '#e8d4ab', '#ddc196', '#f1eadc', '#e4c9b0', '#d6b78f', '#efdcc0'],
    roofs: ['#b65c3d', '#c26d45', '#a95d47', '#c47d57', '#a05848', '#ba684b', '#c98a63'],
    parts: { 1: '#e6dcc8', 2: '#cdb38c', 3: '#cbbd9f', 4: '#5a7340', 5: '#4f8aa3', 6: '#2f2620', 7: '#d6caae', 9: '#a65d45', 10: '#c9b086', 11: '#bcae92' },
    land: LAND_PALETTES.mediterranean,
    glb: { stone: '#e8dfcc', dark: '#2b231d', roof: '#a85b43', sand: '#d2b98c' }, cypress: .3,
    detail: { window: '#33281f', door: '#4b3323', cornice: '#f4eee2', base: '#b9a588', coping: '#b0603f', archRing: '#ebe3d2', flags: ['#a3262a', '#6e2a63'], sail: '#efe6d2' },
    faces: { earth: '#c9ad86', brick: '#b8805c', stone: '#ddd3c0', banded: '#e6dbc6' },
  },
  chinese: {
    walls: ['#ddcca8', '#d4bd94', '#e6d8bb', '#cdb38c', '#e0cfae'],
    roofs: ['#6c6863', '#78726b', '#625f5b', '#7f7970', '#5c5854'],
    parts: { 1: '#e2d5b8', 2: '#bfa070', 3: '#cbbd9f', 4: '#5f7d3c', 5: '#5d8fa8', 6: '#2f2620', 7: '#d8cbaa', 9: '#5d5955', 10: '#c9a978', 11: '#b8a58a' },
    land: LAND_PALETTES.loess,   // the loess plain: wheat, millet, bare earth
    glb: { stone: '#e3d6b8', dark: '#2b231d', roof: '#5f5b56', sand: '#c8a676' }, cypress: .08, tree: { size: .6, keep: .35, dark: .78 },   // (tree: its size, the share of places kept, its lightness)
    detail: { base: '#97918a', post: '#7a3524', beam: '#4e3b2e', ridgeEnd: '#4f4b47', coping: '#5b5853', archRing: '#8f8b85', column: '#8a2e20', flags: ['#b3262c', '#d9a21b'], sail: '#a8764a' },
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
function colourMesh(mesh, pal, detail, wall, trees = null) {
  const g = mesh.geometry, d = g.attributes.aData, c = g.attributes.aCtr, n = g.attributes.position.count, out = new Float32Array(n * 3), col = new THREE.Color(), P = g.attributes.position;
  const walls = pal.walls.map(v => new THREE.Color(v)), roofs = pal.roofs.map(v => new THREE.Color(v)), gable = detail ? gableEnds(g) : new Uint8Array(n);
  const parts = Object.fromEntries(Object.entries(pal.parts).map(([k, v]) => [k, new THREE.Color(v)]));
  const faces = detail && pal.faces ? Object.fromEntries(Object.entries(pal.faces).map(([k, v]) => [k, new THREE.Color(v)])) : null, N = g.attributes.normal;
  const faceAt = i => { if (wall.face) return faces[wall.face]; const ny = Math.abs(N.getY(i - i % 3) + N.getY(i - i % 3 + 1) + N.getY(i - i % 3 + 2)) / 3; return faces[ny > .02 && ny < .9 ? 'earth' : wall.upright]; };
  for (let i = 0; i < n; i++) {
    const part = d ? Math.round(d.getY(i)) : 0, h = c ? hash(c.getX(i), c.getY(i)) : .5, h2 = (h * 7.31) % 1, h3 = (h * 13.7) % 1;
    if (part === 0 || gable[i]) col.copy(walls[Math.floor(h * walls.length)]);
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
function colourToday(mesh, T = TODAY.roman) {
  const g = mesh.geometry, d = g.attributes.aData, nrm = g.attributes.normal, n = g.attributes.position.count, out = new Float32Array(n * 3), col = new THREE.Color();
  const C = a => a.map(c => new THREE.Color(c)), roofs = C(T.roofs), flats = C(T.flat), walls = C(T.walls), tall = C(T.tall);
  for (let i = 0; i < n; i++) {
    const h = d.getZ(i), hm = d.getY(i), top = nrm.getY(i) > .6, mound = d.getW(i) > .5;
    if (mound) col.set('#9a8f6a');
    else if (top) col.copy(hm > 24 || h < T.flatShare ? flats[Math.floor(h * 41) % flats.length] : roofs[Math.floor(h * 97) % roofs.length]);
    else col.copy(hm > 30 ? tall[Math.floor(h * 31) % tall.length] : walls[Math.floor(h * 53) % walls.length]);
    const k = .9 + .2 * ((h * 7.13) % 1); out[i * 3] = col.r * k; out[i * 3 + 1] = col.g * k; out[i * 3 + 2] = col.b * k;
  }
  g.setAttribute('color', new THREE.BufferAttribute(out, 3));
  return new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .92, metalness: 0 });
}

// the land: fx.js's (a patchwork of fields, straw and bare earth, woods in patches and, with the relief, on the slopes: the white
// model's land under fx land is the same code, muted); the water (the studio's water map) turquoise in the shallows and deeper blue
// away from the shore, with the sun's glint. o: the land's settings (fx land, else the palette's fields alone, no woods).
// S (the film): the fields calming with distance into the same land's soft large areas (fx.js 'quiet': a patchwork seen from
// afar read as rags sewn together; a close shot keeps its fields), the water as it was (the studio's wThen), the plate lowered in
// a dug pool (the studio's deformation); far: the land beyond the plate (no water, no pools)
function landMaterial(U, PW, PD, kind, land, relief, o, ex, scale, S = null, far = false) {
  const m = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .97, metalness: 0, side: far ? THREE.DoubleSide : THREE.FrontSide });
  const then = !!(S && S.wThenGLSL && !far), wr = then ? 'wThen(vXZ / uPlateM + .5, vXZ)' : far ? '0.' : 'texture2D(uWaterM, vXZ / uPlateM + .5).r';
  m.onBeforeCompile = sh => {
    sh.uniforms.uWaterM = U.uWater; sh.uniforms.uPlateM = { value: new THREE.Vector2(PW, PD) }; sh.uniforms.uKind = { value: kind === 'modern' ? 1 : 0 };
    if (then) for (const k of ['uWater', 'uWT', 'uWTF', 'uWTE']) sh.uniforms[k] = U[k];
    if (relief) { for (const k of ['uFxHgt', 'uFxRect', 'uFxSun', 'uFxR', 'uFxRA', 'uFxLitC', 'uFxShadeC', 'uFxFlat']) sh.uniforms[k] = U[k]; sh.uniforms.uFxAdd = { value: 0 }; }   // (a bright ground: no light added on top)
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vXZ; varying vec3 vFxW;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvXZ = (modelMatrix * vec4(position, 1.)).xz; vFxW = (modelMatrix * vec4(transformed, 1.)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec2 vXZ; varying vec3 vFxW; uniform sampler2D uWaterM; uniform vec2 uPlateM; uniform float uKind;${relief ? RELIEF_GLSL : ''}${landLookGLSL(land, relief, o || null, ex, scale, 'mini')}${S ? farLandGLSL(land) : ''}${then ? '\nuniform sampler2D uWater;' + S.wThenGLSL : ''}`)
      .replace('#include <color_fragment>', `#include <color_fragment>${S ? '\n// (look: mini)' : ''}
  vec2 m_ = vXZ / ${scale.toFixed(6)};   // metres
  float wr_ = ${wr}, wMask = smoothstep(.35, .65, wr_);
{ vec3 land = fxLandAt(vFxW);${S ? `
  land = mix(land, fxLandFar(m_), smoothstep(1.2, 5., length(fwidth(m_))));   // (afar: the fields calm into soft large areas once one is under about 40 pixels of the drawn picture, gone by about 12)
  land = mix(vec3(dot(land, vec3(.2126, .7152, .0722))), land, 1.05) * vec3(.92, 1.06, .95) * 1.14;   // (the film's land lighter and cleaner, a little greener: a sunlit model's, not a murky olive ground)` : ''}
  if (uKind > .5) land = mix(land, vec3(.29, .27, .23), .55);   // a city's ground: paved, dusty
  float deep = smoothstep(.4, .98, wr_);
  vec3 water = mix(vec3(.38, .68, .70), vec3(.17, .42, .56), deep) * (.95 + .1 * fxLn(m_ / 40.));
  diffuseColor.rgb = mix(land, pow(water, vec3(2.2)), wMask); }`)   // (the water's colours are sRGB; the shading is linear)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = mix(roughnessFactor, .32, wMask);')
      .replace('#include <opaque_fragment>', `${relief ? 'outgoingLight = mix(outgoingLight, fxReliefLight(vFxW, outgoingLight, diffuseColor.rgb), 1. - wMask);   // the relief (fx.js)\n' : ''}#include <opaque_fragment>`);
  };
  m.customProgramCacheKey = () => 'mini-land' + (relief ? ' fx' : '') + (o ? ' land' : '') + (S ? ' film' : '') + (then ? ' then' : '') + (far ? ' far' : '');
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

// the colour film's land seen from afar (landMaterial S): the palette's grass and earth in a few soft areas kilometres wide, clean,
// no grain (the fields' patchwork read from afar as rags sewn together, a finer noise in its place as smudged felt)
function farLandGLSL(p) {
  const v3 = a => `vec3(${a.map(x => x.toFixed(3)).join(', ')})`;
  return `
vec3 fxLandFar(vec2 m){ float n1 = fxLn(m / 3200.), n2 = fxLn(m / 1400. + 3.1);
  vec3 g = mix(${v3(p.grass0)}, ${v3(p.grass1)}, .35 + .5 * smoothstep(.25, .75, n2)), e = mix(${v3(p.straw)}, ${v3(p.soil)}, .3);
  return pow(mix(g, e, smoothstep(.45, .8, n1) * .3), vec3(2.2)); }`;
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
export function miniLook({ S, cityMesh, scale, lens = null, palette = 'roman', ground = 'land', card = null, prims = null, hex = () => 2, face = () => null, film = false, lost = null,
  paletteOf = () => palette, today = null, fadeAt = .8, phone = false }) {   // (phone: the film on a phone, main.js: no ambient occlusion, a smaller shadow map; the caller leaves the detail out)
  const { scene, camera, renderer, U } = S, PW = S.PW, PD = S.PD;
  const pal = PALETTES[palette] || PALETTES.roman, palOf = id => PALETTES[paletteOf(id)] || pal;
  // the meshes this look draws: the period cities, today's city, the plate
  const eraMeshes = Object.values(S.eras).map(e => e.mesh);
  let plate = null;
  scene.traverse(o => { if (o.isMesh && o.material && o.material.customProgramCacheKey && /^proj1/.test(o.material.customProgramCacheKey()) && o.geometry.attributes.position.count > 1000) plate = o; });
  const FX = S.fx, relief = !!(FX && FX.relief && U.uFxRA && U.uFxRA.value);   // the effects (fx.js), as the studio has them
  if (plate) plate.userData.mini = landMaterial(U, PW, PD, ground, FX && FX.land ? landPalette(FX.land) : pal.land, relief, FX && FX.land, S.terrainEx, scale, film ? S : null);
  U.__ground = S.ground;
  // the film: the ruins' uniforms (filmMaterial; main.js sets their values each frame), the land beyond the plate (its context relief,
  // else a skirt of land to the horizon), the light the studio lays on the plate (S.colourLight: more of it at night)
  const RUIN_T = { value: Array(S.slots).fill(-1) };
  if (film) for (const [id, E] of Object.entries(S.eras)) Object.assign(E.u, { uRuinLater: { value: Array(S.slots).fill(0) }, uRuinT: RUIN_T, uRuinH: { value: 1.4 * hex(id) * scale },
    uLossBurnt: { value: Array(E.u.uLossBurn.value.length).fill(0) } });
  if (film) S.colourGround.value.set(pal.parts[7]);   // (a city's open ground in its paving's colour: studio.js lightMaterial ground)
  const far = film ? landMaterial(U, PW, PD, 'land', FX && FX.land ? landPalette(FX.land) : pal.land, false, FX && FX.land, S.terrainEx, scale, S, true) : null;
  const ctx = film ? S.context() : null, skirt = film ? skirtMesh(S, far, ctx) : null, marks = film && plate ? marksMesh(S, plate) : null;
  // the land's woods where trees stand close (fx land: fx.js woodsFn)
  const woods = FX && FX.land ? woodsFn(FX.land, S.terrainEx, scale, S.ground, relief) : null;
  // the light of a clear day: the sun to one side behind the eye, 40 degrees up, soft shadows; the sky's blue from above, the land's from below
  // (fx light: a lower, warmer sun, as in the late afternoon, as bright on flat ground as the higher one; the sky's light a little bluer)
  const warm = FX && FX.light ? FX.light.warm : 0, SUN_EL = THREE.MathUtils.lerp(40, 28, warm), SUN_SIDE = relief ? 95 : 55;   // (fx relief: the sun more to the side, so the slopes facing the eye show light and shade)
  const sun = new THREE.DirectionalLight(new THREE.Color('#ffeed4').lerp(new THREE.Color('#ffd09a'), warm), 2.7 * (FX ? MINI_LIFT.sun : 1) * Math.sin(THREE.MathUtils.degToRad(40)) / Math.sin(THREE.MathUtils.degToRad(SUN_EL))), sky = new THREE.HemisphereLight(new THREE.Color('#c3d8ee').lerp(new THREE.Color('#a9c4ea'), warm), '#6b7550', .9 * (FX ? MINI_LIFT.sky : 1));
  sun.castShadow = true; sun.shadow.mapSize.set(phone ? 2048 : 4096, phone ? 2048 : 4096); sun.shadow.bias = -.0004; sun.shadow.normalBias = .00002; sun.shadow.radius = 2;
  for (const o of [sun, sun.target, sky]) { o.layers.set(L); scene.add(o); }
  const bg = new THREE.Color('#c4d8ea'), fog = new THREE.Fog('#cfdde8', 1, 3), FOG = fog.color.clone(), SUN0 = sun.intensity, SKY0 = sky.intensity;
  const NIGHT = { bg: new THREE.Color('#16223a'), fog: new THREE.Color('#1c2a44'), sun: new THREE.Color('#9fb4e0') }, SUNC = sun.color.clone(), bgNow = bg.clone();   // (the film at night: film.night)
  const PALL = { sun: new THREE.Color('#ffb070'), sky: new THREE.Color('#8f8273') };   // (under a burning city's smoke)
  const landmarks = [];   // detailed models drawn in place of the generator's (swap)
  // each period city's detail (engine/detail.js), made the first time it is shown: era id -> a promise of its group
  const DET = prims ? new Map() : null;
  const colsOf = pal => {   // the detail's colours in a palette
    const dcols = { ...(pal.detail || PALETTES.roman.detail), tile: (x, z) => roofOf(pal, x, z).multiplyScalar(FLAT.tile), verge: (x, z) => roofOf(pal, x, z).multiplyScalar(FLAT.verge) };   // (a roof's tiles in its own colour, lighter, its gable ridges darker: detail.js FLAT)
    for (const [f, v] of Object.entries(pal.faces || PALETTES.roman.faces)) {   // (a wall's face: its courses a shade darker, a stone wall's bands brick; a gate's parts the wall's)
      dcols['course_' + f] = f === 'banded' ? (pal.faces || PALETTES.roman.faces).brick : new THREE.Color(v).multiplyScalar(FLAT.course);
      dcols['spandrel_' + f] = dcols['parapet_' + f] = dcols['merlon_' + f] = v; }
    // the town's trees as the land's (fx.js plantTrees' colours), flags in the palette's colours (one or the other by the flag's
    // building), the boats' wood, sails and mat roofs
    const tdark = (pal.tree && pal.tree.dark) || 1, H3 = (x, z) => { const h = hash(x, z); return [h, (h * 7.31) % 1, (h * 13.7) % 1]; }, D_ = pal.detail || PALETTES.roman.detail;
    Object.assign(dcols, { crown: (x, z) => { const [a, b, c] = H3(x, z); return new THREE.Color().setHSL(.2 + a * .09, .32 + b * .16, (.24 + c * .1) * tdark); },
      cone: (x, z) => { const [a, , c] = H3(x, z); return new THREE.Color().setHSL(.27 + a * .05, .4, (.18 + c * .06) * tdark); }, trunk: '#6b5440', pole: '#5b4a3a',
      flag: (x, z) => new THREE.Color(D_.flags[Math.floor(H3(x, z)[1] * D_.flags.length)]), hull: '#7a5236', mast: '#5b4a3a', sail: D_.sail, cabin: '#4a4038' });
    return dcols; };
  const dcols = colsOf(pal), DCOLS = new Map([[pal, dcols]]), dcolsOf = p => DCOLS.get(p) || DCOLS.set(p, colsOf(p)).get(p);
  const pxK = { value: 1 }, idOf = new Map(Object.entries(S.eras).map(([id, E]) => [E.mesh, id])), uprightOf = id => (STYLES[paletteOf(id)] || STYLES[palette] || STYLES.roman).wall;   // (the fade's scale: detail.js FADE_PX)
  // (the film: each piece rises and falls with its building, and burns away as its building chars: filmMaterial)
  const riseOf = async id => { if (!film) return null; const lo = lost ? await lost(id) : null, u = S.eras[id].u, nL = u.uLossBurn.value.length, fire = S.fires[id] && S.fires[id].day ? S.fires[id] : null;
    const glsl = S.eraRiseGLSL().replace('float eraRiseK(){', 'float eraRiseK0(){') + `
  uniform float uNow, uEraBurn, uLossBurn[${nL}];${fire ? ' uniform vec2 uO;' + S.fireGLSL : ''}
  float eraRiseK(){ float c = uEraBurn; for (int k = 0; k < ${nL}; k++) if (abs(iW - 4. - float(k)) < .5) c = max(c, uLossBurn[k]);${fire ? '\n    if (uEraBurn > 0.) c = smoothstep(.3, 2., uNow - ign(iCtr, fireHash(iCtr)));' : ''}
    return eraRiseK0() * (1. - c); }`;
    return { glsl, uniforms: { ...u, uNow: U.uNow, ...(fire ? { ...fire.day.F, uO: fire.u.uO } : {}) }, w: lo ? Float32Array.from(lo, v => 3 + v) : null }; };
  const detailOf = async id => { const D = eraDetail(await prims(id), { scale, hex: hex(id), style: paletteOf(id), face: face(id) }), g = detailMeshes(D, dcolsOf(palOf(id)), { layer: L, pxK, rise: await riseOf(id) });
    g.userData.count = D.count; g.userData.treeOK = D.treeOK; scene.add(g); return g; };
  // where trees may stand: off every shown city's wall bands and gate approaches (detail.js eraDetail treeOK)
  let clearNow = [];
  const TF = treeField(scene, renderer, U, PW, PD, scale, { size: 1, keep: 1, dark: 1, ...pal.tree, cypress: pal.cypress, woods, ground: S.ground, layer: L, tone: 'mini',
    clear: (x, z) => clearNow.every(f => f(x, z)) });
  // boats on the water round where the eye looks (detail.js boatsAt), planted again when it moves away, as the trees are
  let wpx = null; const water = () => { if (wpx) return wpx; const img = U.uWater.value && U.uWater.value.image; if (!img) return null;
    const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height; const g = cv.getContext('2d'); g.drawImage(img, 0, 0); return wpx = { d: g.getImageData(0, 0, img.width, img.height).data, w: img.width, h: img.height }; };
  const chan = () => film && S.wThenGLSL ? Math.round(U.uWT.value.x) : 0;   // (the film's water as it was: the state's channel, studio.js WTHEN; else today's, R)
  const wet = (x, z) => { const W_ = water(); if (!W_) return false; const u = Math.floor((x / PW + .5) * W_.w), v = Math.floor((z / PD + .5) * W_.h); return u >= 0 && v >= 0 && u < W_.w && v < W_.h && W_.d[(v * W_.w + u) * 4 + chan()] > 90; };
  const BF = { at: null, dAt: 1, g: null, ch: 0 };
  const boats = (target, d) => { if (BF.at && BF.at.distanceTo(target) <= d * .3 && Math.abs(Math.log(d / BF.dAt)) <= .4 && BF.ch === chan()) return; BF.ch = chan();
    if (BF.g) { scene.remove(BF.g); BF.g.traverse(o => { if (o.isMesh) { o.geometry.dispose(); o.material.dispose(); } }); }
    BF.g = detailMeshes(boatsAt(wet, target, d * 2.2, { scale, style: palette, ground: S.ground }), dcols, { layer: L, pxK }); scene.add(BF.g); BF.at = target.clone(); BF.dAt = d; };
  const info = card ? infoPanel(card) : null;
  // the tilt-shift: sharp in a band through the middle, blurred above and below
  // with the effects: the film's own passes (post.js: ambient occlusion, haze toward a sky dome, the stronger depth of field),
  // in place of the tilt-shift band
  // (the film: always the film's passes, its ambient occlusion from the picture's own depth: the geometry the passes would draw
  // themselves is the city as built, not as it stands at that moment)
  const FP = FX || film ? makePost(renderer, scene, camera, S.post.dof.rt.width / S.post.dof.s, S.post.dof.rt.height / S.post.dof.s,
    { ssaa: S.post.dof.s, ao: !phone, aoAmt: FX ? MINI_LIFT.ao : FILM_AO, aoDepth: film, ...S.gpu.targets, ...(FX && FX.haze ? { haze: FX_SKY.mini } : {}), ...(FX && FX.dof ? { dof2: true } : {}) }) : null;
  const dome = FX && FX.haze ? makeSky(FX_SKY.mini) : null;
  if (FP) { FP.bloom.strength = .1; FP.bloom.threshold = 2.2;   // (a bright day: only the sun's glints glow, not every lit wall)
    FP.vig.uniforms.amt.value = .22;
    if (FP.dof.haze) { const ex = S.terrainEx; FP.dof.haze.uHazeD.value = 1 / (FX.haze.dist_km * 1000 * scale * MINI_LIFT.haze); FP.dof.haze.uHazeB.value = 1 / (FX.haze.height_m * scale * ex); FP.dof.haze.uHazeK.value = FX.haze.k; FP.dof.haze.uHazeS.value = FX.haze.start_km * 1000 * scale; FP.dof.haze.uHazeRect.value.copy(S.post.dof.haze ? S.post.dof.haze.uHazeRect.value : new THREE.Vector4(-PW / 2, -PD / 2, PW / 2, PD / 2)); FP.dof.haze.uHazeRect2.value.copy(S.post.dof.haze ? S.post.dof.haze.uHazeRect2.value : FP.dof.haze.uHazeRect.value); FP.dof.haze.uHazeEdge.value = FX.haze.edge_km * 1000 * scale; } }
  if (dome) { dome.mesh.layers.set(L); scene.add(dome.mesh); }
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
  async function swap({ url, theta_deg = 0, near, r_m = 120 }) {
    const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js'), { DRACOLoader } = await import('three/addons/loaders/DRACOLoader.js');
    const map = (() => { try { return JSON.parse(document.querySelector('script[type=importmap]').textContent).imports['three/addons/']; } catch (e) { return null; } })();
    const draco = new DRACOLoader().setDecoderPath((map || 'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/') + 'libs/draco/gltf/');
    const g = await new GLTFLoader().setDRACOLoader(draco).loadAsync(url); draco.dispose();
    const votes = new Map(), r = r_m * scale;
    for (const m of eraMeshes) { if (!m.visible) continue; const P = m.geometry.attributes.position, D = m.geometry.attributes.aData, C = m.geometry.attributes.aCtr;
      for (let i = 0; i < P.count; i++) { if (Math.round(D.getY(i)) !== 1 || Math.hypot(P.getX(i) - near[0], P.getZ(i) - near[1]) > r) continue;
        const k = C.getX(i).toFixed(7) + ',' + C.getY(i).toFixed(7); votes.set(k, (votes.get(k) || 0) + 1); } }
    if (!votes.size) throw new Error(`mini: no landmark near ${near}`);
    const [key] = [...votes].sort((a, b) => b[1] - a[1])[0], [cx, cz] = key.split(',').map(Number), y0 = S.ground(cx, cz);
    let top = -Infinity, folded = 0;
    for (const m of eraMeshes) { const P = m.geometry.attributes.position, C = m.geometry.attributes.aCtr; let hit = false;
      for (let i = 0; i < P.count; i++) if (Math.abs(C.getX(i) - cx) < 2e-7 && Math.abs(C.getY(i) - cz) < 2e-7) { top = Math.max(top, P.getY(i)); P.setXYZ(i, cx, y0 - 1e-4, cz); hit = true; folded++; }
      if (hit) P.needsUpdate = true; }
    const box = new THREE.Box3().setFromObject(g.scene), H = box.max.y - Math.max(box.min.y, 0), k = THREE.MathUtils.clamp((top - y0) / (H * scale), 1, 3);
    const M = new THREE.Matrix4().makeTranslation(cx, y0, cz).multiply(new THREE.Matrix4().makeScale(scale, scale * k, scale)).multiply(new THREE.Matrix4().makeRotationY(THREE.MathUtils.degToRad(theta_deg)));
    const root = new THREE.Group(); root.matrixAutoUpdate = false; root.matrix.copy(M); root.add(g.scene);
    const mats = {};
    g.scene.traverse(o => { if (!o.isMesh) return; const nm = (o.material && o.material.name) || 'stone';
      o.material = mats[nm] ||= new THREE.MeshStandardMaterial({ color: pal.glb[nm] || pal.glb.stone, roughness: .9, metalness: 0, side: THREE.DoubleSide });
      o.castShadow = o.receiveShadow = true; o.layers.set(L); });
    scene.add(root); root.updateMatrixWorld(true); landmarks.push(root); TF.reset();
    return { centre: [cx, cz], folded, height_k: +k.toFixed(3) };
  }

  // a city's colours, made the first time it is shown (or warmed)
  function colour(m) {
    if (m.userData.mini) return; const id = idOf.get(m);
    m.userData.mini = m === cityMesh ? colourToday(m, today ? TODAY[today] : undefined) : colourMesh(m, palOf(id), !!DET, { face: face(id), upright: uprightOf(id) }, { cell: 12 * scale, dark: (palOf(id).tree && palOf(id).tree.dark) || 1 });
    if (film) { const u = m === cityMesh ? null : S.eras[id].u, ruin = m === cityMesh ? null : new THREE.Color(palOf(id).parts[11]);
      filmMaterial(S, m.userData.mini, u, ruin, fadeAt, u && S.fires[id] && S.fires[id].day ? S.fires[id] : null); m.userData.miniDepth = filmMaterial(S, new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), u, null, fadeAt); }
  }
  // the programs of every city's colours made before playback (main.js warm-up: else the first frame a city shows stalls; and
  // tools/phonecheck.mjs sees them all)
  function warmUp() {
    const keep = [...eraMeshes, cityMesh, plate].filter(Boolean).map(m => [m, m.visible, m.material, m.layers.mask]), lay0 = camera.layers.mask;
    for (const [m] of keep) { colour(m); m.visible = true; m.material = m.userData.mini || m.material; m.layers.enable(L); }
    camera.layers.set(L); renderer.compile(scene, camera); camera.layers.mask = lay0;
    for (const [m, v, mat, mask] of keep) { m.visible = v; m.material = mat; m.layers.mask = mask; }
  }
  async function render({ target, d }) {
    window.__MINI = { scene, camera, eraMeshes, cityMesh, plate, trees: () => TF.objs(), sun, target: target.clone(), d, swap, detail: DET };   // (for a script: tools that export the frame's geometry, swap)
    renderer.getDrawingBufferSize(size); pxK.value = camera.projectionMatrix.elements[5] * size.y / renderer.getPixelRatio() / 2;   // (the picture's pixels, not the drawing buffer's: it is drawn at twice their number and shrunk)
    const up = E => E.mesh.visible && !E.mesh.userData.gone;   // (the film: a city gone may still show its foundations, without its detail)
    if (DET) { for (const [id, E] of Object.entries(S.eras)) if (up(E) && !DET.has(id)) DET.set(id, detailOf(id));
      clearNow = [];
      for (const [id, g] of DET) { const G = await g; G.visible = up(S.eras[id]); if (G.visible) clearNow.push(G.userData.treeOK); }
      boats(target, d); }
    const swapM = [];   // (the studio's materials back after the frame)
    for (const m of [...eraMeshes, cityMesh]) if (m.visible) colour(m);
    for (const m of [...eraMeshes, cityMesh, plate].filter(Boolean)) { if (!m.userData.mini) continue; swapM.push([m, m.material, m.customDepthMaterial]); m.material = m.userData.mini; m.customDepthMaterial = m.userData.miniDepth; m.layers.enable(L); m.castShadow = m.receiveShadow = true; }   // (the film: shadows deformed as the city stands)
    { const src = [...eraMeshes.filter(m => m.visible), ...(cityMesh.visible ? [cityMesh] : [])]; for (const l of landmarks) l.traverse(o => { if (o.isMesh) src.push(o); });
      TF.update(target, d, src); }
    const v = camera.position.clone().sub(target), kd = U.uKeyDir.value, el = THREE.MathUtils.degToRad(SUN_EL), r = d * 1.2;
    const az = film ? Math.atan2(kd.x, kd.z) : Math.atan2(v.x, v.z) + THREE.MathUtils.degToRad(SUN_SIDE);   // the sun: behind the eye, to its left, 40 degrees up (fx light: lower); the film: from the key light's bearing
    sun.position.set(target.x + r * Math.sin(az) * Math.cos(el), target.y + r * Math.sin(el), target.z + r * Math.cos(az) * Math.cos(el)); sun.target.position.copy(target);
    if (S.fxSun) sun.position.copy(target).addScaledVector(S.fxSun, r);   // (fx light: the sun fixed in the world, as the white model's)
    const c = sun.shadow.camera; c.left = c.bottom = -d * 1.6; c.right = c.top = d * 1.6; c.near = r * .2; c.far = r * 2.5; c.updateProjectionMatrix();
    const bg0 = scene.background, fog0 = scene.fog, lay0 = camera.layers.mask;
    const nt = film ? U.uNight.value : 0;   // the film at night: the sun down to a moon's light, the sky dark, the windows and the studio's light the brighter
    // a burning city's pall (its smoke: studio.js fireByDay) dims the light and warms it, by the fire's size
    let fk = 0; if (film) for (const f of Object.values(S.fires)) if (f.day) fk = Math.max(fk, f.u.uA.value * THREE.MathUtils.clamp(f.size / 1500, .15, 1));
    if (film) { sun.intensity = SUN0 * (1 - .9 * nt) * (1 - .2 * fk); sun.color.copy(SUNC).lerp(NIGHT.sun, nt).lerp(PALL.sun, .4 * fk); sky.intensity = SKY0 * (1 - .78 * nt) * (1 - .15 * fk);
      bgNow.copy(bg).lerp(NIGHT.bg, nt).lerp(PALL.sky, .3 * fk); fog.color.copy(FOG).lerp(NIGHT.fog, nt).lerp(PALL.sky, .3 * fk);
      S.colourLight.value = .55 + .6 * nt; if (FP) { FP.bloom.threshold = THREE.MathUtils.lerp(2.2, .9, nt); FP.bloom.strength = THREE.MathUtils.lerp(.1, .45, nt); }
      if (ctx) { swapM.push([ctx, ctx.material, ctx.customDepthMaterial]); ctx.material = far; ctx.userData.vis0 = ctx.visible; ctx.visible = true; ctx.layers.enable(L); ctx.receiveShadow = true; } }
    scene.background = film ? bgNow : bg; fog.near = d * (film ? 2.6 : 1.6); fog.far = d * (film ? 14 : 8); scene.fog = FX && FX.haze ? null : fog; camera.layers.set(L);   // (the film: less haze over the plate)
    const sd = sun.position.clone().sub(target).normalize();
    if (relief) { U.uFxSun.value.copy(sd); if (FX.light) { U.uFxLitC.value.setRGB(1, 1, 1).lerp(new THREE.Color(1.1, .99, .84), warm); U.uFxShadeC.value.setRGB(1, 1, 1).lerp(new THREE.Color(.82, .9, 1.1), warm); } }
    if (dome) dome.u.uSunD.value.copy(sd);
    if (FP) {   // the film's lens for this distance (main.js lens), with the stronger depth of field
      if (lens) { if (!film) lens(d); FP.dof.focus = S.post.dof.focus; FP.dof.aper = film || FX.dof ? S.post.dof.aper : 0; FP.dof.maxCoc = S.post.dof.maxCoc; FP.dof.band = S.post.dof.band; }   // (the film: as main.js set it for this frame, a living moment's sharp picture included)
      if (FX && FX.dof && !S.post.dof.rtB) fxLens(FP.dof, FX.dof, d);   // (the studio's own pass applied it already where it has the stronger gather)
      if (FP.dof.haze) FP.dof.haze.uHazeSunD.value.copy(sd);
      if (FP.dof.ao) FP.dof.ao.updateGtaoMaterial({ radius: fxAoRadius(d) });
    }
    renderer.getDrawingBufferSize(size); composer.setSize(size.x / renderer.getPixelRatio(), size.y / renderer.getPixelRatio());
    ht.uniforms.h.value = 4 / size.x; vt.uniforms.v.value = 4 / size.y; ht.uniforms.r.value = vt.uniforms.r.value = .5;
    ao.setSize(size.x, size.y); ao.updateGtaoMaterial({ radius: d * .02 });
    renderer.shadowMap.needsUpdate = true; (FP ? FP.composer : composer).render();
    scene.background = bg0; scene.fog = fog0; camera.layers.mask = lay0;
    for (const [m, mat, dm] of swapM) { m.material = mat; m.customDepthMaterial = dm; }
    if (ctx) ctx.visible = ctx.userData.vis0;
  }
  return { render, warm: warmUp, sun, sky, card: info, swap, ruinT: RUIN_T };
}

// the modern section, for the colour film (the year the counter tells, or the modern growth begun): before it a city's present
// fabric did not stand, from it much of it did. Before it, today's city goes where the white film dims it, and a period city's
// foundations stay; from it, today's city stays there as a muted backdrop and the foundations are cleared (main.js RUINS_TO)
const MODERN_GLSL = 'max(uGrowRise, smoothstep(1795., 1805., uYear))';

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
function filmMaterial(S, mat, u, ruin, fadeAt, fire = null) {
  S.deformMaterial(mat, u); const deform = mat.onBeforeCompile, nL = u ? u.uLossBurn.value.length : 0, H = S.slots, depth = !!mat.isMeshDepthMaterial, E = S.marksN();
  const hm = `vec2 huv_ = aCtr / uPlateV + .5; vec4 h1_ = texture2D(uHide, huv_), h2_ = texture2D(uHide2, huv_)${S.slots3 ? ', h3_ = texture2D(uHide3, huv_)' : ''};
     float hm_[${H}]; hm_[0] = h1_.r; hm_[1] = h1_.g; hm_[2] = h1_.b; hm_[3] = h1_.a; hm_[4] = h2_.r; hm_[5] = h2_.g; hm_[6] = h2_.b; hm_[7] = h2_.a;${S.slots3 ? ' hm_[8] = h3_.r; hm_[9] = h3_.g; hm_[10] = h3_.b; hm_[11] = h3_.a;' : ''}`;
  const dim = 'clamp(mix(uDimToday0, uDimToday, smoothstep(uNodeR + .004, uNodeR - .025, length(aCtr - uNodeC))) / uFadeAt, 0., 1.)';
  const vert = u ? `
   if (aData.w > 2.5) { float ry; ${S.eraRy('aData.z', 'aData.w')}
     float up_ = smoothstep(st, st + uEraGrow, uEraT), clr_ = ${MODERN_GLSL};   // (risen; cleared: the modern section, or a later city risen here)
     ${hm}
     for (int i = 0; i < ${H}; i++) if (uRuinLater[i] > .5 && hm_[i] > .02) { float r_ = (hm_[i] - .04) / .96, g_ = uHideG[i]; clr_ = max(clr_, smoothstep(r_ - g_ * .7, r_ + g_ * .15, uRuinT[i])); }
     float hh_ = tr0_.y - aBase, fd_ = min(hh_, uRuinH) * up_ * (1. - clr_);
     vRuin = up_ * (1. - clr_) * (1. - max(ry, 0.));
     if (fd_ > hh_ * max(ry, 0.) && fd_ > 1e-7) transformed.y = aBase + fd_; }` : `
   if (aData.w > -.5 && aData.w < .5) {   // (by its building: a building goes whole, the ring passing it as the white film's dimming does)
     float dm_ = ${dim}, mod_ = ${MODERN_GLSL}; vMute = dm_ * mod_;
     if (fract(sin(dot(aCtr, vec2(127.1e3, 311.7e3))) * 43758.5453) < dm_ * (1. - mod_) * 1.001 - .001) transformed.y = aBase - .02;
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
    if (u) Object.assign(sh.uniforms, { uRuinLater: u.uRuinLater, uRuinT: u.uRuinT, uRuinH: u.uRuinH, uLossBurnt: u.uLossBurnt, uRuinC: { value: ruin || new THREE.Color('#bcae92') } },
      fire ? { ...fire.day.F, uO: fire.u.uO } : {});
    else sh.uniforms.uFadeAt = { value: fadeAt };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>\nvarying float vRuin, vMute, vFresh;${u ? ` uniform float uRuinLater[${H}], uRuinT[${H}], uRuinH;` : ' uniform float uDimToday, uDimToday0, uNodeR, uFadeAt, uGrowWarm; uniform vec2 uNodeC;'}`)
      .replace('#include <begin_vertex>', '#include <begin_vertex>\n vec3 tr0_ = transformed; vRuin = 0.; vMute = 0.; vFresh = 0.;')   // (as built, before the studio's deformation)
      .replace('#include <project_vertex>', vert + '\n#include <project_vertex>')
      .replace('#include <fog_vertex>', '#include <fog_vertex>\n vData = aData; vWP = (modelMatrix * vec4(transformed, 1.)).xyz;' + (depth ? '' : ' vWN = normalize(mat3(modelMatrix) * objectNormal);'));
    if (depth) return;
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>\n// (look: mini)\nvarying vec4 vData; varying vec3 vWP, vWN; varying float vUp, vBase, vRuin, vMute, vFresh; varying vec2 aCtrV; uniform float uNow, uNight, uScaleM;${S.marksGLSL()}${u ? ` uniform float uEraBurn, uLossBurn[${nL}], uLossBurnt[${nL}]; uniform vec3 uRuinC;${fire ? ' uniform vec2 uO;' + S.fireGLSL : ''}` : ''}`)
      .replace('#include <color_fragment>', '#include <color_fragment>' + marks)
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>' + night);
    if (u) sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
  float burn_ = uEraBurn, burnt_ = uEraBurn, char_ = uEraBurn; for (int k = 0; k < ${nL}; k++) if (abs(vData.w - 4. - float(k)) < .5) { burn_ = max(burn_, uLossBurn[k]); char_ = max(char_, uLossBurn[k]); burnt_ = max(burnt_, uLossBurnt[k]); }   // (studio.js eraBurnK; burnt: a part a fire took)${fire ? `
  if (uEraBurn > 0.) { float e_ = uNow - ign(aCtrV, fireHash(aCtrV)); char_ = smoothstep(0., 2.5, e_); burn_ = smoothstep(0., .6, e_) * (1. - .7 * smoothstep(2.5, 5., e_)); }   // (the fire's front: studio.js fireByDay)` : ''}
  diffuseColor.rgb *= 1. - .88 * char_;
  diffuseColor.rgb = mix(diffuseColor.rgb, uRuinC * (1. - .8 * burnt_), vRuin);   // foundations`)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
  { float h_ = fract(sin(dot(aCtrV, vec2(127.1e3, 311.7e3))) * 43758.5453), fl_ = .5 + .5 * sin(uNow * (6. + 5. * h_) + h_ * 40.);   // a burning building's walls glow, flickering (its flames: studio.js)
    totalEmissiveRadiance += vec3(1., .34, .06) * burn_ * vUp * (abs(vWN.y) < .5 ? .15 + .55 * fl_ : .04); }`);
    else sh.fragmentShader = sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
  { float l_ = dot(diffuseColor.rgb, vec3(.2126, .7152, .0722)); diffuseColor.rgb = mix(diffuseColor.rgb, mix(vec3(l_), diffuseColor.rgb, .35) * .8 + .1 * l_ + .03, .8 * vMute);   // a muted backdrop
    diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(1.22, 1.1, .88) + vec3(.07, .045, 0.), vFresh); }   // new: warm while new`); };
  mat.customProgramCacheKey = () => 'mini-film ' + (u ? 'era ' + nL + (fire ? ' fire' : '') : 'today') + (depth ? ' depth' : '');
  return mat;
}
