// Detail on a period city's houses and walls, read from its records alone (pipeline/citygen.py, engine/props.js buildEra:
// [type, cx, cz, rot, y0, a, b, c, d, e, rank, part, ground, gx, gz, bx, bz, shape]) and drawn as instances: the generator's
// boxes stay as they are, and what a body, a wall piece or a tower is gives what it carries, in its region's way (STYLES):
// windows on every storey of its open faces, a door, a cornice under the eaves and a base at its foot (a Roman house); timber
// posts and a beam across the front its door opens in, a stone base, ornaments at the ends of its ridge (a Chinese hall); a
// small tiled coping on a yard wall; a city wall's courses as its face is built (WALL_FACES: the lifts of rammed earth, brick, stone,
// stone with bands of brick), windows high in a curtain wall's towers; a gate's passage arched at both ends, its gatehouse
// crenellated; a Chinese hall's columns lacquered and its beams painted. Nothing here knows a city: the same records of any city
// in a region get the same detail.
// eraDetail(prims, { scale, hex, style, face }) -> { kinds: { <kind>: { n, m: Float32Array (16 per instance), k: Float32Array (a
//   lightness each), ctr: Float32Array (its building's centre, x z), rank: Float32Array (its building's rank), base: Float32Array
//   (its record's ground, what the building rises from: aBase), src: Float32Array (its record's index, for its loss), size: the
//   piece's own size (model units: what detailMeshes fades it out by, as it gets too small to draw) } }, count }:
//   plain arrays, so any look draws them (detailMeshes: one InstancedMesh a kind, coloured by the look); ctr, rank and base are the
//   records' own (aCtr, aData.z, aBase), so a film that raises a city building by building raises these pieces with their building
//   (detailMeshes o.rise).
// hex: the period city's height exaggeration (city.yaml era `exaggeration`, film.json's era `exaggeration`; the generator's
// default 2): a storey's drawn height and every piece's height scale with it, widths do not. face: what the city's walls are
// faced with where its walls say (city.yaml walls `face`, film.json's era `wall_face`): else a battered wall's rammed earth and an
// upright one's its region's (STYLES wall).
import * as THREE from 'three';

const FAB = 0, LMK = 1, WALL = 2, DARK = 6, ROOF = 8, LROOF = 9;
// what a region's buildings carry, in metres (heights before the exaggeration). storey: a storey's height where the records do
// not say (a body's storeys: its height over this, rounded); window: { w, h, every (a window a bay this wide), sill (its foot
// above its storey's floor, a share of the storey), arch } as the generator draws a street front's (citygen house_body), null: none added (a Chinese hall's back and ends are blank: its
// openings are on its front, the generator's own); door: { w, h, arch }; cornice: { h, out } a band under the eaves; base: { h,
// out } a plinth course at the foot; front: { post, every, beam } timber posts and a beam across the face the generator opened
// (its door, its windows); ridgeEnds: ornaments at the ends of a ridge; coping: { h, over } a small roof on a yard wall;
// wall: what an upright city wall is faced with, where its walls do not say (WALL_FACES); towerWindows: { w, h, n } on each open face of a curtain wall's tower, high up; tiles: { every, w, t, verge: { w, t } } the
// rows of a tiled roof down each slope of a gable (筒瓦 rows, drawn wider and further apart than they are, so they read at a model's scale)
// and the heavier ridge down each of its gable edges (垂脊)
export const STYLES = {
  roman: {
    storey: 3.5, window: { w: 1.0, h: 1.5, every: 3.6, sill: .38, arch: true }, door: { w: 1.5, h: 2.5, arch: true },
    cornice: { h: .38, out: .22 }, base: { h: 1.0, out: .08 }, front: null, ridgeEnds: false, coping: { h: .32, over: .14 },
    wall: 'brick', towerWindows: { w: 1.3, h: 2.1, n: 2 }, tiles: null, halls: null,
    trees: { court: 2, street: 30, cypress: .5 }, tiles: { every: .9, w: .32, t: .14, verge: { w: .42, t: .3 } }, ridge: { w: .7, h: .5 },
    court: { arcade: { every: 3.0, out: 2.2, col: .55, h: 3.4, lintel: .55 }, beds: { n: 3, size: [3.2, 1.8] } }, paving: { every: 3.2, w: .14 },
    vary: { front: [6, 12], deep: 9, raise: [.45, .4], most: .4, storey: 3.2, gable: .45, over: .45, rise: .27,
      shops: { w: 2.3, h: 2.2, every: 3.4 }, pent: { out: 1.3, t: .22, tilt: .3 } }, flags: { gate: 4 },   // (a dense town's open ground stays its streets' and yards': no gardens)
  },
  chinese: {
    storey: 3.6, window: null, door: null, cornice: { h: .55, out: .45 }, base: { h: .6, out: .1 },   // (cornice: the eave's dark underside over the wall's top)
    front: { post: .34, every: 2.8, beam: .45 }, ridgeEnds: true, coping: { h: .42, over: .2 },
    wall: 'earth', towerWindows: null, tiles: { every: 1.1, w: .36, t: .16, verge: { w: .46, t: .34 } }, halls: { column: .65, beam: .7 },
    eaves: { out: 1.8, t: .35 }, ridge: { w: 1.1, h: .9 },
    trees: { court: 0, street: 12, cypress: .1, gardens: { every: 11, share: .15, reach: 70, size: [5, 3] } }, flags: { gate: 6 },
    court: { posts: { every: 2.8, out: 1.3, t: .32 }, lattice: { every: 3.0, w: 1.4, h: 1.3, sill: .9, door: [1.7, 2.5] }, hall: { lift: 1.6, over: 1.2, rise: .42 },
      gate: { w: 4.5, over: 1.0, rise: .5, lift: .9 }, path: 2.4, well: 1.5, patch: [4.5, 3], tree: 6 },
  },
};
// eaves: { out, t } a gable roof's eaves carried this far out past the generator's own overhang, this thick, down its slope; ridge:
// { w, h } a ridge this wide and high laid along its top (a Chinese roof, read from afar as a roof over its walls, not a slab on a ring)
// halls: { column, beam } a timber hall's (citygen hall) columns this thick and its architrave this high, in metres: the columns
// lacquered, the beam painted (a Chinese hall's); trees: { gardens: { every, share, reach, size } the town's open ground between its
// buildings planted, one place every `every` metres, `share` of them a tree (more in its groves and round its landmarks), within
// `reach` metres of a building, each rising with the nearest, its crown size[0] + up to size[1] metres (default 8 + 5); court: trees a court holds (the generator's own counted; on its paving
// too), street: one every this many metres down each edge of a street 10 m wide or more (0: none), cypress: the share of them
// tall and narrow }; flags: { gate: flags on a gatehouse, round its edges }, and one on each landmark
// vary: houses that differ as a real quarter's do, each from a hash of its place (the generator's records as they are, the colour
// look's): each open face of a body split into fronts front[0]..front[1] m wide, `deep` m deep at most; raise: the shares of
// them raised by none and by one storey (the rest by two) of `storey` m, never more than `most` of the body's height; each
// raised front in a wash of its own under a roof of its own, its gable to the street for `gable` of them (`over` m of eaves,
// `rise` its height over its span), with windows, courses, tiles and ridges as the generator's own; on every open face of a
// ground floor, shop openings (shops: w, h, every) and over half of them a pent roof of tiles (pent: out, t, tilt in radians)
// court: what a court shows, read from a building of three wings or more round a free middle (the colour look's: the generator's
// records unchanged): the face each wing turns to the middle; the wing with the generator's way in at its foot the gate's (else
// the smallest), the one farthest across the middle from it the hall's. posts { every, out, t } under the eaves along those faces;
// lattice { every, w, h, sill, door: [w, h] } windows on them and a door in their middle; hall { lift, over, rise } the hall
// raised by `lift` m under a roof `over` m wider each way, its rise a share of its depth; gate { w, over, rise, lift } a roofed
// gate over the way in; path (its width) paved from the gate to the hall; well (its width), patch [along, across] a vegetable
// patch, tree (a crown's metres): either side of the path; arcade { every, out, col, h, lintel } a colonnade round the court on
// its ground floor, `out` m deep under a tiled slab; beds { n, size } garden beds round the court's middle
// a city wall's face (city.yaml walls `face`): the courses it shows, every `every` metres, `h` high: rammed earth's lifts, brick's
// courses (faint), stone's, a stone wall's bands of brick
export const WALL_FACES = { earth: { every: 1.1, h: .1 }, brick: { every: .8, h: .07 }, stone: { every: 1.0, h: .06 }, banded: { every: 1.6, h: .32 } };
STYLES.roman.boats = { sail: true, cabin: false }; STYLES.chinese.boats = { sail: false, cabin: true };   // (a Roman river boat under a square sail; a Chinese one under its mat roof)
STYLES.modern = STYLES.roman;   // (the palette `modern`: a European town's houses)

