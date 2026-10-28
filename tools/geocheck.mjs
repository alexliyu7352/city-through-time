// Geometry check of the period cities and props: every face must point out of the piece it belongs to. WebGL draws a
// triangle's front side only, so a face whose normal points inward is either not drawn from outside (a wall missing, the far
// wall's inner side showing through) or lit as if it faced the other way (a gable end shining white in a roof). Each piece
// (box, gable, frustum, cylinder, cone) is checked on its own: every triangle wound along its normal, and the normal pointing
// away from the piece's centre (a piece laid along a slope is checked as if level); a solid of revolution or a prism, which can
// face inward (a ring's arena wall, a court's inner wall), with a point just off each face: outside the piece's own surface on
// its front, inside on its back. It renders nothing.
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

// whether a point is inside the piece's own surface: a ray up from it crosses that surface an odd number of times (the piece is
// closed but for its foot, which a ray going up never meets); positions level (the slope taken off). Independent of how the
// engine made the surface (a ring's inner wall, a sector's cut ends, a court's hole all count alike)
function closed(tris) {
  const D = [1e-3, 1, 2.3e-3];   // (a ray a hair off the vertical: never along an edge)
  const hit = (o, [a, b, c]) => {   // Möller-Trumbore, the ray o + t D, t > 0
    const e1 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], e2 = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
    const p = [D[1] * e2[2] - D[2] * e2[1], D[2] * e2[0] - D[0] * e2[2], D[0] * e2[1] - D[1] * e2[0]], det = e1[0] * p[0] + e1[1] * p[1] + e1[2] * p[2];
    if (Math.abs(det) < 1e-30) return false;
    const f = 1 / det, s = [o[0] - a[0], o[1] - a[1], o[2] - a[2]], u = f * (s[0] * p[0] + s[1] * p[1] + s[2] * p[2]); if (u < 0 || u > 1) return false;
    const q = [s[1] * e1[2] - s[2] * e1[1], s[2] * e1[0] - s[0] * e1[2], s[0] * e1[1] - s[1] * e1[0]], v = f * (D[0] * q[0] + D[1] * q[1] + D[2] * q[2]); if (v < 0 || u + v > 1) return false;
    return f * (e2[0] * q[0] + e2[1] * q[1] + e2[2] * q[2]) > 0;
  };
  return o => tris.reduce((k, T) => k + hit(o, T), 0) % 2 === 1;
}

// the faces of one piece that fail, as strings
export function faults(P) {
  const { pos, nor } = P, n = pos.length / 9, bad = [];
  const at = j => [pos[j], pos[j + 1] - P.gx * (pos[j] - P.cx) - P.gz * (pos[j + 2] - P.cz), pos[j + 2]];   // (the slope taken off)
  let y0 = Infinity, y1 = -Infinity; for (let j = 0; j < pos.length; j += 3) { const y = at(j)[1]; y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  const C = [P.cx, (y0 + y1) / 2, P.cz];
  let S = null;
  if (P.kind === 'revolve' || P.kind === 'prism') {
    const T = [...Array(n).keys()].map(i => [at(i * 9), at(i * 9 + 3), at(i * 9 + 6)]), xs = T.flat().map(p => p[0]), zs = T.flat().map(p => p[2]);
    S = { inside: closed(T), size: Math.min(Math.max(...xs) - Math.min(...xs), Math.max(...zs) - Math.min(...zs), y1 - y0) };
  }
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
