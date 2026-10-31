// The film on a phone's graphics: opens the live player (play.html?play) as a phone reports itself (16 textures a shader, 224
// uniform vectors a fragment shader, 256 a vertex shader) and measures what each shader of its scene needs, its uniforms packed
// as ANGLE packs them (the WebGL of Chrome, Safari and the browsers built on them refuses a shader over its graphics' limits, and
// the model is then not drawn: the buildings and the plate go black while the lines and the dust still show). There the page
// sizes its shaders to what the film uses (engine/studio.js fit); a film that still needs more than a phone has (more decals,
// more period cities standing at once, more epoch channels) prints OVER and the tool exits 1: on a phone the page would say it
// cannot draw the film. Run it after a change that adds uniforms or textures to the shaders, and for a film with more of them.
// usage: node tools/phonecheck.mjs <city_slug>
import { openFilm, closeServer } from '../render/page.mjs';

const city = process.argv[2];
if (!city) { console.error('usage: node tools/phonecheck.mjs <city_slug>'); process.exit(2); }
const LIM = { textures: 16, fragment: 224, vertex: 256 };
const { browser, page } = await openFilm(city, { q: 'play=1', onPage: p => p.addInitScript(LIM => {
  const P = WebGL2RenderingContext.prototype, gp = P.getParameter, ss = P.shaderSource, at = P.attachShader, ln = P.linkProgram, src = new WeakMap();
  P.getParameter = function (k) { return k === this.MAX_TEXTURE_IMAGE_UNITS ? LIM.textures : k === this.MAX_FRAGMENT_UNIFORM_VECTORS ? LIM.fragment : k === this.MAX_VERTEX_UNIFORM_VECTORS ? LIM.vertex : gp.call(this, k); };
  P.shaderSource = function (s, t) { src.set(s, t); return ss.call(this, s, t); };
  P.attachShader = function (p, s) { (p.__sh ||= []).push(s); return at.call(this, p, s); };
  window.__progs = [];
  P.linkProgram = function (p) { ln.call(this, p); window.__gl = this; const [a, b] = (p.__sh || []).map(s => src.get(s)); if (a && b) window.__progs.push(/gl_Position/.test(a) ? [a, b] : [b, a]); };
}, LIM) });
const rows = await page.evaluate(() => {
  const gl = window.__gl, E = gl;
  // GLSL ES 1.00 appendix A.7, as ANGLE's VariablePacker does it: the rows of maxRows x 4 that hold these uniforms, or false
  const T = { [E.FLOAT_MAT4]: [4, 4, 0], [E.FLOAT_MAT2]: [2, 2, 1], [E.FLOAT_VEC4]: [1, 4, 2], [E.INT_VEC4]: [1, 4, 2], [E.FLOAT_MAT3]: [3, 3, 3], [E.FLOAT_VEC3]: [1, 3, 4], [E.INT_VEC3]: [1, 3, 4], [E.FLOAT_VEC2]: [1, 2, 5], [E.INT_VEC2]: [1, 2, 5] };
  function fits(vars, maxRows) {
    const v = vars.map(x => { const [r, c, o] = T[x.type] || [1, 1, 6]; return { rows: r * x.size, c, o, n: x.size }; }).sort((a, b) => a.o - b.o || b.n - a.n);
    const rows = new Array(maxRows).fill(0); let top = 0, bottom = maxRows - 1, i = 0;
    const fill = (r0, n, c0, nc) => { const m = ((1 << nc) - 1) << c0; for (let k = r0; k < r0 + n; k++) rows[k] |= m; };
    for (; i < v.length && v[i].c === 4; i++) top += v[i].rows; if (top > maxRows) return false;
    let n3 = 0; for (; i < v.length && v[i].c === 3; i++) n3 += v[i].rows; if (top + n3 > maxRows) return false;
    fill(top, n3, 0, 3);
    const t2 = top + n3, avail = maxRows - t2; let a01 = avail, a23 = avail;
    for (; i < v.length && v[i].c === 2; i++) { const n = v[i].rows; if (n <= a01) a01 -= n; else if (n <= a23) a23 -= n; else return false; }
    fill(t2, avail - a01, 0, 2); fill(maxRows - (avail - a23), avail - a23, 2, 2);
    for (; i < v.length; i++) {
      const n = v[i].rows; let best = -1, bs = maxRows + 1, br = -1;
      for (let c = 0; c < 4; c++) {
        while (top < maxRows && rows[top] === 15) top++; while (bottom >= 0 && rows[bottom] === 15) bottom--;
        if (bottom - top + 1 < n) continue;
        let gt = 0, found = false, sgt = -1, sgs = maxRows + 1;
        for (let r = top; r <= bottom + 1; r++) { const e = r <= bottom ? (rows[r] & (1 << c)) === 0 : false;
          if (e) { if (!found) { gt = r; found = true; } } else { if (found && r - gt >= n && r - gt < sgs) { sgs = r - gt; sgt = gt; } found = false; } }
        if (sgt >= 0 && sgs < bs) { bs = sgs; best = c; br = sgt; }
      }
      if (best < 0) return false; fill(br, n, best, 1);
    }
    return true;
  }
  const need = vars => { let lo = 1, hi = 4096; if (!fits(vars, hi)) return Infinity; while (lo < hi) { const m = (lo + hi) >> 1; if (fits(vars, m)) hi = m; else lo = m + 1; } return lo; };
  const sampler = t => [E.SAMPLER_2D, E.SAMPLER_CUBE, E.SAMPLER_3D, E.SAMPLER_2D_SHADOW, E.SAMPLER_2D_ARRAY].includes(t);
  // one stage's active uniforms: that stage linked with a stub for the other (the fragment shader's stub declares its inputs:
  // its own preprocessor lines and varying declarations, as outputs)
  const mk = (t, s) => { const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh); return sh; };
  const active = (vs, fs) => { const p = gl.createProgram(); gl.attachShader(p, mk(gl.VERTEX_SHADER, vs)); gl.attachShader(p, mk(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) return null;
    const out = []; for (let k = 0; k < gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS); k++) { const u = gl.getActiveUniform(p, k); out.push({ type: u.type, size: u.size }); } return out; };
  const STUBF = '#version 300 es\nprecision highp float; out vec4 o_; void main(){ o_ = vec4(1.); }';
  const stubV = fs => `#version 300 es\n#define varying out\nprecision highp float; precision highp int;\n${fs.split('\n').filter(l => (/^\s*#/.test(l) && !/^\s*#(version|extension)|#define\s+(varying|gl_FragColor|gl_FragDepth|texture|layout)/.test(l)) || (/\bvarying\b/.test(l) && !/#define/.test(l))).join('\n')}\nvoid main(){ gl_Position = vec4(0.); }`;
  const seen = new Set(), out = [];
  for (const [vs, fs] of [...window.__progs]) {
    const key = vs + '\0' + fs; if (seen.has(key) || !/projLight/.test(fs)) continue; seen.add(key);   // (the scene's model shaders: the city, the plate, the plinth, the period cities)
    const v = active(vs, STUBF), f = active(stubV(fs), fs);
    if (!v || !f) { out.push({ name: '(a shader that would not link in parts)' }); continue; }
    out.push({ name: (fs.match(/#define SHADER_NAME (.*)/) || [, ''])[1] || 'MeshStandardMaterial', textures: f.filter(x => sampler(x.type)).length,
      fragment: need(f.filter(x => !sampler(x.type))), vertex: need(v.filter(x => !sampler(x.type))) });
  }
  return [...new Map(out.map(r => [JSON.stringify(r), r])).values()];   // (a shader drawn into the picture and once onto the screen: the same needs)
});
const path = await page.evaluate(() => [...document.querySelectorAll('.unable')].length ? 'cannot draw' : 'drawn');
await browser.close(); closeServer();
let over = false;
console.log(`phone limits: ${LIM.textures} textures, ${LIM.fragment} fragment and ${LIM.vertex} vertex uniform vectors a shader`);
for (const r of rows) {
  const bad = !r.textures || r.textures > LIM.textures || r.fragment > LIM.fragment || r.vertex > LIM.vertex; over ||= bad;
  console.log(`${bad ? 'OVER' : 'ok  '} ${r.name}: ${r.textures ?? '?'} textures, ${r.fragment ?? '?'} fragment vectors, ${r.vertex ?? '?'} vertex vectors`);
}
console.log(rows.length ? (over ? `phonecheck: ${city} needs more than a phone has (${path})` : `phonecheck: ${city} fits a phone's graphics`) : 'phonecheck: no model shader was seen');
process.exit(over || !rows.length ? 1 : 0);
