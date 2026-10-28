// Geometry check of the period cities and props: every face must point out of the piece it belongs to. WebGL draws a
// triangle's front side only, so a face whose normal points inward is either not drawn from outside (a wall missing, the far
// wall's inner side showing through) or lit as if it faced the other way (a gable end shining white in a roof). Each piece
// (box, gable, frustum, cylinder, cone) is checked on its own: every triangle wound along its normal, and the normal pointing
// away from the piece's centre (a piece laid along a slope is checked as if level); a solid of revolution or a prism, which can
// face inward (a ring's arena wall, a court's inner wall), with a point just off each face: outside the solid on its front, inside
// on its back. It renders nothing.
// usage: node tools/geocheck.mjs <city_slug | city folder> [--eras a,b]     exit 1 on any face that fails, naming the city, the piece and where
import fs from 'fs';
import path from 'path';
import { Geo, buildEra, buildProp } from '../engine/props.js';
import { buildDir } from '../render/local.mjs';

const KINDS = ['box', 'gable', 'frustum', 'cylinder', 'cone', 'revolve', 'prism'];

// every piece a build makes, with the triangles it wrote: Geo's shape methods are wrapped while the build runs
export function pieces(build) {
  const out = [], orig = {};
  for (const k of KINDS) {
    orig[k] = Geo.prototype[k];
    Geo.prototype[k] = function (cx, y0, cz, ...rest) {
      const i0 = this.pos.length; orig[k].call(this, cx, y0, cz, ...rest);
      out.push({ kind: k, cx, y0, cz, args: rest, gx: this.gx, gz: this.gz, pos: this.pos.slice(i0), nor: this.nor.slice(i0) });
    };
  }
  try { build(); } finally { for (const k of KINDS) Geo.prototype[k] = orig[k]; }
  return out;
}

const inPoly = (r, x, y) => { let k = false; for (let i = 0, j = r.length - 1; i < r.length; j = i++) { const [xi, yi] = r[i], [xj, yj] = r[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) k = !k; } return k; };
// whether a point (level: the slope taken off) is inside a revolve or a prism (engine/props.js: the same parameters), and the
// solid's size (how far off its faces to test)
function solid(P) {
  const { cx, y0, cz } = P, rot = (P.kind === 'revolve' ? P.args[5] : P.args[4]) || 0, c = Math.cos(rot), s = Math.sin(rot);
  const local = ([X, Y, Z]) => { const dx = X - cx, dz = Z - cz; return [dx * c + dz * s, Y - y0, -dx * s + dz * c]; };
  if (P.kind === 'revolve') {
    const [rx, rz, h, prof, sides = 32, , , , sweep = 1] = P.args, sw = sweep > 0 && sweep < 1 ? sweep : 1, A0 = sw < 1 ? -Math.PI / 2 - sw * Math.PI : 0, st = sw * 2 * Math.PI / sides;
    return { size: Math.min((rx + rz) / 2, h), inside: q => {
      const [x, y, z] = local(q), u = x / rx, w = z / rz, T = 2 * Math.PI, a = ((Math.atan2(w, u) - A0) % T + T) % T;   // (the angle from the start of the turn)
      if (a > sw * T) return false;   // outside the part of a turn
      const am = (Math.floor(a / st) + .5) * st;
      return inPoly(prof, Math.hypot(u, w) * Math.cos(a - am) / Math.cos(st / 2), y / h);   // the radius measured to the facet (a polygon, not the circle)
    } };
  }
  const [rings, h, top = 1, axis = 0] = P.args, O = rings[0], gu = O.reduce((a, p) => a + p[0], 0) / O.length, gv = O.reduce((a, p) => a + p[1], 0) / O.length;
  const us = rings.flat().map(p => p[0]), vs = rings.flat().map(p => p[1]);
  return { size: Math.min(Math.max(...us) - Math.min(...us), Math.max(...vs) - Math.min(...vs), h), inside: q => {
    const [x, y, z] = local(q); let u, v, t;
    if (axis) { u = x; v = y; t = z / h + .5; } else { t = y / h; const k = 1 + (top - 1) * t; if (k <= 0) return false; u = gu + (x - gu) / k; v = gv + (z - gv) / k; }
    return t >= 0 && t <= 1 && inPoly(rings[0], u, v) && !rings.slice(1).some(r => inPoly(r, u, v));
  } };
}

