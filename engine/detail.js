// Detail on a period city's houses and walls, read from its records alone (pipeline/citygen.py, engine/props.js buildEra:
// [type, cx, cz, rot, y0, a, b, c, d, e, rank, part, ground, gx, gz, bx, bz, shape]) and drawn as instances: the generator's
// boxes stay as they are, and what a body, a wall piece or a tower is gives what it carries, in its region's way (STYLES):
// windows on every storey of its open faces, a door, a cornice under the eaves and a base at its foot (a Roman house); timber
// posts and a beam across the front its door opens in, a stone base, ornaments at the ends of its ridge (a Chinese hall); a
// small tiled coping on a yard wall; courses on a city wall (brick courses on an upright curtain, the lifts of rammed earth
// on a battered one) and windows high in a curtain wall's towers. Nothing here knows a city: the same records of any city in a
// region get the same detail.
// eraDetail(prims, { scale, hex, style }) -> { kinds: { <kind>: { n, m: Float32Array (16 per instance), k: Float32Array (a
//   lightness each), ctr: Float32Array (its building's centre, x z), rank: Float32Array (its building's rank) } }, count }:
//   plain arrays, so any look draws them (detailMeshes: one InstancedMesh a kind, coloured by the look); ctr and rank are the
//   records' own (aCtr, aData.z), so a film that raises a city building by building can raise these pieces with their building.
// hex: the period city's height exaggeration (city.yaml era `exaggeration`, the generator's default 2): a storey's drawn height
// and every piece's height scale with it, widths do not.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const FAB = 0, LMK = 1, WALL = 2, DARK = 6, ROOF = 8, LROOF = 9;
// what a region's buildings carry, in metres (heights before the exaggeration). storey: a storey's height where the records do
// not say (a body's storeys: its height over this, rounded); window: { w, h, every (a window a bay this wide), sill (its foot
// above its storey's floor, a share of the storey), arch } as the generator draws a street front's (citygen house_body), null: none added (a Chinese hall's back and ends are blank: its
// openings are on its front, the generator's own); door: { w, h, arch }; cornice: { h, out } a band under the eaves; base: { h,
// out } a plinth course at the foot; front: { post, every, beam } timber posts and a beam across the face the generator opened
// (its door, its windows); ridgeEnds: ornaments at the ends of a ridge; coping: { h, over } a small roof on a yard wall;
// courses: { every, h, from } bands on a city wall's faces (from: on 'upright' curtains, 'battered' earthworks or 'all');
// towerWindows: { w, h, n } on each open face of a curtain wall's tower, high up; tiles: { every, w, t, verge: { w, t } } the
// rows of a tiled roof down each slope of a gable (筒瓦 rows, drawn wider apart than they are, so they read at a model's scale)
// and the heavier ridge down each of its gable edges (垂脊)
export const STYLES = {
  roman: {
    storey: 3.5, window: { w: 1.0, h: 1.5, every: 3.6, sill: .38, arch: true }, door: { w: 1.5, h: 2.5, arch: true },
    cornice: { h: .38, out: .22 }, base: { h: .55, out: .06 }, front: null, ridgeEnds: false, coping: { h: .32, over: .14 },
    courses: { every: 1.6, h: .32, from: 'all' }, towerWindows: { w: 1.3, h: 2.1, n: 2 }, tiles: null,
  },
  chinese: {
    storey: 3.6, window: null, door: null, cornice: null, base: { h: .6, out: .1 },
    front: { post: .34, every: 2.8, beam: .45 }, ridgeEnds: true, coping: { h: .42, over: .2 },
    courses: { every: 1.1, h: .1, from: 'battered' }, towerWindows: null, tiles: { every: .75, w: .24, t: .13, verge: { w: .42, t: .32 } },
  },
};
STYLES.modern = STYLES.roman;   // (the palette `modern`: a European town's houses)

