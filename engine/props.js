// Schematic 3D props on the white model: rammed-earth terraces, halls, walls with gates, bridges, huts, sheds, towers,
// and the city's emblem (a Qin tiger tally). Every prop is built from boxes, frustums and extruded polygons into ONE geometry
// with the studio's aData attribute (year, height, rank, kind = 1), so the projector tints props like buildings.
// Positions are model units (x east, z south), y up; `ground(x, z)` gives the terrain height under a point.
import * as THREE from 'three';

export class Geo {
  constructor() { this.pos = []; this.nor = []; this.dat = []; this.base = []; this.ctr = []; this.gx = 0; this.gz = 0; this.cc = null; }   // gx, gz: a shear (model y per model x / z) so long pieces follow a slope; cc: the building centre written per vertex (aCtr)
  // a triangle is wound to face along its normal: WebGL draws only the counter-clockwise (front) side, and a face wound the other
  // way round is seen from inside, so the near wall of a house vanished and the inner side of its far wall showed through
  // (ns: a normal per corner, for a curved surface shaded smooth; the winding still follows n, the face's own)
  tri(a, b, c, n, d, base = 0, ns = null) {
    const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
    let m = ns || [n, n, n];
    if ((u[1] * v[2] - u[2] * v[1]) * n[0] + (u[2] * v[0] - u[0] * v[2]) * n[1] + (u[0] * v[1] - u[1] * v[0]) * n[2] < 0) { [b, c] = [c, b]; m = [m[0], m[2], m[1]]; }
    [a, b, c].forEach((p, i) => { this.pos.push(...p); this.nor.push(...m[i]); this.dat.push(...d); this.base.push(base); if (this.cc) this.ctr.push(this.cc[0], this.cc[1]); }); }
  quad(a, b, c, d_, n, d, base = 0) { this.tri(a, b, c, n, d, base); this.tri(a, c, d_, n, d, base); }
  // axis-aligned box, rotated about y by rot (radians) around (cx, cz); y from y0 to y0 + h
  box(cx, y0, cz, w, h, d, rot = 0, data = [0, 0, 0, 1], base = null) {
    const B0 = base == null ? y0 : base;
    const c = Math.cos(rot), s = Math.sin(rot);
    const R = (x, z) => [cx + x * c - z * s, cz + x * s + z * c];
    const P = (x, y, z) => { const [X, Z] = R(x, z); return [X, y0 + y + this.gx * (X - cx) + this.gz * (Z - cz), Z]; };
    const N = (x, z) => { const [X, Z] = R(x, z); return [X - cx, 0, Z - cz]; };
    const hw = w / 2, hd = d / 2;
    // +x, -x, +z, -z faces, top, bottom
    this.quad(P(hw, 0, -hd), P(hw, 0, hd), P(hw, h, hd), P(hw, h, -hd), N(1, 0), data, B0);
    this.quad(P(-hw, 0, hd), P(-hw, 0, -hd), P(-hw, h, -hd), P(-hw, h, hd), N(-1, 0), data, B0);
    this.quad(P(hw, 0, hd), P(-hw, 0, hd), P(-hw, h, hd), P(hw, h, hd), N(0, 1), data, B0);
    this.quad(P(-hw, 0, -hd), P(hw, 0, -hd), P(hw, h, -hd), P(-hw, h, -hd), N(0, -1), data, B0);
    this.quad(P(-hw, h, hd), P(hw, h, hd), P(hw, h, -hd), P(-hw, h, -hd), [0, 1, 0], data, B0);
  }
  // truncated pyramid: base w0 x d0 at y0, top w1 x d1 at y0 + h (a rammed-earth tier, a hip roof when w1, d1 are small)
  frustum(cx, y0, cz, w0, d0, w1, d1, h, rot = 0, data = [0, 0, 0, 1], base = null) {
    const B0 = base == null ? y0 : base;
    const c = Math.cos(rot), s = Math.sin(rot);
    const R = (x, z) => [cx + x * c - z * s, cz + x * s + z * c];
    const P = (x, y, z) => { const [X, Z] = R(x, z); return [X, y0 + y + this.gx * (X - cx) + this.gz * (Z - cz), Z]; };
    const b = [P(-w0 / 2, 0, -d0 / 2), P(w0 / 2, 0, -d0 / 2), P(w0 / 2, 0, d0 / 2), P(-w0 / 2, 0, d0 / 2)];
    const t = [P(-w1 / 2, h, -d1 / 2), P(w1 / 2, h, -d1 / 2), P(w1 / 2, h, d1 / 2), P(-w1 / 2, h, d1 / 2)];
    for (let i = 0; i < 4; i++) {
      const a = b[i], b2 = b[(i + 1) % 4], c2 = t[(i + 1) % 4], d2 = t[i];
      const u = [b2[0] - a[0], b2[1] - a[1], b2[2] - a[2]], v = [d2[0] - a[0], d2[1] - a[1], d2[2] - a[2]];
      let n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
      const L = Math.hypot(...n) || 1; n = n.map(q => q / L);
      const mid = [(a[0] + c2[0]) / 2 - cx, 0, (a[2] + c2[2]) / 2 - cz];
      if (n[0] * mid[0] + n[2] * mid[2] < 0) { n = n.map(q => -q); this.quad(a, d2, c2, b2, n, data, B0); } else this.quad(a, b2, c2, d2, n, data, B0);
    }
    if (w1 > 1e-6 && d1 > 1e-6) this.quad(t[3], t[2], t[1], t[0], [0, 1, 0], data, B0);
  }
  // gable roof: span w across local x, ridge along local z (length d), ridge height h above y0, eave overhang o
  gable(cx, y0, cz, w, d, h, rot = 0, o = 0, data = [0, 0, 0, 1], base = 0) {
    const c = Math.cos(rot), s = Math.sin(rot);
    const P = (x, y, z) => { const X = cx + x * c - z * s, Z = cz + x * s + z * c; return [X, y0 + y + this.gx * (X - cx) + this.gz * (Z - cz), Z]; };
    const hw = w / 2 + o, hd = d / 2, drop = o * h / Math.max(1e-6, w / 2);
    const a = P(-hw, -drop, -hd), b = P(hw, -drop, -hd), e = P(hw, -drop, hd), f = P(-hw, -drop, hd), r0 = P(0, h, -hd), r1 = P(0, h, hd);
    const nrm = (p, q, r) => { const u = [q[0] - p[0], q[1] - p[1], q[2] - p[2]], v = [r[0] - p[0], r[1] - p[1], r[2] - p[2]]; let n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]; const L = Math.hypot(...n) || 1; return n.map(t => t / L); };
    const up = n => n[1] < 0 ? n.map(t => -t) : n;
    let n1 = up(nrm(a, r0, f)); this.quad(a, f, r1, r0, n1, data, base);      // west slope
    let n2 = up(nrm(b, e, r1)); this.quad(b, r0, r1, e, n2, data, base);      // east slope
    const gs = [s, 0, -c];                                                    // gable ends (normals along local -z / +z)
    this.tri(P(-w / 2, 0, -hd), P(w / 2, 0, -hd), P(0, h, -hd), gs, data, base);
    this.tri(P(w / 2, 0, hd), P(-w / 2, 0, hd), P(0, h, hd), [-gs[0], 0, -gs[2]], data, base);
    // soffit under the eaves so the overhang reads from below
    if (o > 0) { this.quad(f, e, b, a, [0, -1, 0], data, base); }
  }
  cylinder(cx, y0, cz, r, h, n = 16, data = [0, 0, 0, 1], base = null) {
    const B0 = base == null ? y0 : base;
    for (let i = 0; i < n; i++) {
      const a0 = i / n * Math.PI * 2, a1 = (i + 1) / n * Math.PI * 2;
      const p0 = [cx + r * Math.cos(a0), y0, cz + r * Math.sin(a0)], p1 = [cx + r * Math.cos(a1), y0, cz + r * Math.sin(a1)];
      const q0 = [p0[0], y0 + h, p0[2]], q1 = [p1[0], y0 + h, p1[2]];
      const nn = [Math.cos((a0 + a1) / 2), 0, Math.sin((a0 + a1) / 2)];
      this.quad(p0, p1, q1, q0, nn, data, B0);
      this.tri([cx, y0 + h, cz], q1, q0, [0, 1, 0], data, B0);
    }
  }
  cone(cx, y0, cz, r, h, n = 16, data = [0, 0, 0, 1], base = null) {
    const B0 = base == null ? y0 : base;
    for (let i = 0; i < n; i++) {
      const a0 = i / n * Math.PI * 2, a1 = (i + 1) / n * Math.PI * 2;
      const p0 = [cx + r * Math.cos(a0), y0, cz + r * Math.sin(a0)], p1 = [cx + r * Math.cos(a1), y0, cz + r * Math.sin(a1)];
      const m = (a0 + a1) / 2, k = r / Math.hypot(r, h);
      this.tri(p0, p1, [cx, y0 + h, cz], [Math.cos(m) * (1 - k * .3), k, Math.sin(m) * (1 - k * .3)], data, B0);
    }
  }
  // a solid of revolution: the section `prof` ([[r, y], ...]: r a share of the radius, y of the height h; a closed outline, from
  // the base round counter-clockwise with r to the right and y up) spun round the vertical axis in `sides` steps; rx, rz the radii
  // along local x and z (an oval: an amphitheatre, a dome over an oblong hall). Every edge of the outline is a surface but those on
  // the axis and those along the base (never seen); its normal is the outline's outward one (so a ring's inner wall faces the
  // arena), shaded smooth across a corner under 30 degrees, round the axis too when a step is under 30 degrees (a dome reads
  // round, a drum's rim and an octagon's corners stay sharp). sweep < 1: that share of a turn, centred on the piece's back
  // (local -z: a theatre's seats, an apse, a half dome), `sides` steps over it, the section capped at both cut ends
  revolve(cx, y0, cz, rx, rz, h, prof, sides = 32, rot = 0, data = [0, 0, 0, 1], base = null, sweep = 1) {
    if (prof.reduce((A, p, i) => { const q = prof[(i + 1) % prof.length]; return A + p[0] * q[1] - q[0] * p[1]; }, 0) < 0) prof = prof.slice().reverse();   // (given clockwise)
    const B0 = base == null ? y0 : base, c = Math.cos(rot), s = Math.sin(rot), n = prof.length, Rm = (rx + rz) / 2, CR = Math.cos(Math.PI / 6);
    const P = (r, y, a) => { const x = r * rx * Math.cos(a), z = r * rz * Math.sin(a), X = cx + x * c - z * s, Z = cz + x * s + z * c; return [X, y0 + y * h + this.gx * (X - cx) + this.gz * (Z - cz), Z]; };
    // a section normal (metres, r and y) -> the surface's normal at angle a (the oval's scaling and the rotation applied)
    const N3 = ([nr, ny], a) => { const x = nr / h * Math.cos(a) / rx, y = ny / Rm / h, z = nr / h * Math.sin(a) / rz, X = x * c - z * s, Z = x * s + z * c, L = Math.hypot(X, y, Z) || 1; return [X / L, y / L, Z / L]; };
    const en = [];   // each edge's outward normal in metres
    for (let i = 0; i < n; i++) { const [r0, q0] = prof[i], [r1, q1] = prof[(i + 1) % n], dr = (r1 - r0) * Rm, dy = (q1 - q0) * h, L = Math.hypot(dr, dy) || 1; en.push([dy / L, -dr / L]); }
    const vn = (i, k) => {   // edge i's normal at its corner k (0 start, 1 end): the mean with the neighbour's where they meet gently
      const j = k ? (i + 1) % n : (i + n - 1) % n, a = en[i], b = en[j];
      return a[0] * b[0] + a[1] * b[1] > CR ? [a[0] + b[0], a[1] + b[1]] : a;
    };
    const sw = sweep > 0 && sweep < 1 ? sweep : 1, A0 = sw < 1 ? -Math.PI / 2 - sw * Math.PI : 0, st = sw * 2 * Math.PI / sides, smooth = st < Math.PI / 6;
    for (let i = 0; i < n; i++) {
      const [r0, q0] = prof[i], [r1, q1] = prof[(i + 1) % n];
      if ((r0 <= 0 && r1 <= 0) || (q0 <= 0 && q1 <= 0)) continue;   // on the axis, along the base
      const m0 = vn(i, 0), m1 = vn(i, 1);
      for (let k = 0; k < sides; k++) {
        const a0 = A0 + k * st, a1 = A0 + (k + 1) * st, am = (a0 + a1) / 2, b0 = smooth ? a0 : am, b1 = smooth ? a1 : am;
        const p00 = P(r0, q0, a0), p01 = P(r0, q0, a1), p10 = P(r1, q1, a0), p11 = P(r1, q1, a1), f = N3(en[i], am);
        if (r0 <= 0) this.tri(p00, p11, p10, f, data, B0, [N3(m0, am), N3(m1, b1), N3(m1, b0)]);
        else if (r1 <= 0) this.tri(p00, p01, p10, f, data, B0, [N3(m0, b0), N3(m0, b1), N3(m1, am)]);
        else { this.tri(p00, p01, p11, f, data, B0, [N3(m0, b0), N3(m0, b1), N3(m1, b1)]); this.tri(p00, p11, p10, f, data, B0, [N3(m0, b0), N3(m1, b1), N3(m1, b0)]); }
      }
    }
    if (sw < 1) {   // the cut ends: the section itself, facing away round the turn
      const C = prof.map(([r, y]) => new THREE.Vector2(r, y)), faces = THREE.ShapeUtils.triangulateShape(C, []);
      for (const [a, k] of [[A0, -1], [A0 + sw * 2 * Math.PI, 1]]) {
        const x = -rz * Math.sin(a) * k, z = rx * Math.cos(a) * k, L = Math.hypot(x, z) || 1, nn = [(x * c - z * s) / L, 0, (x * s + z * c) / L];
        for (const [i, j, m] of faces) this.tri(P(C[i].x, C[i].y, a), P(C[j].x, C[j].y, a), P(C[m].x, C[m].y, a), nn, data, B0);
      }
    }
  }
  // a prism: the outline `rings` (the outer ring, then any holes; [[u, v], ...] in model units, the last point not repeating the
  // first) carried straight for length h. axis 0: a plan (u east, v south, round (cx, cz) before the rotation) raised from y0, its
  // top shrunk toward the outer ring's centre by `top` (1 straight up, 0 to a point: a spire, a hipped roof on any plan); the top
  // capped. axis 1: a section (u across, v up from y0) laid along local z, centred, both ends capped (a vault, a nave with its
  // aisles in one piece). A wall's normal faces away from the solid (a hole's into the hole), shaded smooth across a corner under
  // 30 degrees (a curved plan reads curved, a rectangle's corners stay sharp)
  prism(cx, y0, cz, rings, h, top = 1, axis = 0, rot = 0, data = [0, 0, 0, 1], base = null) {
    const B0 = base == null ? y0 : base, c = Math.cos(rot), s = Math.sin(rot), CR = Math.cos(Math.PI / 6);
    const area = r => r.reduce((A, p, i) => { const q = r[(i + 1) % r.length]; return A + p[0] * q[1] - q[0] * p[1]; }, 0) / 2;
    const R = rings.map((r, i) => (area(r) > 0) === (i === 0) ? r.slice() : r.slice().reverse());   // the outer ring counter-clockwise, holes clockwise
    const O = R[0], gu = O.reduce((a, p) => a + p[0], 0) / O.length, gv = O.reduce((a, p) => a + p[1], 0) / O.length;
    const L3 = axis ? ((u, v, t) => [u, v, (t - .5) * h]) : ((u, v, t) => { const k = 1 + (top - 1) * t; return [gu + (u - gu) * k, t * h, gv + (v - gv) * k]; });
    const W = ([x, y, z]) => { const X = cx + x * c - z * s, Z = cz + x * s + z * c; return [X, y0 + y + this.gx * (X - cx) + this.gz * (Z - cz), Z]; };
    const Wn = ([x, y, z]) => { const L = Math.hypot(x, y, z) || 1; return [(x * c - z * s) / L, y / L, (x * s + z * c) / L]; };
    const P = (u, v, t) => W(L3(u, v, t));
    const loc = (u, v) => axis ? [u, v, 0] : [u, 0, v];   // a plan or section direction in local xyz
    for (const r of R) {
      const n = r.length, en = r.map((p, i) => { const q = r[(i + 1) % n], du = q[0] - p[0], dv = q[1] - p[1], L = Math.hypot(du, dv) || 1; return [dv / L, -du / L]; });
      const vn = (i, j) => { const a = en[i], b = en[j]; return a[0] * b[0] + a[1] * b[1] > CR ? [a[0] + b[0], a[1] + b[1]] : a; };
      for (let i = 0; i < n; i++) {
        const j = (i + 1) % n, [u0, v0] = r[i], [u1, v1] = r[j];
        if (axis && v0 <= 0 && v1 <= 0) continue;   // a section's foot (never seen)
        const a = P(u0, v0, 0), b = P(u1, v1, 0), e = P(u1, v1, 1), d = P(u0, v0, 1);
        // the face's normal: the edge's outward direction, leaning in with the taper
        const x = [e[0] - b[0], e[1] - b[1], e[2] - b[2]], y_ = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
        let f = [y_[1] * x[2] - y_[2] * x[1], y_[2] * x[0] - y_[0] * x[2], y_[0] * x[1] - y_[1] * x[0]];
        const o = Wn(loc(...en[i])); if (f[0] * o[0] + f[1] * o[1] + f[2] * o[2] < 0) f = f.map(q => -q);
        const Lf = Math.hypot(...f); if (Lf < 1e-14) continue;
        f = f.map(q => q / Lf);
        const lean = q => top === 1 || axis ? Wn(loc(...q)) : (() => { const w = Wn(loc(...q)), k = f[1]; const L = Math.hypot(w[0], w[2]) || 1, hz = Math.sqrt(Math.max(0, 1 - k * k)); return [w[0] / L * hz, k, w[2] / L * hz]; })();
        const ma = lean(vn(i, (i + n - 1) % n)), mb = lean(vn(i, j));
        if (top === 0 && !axis) this.tri(a, b, d, f, data, B0, [ma, mb, ma]);
        else { this.tri(a, b, e, f, data, B0, [ma, mb, mb]); this.tri(a, e, d, f, data, B0, [ma, mb, ma]); }
      }
    }
    // the caps: the top (axis 0), both ends (axis 1)
    const C = R.map(r => r.map(([u, v]) => new THREE.Vector2(u, v))), faces = THREE.ShapeUtils.triangulateShape(C[0], C.slice(1)), V = C.flat();
    for (const t of axis ? [0, 1] : (top > 0 ? [1] : [])) {
      const nn = Wn(axis ? [0, 0, t ? 1 : -1] : [0, 1, 0]);
      for (const [i, j, k] of faces) this.tri(P(V[i].x, V[i].y, t), P(V[j].x, V[j].y, t), P(V[k].x, V[k].y, t), nn, data, B0);
    }
  }
  // a wall segment from a to b (model xz) as a box of thickness t and height h, standing on y0
  seg(a, b, y0, h, t, data) {
    const dx = b[0] - a[0], dz = b[1] - a[1], L = Math.hypot(dx, dz); if (L < 1e-7) return;
    this.box((a[0] + b[0]) / 2, y0, (a[1] + b[1]) / 2, L, h, t, Math.atan2(dz, dx), data);
  }
  geometry() {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(this.pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(this.nor, 3));
    g.setAttribute('aData', new THREE.Float32BufferAttribute(this.dat, 4));
    g.setAttribute('aBase', new THREE.Float32BufferAttribute(this.base, 1));
    if (this.ctr.length) g.setAttribute('aCtr', new THREE.Float32BufferAttribute(this.ctr, 2));
    return g;
  }
}

