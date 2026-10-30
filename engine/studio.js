// The showroom (adapted from lemo-opuscar's white-model demo, MIT): a white massing model on a dark plinth, a projector
// above it, house lights. Every data colour is projected light added to the lit white surface in the shader: scaled by how
// squarely the surface faces the projector, limited to the plate, never painted into the material.
// Generic layers (all driven by uniforms from main.js):
//   epochs   up to 8 schematic layers: a mask index map (data/layers.png) on the plate + buildings/mounds by year range
//   growth   up to 8 year bands: each building switches on at band onset + rank * spread, with a short flash
//   height   a level of light climbing every facade; behind it the height colour ramp
//   pick     one building (or mound) lit alone with a halo
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { makePost } from './post.js';
import { buildProp, makeTally, buildEra } from './props.js';

const lin = h => new THREE.Color(h);
export const NMAX = 8;
export const LMAX = 16;
export const BMAX = 32;   // dug pools in a film (compile BASIN_MAX): the plate is lowered in each while it stands   // the parts one period city can lose while the rest stands (compile LOSE_MAX; record kind 4.. in aData.w)
export const GMAX = 8;   // period cities whose open ground (compile ground map) the plate shows at one moment: the most standing at once
export const EMAX = 12;   // epoch mask channels: data/layers1-3.png, RGBA each (compile shares a channel between masks apart in time and place)
const YLN = 48;   // points of the modern year line the shaders read (compile: grow.yl)