// the pieces' shapes, each a unit: x across (-.5..5), y up (0..1), z out of the face (-.5..5; a flat one at z 0, facing +z)
function arched(top = .72, n = 7) {   // a window's or a door's opening, its head a half oval (the height exaggeration stretches it)
  const s = new THREE.Shape(); s.moveTo(-.5, 0); s.lineTo(.5, 0); s.lineTo(.5, top);
  for (let i = 1; i < n; i++) { const a = Math.PI * i / n; s.lineTo(.5 * Math.cos(a), top + (1 - top) * Math.sin(a)); }
  s.lineTo(-.5, top); s.closePath();
  return new THREE.ShapeGeometry(s, 1);
}
const box = () => new THREE.BoxGeometry(1, 1, 1).translate(0, .5, 0);
function roundCrown() {   // a tree's crown, round and full: its faces shaded as the sphere they stand for, not as facets
  const g = new THREE.IcosahedronGeometry(.345, 1).scale(1, .85, 1).translate(0, .62, 0), P = g.attributes.position, N = g.attributes.normal;
  for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = (P.getY(i) - .62) / .7225, z = P.getZ(i), l = Math.hypot(x, y, z) || 1; N.setXYZ(i, x / l, y / l, z / l); }
  return g;
}
function gableZGeometry() {   // a gable roof on a 1 x 1 base, 1 high, its ridge along z (a roof record's own frame: slopes across x)
  const P = [[-.5, 0, -.5], [-.5, 0, .5], [0, 1, .5], [0, 1, -.5], [.5, 0, -.5], [.5, 0, .5]], F = [[0, 1, 2, 3], [4, 3, 2, 5], [0, 3, 4], [1, 5, 2]], pos = [];
  for (const f of F) for (let i = 1; i < f.length - 1; i++) for (const j of [f[0], f[i], f[i + 1]]) pos.push(...P[j]);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals(); return g;
}
function hipGeometry() {   // a hipped roof on a 1 x 1 base, 1 high, its ridge along x over the middle half
  const P = [[-.5, 0, -.5], [.5, 0, -.5], [.5, 0, .5], [-.5, 0, .5], [-.25, 1, 0], [.25, 1, 0]], F = [[0, 4, 5, 1], [1, 5, 2], [2, 5, 4, 3], [3, 4, 0]], pos = [];
  for (const f of F) for (let i = 1; i < f.length - 1; i++) for (const j of [f[0], f[i + 1], f[i]]) pos.push(...P[j]);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals(); return g;
}
function leanGeometry() {   // a lean-to roof on a 1 x 1 base: high along -z, down to the eaves along +z
  const P = [[-.5, 1, -.5], [.5, 1, -.5], [.5, 0, .5], [-.5, 0, .5], [-.5, 0, -.5], [.5, 0, -.5]], F = [[0, 3, 2, 1], [4, 0, 1, 5], [0, 4, 3], [1, 2, 5]], pos = [];
  for (const f of F) for (let i = 1; i < f.length - 1; i++) for (const j of [f[0], f[i], f[i + 1]]) pos.push(...P[j]);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals(); return g;
}
function capGeometry() {   // a coping: a little roof along x, its section across z
  const s = new THREE.Shape(); s.moveTo(-.5, 0); s.lineTo(.5, 0); s.lineTo(.5, .3); s.lineTo(0, 1); s.lineTo(-.5, .3); s.closePath();
  return new THREE.ExtrudeGeometry(s, { depth: 1, bevelEnabled: false }).translate(0, 0, -.5).rotateY(Math.PI / 2);
}
function hornGeometry() {   // a ridge's end (a common house's 蠍子尾, simply): the ridge carried on past the gable and swept up and out, x along the ridge (out: +x)
  const s = new THREE.Shape(); s.moveTo(-.5, 0); s.lineTo(.15, 0); s.lineTo(.5, .62); s.lineTo(.62, 1); s.lineTo(.3, .96); s.lineTo(.02, .5); s.lineTo(-.5, .5); s.closePath();
  return new THREE.ExtrudeGeometry(s, { depth: 1, bevelEnabled: false }).translate(0, 0, -.5);
}
function spandrelGeometry(spring = .6, apex = .94, n = 9) {   // a passage's end above its arch: the wall's face across the corners, the arch cut out of it
  const s = new THREE.Shape(); s.moveTo(.5, spring); s.lineTo(.5, 1); s.lineTo(-.5, 1); s.lineTo(-.5, spring);
  for (let i = n - 1; i > 0; i--) { const a = Math.PI * i / n; s.lineTo(.5 * Math.cos(a), spring + (apex - spring) * Math.sin(a)); }
  s.closePath(); return new THREE.ShapeGeometry(s, 1);
}
function ringGeometry(spring = .6, apex = .94, band = .08, n = 9) {   // the arch's ring of voussoirs round it
  const s = new THREE.Shape(), pts = [];
  for (let i = 0; i <= n; i++) { const a = Math.PI * i / n; pts.push([(.5 + band) * Math.cos(a), spring + (apex - spring + band) * Math.sin(a)]); }
  s.moveTo(...pts[0]); for (const q of pts.slice(1)) s.lineTo(...q);
  for (let i = n; i >= 0; i--) { const a = Math.PI * i / n; s.lineTo(.5 * Math.cos(a), spring + (apex - spring) * Math.sin(a)); }
  s.closePath(); return new THREE.ShapeGeometry(s, 1);
}
export const SHAPES = { window: () => arched(), door: () => arched(.66), pane: () => new THREE.PlaneGeometry(1, 1).translate(0, .5, 0),
  spandrel: () => spandrelGeometry(), archRing: () => ringGeometry(), merlon: box, parapet: box, column: box,
  course_earth: box, course_brick: box, course_stone: box, course_banded: box,
  // a tree (fx.js plantTrees' own, 1 high): its round crown, a cypress's, its trunk; a flag on its pole, the cloth in the wind (+x)
  crown: () => roundCrown(), cone: () => new THREE.ConeGeometry(.15, 1.25, 7).translate(0, .72, 0),
  trunk: () => new THREE.CylinderGeometry(.055, .07, .45, 5).translate(0, .22, 0), pole: () => new THREE.CylinderGeometry(.5, .5, 1, 5).translate(0, .5, 0),
  flag: () => { const g = new THREE.PlaneGeometry(1, 1, 6, 1).translate(.5, -.5, 0), P = g.attributes.position; for (let i = 0; i < P.count; i++) P.setZ(i, Math.sin(P.getX(i) * 5.5) * .07 * P.getX(i)); g.computeVertexNormals(); return g; },
  // a boat: its hull (a long low shape pointed at both ends), a mast, a square sail across it, a mat roof over its middle
  hull: () => { const s = new THREE.Shape(); s.moveTo(-.5, 0); s.quadraticCurveTo(-.32, .5, 0, .5); s.quadraticCurveTo(.32, .5, .5, 0); s.quadraticCurveTo(.32, -.5, 0, -.5); s.quadraticCurveTo(-.32, -.5, -.5, 0);
    return new THREE.ExtrudeGeometry(s, { depth: 1, bevelEnabled: false, curveSegments: 4 }).rotateX(-Math.PI / 2); },
  mast: () => new THREE.CylinderGeometry(.5, .5, 1, 5).translate(0, .5, 0), sail: () => new THREE.PlaneGeometry(1, 1).translate(0, .5, 0).rotateY(Math.PI / 2),
  cabin: () => new THREE.CylinderGeometry(.5, .5, 1, 8, 1, false, 0, Math.PI).rotateZ(Math.PI / 2),   // (its arch over the top, along x)
  cornice: box, base: box, post: box, beam: box, course: box, coping: capGeometry, ridgeEnd: hornGeometry,
  joint: box, gableZ: () => gableZGeometry(), hip: () => hipGeometry(), lean: () => leanGeometry(), upper: box, shop: () => SHAPES.pane(), pent: box,
  lattice: () => SHAPES.pane(), leaf: () => SHAPES.pane(), hallroof: capGeometry, paving: box, patch: box, arcade: box, eaveslab: box,
  well: () => new THREE.CylinderGeometry(.5, .5, 1, 10).translate(0, .5, 0),
  tile: () => new THREE.BoxGeometry(1, 1, 1), verge: () => new THREE.BoxGeometry(1, 1, 1), eave: () => new THREE.BoxGeometry(1, 1, 1), ridge: () => new THREE.BoxGeometry(1, 1, 1) };   // (a row of tiles: x down the slope, y out of it, centred)
// which kinds cast a shadow (a flat opening or a thin course does not: it would only darken itself)
export const SHADOW = { eave: true, ridge: true, cornice: true, post: true, beam: true, coping: true, ridgeEnd: true, verge: true, merlon: true, parapet: true, column: true, hallroof: true, gableZ: true, hip: true, lean: true, upper: true, pent: true, arcade: true, eaveslab: true, well: true, crown: true, cone: true, trunk: true, pole: true, flag: true, hull: true, sail: true, cabin: true };