const deg = d => d * Math.PI / 180;

// ---------------------------------------------------------------- prop kinds (dimensions in model units; `S` = metres -> model units)
export function buildProp(p, ground, S, exag = 3) {
  const G = new Geo(); const data = [p.year || 0, (p.h_m || 10), 0, 2];
  const at = (x, z) => ground(x, z);
  const m = v => v * S;              // plan dimensions: true scale
  const mh = v => v * S * (p.exag ?? exag);   // heights: exaggerated so a 10 m terrace reads on a 1:10000 table (labelled 示意)
  switch (p.kind) {
    case 'terrace': {   // stepped rammed-earth platform (高台建築): `tiers` tiers shrinking to `top` fraction, a hall on top when p.hall
      const [x, z] = p.pos, y0 = at(x, z), rot = deg(p.rot || 0), H = mh(p.h_m), n = p.tiers || 3, W = m(p.w_m), D = m(p.d_m), tf = p.top ?? .55;
      for (let i = 0; i < n; i++) {
        const k0 = 1 - (1 - tf) * i / n, k1 = 1 - (1 - tf) * (i + 1) / n;
        G.frustum(x, y0 + H * i / n, z, W * k0, D * k0, W * k1 * .98, D * k1 * .98, H / n, rot, data);
      }
      if (p.hall) {
        const hw = W * tf * (p.hall.w ?? .7), hd = D * tf * (p.hall.d ?? .6), hh = mh(p.hall.h_m || 8), ry = y0 + H;
        G.box(x, ry, z, hw, hh * .6, hd, rot, data);                                  // the hall body
        G.frustum(x, ry + hh * .6, z, hw * 1.15, hd * 1.2, hw * .35, hd * .05, hh * .4, rot, data);   // the hip roof
      }
      break;
    }
    case 'hall': {   // a hall: body + hip roof
      const [x, z] = p.pos, y0 = at(x, z), rot = deg(p.rot || 0), W = m(p.w_m), D = m(p.d_m), H = mh(p.h_m);
      G.box(x, y0, z, W, H * .6, D, rot, data); G.frustum(x, y0 + H * .6, z, W * 1.15, D * 1.2, W * .35, D * .05, H * .4, rot, data);
      break;
    }
    case 'tower': { const [x, z] = p.pos; G.box(x, at(x, z), z, m(p.w_m), mh(p.h_m), m(p.d_m || p.w_m), deg(p.rot || 0), data); if (p.roof) G.frustum(x, at(x, z) + mh(p.h_m), z, m(p.w_m) * 1.2, m(p.d_m || p.w_m) * 1.2, m(p.w_m) * .2, m(p.d_m || p.w_m) * .2, mh(p.h_m) * .25, deg(p.rot || 0), data); break; }
    case 'hut': { const [x, z] = p.pos, r = m(p.r_m || 4), h = mh(p.h_m || 3); G.cylinder(x, at(x, z), z, r, h * .45, 12, data); G.cone(x, at(x, z) + h * .45, z, r * 1.15, h * .55, 12, data); break; }
    case 'huts': {   // a cluster: n huts around pos within radius_m (deterministic)
      const [x, z] = p.pos, R = m(p.radius_m || 120), n = p.n || 12; let s = 7;
      const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
      for (let i = 0; i < n; i++) { const a = rnd() * Math.PI * 2, r = Math.sqrt(rnd()) * R, hx = x + r * Math.cos(a), hz = z + r * Math.sin(a), hr = m(p.r_m || 4) * (.7 + rnd() * .6), hh = mh(p.h_m || 3.5);
        G.cylinder(hx, at(hx, hz), hz, hr, hh * .45, 10, data); G.cone(hx, at(hx, hz) + hh * .45, hz, hr * 1.15, hh * .55, 10, data); }
      break;
    }
    case 'wall': {   // a wall along pts (model xz) with gates (gaps + gate houses) and corner towers
      const pts = p.pts, H = mh(p.h_m || 8), T = m(p.t_m || 6), closed = p.closed !== false, gates = p.gates || [];
      const n = closed ? pts.length : pts.length - 1;
      const gateAt = (i, k) => gates.find(g => g.seg === i && Math.abs(g.k - k) < 1e-6);
      for (let i = 0; i < n; i++) {
        const a = pts[i], b = pts[(i + 1) % pts.length];
        const gs = gates.filter(g => g.seg === i).sort((u, v) => u.k - v.k);
        let k0 = 0;
        const y0 = (at(a[0], a[1]) + at(b[0], b[1])) / 2;
        for (const g of gs) {
          const L = Math.hypot(b[0] - a[0], b[1] - a[1]), gw = m(g.w_m || 12) / L;
          const pA = [a[0] + (b[0] - a[0]) * k0, a[1] + (b[1] - a[1]) * k0], pB = [a[0] + (b[0] - a[0]) * (g.k - gw / 2), a[1] + (b[1] - a[1]) * (g.k - gw / 2)];
          G.seg(pA, pB, y0, H, T, data);
          const gx = a[0] + (b[0] - a[0]) * g.k, gz = a[1] + (b[1] - a[1]) * g.k, rot = Math.atan2(b[1] - a[1], b[0] - a[0]);
          G.box(gx, y0, gz, m(g.w_m || 12) * 1.6, H * 1.25, T * 2.2, rot, data);                    // gate house base
          G.frustum(gx, y0 + H * 1.25, gz, m(g.w_m || 12) * 1.7, T * 2.4, m(g.w_m || 12) * .5, T * .3, H * .5, rot, data);   // its roof
          k0 = g.k + gw / 2;
        }
        const pA = [a[0] + (b[0] - a[0]) * k0, a[1] + (b[1] - a[1]) * k0];
        G.seg(pA, b, y0, H, T, data);
        if (p.towers !== false) G.box(b[0], at(b[0], b[1]), b[1], T * 2.4, H * 1.15, T * 2.4, 0, data);
      }
      break;
    }
    case 'bridge': {   // deck from `from` to `to` on `piers` rows of posts
      const [ax, az] = p.from, [bx, bz] = p.to, L = Math.hypot(bx - ax, bz - az), rot = Math.atan2(bz - az, bx - ax);
      const y = Math.max(at(ax, az), at(bx, bz)) + mh(p.h_m || 6), W = m(p.w_m || 12);
      G.box((ax + bx) / 2, y, (az + bz) / 2, L, mh(p.deck_m || 1.5), W, rot, data);
      const n = p.piers || Math.max(3, Math.round(L / m(40)));
      for (let i = 0; i <= n; i++) { const k = i / n, px = ax + (bx - ax) * k, pz = az + (bz - az) * k, g0 = at(px, pz) - m(2); G.box(px, g0, pz, m(p.pier_m || 4), y - g0, W * .9, rot, data); }
      break;
    }
    case 'shed': {   // a saw-tooth factory block: `bays` north-light bays along w
      const [x, z] = p.pos, y0 = at(x, z), rot = deg(p.rot || 0), W = m(p.w_m), D = m(p.d_m), H = mh(p.h_m || 8), bays = p.bays || 6;
      G.box(x, y0, z, W, H * .55, D, rot, data);
      const c = Math.cos(rot), s = Math.sin(rot), bw = W / bays;
      for (let i = 0; i < bays; i++) {
        const lx = -W / 2 + bw * (i + .5), cx = x + lx * c, cz = z + lx * s;
        G.frustum(cx, y0 + H * .55, cz, bw, D, bw * .05, D * .98, H * .45, rot, data);
      }
      break;
    }
    case 'blocks': {   // a field of simple blocks (a district): n boxes in a w x d area, deterministic
      const [x, z] = p.pos, W = m(p.w_m), D = m(p.d_m), n = p.n || 30, rot = deg(p.rot || 0); let s = 11;
      const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
      const c = Math.cos(rot), sn = Math.sin(rot);
      for (let i = 0; i < n; i++) { const lx = (rnd() - .5) * W, lz = (rnd() - .5) * D, bx = x + lx * c - lz * sn, bz = z + lx * sn + lz * c;
        G.box(bx, at(bx, bz), bz, m(p.bw_m || 20) * (.6 + rnd() * .8), mh(p.h_m || 15) * (.5 + rnd()), m(p.bd_m || 15) * (.6 + rnd() * .8), rot, data); }
      break;
    }
    case 'boats': {   // a few hulls along a line (a ferry crossing), deterministic
      const [ax, az] = p.from, [bx, bz] = p.to, n = p.n || 5; let sd = 17; const rnd = () => { sd = (sd * 16807) % 2147483647; return sd / 2147483647; };
      for (let i = 0; i < n; i++) { const k = (i + .5) / n, x = ax + (bx - ax) * k + (rnd() - .5) * m(40), z = az + (bz - az) * k + (rnd() - .5) * m(40);
        const rot = Math.atan2(bz - az, bx - ax) + (rnd() - .5) * .4; G.box(x, at(x, z) + m(.5), z, m(p.l_m || 14), mh(p.h_m || 2), m(p.w_m || 4), rot, data); G.box(x, at(x, z) + m(.5) + mh(p.h_m || 2), z, m(3), mh(5), m(1), rot, data); }
      break;
    }
    case 'station': {   // a railway station: a long low hall with a hip roof and a platform canopy beside the line
      const [x, z] = p.pos, y0 = at(x, z), rot = deg(p.rot || 0), W = m(p.w_m || 60), D = m(p.d_m || 18), H = mh(p.h_m || 10);
      G.box(x, y0, z, W, H * .65, D, rot, data); G.frustum(x, y0 + H * .65, z, W * 1.08, D * 1.2, W * .9, D * .1, H * .35, rot, data);
      const c = Math.cos(rot), s_ = Math.sin(rot), off = D * 1.1; G.box(x - s_ * off, y0 + H * .3, z + c * off, W * 1.6, mh(.8), D * .6, rot, data);
      break;
    }
    default: throw new Error('unknown prop kind ' + p.kind);
  }
  return G.geometry();
}

