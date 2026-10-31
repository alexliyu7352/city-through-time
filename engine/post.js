// Post-processing (adapted from lemo-opuscar core/three/post.js, MIT, (c) 2026 LemoLab; see NOTICE): scene -> (MSAA + depth) ->
// [GTAO ambient occlusion] -> physical depth of field (CoC ~ |1/f - 1/z|, spiral sampling) -> bloom -> grade / vignette -> tone mapping -> dither.
// makePost(renderer, scene, camera, w, h, { ssaa: 2, ao: true, ...targets(renderer) }): ssaa is the internal supersampling factor (the
// canvas shows at its CSS size; the browser scales it down in the screenshot); the targets' kind as targets() found it (by default the
// film's: half-float, 4x multisampled, a depth texture)
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { Pass, FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';

const cocShader = {
  uniforms: { tColor: { value: null }, tDepth: { value: null }, tAO: { value: null }, aoAmt: { value: 0 }, aoDebug: { value: 0 }, focus: { value: .3 }, aper: { value: 4 }, maxCoc: { value: 18 }, near: { value: .01 }, far: { value: 50 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`,
  fragmentShader: `
    #include <packing>
    varying vec2 vUv; uniform sampler2D tColor, tDepth, tAO; uniform float aoAmt, focus, aper, maxCoc, near, far, aoDebug;
    void main(){
      float d = texture2D(tDepth, vUv).x;
      float z = -perspectiveDepthToViewZ(d, near, far);
      float c = clamp(aper * (1.0/focus - 1.0/z), -maxCoc, maxCoc);   // negative = near, positive = far (pixels)
      vec3 col = texture2D(tColor, vUv).rgb;
      if (aoAmt > 0.) col *= mix(1., pow(texture2D(tAO, vUv).r, 1.6), aoAmt);
      if (aoDebug > .5) col = vec3(pow(texture2D(tAO, vUv).r, 1.6));
      gl_FragColor = vec4(col, c);
    }`
};
const gatherShader = {
  uniforms: { tIn: { value: null }, res: { value: new THREE.Vector2(1920, 1080) }, maxCoc: { value: 18 } },
  vertexShader: cocShader.vertexShader,
  fragmentShader: `
    varying vec2 vUv; uniform sampler2D tIn; uniform vec2 res; uniform float maxCoc;
    void main(){
      vec4 c0 = texture2D(tIn, vUv); float a0 = abs(c0.a);
      if (maxCoc < .5) { gl_FragColor = vec4(c0.rgb, 1.); return; }
      vec3 acc = c0.rgb / (a0*a0 + 1.); float wsum = 1. / (a0*a0 + 1.);
      const int N = 96;
      for (int i = 0; i < N; i++) {
        float r = maxCoc * sqrt((float(i) + .5) / float(N));
        float th = float(i) * 2.39996;
        vec2 off = vec2(cos(th), sin(th)) * r / res;
        vec4 s = texture2D(tIn, vUv + off);
        float sa = abs(s.a);
        // a sample farther than the centre spreads no wider than the centre's own (keeps the background from bleeding onto a sharp foreground)
        if (s.a > c0.a) sa = min(sa, max(a0, 0.));
        float w = smoothstep(r - 1.5, r + .5, sa) / (sa*sa + 1.);
        acc += s.rgb * w; wsum += w;
      }
      gl_FragColor = vec4(acc / wsum, 1.);
    }`
};

class DofScenePass extends Pass {
  constructor(scene, camera, w, h, o = {}) {
    super(); this.scene = scene; this.camera = camera; this.needsSwap = true; this.s = o.ssaa || 1;
    const type = o.type ?? THREE.HalfFloatType;
    this.rt = new THREE.WebGLRenderTarget(w, h, { samples: o.samples ?? 4, type, depthTexture: new THREE.DepthTexture(w, h, THREE.FloatType) });
    this.rtC = new THREE.WebGLRenderTarget(w, h, { type });
    // no depth of field where the blur's signed size cannot be kept (8-bit targets), nor it or the edge lines without a depth texture that reads right
    this.flat = o.half === false || o.depth === false; this.noDepth = o.depth === false;
    this.coc = new FullScreenQuad(new THREE.ShaderMaterial(cocShader));
    this.gat = new FullScreenQuad(new THREE.ShaderMaterial(gatherShader));
    this.gat.material.uniforms.res.value.set(w, h);
    this.focus = .3; this.aper = 4; this.maxCoc = 16; this.aoAmt = 0;
    if (o.ao) {
      this.ao = new GTAOPass(scene, camera, w, h);
      this.ao.output = GTAOPass.OUTPUT.Off;
      this.ao.updateGtaoMaterial({ radius: o.aoRadius ?? .25, distanceExponent: 1.2, thickness: o.aoThickness ?? 1, scale: o.aoScale ?? 2.5, distanceFallOff: .6, samples: 16 });
      this.ao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6 * this.s, rings: 2, samples: 16 });
      this.aoAmt = o.aoAmt ?? .85;
    }
  }
  // a page that fills its window (studio resize; the film's picture is always 1920 x 1080). Not setSize: the composer calls that
  // with its pixel ratio on top of the supersampling when the pass is added, and the film's pass keeps the size it was made at
  resize(w, h) { this.rt.setSize(w, h); this.rtC.setSize(w, h); this.gat.material.uniforms.res.value.set(w, h); if (this.ao) this.ao.setSize(w, h); }
  render(renderer, writeBuffer) {
    renderer.setRenderTarget(this.rt); renderer.clear(); renderer.render(this.scene, this.camera);
    if (this.ao && this.aoAmt > 0) this.ao.render(renderer, null, null);
    const u = this.coc.material.uniforms;
    u.tColor.value = this.rt.texture; u.tDepth.value = this.rt.depthTexture; u.focus.value = this.focus; u.aper.value = this.aper * this.s; u.maxCoc.value = this.maxCoc * this.s;
    u.near.value = this.camera.near; u.far.value = this.camera.far;
    u.tAO.value = this.ao ? this.ao.gtaoMap : null; u.aoDebug.value = this.aoDebug ? 1 : 0; u.aoAmt.value = this.ao ? this.aoAmt : 0;
    if (this.flat) u.maxCoc.value = 0; if (this.noDepth && u.edgeAmt) u.edgeAmt.value = 0;
    renderer.setRenderTarget(this.rtC); this.coc.render(renderer);
    const g = this.gat.material.uniforms; g.tIn.value = this.rtC.texture; g.maxCoc.value = this.flat ? 0 : this.maxCoc * this.s;
    renderer.setRenderTarget(this.renderToScreen ? null : writeBuffer); this.gat.render(renderer);
  }
}

const vignetteShader = {
  uniforms: { tDiffuse: { value: null }, amt: { value: .35 }, fade: { value: 1 }, warm: { value: 0 }, contrast: { value: 0 }, sat: { value: 1 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
  fragmentShader: `varying vec2 vUv; uniform sampler2D tDiffuse; uniform float amt, fade, warm, contrast, sat;
    void main(){ vec4 c = texture2D(tDiffuse, vUv); vec2 d = vUv - .5; d.x *= 1.25; float v = 1. - amt * smoothstep(.25, .85, length(d));
      c.rgb *= v * fade; c.rgb *= mix(vec3(1.), vec3(1.06, 1., .9), warm);
      float l = dot(c.rgb, vec3(.2126, .7152, .0722)); c.rgb = mix(vec3(l), c.rgb, sat);
      c.rgb = c.rgb * (1. + contrast) / (1. + contrast * c.rgb / (c.rgb + .6));   // soft contrast in linear light
      gl_FragColor = c; }`
};

// the last step, on the finished sRGB picture: noise of about one 8-bit step, so the dark room's gradients do not break into bands
// when the picture is cut to 8 bits (OutputPass does not dither)
const ditherShader = {
  uniforms: { tDiffuse: { value: null } },
  vertexShader: vignetteShader.vertexShader,
  fragmentShader: `varying vec2 vUv; uniform sampler2D tDiffuse;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
    void main(){ vec4 c = texture2D(tDiffuse, vUv); vec2 p = gl_FragCoord.xy; c.rgb += (h(p) - h(p + 17.31)) * (1.5 / 255.); gl_FragColor = c; }`
};

// weather over a living moment's picture: a band of mist drifting across the horizon (uMistY: its height in the frame, 0 bottom)
// and a fine slanting rain; off (the pass disabled) unless a moment asks for it
const weatherShader = {
  uniforms: { tDiffuse: { value: null }, uRain: { value: 0 }, uMist: { value: 0 }, uMistY: { value: .7 }, uT: { value: 0 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
  fragmentShader: `varying vec2 vUv; uniform sampler2D tDiffuse; uniform float uRain, uMist, uMistY, uT;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
    float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f); return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
    float fbm(vec2 p){ float a = .5, s = 0.; for (int i = 0; i < 4; i++) { s += a * vn(p); p *= 2.03; a *= .5; } return s; }
    void main(){ vec4 c = texture2D(tDiffuse, vUv);
      float band = pow(clamp(1. - abs(vUv.y - uMistY) / .16, 0., 1.), 1.3);
      c.rgb = mix(c.rgb, vec3(.55, .6, .66), fbm(vec2(vUv.x * 3. + uT * .04, vUv.y * 6.)) * band * uMist);
      vec2 q = vec2(vUv.x * 160. + vUv.y * 25., vUv.y * 40. + uT * 22.), f = fract(q);
      float s = step(.86, h(floor(q))) * smoothstep(0., .05, f.x) * smoothstep(.12, .05, f.x) * smoothstep(0., .3, f.y) * smoothstep(1., .6, f.y);
      c.rgb += vec3(.7, .74, .8) * s * uRain * .25; gl_FragColor = c; }`
};

export function makePost(renderer, scene, camera, w, h, o = {}) {
  const s = o.ssaa || 1, W = w * s, H = h * s;
  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { type: o.type ?? THREE.HalfFloatType }));
  const dof = new DofScenePass(scene, camera, W, H, o);
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), .2, .5, 1.6);
  if (o.half === false) bloom.enabled = false;   // (its own targets are half-float; and in 8 bits nothing is brighter than white)
  const vig = new ShaderPass(vignetteShader);
  const weather = new ShaderPass(weatherShader); weather.enabled = false;
  const out = new OutputPass();
  composer.addPass(dof); composer.addPass(bloom); composer.addPass(weather); composer.addPass(vig); composer.addPass(out); composer.addPass(new ShaderPass(ditherShader));
  return { composer, dof, bloom, vig, weather };
}

// what kind of target this browser can draw the scene into, tried rather than taken from what it reports (a browser can claim
// what it cannot do, and a target it cannot draw into stays black, with all that is drawn through it): the film's (half-float
// colour, 4x multisampled, a float depth texture), else without multisampling, else in 8-bit colour. Each is drawn into with a
// colour at a known depth and read back through an 8-bit copy -> { type, samples, half, depth } (depth: its depth texture reads
// right), the first whose colour and depth both read right, else the first whose colour does; null when none draws at all
export function targets(renderer) {
  const v = 'void main(){ gl_Position = vec4(position.xy, 0., 1.); }';
  const draw = new FullScreenQuad(new THREE.ShaderMaterial({ vertexShader: v, fragmentShader: 'void main(){ gl_FragColor = vec4(.25, .5, .75, 1.); }' }));
  const read = new FullScreenQuad(new THREE.ShaderMaterial({ uniforms: { c: { value: null }, d: { value: null }, k: { value: 0 } }, vertexShader: v, depthTest: false, depthWrite: false,
    fragmentShader: 'uniform sampler2D c, d; uniform float k; void main(){ gl_FragColor = k < .5 ? texture2D(c, vec2(.5)) : vec4(texture2D(d, vec2(.5)).x); }' }));
  const out = new THREE.WebGLRenderTarget(4, 4), px = new Uint8Array(4), was = renderer.getRenderTarget();
  const reads = (k, rt, want) => { const u = read.material.uniforms; u.c.value = rt.texture; u.d.value = rt.depthTexture; u.k.value = k;
    renderer.setRenderTarget(out); read.render(renderer); px.fill(0); renderer.readRenderTargetPixels(out, 1, 1, 1, 1, px); return want.every((w, i) => Math.abs(px[i] - w) <= 3); };
  const found = [];
  for (const [type, samples] of [[THREE.HalfFloatType, 4], [THREE.HalfFloatType, 0], [THREE.UnsignedByteType, 4], [THREE.UnsignedByteType, 0]]) {
    const rt = new THREE.WebGLRenderTarget(4, 4, { type, samples, depthTexture: new THREE.DepthTexture(4, 4, THREE.FloatType) });
    try { renderer.setRenderTarget(rt); draw.render(renderer);
      const colour = reads(0, rt, [64, 128, 191, 255]); if (colour) found.push({ type, samples, half: type === THREE.HalfFloatType, depth: reads(1, rt, [128, 128, 128]) }); }
    catch { /* (this kind: not drawable here) */ }
    rt.depthTexture.dispose(); rt.dispose();
    if (found.length && found[found.length - 1].depth) break;
  }
  renderer.setRenderTarget(was); out.dispose(); for (const q of [draw, read]) { q.material.dispose(); q.dispose(); }
  return found.find(f => f.depth) || found[0] || null;
}