export function eraDetail(prims, { scale, hex = 2, style = 'roman', face = null } = {}) {
  const ST = STYLES[style] || STYLES.roman, M = scale, V = scale * hex;   // M: a metre across; V: a metre up, as drawn
  const R = prims.map((p, i) => ({ t: p[0], x: p[1], z: p[2], rot: p[3], y0: p[4], a: p[5], b: p[6], c: p[7], d: p[8], e: p[9], rank: p[10], part: p[11], g: p[12],
    gx: p[13] || 0, gz: p[14] || 0, bx: p[15] ?? p[1], bz: p[16] ?? p[2], i }));
  const out = {}, put = (kind, r, x, y, z, phi, sx, sy, sz, tilt = 0, k = 1, roll = 0) => (out[kind] ||= []).push([x, y, z, phi, sx, sy, sz, tilt, k, r.bx, r.bz, r.rank, roll, r.g ?? r.y0, r.i, r.t === 1 ? r.y0 : -1e9]);   // (last: a roof's eave, the piece's pivot in a close shot's height scale)
  const local = (r, X, Z) => { const c = Math.cos(r.rot), s = Math.sin(r.rot), dx = X - r.x, dz = Z - r.z; return [dx * c + dz * s, -dx * s + dz * c]; };
  const world = (r, lx, lz) => { const c = Math.cos(r.rot), s = Math.sin(r.rot); return [r.x + lx * c - lz * s, r.z + lx * s + lz * c]; };
  const shear = (r, X, Z) => r.gx * (X - r.x) + r.gz * (Z - r.z);
  const top = r => r.y0 + r.c, floor = r => Math.max(r.y0, r.g);   // (a body's foundation reaches below its ground: it is seen from its ground up)
  const hash = (x, z) => { const s = Math.sin(x * 127.1e3 + z * 311.7e3) * 43758.5453; return s - Math.floor(s); };

  // the solids a point outside a face may stand in (a neighbour's wall, a wing, the city wall a tower stands in): boxes, in cells
  const CELL = 16 * M, cells = new Map(), key = (i, j) => i * 73856093 ^ j * 19349663;
  for (const r of R) {
    if (r.t !== 0 || r.d === 1 || !(r.part === FAB || r.part === LMK || r.part === WALL) || Math.min(r.a, r.b) < .9 * M) continue;
    const h = Math.hypot(r.a, r.b) / 2;
    for (let i = Math.floor((r.x - h) / CELL); i <= Math.floor((r.x + h) / CELL); i++) for (let j = Math.floor((r.z - h) / CELL); j <= Math.floor((r.z + h) / CELL); j++) {
      const k = key(i, j); (cells.get(k) || cells.set(k, []).get(k)).push(r); }
  }
  const inside = (X, Y, Z, self) => { for (const r of cells.get(key(Math.floor(X / CELL), Math.floor(Z / CELL))) || []) {
    if (r === self || Y < r.y0 + shear(r, X, Z) || Y > top(r) + shear(r, X, Z)) continue;
    const [lx, lz] = local(r, X, Z); if (Math.abs(lx) < r.a / 2 && Math.abs(lz) < r.b / 2) return true; } return false; };
  // the openings the generator made, by building
  const darks = new Map(), bkey = r => r.bx.toFixed(6) + ',' + r.bz.toFixed(6);
  for (const r of R) if (r.part === DARK && r.t === 0) (darks.get(bkey(r)) || darks.set(bkey(r), []).get(bkey(r))).push(r);

  // a box's four faces: f 0 +x, 1 -x, 2 +z, 3 -z; each its width, its centre and outward normal (local), the turn that faces a piece out of it
  const FACES = [[1, 0, Math.PI / 2], [-1, 0, -Math.PI / 2], [0, 1, 0], [0, -1, Math.PI]];
  const faceOf = (r, f) => { const [nx, nz, turn] = FACES[f]; return { nx, nz, w: nx ? r.b : r.a, half: nx ? r.a / 2 : r.b / 2, phi: -r.rot + turn }; };
  const onFace = (r, F, s, o) => { const lx = F.nx ? F.nx * (F.half + o) : -F.nz * s, lz = F.nz ? F.nz * (F.half + o) : F.nx * s; return world(r, lx, lz); };   // the point s along face F (from its middle), o out of it

  // a street front split into narrow houses (STYLES vary): each open face of a body, `front` metres a house, some raised by a
  // storey or two (no more than `most` of the body's height) under a roof of their own, gable or eaves to the street; drawn
  // here as pieces, and added to the records as a body and a roof of their own, so the passes below give them what the
  // generator's own get: windows on every storey, a base course and a cornice, tile rows, ridges and verges
  if (ST.vary && ST.vary.front) {
    const VY = ST.vary, sv = VY.storey * V, gen = R.filter(r => r.t === 0 && r.part === FAB && r.d !== 1 && Math.min(r.a, r.b) >= 4 * M);
    const add = r => { R.push(r); const h = Math.hypot(r.a, r.b) / 2;
      for (let i = Math.floor((r.x - h) / CELL); i <= Math.floor((r.x + h) / CELL); i++) for (let j = Math.floor((r.z - h) / CELL); j <= Math.floor((r.z + h) / CELL); j++) { const k = key(i, j); (cells.get(k) || cells.set(k, []).get(k)).push(r); } };
    for (const b of gen) {
      const y0 = floor(b), Hm = (top(b) - y0) / V, most = Math.round(VY.most * Hm / VY.storey); if (most < 1) continue;
      for (let f = 0; f < 4; f++) {
        const F = faceOf(b, f), [px, pz] = onFace(b, F, 0, 1.2 * M); if (F.w < 8 * M || inside(px, y0 + 1 * V, pz, b)) continue;
        const deep = Math.min(2 * F.half, VY.deep * M), run = F.w - 2 * deep; if (run < VY.front[0] * M) continue;   // (the corners left to the body: a front from the next face would cross it)
        const n = Math.max(1, Math.round(run / ((VY.front[0] + (VY.front[1] - VY.front[0]) * hash(b.x * 2.9 + f, b.z)) * M))), w = run / n;
        for (let i = 0; i < n; i++) {
          const s_ = (i + .5 - n / 2) * w, hh = hash(b.x * 7.1 + s_ * 13.3, b.z * 3.7 + f), up = hh < VY.raise[0] ? 0 : hh < VY.raise[0] + VY.raise[1] ? 1 : 2, st = Math.min(up, most);
          if (!st) continue;
          const [X, Z] = onFace(b, F, s_, -deep / 2), along = F.nx !== 0;   // (a face across x runs along z)
          const A = along ? deep : w - .1 * M, Bz = along ? w - .1 * M : deep, c = st * sv, yb = top(b);
          const body = { t: 0, part: FAB, d: 0, x: X, z: Z, rot: b.rot, y0: yb, a: A, b: Bz, c, e: 0, rank: b.rank, g: b.g, gx: b.gx, gz: b.gz, bx: X, bz: Z, i: b.i, syn: true };
          add(body); put('upper', body, X, yb - .05 * V + shear(b, X, Z), Z, -b.rot, A, c + .05 * V, Bz);
          const toStreet = hash(X * 1.3, Z * 5.1) < VY.gable, ridgeX = toStreet ? !along : along;   // (the ridge across the face: its gable to the street)
          const ra = ridgeX ? Bz : A, rb = ridgeX ? A : Bz, rot = b.rot + (ridgeX ? Math.PI / 2 : 0), rc = ra * VY.rise * hex, od = VY.over * M, drop = od * rc / (ra / 2);
          const roof = { t: 1, part: ROOF, d: od, x: X, z: Z, rot, y0: yb + c, a: ra, b: rb, c: rc, e: 0, rank: b.rank, g: b.g, gx: b.gx, gz: b.gz, bx: X, bz: Z, i: b.i, syn: true };
          R.push(roof); put('gableZ', roof, X, yb + c - drop + shear(b, X, Z), Z, -rot, ra + 2 * od, rc + drop, rb + .3 * M);
        }
      }
    }
  }

  // a landmark's open ground paved in large slabs (ST.paving: their joints every `every` m, `w` m wide): on a low, wide platform,
  // and inside a court's ring (a prism piece: its walls stand over the joints under them)
  if (ST.paving) for (const r of R) {
    const low = r.t === 0 && (top(r) - floor(r)) / V <= 1.5, ring = r.t === 6;   // (a low platform, paved on top; a court's ring, paved inside on its ground)
    if (r.part !== LMK || r.d === 1 || !(low || ring) || r.a * r.b < 600 * M * M) continue;
    const P_ = ST.paving, e_ = P_.every * M, y = (low ? top(r) : floor(r)) + .02 * V;
    for (let s = -r.a / 2 + e_; s < r.a / 2; s += e_) { const [X, Z] = world(r, s, 0); put('joint', r, X, y + shear(r, X, Z), Z, -r.rot + Math.PI / 2, r.b, .03 * V, P_.w * M); }
    for (let s = -r.b / 2 + e_; s < r.b / 2; s += e_) { const [X, Z] = world(r, 0, s); put('joint', r, X, y + shear(r, X, Z), Z, -r.rot, r.a, .03 * V, P_.w * M); }
  }
  // ---------------------------------------------------------------- houses: the generator's bodies (a house's, a wing's, a hall's)
  const bodies = R.filter(r => r.t === 0 && r.part === FAB && r.d !== 1 && Math.min(r.a, r.b) >= 2.5 * M && (top(r) - floor(r)) / V >= 2.2);
  const byBuilding = new Map(); for (const b of bodies) (byBuilding.get(bkey(b)) || byBuilding.set(bkey(b), []).get(bkey(b))).push(b);
  for (const [k, list] of byBuilding) {
    const ds = darks.get(k) || [];
    const doored = ds.some(q => list.some(b => (q.y0 - floor(b)) / V < .6));   // (a way in already: the generator's door, gate, passage or shop front at the foot)
    // the generator's openings on each face of each body: [face] -> [{ s, w, y, h }] (s along the face, w its width; y its foot
    // above the floor and h its height, as drawn); an opening through the body (a gate's passage) on both its faces
    const opened = new Map();
    for (const b of list) opened.set(b, [0, 1, 2, 3].map(f => {
      const F = faceOf(b, f), got = [];
      for (const q of ds) {
        const [lx, lz] = local(b, q.x, q.z), dt = q.rot - b.rot, cs = Math.abs(Math.cos(dt)), sn = Math.abs(Math.sin(dt));
        const hx = cs * q.a / 2 + sn * q.b / 2, hz = sn * q.a / 2 + cs * q.b / 2;   // (its half sizes along the body's own axes)
        const across = F.nx ? lx * F.nx : lz * F.nz, along = F.nx ? lz * F.nx : -lx * F.nz, ha = F.nx ? hx : hz, hs = F.nx ? hz : hx;
        if (across + ha > F.half - .05 * M && across - ha < F.half + .6 * M && Math.abs(along) < F.w / 2 + .2 * M)
          got.push({ s: along, w: 2 * hs, y: q.y0 - floor(b), h: q.y0 + q.c - Math.max(q.y0, floor(b)) });
      }
      return got;
    }));
    // a door where the building has none: on its largest body's longest open face, in the middle
    let door = null;
    if (ST.door && !doored && !list[0].syn) {
      const b = list.reduce((m, q) => q.a * q.b > m.a * m.b ? q : m);
      const fs = [0, 1, 2, 3].sort((p, q) => faceOf(b, q).w - faceOf(b, p).w);
      for (const f of fs) { const F = faceOf(b, f), [X, Z] = onFace(b, F, 0, .8 * M);
        if (!inside(X, floor(b) + shear(b, X, Z) + 1.2 * V, Z, b)) { door = { b, f }; break; } }
    }
    for (const b of list) {
      const H = top(b) - floor(b), n = Math.max(1, Math.round(H / V / ST.storey)), sm = H / n;   // its storeys, as drawn
      for (let f = 0; f < 4; f++) {
        const F = faceOf(b, f), got = opened.get(b)[f], front = got.length > 0;
        const y0 = floor(b), yTop = top(b);
        // the foot's plinth course and the cornice: on every face (where a neighbour stands they are inside it, unseen)
        if (ST.base) { const [X, Z] = onFace(b, F, 0, ST.base.out / 2 * M); put('base', b, X, y0 + shear(b, X, Z), Z, F.phi, F.w + 2 * ST.base.out * M, ST.base.h * V, ST.base.out * 2 * M); }
        if (ST.cornice) { const [X, Z] = onFace(b, F, 0, ST.cornice.out / 2 * M); put('cornice', b, X, yTop - ST.cornice.h * V + shear(b, X, Z), Z, F.phi, F.w + 2 * ST.cornice.out * M, ST.cornice.h * V, ST.cornice.out * 2 * M); }
        // a Chinese front: posts between its openings, a beam under the eaves
        if (ST.front && front) {
          const P = ST.front, nb = Math.max(2, Math.round(F.w / M / P.every)), at = [];
          for (let i = 0; i <= nb; i++) at.push(-F.w / 2 + F.w * i / nb + (i === 0 ? P.post * M / 2 : i === nb ? -P.post * M / 2 : 0));
          for (const s of at) { if (got.some(o => Math.abs(o.s - s) < o.w / 2 + P.post * M * .6)) continue;
            const [X, Z] = onFace(b, F, s, P.post / 2 * M); put('post', b, X, y0 + shear(b, X, Z), Z, F.phi, P.post * M, H - P.beam * V * .5, P.post * M); }
          const [X, Z] = onFace(b, F, 0, P.post / 2 * M); put('beam', b, X, yTop - P.beam * V + shear(b, X, Z), Z, F.phi, F.w, P.beam * V, P.post * M * 1.1);
        }
        // windows: a row on each storey of an open face, the generator's rhythm (a window a bay of `every` metres), where it has none
        const isDoor = door && door.b === b && door.f === f;
        if (isDoor) { const [X, Z] = onFace(b, F, 0, .07 * M); put('door', b, X, y0 + shear(b, X, Z), Z, F.phi, ST.door.w * M, Math.min(ST.door.h * V, sm * .8), 1, 0, .9 + .2 * hash(X, Z)); }
        if (!ST.window) continue;
        const W = ST.window, kw = Math.max(1, Math.min(6, Math.floor(F.w / M / W.every))), ww = Math.min(W.w, F.w / M / kw * .4) * M, wh = Math.min(W.h * V, sm * .42);
        for (let s = 0; s < n; s++) {
          const yw = s * sm + sm * W.sill;
          if (got.filter(o => o.h < sm * .6 && o.y >= s * sm - .2 * V && o.y < (s + 1) * sm - .2 * V).length >= 2) continue;   // (the generator drew this row)
          for (let i = 0; i < kw; i++) {
            const at = -F.w / 2 + F.w * (i + .5) / kw;
            if (got.some(o => Math.abs(o.s - at) < (o.w + ww) / 2 + .3 * M && o.y < yw + wh && o.y + o.h > yw)) continue;   // (one of the generator's openings there)
            if (isDoor && s === 0 && Math.abs(at) < ST.door.w * M / 2 + ww * 1.2) continue;
            const [Xo, Zo] = onFace(b, F, at, .7 * M);
            if (inside(Xo, y0 + shear(b, Xo, Zo) + yw + wh / 2, Zo, b)) continue;   // (a neighbour's wall, a wing, before it)
            const [X, Z] = onFace(b, F, at, .07 * M);
            put('window', b, X, y0 + yw + shear(b, X, Z), Z, F.phi, ww, wh, 1, 0, .85 + .25 * hash(X, Z));
          }
        }
      }
    }
  }

  // ---------------------------------------------------------------- a tiled roof's rows and gable ridges; a ridge's ends; a yard wall's coping
  // a gable (engine/props.js Geo.gable: its span a across x, its ridge b long along z, c high over its eaves at y0, d of overhang):
  // on each slope a row of tiles every `every` metres along the ridge, eave to ridge, and a heavier one down each gable edge
  const tiled = r => r.part === ROOF || r.part === LROOF;   // (a house's roof, a landmark's: a roof of tiles either way)
  if (ST.tiles) for (const r of R) {
    if (r.t !== 1 || !tiled(r) || r.a < 2 * M || r.b < 2 * M) continue;
    const T = ST.tiles, run = r.a / 2 + r.d, drop = r.d * r.c / Math.max(1e-9, r.a / 2), rise = r.c + drop, L = Math.hypot(run, rise), al = Math.atan2(rise, run);
    const nU = run / L, nR = rise / L;   // (a slope's normal: up and out)
    for (const side of [-1, 1]) {
      const place = (kind, lz, w, t, k) => { const lx = side * (run / 2 + nR * t / 2), ly = (r.c - drop) / 2 + nU * t / 2, [X, Z] = world(r, lx, lz);
        put(kind, r, X, r.y0 + ly + shear(r, X, Z), Z, -r.rot, L, t, w, 0, k, -side * al); };
      const n = Math.floor((r.b - 2 * T.verge.w * M) / (T.every * M));
      for (let i = 0; i < n; i++) place('tile', -r.b / 2 + T.verge.w * M + (r.b - 2 * T.verge.w * M) * (i + .5) / n, T.w * M, T.t * M, 1);
      for (const e of [-1, 1]) place('verge', e * (r.b / 2 - T.verge.w * M / 2), T.verge.w * M, T.verge.t * M, 1);
    }
  }
  // a hipped roof's (engine/props.js Geo.frustum: a x b at its eaves, d x e at its top, c high): the rows down each of its four
  // slopes, shorter toward the hips (each ends where it meets one)
  if (ST.tiles) for (const r of R) {
    if (r.t !== 2 || !tiled(r) || Math.min(r.a, r.b) < 2 * M || (r.a - r.d) * (r.b - r.e) <= 0) continue;
    const T = ST.tiles;
    for (let f = 0; f < 4; f++) {
      const F = faceOf(r, f), top = F.nx ? r.d / 2 : r.e / 2, wt = F.nx ? r.e : r.d, run = F.half - top, L = Math.hypot(run, r.c);
      if (run <= .2 * M || L < 1 * M) continue;
      const nU = run / L, nO = r.c / L, th = -Math.atan2(run, r.c), n = Math.floor(F.w / (T.every * M));
      const row = (kind, s, w, t) => {
        const fm = Math.abs(s) <= wt / 2 ? 1 : Math.max(0, (F.w / 2 - Math.abs(s)) / Math.max(1e-9, (F.w - wt) / 2)); if (fm < .08) return;
        const fc = fm / 2, across = F.half - fc * run + nO * t / 2, lx = F.nx ? F.nx * across : -F.nz * s, lz = F.nz ? F.nz * across : F.nx * s, [X, Z] = world(r, lx, lz);
        put(kind, r, X, r.y0 + fc * r.c + nU * t / 2 + shear(r, X, Z), Z, F.phi, fm * L, w, t, th, 1, Math.PI / 2); };
      for (let i = 0; i < n; i++) row('tile', -F.w / 2 + F.w * (i + .5) / n, T.w * M, T.t * M);
    }
  }
  if (ST.eaves || ST.ridge) for (const r of R) {   // a gable's eaves carried out and its ridge on top (ST.eaves, ST.ridge)
    if (r.t !== 1 || !tiled(r) || r.a < 2 * M || r.b < 2 * M) continue;
    const run = r.a / 2 + r.d, drop = r.d * r.c / Math.max(1e-9, r.a / 2), rise = r.c + drop, L = Math.hypot(run, rise), al = Math.atan2(rise, run), nU = run / L, nR = rise / L;
    if (ST.eaves) { const o = ST.eaves.out * M, t = ST.eaves.t * V;
      for (const side of [-1, 1]) { const lx = side * (run + o / 2 * Math.cos(al) + nR * t / 2), ly = -drop - o / 2 * Math.sin(al) + nU * t / 2, [X, Z] = world(r, lx, 0);
        put('eave', r, X, r.y0 + ly + shear(r, X, Z), Z, -r.rot, o, t, r.b + o, 0, 1, -side * al); } }
    if (ST.ridge) { const [X, Z] = world(r, 0, 0); put('ridge', r, X, r.y0 + r.c + ST.ridge.h * V / 2 + shear(r, X, Z), Z, -r.rot, ST.ridge.w * M, ST.ridge.h * V, r.b + (ST.eaves ? ST.eaves.out * M * .5 : 0)); }
  }
  if (ST.ridgeEnds) for (const r of R) {
    if (r.t !== 0 || r.part !== ROOF || r.a < 3 * M || r.b > .7 * M || r.c > 2.5 * V || r.a < r.b * 5) continue;
    for (const sgn of [-1, 1]) { const [X, Z] = world(r, sgn * (r.a / 2 - .25 * M), 0);
      put('ridgeEnd', r, X, top(r) - .15 * V + shear(r, X, Z), Z, -r.rot + (sgn > 0 ? 0 : Math.PI), .6 * M, .85 * V, r.b * 1.1); }
  }
  if (ST.coping) for (const r of R) {
    if (r.t !== 0 || r.part !== FAB || r.d === 1) continue;
    const thin = Math.min(r.a, r.b), long = Math.max(r.a, r.b), hm = (top(r) - floor(r)) / V;
    if (thin > .8 * M || long < 1.2 * M || hm < .5 || hm > 5) continue;
    const along = r.a >= r.b, [X, Z] = [r.x, r.z];
    put('coping', r, X, top(r) + shear(r, X, Z), Z, -r.rot + (along ? 0 : Math.PI / 2), long + .1 * M, ST.coping.h * V, thin + 2 * ST.coping.over * M);
  }

  // ---------------------------------------------------------------- city walls: courses; windows high in a curtain's towers
  const faceOfWall = battered => face || (battered ? 'earth' : ST.wall);   // (what a wall piece is faced with)
  for (const r of R) {
    if (r.part !== WALL || !(r.t === 0 || r.t === 2) || r.d === 1) continue;
    const y0 = r.y0, h = r.c, g = r.g, faces = r.t === 0 && Math.abs(r.a - r.b) < .5 * Math.max(r.a, r.b) ? [0, 1, 2, 3] : [2, 3];   // (a tower: all round; a wall piece: its two long faces)
    if (Math.min(r.a, r.b) < 1.5 * M || (top(r) - Math.max(y0, g)) / V < 2.5) continue;   // (not a parapet, a merlon)
    const battered = r.t === 2, tower = faces.length === 4, fk = faceOfWall(battered), CO = WALL_FACES[fk];
    for (const f of faces) {
      const F = faceOf(r, f), lean = battered ? Math.atan2((F.nx ? r.a - r.d : r.b - r.e) / 2, h) : 0;   // (a battered face leans in as it rises)
      for (let y = g + CO.every * V; y < top(r) - .4 * V; y += CO.every * V) {
        const fr = (y - y0) / h, half = battered ? F.half + ((F.nx ? r.d : r.e) / 2 - F.half) * fr : F.half, w = battered ? F.w + ((F.nx ? r.e : r.d) - F.w) * fr : F.w;
        const lx = F.nx ? F.nx * (half + .02 * M) : 0, lz = F.nz ? F.nz * (half + .02 * M) : 0, [X, Z] = world(r, lx, lz);
        put('course_' + fk, r, X, y + shear(r, X, Z), Z, F.phi, w + .04 * M, CO.h * V, .06 * M, -lean, .9 + .2 * hash(X, y));
      }
    }
    if (tower && ST.towerWindows && !battered && r.c > 0) {
      const TW = ST.towerWindows, yw = top(r) - (TW.h + 1.6) * V;
      if (yw - Math.max(y0, g) < 2 * V) continue;
      for (const f of faces) { const F = faceOf(r, f);
        for (let i = 0; i < TW.n; i++) { const s = F.w * ((i + .5) / TW.n - .5) * .6, [Xo, Zo] = onFace(r, F, s, .8 * M);
          if (inside(Xo, yw + TW.h * V / 2, Zo, r)) continue;
          const [X, Z] = onFace(r, F, s, .05 * M); put('window', r, X, yw + shear(r, X, Z), Z, F.phi, TW.w * M, TW.h * V, 1, 0, .8); } }
    }
  }

  // ---------------------------------------------------------------- gates: a passage (a dark box the generator cut through a
  // wall piece of its own building, citygen walls) arched at both its ends, the wall's face across the corners above the arch
  // and a ring of voussoirs round it; its gatehouse crenellated along both its long edges (a parapet, merlons), a curtain's
  // with windows high above the passage
  const wallsOf = new Map();
  for (const r of R) if (r.part === WALL && r.t === 0 && Math.min(r.a, r.b) >= 1.5 * M) (wallsOf.get(bkey(r)) || wallsOf.set(bkey(r), []).get(bkey(r))).push(r);
  const gated = new Set(), passages = new Map();   // (a gate built again higher on the same place, a wall raised: its tallest passage alone, arched)
  for (const q of R) {
    if (q.part !== DARK || q.t !== 0) continue;
    const host = (wallsOf.get(bkey(q)) || []).find(r => { const [lx, lz] = local(r, q.x, q.z); return Math.abs(lx) < r.a / 2 && Math.abs(lz) < r.b / 2 && q.b > r.b * .8; });
    if (!host) continue;
    const pk = Math.round(q.x / (2 * M)) + ',' + Math.round(q.z / (2 * M)), was = passages.get(pk);
    if (!was || top(q) > top(was[0])) passages.set(pk, [q, host]);
  }
  for (const [q, host] of passages.values()) {
    const fl = Math.max(q.y0, floor(host)), H = top(q) - fl, fk = faceOfWall(false);
    for (const e of [-1, 1]) {   // (each end of the passage, out of the gatehouse's face)
      const [X, Z] = world(q, 0, e * (q.b / 2 + .03 * M)), phi = -q.rot + (e > 0 ? 0 : Math.PI);
      put('spandrel_' + fk, q, X, fl + shear(q, X, Z), Z, phi, q.a, H, 1);
      const [X2, Z2] = world(q, 0, e * (q.b / 2 + .05 * M)); put('archRing', q, X2, fl + shear(q, X2, Z2), Z2, phi, q.a, H, 1);
    }
    if (gated.has(host)) continue; gated.add(host);
    const lng = host.a >= host.b, L = lng ? host.a : host.b, Tk = lng ? host.b : host.a, ph = -host.rot + (lng ? 0 : Math.PI / 2), yt = top(host);
    for (const side of [-1, 1]) {   // (both long edges: the field side and the city's)
      const off = side * (Tk / 2 - .4 * M), [PX, PZ] = world(host, lng ? 0 : off, lng ? off : 0);
      put('parapet_' + fk, host, PX, yt + shear(host, PX, PZ), PZ, ph, L, .9 * V, .8 * M);
      const nm = Math.max(2, Math.floor(L / M / 2.8));
      for (let i = 0; i < nm; i++) { const a_ = L * ((i + .5) / nm - .5), [X, Z] = world(host, lng ? a_ : off, lng ? off : a_);
        put('merlon_' + fk, host, X, yt + .9 * V + shear(host, X, Z), Z, ph, 1.4 * M, 1.0 * V, .8 * M); }
    }
    if (ST.towerWindows) {   // (a curtain's gatehouse: two arched windows on each long face, over the passage)
      const TW = ST.towerWindows, yw = yt - (TW.h + 1.6) * V;
      if (yw > top(q) + .6 * V) for (const f of (lng ? [2, 3] : [0, 1])) { const F = faceOf(host, f);
        for (const s_ of [-.28, .28]) { const [X, Z] = onFace(host, F, F.w * s_, .05 * M); put('window', host, X, yw + shear(host, X, Z), Z, F.phi, TW.w * M, TW.h * V, 1, 0, .8); } }
    }
  }

  // ---------------------------------------------------------------- a timber hall's columns lacquered, its architrave painted
  if (ST.halls) for (const r of R) {
    if (r.part !== LMK || r.t !== 0) continue;
    const HL = ST.halls;
    if (Math.abs(r.a - HL.column * M) < .06 * M && Math.abs(r.b - HL.column * M) < .06 * M && r.c > 1.5 * V)
      put('column', r, r.x, floor(r) + shear(r, r.x, r.z), r.z, -r.rot, (HL.column + .08) * M, top(r) - floor(r), (HL.column + .08) * M);
    else if (Math.abs(r.c - HL.beam * V) < .04 * V && Math.min(r.a, r.b) > 3 * M)
      put('beam', r, r.x, r.y0 - .02 * V + shear(r, r.x, r.z), r.z, -r.rot, r.a + .06 * M, r.c + .04 * V, r.b + .06 * M);
  }

  // ---------------------------------------------------------------- where no tree stands: a band along every city wall piece and
  // tower as deep as it is high (as drawn), inside and out, and each gate's approach, out on both sides of its passage as far as
  // twice the band; rects [x, z, rot, half width, half depth] (model units), with the test the planting of every tree takes
  const clear = [];
  for (const r of R) {
    if (r.part !== WALL || !(r.t === 0 || r.t === 2) || r.d === 1 || Math.min(r.a, r.b) < 1.5 * M) continue;
    const hh = top(r) - floor(r); if (hh / V < 2.5) continue;
    const band = Math.max(hh, 10 * M); clear.push([r.x, r.z, r.rot, r.a / 2 + band, r.b / 2 + band]);
  }
  for (const [q, host] of passages.values()) {   // (each gate's passage: its approach)
    const band = Math.max(top(host) - floor(host), 10 * M); clear.push([q.x, q.z, q.rot, q.a / 2 + 8 * M, q.b / 2 + 2 * band + 12 * M]);
  }
  const CC = 40 * M, ccells = new Map();
  for (const c of clear) { const h = Math.hypot(c[3], c[4]);
    for (let i = Math.floor((c[0] - h) / CC); i <= Math.floor((c[0] + h) / CC); i++) for (let j = Math.floor((c[1] - h) / CC); j <= Math.floor((c[1] + h) / CC); j++) {
      const k = key(i, j); (ccells.get(k) || ccells.set(k, []).get(k)).push(c); } }
  const treeOK = (X, Z) => { for (const c of ccells.get(key(Math.floor(X / CC), Math.floor(Z / CC))) || []) {
    const cs = Math.cos(c[2]), sn = Math.sin(c[2]), dx = X - c[0], dz = Z - c[1];
    if (Math.abs(dx * cs + dz * sn) < c[3] && Math.abs(-dx * sn + dz * cs) < c[4]) return false; } return true; };

  // ---------------------------------------------------------------- trees in town: in the courts of houses round a court, along
  // the streets, never in a wall's band or a gate's approach (treeOK), on a building or a street (any piece's plan, with room for
  // the crown); a court's trees as many as its region's style gives, the generator's own counted
  const solid = new Map(), SC = 16 * M;   // (every piece's plan but a tree's and the water's)
  for (const r of R) {
    if (r.part === 4 || r.part === 5 || !(r.t === 0 || r.t === 1 || r.t === 2)) continue;
    const h = Math.hypot(r.a, r.b) / 2;
    for (let i = Math.floor((r.x - h) / SC); i <= Math.floor((r.x + h) / SC); i++) for (let j = Math.floor((r.z - h) / SC); j <= Math.floor((r.z + h) / SC); j++) {
      const k = key(i, j); (solid.get(k) || solid.set(k, []).get(k)).push(r); }
  }
  const free = (X, Z, rr) => { for (let a = 0; a < 9; a++) { const x = a ? X + Math.cos(a * Math.PI / 4) * rr : X, z = a ? Z + Math.sin(a * Math.PI / 4) * rr : Z;   // (paving does not stop a tree: a court's, a street's edge)
      for (const r of solid.get(key(Math.floor(x / SC), Math.floor(z / SC))) || []) { if (r.part === 7) continue; const [lx, lz] = local(r, x, z); if (Math.abs(lx) < r.a / 2 && Math.abs(lz) < r.b / 2) return false; } }
    return treeOK(X, Z); };
  const TR = ST.trees, gTrees = new Map();   // (the generator's own trees, by building)
  for (const r of R) if (r.part === 4) gTrees.set(bkey(r), (gTrees.get(bkey(r)) || 0) + 1);
  const tree = (r, X, Z, size, tier = '') => { const cyp = hash(X * 3.1, Z * 1.7) < TR.cypress, sz = size * (.85 + .3 * hash(Z, X)), g = r.g + shear(r, X, Z);   // (tier: a garden tree's, _g1 or _g2: gone sooner afar)
    put((cyp ? 'cone' : 'crown') + tier, r, X, g, Z, hash(X, Z) * 6.28, sz, sz * (cyp ? 1.15 : .9 + .25 * hash(X * 2, Z)), sz, 0, .85 + .3 * hash(X * 5, Z * 3));
    put('trunk' + tier, r, X, g, Z, 0, sz, sz, sz); };
  if (TR) {
    for (const [k, list] of byBuilding) {   // (a court: a building of three wings or more round a free middle)
      if (list.length < 3 || (gTrees.get(k) || 0) >= TR.court) continue;
      const b0 = list.reduce((m, q) => q.a * q.b > m.a * m.b ? q : m), X0 = b0.bx, Z0 = b0.bz, want = TR.court - (gTrees.get(k) || 0);
      let rr = 0; while (rr < 14 * M && free(X0, Z0, rr + 1 * M)) rr += 1 * M;   // (the court's room round its middle)
      const at = rr >= 3.5 * M && want === 1 ? [[X0, Z0, rr]] : [];
      if (!at.length) for (const [ox, oz] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1]]) {   // (two to a court, or a small court: either side of its middle)
        const [X, Z] = world(b0, ox * 3.2 * M, oz * 3.2 * M); if (free(X, Z, 2.2 * M) && at.every(([x, z]) => Math.hypot(x - X, z - Z) > 4 * M)) at.push([X, Z, 2.2 * M]); if (at.length >= want) break; }
      for (const [X, Z, room] of at.slice(0, want)) tree(b0, X, Z, Math.min(11 * M, room * 2.6) * .8);
    }
    if (TR.gardens) {   // (the open ground between the buildings: gardens and groves, off the streets and squares, each tree rising with its nearest building)
      const G = TR.gardens, step = G.every * M, reach = G.reach * M, homes = R.filter(r => r.t === 0 && (r.part === FAB || r.part === LMK) && r.d !== 1);
      if (homes.length) {
        const HC = 32 * M, hc = new Map(); for (const r of homes) { const k = key(Math.floor(r.x / HC), Math.floor(r.z / HC)); (hc.get(k) || hc.set(k, []).get(k)).push(r); }
        const near = (X, Z) => { let best = null, bd = reach; const i0 = Math.floor(X / HC), j0 = Math.floor(Z / HC), n = Math.ceil(reach / HC);
          for (let i = i0 - n; i <= i0 + n; i++) for (let j = j0 - n; j <= j0 + n; j++) for (const r of hc.get(key(i, j)) || []) { const dd = Math.hypot(r.x - X, r.z - Z) - Math.max(r.a, r.b) / 2; if (dd < bd) { bd = dd; best = r; } }
          return best; };
        const street = (X, Z) => { for (const r of solid.get(key(Math.floor(X / SC), Math.floor(Z / SC))) || []) { if (r.part !== 7) continue; const [lx, lz] = local(r, X, Z); if (Math.abs(lx) < r.a / 2 + 2 * M && Math.abs(lz) < r.b / 2 + 2 * M) return true; } return false; };
        const xs = homes.map(r => r.x), zs = homes.map(r => r.z), x0 = Math.min(...xs) - reach, x1 = Math.max(...xs) + reach, z0 = Math.min(...zs) - reach, z1 = Math.max(...zs) + reach;
        for (let gx = Math.floor(x0 / step); gx <= Math.ceil(x1 / step); gx++) for (let gz = Math.floor(z0 / step); gz <= Math.ceil(z1 / step); gz++) {
          const X = (gx + .2 + .6 * hash(gx * 1.3, gz * .7)) * step, Z = (gz + .2 + .6 * hash(gx * .9, gz * 1.9)) * step;
          const grove = .5 + .5 * Math.sin(X / M / 61 + Math.sin(Z / M / 47) * 1.7) * Math.sin(Z / M / 53 + Math.sin(X / M / 71) * 1.3);
          const h = near(X, Z); if (!h) continue;
          const gr = THREE.MathUtils.smoothstep(grove, .45, .8);   // (in groves and orchards, a few alone between them)
          if (hash(X * 7.7, Z * 3.3) > G.share * (.15 + 2.6 * gr) * (h.part === LMK ? 2 : 1) || street(X, Z) || !free(X, Z, 3 * M)) continue;
          const th = hash(X * 1.9, Z * 4.3);   // (afar fewer: half gone by the time a tree is 7 px, three in ten more by 11 px, the roofs read first)
          tree(h, X, Z, ((G.size || [8, 5])[0] + (G.size || [8, 5])[1] * hash(Z * 2.1, X)) * (.8 + .35 * gr) * M, th < .5 ? '_g1' : th < .8 ? '_g2' : '');
        }
      }
    }
    if (ST.vary) for (const [k, list] of byBuilding) {   // a ground floor's open faces: shops, and over some a pent roof of tiles (STYLES vary)
      const VY = ST.vary;
      for (const b of list) {
        if (b.syn) continue;   // (a front raised by `vary`: its ground floor is the body's below it)
        const y0 = floor(b);
        for (let f = 0; f < 4; f++) {
          const F = faceOf(b, f), [px, pz] = onFace(b, F, 0, 1.2 * M); if (inside(px, y0 + 1 * V, pz, b) || F.w < 4 * M) continue;
          if (VY.shops) { const S_ = VY.shops, n = Math.max(1, Math.floor(F.w / (S_.every * M)));
            for (let i = 0; i < n; i++) { const [X, Z] = onFace(b, F, (i + .5 - n / 2) * S_.every * M, .05 * M); put('shop', b, X, y0 + shear(b, X, Z), Z, F.phi, S_.w * M, S_.h * V, 1, 0, .8 + .3 * hash(X, Z)); } }
          if (VY.pent && hash(b.x + f, b.z) < .5) { const P_ = VY.pent, [X, Z] = onFace(b, F, 0, P_.out * M / 2);
            put('pent', b, X, y0 + (VY.shops ? VY.shops.h : 2.4) * V + .5 * V + shear(b, X, Z), Z, F.phi, F.w, P_.t * V, P_.out * M, P_.tilt); }
        }
      }
    }
    if (ST.court) for (const [k, list] of byBuilding) {   // a court's inside (STYLES court)
      if (list.length < 3) continue;
      const CS = ST.court, X0 = list[0].bx, Z0 = list[0].bz, y = Math.min(...list.map(floor));
      if (inside(X0, y + 1 * V, Z0, null)) continue;   // (its middle free)
      const room = (ux, uz) => { let r = 0; while (r < 30 * M && !inside(X0 + ux * (r + .5 * M), y + 1 * V, Z0 + uz * (r + .5 * M), null)) r += .5 * M; return r; };
      const W = list.map(b => { const [lx, lz] = local(b, X0, Z0), f = Math.abs(lx) / b.a > Math.abs(lz) / b.b ? (lx > 0 ? 0 : 1) : (lz > 0 ? 2 : 3), F = faceOf(b, f);
        return { b, F, gap: (F.nx ? Math.abs(lx) : Math.abs(lz)) - F.half }; });   // (gap: from the face to the middle)
      const gq = (darks.get(k) || []).filter(q => (q.y0 - y) / V < .6).sort((p, q) => q.a * q.b - p.a * p.b)[0];
      const away = (w, q) => { const [lx, lz] = local(w.b, q.x, q.z); return Math.max(Math.abs(lx) - w.b.a / 2, Math.abs(lz) - w.b.b / 2); };
      const gate = gq ? W.reduce((m, w) => away(w, gq) < away(m, gq) ? w : m) : W.reduce((m, w) => w.b.a * w.b.b < m.b.a * m.b.b ? w : m);
      const hall = W.filter(w => w !== gate).reduce((m, w) => Math.hypot(w.b.x - gate.b.x, w.b.z - gate.b.z) > Math.hypot(m.b.x - gate.b.x, m.b.z - gate.b.z) ? w : m, W.find(w => w !== gate));
      for (const w of W) {
        const { b, F } = w, y0 = floor(b), H = top(b) - y0;
        if (CS.posts && w.gap > (CS.posts.out + 1) * M) { const P = CS.posts, n = Math.max(1, Math.round(F.w / (P.every * M)));
          for (let i = 0; i <= n; i++) { const [X, Z] = onFace(b, F, (i / n - .5) * (F.w - P.t * M), P.out * M); if (!inside(X, y0 + 1 * V, Z, b)) put('post', b, X, y0 + shear(b, X, Z), Z, F.phi, P.t * M, H * .9, P.t * M); }
          const [X, Z] = onFace(b, F, 0, P.out * M); put('beam', b, X, y0 + H * .9 - .45 * V + shear(b, X, Z), Z, F.phi, F.w, .45 * V, P.t * M * 1.3); }
        if (CS.lattice && w.gap > 1.5 * M) { const L_ = CS.lattice, n = Math.max(1, Math.floor(F.w / (L_.every * M))), mid = Math.floor(n / 2);
          for (let i = 0; i < n; i++) { const s_ = (i + .5 - n / 2) * L_.every * M, [X, Z] = onFace(b, F, s_, .06 * M); if (inside(X, y0 + 1 * V, Z, b)) continue;
            if (i === mid) put('leaf', b, X, y0 + shear(b, X, Z), Z, F.phi, L_.door[0] * M, L_.door[1] * V, 1);
            else put('lattice', b, X, y0 + L_.sill * V + shear(b, X, Z), Z, F.phi, L_.w * M, L_.h * V, 1); } }
        if (CS.arcade && w.gap > (CS.arcade.out + 1.5) * M) { const A_ = CS.arcade, h = A_.h * V, n = Math.max(1, Math.round(F.w / (A_.every * M)));
          for (let i = 0; i <= n; i++) { const [X, Z] = onFace(b, F, (i / n - .5) * (F.w - A_.col * M), A_.out * M); if (!inside(X, y0 + 1 * V, Z, b)) put('arcade', b, X, y0 + shear(b, X, Z), Z, F.phi, A_.col * M, h, A_.col * M); }
          const [X, Z] = onFace(b, F, 0, A_.out * M / 2); put('arcade', b, X, y0 + h + shear(b, X, Z), Z, F.phi, F.w, A_.lintel * V, A_.out * M + A_.col * M);
          put('eaveslab', b, X, y0 + h + A_.lintel * V + shear(b, X, Z), Z, F.phi, F.w, .3 * V, A_.out * M + A_.col * M + .4 * M); }
      }
      const raise = (b, X, Z, len, dep, along, o) => { const phi = -b.rot + (along ? 0 : Math.PI / 2), y1 = top(b) + o.lift * V + shear(b, X, Z);
        put('beam', b, X, top(b) + shear(b, X, Z), Z, phi, len * .96, o.lift * V, dep * .86);
        put('hallroof', b, X, y1, Z, phi, len + 2 * o.over * M, dep * o.rise * hex, dep + 2 * o.over * M); };
      if (CS.hall && hall) {   // (a second, higher roof over the hall's own ridge, on a timber storey: the hall the court's tallest, its tiles kept)
        const b = hall.b, along = b.a >= b.b, [X, Z] = world(b, 0, 0), len = along ? b.a : b.b, dep = along ? b.b : b.a, phi = -b.rot + (along ? 0 : Math.PI / 2);
        const rf = R.find(r => r.t === 1 && tiled(r) && Math.hypot(r.x - b.x, r.z - b.z) < .5 * Math.min(b.a, b.b)), apex = rf ? rf.y0 + rf.c : top(b) + .3 * dep * hex, rise = apex - top(b), o = CS.hall;
        put('beam', b, X, apex - .35 * rise + shear(b, X, Z), Z, phi, len * .62, .35 * rise + o.lift * V, dep * .42);
        put('hallroof', b, X, apex + o.lift * V + shear(b, X, Z), Z, phi, len * .72 + 2 * o.over * M, rise * o.rise / .42, dep * .58 + 2 * o.over * M); }
      if (CS.gate) { const b = gate.b, along = b.a >= b.b, [lx, lz] = gq ? local(b, gq.x, gq.z) : [0, 0], [X, Z] = world(b, along ? lx : 0, along ? 0 : lz);
        raise(b, X, Z, CS.gate.w * M, along ? b.b : b.a, along, CS.gate); }
      if (hall && hall !== gate && (CS.path || CS.well || CS.patch)) {
        const [ax, az] = onFace(gate.b, gate.F, 0, 0), [hx, hz] = onFace(hall.b, hall.F, 0, CS.posts ? CS.posts.out * M : 0), dx = hx - ax, dz = hz - az, Ln = Math.hypot(dx, dz), ux = dx / Ln, uz = dz / Ln, phi = Math.atan2(-dz, dx);
        const rv = Math.min(room(-uz, ux), room(uz, -ux));
        if (CS.path) put('paving', gate.b, (ax + hx) / 2, y + shear(gate.b, (ax + hx) / 2, (az + hz) / 2), (az + hz) / 2, phi, Ln, .12 * V, CS.path * M);
        if (rv > 2.5 * M) {
          const at = (fv, fu) => [X0 - uz * rv * fv + ux * Ln * fu, Z0 + ux * rv * fv + uz * Ln * fu];
          if (CS.well) { const [X, Z] = at(.5, .15), w_ = Math.min(CS.well * M, rv * .45); put('well', gate.b, X, y + shear(gate.b, X, Z), Z, 0, w_, .9 * V, w_); }
          if (CS.patch) { const [X, Z] = at(-.5, -.1); put('patch', gate.b, X, y + shear(gate.b, X, Z), Z, phi, Math.min(CS.patch[0] * M, Ln * .4), .25 * V, Math.min(CS.patch[1] * M, rv * .6)); }
          if (CS.tree) { const [X, Z] = at(.55, -.25); tree(hall.b, X, Z, Math.min(CS.tree * M, rv * 1.1)); }
        }
      }
      if (CS.beds) { const rr = Math.min(room(1, 0), room(-1, 0), room(0, 1), room(0, -1));
        if (rr > 2.5 * M) for (let i = 0; i < CS.beds.n; i++) { const th = list[0].rot + i * 2 * Math.PI / CS.beds.n + .5, X = X0 + Math.cos(th) * rr * .5, Z = Z0 + Math.sin(th) * rr * .5;
          put('patch', list[0], X, y + shear(list[0], X, Z), Z, -th, Math.min(CS.beds.size[0] * M, rr * .5), .35 * V, Math.min(CS.beds.size[1] * M, rr * .3)); } }
    }
    if (TR.street) for (const r of R) {   // (a street: a road piece, citygen strip; its trees down its edges, the way between them clear)
      if (r.t !== 0 || r.d !== 1 || r.b < 10 * M || r.a < TR.street * M * .6) continue;
      const n = Math.max(1, Math.floor(r.a / (TR.street * M)));
      for (const side of [-1, 1]) for (let i = 0; i < n; i++) {
        const along = r.a * ((i + .5 + (side > 0 ? .5 : 0)) / n - .5); if (Math.abs(along) > r.a / 2) continue;
        const [X, Z] = world(r, along, side * (r.b / 2 - 2 * M));
        if (free(X, Z, 2 * M)) tree(r, X, Z, 8 * M);
      }
    }
  }

  // ---------------------------------------------------------------- flags: on each gatehouse (its outer corners and between), and
  // one on each landmark at its highest point, the cloth all one way in the wind
  const WIND = -Math.PI / 6;   // (a turn about y: the cloth's +x toward the east-north-east)
  const flag = (r, X, Y, Z, h) => { put('pole', r, X, Y, Z, 0, .22 * M, h, .22 * M); put('flag', r, X, Y + h, Z, WIND, 4.5 * M, 1.5 * V, 4.5 * M, 0, .9 + .2 * hash(X, Z)); };   // (a banner as a model shows one, larger than life; its wave as deep as the cloth is long allows)
  if (ST.flags) {
    for (const host of gated) {
      const lng = host.a >= host.b, L = lng ? host.a : host.b, Tk = lng ? host.b : host.a, n = ST.flags.gate, per = Math.ceil(n / 2);
      for (let i = 0; i < n; i++) { const side = i < per ? 1 : -1, j = i % per, a_ = L * (per > 1 ? j / (per - 1) - .5 : 0) * .92, off = side * (Tk / 2 - .5 * M), [X, Z] = world(host, lng ? a_ : off, lng ? off : a_);
        flag(host, X, top(host) + .9 * V + shear(host, X, Z), Z, 4.5 * V); }   // (half along its field side, half along the city's)
      for (const r of R) {   // (and on the towers either side of it, which stand above it: a curtain's)
        if (r.part !== WALL || r.t !== 0 || Math.abs(r.a - r.b) > .5 * Math.max(r.a, r.b) || top(r) <= top(host) || Math.min(r.a, r.b) < 3 * M) continue;
        const [lx, lz] = local(host, r.x, r.z); if (Math.abs(lx) > (lng ? L / 2 : Tk / 2) + r.a || Math.abs(lz) > (lng ? Tk / 2 : L / 2) + r.a) continue;
        flag(r, r.x, top(r) + 1 * V + shear(r, r.x, r.z), r.z, 4.5 * V);
      }
    }
    const lmk = new Map();   // (a landmark: a building with landmark parts, its plan 300 m² or more)
    for (const r of R) if ((r.part === LMK || r.part === LROOF) && (r.t === 0 || r.t === 1 || r.t === 2)) { const k = bkey(r), v = lmk.get(k) || { area: 0, hi: null };
      if (r.part === LMK) v.area += r.a * r.b; if (!v.hi || top(r) > top(v.hi)) v.hi = r; lmk.set(k, v); }
    for (const [, v] of lmk) if (v.area >= 300 * M * M && v.hi) flag(v.hi, v.hi.x, top(v.hi) + shear(v.hi, v.hi.x, v.hi.z), v.hi.z, 5 * V);
  }

  // ---------------------------------------------------------------- packed
  const kinds = {}, m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(0, 0, 0, 'YXZ'), p = new THREE.Vector3(), sc = new THREE.Vector3();
  // each kind's size as it is seen (model units): a band by its height, the courses by their spacing (they flatten into their
  // face, FLAT), the rows of tiles by their spacing (FADE_ROWS), the rest by their width
  const T_ = ST.tiles || {}, SIZE = { window: 1 * M, door: 1.5 * M, cornice: .38 * V, base: .55 * V, post: .34 * M, beam: .45 * V, coping: .4 * M, ridgeEnd: .6 * M,
    tile: (T_.every || 1.1) * M, verge: .46 * M, eave: 6 * M, ridge: 6 * M, spandrel: 4 * M, archRing: 4 * M, merlon: 1.4 * M, parapet: .9 * V, column: .7 * M,
    crown: 6 * M, cone: 3 * M, trunk: 6 * M, pole: 1.5 * M, flag: 4.5 * M,
    ...Object.fromEntries(Object.entries(WALL_FACES).flatMap(([k, F]) => [['course_' + k, F.every * V], ['spandrel_' + k, 4 * M], ['parapet_' + k, .9 * V], ['merlon_' + k, 1.4 * M]])) };
  let count = 0;
  for (const [kind, L] of Object.entries(out)) {
    const n = L.length, m = new Float32Array(n * 16), k = new Float32Array(n), ctr = new Float32Array(n * 2), rank = new Float32Array(n), base = new Float32Array(n), src = new Float32Array(n), piv = new Float32Array(n);
    L.forEach(([x, y, z, phi, sx, sy, sz, tilt, kk, bx, bz, rk, roll, b0, si, pv], i) => {
      e.set(tilt, phi, roll); q.setFromEuler(e); m4.compose(p.set(x, y, z), q, sc.set(sx, sy, sz)).toArray(m, i * 16);
      k[i] = kk; ctr[i * 2] = bx; ctr[i * 2 + 1] = bz; rank[i] = rk; base[i] = b0; src[i] = si; piv[i] = pv ?? -1e9; });
    const root = kind.split('_')[0];
    kinds[kind] = { n, m, k, ctr, rank, base, src, piv, size: SIZE[kind] || SIZE[root] || M, fade: kind === 'tile' ? FADE_ROWS : kind.endsWith('_g1') ? FADE_GARDEN[0] : kind.endsWith('_g2') ? FADE_GARDEN[1] : FADE_PX }; count += n;
  }
  return { kinds, count, treeOK };
}

