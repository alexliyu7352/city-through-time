// Post-processing (adapted from lemo-opuscar core/three/post.js, MIT, (c) 2026 LemoLab; see NOTICE): scene -> (MSAA + depth) ->
// [GTAO ambient occlusion] -> [haze] -> physical depth of field (CoC ~ |1/f - 1/z|, spiral sampling) -> bloom -> grade / vignette -> tone mapping -> dither.
// Two effects only where asked (engine/fx.js, film.fx): haze (o.haze), the air between the eye and what it sees, by distance and
// thinning upward, toward the sky's horizon colour; and a stronger depth of field (o.dof2), gathered at the picture's own size
// from the supersampled one with a turning disc of samples and laid over the sharp picture by each pixel's blur (the depth of
// field's gather after lemo-opuscar styles/tilt-shift/demo/post.js, MIT). Without them the passes are the film's as they were.
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
import { SKY_GLSL } from './fx.js';

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
      if (aoAmt > 0. && d < .99999) col *= mix(1., pow(max(texture2D(tAO, vUv).r, 1e-4), 1.6), aoAmt);   // (not on the sky: nothing there to occlude; pow(0, e) is NaN on some graphics)
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

// haze: inserted into the CoC stage (it reads the depth already), before the blur, so far land blurs with its haze. The air's
// density falls off with height (scale uHazeB^-1 above uHazeY0); along the ray from the eye its integral, toward the sky's colour
// at the horizon on that bearing (fx.js fxSky), lit by uHazeI (the room's light in the white model). The sky itself (depth 1)
// is drawn by the sky dome and left alone
const HAZE_HEAD = `uniform mat4 uInvProj, uCamW; uniform vec3 uHazeHor, uHazeZen, uHazeSunC, uHazeSunD; uniform float uHazeD, uHazeB, uHazeY0, uHazeK, uHazeI, uHazeS, uHazeEdge; uniform vec4 uHazeRect, uHazeRect2;
${SKY_GLSL}
float fxRectSd(vec2 p, vec4 r){ return max(max(r.x - p.x, p.x - r.z), max(r.y - p.y, p.y - r.w)); }
// the share of the light the air takes between the eye and depth dd at this pixel; vp: the point in the eye's space
float fxHazeF(float dd, out vec3 vp){
  vec4 vh = uInvProj * vec4(vUv * 2. - 1., dd * 2. - 1., 1.); vp = vh.xyz / vh.w;
  vec3 wd = normalize(mat3(uCamW) * vp); float dist = max(length(vp) - uHazeS, 0.), dy = wd.y * dist * uHazeB;   // (none nearer than uHazeS: what is near keeps its colour)
  float e0 = exp(-max(uCamW[3].y - uHazeY0, 0.) * uHazeB), fi = abs(dy) > 1e-3 ? (1. - exp(-dy)) / dy : 1. - .5 * dy;
  return 1. - exp(-uHazeD * dist * e0 * fi); }`;
const HAZE = `if (d < .99999 && uHazeK > 0.) {
        vec3 vp_; float f_ = fxHazeF(d, vp_); vec3 wd_ = normalize(mat3(uCamW) * vp_);
        if (uHazeEdge > 0.) {   // the land's last uHazeEdge before the end of the model (the plate uHazeRect and the land beyond it uHazeRect2, x0 z0 x1 z1) fades all the way into the haze, in a low view: no step where the land ends against the sky
          vec3 wp_ = uCamW[3].xyz + wd_ * length(vp_); float sd_ = min(fxRectSd(wp_.xz, uHazeRect), fxRectSd(wp_.xz, uHazeRect2));
          f_ = max(f_, smoothstep(-min(uHazeEdge, length(vp_) * .35), 0., sd_) * (1. - smoothstep(.12, .4, -wd_.y))); }   // (over at most a third of the way to it: an edge close behind the subject takes only its last stretch, not the subject)
        col = mix(col, fxSky(normalize(vec3(wd_.x, 0., wd_.z)), uHazeHor, uHazeZen, uHazeSunC, uHazeSunD) * uHazeI, f_ * uHazeK);
      }
      /*GLOW*/gl_FragColor = vec4(col, c);/*GLOWADD*/`;