// ---------------------------------------------------------------- the tiger tally (虎符): a walking tiger silhouette, extruded, split along its spine
// Outline traced by hand from the Commons photo of a Qin tiger tally (Shaanxi History Museum): nose at the left, curled tail at the right.
// It is a schematic likeness (示意), not a scan. x 0..1 nose -> tail, y 0 feet -> ~0.6 tail tip.
export const TIGER = [[0.00, .33], [.02, .38], [.05, .42], [.09, .45], [.12, .48], [.14, .46], [.17, .45], [.22, .46], [.28, .49], [.36, .52], [.44, .53], [.52, .51], [.60, .48], [.68, .47], [.76, .49],
  [.83, .53], [.89, .58], [.94, .61], [.98, .59], [.99, .54], [.96, .50], [.92, .50], [.90, .53], [.87, .53], [.84, .50], [.80, .45], [.79, .36], [.81, .24], [.82, .12], [.84, .02], [.80, .00], [.73, .00], [.71, .08], [.69, .18],
  [.66, .25], [.58, .27], [.48, .26], [.40, .27], [.35, .25], [.34, .14], [.36, .03], [.33, .00], [.25, .00], [.24, .10], [.25, .20], [.22, .27], [.16, .29], [.10, .28], [.05, .27], [.01, .29]];