// boats on the water round a point: where the water reaches `wide` metres every way (a river a boat can work on, not a ditch),
// at least `apart` metres from each other, each laid along the water (the way it runs furthest); in its region's way (STYLES
// boats: { sail, cabin }). wet(x, z): water there (the look's water map). -> { kinds, count } as eraDetail's
// ground(x, z): the water's height there
export function boatsAt(wet, centre, R, { scale, style = 'roman', wide = 30, apart = 70, most = 40, seed = 1, ground = () => 0 } = {}) {
  const ST = STYLES[style] || STYLES.roman, B = ST.boats || { sail: true, cabin: false }, M = scale, out = [], put = (kind, x, y, z, phi, sx, sy, sz, k = 1) => (out[kind] ||= []).push([x, y, z, phi, sx, sy, sz, k]);
  let a = seed >>> 0; const rnd = () => { a = a + 0x6D2B79F5 >>> 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const placed = [];
  for (let tries = 0; tries < most * 40 && placed.length < most; tries++) {
    const an = rnd() * Math.PI * 2, d = R * Math.sqrt(rnd()), x = centre.x + Math.cos(an) * d, z = centre.z + Math.sin(an) * d;
    if (!wet(x, z) || placed.some(([px, pz]) => Math.hypot(px - x, pz - z) < apart * M)) continue;
    let ok = true; for (let k = 0; k < 8 && ok; k++) ok = wet(x + Math.cos(k * Math.PI / 4) * wide / 2 * M, z + Math.sin(k * Math.PI / 4) * wide / 2 * M);
    if (!ok) continue;
    let best = 0, run = 0;   // (the way the water runs: the longest of eight)
    for (let k = 0; k < 8; k++) { let s = 0; while (s < 200 && wet(x + Math.cos(k * Math.PI / 4) * s * M, z + Math.sin(k * Math.PI / 4) * s * M)) s += 10; if (s > run) { run = s; best = k; } }
    const phi = -best * Math.PI / 4 + (rnd() - .5) * .3, L = (12 + rnd() * 10) * M, y = ground(x, z) - .3 * M;
    placed.push([x, z]);
    put('hull', x, y, z, phi, L, 1.4 * M, L * .26, .9 + .2 * rnd());
    if (B.sail) { put('mast', x, y, z, 0, .25 * M, L * .55, .25 * M); put('sail', x, y + L * .12, z, phi, 1, L * .38, L * .32); }
    if (B.cabin) put('cabin', x, y + 1.1 * M, z, phi, L * .38, L * .13, L * .18);
  }
  const kinds = {}, m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), p = new THREE.Vector3(), sc = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  let count = 0;
  for (const [kind, L] of Object.entries(out)) {
    const n = L.length, m = new Float32Array(n * 16), k = new Float32Array(n), ctr = new Float32Array(n * 2), rank = new Float32Array(n);
    L.forEach(([x, y, z, phi, sx, sy, sz, kk], i) => { q.setFromAxisAngle(up, phi); m4.compose(p.set(x, y, z), q, sc.set(sx, sy, sz)).toArray(m, i * 16); k[i] = kk; ctr[i * 2] = x; ctr[i * 2 + 1] = z; });
    kinds[kind] = { n, m, k, ctr, rank, size: 10 * M, fade: FADE_PX }; count += n;
  }
  return { kinds, count };
}