// the pieces' shapes, each a unit: x across (-.5..5), y up (0..1), z out of the face (-.5..5; a flat one at z 0, facing +z)
function arched(top = .72, n = 7) {   // a window's or a door's opening, its head a half oval (the height exaggeration stretches it)
  const s = new THREE.Shape(); s.moveTo(-.5, 0); s.lineTo(.5, 0); s.lineTo(.5, top);
  for (let i = 1; i < n; i++) { const a = Math.PI * i / n; s.lineTo(.5 * Math.cos(a), top + (1 - top) * Math.sin(a)); }
  s.lineTo(-.5, top); s.closePath();
  return new THREE.ShapeGeometry(s, 1);
}
const box = () => new THREE.BoxGeometry(1, 1, 1).translate(0, .5, 0);
function capGeometry() {   // a coping: a little roof along x, its section across z
  const s = new THREE.Shape(); s.moveTo(-.5, 0); s.lineTo(.5, 0); s.lineTo(.5, .3); s.lineTo(0, 1); s.lineTo(-.5, .3); s.closePath();
  return new THREE.ExtrudeGeometry(s, { depth: 1, bevelEnabled: false }).translate(0, 0, -.5).rotateY(Math.PI / 2);
}
function hornGeometry() {   // a ridge's end (a common house's 蠍子尾, simply): the ridge carried on past the gable and swept up and out, x along the ridge (out: +x)
  const s = new THREE.Shape(); s.moveTo(-.5, 0); s.lineTo(.15, 0); s.lineTo(.5, .62); s.lineTo(.62, 1); s.lineTo(.3, .96); s.lineTo(.02, .5); s.lineTo(-.5, .5); s.closePath();
  return new THREE.ExtrudeGeometry(s, { depth: 1, bevelEnabled: false }).translate(0, 0, -.5);
}
export const SHAPES = { window: () => arched(), door: () => arched(.66), pane: () => new THREE.PlaneGeometry(1, 1).translate(0, .5, 0),
  cornice: box, base: box, post: box, beam: box, course: box, coping: capGeometry, ridgeEnd: hornGeometry,
  tile: () => new THREE.BoxGeometry(1, 1, 1), verge: () => new THREE.BoxGeometry(1, 1, 1) };   // (a row of tiles: x down the slope, y out of it, centred)
// which kinds cast a shadow (a flat opening or a thin course does not: it would only darken itself)
export const SHADOW = { cornice: true, post: true, beam: true, coping: true, ridgeEnd: true, verge: true };

