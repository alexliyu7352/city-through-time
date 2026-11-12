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
const POOL = { value: new THREE.Vector4(0, 0, 1e9, 1) };
// the built area of the period cities standing (a material's ground_in: its plaster inside it, the table beyond): their buildings'
// centres drawn over the plate, each `reach` m round, softened; made again when the cities standing change (builtMask)
const BUILT = { value: null }, BUILT_C = typeof document !== 'undefined' ? document.createElement('canvas') : null; let BUILT_K = null;
function builtMask(meshes, PW, PD, scale, reach) {
  const key = meshes.filter(m => m.visible).map(m => m.uuid).join(); if (key === BUILT_K) return; BUILT_K = key;
  const N = 1024, c = BUILT_C; c.width = c.height = N; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, N, N); g.fillStyle = '#fff';
  const r = Math.max(1, reach * scale / PW * N);
  for (const m of meshes) { if (!m.visible) continue; const C = m.geometry.attributes.aCtr, D = m.geometry.attributes.aData; if (!C) continue;
    let lx = 1e9, lz = 1e9;
    for (let i = 0; i < C.count; i += 6) { const x = C.getX(i), z = C.getY(i); if (x === lx && z === lz) continue; lx = x; lz = z;
      if (D && Math.round(D.getY(i)) === 4) continue;   // (not a tree)
      g.beginPath(); g.arc((x / PW + .5) * N, (z / PD + .5) * N, r, 0, 6.2832); g.fill(); } }
  g.filter = `blur(${(r * 1.6).toFixed(1)}px)`;   // (wide: a lone building outside the city fades under the threshold, a quarter stays)
  g.drawImage(c, 0, 0); g.filter = 'none';
  if (!BUILT.value) { BUILT.value = new THREE.CanvasTexture(c); BUILT.value.colorSpace = THREE.NoColorSpace; } BUILT.value.needsUpdate = true;
}
// the base every material stands on: a grey slate plate, its grain and veins, a sheen where the light grazes it; the land's rise in
// stacked sheets (step m), each a little lighter, its edge a light line; the water a glossy resin; streets and plazas a lighter inlay
const SLATE = { slate: [.31, .31, .31], step: 6, edge: 1.45, resin: [.20, .14, .08] };
// the maquette's base: a photographed cleft slate (engine/tex/slate: Poly Haven dark_rock_02, CC0), its colour scaled to `slate`
// (linear) over its own mean, `size` m a repeat (and 6.3 times that, turned, over it), its normal `bump` strong; the sheets of the
// land's rise `step` m, their edges a faint `edge`; the water a glossy resin
const SLATE_TEX = { tex: 'slate', slate: [.0068, .0068, .0068], mean: .032, size: 55, ground_in: { col: [.80, .76, .68], reach: 45 }, bump: 1.6, ground: '#bdb19c', step: 6, edge: 1.12, resin: [.60, .66, .70] };
// the colour film's picture, as a photograph of a model on a table: a warm key from a sun fixed in the world, low and to the side
// of where the film's camera mostly looks from (sunSide degrees round from it: shadows fall across the frame and toward the eye,
// where they read, and an orbit turns them as a real one would), a cool fill from the sky, the shadow fitted to the ground the
// frame shows (every house and tree on its own hard shadow at any range) and the ambient occlusion full (every crevice and the foot
// of every wall darker); a lens whose depth of field softens what is nearer as well as farther than the subject; no veil of air
// over the plate. The land a meadow with fields in strips and woods in clusters of big canopies; trees big enough to read
const FILM_PIC = { sunEl: 30, sunSide: 75, sun: 1.05, sunC: '#ffdcae', sky: .8, skyC: '#d0d6e2', skyGround: '#9a9578', fogNear: 6, fogFar: 40,
  ao: 1.0, aoR: [.012, 4, 14], vignette: .12, sat: .9, contrast: .1, dof: { k: 1.6, max: 24, band: .375, two: true, at: 1.1, Ak: .0545 },   // (aoR: the occlusion's reach, a share of the distance, between these metres)
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
    // a museum's architectural maquette: plaster walls, light wood roofs and landmarks, a dark slate base, water as dark resin
    maquette: { pic: { sunEl: 50, sun: .95, sunC: '#ffe9cc', sky: .72, skyC: '#ece4d6', skyGround: '#6a645a', ao: .35, vignette: .45, pathW: 0, pool: [.12, .2], haze: [.7, 2.6], fogC: '#3a3530', tree: { keep: 0, wood: 0, count: 0 } }, base: SLATE_TEX,
      roman: { walls: ['#ead9bb', '#e5d2b0', '#eedfc4', '#e0cba8', '#e8d6b6'], roofs: ['#e3cba2', '#ddc398', '#e8d2ad', '#d8bd90', '#e1c69c', '#dbc095'],
        parts: { 1: '#f6f3ec', 4: '#2e4424', 7: '#cbbfa8', 9: '#e2d3b6', 10: '#cbbfa8', 11: '#d2c6b0' }, tree: { dark: .55, sat: .7 }, flags: false,
        detail: { floor: '#e6d5b6', joint: '#3c3e42', ridge: '#cfb184', shop: '#5a4a3a', base: '#d3c6ac' } } },
    // a clay diorama: terracotta tiles in relief, each its own, a sandy ground, cobbled streets, moss at the walls' feet
    clay: { pic: { sunEl: 38, sun: 1.1, sunC: '#ffd6a8', sky: .85, skyC: '#efe2cf', skyGround: '#6e6150', tree: { keep: 0, wood: 0, count: 0 } }, base: SLATE,
      soft: .6, tiles: 2.2, tufts: true,   // (soft: the share of a corner's averaged normal in each face's, a rounded edge; tiles: their rows' relief, times; tufts: moss at the walls' feet)
      roman: { roofs: ['#b8613f', '#c4704a', '#a65a3e', '#c97f57', '#b0573a', '#bd6a48'], parts: { 1: '#d9c7a6', 7: '#9a8f7c', 10: '#9a8f7c', 11: '#9a8f7c' }, flags: false,
        tree: { dark: .7, sat: .6 }, detail: { tuft: '#4f6a2a', joint: '#6e6556' } } } },   // a close shot's heights (HSCALE): walls this share as tall (a period city's x3 toward x1.4) nearer than `near` model units, none from `far`
  band: null };   // the tilt-shift band of screen blur (none: the lens's depth of field does it), else { mid, inner, outer, top, bottom }
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
varying vec2 vXZ; varying vec3 vFxW; uniform sampler2D uWaterM; uniform vec2 uPlateM; uniform float uKind;${S && MAT && MAT.base && MAT.base.tex ? ' uniform sampler2D uSlateC, uSlateN, uSlateR, uBuilt; uniform vec4 uPool; vec3 slateN_ = vec3(0., 0., 1.); float slateR_ = .7;' : ''}${fu ? ' uniform vec2 uPallC; uniform float uPallR, uPallK;' : ''}${town ? `
uniform sampler2D uHide, uHide2${H3 ? ', uHide3' : ''}; uniform float uHideT[${H}], uHideG[${H}];
float townAt(vec2 uv){ vec4 h1 = texture2D(uHide, uv), h2 = texture2D(uHide2, uv)${H3 ? ', h3 = texture2D(uHide3, uv)' : ''};
  float hm[${H}]; hm[0] = h1.r; hm[1] = h1.g; hm[2] = h1.b; hm[3] = h1.a; hm[4] = h2.r; hm[5] = h2.g; hm[6] = h2.b; hm[7] = h2.a;${H3 ? ' hm[8] = h3.r; hm[9] = h3.g; hm[10] = h3.b; hm[11] = h3.a;' : ''}
  float t = 0.; for (int i = 0; i < ${H}; i++) { if (uHideT[i] < -.5 || hm[i] < .02) continue; float r = (hm[i] - .04) / .96;
    t = max(t, smoothstep(.02, .06, hm[i]) * smoothstep(r - uHideG[i] * .7, r + uHideG[i] * .15, uHideT[i])); }
  return t; }` : ''}${relief ? RELIEF_GLSL : ''}${landLookGLSL(land, relief, o || null, ex, scale, 'mini')}${S ? farLandGLSL(land, o) : ''}${then ? '\nuniform sampler2D uWater;' + S.wThenGLSL : ''}`)
      .replace('#include <color_fragment>', `#include <color_fragment>${S ? '\n// (look: mini)' : ''}
  vec2 m_ = vXZ / ${scale.toFixed(6)};   // metres
  float wr_ = ${wr}, wMask = smoothstep(.35, .65, wr_);
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
  diffuseColor.rgb = mix(land, pow(water, vec3(2.2)), wMask);${S && MAT && MAT.base ? baseGLSL(MAT.base, scale, town) : ''}${fu ? `
  diffuseColor.rgb *= 1. - uPallK * .55 * smoothstep(uPallR, uPallR * .3, length(vXZ - uPallC));   // (under a burning city's pall)` : ''}
  }`)   // (the water's colours are sRGB; the shading is linear)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = mix(roughnessFactor, .32, wMask);' + (S && MAT && MAT.base && MAT.base.tex ? '\n  roughnessFactor = mix(clamp(slateR_ * .9, .3, 1.), .15, wMask);   // (the slate\'s own roughness, the resin\'s gloss)' : S && MAT && MAT.base && MAT.base.slate ? '\n  roughnessFactor = mix(.55, .18, wMask);   // (the slate\'s sheen, the resin\'s gloss)' : ''))
      .replace('#include <normal_fragment_begin>', `#include <normal_fragment_begin>${o && o.meadow ? `
  { vec3 up_ = normalize((viewMatrix * vec4(0., 1., 0., 0.)).xyz); float a_ = dot(normal, up_);   // (the film: the land's slopes drawn steeper in the light, a terrace or a plateau read; buildings keep their seat)
    normal = normalize(a_ * up_ + (normal - a_ * up_) * ${(FILM_PIC.relief).toFixed(2)}); }` : ''}${S && MAT && MAT.base && MAT.base.tex ? `
  { vec3 tb_ = normalize(vec3(slateN_.x, slateN_.z, -slateN_.y) * vec3(${MAT.base.bump.toFixed(2)}, 1., ${MAT.base.bump.toFixed(2)}));   // (the slate's cleft, its tangent space laid on the plate: x east, y north)
    vec3 up_ = normalize((viewMatrix * vec4(0., 1., 0., 0.)).xyz), ex_ = normalize((viewMatrix * vec4(1., 0., 0., 0.)).xyz), ez_ = normalize((viewMatrix * vec4(0., 0., 1., 0.)).xyz);
    normal = normalize(mix(normal, normalize(normal + ex_ * tb_.x + ez_ * tb_.z), 1. - wMask)); }` : ''}`)
      .replace('#include <opaque_fragment>', `${relief ? 'outgoingLight = mix(outgoingLight, fxReliefLight(vFxW, outgoingLight, diffuseColor.rgb), 1. - wMask);   // the relief (fx.js)\n' : ''}#include <opaque_fragment>`);
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
export function miniLook({ S, cityMesh, scale, lens = null, palette = 'roman', ground = 'land', card = null, prims = null, hex = () => 2, face = () => null, film = false, lost = null,
  paletteOf = () => palette, today = null, fadeAt = .8, phone = false, backdropFrom = 1800, dataFrom = 1e4, camAz = null, paths = null }) {   // (paths: the film's routes drawn as paths on the land, main.js QUIET)   // (camAz: the bearing the film's camera mostly looks from, degrees: the sun's is fixed from it)   // (phone: the film on a phone, main.js: no ambient occlusion, a smaller shadow map; the caller leaves the detail out)
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
  const bg = new THREE.Color('#c4d8ea'), fog = new THREE.Fog('#cfdde8', 1, 3), FOG = fog.color.clone(), SUN0 = sun.intensity, SKY0 = sky.intensity;
  const NIGHT = { bg: new THREE.Color('#16223a'), fog: new THREE.Color('#1c2a44'), sun: new THREE.Color('#9fb4e0') }, SUNC = sun.color.clone(), bgNow = bg.clone();   // (the film at night: film.night)
  const PALL = { sun: new THREE.Color('#ffb070'), sky: new THREE.Color('#8f8273') };   // (under a burning city's smoke)
  const landmarks = [];   // detailed models drawn in place of the generator's (swap)
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
    { ssaa: S.post.dof.s, ao: !phone, aoAmt: FX ? MINI_LIFT.ao : FP_ ? FILM_PIC.ao : FILM_AO, aoDepth: film, ...S.gpu.targets, ...(FX && FX.haze ? { haze: FX_SKY.mini } : {}), ...(FX && FX.dof || FP_ && FILM_PIC.dof.two ? { dof2: true } : {}) }) : null;
  const dome = FX && FX.haze ? makeSky(FX_SKY.mini) : null;
  if (FP) { FP.bloom.strength = .1; FP.bloom.threshold = 2.2;   // (a bright day: only the sun's glints glow, not every lit wall)
    FP.vig.uniforms.amt.value = .22;
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
    m.userData.mini = m === cityMesh ? colourToday(m, today ? TODAY[today] : undefined) : colourMesh(m, palOf(id), !!DET, { face: face(id), upright: uprightOf(id) }, { cell: 12 * scale, dark: (palOf(id).tree && palOf(id).tree.dark) || 1 }, film);
    if (film && MAT && MAT.soft && m !== cityMesh) softNormals(m.geometry);
    if (film) { const u = m === cityMesh ? null : S.eras[id].u, ruin = m === cityMesh ? null : new THREE.Color(palOf(id).parts[11]);
      filmMaterial(S, m.userData.mini, u, ruin, fadeAt, u && S.fires[id] && S.fires[id].day ? S.fires[id] : null, BACK, FP_ && !!u); m.userData.miniDepth = filmMaterial(S, new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), u, null, fadeAt, null, BACK); }
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
  const SH = { ray: new THREE.Vector3(), cam: new THREE.Object3D(), p: new THREE.Vector3(), q: [] };
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
  async function render({ target, d, sharp = 0 }) {   // (sharp: 0..1, a living moment's picture up, sharp throughout)
    window.__MINI = { scene, camera, eraMeshes, cityMesh, plate, trees: () => TF.objs(), sun, target: target.clone(), d, swap, detail: DET };   // (for a script: tools that export the frame's geometry, swap)
    renderer.getDrawingBufferSize(size); pxK.value = camera.projectionMatrix.elements[5] * size.y / renderer.getPixelRatio() / 2;   // (the picture's pixels, not the drawing buffer's: it is drawn at twice their number and shrunk)
    const up = E => E.mesh.visible && !E.mesh.userData.gone;   // (the film: a city gone may still show its foundations, without its detail)
    if (DET) { for (const [id, E] of Object.entries(S.eras)) if (up(E) && !DET.has(id)) DET.set(id, detailOf(id));
      clearNow = [];
      for (const [id, g] of DET) { const G = await g; G.visible = up(S.eras[id]); if (G.visible) clearNow.push(G.userData.treeOK); }
      boats(target, d); }
    for (const P of PATHS) { const t = U.uNow.value, r = P.r, a = sm(r.on, r.on + .3, t) * (1 - sm(r.off - .6, r.off, t));   // (the routes' paths, as they draw and go)
      P.mesh.visible = a > .002; P.mesh.material.opacity = a; P.u.uP.value = sm(r.on, r.on + r.draw, t) * 1.0001; }
    const swapM = [];   // (the studio's materials back after the frame)
    for (const m of [...eraMeshes, cityMesh]) if (m.visible) colour(m);
    for (const m of [...eraMeshes, cityMesh, plate].filter(Boolean)) { if (!m.userData.mini) continue; swapM.push([m, m.material, m.customDepthMaterial]); m.material = m.userData.mini; m.customDepthMaterial = m.userData.miniDepth; m.layers.enable(L); m.castShadow = m.receiveShadow = true; }   // (the film: shadows deformed as the city stands)
    { const src = [...eraMeshes.filter(m => m.visible), ...(cityMesh.visible ? [cityMesh] : [])]; for (const l of landmarks) l.traverse(o => { if (o.isMesh) src.push(o); });
      TF.update(target, d, src); }
    const v = camera.position.clone().sub(target), kd = U.uKeyDir.value, el = THREE.MathUtils.degToRad(SUN_EL), r = d * 1.2;
    const az = film ? (camAz != null ? THREE.MathUtils.degToRad(camAz + (FP_ ? FILM_PIC.sunSide : 55)) : Math.atan2(kd.x, kd.z)) : Math.atan2(v.x, v.z) + THREE.MathUtils.degToRad(SUN_SIDE);   // the sun: behind the eye, to its left, 40 degrees up (fx light: lower); the film: from the key light's bearing
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
    if (film) { sun.intensity = SUN0 * (1 - .9 * nt) * (1 - .2 * fk); sun.color.copy(SUNC).lerp(NIGHT.sun, nt).lerp(PALL.sun, .4 * fk); sky.intensity = SKY0 * (1 - .78 * nt) * (1 - .15 * fk);
      bgNow.copy(bg).lerp(NIGHT.bg, nt).lerp(PALL.sky, .3 * fk); fog.color.copy(FILM_PIC.fogC ? new THREE.Color(FILM_PIC.fogC) : FOG).lerp(NIGHT.fog, nt).lerp(PALL.sky, .3 * fk);
      S.colourLight.value = FP_ ? FILM_PIC.projector + .6 * nt : .55 + .6 * nt;   // (the film's picture: none of the projector's light by day, main.js QUIET) if (FP) { FP.bloom.threshold = THREE.MathUtils.lerp(2.2, .9, nt); FP.bloom.strength = THREE.MathUtils.lerp(.1, .45, nt); }
      if (ctx) { swapM.push([ctx, ctx.material, ctx.customDepthMaterial]); ctx.material = far; ctx.userData.vis0 = ctx.visible; ctx.visible = true; ctx.layers.enable(L); ctx.receiveShadow = true; } }
    scene.background = film ? bgNow : bg; const kA_ = FP_ && FILM_PIC.pool ? THREE.MathUtils.smoothstep(d, .06, FILM_PIC.pool[1]) : 0;   // (an aerial's share: its pool and haze)
    fog.near = d * (FP_ && FILM_PIC.haze ? THREE.MathUtils.lerp(FILM_PIC.fogNear, FILM_PIC.haze[0], kA_) : FP_ ? FILM_PIC.fogNear : film ? 2.6 : 1.6); fog.far = d * (FP_ && FILM_PIC.haze ? THREE.MathUtils.lerp(FILM_PIC.fogFar, FILM_PIC.haze[1], kA_) : FP_ ? FILM_PIC.fogFar : film ? 14 : 8); scene.fog = FX && FX.haze ? null : fog; camera.layers.set(L);   // (the film: less haze over the plate)
    const sd = sun.position.clone().sub(target).normalize();
    if (relief) { U.uFxSun.value.copy(sd); if (FX.light) { U.uFxLitC.value.setRGB(1, 1, 1).lerp(new THREE.Color(1.1, .99, .84), warm); U.uFxShadeC.value.setRGB(1, 1, 1).lerp(new THREE.Color(.82, .9, 1.1), warm); } }
    if (dome) dome.u.uSunD.value.copy(sd);
    if (FP) {   // the film's lens for this distance (main.js lens), with the stronger depth of field
      if (lens) { if (!film) lens(d); FP.dof.focus = S.post.dof.focus; FP.dof.aper = FP_ ? S.post.dof.aper * FILM_PIC.dof.k : film || FX.dof ? S.post.dof.aper : 0; FP.dof.maxCoc = FP_ ? FILM_PIC.dof.max : S.post.dof.maxCoc; FP.dof.band = FP_ ? FILM_PIC.dof.band : S.post.dof.band; }   // (the film: as main.js set it for this frame, a living moment's sharp picture included)
      // a model's lens (FILM_PIC.dof.A: its opening in the city's metres, the model's own times its scale): the blur a camera that
      // close to a model that small gives, the same opening at every distance (a wide shot from afar blurs less, as a photograph
      // of the whole table does); at: the focus as a share of the shot's distance (beyond 1: the near ground the softer)
      const A_ = FILM_PIC.dof.A || (FILM_PIC.dof.Ak || 0) * d / scale;   // (Ak: the opening as a share of the shot's distance: every shot the same model seen as close)
      if (FP_ && lens && A_ && !(S.post.dof.aper < 1e-6)) { FP.dof.aper = 1080 * A_ * scale / (4 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2)); FP.dof.focus = S.post.dof.focus * (FILM_PIC.dof.at || 1); }   // (a living moment's sharp picture kept where its aperture is 0; its fade in and out not yet followed)
      if (FP_ && MAT && MAT.base && MAT.base.tex && U.uGroundN) U.uGroundN.value = 0;
      if (FP_ && MAT && MAT.base && MAT.base.ground_in && BUILT_C) builtMask(eraMeshes, S.PW, S.PD, scale, MAT.base.ground_in.reach);   // (a material's plate: the period cities' open ground is the plate itself, not patches of earth and gravel on it)
      if (FILM_PIC.pool) { const k_ = THREE.MathUtils.smoothstep(d, .06, FILM_PIC.pool[1]); POOL.value.set(target.x, target.z, d * .95, THREE.MathUtils.lerp(1, FILM_PIC.pool[0], k_)); } else POOL.value.set(0, 0, 1e9, 1);
      HSCALE.value = FP_ && FILM_PIC.hscale ? THREE.MathUtils.lerp(FILM_PIC.hscale.k, 1, THREE.MathUtils.smoothstep(d, FILM_PIC.hscale.near, FILM_PIC.hscale.far)) : 1;   // (a close shot's heights)
      if (FX && FX.dof && !S.post.dof.rtB) fxLens(FP.dof, FX.dof, d);   // (the studio's own pass applied it already where it has the stronger gather)
      if (FP.dof.haze) FP.dof.haze.uHazeSunD.value.copy(sd);
      if (FP.dof.ao) FP.dof.ao.updateGtaoMaterial({ radius: FP_ ? THREE.MathUtils.clamp(d * FILM_PIC.aoR[0], scale * FILM_PIC.aoR[1], scale * FILM_PIC.aoR[2]) : fxAoRadius(d) });   // (the film: contact, a few metres at a crevice, never a whole court in shade)
    }
    if (BAND) { const rt = FP.composer.renderTarget1; for (const b of BAND) { b.uniforms.px.value.set(1 / rt.width, 1 / rt.height); b.uniforms.k.value = rt.height / 1080 * (1 - sharp); } }
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
  return SLATE_MAPS = { uBuilt: BUILT, uPool: POOL, uSlateC: { value: t('Diffuse.jpg', true) }, uSlateN: { value: t('nor_gl.jpg') }, uSlateR: { value: t('Rough.jpg') } };
}
// a material's base under the model (FILM_PIC.looks: maquette, clay), in place of the painted land: m_ the metres, vFxW the world
function baseGLSL(B, scale, town = false) {
  const v3 = c => `vec3(${c.map(x => (+x).toFixed(3)).join(', ')})`;
  if (B.tex) return `
  { float y_ = vFxW.y / ${scale.toFixed(6)} / ${B.step.toFixed(2)}, c_ = fract(y_), w_ = max(fwidth(y_), 1e-4);   // the photographed slate, two scales of it turned against each other (no repeat afar), lit by its own normal and roughness (slateN_, slateR_)
    vec2 a_ = m_ / ${B.size.toFixed(1)}, b_ = mat2(.8, -.6, .6, .8) * m_ / ${(B.size * 6.3).toFixed(1)};
    vec3 c1_ = texture2D(uSlateC, a_).rgb, c2_ = texture2D(uSlateC, b_).rgb; float l1_ = dot(c1_, vec3(.2126, .7152, .0722)), l2_ = dot(c2_, vec3(.2126, .7152, .0722));
    float fd_ = smoothstep(.4, 2., length(fwidth(a_)) * 1024.);   // (texels a pixel: afar its pattern calms to its mean, no repeat)
    vec3 sl_ = ${v3(B.slate)} * mix(l1_, ${B.mean.toFixed(3)}, fd_ * .75) / ${B.mean.toFixed(3)} * mix(1., l2_ / ${B.mean.toFixed(3)}, .35);   // (its grey only: a neutral charcoal)
    sl_ *= 1. + .05 * clamp(floor(y_ - ${(20 / B.step).toFixed(2)}), 0., 4.);   // (each sheet up a little lighter)
    sl_ *= mix(1., ${B.edge.toFixed(2)}, (1. - smoothstep(w_ * .8, w_ * 1.6, c_)) * step(w_, .15));   // (its edge, faint, close only)
    slateN_ = texture2D(uSlateN, a_).xyz * 2. - 1.; slateR_ = texture2D(uSlateR, a_).r;
    ${B.ground_in ? `{ float tw_ = texture2D(uBuilt, vXZ / uPlateM + .5).r;   // inside the built area the model's own ground: a light plaster, a shade under its roofs (builtMask)
      vec3 pl_ = pow(${v3(B.ground_in.col)}, vec3(2.2)) * (.96 + .05 * fxLn(m_ / 13.) + .03 * fxLn(m_ / 2.1));
      float k_ = smoothstep(.42, .62, tw_); sl_ = mix(sl_, pl_, k_); slateR_ = mix(slateR_, .9, k_); slateN_ = mix(slateN_, vec3(0., 0., 1.), k_); }` : ''}
    diffuseColor.rgb = mix(sl_, pow(${v3(B.resin)}, vec3(2.2)), wMask);
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
function filmMaterial(S, mat, u, ruin, fadeAt, fire = null, back = null, surf = false) {   // (surf: a model's surfaces, the film's picture: FILM_PIC)
  S.deformMaterial(mat, u); const deform = mat.onBeforeCompile, nL = u ? u.uLossBurn.value.length : 0, H = S.slots, depth = !!mat.isMeshDepthMaterial, E = S.marksN();
  const hm = `vec2 huv_ = aCtr / uPlateV + .5; vec4 h1_ = texture2D(uHide, huv_), h2_ = texture2D(uHide2, huv_)${S.slots3 ? ', h3_ = texture2D(uHide3, huv_)' : ''};
     float hm_[${H}]; hm_[0] = h1_.r; hm_[1] = h1_.g; hm_[2] = h1_.b; hm_[3] = h1_.a; hm_[4] = h2_.r; hm_[5] = h2_.g; hm_[6] = h2_.b; hm_[7] = h2_.a;${S.slots3 ? ' hm_[8] = h3_.r; hm_[9] = h3_.g; hm_[10] = h3_.b; hm_[11] = h3_.a;' : ''}`;
  const dim = 'clamp(mix(uDimToday0, uDimToday, smoothstep(uNodeR + .004, uNodeR - .025, length(aCtr - uNodeC))) / uFadeAt, 0., 1.)';
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
     float dm_ = ${dim}, mod_ = ${MODERN_GLSL}; vMute = dm_ * mod_;
     if (fract(sin(dot(aCtr, vec2(127.1e3, 311.7e3))) * 43758.5453) < (1. - mod_) * 1.001 - .001) transformed.y = aBase - .02;   // (before the modern section none of it stood: building by building as it begins)
     if (vMute > .02 && aData.x > max(uYear, uDataY0) + .5) transformed.y = aBase - .02;   // (the backdrop: not built yet in the year told)
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
    if (u) { sh.uniforms.uHScale = HSCALE; sh.uniforms.uPool = POOL; }
    if (u) Object.assign(sh.uniforms, { uRuinLater: u.uRuinLater, uRuinT: u.uRuinT, uRuinH: u.uRuinH, uLossBurnt: u.uLossBurnt, uLossBurntV: u.uLossBurnt, uRuinC: { value: ruin || new THREE.Color('#bcae92') } },
      fire ? { ...fire.day.F, uO: fire.u.uO } : {});
    else sh.uniforms.uFadeAt = { value: fadeAt };
    if (u && MAT && MAT.soft && sh.vertexShader.includes('#include <beginnormal_vertex>')) sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec3 aSoft;')
      .replace('#include <beginnormal_vertex>', `#include <beginnormal_vertex>\n  objectNormal = normalize(mix(objectNormal, aSoft, ${MAT.soft.toFixed(2)}));   // (a rounded edge: the material's)`);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>\nvarying float vRuin, vMute, vFresh; uniform float uBackdropY, uDataY0;${u ? ` attribute float aY0; uniform float uHScale; uniform float uLossBurntV[${Math.max(nL, 1)}]; uniform float uRuinLater[${H}], uRuinT[${H}], uRuinH;` : ' uniform float uDimToday, uDimToday0, uNodeR, uFadeAt, uGrowWarm; uniform vec2 uNodeC;'}`)
      .replace('#include <begin_vertex>', '#include <begin_vertex>\n vec3 tr0_ = transformed; vRuin = 0.; vMute = 0.; vFresh = 0.;')   // (as built, before the studio's deformation)
      .replace('#include <project_vertex>', vert + '\n#include <project_vertex>')
      .replace('#include <fog_vertex>', '#include <fog_vertex>\n vData = aData; vWP = (modelMatrix * vec4(transformed, 1.)).xyz;' + (depth ? '' : ' vWN = normalize(mat3(modelMatrix) * objectNormal);'));
    if (depth) return;
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>\n// (look: mini)\nvarying vec4 vData; varying vec3 vWP, vWN; varying float vUp, vBase, vRuin, vMute, vFresh; varying vec2 aCtrV; uniform float uNow, uNight, uScaleM, uPallR, uPallK; uniform vec2 uPallC;${S.marksGLSL()}${u ? ` uniform float uEraBurn, uLossBurn[${nL}], uLossBurnt[${nL}]; uniform vec3 uRuinC;${fire ? ' uniform vec2 uO;' + S.fireGLSL : ''}` : ''}`)
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
      diffuseColor.rgb = mix(vec3(dot(diffuseColor.rgb, vec3(.2126, .7152, .0722))), diffuseColor.rgb, ${FILM_PIC.material === 'clay' ? '.45' : '0.'}) * ${FILM_PIC.material === 'clay' ? '.62' : '.78'} * (.92 + .14 * h_) * (1. - .35 * smoothstep(.94, .99, max(e_.x, e_.y)) * (1. - smoothstep(.3, .7, px_ / 3.2))); }
    else if (pt_ > 6.5 && pt_ < 7.5 && ${FILM_PIC.material === 'clay' ? 'true' : 'false'}) { vec2 q_ = vWP.xz / uScaleM / .55, c_ = floor(q_ + .5 * vec2(0., mod(floor(q_.x), 2.)));   // (clay: cobbles)
      vec2 f_ = fract(q_ + .5 * vec2(0., mod(floor(q_.x), 2.))) - .5; float h_ = fract(sin(dot(c_, vec2(12.99, 78.23))) * 43758.55);
      diffuseColor.rgb *= (.8 + .3 * h_) * (1. - .45 * smoothstep(.32, .5, max(abs(f_.x), abs(f_.y))) * (1. - smoothstep(.3, .7, px_ / .55))) * (1.1 - 1.2 * dot(f_ + vec2(.12, .12), f_ + vec2(.12, .12)));   // (each stone domed, lit from one side)
    }
    else if (pt_ > 6.5 && pt_ < 7.5) { vec2 e_ = abs(fract(vWP.xz / uScaleM / 3.) - .5) * 2.;   // paving in slabs
      diffuseColor.rgb *= 1. - .16 * smoothstep(.86, .97, max(e_.x, e_.y)) * (1. - smoothstep(.3, .7, px_ / 3.)); } }`);
    if (u) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform vec4 uPool;').replace('#include <color_fragment>', `#include <color_fragment>
  diffuseColor.rgb *= mix(1., uPool.w, smoothstep(uPool.z * .35, uPool.z * 1.05, length(vWP.xz - uPool.xy)));   // (the light pool, FILM_PIC pool)
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
  mat.customProgramCacheKey = () => 'mini-film ' + (u ? 'era ' + nL + (fire ? ' fire' : '') : 'today') + (depth ? ' depth' : '') + (surf ? ' surf' : '');
  return mat;
}