// a gable's end in a period city's geometry (buildEra): a lone upright triangle of a roof, two corners level at its foot and the
// third above, between them (a box's side, a ridge's, has its upper corner over a lower one): the house's wall carried up to its
// ridge, for a look to colour as the wall. -> one flag a vertex
export function gableEnds(g) {
  const P = g.attributes.position, N = g.attributes.normal, D = g.attributes.aData, n = P.count, out = new Uint8Array(n), e = 1e-7;
  if (!D) return out;
  for (let t = 0; t + 2 < n; t += 3) {
    if (Math.round(D.getY(t)) !== 8 || Math.abs(N.getY(t)) > .15 || Math.abs(N.getY(t + 1)) > .15 || Math.abs(N.getY(t + 2)) > .15) continue;
    const ys = [0, 1, 2].map(k => P.getY(t + k)), lo = Math.min(...ys), base = [0, 1, 2].filter(k => ys[k] - lo < e), up = [0, 1, 2].find(k => ys[k] - lo >= e);
    if (base.length !== 2 || up == null) continue;
    const [a, b] = base.map(k => [P.getX(t + k), P.getZ(t + k)]), x = P.getX(t + up), z = P.getZ(t + up), L = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (L > 1e-6 && Math.hypot(x - a[0], z - a[1]) > .2 * L && Math.hypot(x - b[0], z - b[1]) > .2 * L) out[t] = out[t + 1] = out[t + 2] = 1;
  }
  return out;
}