export function eraDetail(prims, { scale, hex = 2, style = 'roman' } = {}) {
  const ST = STYLES[style] || STYLES.roman, M = scale, V = scale * hex;   // M: a metre across; V: a metre up, as drawn
  const R = prims.map(p => ({ t: p[0], x: p[1], z: p[2], rot: p[3], y0: p[4], a: p[5], b: p[6], c: p[7], d: p[8], e: p[9], rank: p[10], part: p[11], g: p[12],
    gx: p[13] || 0, gz: p[14] || 0, bx: p[15] ?? p[1], bz: p[16] ?? p[2] }));
  const out = {}, put = (kind, r, x, y, z, phi, sx, sy, sz, tilt = 0, k = 1, roll = 0) => (out[kind] ||= []).push([x, y, z, phi, sx, sy, sz, tilt, k, r.bx, r.bz, r.rank, roll]);
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
    if (ST.door && !doored) {
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
  const CO = ST.courses;
  for (const r of R) {
    if (r.part !== WALL || !(r.t === 0 || r.t === 2) || r.d === 1) continue;
    const y0 = r.y0, h = r.c, g = r.g, faces = r.t === 0 && Math.abs(r.a - r.b) < .5 * Math.max(r.a, r.b) ? [0, 1, 2, 3] : [2, 3];   // (a tower: all round; a wall piece: its two long faces)
    if (Math.min(r.a, r.b) < 1.5 * M || (top(r) - Math.max(y0, g)) / V < 2.5) continue;   // (not a parapet, a merlon)
    const battered = r.t === 2, tower = faces.length === 4;
    if (CO && (CO.from === 'all' || CO.from === (battered ? 'battered' : 'upright'))) {
      for (const f of faces) {
        const F = faceOf(r, f), lean = battered ? Math.atan2((F.nx ? r.a - r.d : r.b - r.e) / 2, h) : 0;   // (a battered face leans in as it rises)
        for (let y = g + CO.every * V; y < top(r) - .4 * V; y += CO.every * V) {
          const fr = (y - y0) / h, half = battered ? F.half + ((F.nx ? r.d : r.e) / 2 - F.half) * fr : F.half, w = battered ? F.w + ((F.nx ? r.e : r.d) - F.w) * fr : F.w;
          const lx = F.nx ? F.nx * (half + .02 * M) : 0, lz = F.nz ? F.nz * (half + .02 * M) : 0, [X, Z] = world(r, lx, lz);
          put('course', r, X, y + shear(r, X, Z), Z, F.phi, w + .04 * M, CO.h * V, .06 * M, -lean, .9 + .2 * hash(X, y));
        }
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

  // ---------------------------------------------------------------- packed
  const kinds = {}, m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(0, 0, 0, 'YXZ'), p = new THREE.Vector3(), sc = new THREE.Vector3();
  let count = 0;
  for (const [kind, L] of Object.entries(out)) {
    const n = L.length, m = new Float32Array(n * 16), k = new Float32Array(n), ctr = new Float32Array(n * 2), rank = new Float32Array(n);
    L.forEach(([x, y, z, phi, sx, sy, sz, tilt, kk, bx, bz, rk, roll], i) => {
      e.set(tilt, phi, roll); q.setFromEuler(e); m4.compose(p.set(x, y, z), q, sc.set(sx, sy, sz)).toArray(m, i * 16);
      k[i] = kk; ctr[i * 2] = bx; ctr[i * 2 + 1] = bz; rank[i] = rk; });
    kinds[kind] = { n, m, k, ctr, rank }; count += n;
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

// one InstancedMesh a kind: cols { <kind>: colour, or (bx, bz) -> THREE.Color: its building's own (a roof's tiles in that roof's
// colour) }, each piece that colour times its lightness; o.layer: the layer it is drawn on
export function detailMeshes(D, cols, o = {}) {
  const group = new THREE.Group(), c = new THREE.Color(), base = new THREE.Color();
  for (const [kind, K] of Object.entries(D.kinds)) {
    if (!cols[kind]) continue;
    const mat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .92, metalness: 0, side: kind === 'window' || kind === 'door' ? THREE.DoubleSide : THREE.FrontSide });
    const mesh = new THREE.InstancedMesh(SHAPES[kind](), mat, K.n);
    mesh.instanceMatrix.array.set(K.m); mesh.instanceMatrix.needsUpdate = true;
    const own = typeof cols[kind] === 'function'; if (!own) base.set(cols[kind]);
    for (let i = 0; i < K.n; i++) mesh.setColorAt(i, (own ? c.copy(cols[kind](K.ctr[i * 2], K.ctr[i * 2 + 1])) : c.copy(base)).multiplyScalar(K.k[i]));
    mesh.instanceColor.needsUpdate = true;
    mesh.geometry.setAttribute('iCtr', new THREE.InstancedBufferAttribute(K.ctr, 2)); mesh.geometry.setAttribute('iRank', new THREE.InstancedBufferAttribute(K.rank, 1));
    mesh.castShadow = !!SHADOW[kind]; mesh.receiveShadow = true; mesh.frustumCulled = false;
    if (o.layer != null) mesh.layers.set(o.layer);
    mesh.name = 'detail:' + kind; group.add(mesh);
  }
  return group;
}