// the faces of one piece that fail, as strings
export function faults(P) {
  const { pos, nor } = P, n = pos.length / 9, bad = [];
  const at = j => [pos[j], pos[j + 1] - P.gx * (pos[j] - P.cx) - P.gz * (pos[j + 2] - P.cz), pos[j + 2]];   // (the slope taken off)
  let y0 = Infinity, y1 = -Infinity; for (let j = 0; j < pos.length; j += 3) { const y = at(j)[1]; y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  const C = [P.cx, (y0 + y1) / 2, P.cz], S = P.kind === 'revolve' || P.kind === 'prism' ? solid(P) : null;
  for (let i = 0; i < n; i++) {
    const a = at(i * 9), b = at(i * 9 + 3), c = at(i * 9 + 6), N = nor.slice(i * 9, i * 9 + 3);
    const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], w = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
    const cr = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
    if (Math.hypot(...cr) < 1e-14) continue;   // a degenerate sliver draws nothing
    if (cr[0] * N[0] + cr[1] * N[1] + cr[2] * N[2] <= 0) { bad.push('wound against its normal'); continue; }
    if (S) {   // the front of the face outside the solid, its back inside
      const L = Math.hypot(...cr), e = S.size * 1e-3, m = [0, 1, 2].map(k => (a[k] + b[k] + c[k]) / 3), off = k => m.map((q, j) => q + k * e * cr[j] / L);
      if (S.inside(off(1)) || !S.inside(off(-1))) bad.push('its front faces into the solid');
      continue;
    }
    const g = [(a[0] + b[0] + c[0]) / 3 - C[0], (a[1] + b[1] + c[1]) / 3 - C[1], (a[2] + b[2] + c[2]) / 3 - C[2]];
    if (g[0] * N[0] + g[1] * N[1] + g[2] * N[2] <= 0) bad.push('its normal points into the piece');
  }
  return bad;
}

// city: a slug (cities/<slug>/) or a city folder (a model study's, tools/modelview.py; compile passes its own)
export function geocheck(city, only = null) {
  const at = (...p) => city.includes('/') ? path.join(path.resolve(city), 'build', ...p) : buildDir(city, ...p);
  const F = JSON.parse(fs.readFileSync(at('film.json'), 'utf8'));
  const runs = [];
  for (const e of F.eras || []) if (!only || only.includes(e.id)) {
    const J = JSON.parse(fs.readFileSync(at(e.file), 'utf8'));
    runs.push([`era ${e.id}`, () => buildEra(J.prims)]);
  }
  for (const p of F.props || []) if (!only || only.includes(p.id)) runs.push([`prop ${p.id}`, () => buildProp(p, () => 0, 1e-4)]);   // (flat ground: the direction of a face does not depend on it)
  let failed = 0; const lines = [];
  for (const [name, build] of runs) {
    const ps = pieces(build), byKind = {};
    for (const P of ps) {
      const f = faults(P); if (!f.length) continue;
      const k = byKind[P.kind] ||= { n: 0, faces: 0, why: new Set(), at: [P.cx, P.cz] }; k.n++; k.faces += f.length; f.forEach(x => k.why.add(x));
    }
    const kinds = Object.entries(byKind);
    if (!kinds.length) { lines.push(`  ok    ${name}: ${ps.length} pieces`); continue; }
    failed++;
    for (const [kind, k] of kinds) lines.push(`  FAIL  ${name}: ${k.n} ${kind} pieces, ${k.faces} faces (${[...k.why].join('; ')}), the first at x ${k.at[0].toFixed(4)} z ${k.at[1].toFixed(4)}`);
  }
  return { failed, lines };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2), city = args[0], i = args.indexOf('--eras');
  if (!city) { console.error('usage: node tools/geocheck.mjs <city_slug | city folder> [--eras a,b]'); process.exit(2); }
  const { failed, lines } = geocheck(city, i >= 0 ? args[i + 1].split(',') : null);
  console.log(`geocheck ${city}:\n${lines.join('\n')}`);
  if (failed) { console.log(`geocheck: ${failed} of the period cities and props have faces pointing the wrong way (engine/props.js Geo)`); process.exit(1); }
  console.log('geocheck: every face points out of its piece');
}