// the fade: a piece shrinks to nothing about its own origin as it gets too small on screen to draw (its size, kinds[].size, under
// FADE_PX pixels: from FADE_PX[1] down to FADE_PX[0]), so a far wall's windows neither shimmer as the camera moves nor sum to a
// darker grey; a near one is drawn whole. A thin piece laid on a face (a row of tiles, a gable's ridge, a wall's course: FLAT)
// flattens into the face instead, its colour going to the face's own (FLAT's factor: the look colours it the face's colour times
// that), so its lines are gone, not thinned to a stair-stepping pixel. pxK: { value } a model unit's pixels at one model unit's
// distance (projectionMatrix[1][1] times half the picture's height in its own pixels, not a larger drawing buffer's), the look's to set each frame
export const FADE_PX = [1.1, 2.6];
// a roof's rows of tiles fade by their spacing, whole from seven pixels apart and gone by five: drawn closer, they crawl as the
// camera moves (a slow pan at a mid shot: more change between frames than their edges account for); a close shot keeps them in
// its foreground
export const FADE_ROWS = [5, 7];
// a town's garden trees afar (STYLES trees gardens): half of them gone by the time a crown is 7 px, three in ten more by 11 px,
// so a district seen from afar reads by its roofs, its gardens thinning, never a moss with specks in it
export const FADE_GARDEN = [[5, 7], [8, 11]];
export const FLAT = { tile: 1.12, verge: .78, course: .84 };
const FADE_GLSL = /* glsl */`
  { vec4 o_ = modelMatrix * instanceMatrix * vec4(0., 0., 0., 1.);
    float px_ = uDetSize * uPxK / max(distance(cameraPosition, o_.xyz), 1e-6);
    vDetF = smoothstep(uDetFade.x, uDetFade.y, px_);
    if (uDetFlat > 0.) transformed *= vec3(smoothstep(0., .3, vDetF), vDetF, smoothstep(0., .3, vDetF)); else transformed *= vDetF; }`;   // (a flat one gone at last too: left lying on its face it caught the face's shadow and shimmered)