export function makeTally(opts = {}) {
  const L = opts.length || .095;   // model units: the real 杜虎符 is 9.5 cm long; 1 model unit = 1 model metre
  const pts = TIGER.map(([x, y]) => new THREE.Vector2(x * L, y * L));
  const shape = new THREE.Shape(); shape.moveTo(pts[0].x, pts[0].y); shape.splineThru(pts.slice(1)); shape.lineTo(pts[0].x, pts[0].y);
  const depth = L * .16, gap = 0;
  const geo = new THREE.ExtrudeGeometry(shape, { depth: depth / 2, bevelEnabled: true, bevelThickness: L * .012, bevelSize: L * .012, bevelSegments: 3, steps: 1, curveSegments: 24 });
  geo.computeVertexNormals();
  // uv: shape space -> 0..1 so an inscription texture wraps the flank
  const pos = geo.attributes.position, uv = new Float32Array(pos.count * 2);
  for (let i = 0; i < pos.count; i++) { uv[i * 2] = pos.getX(i) / L; uv[i * 2 + 1] = pos.getY(i) / (L * .62); }
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  // gold inlay: nine columns of short strokes (an abstract stand-in for the 40-character inscription; the real text is in the readout)
  const c = document.createElement('canvas'); c.width = 1024; c.height = 640; const g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, 1024, 640); g.strokeStyle = '#ffd98a'; g.lineWidth = 7; g.lineCap = 'round';
  let s = 5; const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
  for (let col = 0; col < 9; col++) {
    const cx = 230 + col * 62;
    for (let row = 0; row < 5; row++) {
      const cy = 160 + row * 70; const k = 2 + Math.floor(rnd() * 3);
      for (let j = 0; j < k; j++) { const a = rnd() * Math.PI, r = 10 + rnd() * 14, x = cx + (rnd() - .5) * 26, y = cy + (rnd() - .5) * 30; g.beginPath(); g.moveTo(x - Math.cos(a) * r, y - Math.sin(a) * r); g.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r); g.stroke(); }
    }
  }
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.MeshStandardMaterial({ color: '#4a3d2c', metalness: .85, roughness: .42, emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 0 });
  const group = new THREE.Group();
  const right = new THREE.Mesh(geo, mat); right.position.z = gap / 2; right.castShadow = true;
  const left = new THREE.Mesh(geo, mat); left.scale.z = -1; left.position.z = -gap / 2; left.castShadow = true;
  group.add(right, left);
  group.userData = { L, depth, mat, right, left };
  // k = split (0 joined .. 1 apart), glow = inlay emission
  group.setState = (split, glow) => { right.position.z = split * L * .45 + .0005; left.position.z = -split * L * .45 - .0005; mat.emissiveIntensity = glow * 2.2; };
  return group;
}

