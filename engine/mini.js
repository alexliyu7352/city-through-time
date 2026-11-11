// The colour look, a second engine beside the white-model one: the coloured miniature, drawn in the period cities' viewer
// (play.html?city=<slug>&view&look=mini; &palette=roman|chinese|modern, &ground=land|modern, &card=<year>|<period>|<population>: the
// info on screen; &detail=0: without engine/detail.js's pieces). It leaves the studio's own scene and materials as they are and
// draws the same geometry its own way: daylight from a sun and the sky, each building in its own wall and roof colours, its
// windows, doors, cornices, posts, rows of tiles and copings and the city wall's courses (engine/detail.js, from the period city's
// records; off on a touch screen), trees in the open land and the gardens, fields and water, a landmark's detailed model
// (tools/blender) in place of the generator's, a hazy sky and a tilt-shift blur (sharp in a band across the middle, as a
// photograph of a model).
// Nothing of the film is changed: the studio draws with layer 0, this look with layer 1 alone.
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
import { eraDetail, detailMeshes, gableEnds, STYLES } from './detail.js';

const L = 1;   // the layer this look draws
// with the effects: a bright day, as bright and as coloured as the look without them (the low warm sun, the haze and the occlusion
// had greyed it): the sun and the sky's light raised, the air thinner (its distance times haze), the occlusion lighter
const MINI_LIFT = { sun: 1.5, sky: 1.45, haze: 3.5, ao: .3 };
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
    detail: { window: '#33281f', door: '#4b3323', cornice: '#f4eee2', base: '#b9a588', coping: '#b0603f', archRing: '#ebe3d2' },
    faces: { earth: '#c9ad86', brick: '#b8805c', stone: '#ddd3c0', banded: '#e6dbc6' },
  },
  chinese: {
    walls: ['#ddcca8', '#d4bd94', '#e6d8bb', '#cdb38c', '#e0cfae'],
    roofs: ['#6c6863', '#78726b', '#625f5b', '#7f7970', '#5c5854'],
    parts: { 1: '#e2d5b8', 2: '#bfa070', 3: '#cbbd9f', 4: '#5f7d3c', 5: '#5d8fa8', 6: '#2f2620', 7: '#d8cbaa', 9: '#5d5955', 10: '#c9a978', 11: '#b8a58a' },
    land: LAND_PALETTES.loess,   // the loess plain: wheat, millet, bare earth
    glb: { stone: '#e3d6b8', dark: '#2b231d', roof: '#5f5b56', sand: '#c8a676' }, cypress: .08, tree: { size: .6, keep: .35, dark: .78 },   // (tree: its size, the share of places kept, its lightness)
    detail: { base: '#97918a', post: '#7a3524', beam: '#4e3b2e', ridgeEnd: '#4f4b47', coping: '#5b5853', archRing: '#8f8b85', column: '#8a2e20' },
    faces: { earth: '#bfa070', brick: '#8f8b84', stone: '#cac2b3', banded: '#d9cdb6' },
  },
  modern: {
    walls: ['#e9dfcf', '#f1ebe0', '#ddd2bf'], roofs: ['#c0714c', '#9d6a52', '#a8a39b'],
    parts: { 1: '#f1ebe0', 2: '#cdb08a', 3: '#d4d0c8', 4: '#5f7d3c', 5: '#5d8fa8', 6: '#3a3a3c', 7: '#c9c6bf', 9: '#9d6a52', 10: '#cdb48c', 11: '#bdb6aa' },
    land: LAND_PALETTES.temperate,
    glb: { stone: '#efe9de', dark: '#2b2b2d', roof: '#9d6a52', sand: '#cdb48c' }, cypress: .1,
    detail: { window: '#33302c', door: '#4b3a2c', cornice: '#f4f0e8', base: '#b8b0a2', coping: '#9d6a52', archRing: '#efe9de' },
    faces: { earth: '#cdb08a', brick: '#b37e5e', stone: '#ddd6c8', banded: '#e6ddcc' },
  },
};
const hash = (x, z) => { const s = Math.sin(x * 127.1 + z * 311.7) * 43758.5453; return s - Math.floor(s); };