// a piece rising with its building (detailMeshes o.rise): the look's float eraRiseK() of the instance's building (0 not up or gone
// .. 1 standing), and the piece raised as its building is, about the building's ground (iBase): up to it as the building rises,
// down as it falls; not drawn at all while its building is not up
const RISE_PIECE = /* glsl */`
  { float ry_ = eraRiseK();
    if (ry_ < .002) transformed = vec3(0.);
    else { vec4 w_ = instanceMatrix * vec4(transformed, 1.); w_.y = iBase + (w_.y - iBase) * ry_;
      if (uHScale < .999) w_.y = iPiv > -1e8 ? w_.y + (uHScale - 1.) * max(iPiv - iBase, 0.) : iBase + (w_.y - iBase) * uHScale;   // (a close shot's heights: mini.js HSCALE)
      transformed = (inverse(instanceMatrix) * w_).xyz; } }`;
function fading(mat, size, pxK, flat = 0, fade = FADE_PX, rise = null) {
  mat.onBeforeCompile = sh => { if (pxK) { sh.uniforms.uDetSize = { value: size }; sh.uniforms.uPxK = pxK; sh.uniforms.uDetFlat = { value: flat }; sh.uniforms.uDetFade = { value: new THREE.Vector2(...fade) }; }
    if (rise) Object.assign(sh.uniforms, rise.uniforms);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\n' + (pxK ? 'uniform float uDetSize, uPxK, uDetFlat; uniform vec2 uDetFade; varying float vDetF;' : '') + (rise ? '\nattribute float iBase, iPiv; uniform float uHScale;\n' + rise.glsl : ''))
      .replace('#include <begin_vertex>', '#include <begin_vertex>' + (pxK ? FADE_GLSL : '') + (rise ? RISE_PIECE : ''));
    if (pxK && sh.fragmentShader.includes('#include <color_fragment>'))
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform float uDetFlat; varying float vDetF;')
        .replace('#include <color_fragment>', '#include <color_fragment>\n  if (uDetFlat > 0.) diffuseColor.rgb *= mix(1. / uDetFlat, 1., vDetF);'); };
  mat.customProgramCacheKey = () => (pxK ? 'detail-fade' : 'detail') + (rise ? '-rise' : ''); return mat;
}