export function makeStudio(W, H, M, PAL, opts = {}) {
  const LOW = !!opts.low;   // live preview: pixel ratio 1, no supersampling
  const renderer = new THREE.WebGLRenderer({ antialias: LOW, preserveDrawingBuffer: true });
  renderer.setPixelRatio(LOW ? 1 : 2); renderer.setSize(W, H);
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap; renderer.shadowMap.autoUpdate = false;
  document.getElementById('stage').appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const PW = M.size[0], PD = M.size[1], DIAG = Math.hypot(PW, PD);
  const camera = new THREE.PerspectiveCamera(30, W / H, 0.02, 4 * DIAG);
  // no screen-space ambient occlusion (GTAO): in every low view it turned all beyond some distance black, a straight band
  // across the picture and the far half of each close-up a fifth as bright; the walls' dark foot and the shadows stand in for it
  const post = makePost(renderer, scene, camera, W, H, { ssaa: LOW ? 1 : 2, ao: false });
  post.bloom.strength = .26; post.bloom.radius = .55; post.bloom.threshold = 1.1;   // only what is brighter than white glows: lit white walls bloomed into a milky haze
  post.vig.uniforms.amt.value = .25;   // the corners darken a little (at .42 they took a fifth of a wide shot's light)
  {   // crisp model edges: creases and silhouettes from the Laplacian of inverse depth (planes are linear in 1/z on screen)
    const m = post.dof.coc.material, SS = LOW ? 1 : 2;
    m.uniforms.res = { value: new THREE.Vector2(W * SS, H * SS) }; m.uniforms.edgeAmt = { value: 0 }; m.uniforms.edgeW = { value: SS };
    m.fragmentShader = m.fragmentShader
      .replace('uniform float aoAmt,', 'uniform vec2 res; uniform float edgeAmt, edgeW; uniform float aoAmt,')
      .replace('gl_FragColor = vec4(col, c);', `if (edgeAmt > 0.) {
        vec2 px = edgeW / res; float w0 = 1. / max(z, 1e-6);
        float wl = 1. / max(-perspectiveDepthToViewZ(texture2D(tDepth, vUv - vec2(px.x, 0.)).x, near, far), 1e-6);
        float wr = 1. / max(-perspectiveDepthToViewZ(texture2D(tDepth, vUv + vec2(px.x, 0.)).x, near, far), 1e-6);
        float wd = 1. / max(-perspectiveDepthToViewZ(texture2D(tDepth, vUv - vec2(0., px.y)).x, near, far), 1e-6);
        float wu = 1. / max(-perspectiveDepthToViewZ(texture2D(tDepth, vUv + vec2(0., px.y)).x, near, far), 1e-6);
        float lap = abs(wl + wr + wd + wu - 4. * w0) / w0;
        col *= 1. - edgeAmt * smoothstep(.0025, .012, lap) * smoothstep(.02, .08, abs(texture2D(tColor, vUv).a - .5));   // (not on a draped pool: the ground's creases under its water are no edge)
      }
      gl_FragColor = vec4(col, c);`);
    m.needsUpdate = true;
  }

  // the room: dark, a faint pool of light behind the plinth
  {
    const c = document.createElement('canvas'); c.width = 512; c.height = 288;
    const g = c.getContext('2d'), gr = g.createRadialGradient(256, 150, 10, 256, 160, 320);
    gr.addColorStop(0, '#1b1e22'); gr.addColorStop(.5, '#0b0c0e'); gr.addColorStop(1, '#030304');
    g.fillStyle = gr; g.fillRect(0, 0, 512, 288);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; scene.background = tex;
  }
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(new RoomEnvironment(), .02).texture;

  const arr = (n, v) => Array.from({ length: n }, () => v);
  const cols = (list, n) => { const out = list.map(lin); while (out.length < n) out.push(lin('#000000')); return out.slice(0, n); };
  // ---------------------------------------------------------------- projection uniforms (shared by every surface)
  const U = {
    uProj: { value: 0 }, uNow: { value: 0 }, uYear: { value: -9999 }, uToday: { value: 1 }, uGrowRise: { value: 0 }, uGhost: { value: 0 }, uPulse: { value: 0 },
    uRingC: { value: new THREE.Vector2(0, 0) }, uRingS: { value: .035 }, uRingN: { value: 0 }, uRingA: { value: 0 }, uProjPos: { value: new THREE.Vector3(0, 1.3 * DIAG, .2 * DIAG) }, uKeyDir: { value: new THREE.Vector3(0, 1, 0) },
    uPlate: { value: new THREE.Vector2(PW, PD) }, uWater: { value: null }, uL1: { value: null }, uL2: { value: null }, uL3: { value: null },
    uBase: { value: 0 },                                          // the plate's faint grid under the projector (0..1)
    uEpA: { value: arr(EMAX, 0) }, uEpY0: { value: arr(EMAX, 1e9) }, uEpY1: { value: arr(EMAX, -1e9) }, uEpB: { value: arr(EMAX, 0) },
    uEpC: { value: Array.from({ length: EMAX }, () => new THREE.Vector2(0, 0)) }, uEpR: { value: arr(EMAX, 9) }, uEpRim: { value: arr(EMAX, 1) }, uEpW: { value: arr(EMAX, 1) },
    uD0: { value: null }, uD1: { value: null }, uD2: { value: null }, uD3: { value: null },
    uDA: { value: [0, 0, 0, 0] }, uDG: { value: [1, 1, 1, 1] }, uDrect: { value: Array.from({ length: 4 }, () => new THREE.Vector4(0, 0, 1, 1)) },
    uPhoto: { value: null }, uPhotoA: { value: 0 }, uPhotoSweep: { value: 2 }, uPhotoSweep0: { value: -1 },
    // node colour wave: the old colour (Col0, A0) outside a ring of radius R around C, the new one inside, a light front on the ring
    uNodeCol0: { value: new THREE.Color(1, 1, 1) }, uNodeA0: { value: 0 }, uNodeC: { value: new THREE.Vector2(0, 0) }, uNodeR: { value: 99 }, uNodeFront: { value: 0 },
    uGround: { value: null }, uGroundM: { value: Array.from({ length: GMAX }, () => new THREE.Vector4()) }, uGroundA: { value: Array.from({ length: GMAX }, () => new THREE.Vector4()) },
    uGroundC0: { value: Array.from({ length: GMAX }, () => new THREE.Vector4()) }, uGroundC: { value: Array.from({ length: GMAX }, () => new THREE.Vector4()) }, uGroundN: { value: 0 }, uGroundBand: { value: 4 },
    uBasin: { value: null }, uBasinA: { value: Array(BMAX).fill(0) }, uBasinL: { value: Array.from({ length: BMAX }, () => new THREE.Vector4(0, 0, 1e9, 2e9)) }, uBasinLo: { value: 0 }, uBasinHi: { value: 1 }, uBasinK: { value: 0 }, uBasinBand: { value: 4 }, uWaterRip: { value: .022 }, uWaterGlint: { value: 1.2 }, uWaterShore: { value: .35 },
    uDimToday: { value: 0 }, uDimToday0: { value: 0 }, uEraGlow: { value: 0 }, uEdge: { value: null }, uEdge2: { value: null }, uEdgeGain: { value: 1 },
    // per era channel (the hide masks): era time (0..1 over its rise, -1 off), grow share, the taking-back ring (centre, radius, in/out, width),
    // the edge (alpha, crop of its distance field, falloff); the ring/edge colour is uHideCol
    uHideT: { value: Array(8).fill(-1) }, uHideG: { value: Array(8).fill(.1) }, uHideO: { value: Array.from({ length: 8 }, () => new THREE.Vector2()) }, uHideFR: { value: Array(8).fill(-1) }, uHideFI: { value: Array(8).fill(0) }, uHideFW: { value: Array(8).fill(.01) },
    uEdgeA: { value: Array(8).fill(0) }, uEdgeD: { value: Array(8).fill(.015) }, uEdgeRect: { value: Array.from({ length: 8 }, () => new THREE.Vector4(0, 0, 1, 1)) }, uEdgeLight: { value: .0045 }, uEdgeHalo: { value: .0014 }, uGrowWarm: { value: 0 }, uShockA: { value: 0 }, uShockR: { value: 0 }, uShockC: { value: new THREE.Vector2() }, uHideFA: { value: Array(8).fill(0) }, uRiseA: { value: Array(8).fill(0) }, uRiseMode: { value: Array(8).fill(0) }, uRiseW: { value: Array(8).fill(0) }, uRiseO: { value: Array.from({ length: 8 }, () => new THREE.Vector2()) }, uRiseDir: { value: Array.from({ length: 8 }, () => new THREE.Vector2()) }, uRiseR: { value: Array(8).fill(-1) },
    uResetC: { value: new THREE.Vector2(0, 0) }, uResetR: { value: -1 }, uResetY: { value: 0 }, uGrowMono: { value: 0 }, uYLt: { value: arr(YLN, 1e6) }, uYLy: { value: arr(YLN, 1e6) }, uYLn: { value: 0 }, uGrowDur: { value: 1.8 },   // while a period city stands: today's city dims, its ground glows, a band of light along its edge
    cEp: { value: cols(PAL.epochs || [], EMAX) },
    uGrowOn: { value: 0 }, uGT: { value: arr(NMAX, 99999) }, uGS: { value: arr(NMAX, 1) }, uBLo: { value: arr(NMAX, 1e9) }, uNB: { value: 0 }, uGrowDim: { value: 1 },
    cBand: { value: cols(PAL.bands || [], NMAX) },
    uHgtF: { value: -1 }, uHgtOn: { value: 0 }, uHgtBand: { value: 0 }, uHgtMax: { value: 100 }, cH: { value: cols(PAL.hgt || ['#1a1440', '#5a35d6', '#e2509a', '#ffe7c4'], 4) },
    uPickOn: { value: 0 }, uPickPos: { value: new THREE.Vector2(9, 9) }, uPickR: { value: .02 }, cPick: { value: lin(PAL.pick || '#ffd27a') },
    cBlack: { value: lin(PAL.black || '#0b0f18') },
    uEraA: { value: 0 }, uEraBurn: { value: 0 }, uPhotoK: { value: 1 }, uEraCol: { value: lin('#ffffff') }, uEraFab: { value: .9 },
    cWater: { value: lin(PAL.water || '#1a2129') }, uPlateEmit: { value: PAL.plateEmit ?? .1 }, uNight: { value: 0 }, uLit: { value: .35 }, uScaleH: { value: .0003 }, uScaleM: { value: .0001 }, uFootM: { value: 4 }, uHide: { value: null }, uHide2: { value: null }, uHideCol: { value: Array.from({ length: 8 }, () => new THREE.Color(1, 1, 1)) }, uNodeCol: { value: new THREE.Color(1, 1, 1) }, uNodeA: { value: 0 }, uPlateV: { value: new THREE.Vector2(PW, PD) },
    uShadeL: { value: new THREE.Vector3(0, 1, 0) }, uShadeK: { value: 0 }, uShadeC: { value: lin('#3a4757') },   // terrain.shade (main.js): its hue, the plate's own unless col is written
    uNightDeep: { value: 0 },   // film.night_look.deep: at night today's buildings go dark, a few windows burn brighter (the night city)
    uSpotC: { value: new THREE.Vector2(0, 0) }, uSpotR: { value: 9 }, uSpotK: { value: 1 }, uSpotB: { value: 1 },   // spot: the light falls on a subject, the rest of the room goes dark
    // a living moment: a picture of the period projected from its shot's camera onto the model (uPM), shown inside a ring of light
    // (uPRC, uPRR) and on the far land as the sky comes (uPF beyond uPF0..uPF1 from the ring's centre); uLiveSink: today's city sinks
    uPI: { value: null }, uPM: { value: new THREE.Matrix4() }, uPA: { value: 0 }, uPRC: { value: new THREE.Vector2(0, 0) }, uPRR: { value: 0 }, uPF: { value: 0 },
    uPF0: { value: 9 }, uPF1: { value: 10 }, uLiveSink: { value: 0 },
  };

  // the film's year line from the modern growth on (compile: grow.yl): when the counter first reaches a year. Today's buildings
  // rise at that moment (uGrowDur seconds), one by one as the counter runs, and flash warm as they do
  const YL_GLSL = `uniform float uYLt[${YLN}], uYLy[${YLN}], uYLn, uGrowDur;
  float tOfYear(float y){ for (int i = 0; i < ${YLN - 1}; i++) { if (float(i) + 1.5 > uYLn) break; float y0 = uYLy[i], y1 = uYLy[i + 1];
      if (y1 >= y) return y0 >= y ? uYLt[i] : uYLt[i] + (uYLt[i + 1] - uYLt[i]) * (y - y0) / max(y1 - y0, 1e-4); }
    return 1e6; }`;
  const HEAD = /* glsl */`
  ${YL_GLSL}
  varying float vGrowT;
  uniform float uProj, uNow, uYear, uBase, uGrowOn, uGrowDim, uHgtF, uHgtOn, uHgtBand, uHgtMax, uPickOn, uPickR, uNB, uPulse, uRingS, uRingN, uRingA;
  uniform vec2 uRingC;
  uniform float uEpA[${EMAX}], uEpY0[${EMAX}], uEpY1[${EMAX}], uEpB[${EMAX}], uEpR[${EMAX}], uEpRim[${EMAX}], uEpW[${EMAX}], uGT[${NMAX}], uGS[${NMAX}], uBLo[${NMAX}];
  uniform vec2 uEpC[${EMAX}];
  uniform sampler2D uD0, uD1, uD2, uD3, uPhoto; uniform float uDA[4], uDG[4], uPhotoA, uPhotoSweep, uPhotoSweep0; uniform vec4 uDrect[4];
  // the model-to-photo sweep: the photo covers the plate (and the buildings) between two lines that cross from west to east
  // (the leading line brings the photo in, the trailing one gives the model back)
  float photoK(vec2 uv){ return uPhotoA * (1. - smoothstep(uPhotoSweep - .004, uPhotoSweep + .004, uv.x)) * smoothstep(uPhotoSweep0 - .004, uPhotoSweep0 + .004, uv.x); }
  uniform vec3 uNodeCol0; uniform float uNodeA0, uNodeR, uNodeFront, uDimToday, uDimToday0, uEdgeGain; uniform vec2 uNodeC; uniform sampler2D uEdge, uEdge2;
  uniform float uHideT[8], uHideG[8], uHideFR[8], uHideFI[8], uHideFW[8], uEdgeA[8], uEdgeD[8], uEdgeLight, uEdgeHalo, uGrowWarm; uniform vec2 uHideO[8], uRiseO[8], uRiseDir[8]; uniform float uRiseR[8], uRiseA[8], uRiseMode[8], uRiseW[8], uHideFA[8], uShockA, uShockR; uniform vec2 uShockC; uniform vec4 uEdgeRect[8];
  // a ring of light, the same everywhere (colour rings, fronts, the taking-back ring): a 1-2 px core, a soft glow a few px wide
  // and a faint trail on one side (sgn +1: inside, a growing ring; -1: outside, a contracting one), all in screen pixels
  float ringGlow(float f, float R, float sgn){ float fw = max(fwidth(f), 1e-7), x = abs(f - R);
    float core = 1. - smoothstep(.6 * fw, 2.2 * fw, x), glow = exp(-x / (8. * fw)), d = sgn * (R - f), tr = d > 0. ? exp(-d / (70. * fw)) * .2 : 0.;
    return core * 1.25 + glow * .45 + tr; }
  varying vec2 aCtrV; uniform float uEraInk, uEraInk0;   // ink: the period city dark, its walls, landmarks and streets lit in its colour (秦尚黑 for the empire)
  uniform float uGrowMono;
  uniform vec3 uEraCol0;   // a period city's colour outside the current node's colour ring (inside it: uEraCol)
  uniform vec3 cEp[${EMAX}], cBand[${NMAX}], cH[4], cPick, cBlack;
  uniform vec2 uPlate, uPickPos; uniform vec3 uProjPos, uKeyDir; uniform sampler2D uWater, uL1, uL2, uL3;
  uniform float uEraA, uEraFab, uEraGlow, uNight, uLit, uScaleH, uScaleM, uFootM, uEraBurn, uPhotoK, uPlateEmit, uNodeA; uniform vec3 uEraCol, cWater, uNodeCol, uHideCol[8];
  uniform vec3 uShadeL, uShadeC; uniform float uShadeK, uNightDeep;
  uniform float uSpotR, uSpotK, uSpotB; uniform vec2 uSpotC;
  uniform sampler2D uPI; uniform mat4 uPM; uniform float uPA, uPRR, uPF, uPF0, uPF1; uniform vec2 uPRC;
  uniform sampler2D uHide, uHide2;
  varying vec4 vData; varying vec3 vWP; varying vec3 vWN; varying float vUp; varying float vBase;
  uniform float uLossBurn[${LMAX}];
  float eraBurnK(){ float b = uEraBurn; for (int k = 0; k < ${LMAX}; k++) if (abs(vData.w - 4. - float(k)) < .5) b = max(b, uLossBurn[k]); return b; }   // the whole city burning, or the part of it a fire takes (lose: burn)
  // vData: x = year (0 unknown, negative BCE), y = height m, z = rank 0..1 (switch-on order), w = kind (0 building, 1 mound/earthwork, -1 plate)
  int bandOf(float y){ int b = -1; for (int i = 0; i < ${NMAX}; i++) { if (float(i) < uNB && y >= uBLo[i]) b = i; } return b; }
  vec3 hgtCol(float h){
    float m = max(uHgtMax, 1.);
    float a = clamp(h / (m * .15), 0., 1.), b = clamp((h - m * .15) / (m * .35), 0., 1.), c = clamp((h - m * .5) / (m * .5), 0., 1.);
    return mix(mix(mix(cH[0], cH[1], a), cH[2], b), cH[3] * 1.3, c);
  }
  vec2 plateUV(){ return vWP.xz / uPlate + .5; }
  // era cities: how light each part of a building is (citygen.py parts): walls, landmarks, city walls, bridges, trees,
  // water, openings, paving, roofs, landmark roofs, rammed earth, plinths (a body's base on a slope: a little darker than its
  // walls; at half their light, the plinths of a row stepping down a slope read as a jagged shadow along its foot)
  float eraShade(float p){
    if (p < .5) return uEraFab; if (p < 1.5) return 1.1; if (p < 2.5) return .95; if (p < 3.5) return .75; if (p < 4.5) return .5;
    if (p < 5.5) return .06; if (p < 6.5) return .1; if (p < 7.5) return .3; if (p < 8.5) return .5; if (p < 9.5) return .55; if (p < 10.5) return .8; return .82;   // roofs half the walls' light, tile against plaster, so a roof reads apart from its walls (at .72 they were one tone); darker, a house seen from above reads as a hollow box
  }
  float h21(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
    return mix(mix(h21(i), h21(i + vec2(1., 0.)), f.x), mix(h21(i + vec2(0., 1.)), h21(i + vec2(1., 1.)), f.x), f.y); }
  // paving of a period city seen from above: rammed earth, soft patches and fine grain; a road piece (vData.x > 5: 10 + its
  // direction, citygen strip) also carries cart ruts along it (an asphalt one, 30 + its direction: smooth and darker, no ruts), a pair of tracks 1.4 m apart in every 4.2 m lane, worn more in
  // places. Every detail fades out where one pixel covers more ground than it shows (no shimmer from afar)
  float paveTex(){
    if (normalize(vWN).y < .7) return 1.;
    vec2 P = vWP.xz / uScaleM; float px = length(fwidth(P));   // metres; metres per pixel
    float g = (vnoise(P * .08) - .5) * .5 + (vnoise(P * .6) - .5) * .35 * (1. - smoothstep(.3, 1.2, px)) + (vnoise(P * 2.7) - .5) * .25 * (1. - smoothstep(.08, .35, px));
    if (vData.x > 20.) return .58 + .04 * g;   // asphalt (a street with surface: asphalt): darker, smooth, no ruts
    float k = 1. + .16 * g;
    if (vData.x > 5.) {
      float a = vData.x - 10.; vec2 d = vec2(cos(a), sin(a)), n = vec2(-d.y, d.x);
      float u = dot(P, d), v = dot(P, n), lane = floor(v / 4.2), w = abs(fract(v / 4.2) * 4.2 - 2.1);
      float rut = 1. - smoothstep(.12, .18 + px * 1.2, abs(w - .7));
      rut *= .5 + .5 * vnoise(vec2(u * .03, lane * 3.1));
      k *= 1. - .22 * rut * (1. - smoothstep(.15, .5, px));
    }
    return k;
  }
  // fire on a burning era city: flames licking up from each part's base, every part flickering on its own
  vec3 eraFire(){   // a building burns for a while and then smoulders: about a third alight at any moment, the fire moving through the city
    float hb = fract(sin(dot(aCtrV, vec2(127.1, 311.7))) * 43758.5453), alight = smoothstep(.62, .78, fract(hb * 3.7 + uNow * .23)) * smoothstep(1., .9, fract(hb * 3.7 + uNow * .23));
    float hh = clamp((vWP.y - vBase) / (uScaleH * 14.), 0., 1.);
    float n = fract(sin(vData.z * 931.7 + floor(uNow * 11.) * 1.37) * 43758.5453), n2 = fract(sin(vData.z * 377.1 + floor(uNow * 5.) * 2.11) * 24634.6345);
    return mix(vec3(1., .42, .08), vec3(.75, .07, .01), hh) * (1.25 - hh) * (.25 + .75 * n * n) * (.5 + .5 * n2) * (.12 + 1.6 * alight);
  }
  vec3 photoAt(vec2 uv){ vec3 p = texture2D(uPhoto, uv).rgb; p = pow(p, vec3(1.08)) * 1.18; float l = dot(p, vec3(.299, .587, .114)); p = mix(vec3(l), p, 1.12); return p * vec3(1.02, 1., .97) * uPhotoK; }
  bool onPlate(vec2 uv){ return all(greaterThanEqual(uv, vec2(0.))) && all(lessThanEqual(uv, vec2(1.))); }
  uniform sampler2D uBasin; uniform float uBasinA[${BMAX}], uBasinBand, uWaterRip, uWaterGlint, uWaterShore; uniform vec4 uBasinL[${BMAX}];   // (a draped pool's loss ring: origin, radius now, radius a moment ago)
  float wDrapedK = 0.;   // this fragment's share of a draped pool (wmask sets it): no edge lines are drawn on it (post, the plate's alpha)
  float wmask(){ vec2 uv = plateUV(); if (!onPlate(uv)) return 0.; float w = texture2D(uWater, uv).r;
    // a draped pool (alpha 128 + its number in the basin map): the plate is its water while it stands. Round its edge the map
    // holds the distance to it (texels, + inside, compile BAS_BAND), blended between the four nearest texels, so the edge
    // follows the drawn outline, not the texels' steps (the map is read exactly, nearest, for the dug pools' water tops)
    vec2 ts = vec2(textureSize(uBasin, 0)), p = uv * ts - .5, f = fract(p), c0 = (floor(p) + .5) / ts; float s[4]; int kq[4], k = -1; float top = -1e9;
    for (int q = 0; q < 4; q++) { vec4 b = texture2D(uBasin, c0 + vec2(float(q % 2), float(q / 2)) / ts); s[q] = -uBasinBand; kq[q] = -1;
      if (b.a > 128.5 / 255.) { kq[q] = int(b.a * 255. + .5) - 129; s[q] = ((b.g * 65280. + b.b * 255.) / 65535. - .5) * 2. * uBasinBand; if (s[q] > top) { top = s[q]; k = kq[q]; } } }
    if (k < 0) return w;
    for (int q = 0; q < 4; q++) if (kq[q] != k) s[q] = -uBasinBand;   // (two pools' bands meeting: the nearer pool's)
    float sd = mix(mix(s[0], s[1], f.x), mix(s[2], s[3], f.x), f.y), aa = max(fwidth(sd), .3);
    for (int i = 0; i < ${BMAX}; i++) if (i == k) { vec4 L = uBasinL[i];
      wDrapedK = uBasinA[i] * smoothstep(-aa, aa, sd) * (1. - smoothstep(0., 1., clamp((distance(vWP.xz, L.xy) - L.z) / (L.w - L.z), 0., 1.))); }   // (lost where its ring has passed, as main.js ringK)
    return max(w, wDrapedK); }
  // open ground of the period cities standing (compile ground map, a crop per city): earth, grass, gravel or a paved yard,
  // drawn as the era's paving is, in light and grain only, lit as its paving (its key light tinted, eraKeyT; its projector colour): earth as its streets, a paved yard
  // as an asphalt road. A later city's over an earlier one's; water over all (wmask, after). Per crop (bound by groundsNow):
  // plate xz -> its texels (origin, texels per unit) and the city's colour strength, where it lies in the map (texel origin,
  // size), the city's colour and ink before and after the node's ring (as uEraCol0 / uEraInk0, uEraCol / uEraInk)
  // A platform a lot or a court stands on (part 11, citygen lot_site) is that ground's top where it lies in it (its court, its
  // apron), as the trees of a court on a platform stand on its top: grounds(col, self, false) on its upward faces, its own
  // city's crop only (uGroundSelf, the place groundsNow bound it at, -1 none), the city's light and ink left to its own shading
  uniform sampler2D uGround; uniform vec4 uGroundM[${GMAX}], uGroundA[${GMAX}], uGroundC0[${GMAX}], uGroundC[${GMAX}]; uniform float uGroundN, uGroundBand, uGroundSelf;
  float groundTex(int sf, vec2 P, float px){   // P metres, px metres per pixel: grain that would shimmer fades out
    float g = (vnoise(P * .08) - .5) * .5 + (vnoise(P * .6) - .5) * .35 * (1. - smoothstep(.3, 1.2, px)) + (vnoise(P * 2.7) - .5) * .25 * (1. - smoothstep(.08, .35, px));
    if (sf == 1) return .3 * (1. + .16 * g);   // earth: the streets' rammed earth, no ruts
    if (sf == 2) return .17 * (1. + .3 * (vnoise(P * .05) - .5) + .3 * (vnoise(P * .25) - .5) * (1. - smoothstep(.5, 1.5, px)) + .3 * (vnoise(P * 1.1) - .5) * (1. - smoothstep(.12, .35, px)));   // grass: darker, in soft patches and tufts
    if (sf == 3) return .38 * (1. + .05 * g + .35 * (h21(floor(P * 2.)) - .5) * (1. - smoothstep(.06, .2, px)));   // gravel: lighter, a fine speckle
    return .3 * (.58 + .04 * g);   // paved: an asphalt road's (paveTex)
  }
  // a ground's distance to its edge here (texels, + inside) from the four nearest texels: its own texels as they are, another
  // ground's as their own distance turned round (where two meet the one's edge is the other's: no seam between them), none's
  // as far outside
  float groundSd(int k, float s[4], int kq[4], vec2 f){
    float t[4]; for (int q = 0; q < 4; q++) t[q] = kq[q] == k ? s[q] : kq[q] >= 0 ? -s[q] : -uGroundBand;
    return mix(mix(t[0], t[1], f.x), mix(t[2], t[3], f.x), f.y); }
  float groundOn(int k){ float on = 0.;   // its slot: up as its mark rises, lost where its loss's ring has passed
    for (int j = 0; j < ${BMAX}; j++) if (j == k) { vec4 L = uBasinL[j]; on = uBasinA[j] * (1. - smoothstep(0., 1., clamp((distance(vWP.xz, L.xy) - L.z) / (L.w - L.z), 0., 1.))); }
    return on; }
  float gCover = 0., gEraA = 0., gInk = 0.; vec3 gEcol = vec3(0.), gKeyT = vec3(1.);   // the plate's share of a ground here and its city's light: lit as the city's own paving (projLight, the key light as eraKeyT)
  vec3 grounds(vec3 col, int only, bool tint){
    if (uGroundN < .5) return col;
    vec2 ts = vec2(textureSize(uGround, 0)), P = vWP.xz / uScaleM; float px = length(fwidth(P)), wp = length(fwidth(vWP.xz));
    float iw = smoothstep(uNodeR + .012, uNodeR - .05, length(vWP.xz - uNodeC));   // (inside the node's ring: as the city's own parts)
    for (int i = 0; i < ${GMAX}; i++) { if (float(i) >= uGroundN) break;
      if (only >= 0 && i != only) continue;
      vec4 M = uGroundM[i], A = uGroundA[i]; vec2 l = (vWP.xz - M.xy) * M.z;
      if (any(lessThan(l, vec2(1.))) || any(greaterThan(l, A.zw - 1.))) continue;   // (off its crop; its edge texels hold nothing)
      vec2 p = A.xy + l - .5, f = fract(p), c0 = (floor(p) + .5) / ts; float s[4]; int kq[4], sq[4], k = -1, k2 = -1, sf = 0, sf2 = 0; float top = -1e9, top2 = -1e9;
      for (int q = 0; q < 4; q++) { vec4 b = texture2D(uGround, c0 + vec2(float(q % 2), float(q / 2)) / ts); s[q] = -uGroundBand; kq[q] = -1; sq[q] = 0;
        if (b.b > .5 / 255.) { kq[q] = int(b.b * 255. + .5) - 1; sq[q] = int(b.r * 255. + .5); s[q] = (b.g - .5) * 2. * uGroundBand; } }
      for (int q = 0; q < 4; q++) if (kq[q] >= 0 && s[q] > top) { top = s[q]; k = kq[q]; sf = sq[q]; }
      if (k < 0) continue;
      for (int q = 0; q < 4; q++) if (kq[q] >= 0 && kq[q] != k && s[q] > top2) { top2 = s[q]; k2 = kq[q]; sf2 = sq[q]; }
      vec4 C = mix(uGroundC0[i], uGroundC[i], iw); vec3 kt = mix(vec3(1.), C.rgb / max(max(C.r, C.g), max(C.b, .001)), M.w * .85 * (1. - C.a));
      vec3 base = tint ? vec3(.9) * (1. - .84 * C.a) : vec3(.9); float aa = max(wp * M.z, .3);
      if (k2 >= 0) col = mix(col, base * groundTex(sf2, P, px), groundOn(k2) * smoothstep(-aa, aa, groundSd(k2, s, kq, f)));   // (the other ground at a meeting, under)
      float ck = groundOn(k) * smoothstep(-aa, aa, groundSd(k, s, kq, f));
      col = mix(col, base * groundTex(sf, P, px), ck);
      if (ck > 0.) { gCover = max(gCover * (1. - ck), ck); gEcol = C.rgb; gEraA = M.w; gInk = C.a; gKeyT = kt; }
    }
    return col;
  }
  // water's surface (where wmask is): long swells and short ripples running across it with the wind, in metres and film seconds,
  // each fading out once it is finer than a few pixels (a wide shot keeps the swells, a far one is a still mirror). Its slope
  // tilts the plate's normal, so the room's light and its reflection move on the water as it does on water
  vec2 waterSlope(vec2 P, float px){
    P += (vec2(vnoise(P * .011), vnoise(P * .011 + 17.)) - .5) * 60.;   // (crests bent, not ruled)
    vec2 s = vec2(0.);
    float gust = .35 + 1.3 * vnoise(P * .0045 + vec2(uNow * .02, 0.));   // (the wind uneven over the water: calm patches, rougher ones)
    for (int i = 0; i < 6; i++) {
      float fi = float(i), L = 2.5 * pow(1.7, fi), k = 6.2832 / L, a = .35 + (fract(fi * .618) - .5) * 1.6;   // 2.5 .. 35 m, within 45 degrees of the wind
      vec2 d = vec2(cos(a), sin(a));
      s += d * sin(dot(d, P) * k - sqrt(9.8 * k) * uNow + fi * 2.1) * (1. - smoothstep(L * .04, L * .12, px));   // (a wave goes before it is under 8 pixels: no moire)
    }
    return s * uWaterRip * gust;
  }
  // light caught on the ripples: small points that flare and go, sparse, on water only, at three sizes (a close shot sees
  // the small ones, a wider one the larger), none smaller than a pixel or two
  float waterGlint(vec2 P, float px){
    float g = 0.;
    for (int j = 0; j < 3; j++) {
      float c = j == 0 ? 6. : j == 1 ? 22. : 70.; vec2 q = P / c, i = floor(q), o = vec2(h21(i + 3.1), h21(i + 7.7));
      float h = h21(i), r = length(q - i - .2 - .6 * o) * c, sz = c * .1;
      float tw = pow(max(sin(uNow * (1.3 + 2.1 * h) + h * 31.), 0.), 18.) * step(.72, h);   // (one cell in four has a glint, flaring for a moment now and then)
      g += tw * (1. - smoothstep(sz * .3, sz, r)) * (1. - smoothstep(sz * .6, sz * 1.2, px));
    }
    return g;
  }
  float layerAt(vec2 uv, int i){ if (!onPlate(uv)) return 0.; vec4 m = i < 4 ? texture2D(uL1, uv) : i < 8 ? texture2D(uL2, uv) : texture2D(uL3, uv); int k = i - (i < 4 ? 0 : i < 8 ? 4 : 8); return k == 0 ? m.r : k == 1 ? m.g : k == 2 ? m.b : m.a; }
  // today's buildings inside an epoch's mask (an area the narration names) take its colour in their own material, as a period city
  // takes its node's: the projector light alone was washed out by the lit white walls (the ground showed the colour, the houses not)
  vec3 epTint(vec3 base){
    vec2 uv = plateUV(); vec3 o = base;
    for (int i = 0; i < ${EMAX}; i++) {
      float a = uEpA[i]; if (a <= 0. || uEpB[i] < .5) continue;
      float m = layerAt(uv, i); if (m <= 0.) continue;
      float rv = smoothstep(.08, -.08, length(vWP.xz - uEpC[i]) - uEpR[i]);
      vec3 ec = cEp[i] / max(max(cEp[i].r, cEp[i].g), max(cEp[i].b, .001));
      o = mix(o, base * ec, clamp(a * m * rv * 1.6, 0., 1.));
    }
    return o;
  }
  float aaLine(float x, float period, float w){ float d = abs(fract(x / period + .5) - .5) * period; float fw = fwidth(x); return 1. - smoothstep(w, w + fw * 1.5, d); }
  // how squarely a face meets the key light (followShadow): 1 on level ground and on a face turned to it, a third on the faces turned away
  float keyK(vec3 N){ return (.3 + max(dot(N, uKeyDir), 0.)) / (.3 + max(uKeyDir.y, .2)); }
  // how much of the projected light a face takes: the projector hangs high above the plate, so level ground and roofs take all of
  // it (as squarely as they face it) and a wall little: .3 on the side turned to the key light, .12 on the side turned away. The
  // key light models the walls; the projector's light is what makes a roof the brightest face. (Scaled by keyK, the 45-degree key
  // gave the wall it faced as much as a roof, and the lit modern city went white as one sheet; at a flat .42 on every wall it
  // filled the shade)
  float projK(vec3 N){
    float l = length(uKeyDir.xz), side = l > 1e-4 ? max(dot(N.xz, uKeyDir.xz / l), 0.) : 0.;
    return mix(.42 + .58 * max(dot(N, normalize(uProjPos - vWP)), 0.), .12 + .18 * side, 1. - abs(N.y));
  }
  // kind 0 building/mound, 1 plate, 2 plinth
  vec3 projLight(float kind, float wm){
    vec3 N = normalize(vWN);
    float dirK = projK(N);
    vec2 q = abs(vWP.xz) - (uPlate * .5 + .05);
    float thr = 1. - smoothstep(0., .03, max(q.x, q.y));
    bool bld = kind < .5 && vData.w > -.5;
    float yr = vData.x;
    vec3 c = cBlack * uBase;
    // plate: a faint grid once the projector is on, brightened by the node pulse
    if (kind > .5 && kind < 1.5) c += (cBlack * .5 + vec3(.010, .014, .024) * (1. + 3. * uPulse) * (aaLine(vWP.x, .1, .0005) + aaLine(vWP.z, .1, .0005))) * uBase * (1. - gCover);   // (a period city's ground covers it, as its paving would)
    // the rings of the city: one fine ring per century, spreading from the old town as the counter runs
    if (kind < 1.5 && uRingN > 0.) {
      float rr = length(vWP.xz - uRingC) / uRingS;                    // ring index at this point
      float ring = aaLine(rr, 1., .028) * smoothstep(uRingN, uRingN - 1., rr) * exp(-max(0., uRingN - rr) * .09);   // rings already grown, older ones fading
      float front = exp(-pow((rr - uRingN) * 1.6, 2.)) * .9;             // the newest ring glows as it forms
      c += vec3(.86, .9, 1.) * (ring * .55 + front) * uRingA * (kind < .5 ? .5 : 1.);
    }
    // growth (before the masks, so an area's colour tints the grown buildings inside it): a building flashes as it rises (the moment the counter reaches its year) and stays warm for a while: the growing
    // edge of the city reads all the way through the modern growth, not in bursts
    if (bld && vData.w < .5 && uGrowOn > .5 && yr > 0.) {
      int bd = bandOf(yr);
      if (bd >= 0) {
        float on = uYLn > 1.5 ? (vGrowT > 0. ? vGrowT : tOfYear(yr - .5)) : uGT[bd] + vData.z * uGS[bd], e = uNow - on;
        float a = smoothstep(0., .22, e), fl = e > 0. ? exp(-e / .16) : 0.;
        vec3 bc = uGrowMono > .5 ? mix(vec3(1., .74, .38) * 1.25, vec3(.9, .93, 1.), uGrowWarm > 0. ? smoothstep(.15, uGrowWarm, e) : 1.) : cBand[bd];   // mono: every building rises white (warm while it is new)
        c = mix(c, bc * uGrowDim, a) + bc * fl * 1.4 + vec3(.6) * fl;
      }
    }
    // epochs: schematic masks on the plate, and buildings/mounds whose year falls in the epoch's range
    vec2 uv = plateUV();
    for (int i = 0; i < ${EMAX}; i++) {
      float a = uEpA[i]; if (a <= 0.) continue;
      vec3 ec = cEp[i];
      float rv = smoothstep(.08, -.08, length(vWP.xz - uEpC[i]) - uEpR[i]);              // a wash spreading from the epoch's centre (soft rim)
      float m = kind < 1.5 ? layerAt(uv, i) : 0.;
      float rim = (abs(dFdx(m)) + abs(dFdy(m))) * 14. * uEpRim[i];                          // a glowing edge where the mask ends
      if (kind > .5) m *= .5 * uEpW[i];                                                      // the plate takes the wash quietly, a large area more quietly still (compile: wash); the things on it carry the colour
      else if (vData.w > 1.5) m *= 1.25;                                                     // schematic props a little brighter
      else if (uEpB[i] < .5) m = 0.;                                                         // buildings inside the mask only when the epoch asks for it
      c = mix(c, ec * 1.05, a * m * rv) + ec * clamp(rim, 0., 1.) * a * rv * 1.3;
      if (bld && vData.w < 2.5 && yr != 0. && yr >= uEpY0[i] && yr <= uEpY1[i]) {   // (a period city's x is a road's direction, not a year)                                // by year (mounds, dated parts): each lights as the counter passes its year
        float e = uYear - yr, k = smoothstep(0., 2.5, e), fl = e > 0. ? exp(-e / 2.) : 0.;
        c = mix(c, ec * 1.2, a * rv * k) + ec * fl * .8 * a * rv;
      }
    }
    // height: a level of light climbs every facade; behind it the building takes its height colour
    float s2 = vWP.y - uHgtF;
    float r2 = kind < .5 ? uHgtOn * smoothstep(.0015, -.0015, s2) : uHgtOn * smoothstep(0., .03, uHgtF);
    vec3 a2 = bld ? hgtCol(vData.y) : cH[0] * .5 + vec3(.03, .025, .07) * (aaLine(vWP.x, .1, .0005) + aaLine(vWP.z, .1, .0005));
    if (bld && abs(N.y) < .5) a2 += vec3(.35, .3, .45) * aaLine(vWP.y, .01, .00012);
    c = mix(c, a2, r2);
    float band = bld ? uHgtOn * uHgtBand * exp(-s2 * s2 / 1.6e-5) * .9 : 0.;
    // today's white city takes the colour of the age being told (the reference's grammar: one colour per time node); at a
    // node change the new colour spreads as a ring of light from where the story was, the old colour outside it
    float dW = length(vWP.xz - uNodeC), inW = smoothstep(uNodeR + .004, uNodeR - .025, dW);
    vec3 ncol = mix(uNodeCol0, uNodeCol, inW); float na = mix(uNodeA0, uNodeA, inW);
    if (bld && vData.w < .5) c = mix(c, ncol, na) * (1. - .8 * mix(uDimToday0, uDimToday, inW));   // under a period city's show, today's city steps back, as the node's ring passes
    else if (kind > .5 && kind < 1.5) c += ncol * na * .06;
    if (kind < 1.5 && uNodeFront > 0.) {
      c += mix(uNodeCol, vec3(1.), .25) * ringGlow(dW, uNodeR, 1.) * uNodeFront * (kind > .5 ? 1. : 1.5);
    }
    if (kind < 1.5 && uShockA > .001) c += vec3(1., .97, .9) * ringGlow(length(vWP.xz - uShockC), uShockR, 0.) * uShockA * 1.6;   // a beam's landing: the shock ring
    // period cities on the plate: the front where buildings are being replaced (their rank isoline), the ring that takes a
    // city back, and the edge of a standing city lighting what stands near it (a distance field; the line itself is geometry)
    if (kind < 1.5) {
      vec2 huv = plateUV(); vec4 h1 = texture2D(uHide, huv), h2 = texture2D(uHide2, huv);
      float hm[8]; hm[0] = h1.r; hm[1] = h1.g; hm[2] = h1.b; hm[3] = h1.a; hm[4] = h2.r; hm[5] = h2.g; hm[6] = h2.b; hm[7] = h2.a;
      for (int i = 0; i < 8; i++) {
        float tn = uHideT[i]; if (tn < -.5 && uEdgeA[i] < .001) continue;   // (a city gone may still show its outline: node ghost)
        vec3 hc = min(uHideCol[i], vec3(1.));
        if (uRiseA[i] > .001) {   // the front where the city is being replaced: a ring, a sweeping line, or a band scanning inside the outline
          vec2 dp = vWP.xz - uRiseO[i]; float f = uRiseMode[i] > .5 ? dot(dp, uRiseDir[i]) : length(dp), R = uRiseR[i], inside = smoothstep(.02, .05, hm[i]);
          if (uRiseMode[i] < 1.5) c += mix(hc, vec3(1.), .2) * ringGlow(f, R, 1.) * (.3 + .7 * inside) * uRiseA[i] * (kind > .5 ? 1. : 1.4);
          // scan (a place small on screen): nothing on the ground; its outline draws itself (geometry, addEdge) and each
          // building flashes as it rises (a mask-sized band showed the mask's pixels up close, docs/STAGING.md 9b)
        }
        if (uHideFA[i] > .001) {   // a contracting ring that takes the city back (a growing one is the next node's colour ring)
          float d = length(vWP.xz - uHideO[i]); c += mix(hc, vec3(1.), .2) * ringGlow(d, uHideFR[i], -1.) * uHideFA[i] * (kind > .5 ? 1. : 1.5); }
        if (uEdgeA[i] > .001) {
          vec4 R = uEdgeRect[i]; vec2 q = (huv - R.xy) / (R.zw - R.xy);
          if (all(greaterThanEqual(q, vec2(0.))) && all(lessThanEqual(q, vec2(1.)))) {
            vec4 ev = i < 4 ? texture2D(uEdge, q) : texture2D(uEdge2, q); int k = i < 4 ? i : i - 4;
            float d = (k == 0 ? ev.r : k == 1 ? ev.g : k == 2 ? ev.b : ev.a) * uEdgeD[i];
            c += hc * exp(-pow(d / (kind > .5 ? uEdgeHalo : uEdgeLight), 2.)) * uEdgeA[i] * uEdgeGain * (kind > .5 ? .45 : 1.3);
          }
        }
      }
    }
    // era cities: the whole period city takes the era's colour; landmarks and walls a little brighter; a flash as each part rises
    if (kind < .5 && vData.w > 2.5) {
      float pk = eraShade(vData.y);
      vec3 ecol = mix(uEraCol0, uEraCol, inW);   // a later node's colour ring repaints a city still standing
      float ink = mix(uEraInk0, uEraInk, inW);
      c = mix(c, ecol * pk * .45, uEraA * (1. - ink));   // (at full strength it washed the lit faces past white, roofs and walls one pale tone)
      float fl = vUp * (1. - vUp) * 4.;
      c += ecol * fl * .9 * uEraA + vec3(.4) * fl * uEraA;
      c *= 1. - .9 * eraBurnK();   // charred (the flames are added as emission, see eraFire)
    }
    // a period city's open ground on the plate (grounds): the projector colours it as it does that city's paving (eraShade .3)
    if (kind > .5 && kind < 1.5 && gCover > 0.) c = mix(c, mix(c, gEcol * .3 * .45, gEraA * (1. - gInk)), gCover);
    // decals: graphics projected on the plate (and the things standing on it): emblem, star map, plan, rings
    if (kind < 1.5) {
      for (int i = 0; i < 4; i++) {
        if (uDA[i] <= 0.) continue;
        vec4 r = uDrect[i]; if (uv.x < r.x || uv.y < r.y || uv.x > r.z || uv.y > r.w) continue;
        vec2 duv = (uv - r.xy) / (r.zw - r.xy);
        vec4 d = i == 0 ? texture2D(uD0, duv) : i == 1 ? texture2D(uD1, duv) : i == 2 ? texture2D(uD2, duv) : texture2D(uD3, duv);
        c += d.rgb * d.a * uDA[i] * uDG[i] * .85;
      }
      // today from above: the satellite photo projected on the plate
      if (uPhotoA > 0.) { float pk = photoK(uv), up = smoothstep(.4, .7, N.y); if (bld) c *= 1. - .8 * pk; c += photoAt(uv) * pk * (kind > .5 ? .9 * up : .55 + .35 * up);   // the photo on the plate's top and draped over the buildings
        if (uPhotoSweep > 0. && uPhotoSweep < 1.) c += vec3(.75, .88, 1.) * exp(-pow((uv.x - uPhotoSweep) / .0035, 2.)) * 2.2 * uPhotoA;   // the sweeping line
        if (uPhotoSweep0 > 0. && uPhotoSweep0 < 1.) c += vec3(.75, .88, 1.) * exp(-pow((uv.x - uPhotoSweep0) / .0035, 2.)) * 2.2 * uPhotoA; }
    }
    // pick-out: a halo on the plate around one point, the thing inside lit in the pick colour
    if (uPickOn > 0. && kind < 1.5) {
      float d = length(vWP.xz - uPickPos);
      float halo = exp(-pow(d / uPickR, 2.)) * (kind < .5 ? 1.2 : .55);
      c += cPick * halo * uPickOn;
    }
    vec3 L = (c + vec3(1., .96, .9) * band) * dirK * thr * uProj;
    return L * (1. - .55 * wm);
  }`;

  const RISE_DECL = `${YL_GLSL}
  uniform float uNow; attribute vec4 aData; attribute float aBase; varying vec4 vData; varying vec3 vWP; varying vec3 vWN; varying float vUp; varying float vBase; uniform float uToday, uGrowRise, uYear, uGhost, uLiveSink; uniform sampler2D uHide, uHide2; uniform vec2 uPlateV; attribute vec2 aCtr; uniform vec2 uResetC; uniform float uResetR, uResetY; varying vec2 aCtrV; attribute vec3 aGrowH; attribute float aGrowT; varying float vGrowT;
  uniform float uHideT[8], uHideG[8], uHideFR[8], uHideFI[8], uHideFW[8]; uniform vec2 uHideO[8];
  uniform float uEraT, uEraSpan, uEraGrow, uEraFallR, uEraFallIn, uEraFallW; uniform vec2 uEraO;
  uniform float uLossR[${LMAX}], uLossIn[${LMAX}], uLossW[${LMAX}]; uniform vec2 uLossO[${LMAX}];   // a part of the city lost (lose:): its ring
  uniform sampler2D uBasin; uniform float uBasinA[${BMAX}], uBasinLo, uBasinHi, uBasinK, uPlateTop;   // dug pools (compile basin map): the plate lowered in them
  // a ring that takes a city back: contracting (in) it takes what lies outside it, growing (out) what lies inside. R is the
  // ring now, R1 where it was a sink-time ago: a building the ring passed sinks over that time (0 standing .. 1 gone)
  float fallK(vec2 o, float R, float fin, float R1){ float d = length(aCtr - o);
    float a = fin > .5 ? (d - R) / max(R1 - R, 1e-5) : (R - d) / max(R - R1, 1e-5); return smoothstep(0., 1., a); }
  // today's building over era channel i (m: the rank code there): it steps aside just before the era building beside it rises,
  // and comes back where the era is taken back
  float hideK(float m, int i){ if (m < .02 || uHideT[i] < -.5) return 0.; float r = (m - .04) / .96, g = uHideG[i];
    return smoothstep(r - g * .7, r + g * .15, uHideT[i]) * (1. - fallK(uHideO[i], uHideFR[i], uHideFI[i], uHideFW[i])); }`;
  const RISE = `
 { // rise: buildings grow from the plate as the year counter passes their first-seen year; mounds/props appear at their year; everything is up "today"
   float yr = aData.x; float ry = 1.;
   if (aData.w > -.5 && aData.w < .5) {
     float by = yr > 0. ? (uYLn > 1.5 ? smoothstep(0., uGrowDur, uNow - (aGrowT > 0. ? aGrowT : tOfYear(yr - .5))) : smoothstep(yr - .5, yr + 2.5, uYear)) : smoothstep(1985., 1988., uYear);
     float keep = uGhost;   // the latent city: today's footprints before they grow; a reset ring takes back what came after uResetY
     // rebuilt taller later: f0 of today's height until yA, today's height by yB (only while the modern growth is told)
     float hf = aGrowH.x < .999 ? mix(aGrowH.x, 1., smoothstep(aGrowH.y, aGrowH.z, uYear)) : 1.;
     if (uResetY > 0.) { float inR = smoothstep(-.02, .04, uResetR - length(aCtr - uResetC)); keep *= yr > uResetY ? 1. - inR : mix(1., hf, inR); }
     ry = max(max(uToday, uGrowRise * by * hf), keep);
     vec2 huv = aCtr / uPlateV + .5; vec4 h1 = texture2D(uHide, huv), h2 = texture2D(uHide2, huv);   // where an era city stands, today's buildings step aside,
     float hm[8]; hm[0] = h1.r; hm[1] = h1.g; hm[2] = h1.b; hm[3] = h1.a; hm[4] = h2.r; hm[5] = h2.g; hm[6] = h2.b; hm[7] = h2.a;
     float hk = 0.; for (int i = 0; i < 8; i++) hk = max(hk, hideK(hm[i], i));   // with the same front that raises the era
     ry *= (1. - hk) * (1. - uLiveSink);   // (a living moment: today's city sinks while the period's picture is shown)
     if (hk > .985 || ry < .002) ry = -1.;   // fully stepped aside: below the plate, not a bright sliver of roof on the ground
   }
   else if (aData.w > .5 && aData.w < 1.5) { float by = smoothstep(yr - 1., yr + 3., uYear); ry = max(uToday, by); }
   else if (aData.w > 2.5) {   // era cities: each building rises at its own start (rank x span, from the stages), whole; a ring takes them back
     float st = aData.z * uEraSpan; ry = smoothstep(st, st + uEraGrow, uEraT) * (1. - fallK(uEraO, uEraFallR, uEraFallIn, uEraFallW));
     for (int k = 0; k < ${LMAX}; k++) if (abs(aData.w - 4. - float(k)) < .5) ry *= 1. - fallK(uLossO[k], uLossR[k], uLossIn[k], uLossW[k]);   // a lost part goes with its own ring
     if (ry < .002) ry = -1.; }
   vUp = max(ry, 0.); vBase = aBase; aCtrV = aCtr; vGrowT = aGrowT;
   transformed.y = ry < 0. ? aBase - .02 : aBase + (transformed.y - aBase) * max(ry, .0005);
   if (uPlateTop > .5 && uBasinK > 0.) {   // the plate in a dug pool: below its water while the pool stands, back when it is taken back or lost
     vec4 bs = texture2D(uBasin, transformed.xz / uPlateV + .5);
     if (bs.r > .5 && bs.g + bs.b > .5 / 255.) { int k = int(bs.a * 255. + .5) - 1; float on = 0.; for (int i = 0; i < ${BMAX}; i++) if (i == k) on = uBasinA[i];
       float wy = (uBasinLo + (bs.g * 65280. + bs.b * 255.) / 65535. * (uBasinHi - uBasinLo)) * uBasinK;
       transformed.y = mix(transformed.y, min(transformed.y, wy - .6 * uBasinK), on); } } }`;
  // the same deformation for depth-only passes (ambient-occlusion normals/depth, shadow maps), so they see the city the camera sees
  function deformMaterial(m, extra = null) {
    m.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, U, extra || {});
      sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>\n${RISE_DECL}`).replace('#include <begin_vertex>', `#include <begin_vertex>${RISE}`);
    };
    m.customProgramCacheKey = () => 'deform' + (extra ? Object.keys(extra).length : 0);
    return m;
  }
  function projMaterial(kind, opts, extra = null) {
    const m = new THREE.MeshStandardMaterial(opts);
    m.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, U, extra || {});
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', `#include <common>\n${RISE_DECL}`)
        .replace('#include <begin_vertex>', `#include <begin_vertex>${RISE}`)
        .replace('#include <fog_vertex>', `#include <fog_vertex>\n vData = aData; vWP = (modelMatrix * vec4(transformed, 1.)).xyz; vWN = normalize(mat3(modelMatrix) * objectNormal);`);
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>\n${HEAD}`)
        .replace('#include <color_fragment>', `#include <color_fragment>\n float wm = ${kind === 1 ? 'wmask()' : '0.'}; diffuseColor.rgb = mix(${kind === 1 ? 'grounds(diffuseColor.rgb, -1, true)' : 'diffuseColor.rgb'}, cWater * .72, wm);${kind === 0 ? ' vec3 eraKeyT = vec3(1.); if (vData.w > 2.5) { diffuseColor.rgb *= min(1., eraShade(vData.y)) * (1. - .88 * eraBurnK()); if (abs(vData.y - 5.) < .5 && normalize(vWN).y > .7) diffuseColor.rgb = cWater * .72; if (abs(vData.y - 7.) < .5) diffuseColor.rgb *= paveTex(); if (abs(vData.y - 11.) < .5 && uGroundSelf > -.5 && normalize(vWN).y > .7) diffuseColor.rgb = grounds(diffuseColor.rgb, int(uGroundSelf + .5), false); float iw_ = smoothstep(uNodeR + .012, uNodeR - .05, length(vWP.xz - uNodeC)); vec3 ec_ = mix(uEraCol0, uEraCol, iw_); float ik_ = mix(uEraInk0, uEraInk, iw_); eraKeyT = mix(vec3(1.), ec_ / max(max(ec_.r, ec_.g), max(ec_.b, .001)), uEraA * .85 * (1. - ik_)); diffuseColor.rgb *= 1. - .84 * ik_; } else if (vData.w > -.5 && vData.w < .5) { diffuseColor.rgb = epTint(diffuseColor.rgb); diffuseColor.rgb *= 1. - mix(uDimToday0, uDimToday, smoothstep(uNodeR + .004, uNodeR - .025, length(vWP.xz - uNodeC))); }' : ''}${kind < 2 ? ' { vec2 puv = plateUV(); if (uPhotoA > 0. && onPlate(puv)) { float up = smoothstep(.4, .7, normalize(vWN).y); diffuseColor.rgb = mix(diffuseColor.rgb, photoAt(puv) * mix(.6, 1., up), photoK(puv) * (' + (kind === 1 ? 'up' : '1.') + ')); } }' : ''}`)
        // a period city's colour is in the light that falls on it, not in its plaster: the lamps' direct light (key, fill, rim) takes
        // the era's colour, the room's soft light stays neutral, so its walls are warm where lit and grey in the shade
        .replace('#include <aomap_fragment>', `#include <aomap_fragment>${kind === 0 ? '\n reflectedLight.directDiffuse *= eraKeyT;' : kind === 1 ? '\n reflectedLight.directDiffuse *= mix(vec3(1.), gKeyT, gCover);' : ''}`)
        // water, the plate's (wmask) and a period city's own (its pools' and moats' tops, part 5): its ripples tilt the normal
        .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>${kind < 2 ? `\n float wq_ = ${kind === 1 ? 'wm' : '(vData.w > 2.5 && abs(vData.y - 5.) < .5 ? step(.7, normalize(vWN).y) : 0.)'}; vec2 wP_ = vWP.xz / uScaleM; float wPx_ = length(fwidth(wP_)), wEdge_ = fwidth(wm); vec2 wSl_ = wq_ > 0. ? waterSlope(wP_, wPx_) * wq_ : vec2(0.); normal = normalize(normal + (viewMatrix * vec4(-wSl_.x, 0., -wSl_.y, 0.)).xyz);` : ''}`)
        .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>\n roughnessFactor = mix(roughnessFactor, .28, wm);${kind === 0 ? ' if (vData.w > 2.5 && abs(vData.y - 5.) < .5) roughnessFactor = .28;' : ''}`)
        .replace('#include <opaque_fragment>', `outgoingLight += projLight(${kind}.0, wm) * mix(diffuseColor.rgb, vec3(1.), ${kind === 1 ? 'uPlateEmit' : '.1'}) * 1.35;
 ${kind < 2 ? '{ float sl_ = (1. - smoothstep(0., 1.5 * max(wEdge_, 1e-5), abs(wm - .5))) * smoothstep(.001, .006, wEdge_) * uWaterShore, wg_ = wq_ > .8 ? waterGlint(wP_, wPx_) * smoothstep(.8, .97, wq_) * uWaterGlint : 0.; outgoingLight += vec3(.78, .9, 1.) * sl_ * (.25 + uProj) * .5 + vec3(1., .96, .88) * wg_ * (.35 + uProj); }   // water: a fine lit line along its shore (a pixel or so wide at any distance; none inside a pool fading as a whole), and light caught on its ripples' : ''}
 ${kind === 1 ? '{ float sh_ = clamp((dot(normalize(vWN), uShadeL) - uShadeL.y) / max(1. - uShadeL.y, .01), -1., 1.) * (1. - wm) * step(.5, normalize(vWN).y); vec3 tn_ = mix(uShadeC / max(max(uShadeC.r, uShadeC.g), max(uShadeC.b, .001)), diffuseColor.rgb / max(max(diffuseColor.r, diffuseColor.g), max(diffuseColor.b, .001)), gCover); outgoingLight = outgoingLight * (sh_ < 0. ? max(.5, 1. + .35 * uShadeK * sh_) : 1.) + tn_ * .5 * uShadeK * max(sh_, 0.); }   // terrain.shade: a fixed low sun on the plate top (not its sides): a slope turned to it lit in the plate\'s own hue (a period city\'s ground: in the ground\'s) (at most .5 k, a steel blue on a dark blue plate), a slope turned away darker, flat ground and water as they are; a white light added on the dark plate read as snow on the hills' : ''}
 ${kind === 0 ? `if (vData.w > -.5 && abs(vData.w - 1.) > .5 && abs(normalize(vWN).y) < .5 && !(vData.w > 2.5 && abs(vData.y - 11.) < .5)) {   // a wall darkens toward its foot, where the street and its neighbours hide the room's light: the city stands on the plate instead of floating over it (a period house's plinth is that foot already, and keeps its light). The band is uFootM metres (main.js: a few metres up close, a few pixels' worth from afar)
   float fh_ = (vWP.y - vBase) / uScaleH; outgoingLight *= mix(.62, 1., smoothstep(0., uFootM, fh_)); }
 if (vData.w > 2.5) { float eb_ = eraBurnK(); if (eb_ > 0.) outgoingLight += eraFire() * eb_ * 1.7 * uProj * vUp; }   // a building that has fallen no longer burns
 if (vData.w > 2.5 && max(uEraInk, uEraInk0) > 0.) {   // ink: the dark city's walls, landmarks, streets and ridges lit in its colour
   float iw2 = smoothstep(uNodeR + .012, uNodeR - .05, length(vWP.xz - uNodeC)); float ik2 = mix(uEraInk0, uEraInk, iw2); vec3 ec2 = mix(uEraCol0, uEraCol, iw2); float p2 = vData.y;
   float gold = p2 < .5 ? .05 : p2 < 3.5 ? .7 : p2 < 6.5 ? 0. : p2 < 7.5 ? .35 : p2 < 8.5 ? .12 : p2 < 9.5 ? .8 : .25;
   outgoingLight += ec2 * gold * ik2 * (.35 + .65 * max(normalize(vWN).y, 0.)) * .55 * uProj * (1. - eraBurnK()); }
 if (vData.w > 2.5) outgoingLight += diffuseColor.rgb * uEraCol * uEraGlow * .2 * uProj * (1. - eraBurnK()) * vUp * keyK(normalize(vWN));   // the period city glows a little (it is the subject), more on the faces the key light finds
 if (uNight > 0. && vData.w > -.5 && vData.w < .5) {   // night: lit windows on the facades of today's buildings, roofs dark
   vec3 Nn = normalize(vWN); float fl = (vWP.y - vBase) / (uScaleH * 3.2);           // floors of 3.2 m
   float nd_ = uNightDeep * uNight; if (abs(Nn.y) < .5) outgoingLight *= 1. - .9 * nd_;   // the deep night: the walls go dark, the lit windows carry the city
   if (abs(Nn.y) < .5 && fl > .6) {
     vec2 tg = normalize(vec2(-Nn.z, Nn.x)); float u = dot(vWP.xz, tg) / (uScaleH / 3. * 3.6);  // bays of 3.6 m (plan scale = height scale / exaggeration)
     vec2 cell = vec2(floor(u), floor(fl)); float h = fract(sin(dot(cell + vData.z * 91.7, vec2(12.9898, 78.233))) * 43758.5453);
     vec2 f = fract(vec2(u, fl)); float win = step(.18, f.x) * step(f.x, .82) * step(.25, f.y) * step(f.y, .8);
     float fw = max(fwidth(u), fwidth(fl)); float lit = h < uLit * (1. - .37 * nd_) ? 1. : 0.;
     float e = mix(win * lit, uLit * .3 * (1. - .75 * nd_), smoothstep(.35, .8, fw));   // far away: an average glow instead of aliasing (fewer windows lit in the deep night)
     vec3 wc = mix(vec3(1., .78, .48), vec3(.75, .86, 1.), step(.7, fract(h * 7.3)));
     outgoingLight += wc * e * (1.6 + 2.6 * nd_) * uNight;
   }
   outgoingLight *= mix(1., .6, uNight * step(.5, Nn.y)) * (1. - .85 * nd_ * step(.5, Nn.y));   // (roofs to .35 turned the wide shots of the modern half grey: a roof is most of what a wide shot sees)
 }` : ''}
 ${kind === 1 ? 'outgoingLight *= 1. - .45 * uNightDeep * uNight;' : ''}
 ${kind < 1.5 ? 'outgoingLight *= mix(uSpotK, uSpotB, smoothstep(uSpotR, uSpotR * .35, length(vWP.xz - uSpotC)));' : ''}
 ${kind < 1.5 ? `if (uPA > 0.) {
   vec4 pc_ = uPM * vec4(vWP, 1.); vec2 pu_ = pc_.xy / pc_.w * .5 + .5; float dr_ = length(vWP.xz - uPRC) - uPRR;
   if (pc_.w > 0. && pu_.x > 0. && pu_.x < 1. && pu_.y > 0. && pu_.y < 1.) {
     float in_ = max(smoothstep(.0012, -.0012, dr_), smoothstep(uPF0, uPF1, length(vWP.xz - uPRC)) * uPF);
     outgoingLight = mix(outgoingLight, texture2D(uPI, pu_).rgb, uPA * in_); }
   float gw_ = max(1.5e-4, distance(cameraPosition, vWP) * .012); outgoingLight += vec3(1., .84, .6) * exp(-dr_ * dr_ / (gw_ * gw_)) * uPA * .9 * step(.0001, uPRR) * (1. - uPF); }` : ''}
#include <opaque_fragment>${kind === 1 ? '\n gl_FragColor.a = 1. - .5 * wDrapedK;   // (.5 on a draped pool: the edge pass leaves it out; the scene buffer\'s alpha is read for nothing else)' : ''}`);
    };
    m.customProgramCacheKey = () => 'proj' + kind;
    return m;
  }

  // ---------------------------------------------------------------- the model: extruded footprints (+ mounds), one mesh
  const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  function buildCity() {
    const pos = [], nor = [], dat = [], bas = [], ctr = [], gh = [], gt = [];
    let BASE = 0, CX = 0, CZ = 0, GH = [1, 0, 0], GT = 0;
    const push = (p, n, d) => { pos.push(...p); nor.push(...n); dat.push(...d); bas.push(BASE); ctr.push(CX, CZ); gh.push(...GH); gt.push(GT); };
    const area = r => { let a = 0; for (let i = 0; i < r.length; i++) { const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length]; a += x0 * z1 - x1 * z0; } return a / 2; };
    const prism = (rings, h, d, base = 0) => {
      BASE = base; CX = rings[0].reduce((a, p) => a + p[0], 0) / rings[0].length; CZ = rings[0].reduce((a, p) => a + p[1], 0) / rings[0].length;
      rings.forEach((r, ri) => {
        const A = area(r), sgn = (A > 0 ? 1 : -1) * (ri ? -1 : 1);
        for (let i = 0; i < r.length; i++) {
          const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length];
          const dx = x1 - x0, dz = z1 - z0, L = Math.hypot(dx, dz); if (L < 1e-7) continue;
          const nx = dz / L * sgn, nz = -dx / L * sgn;
          const a = [x0, base, z0], b = [x1, base, z1], c = [x1, base + h, z1], e = [x0, base + h, z0];
          const cx = (b[1] - a[1]) * (e[2] - a[2]) - (b[2] - a[2]) * (e[1] - a[1]);
          const cz = (b[0] - a[0]) * (e[1] - a[1]) - (b[1] - a[1]) * (e[0] - a[0]);
          const tri = cx * nx + cz * nz > 0 ? [a, b, c, a, c, e] : [a, c, b, a, e, c];
          for (const p of tri) push(p, [nx, 0, nz], d);
        }
      });
      const V = THREE.Vector2;
      const contour = rings[0].map(([x, z]) => new V(x, z)), holes = rings.slice(1).map(r => r.map(([x, z]) => new V(x, z)));
      const all = contour.concat(...holes);
      let tris; try { tris = THREE.ShapeUtils.triangulateShape(contour, holes); } catch { return; }
      for (const [i, j, k] of tris) {
        const p = all[i], q = all[j], r = all[k];
        const up = (q.y - p.y) * (r.x - p.x) - (q.x - p.x) * (r.y - p.y) > 0;
        for (const v of (up ? [p, q, r] : [p, r, q])) push([v.x, base + h, v.y], [0, 1, 0], d);
      }
    };
    // frustum: a truncated pyramid (earthwork mounds) from a base ring and a top ring at height h, standing on g
    const frustum = (base, top, h, d, g = 0) => {
      BASE = g; CX = base.reduce((a, p) => a + p[0], 0) / base.length; CZ = base.reduce((a, p) => a + p[1], 0) / base.length;
      const n = base.length;
      for (let i = 0; i < n; i++) {
        const [x0, z0] = base[i], [x1, z1] = base[(i + 1) % n], [tx0, tz0] = top[i], [tx1, tz1] = top[(i + 1) % n];
        const a = [x0, g, z0], b = [x1, g, z1], c = [tx1, g + h, tz1], e = [tx0, g + h, tz0];
        const ux = b[0] - a[0], uy = 0, uz = b[2] - a[2], vx = e[0] - a[0], vy = h, vz = e[2] - a[2];
        let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; const L = Math.hypot(nx, ny, nz) || 1; nx /= L; ny /= L; nz /= L;
        const mx = (x0 + x1) / 2, mz = (z0 + z1) / 2, cx = base.reduce((s, p) => s + p[0], 0) / n, cz = base.reduce((s, p) => s + p[1], 0) / n;
        if ((mx - cx) * nx + (mz - cz) * nz < 0) { nx = -nx; ny = -ny; nz = -nz; }
        const tri = [a, b, c, a, c, e];
        const cxp = (b[1] - a[1]) * (e[2] - a[2]) - (b[2] - a[2]) * (e[1] - a[1]), czp = (b[0] - a[0]) * (e[1] - a[1]) - (b[1] - a[1]) * (e[0] - a[0]);
        for (const p of (cxp * nx + czp * nz > 0 ? tri : [a, c, b, a, e, c])) push(p, [nx, ny, nz], d);
      }
      const V = THREE.Vector2, contour = top.map(([x, z]) => new V(x, z));
      for (const [i, j, k] of THREE.ShapeUtils.triangulateShape(contour, [])) {
        const p = contour[i], q = contour[j], r = contour[k];
        const up = (q.y - p.y) * (r.x - p.x) - (q.x - p.x) * (r.y - p.y) > 0;
        for (const v of (up ? [p, q, r] : [p, r, q])) push([v.x, g + h, v.y], [0, 1, 0], d);
      }
    };
    M.p.forEach(([bi, h, rings, base], i) => {
      const [y0, bh] = M.b[bi], year = EARLY.get(i) ?? y0;   // the first layer dated from GHSL (1975-1987, pipeline/ghsl_change.py)
      GH = RENEW.get(i) || [1, 0, 0];   // rebuilt taller later (pipeline/ghsl_change.py): first f0 of its height, today's height from yA to yB
      GT = GROWT.get(i) || 0;           // rises later than its year: when the camera first sees it (compile, data/grow_t.json)
      prism(rings, h, [year, bh, hash(bi * 1.37 + .5), 0], base || 0);
    });
    GH = [1, 0, 0]; GT = 0;
    for (const m of (M.mounds || [])) frustum(m.base, m.top, m.h, [m.year, m.h_m, 0, 1], m.g || 0);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute('aData', new THREE.Float32BufferAttribute(dat, 4));
    g.setAttribute('aBase', new THREE.Float32BufferAttribute(bas, 1));
    g.setAttribute('aCtr', new THREE.Float32BufferAttribute(ctr, 2));
    g.setAttribute('aGrowH', new THREE.Float32BufferAttribute(gh, 3));
    g.setAttribute('aGrowT', new THREE.Float32BufferAttribute(gt, 1));
    return g;
  }
  const RENEW = new Map(), EARLY = new Map(), GROWT = new Map();
  function setGrowT(list) { for (const [i, t] of list || []) GROWT.set(i, t); }
  function setRenew(list, early) { for (const [i, f0, yA, yB] of list || []) RENEW.set(i, [f0, yA, yB]); for (const [i, y] of early || []) EARLY.set(i, y); }
  const zero = g => { const n = g.attributes.position.count, a = new Float32Array(n * 4); for (let i = 0; i < n; i++) a[i * 4 + 3] = -1; g.setAttribute('aData', new THREE.Float32BufferAttribute(a, 4)); g.setAttribute('aBase', new THREE.Float32BufferAttribute(new Float32Array(n), 1)); return g; };

  // ---------------------------------------------------------------- terrain: a heightfield under the plate (data/terrain.png, 8-bit over min..max metres)
  let HF = null;   // { w, h, data: Float32Array (model units of relief), size: [PW, PD] }
  function ground(x, z) {
    if (!HF) return 0;
    const u = (x / PW + .5) * (HF.w - 1), v = (z / PD + .5) * (HF.h - 1);
    const i0 = Math.max(0, Math.min(HF.w - 2, Math.floor(u))), j0 = Math.max(0, Math.min(HF.h - 2, Math.floor(v))), fu = Math.min(1, Math.max(0, u - i0)), fv = Math.min(1, Math.max(0, v - j0));
    const a = HF.data[j0 * HF.w + i0], b = HF.data[j0 * HF.w + i0 + 1], c = HF.data[(j0 + 1) * HF.w + i0], d = HF.data[(j0 + 1) * HF.w + i0 + 1];
    return (a * (1 - fu) + b * fu) * (1 - fv) + (c * (1 - fu) + d * fu) * fv;
  }
  function setTerrain(img, info, scale) {   // img: HTMLImageElement of terrain.png; info: {min_m, max_m, exaggeration}
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const g = c.getContext('2d'); g.drawImage(img, 0, 0);
    const px = g.getImageData(0, 0, img.width, img.height).data, data = new Float32Array(img.width * img.height);
    const span = (info.max_m - info.min_m) * scale * (info.exaggeration || 3);
    if (img.sixteen) for (let i = 0; i < data.length; i++) data[i] = (px[i * 4] * 256 + px[i * 4 + 1]) / 65535 * span;
    else for (let i = 0; i < data.length; i++) data[i] = px[i * 4] / 255 * span;
    HF = { w: img.width, h: img.height, data };
  }
  function plateGeometry() {   // the plate top: a subdivided plane displaced by the heightfield (flat without one)
    const nx = HF ? 640 : 1, nz = HF ? Math.round(640 * PD / PW) : 1;   // ~50 m cells: buildings and the plate agree within the foundations' depth
    const g = new THREE.PlaneGeometry(PW + .1, PD + .1, nx, nz).rotateX(-Math.PI / 2);
    if (HF) {
      const p = g.attributes.position;
      for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); const inside = Math.abs(x) <= PW / 2 && Math.abs(z) <= PD / 2; p.setY(i, inside ? ground(x, z) : ground(Math.max(-PW / 2, Math.min(PW / 2, x)), Math.max(-PD / 2, Math.min(PD / 2, z)))); }
      g.computeVertexNormals();
    }
    return zero(g);
  }

  // ---------------------------------------------------------------- the land beyond the plate (terrain.context): relief only, shown by node
  // (the mountain a city is named after). A plain lit material, not the plate's: the plate's masks, tints and decals read
  // plate uv and would smear out here. Cells wholly under the plate are dropped; within a cell and a half of its edge the
  // heights blend into the plate's own ground(), so the two meet without a step. Its edges fade into the dark.
  let ctxMesh = null;
  const ctxU = { uCtxA: { value: 0 }, uCtxR: { value: new THREE.Vector4() }, uCtxF: { value: 1 }, uCtxE: { value: 0 }, uCtxS: { value: new THREE.Color() } };
  function addContext(img, c) {   // img: context16.png (16-bit relief in R/G over c.lo..c.hi metres); c: {rect: [x0, x1, z0, z1], lo, hi, ref, ex, exFar, blend, fade, col, shade}
    const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height; const g = cv.getContext('2d'); g.drawImage(img, 0, 0);
    const px = g.getImageData(0, 0, img.width, img.height).data, w = img.width, h = img.height;
    const [x0, x1, z0, z1] = c.rect, cell = (x1 - x0) / (w - 1);
    const pos = new Float32Array(w * h * 3), inside = new Uint8Array(w * h);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      const k = j * w + i, x = x0 + i * cell, z = z0 + j * (z1 - z0) / (h - 1);
      const dx = Math.max(0, Math.abs(x) - PW / 2), dz = Math.max(0, Math.abs(z) - PD / 2), out = Math.hypot(dx, dz);
      const ex = c.ex + ((c.exFar ?? c.ex) - c.ex) * THREE.MathUtils.smoothstep(out, 0, c.blend || 1);   // the plate's exaggeration at its edge, less far off
      let y = ((px[k * 4] * 256 + px[k * 4 + 1]) / 65535 * (c.hi - c.lo) + c.lo - c.ref) * M.scale * ex;
      inside[k] = out === 0 ? 1 : 0;
      const edge = ground(Math.max(-PW / 2, Math.min(PW / 2, x)), Math.max(-PD / 2, Math.min(PD / 2, z)));
      if (out === 0) y = ground(x, z) - .0008;   // under the plate top
      else if (out < cell * 1.5) y = edge + (y - edge) * (out / (cell * 1.5));
      pos[k * 3] = x; pos[k * 3 + 1] = y; pos[k * 3 + 2] = z;
    }
    const idx = [];
    for (let j = 0; j < h - 1; j++) for (let i = 0; i < w - 1; i++) {
      const a = j * w + i, b = a + 1, d = a + w, e = d + 1;
      if (inside[a] && inside[b] && inside[d] && inside[e]) continue;
      idx.push(a, d, b, b, d, e);
    }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setIndex(idx); geo.computeVertexNormals();
    // shade {az, el, k, col}: a fixed low sun baked in as light of its own, so a far mountain's ridges read against the night sky
    // whatever the scene's lamps do. Only slopes turned to that sun catch it (flat ground keeps the plate's colour, a bright plain
    // read as snow); nothing at the plate's edge, full from blend out
    const sd = c.shade || { k: 0 }, sa = THREE.MathUtils.degToRad(sd.az ?? 250), se = THREE.MathUtils.degToRad(sd.el ?? 25);
    const L = new THREE.Vector3(Math.sin(sa) * Math.cos(se), Math.sin(se), -Math.cos(sa) * Math.cos(se)), nrm = geo.attributes.normal, shade = new Float32Array(w * h);
    for (let k = 0; k < w * h; k++) {
      const out = Math.hypot(Math.max(0, Math.abs(pos[k * 3]) - PW / 2), Math.max(0, Math.abs(pos[k * 3 + 2]) - PD / 2));
      shade[k] = Math.max(0, nrm.getX(k) * L.x + nrm.getY(k) * L.y + nrm.getZ(k) * L.z - L.y) / (1 - L.y) * THREE.MathUtils.smoothstep(out, 0, c.blend || 1);
    }
    geo.setAttribute('aShade', new THREE.BufferAttribute(shade, 1));
    const mat = new THREE.MeshStandardMaterial({ color: c.col || PAL.context || PAL.plate || '#262c33', roughness: 1, metalness: 0, transparent: true });
    ctxU.uCtxR.value.set(x0, x1, z0, z1); ctxU.uCtxF.value = c.fade || 1; ctxU.uCtxE.value = sd.k || 0; ctxU.uCtxS.value = lin(sd.col || '#c9d6e8');
    mat.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, ctxU);
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vCW; attribute float aShade; varying float vShade;')
        .replace('#include <fog_vertex>', '#include <fog_vertex>\n vCW = (modelMatrix * vec4(transformed, 1.)).xyz; vShade = aShade;');
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform float uCtxA, uCtxF, uCtxE; uniform vec3 uCtxS; uniform vec4 uCtxR; varying vec3 vCW; varying float vShade;')
        .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n totalEmissiveRadiance += uCtxS * vShade * uCtxE;')
        .replace('#include <dithering_fragment>', '#include <dithering_fragment>\n float ce = min(min(vCW.x - uCtxR.x, uCtxR.y - vCW.x), min(vCW.z - uCtxR.z, uCtxR.w - vCW.z));\n gl_FragColor.a *= uCtxA * smoothstep(0., uCtxF, ce);');
    };
    ctxMesh = new THREE.Mesh(geo, mat); ctxMesh.visible = false; ctxMesh.frustumCulled = false; ctxMesh.renderOrder = 1; scene.add(ctxMesh);
  }
  function setContext(a) { if (!ctxMesh) return; ctxU.uCtxA.value = a; ctxMesh.visible = a > .002; }

  // ---------------------------------------------------------------- props: schematic models that appear at their time (scale.y from the ground)
  const props = {};
  function addProp(p) {
    const geo = buildProp(p, ground, M.scale, (M.terrain && M.terrain.exaggeration) || 3);
    const mesh = new THREE.Mesh(geo, projMaterial(0, { color: '#f3f3f1', roughness: .88, metalness: 0 }));
    mesh.castShadow = mesh.receiveShadow = true; mesh.frustumCulled = false; scene.add(mesh);
    props[p.id] = mesh;
    return mesh;
  }
  // era cities: one mesh per period, each with its own rise/sink/colour uniforms
  const eras = {};
  function addEra(id, prims, col, lost = null) {
    const geo = buildEra(prims, 0, lost);
    const u = { uGroundSelf: { value: -1 }, uEraT: { value: -1 }, uEraSpan: { value: 1 }, uEraGrow: { value: 1 }, uEraFallR: { value: -1 }, uEraFallIn: { value: 0 }, uEraFallW: { value: .01 }, uEraO: { value: new THREE.Vector2() }, uEraInk: { value: 0 }, uEraInk0: { value: 0 }, uEraA: { value: 0 }, uEraBurn: { value: 0 }, uEraCol: { value: lin(col || '#ffd9a0') }, uEraCol0: { value: lin(col || '#ffd9a0') }, uEraFab: { value: 1.0 }, uEraGlow: { value: 0 },
      uLossR: { value: Array(LMAX).fill(-1) }, uLossIn: { value: Array(LMAX).fill(0) }, uLossW: { value: Array(LMAX).fill(.01) }, uLossBurn: { value: Array(LMAX).fill(0) }, uLossO: { value: Array.from({ length: LMAX }, () => new THREE.Vector2()) } };
    const mesh = new THREE.Mesh(geo, projMaterial(0, { color: '#f4f2ee', roughness: .86, metalness: 0 }, u));
    mesh.customDepthMaterial = deformMaterial(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), u);
    mesh.castShadow = !LOW; mesh.receiveShadow = true; mesh.frustumCulled = false; mesh.visible = false; scene.add(mesh);   // live preview: era cities cast no shadow (the shadow pass would draw them twice)
    eras[id] = { mesh, u, base: u.uEraCol.value.clone() };
    return eras[id];
  }
  // light routes: a glowing path drawn along a raised arc (a capital moving, a river shifting, a distance): the head is a
  // comet, the drawn part carries travelling pulses; additive, so it reads as light over the model
  const routes = {};
  const LREF = 1.2, LKMIN = .1;   // lines and routes keep their width from 1.2 model units out, and thin to a tenth closer in
  function addRoute(id, pts, col, width = .0018) {
    const curve = new THREE.CatmullRomCurve3(pts.map(p => new THREE.Vector3(...p)), false, 'centripetal');
    const geo = new THREE.TubeGeometry(curve, Math.max(64, pts.length * 48), width, 8, false);
    const u = { uProg: { value: 0 }, uA: { value: 0 }, uCol: { value: lin(col) }, uNow: U.uNow, uW0: { value: width }, uRef: { value: LREF }, uKmin: { value: LKMIN } };
    const mat = new THREE.ShaderMaterial({ uniforms: u, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      // the tube thins as the camera comes close, so a route stays a line of light in a street-level shot instead of a beam
      vertexShader: `uniform float uW0, uRef, uKmin; varying vec2 vUv; void main(){ vUv = uv; vec3 c = position - normal * uW0;
        float k = clamp(distance(cameraPosition, (modelMatrix * vec4(c, 1.)).xyz) / uRef, uKmin, 1.);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(c + normal * uW0 * k, 1.); }`,
      fragmentShader: `uniform float uProg, uA, uNow; uniform vec3 uCol; varying vec2 vUv;
        void main(){ float x = vUv.x; if (x > uProg) discard;
          float head = exp(-pow((uProg - x) / .018, 2.)) * 3.;
          float pulse = .55 + .45 * smoothstep(.6, 1., sin((x * 26. - uNow * 3.) ));
          gl_FragColor = vec4(uCol * (pulse + head) * uA * 1.4, 1.); }` });
    const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false; mesh.renderOrder = 5; scene.add(mesh);
    const head = new THREE.Mesh(new THREE.SphereGeometry(width * 2.2, 16, 12), new THREE.MeshBasicMaterial({ color: lin(col).multiplyScalar(3), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    head.renderOrder = 6; scene.add(head);
    routes[id] = { curve, u, head, set(prog, a, flash = 0) { u.uProg.value = prog; u.uA.value = a; mesh.visible = head.visible = (a > .002 && prog > .001) || flash > .01; head.position.copy(curve.getPointAt(Math.min(1, prog)));
      head.material.opacity = Math.min(1, a * (prog < 1 ? 1 : .6) + flash);   // flash: the landing (a burst of light where the beam hits)
      head.scale.setScalar(Math.min(1, Math.max(LKMIN, head.position.distanceTo(camera.position) / LREF)) * (1 + 7 * flash)); } };   // camera is placed before the layers each frame
    return routes[id];
  }
  // the edge of a standing period city: a thin neon line draped on the ground along its outline (the reference's lit edge).
  // The tube keeps about the same width on screen at any distance (radius = uW x camera distance); its core is near white,
  // its rim the city's colour; bloom gives the glow. set(alpha, colour).
  const edges = {};
  // the neon line on a standing city's outline. `start` (a direction [dx, dz]): the line can draw itself (uDraw 0..1) both ways
  // round from the point of the outline furthest against it, the two ends meeting on the far side, a bright head on each
  function addEdge(id, rings, col, start = null) {
    const u = { uA: { value: 0 }, uCol: { value: lin(col) }, uW: { value: .0007 }, uWmax: { value: .006 }, uDraw: { value: 1 } };
    const mat = new THREE.ShaderMaterial({ uniforms: u, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: `uniform float uW, uWmax; varying vec3 vN; varying vec3 vV; varying float vS;
        void main(){ vec3 c = position - normal * .0001; float r = min(uWmax, uW * distance(cameraPosition, (modelMatrix * vec4(c, 1.)).xyz));
          vec4 mv = modelViewMatrix * vec4(c + normal * r, 1.); vN = normalize(normalMatrix * normal); vV = -mv.xyz; vS = 1. - abs(1. - 2. * uv.x); gl_Position = projectionMatrix * mv; }`,
      fragmentShader: `uniform float uA, uDraw; uniform vec3 uCol; varying vec3 vN; varying vec3 vV; varying float vS;
        void main(){ if (vS > uDraw + 1e-4) discard; float f = abs(dot(normalize(vN), normalize(vV)));
          float head = uDraw < 1. ? exp(-pow((uDraw - vS) / .025, 2.)) : 0.;
          gl_FragColor = vec4((uCol * (.25 + 1.3 * pow(f, 2.5)) + vec3(1.) * pow(f, 10.) * .9 + vec3(1.) * head * 1.6) * uA, 1.); }` });
    const meshes = [];
    for (const r0 of rings) {
      let r = r0.length > 2 && r0[0][0] === r0[r0.length - 1][0] && r0[0][1] === r0[r0.length - 1][1] ? r0.slice(0, -1) : r0;
      if (start) { let k = 0, best = Infinity; r.forEach(([x, z], i) => { const v = x * start[0] + z * start[1]; if (v < best) { best = v; k = i; } }); r = r.slice(k).concat(r.slice(0, k)); }
      const pts = [];
      for (let i = 0; i < r.length; i++) {   // every ~10 m, on the ground (the plate is linear between its 50 m vertices: a few metres above)
        const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length], n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, z1 - z0) / .001));
        for (let k = 0; k < n; k++) { const x = x0 + (x1 - x0) * k / n, z = z0 + (z1 - z0) * k / n; pts.push(new THREE.Vector3(x, ground(x, z) + .0005, z)); }
      }
      if (pts.length < 4) continue;
      const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true, 'centripetal'), pts.length, .0001, 6, true);
      const m = new THREE.Mesh(geo, mat); m.frustumCulled = false; m.renderOrder = 4; m.visible = false; scene.add(m); meshes.push(m);
    }
    edges[id] = { u, set(a, c, draw = 1) { u.uA.value = a; u.uDraw.value = draw; if (c) u.uCol.value.copy(c); for (const m of meshes) m.visible = a > .002; } };
    return edges[id];
  }
  // the key light stands to the camera's front left, KEY_SIDE degrees round from it at KEY_EL above the plate, whichever way
  // the camera looks (az: the camera's bearing from its target, main.js): the faces the camera sees are lit from the side and
  // cast their shadows away to the right. A light fixed in the room lit half the film's shots from behind, every face in shade.
  // The rim stands behind the city on the other side. The key's shadow follows the camera target so close-ups get sharp
  // shadows (texel ~ 0.7 m at the closest shots)
  const KEY_SIDE = -50, KEY_EL = 45, RIM_SIDE = 150, RIM_EL = 28, keyDir = new THREE.Vector3(), rimDir = new THREE.Vector3();
  function followShadow(tx, ty, tz, d, az) {
    const S = Math.min(DIAG * .55, Math.max(.06, d * .75)), rad = THREE.MathUtils.degToRad;
    keyDir.setFromSphericalCoords(1, rad(90 - KEY_EL), rad(az + KEY_SIDE)); rimDir.setFromSphericalCoords(1, rad(90 - RIM_EL), rad(az + RIM_SIDE));
    house.position.set(tx + keyDir.x * DIAG * 1.2, ty + keyDir.y * DIAG * 1.2, tz + keyDir.z * DIAG * 1.2);
    house.target.position.set(tx, ty, tz); house.target.updateMatrixWorld(); U.uKeyDir.value.copy(keyDir);
    rim.position.set(tx + rimDir.x * DIAG, ty + rimDir.y * DIAG, tz + rimDir.z * DIAG);
    rim.target.position.set(tx, ty, tz); rim.target.updateMatrixWorld();
    Object.assign(house.shadow.camera, { left: -S, right: S, top: S, bottom: -S, near: .05, far: DIAG * 2.6 });
    house.shadow.camera.updateProjectionMatrix();
    house.shadow.normalBias = .0015 * S / (DIAG * .55) + .00008; house.shadow.bias = -.00002;
  }
  // the emblem (a tiger tally), bronze with gold inlay
  const tally = makeTally({ length: .095 }); tally.visible = false; scene.add(tally);
  const tallyLight = new THREE.PointLight('#ffe2b0', 0, 1.2, 1.4); tallyLight.position.set(.06, .09, .08); tally.add(tallyLight);
  const tallyFill = new THREE.PointLight('#bcd0ff', 0, 1.0, 1.4); tallyFill.position.set(-.08, .05, -.06); tally.add(tallyFill);
  tally.setLight = (k) => { tallyLight.intensity = .012 * k; tallyFill.intensity = .005 * k; };

  // ---------------------------------------------------------------- projected lines (roads, rail): flat ribbons just above the plate
  const lineGroups = {};
  function addLines(id, polylines, col, width, flow = 0, kmax = 1) {   // kmax > 1: in a wide shot the line keeps its width on screen (up to kmax x)
    const pos = [], idx = [], arc = [], side = [];
    for (const pts of polylines) {
      if (pts.length < 2) continue;
      const base = pos.length / 3; let sAcc = 0;
      for (let i = 0; i < pts.length; i++) {
        if (i) sAcc += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); arc.push(sAcc, sAcc);
        const [x0, z0] = pts[Math.max(0, i - 1)], [x1, z1] = pts[Math.min(pts.length - 1, i + 1)];
        let dx = x1 - x0, dz = z1 - z0; const L = Math.hypot(dx, dz) || 1; dx /= L; dz /= L;
        const nx = -dz * width / 2, nz = dx * width / 2, [x, z] = pts[i], gy = ground(x, z);
        pos.push(x, gy, z, x, gy, z); side.push(nx, nz, -nx, -nz);   // the centre line; the half-width goes on in the shader
        if (i) { const b = base + i * 2; idx.push(b - 2, b - 1, b, b - 1, b + 1, b); }
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aArc', new THREE.Float32BufferAttribute(arc, 1));
    g.setAttribute('aSide', new THREE.Float32BufferAttribute(side, 2)); g.setIndex(idx);
    const mat = new THREE.ShaderMaterial({
      uniforms: { uA: { value: 0 }, uCol: { value: lin(col) }, uProj: U.uProj, uProjPos: U.uProjPos, uPlate: U.uPlate, uNow: U.uNow, uFlow: { value: flow }, uRef: { value: LREF }, uKmin: { value: LKMIN * 1.5 }, uKmax: { value: kmax } },
      vertexShader: `attribute float aArc; attribute vec2 aSide; uniform float uRef, uKmin, uKmax; varying vec3 vWP; varying float vArc;
        void main(){ vArc = aArc; vec3 c = (modelMatrix * vec4(position, 1.)).xyz; float k = clamp(distance(cameraPosition, c) / uRef, uKmin, uKmax);
          vec3 p = position + vec3(aSide.x, 0., aSide.y) * k; vWP = (modelMatrix * vec4(p, 1.)).xyz; gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.); }`,
      fragmentShader: `uniform float uA, uProj, uNow, uFlow; uniform vec3 uCol, uProjPos; uniform vec2 uPlate; varying vec3 vWP; varying float vArc;
        void main(){ vec2 q = abs(vWP.xz) - (uPlate * .5 + .05); float thr = 1. - smoothstep(0., .03, max(q.x, q.y));
          float k = .6 + .4 * max(dot(vec3(0., 1., 0.), normalize(uProjPos - vWP)), 0.);
          float f = 1.;
          if (uFlow > 0.) { float ph = fract(vArc / .045 - uNow * uFlow); f = .25 + 1.4 * exp(-pow((ph - .5) * 6., 2.)); }   // pulses of light travelling along the line
          gl_FragColor = vec4(uCol * k * thr * max(uProj, uFlow > 0. ? .9 : 0.) * uA * f, 1.); }`,
      transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: true, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6,
    });
    g.computeBoundingSphere();
    const mesh = new THREE.Mesh(g, mat); mesh.position.y = .0025; mesh.renderOrder = 2; mesh.frustumCulled = false; scene.add(mesh);
    lineGroups[id] = mat.uniforms.uA;
    return mat.uniforms.uA;
  }

  const blank = new THREE.DataTexture(new Uint8Array([0, 0, 0, 0]), 1, 1); blank.needsUpdate = true;
  function setTex(k, t, srgb = false) { if (!t) { U[k].value = blank; return; } t.flipY = false; t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; t.anisotropy = 4; U[k].value = t; }
  function setBasins(t, map) { t.flipY = false; t.colorSpace = THREE.NoColorSpace; t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.needsUpdate = true;
    U.uBasin.value = t; U.uBasinLo.value = map.lo; U.uBasinHi.value = map.hi; U.uBasinK.value = map.k; U.uBasinBand.value = map.band ?? 4; }
  // open ground (compile ground map): the cities that have some, in film order; each frame the crops of those standing are bound
  let GROUNDS = [];
  function setGrounds(t, map, eraList) { t.flipY = false; t.colorSpace = THREE.NoColorSpace; t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.needsUpdate = true;
    U.uGround.value = t; U.uGroundBand.value = map.band ?? 4; GROUNDS = eraList.filter(e => e.ground); }
  function groundsNow() {   // after the cities' shapes and colours (eraShape, setLayers / the viewer's apply), before drawing
    let n = 0;
    for (const e of GROUNDS) if (eras[e.id]) eras[e.id].u.uGroundSelf.value = -1;
    for (const e of GROUNDS) {
      if (n >= GMAX || !eras[e.id] || !e.basins.some(b => b.ground && U.uBasinA.value[b.k] > 0)) continue;
      const u = eras[e.id].u, c0 = u.uEraCol0.value, c = u.uEraCol.value; U.uGroundM.value[n].set(e.ground.m[0], e.ground.m[1], e.ground.m[2], u.uEraA.value); U.uGroundA.value[n].set(...e.ground.a);
      U.uGroundC0.value[n].set(c0.r, c0.g, c0.b, u.uEraInk0.value); U.uGroundC.value[n].set(c.r, c.g, c.b, u.uEraInk.value); u.uGroundSelf.value = n; n++; }
    U.uGroundN.value = n; }
  function setHideCols(cols) { cols.forEach((c, i) => { if (i < 8) U.uHideCol.value[i].copy(lin(c)); }); }
  function setHide(t, t2, e, e2) { for (const [k, x] of [['uHide', t], ['uHide2', t2], ['uEdge', e], ['uEdge2', e2]]) { x.flipY = false; x.colorSpace = THREE.NoColorSpace; x.magFilter = x.minFilter = THREE.LinearFilter; x.generateMipmaps = false; U[k].value = x; } }
  // cities apart in time share a channel (compile: era channels). In a film that has them the four channel textures become
  // render targets holding what the files hold; a city taking a channel over is drawn into it from its own files (hide_<id>,
  // edge_<id>): one channel written, the other three kept (a constant blend colour masks them), all on the graphics card
  let chans = null;
  function shareChannels() {
    const copy = new THREE.ShaderMaterial({ uniforms: { uSrc: { value: null }, uOne: { value: 0 } }, depthTest: false, depthWrite: false,
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
      fragmentShader: 'uniform sampler2D uSrc; uniform float uOne; varying vec2 vUv; void main(){ vec4 c = texture2D(uSrc, vUv); gl_FragColor = uOne > .5 ? vec4(c.r) : c; }' });
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), copy), qs = new THREE.Scene(), qc = new THREE.Camera(); qs.add(quad);
    const exact = x => { x.flipY = false; x.colorSpace = THREE.NoColorSpace; x.magFilter = x.minFilter = THREE.NearestFilter; x.generateMipmaps = false; x.needsUpdate = true; return x; };
    const draw = (rt, src, k) => {   // k: the channel to write (0-3), or -1 for all four
      copy.uniforms.uSrc.value = exact(src); copy.uniforms.uOne.value = k < 0 ? 0 : 1;
      copy.blending = k < 0 ? THREE.NoBlending : THREE.CustomBlending;
      copy.blendSrc = THREE.ConstantColorFactor; copy.blendDst = THREE.OneMinusConstantColorFactor; copy.blendSrcAlpha = THREE.ConstantAlphaFactor; copy.blendDstAlpha = THREE.OneMinusConstantAlphaFactor;
      copy.blendColor.setRGB(k === 0 ? 1 : 0, k === 1 ? 1 : 0, k === 2 ? 1 : 0); copy.blendAlpha = k === 3 ? 1 : 0;
      const was = renderer.getRenderTarget(), ac = renderer.autoClear; renderer.autoClear = false; renderer.setRenderTarget(rt); renderer.render(qs, qc); renderer.setRenderTarget(was); renderer.autoClear = ac; };   // (no clear: the other channels stay)
    const rts = {};
    for (const k of ['uHide', 'uHide2', 'uEdge', 'uEdge2']) {
      const src = U[k].value, rt = new THREE.WebGLRenderTarget(src.image.width, src.image.height, { depthBuffer: false, generateMipmaps: false, magFilter: THREE.LinearFilter, minFilter: THREE.LinearFilter });
      rt.texture.colorSpace = THREE.NoColorSpace; rt.texture.flipY = false; draw(rt, src, -1); rts[k] = rt; U[k].value = rt.texture;
    }
    chans = { put(h, hide, edge) { draw(rts[h < 4 ? 'uHide' : 'uHide2'], hide, h % 4); draw(rts[h < 4 ? 'uEdge' : 'uEdge2'], edge, h % 4); } };
    return chans;
  }
  function build(water, l1, l2, l3, decals = [], photo = null, terrain = null) {
    water.flipY = false; water.colorSpace = THREE.NoColorSpace; water.anisotropy = 8; U.uWater.value = water;
    for (const [k, t] of [['uL1', l1], ['uL2', l2], ['uL3', l3]]) { t.flipY = false; t.colorSpace = THREE.NoColorSpace; t.anisotropy = 4; U[k].value = t; }
    for (let i = 0; i < 4; i++) setTex('uD' + i, decals[i] || null, true);
    setTex('uPhoto', photo, true);
    if (terrain) setTerrain(terrain.img, terrain.info, M.scale);
    const white = '#f3f3f1', plateCol = PAL.plate || white;   // the model stays white; only the plate takes the palette's colour
    const city = new THREE.Mesh(buildCity(), projMaterial(0, { color: white, roughness: .88, metalness: 0 }));
    city.customDepthMaterial = deformMaterial(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }));
    city.castShadow = city.receiveShadow = true; scene.add(city);
    const RIM = .05, PT = .022;
    const plateTop = new THREE.Mesh(plateGeometry(), projMaterial(1, { color: plateCol, roughness: .9 }, { uPlateTop: { value: 1 } }));
    plateTop.customDepthMaterial = deformMaterial(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), { uPlateTop: { value: 1 } });   // (its shadow lowered in a pool too)
    plateTop.receiveShadow = true; plateTop.castShadow = !!HF; scene.add(plateTop);
    const plateBox = new THREE.Mesh(zero(new THREE.BoxGeometry(PW + RIM * 2, PT, PD + RIM * 2)), projMaterial(1, { color: PAL.plateSide || '#e9e6e0', roughness: .9 }));
    plateBox.position.y = -PT / 2 - .0005; plateBox.receiveShadow = true; scene.add(plateBox);
    const plinth = new THREE.Mesh(zero(new THREE.BoxGeometry(PW + .34, .9, PD + .34)), projMaterial(2, { color: '#17181a', roughness: .5 }));
    plinth.position.y = -PT - .45; plinth.receiveShadow = true; scene.add(plinth);
    return city;
  }

  // ---------------------------------------------------------------- lights (index 0 house, index 1 sun kept for the shader's light loop)
  const house = new THREE.DirectionalLight('#ffffff', 2);
  house.castShadow = true;   // (placed by followShadow)
  const SH = DIAG * .55;
  Object.assign(house.shadow.camera, { left: -SH, right: SH, top: SH, bottom: -SH, near: .5, far: 4 * DIAG });
  house.shadow.mapSize.set(4096, 4096); house.shadow.radius = 5; house.shadow.bias = -.0002; house.shadow.normalBias = .0015;
  house.shadow.camera.updateProjectionMatrix();
  scene.add(house, house.target);
  const hemi = new THREE.HemisphereLight('#dfe7f2', '#141414', .3); scene.add(hemi);
  // a cool rim from behind the city (placed by followShadow): edges of buildings and props catch it while the projector runs
  const rim = new THREE.DirectionalLight('#9fc3ff', 0); scene.add(rim, rim.target);
  // dust in the projector beam: a slow cloud of soft points above the plate, warm, brighter in the beam; embers during a burn
  const NP = 2600, pp = new Float32Array(NP * 3), ps = new Float32Array(NP);
  { let sd = 3; const rnd = () => { sd = (sd * 16807) % 2147483647; return sd / 2147483647; };
    for (let i = 0; i < NP; i++) { pp[i * 3] = (rnd() - .5) * PW * 1.1; pp[i * 3 + 1] = rnd() * .55 * DIAG * .5; pp[i * 3 + 2] = (rnd() - .5) * PD * 1.1; ps[i] = rnd(); } }
  const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(pp, 3)); pg.setAttribute('aSeed', new THREE.Float32BufferAttribute(ps, 1));
  const pm2 = new THREE.ShaderMaterial({
    uniforms: { uT: { value: 0 }, uA: { value: 0 }, uEmber: { value: 0 }, uProjPos: U.uProjPos, uH: { value: .55 * DIAG * .5 } },
    vertexShader: `attribute float aSeed; uniform float uT, uEmber, uH; varying float vA; varying float vS;
      void main(){ vec3 p = position; float sp = .004 + aSeed * .006;
        p.y = mod(p.y + uT * sp * (1. + 6. * uEmber) + aSeed * uH, uH); p.x += sin(uT * .13 + aSeed * 40.) * .01; p.z += cos(uT * .11 + aSeed * 30.) * .01;
        vec4 mv = modelViewMatrix * vec4(p, 1.); gl_Position = projectionMatrix * mv;
        float beam = 1. - smoothstep(0., uH, p.y);                        // denser near the plate, where the beam is wide
        vA = beam * (.35 + .65 * aSeed); vS = aSeed;
        float sz = (1.2 + 1.8 * aSeed * (1. + uEmber)) * 220. / max(.05, -mv.z);
        gl_PointSize = mv.z > -.06 ? 0. : clamp(sz, 0., 9.); }`,
    fragmentShader: `uniform float uA, uEmber; varying float vA; varying float vS;
      void main(){ float d = length(gl_PointCoord - .5); float k = smoothstep(.5, .1, d);
        vec3 col = mix(vec3(1., .96, .88), vec3(1., .45, .12), uEmber * (.5 + .5 * vS));
        gl_FragColor = vec4(col * k * vA * uA * (1. + 2. * uEmber), 1.); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const dust = new THREE.Points(pg, pm2); dust.frustumCulled = false; scene.add(dust);
  function setBeam(proj, ember, t) { pm2.uniforms.uT.value = t; pm2.uniforms.uA.value = proj * .22 * (1 - .7 * ember); pm2.uniforms.uEmber.value = 0; rim.intensity = .7 * proj; }
  // fire over a burning period city: sparks rising from its buildings (seeded round their centres) as fine streaks of light,
  // drawn at their real size (about 40 m long: a few pixels from 10 km, never a fat dot up close), a quarter of them embers
  // that live longer and drift high; each cools from yellow to red and fades; buildings already taken back by the contracting
  // ring (outside it) stop sending them
  const fires = {};
  function addFire(id, centres, ground) {
    const N = Math.min(24000, centres.length * 4), pos = new Float32Array(N * 3), seed = new Float32Array(N);
    let sd = 11; const rnd = () => { sd = (sd * 16807) % 2147483647; return sd / 2147483647; };
    for (let i = 0; i < N; i++) { const c = centres[Math.floor(rnd() * centres.length)]; pos[i * 3] = c[0]; pos[i * 3 + 1] = ground(c[0], c[1]); pos[i * 3 + 2] = c[1]; seed[i] = rnd(); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
    const u = { uT: { value: 0 }, uA: { value: 0 }, uH: { value: .009 }, uR: { value: 1e3 }, uO: { value: new THREE.Vector2() }, uPxH: { value: H * .5 } };
    const mat = new THREE.ShaderMaterial({ uniforms: u, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: `attribute float aSeed; uniform float uT, uH, uR, uPxH; uniform vec2 uO; varying float vK, vA, vE, vL;
        void main(){ float em = step(fract(aSeed * 13.7), .25);   // an ember: longer, higher, drifting
          float life = mix(1.5, 3.4, em) * (.8 + .4 * fract(aSeed * 7.1)), ph = fract(uT / life + aSeed * 7.31), k = ph;   // 0 born .. 1 gone
          vec3 p = position; float sw = aSeed * 40.;
          p.xz += (vec2(fract(aSeed * 91.3), fract(aSeed * 57.7)) - .5) * uH * 2.2;   // from anywhere on the burning building
          p.y += uH * mix(1., 3.2, em) * (k * 1.3 + .08 * sin(sw));
          p.x += uH * mix(.3, 1.4, em) * k * sin(uT * .9 + sw); p.z += uH * mix(.3, 1.4, em) * k * cos(uT * .7 + sw * 1.7);
          vK = k; vE = em; vA = length(position.xz - uO) < uR ? 1. : 0.;   // the contracting ring has passed: no more sparks there
          vec4 mv = modelViewMatrix * vec4(p, 1.); gl_Position = projectionMatrix * mv;
          float px = uPxH * projectionMatrix[1][1] / max(.02, -mv.z);   // pixels per model unit at this depth
          vL = clamp(.004 * px * (1. - .4 * k), 3., 11.);
          gl_PointSize = vA * vL; }`,
      fragmentShader: `uniform float uA; varying float vK, vA, vE, vL;
        void main(){ vec2 c = gl_PointCoord - .5;   // y down: the head at the top, the tail below
          float across = smoothstep(.75 / vL + .02, 0., abs(c.x)), along = clamp(.5 - c.y, 0., 1.);
          float head = exp(-dot(c - vec2(0., -.4), c - vec2(0., -.4)) * vL * vL * .5);
          vec3 col = mix(mix(vec3(1., .74, .38), vec3(.9, .24, .05), vK), vec3(1., .42, .1), vE * .5);
          float a = (across * along * 1.3 + head * .55) * (1. - vK) * uA * 2.2 * vA;
          if (a < .003) discard;
          gl_FragColor = vec4(col * a, 1.); }` });
    const pts = new THREE.Points(g, mat); pts.frustumCulled = false; pts.visible = false; pts.renderOrder = 7; scene.add(pts);
    fires[id] = { u, set(a, t, R, o) { u.uA.value = a; u.uT.value = t; u.uR.value = R; if (o) u.uO.value.set(o[0], o[1]); pts.visible = a > .002; } };
    return fires[id];
  }

  // a living moment's sky: the picture's sky and far land on a card far behind the shot, facing its camera (placed by main.js)
  const liveSky = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShaderMaterial({ uniforms: { uPI: U.uPI, uPM: U.uPM, uA: { value: 0 } }, depthWrite: false, transparent: true,
    vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: 'uniform sampler2D uPI; uniform mat4 uPM; uniform float uA; varying vec3 vW; void main(){ vec4 c = uPM * vec4(vW, 1.); vec2 u = c.xy / c.w * .5 + .5; if (u.x < 0. || u.x > 1. || u.y < 0. || u.y > 1.) discard; gl_FragColor = vec4(texture2D(uPI, u).rgb, uA); }' }));
  liveSky.visible = false; liveSky.renderOrder = -1; liveSky.frustumCulled = false; scene.add(liveSky);
  return { renderer, scene, camera, post, U, liveSky, addContext, setContext, setHide, setHideCols, shareChannels, setBasins, setGrounds, groundsNow, addRoute, routes, build, setRenew, addLines, lineGroups, addEdge, setGrowT, edges, addFire, fires, addProp, props, addEra, eras, followShadow, tally, setBeam, ground: (x, z) => ground(x, z), house, hemi, rim, DIAG, PW, PD };
}