// a house's roof colour, by its building's centre (aCtr): one of the palette's, a little lighter or darker (its tiles' rows: detail.js)
const roofOf = (pal, x, z) => { const h = hash(x, z); return new THREE.Color(pal.roofs[Math.floor((h * 7.31) % 1 * pal.roofs.length)]).multiplyScalar(.9 + .18 * ((h * 13.7) % 1)); };
// a period city's colour per vertex: a house's walls and roof each one of the palette's, by its building; a little lighter or darker;
// with the detail (detail.js; wall: { face: the city's walls' (film.json wall_face) or null, upright: its region's for an upright
// wall }), a gable's end in its wall's colour and a city wall in the colour of what it is faced with (a battered side rammed earth)
function colourMesh(mesh, pal, detail, wall) {
  const g = mesh.geometry, d = g.attributes.aData, c = g.attributes.aCtr, n = g.attributes.position.count, out = new Float32Array(n * 3), col = new THREE.Color();
  const walls = pal.walls.map(v => new THREE.Color(v)), roofs = pal.roofs.map(v => new THREE.Color(v)), gable = detail ? gableEnds(g) : new Uint8Array(n);
  const parts = Object.fromEntries(Object.entries(pal.parts).map(([k, v]) => [k, new THREE.Color(v)]));
  const faces = detail && pal.faces ? Object.fromEntries(Object.entries(pal.faces).map(([k, v]) => [k, new THREE.Color(v)])) : null, N = g.attributes.normal;
  const faceAt = i => { if (wall.face) return faces[wall.face]; const ny = Math.abs(N.getY(i - i % 3) + N.getY(i - i % 3 + 1) + N.getY(i - i % 3 + 2)) / 3; return faces[ny > .02 && ny < .9 ? 'earth' : wall.upright]; };
  for (let i = 0; i < n; i++) {
    const part = d ? Math.round(d.getY(i)) : 0, h = c ? hash(c.getX(i), c.getY(i)) : .5, h2 = (h * 7.31) % 1, h3 = (h * 13.7) % 1;
    if (part === 0 || gable[i]) col.copy(walls[Math.floor(h * walls.length)]);
    else if (part === 8) col.copy(roofs[Math.floor(h2 * roofs.length)]);
    else if (part === 2 && faces) col.copy(faceAt(i));
    else col.copy(parts[part] || walls[0]);
    const k = part === 0 || part === 8 ? .9 + .18 * h3 : .96 + .08 * h3;
    out[i * 3] = col.r * k; out[i * 3 + 1] = col.g * k; out[i * 3 + 2] = col.b * k;
  }
  g.setAttribute('color', new THREE.BufferAttribute(out, 3));
  return new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .92, metalness: 0 });
}

// today's city: its records have no parts (year, height, an id), so a top is a roof and a side a wall; roofs mostly tile, some flat
// and grey; walls in the warm plasters of an old city, tall buildings in the pale tones of new ones
function colourToday(mesh) {
  const g = mesh.geometry, d = g.attributes.aData, nrm = g.attributes.normal, n = g.attributes.position.count, out = new Float32Array(n * 3), col = new THREE.Color();
  const roofs = ['#9a5038', '#8c4b36', '#a6603f', '#7f4a3a'].map(c => new THREE.Color(c)), flat = new THREE.Color('#9d9a94');
  const walls = ['#d9b57e', '#e3cc9e', '#cf9a6c', '#e8dcc2', '#c98f6a'].map(c => new THREE.Color(c)), tall = ['#e6e3dc', '#cfd2d4', '#d9d2c4'].map(c => new THREE.Color(c));
  for (let i = 0; i < n; i++) {
    const h = d.getZ(i), hm = d.getY(i), top = nrm.getY(i) > .6, mound = d.getW(i) > .5;
    if (mound) col.set('#9a8f6a');
    else if (top) col.copy(hm > 24 || h < .3 ? flat : roofs[Math.floor(h * 97) % roofs.length]);
    else col.copy(hm > 30 ? tall[Math.floor(h * 31) % tall.length] : walls[Math.floor(h * 53) % walls.length]);
    const k = .9 + .2 * ((h * 7.13) % 1); out[i * 3] = col.r * k; out[i * 3 + 1] = col.g * k; out[i * 3 + 2] = col.b * k;
  }
  g.setAttribute('color', new THREE.BufferAttribute(out, 3));
  return new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .92, metalness: 0 });
}