// the stronger depth of field (o.dof2): the CoC picture (signed blur in supersampled pixels in alpha) box-filtered to the
// picture's own size, gathered there with 128 samples on a disc turned per pixel (noise, not rings), its alpha the share of the
// light that came from a nearer, wider blur (a blurred foreground spreads over what is behind it); then laid over the sharp
// supersampled picture by the pixel's own blur or that share
const gather2Shader = {
  uniforms: { tIn: { value: null }, res: { value: new THREE.Vector2(1920, 1080) }, maxCoc: { value: 18 }, uS: { value: 2 } },
  vertexShader: cocShader.vertexShader,
  fragmentShader: `
    varying vec2 vUv; uniform sampler2D tIn; uniform vec2 res; uniform float maxCoc, uS;
    float h12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
    void main(){
      vec4 c0 = texture2D(tIn, vUv); c0.a /= uS; float a0 = abs(c0.a);
      vec3 acc = c0.rgb / (a0*a0 + 1.); float wsum = 1. / (a0*a0 + 1.), near = 0.;
      float rot = h12(gl_FragCoord.xy) * 6.2832;
      const int N = 128;
      for (int i = 0; i < N; i++) {
        float r = maxCoc * sqrt((float(i) + .5) / float(N));
        float th = float(i) * 2.39996 + rot;
        vec4 s = texture2D(tIn, vUv + vec2(cos(th), sin(th)) * r / res); s.a /= uS;
        float sa = abs(s.a);
        if (s.a > c0.a) sa = min(sa, max(a0, 0.));
        float w = smoothstep(r - 1.5, r + .5, sa) / (sa*sa + 1.);
        acc += s.rgb * w; wsum += w;
        if (s.a < 0. && -s.a > a0 + 1.) near += w * smoothstep(1.5, 4., -s.a);   // (a nearer blur of a few pixels or more)
      }
      gl_FragColor = vec4(acc / wsum, clamp(2.5 * near / wsum, 0., 1.));
    }`
};
const downShader = {
  uniforms: { tIn: { value: null } }, vertexShader: cocShader.vertexShader,
  fragmentShader: 'varying vec2 vUv; uniform sampler2D tIn; void main(){ gl_FragColor = texture2D(tIn, vUv); }'   // (at the centre of each 2 x 2 block: the linear filter averages it)
};
const layShader = {
  uniforms: { tSharp: { value: null }, tBlur: { value: null }, uS: { value: 2 } }, vertexShader: cocShader.vertexShader,
  fragmentShader: `varying vec2 vUv; uniform sampler2D tSharp, tBlur; uniform float uS;
    void main(){ vec4 a = texture2D(tSharp, vUv), b = texture2D(tBlur, vUv);
      float k = max(smoothstep(1., 2.5, abs(a.a) / uS), b.a);   // (under a pixel or so of blur at the picture's size: the sharp picture)
      gl_FragColor = vec4(mix(a.rgb, b.rgb, k), 1.); }`
};