// ---------------------------------------------------------------- era cities: primitive list (pipeline/citygen.py) -> one geometry
// record: [type, cx, cz, rot, y0, a, b, c, d, e, rank, part, g, gx, gz, bx, bz, shape]; aData = [year, part, rank, 3]; aBase = g (the rise pivot)
export function buildEra(prims, year = 0) {
  const G = new Geo();
  for (const p of prims) {
    const [t, cx, cz, rot, y0, a, b, c, d, e, rank, part, g, gx = 0, gz = 0, bx = cx, bz = cz] = p;
    const data = [t === 0 && d === 1 ? 10 + rot : year, part, rank, 3];   // a road piece carries its direction (the engine draws ruts along it)
    G.gx = gx; G.gz = gz;   // a piece laid along a slope (citygen: walls, corridors, paving)
    G.cc = [bx, bz];        // the building it belongs to: rises and falls as one
    if (t === 0) G.box(cx, y0, cz, a, c, b, rot, data, g);
    else if (t === 1) G.gable(cx, y0, cz, a, b, c, rot, d, data, g);
    else if (t === 2) G.frustum(cx, y0, cz, a, b, d, e, c, rot, data, g);
    else if (t === 3) G.cylinder(cx, y0, cz, a, c, 10, data, g);
    else if (t === 4) G.cone(cx, y0, cz, a, c, 10, data, g);
    else if (t === 5) G.revolve(cx, y0, cz, a / 2, b / 2, c, p[17], d, rot, data, g, e);   // a, b: width, depth; d: sides; e: the share of a turn (0: whole); p[17]: the section
    else if (t === 6) G.prism(cx, y0, cz, p[17], e ? b : c, d, e, rot, data, g);      // a, b: width, depth (laid along: b its length); c: height; d: top scale; e: laid along; p[17]: the rings
  }
  return G.geometry();
}