// the land: fx.js's (a patchwork of fields, straw and bare earth, woods in patches and, with the relief, on the slopes: the white
// model's land under fx land is the same code, muted); the water (the studio's water map) turquoise in the shallows and deeper blue
// away from the shore, with the sun's glint. o: the land's settings (fx land, else the palette's fields alone, no woods)
function landMaterial(U, PW, PD, kind, land, relief, o, ex, scale) {
  const m = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .97, metalness: 0 });
  m.onBeforeCompile = sh => {
    sh.uniforms.uWaterM = U.uWater; sh.uniforms.uPlateM = { value: new THREE.Vector2(PW, PD) }; sh.uniforms.uKind = { value: kind === 'modern' ? 1 : 0 };
    if (relief) { for (const k of ['uFxHgt', 'uFxRect', 'uFxSun', 'uFxR', 'uFxRA', 'uFxLitC', 'uFxShadeC', 'uFxFlat']) sh.uniforms[k] = U[k]; sh.uniforms.uFxAdd = { value: 0 }; }   // (a bright ground: no light added on top)
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vXZ; varying vec3 vFxW;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvXZ = (modelMatrix * vec4(position, 1.)).xz; vFxW = (modelMatrix * vec4(transformed, 1.)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec2 vXZ; varying vec3 vFxW; uniform sampler2D uWaterM; uniform vec2 uPlateM; uniform float uKind;${relief ? RELIEF_GLSL : ''}${landLookGLSL(land, relief, o || null, ex, scale, 'mini')}`)
      .replace('#include <color_fragment>', `#include <color_fragment>
  vec2 m_ = vXZ / ${scale.toFixed(6)};   // metres
  float wMask = smoothstep(.35, .65, texture2D(uWaterM, vXZ / uPlateM + .5).r);
{ vec3 land = fxLandAt(vFxW);
  if (uKind > .5) land = mix(land, vec3(.29, .27, .23), .55);   // a city's ground: paved, dusty
  float deep = smoothstep(.4, .98, texture2D(uWaterM, vXZ / uPlateM + .5).r);
  vec3 water = mix(vec3(.38, .68, .70), vec3(.17, .42, .56), deep) * (.95 + .1 * fxLn(m_ / 40.));
  diffuseColor.rgb = mix(land, pow(water, vec3(2.2)), wMask); }`)   // (the water's colours are sRGB; the shading is linear)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n  roughnessFactor = mix(roughnessFactor, .32, wMask);')
      .replace('#include <opaque_fragment>', `${relief ? 'outgoingLight = mix(outgoingLight, fxReliefLight(vFxW, outgoingLight, diffuseColor.rgb), 1. - wMask);   // the relief (fx.js)\n' : ''}#include <opaque_fragment>`);
  };
  m.customProgramCacheKey = () => 'mini-land' + (relief ? ' fx' : '') + (o ? ' land' : '');
  return m;
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
export function miniLook({ S, cityMesh, scale, lens = null, palette = 'roman', ground = 'land', card = null, prims = null, hex = () => 2, face = () => null }) {
  const { scene, camera, renderer, U } = S, PW = S.PW, PD = S.PD;
  const pal = PALETTES[palette] || PALETTES.roman;
  // the meshes this look draws: the period cities, today's city, the plate
  const eraMeshes = Object.values(S.eras).map(e => e.mesh);
  let plate = null;
  scene.traverse(o => { if (o.isMesh && o.material && o.material.customProgramCacheKey && /^proj1/.test(o.material.customProgramCacheKey()) && o.geometry.attributes.position.count > 1000) plate = o; });
  const FX = S.fx, relief = !!(FX && FX.relief && U.uFxRA && U.uFxRA.value);   // the effects (fx.js), as the studio has them
  if (plate) plate.userData.mini = landMaterial(U, PW, PD, ground, FX && FX.land ? landPalette(FX.land) : pal.land, relief, FX && FX.land, S.terrainEx, scale);
  U.__ground = S.ground;
  // the land's woods where trees stand close (fx land: fx.js woodsFn)
  const woods = FX && FX.land ? woodsFn(FX.land, S.terrainEx, scale, S.ground, relief) : null;
  // the light of a clear day: the sun to one side behind the eye, 40 degrees up, soft shadows; the sky's blue from above, the land's from below
  // (fx light: a lower, warmer sun, as in the late afternoon, as bright on flat ground as the higher one; the sky's light a little bluer)
  const warm = FX && FX.light ? FX.light.warm : 0, SUN_EL = THREE.MathUtils.lerp(40, 28, warm), SUN_SIDE = relief ? 95 : 55;   // (fx relief: the sun more to the side, so the slopes facing the eye show light and shade)
  const sun = new THREE.DirectionalLight(new THREE.Color('#ffeed4').lerp(new THREE.Color('#ffd09a'), warm), 2.7 * (FX ? MINI_LIFT.sun : 1) * Math.sin(THREE.MathUtils.degToRad(40)) / Math.sin(THREE.MathUtils.degToRad(SUN_EL))), sky = new THREE.HemisphereLight(new THREE.Color('#c3d8ee').lerp(new THREE.Color('#a9c4ea'), warm), '#6b7550', .9 * (FX ? MINI_LIFT.sky : 1));
  sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -.0004; sun.shadow.normalBias = .00002; sun.shadow.radius = 2;
  for (const o of [sun, sun.target, sky]) { o.layers.set(L); scene.add(o); }
  const bg = new THREE.Color('#c4d8ea'), fog = new THREE.Fog('#cfdde8', 1, 3);
  const landmarks = [];   // detailed models drawn in place of the generator's (swap)
  // each period city's detail (engine/detail.js), made the first time it is shown: era id -> a promise of its group
  const DET = prims ? new Map() : null;
  const dcols = { ...(pal.detail || PALETTES.roman.detail), tile: (x, z) => roofOf(pal, x, z).multiplyScalar(1.12), verge: (x, z) => roofOf(pal, x, z).multiplyScalar(.78) };   // (a roof's tiles in its own colour)
  for (const [f, v] of Object.entries(pal.faces || PALETTES.roman.faces)) {   // (a wall's face: its courses a shade darker, a stone wall's bands brick; a gate's parts the wall's)
    dcols['course_' + f] = f === 'banded' ? (pal.faces || PALETTES.roman.faces).brick : new THREE.Color(v).multiplyScalar(.84);
    dcols['spandrel_' + f] = dcols['parapet_' + f] = dcols['merlon_' + f] = v; }
  const pxK = { value: 1 }, idOf = new Map(Object.entries(S.eras).map(([id, E]) => [E.mesh, id])), upright = (STYLES[palette] || STYLES.roman).wall;   // (the fade's scale: detail.js FADE_PX)
  const detailOf = async id => { const D = eraDetail(await prims(id), { scale, hex: hex(id), style: palette, face: face(id) }), g = detailMeshes(D, dcols, { layer: L, pxK });
    g.userData.count = D.count; scene.add(g); return g; };
  const TF = treeField(scene, renderer, U, PW, PD, scale, { size: 1, keep: 1, dark: 1, ...pal.tree, cypress: pal.cypress, woods, ground: S.ground, layer: L, tone: 'mini' });
  const info = card ? infoPanel(card) : null;
  // the tilt-shift: sharp in a band through the middle, blurred above and below
  // with the effects: the film's own passes (post.js: ambient occlusion, haze toward a sky dome, the stronger depth of field),
  // in place of the tilt-shift band
  const FP = FX ? makePost(renderer, scene, camera, S.post.dof.rt.width / S.post.dof.s, S.post.dof.rt.height / S.post.dof.s,
    { ssaa: S.post.dof.s, ao: true, aoAmt: MINI_LIFT.ao, ...S.gpu.targets, ...(FX.haze ? { haze: FX_SKY.mini } : {}), ...(FX.dof ? { dof2: true } : {}) }) : null;
  const dome = FX && FX.haze ? makeSky(FX_SKY.mini) : null;
  if (FP) { FP.bloom.strength = .1; FP.bloom.threshold = 2.2;   // (a bright day: only the sun's glints glow, not every lit wall)
    FP.vig.uniforms.amt.value = .22;
    if (FP.dof.haze) { const ex = S.terrainEx; FP.dof.haze.uHazeD.value = 1 / (FX.haze.dist_km * 1000 * scale * MINI_LIFT.haze); FP.dof.haze.uHazeB.value = 1 / (FX.haze.height_m * scale * ex); FP.dof.haze.uHazeK.value = FX.haze.k; FP.dof.haze.uHazeS.value = FX.haze.start_km * 1000 * scale; FP.dof.haze.uHazeRect.value.copy(S.post.dof.haze ? S.post.dof.haze.uHazeRect.value : new THREE.Vector4(-PW / 2, -PD / 2, PW / 2, PD / 2)); FP.dof.haze.uHazeRect2.value.copy(S.post.dof.haze ? S.post.dof.haze.uHazeRect2.value : FP.dof.haze.uHazeRect.value); FP.dof.haze.uHazeEdge.value = FX.haze.edge_km * 1000 * scale; } }
  if (dome) { dome.mesh.layers.set(L); scene.add(dome.mesh); }
  const composer = new EffectComposer(renderer), rp = new RenderPass(scene, camera);
  const ht = new ShaderPass(HorizontalTiltShiftShader), vt = new ShaderPass(VerticalTiltShiftShader);
  const ao = new GTAOPass(scene, camera, 1920, 1080); ao.updateGtaoMaterial({ radius: .0012, distanceExponent: 1, thickness: 1, scale: 1.2 }); ao.blendIntensity = 1;
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

  async function render({ target, d }) {
    window.__MINI = { scene, camera, eraMeshes, cityMesh, plate, trees: () => TF.objs(), sun, target: target.clone(), d, swap, detail: DET };   // (for a script: tools that export the frame's geometry, swap)
    renderer.getDrawingBufferSize(size); pxK.value = camera.projectionMatrix.elements[5] * size.y / 2;
    if (DET) { for (const [id, E] of Object.entries(S.eras)) if (E.mesh.visible && !DET.has(id)) DET.set(id, detailOf(id));
      for (const [id, g] of DET) (await g).visible = S.eras[id].mesh.visible; }
    const swapM = [];   // (the studio's materials back after the frame)
    for (const m of [...eraMeshes, cityMesh]) if (m.visible && !m.userData.mini) m.userData.mini = m === cityMesh ? colourToday(m) : colourMesh(m, pal, !!DET, { face: face(idOf.get(m)), upright });   // (coloured when first shown)
    for (const m of [...eraMeshes, cityMesh, plate].filter(Boolean)) { if (!m.userData.mini) continue; swapM.push([m, m.material, m.customDepthMaterial]); m.material = m.userData.mini; m.customDepthMaterial = undefined; m.layers.enable(L); m.castShadow = m.receiveShadow = true; }
    { const src = [...eraMeshes.filter(m => m.visible), ...(cityMesh.visible ? [cityMesh] : [])]; for (const l of landmarks) l.traverse(o => { if (o.isMesh) src.push(o); });
      TF.update(target, d, src); }
    const v = camera.position.clone().sub(target), az = Math.atan2(v.x, v.z) + THREE.MathUtils.degToRad(SUN_SIDE), el = THREE.MathUtils.degToRad(SUN_EL), r = d * 1.2;   // the sun: behind the eye, to its left, 40 degrees up (fx light: lower)
    sun.position.set(target.x + r * Math.sin(az) * Math.cos(el), target.y + r * Math.sin(el), target.z + r * Math.cos(az) * Math.cos(el)); sun.target.position.copy(target);
    if (S.fxSun) sun.position.copy(target).addScaledVector(S.fxSun, r);   // (fx light: the sun fixed in the world, as the white model's)
    const c = sun.shadow.camera; c.left = c.bottom = -d * 1.6; c.right = c.top = d * 1.6; c.near = r * .2; c.far = r * 2.5; c.updateProjectionMatrix();
    const bg0 = scene.background, fog0 = scene.fog, lay0 = camera.layers.mask;
    scene.background = bg; fog.near = d * 1.6; fog.far = d * 8; scene.fog = FX && FX.haze ? null : fog; camera.layers.set(L);
    const sd = sun.position.clone().sub(target).normalize();
    if (relief) { U.uFxSun.value.copy(sd); if (FX.light) { U.uFxLitC.value.setRGB(1, 1, 1).lerp(new THREE.Color(1.1, .99, .84), warm); U.uFxShadeC.value.setRGB(1, 1, 1).lerp(new THREE.Color(.82, .9, 1.1), warm); } }
    if (dome) dome.u.uSunD.value.copy(sd);
    if (FP) {   // the film's lens for this distance (main.js lens), with the stronger depth of field
      if (lens) { lens(d); FP.dof.focus = S.post.dof.focus; FP.dof.aper = FX.dof ? S.post.dof.aper : 0; FP.dof.maxCoc = S.post.dof.maxCoc; FP.dof.band = S.post.dof.band; }
      if (FX.dof && !S.post.dof.rtB) fxLens(FP.dof, FX.dof, d);   // (the studio's own pass applied it already where it has the stronger gather)
      if (FP.dof.haze) FP.dof.haze.uHazeSunD.value.copy(sd);
      if (FP.dof.ao) FP.dof.ao.updateGtaoMaterial({ radius: fxAoRadius(d) });
    }
    renderer.getDrawingBufferSize(size); composer.setSize(size.x / renderer.getPixelRatio(), size.y / renderer.getPixelRatio());
    ht.uniforms.h.value = 4 / size.x; vt.uniforms.v.value = 4 / size.y; ht.uniforms.r.value = vt.uniforms.r.value = .5;
    ao.setSize(size.x, size.y); ao.updateGtaoMaterial({ radius: d * .02 });
    renderer.shadowMap.needsUpdate = true; (FP ? FP.composer : composer).render();
    scene.background = bg0; scene.fog = fog0; camera.layers.mask = lay0;
    for (const [m, mat, dm] of swapM) { m.material = mat; m.customDepthMaterial = dm; }
  }
  return { render, sun, sky, card: info, swap };
}