class DofScenePass extends Pass {
  constructor(scene, camera, w, h, o = {}) {
    super(); this.scene = scene; this.camera = camera; this.needsSwap = true; this.s = o.ssaa || 1;
    const type = o.type ?? THREE.HalfFloatType;
    this.rt = new THREE.WebGLRenderTarget(w, h, { samples: o.samples ?? 4, type, depthTexture: new THREE.DepthTexture(w, h, THREE.FloatType) });
    this.rtC = new THREE.WebGLRenderTarget(w, h, { type });
    // no depth of field where the blur's signed size cannot be kept (8-bit targets), nor it or the edge lines without a depth texture that reads right
    this.flat = o.half === false || o.depth === false; this.noDepth = o.depth === false;
    const own = sh => new THREE.ShaderMaterial({ ...sh, uniforms: THREE.UniformsUtils.clone(sh.uniforms) });   // (each pass its own uniforms: two looks' passes on one page)
    this.coc = new FullScreenQuad(own(cocShader));
    this.gat = new FullScreenQuad(own(gatherShader));
    this.gat.material.uniforms.res.value.set(w, h);
    this.focus = .3; this.aper = 4; this.maxCoc = 16; this.aoAmt = 0;
    if (o.haze) {   // (the haze's uniforms and code only where it is asked for: the film's own shader stays as it was)
      const m = this.coc.material, sky = o.haze;
      Object.assign(m.uniforms, { uInvProj: { value: new THREE.Matrix4() }, uCamW: { value: new THREE.Matrix4() }, uHazeHor: { value: new THREE.Color(sky.horizon) }, uHazeZen: { value: new THREE.Color(sky.zenith) },
        uHazeSunC: { value: new THREE.Color(sky.sun) }, uHazeSunD: { value: new THREE.Vector3(0, .3, 1) }, uHazeD: { value: 1 }, uHazeB: { value: 15 }, uHazeY0: { value: 0 }, uHazeK: { value: 1 }, uHazeI: { value: 1 }, uHazeS: { value: 0 }, uHazeEdge: { value: 0 }, uHazeRect: { value: new THREE.Vector4() }, uHazeRect2: { value: new THREE.Vector4() } });
      m.fragmentShader = m.fragmentShader.replace('uniform float aoAmt,', HAZE_HEAD + '\n    uniform float aoAmt,').replace('gl_FragColor = vec4(col, c);', HAZE);
      this.haze = m.uniforms;
    }
    if (o.dof2 && !this.flat) {
      // a sharp band round the focus (uBand: its half-depth, a share of the focus distance; the blur grows only beyond it, a
      // nearer blur at .7 of a farther one), and the depth of light itself (fx.js glow on layer 2, drawn into tGlowD alone):
      // the column of light and the glowing lines are blurred by their own distance, not by the land behind them
      const m = this.coc.material;
      Object.assign(m.uniforms, { uBand: { value: 0 }, tGlowD: { value: null }, uGlowOn: { value: 0 } });
      m.fragmentShader = m.fragmentShader.replace('uniform float aoAmt,', 'uniform float uBand, uGlowOn; uniform sampler2D tGlowD;\n    uniform float aoAmt,')
        .replace('float c = clamp(aper * (1.0/focus - 1.0/z), -maxCoc, maxCoc);', `float zc = z;
      if (uGlowOn > .5) { float dg = texture2D(tGlowD, vUv).x; if (dg < 1.) zc = min(z, -perspectiveDepthToViewZ(dg, near, far)); }
      float c0_ = aper * (1.0/focus - 1.0/zc), c = sign(c0_) * max(abs(c0_) - aper * uBand / focus, 0.);
      c = clamp(c < 0. ? c * .7 : c, -maxCoc, maxCoc);`);
      // with the haze: light drawn on its own (layer 3, into tGlowC) and added after the haze, hazed by its own distance, hidden
      // where the land is nearer (a column standing where the land ends in the haze had its middle taken by the haze's colour)
      this.glowAfter = !!this.haze;
      if (this.glowAfter) {
        Object.assign(m.uniforms, { tGlowC: { value: null } });
        m.fragmentShader = m.fragmentShader.replace('uniform float aoAmt,', 'uniform sampler2D tGlowC;\n    uniform float aoAmt,')
          .replace('/*GLOW*/', `vec3 glow_ = vec3(0.); if (uGlowOn > .5) { float dg_ = texture2D(tGlowD, vUv).x; vec3 gp_; float fg_ = dg_ < .99999 && uHazeK > 0. ? fxHazeF(dg_, gp_) * uHazeK : 0.;
        glow_ = texture2D(tGlowC, vUv).rgb * (dg_ < .99999 ? step(dg_, d + 1e-6) : 1.) * (1. - fg_); }   // (a flare or a spark has no depth of its own: shown)
      `).replace('/*GLOWADD*/', ' gl_FragColor.rgb += glow_;');
      }
      this.rtG = new THREE.WebGLRenderTarget(w, h, { type, depthTexture: new THREE.DepthTexture(w, h, THREE.FloatType) });
      this.glowMat = new THREE.MeshBasicMaterial({ colorWrite: false });
      const s = this.s, lw = Math.round(w / s), lh = Math.round(h / s);
      this.rtD = s > 1 ? new THREE.WebGLRenderTarget(lw, lh, { type, depthBuffer: false }) : null;
      this.rtB = new THREE.WebGLRenderTarget(lw, lh, { type, depthBuffer: false });
      this.down = new FullScreenQuad(own(downShader));
      this.gat2 = new FullScreenQuad(own(gather2Shader)); this.gat2.material.uniforms.res.value.set(lw, lh);
      this.lay = new FullScreenQuad(own(layShader));
    }
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
  resize(w, h) { this.rt.setSize(w, h); this.rtC.setSize(w, h); this.gat.material.uniforms.res.value.set(w, h); if (this.ao) this.ao.setSize(w, h);
    if (this.rtG) this.rtG.setSize(w, h);
    if (this.rtB) { const lw = Math.round(w / this.s), lh = Math.round(h / this.s); this.rtB.setSize(lw, lh); if (this.rtD) this.rtD.setSize(lw, lh); this.gat2.material.uniforms.res.value.set(lw, lh); } }
  render(renderer, writeBuffer) {
    const lit = [];   // (light drawn after the haze: out of the scene's own picture)
    if (this.glowAfter) this.scene.traverse(o => { if (o.userData.fxGlow && o.visible) { o.visible = false; lit.push(o); } });
    renderer.setRenderTarget(this.rt); renderer.clear(); renderer.render(this.scene, this.camera);
    if (this.glowAfter) for (const o of lit) o.visible = true;
    if (this.ao && this.aoAmt > 0) {   // (light itself, fx.js's glowing objects, is no occluder: hidden from the ambient occlusion's own render)
      const lit = []; this.scene.traverse(o => { if (o.userData.fxGlow && o.visible) { o.visible = false; lit.push(o); } });
      this.ao.render(renderer, null, null); for (const o of lit) o.visible = true; }
    const u = this.coc.material.uniforms;
    u.tColor.value = this.rt.texture; u.tDepth.value = this.rt.depthTexture; u.focus.value = this.focus; u.aper.value = this.aper * this.s; u.maxCoc.value = this.maxCoc * this.s;
    u.near.value = this.camera.near; u.far.value = this.camera.far;
    u.tAO.value = this.ao ? this.ao.gtaoMap : null; u.aoDebug.value = this.aoDebug ? 1 : 0; u.aoAmt.value = this.ao ? this.aoAmt : 0;
    if (this.flat) u.maxCoc.value = 0; if (this.noDepth && u.edgeAmt) u.edgeAmt.value = 0;
    if (this.haze) { this.haze.uInvProj.value.copy(this.camera.projectionMatrixInverse); this.haze.uCamW.value.copy(this.camera.matrixWorld); }
    if (this.rtG) {   // the light's own depth (layer 2), nothing else: no background, no colour
      const sc = this.scene, bg = sc.background, ov = sc.overrideMaterial, mask = this.camera.layers.mask;
      const ac = renderer.autoClear; sc.background = null; renderer.setRenderTarget(this.rtG); renderer.clear(); renderer.autoClear = false;
      if (this.glowAfter) { this.camera.layers.set(3); renderer.render(sc, this.camera); }   // (the light itself, every kind, summed: none of it writes depth)
      sc.overrideMaterial = this.glowMat; this.camera.layers.set(2); renderer.render(sc, this.camera);
      sc.background = bg; sc.overrideMaterial = ov; this.camera.layers.mask = mask; renderer.autoClear = ac;
      u.tGlowD.value = this.rtG.depthTexture; u.uGlowOn.value = 1; u.uBand.value = this.band || 0; if (this.glowAfter) u.tGlowC.value = this.rtG.texture;
    }
    renderer.setRenderTarget(this.rtC); this.coc.render(renderer);
    if (this.rtB && this.maxCoc > .5) {   // the stronger depth of field (o.dof2)
      let src = this.rtC.texture;
      if (this.rtD) { this.down.material.uniforms.tIn.value = src; renderer.setRenderTarget(this.rtD); this.down.render(renderer); src = this.rtD.texture; }
      const g2 = this.gat2.material.uniforms; g2.tIn.value = src; g2.maxCoc.value = this.maxCoc; g2.uS.value = this.s;
      renderer.setRenderTarget(this.rtB); this.gat2.render(renderer);
      const l = this.lay.material.uniforms; l.tSharp.value = this.rtC.texture; l.tBlur.value = this.rtB.texture; l.uS.value = this.s;
      renderer.setRenderTarget(this.renderToScreen ? null : writeBuffer); this.lay.render(renderer); return;
    }
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
export function targets(renderer, only8 = false) {   // (only8: the 8-bit fallback forced, gpu=8bit)
  const v = 'void main(){ gl_Position = vec4(position.xy, 0., 1.); }';
  const draw = new FullScreenQuad(new THREE.ShaderMaterial({ vertexShader: v, fragmentShader: 'void main(){ gl_FragColor = vec4(.25, .5, .75, 1.); }' }));
  const read = new FullScreenQuad(new THREE.ShaderMaterial({ uniforms: { c: { value: null }, d: { value: null }, k: { value: 0 } }, vertexShader: v, depthTest: false, depthWrite: false,
    fragmentShader: 'uniform sampler2D c, d; uniform float k; void main(){ gl_FragColor = k < .5 ? texture2D(c, vec2(.5)) : vec4(texture2D(d, vec2(.5)).x); }' }));
  const out = new THREE.WebGLRenderTarget(4, 4), px = new Uint8Array(4), was = renderer.getRenderTarget();
  const reads = (k, rt, want) => { const u = read.material.uniforms; u.c.value = rt.texture; u.d.value = rt.depthTexture; u.k.value = k;
    renderer.setRenderTarget(out); read.render(renderer); px.fill(0); renderer.readRenderTargetPixels(out, 1, 1, 1, 1, px); return want.every((w, i) => Math.abs(px[i] - w) <= 3); };
  const found = [];
  for (const [type, samples] of [[THREE.HalfFloatType, 4], [THREE.HalfFloatType, 0], [THREE.UnsignedByteType, 4], [THREE.UnsignedByteType, 0]].filter(([t]) => !only8 || t !== THREE.HalfFloatType)) {
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