// one InstancedMesh a kind: cols { <kind>: colour, or (bx, bz) -> THREE.Color: its building's own (a roof's tiles in that roof's
// colour) }, each piece that colour times its lightness; o.layer: the layer it is drawn on; o.pxK: the fade's (FADE_PX; none: no fade);
// o.rise: { glsl, uniforms, w } each piece rising and falling with its building (a film's period city: engine/studio.js eraRiseGLSL,
// its declarations and float eraRiseK() from iCtr, iRank and iW; the era's uniforms; w: the loss code of each record, aData.w, or null)
export function detailMeshes(D, cols, o = {}) {
  const group = new THREE.Group(), c = new THREE.Color(), base = new THREE.Color();
  for (const [kind, K] of Object.entries(D.kinds)) {
    const root = kind.split('_')[0], colK = cols[kind] || cols[root];   // (a tier of a kind, crown_g1: the kind's colour)
    if (!colK) continue;   // (a kind by a wall's face: course_brick, merlon_earth ..: its shape and its shadow the root's)
    const mat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .92, metalness: 0, side: ['window', 'door', 'spandrel', 'archRing', 'flag', 'sail', 'lattice', 'leaf'].includes(root) ? THREE.DoubleSide : THREE.FrontSide });   // (a flat piece seen from either side)
    const flat = FLAT[root] && !kind.endsWith('_banded') ? FLAT[root] : 0;   // (a stone wall's bands of brick are its face's own colour: they fade by their size)
    const rise = o.rise && K.base ? o.rise : null;
    const mesh = new THREE.InstancedMesh((SHAPES[kind] || SHAPES[root])(), o.pxK || rise ? fading(mat, K.size, o.pxK, flat, K.fade, rise) : mat, K.n);
    mesh.instanceMatrix.array.set(K.m); mesh.instanceMatrix.needsUpdate = true;
    const own = typeof colK === 'function'; if (!own) base.set(colK);
    for (let i = 0; i < K.n; i++) mesh.setColorAt(i, (own ? c.copy(colK(K.ctr[i * 2], K.ctr[i * 2 + 1])) : c.copy(base)).multiplyScalar(K.k[i]));
    mesh.instanceColor.needsUpdate = true;
    mesh.geometry.setAttribute('iCtr', new THREE.InstancedBufferAttribute(K.ctr, 2)); mesh.geometry.setAttribute('iRank', new THREE.InstancedBufferAttribute(K.rank, 1));
    if (rise) { mesh.geometry.setAttribute('iBase', new THREE.InstancedBufferAttribute(K.base, 1)); mesh.geometry.setAttribute('iPiv', new THREE.InstancedBufferAttribute(K.piv || new Float32Array(K.n).fill(-1e9), 1));
      mesh.geometry.setAttribute('iW', new THREE.InstancedBufferAttribute(K.src.map(i => rise.w ? rise.w[i] : 3), 1)); }
    mesh.castShadow = !!SHADOW[root]; mesh.receiveShadow = true; mesh.frustumCulled = false;
    if (flat) mesh.userData.noAO = true;   // (an ambient occlusion pass draws a scene with its own material, whole: a flat piece faded away there still shaded its roof in stripes; the look leaves these out of it)
    if (mesh.castShadow && (o.pxK || rise)) mesh.customDepthMaterial = fading(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), K.size, o.pxK, flat, K.fade, rise);
    if (o.layer != null) mesh.layers.set(o.layer);
    mesh.name = 'detail:' + kind; group.add(mesh);
  }
  return group;
}
