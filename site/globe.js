// The entry page's exhibit: the earth as a white massing model, the way the films build a city (site/land.bin, tools/portal_land.py).
// It stands on a pedestal in a brass meridian ring, its axis tilted as the earth's is, under a warm projector from the upper left.
// The land is tens of thousands of plaster blocks, raised where the ground is high and where many people live; on the side the
// projector does not reach, the crowded places glow like a city at night. A city with a film is a column of light, ringed at its
// foot by the colours of its chapters. Drag to turn it (on a phone: sideways; up and down still scrolls the page); left alone it
// turns slowly; choosing a city brings it round. It stops drawing when it is off screen or the tab is hidden.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';

const R = 1, TILT = THREE.MathUtils.degToRad(23.44);
const LAMP_DIR = new THREE.Vector3(-4.4, 2.4, 1.5).normalize();   // where the projector stands (world): from the left, so the night side shows
const FIT = 1.16, TAN = Math.tan(THREE.MathUtils.degToRad(12));      // the ring's reach around the globe; half the camera's 24 degree view
const ll = (lat, lon) => {   // lon 0 faces the camera (+z)
  const a = THREE.MathUtils.degToRad(lat), b = THREE.MathUtils.degToRad(lon);
  return new THREE.Vector3(Math.cos(a) * Math.sin(b), Math.sin(a), Math.cos(a) * Math.cos(b));
};
const hash = n => { const x = Math.sin(n * 127.1 + 31.7) * 43758.5453; return x - Math.floor(x); };

function gradientTexture(stops, size = 512) {   // a radial gradient, for the wall, the pool of light and the glows
  const c = document.createElement('canvas'); c.width = c.height = size; const g = c.getContext('2d');
  const r = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  for (const [o, col] of stops) r.addColorStop(o, col);
  g.fillStyle = r; g.fillRect(0, 0, size, size);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export async function makeGlobe(canvas, cities, { onPick, onHover, onFrame, reduced, small }) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: small, powerPreference: 'high-performance' });   // (throws without WebGL)
  renderer.setPixelRatio(Math.min(devicePixelRatio, small ? 1.75 : 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  const buf = await fetch(new URL('land.bin', import.meta.url)).then(r => r.arrayBuffer());
  const total = new DataView(buf).getUint32(0, true), count = small ? Math.min(total, 26000) : total;   // (the file is shuffled: any first part is an even sample)
  const pts = new DataView(buf, 4);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0c1118);
  const camera = new THREE.PerspectiveCamera(24, 1, .1, 60);

  // the wall behind: a soft halo where the projector's spill lands
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(26, 26), new THREE.MeshBasicMaterial({
    map: gradientTexture([[0, '#1e2734'], [.35, '#141b25'], [1, '#0c1118']]), depthWrite: false }));
  wall.position.set(.4, .3, -9); scene.add(wall);

  // the stand: a pedestal with a brass lip and the projector's pool of light, a stem, the meridian ring with the axis pins
  const brass = new THREE.MeshStandardMaterial({ color: 0x9a7d52, metalness: .92, roughness: .32 });
  const graphite = new THREE.MeshStandardMaterial({ color: 0x1b2028, metalness: .25, roughness: .55 });
  const ped = new THREE.Mesh(new THREE.CylinderGeometry(.5, .57, .1, 128), graphite); ped.position.y = -1.47; scene.add(ped);
  const lip = new THREE.Mesh(new THREE.TorusGeometry(.5, .006, 8, 160), brass); lip.rotation.x = Math.PI / 2; lip.position.y = -1.42; scene.add(lip);
  const pool = new THREE.Mesh(new THREE.CircleGeometry(.495, 96), new THREE.MeshBasicMaterial({
    map: gradientTexture([[0, 'rgba(255,226,180,.42)'], [.6, 'rgba(255,226,180,.08)'], [1, 'rgba(255,226,180,0)']]), transparent: true, depthWrite: false }));
  pool.rotation.x = -Math.PI / 2; pool.position.y = -1.418; scene.add(pool);
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(.016, .022, .3, 24), brass); stem.position.y = -1.27; scene.add(stem);
  const cradle = new THREE.Mesh(new THREE.CylinderGeometry(.011, .011, .12, 16), brass); cradle.position.y = -1.155; scene.add(cradle);
  const axis = new THREE.Group(); axis.rotation.z = -TILT; scene.add(axis);   // everything that leans with the earth's axis
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.1, .0075, 12, 240), brass); ring.rotation.y = Math.PI / 2; axis.add(ring);
  for (const s of [1, -1]) { const pin = new THREE.Mesh(new THREE.CylinderGeometry(.012, .012, .06, 16), brass); pin.position.y = s * 1.07; axis.add(pin); }

  // the earth: it spins inside the leaning axis
  const earth = new THREE.Group(); axis.add(earth);
  earth.add(new THREE.Mesh(new THREE.SphereGeometry(R, 160, 120), new THREE.MeshStandardMaterial({ color: 0x18202b, metalness: .05, roughness: .5 })));
  {   // the graticule: every 15 degrees, engraved faintly into the sea
    const v = [], step = 15, seg = 180, at = (a, b) => ll(a, b).multiplyScalar(R * 1.0015).toArray();
    for (let la = -75; la <= 75; la += step) for (let i = 0; i < seg; i++) v.push(...at(la, i / seg * 360), ...at(la, (i + 1) / seg * 360));
    for (let lo = 0; lo < 360; lo += step) for (let i = 0; i < seg; i++) v.push(...at(-90 + i / seg * 180, lo), ...at(-90 + (i + 1) / seg * 180, lo));
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
    earth.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xc9d3e0, transparent: true, opacity: .085, depthWrite: false })));
  }

  // the land: plaster blocks, darker toward their feet (the shadow between them), the crowded ones lit on the night side
  const box = new THREE.BoxGeometry(1, 1, 1); box.translate(0, 0, .5);
  const plaster = new THREE.MeshStandardMaterial({ color: 0xf3f1ec, roughness: .78, metalness: 0 });
  const uLamp = { value: LAMP_DIR.clone() };
  plaster.onBeforeCompile = sh => {
    sh.uniforms.uLamp = uLamp;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float aGlow; varying float vGlow; varying float vZ; varying float vNight;\nuniform vec3 uLamp;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        vZ = position.z; vGlow = aGlow;
        vec3 up = normalize((modelMatrix * instanceMatrix * vec4(0., 0., 1., 0.)).xyz);
        vNight = smoothstep(.12, -.42, dot(up, uLamp));`);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vGlow; varying float vZ; varying float vNight;')
      .replace('#include <color_fragment>', '#include <color_fragment>\n diffuseColor.rgb *= mix(.42, 1., smoothstep(0., .85, vZ));')
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        totalEmissiveRadiance += vec3(1., .62, .28) * vGlow * (.12 + .88 * vNight) * (.4 + .6 * smoothstep(.55, 1., vZ)) * 3.6;`);
  };
  const blocks = new THREE.InstancedMesh(box, plaster, count);
  const glow = new Float32Array(count);
  {
    const m = new THREE.Matrix4(), up = new THREE.Vector3(0, 1, 0), e = new THREE.Vector3(), n2 = new THREE.Vector3(), w = .0062 * (small ? 1.5 : 1);
    for (let i = 0; i < count; i++) {
      const o = i * 6, lat = pts.getInt16(o, true) / 100, lon = pts.getInt16(o + 2, true) / 100, g = pts.getUint8(o + 4) / 255, p = pts.getUint8(o + 5) / 255;
      const n = ll(lat, lon); e.crossVectors(up, n).normalize(); n2.crossVectors(n, e);
      const h = .0018 + .0012 * hash(i) + .05 * g * g + .085 * p ** 4.5, s = w * (.84 + .16 * hash(i + 3));
      m.makeBasis(e.clone().multiplyScalar(s), n2.clone().multiplyScalar(s), n.clone().multiplyScalar(h)).setPosition(n.multiplyScalar(R * .999));
      blocks.setMatrixAt(i, m);
      glow[i] = p > .5 ? ((p - .5) / .5) ** 1.8 : 0;
    }
  }
  box.setAttribute('aGlow', new THREE.InstancedBufferAttribute(glow, 1));
  earth.add(blocks);

  // the air: a faint rim where the globe meets the dark
  axis.add(new THREE.Mesh(new THREE.SphereGeometry(R * 1.045, 96, 64), new THREE.ShaderMaterial({
    side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { c: { value: new THREE.Color(0x8fa6c8) } },
    vertexShader: 'varying vec3 vN; varying vec3 vV; void main(){ vec4 p = modelViewMatrix * vec4(position, 1.); vN = normalize(normalMatrix * normal); vV = normalize(-p.xyz); gl_Position = projectionMatrix * p; }',
    fragmentShader: 'uniform vec3 c; varying vec3 vN; varying vec3 vV; void main(){ float f = pow(1. - abs(dot(vN, vV)), 3.2); gl_FragColor = vec4(c * f * .55, f); }',
  })));

  // light: a low fill, a cool rim from behind, the warm projector (which strikes when the page opens)
  scene.add(new THREE.HemisphereLight(0x8a9bb5, 0x0b0f16, .32));
  const rim = new THREE.DirectionalLight(0x86a2d0, 1.25); rim.position.set(3.2, 1.4, -4); scene.add(rim);
  const lamp = new THREE.DirectionalLight(0xffe7c6, 0); lamp.position.copy(LAMP_DIR).multiplyScalar(10); scene.add(lamp);
  const LAMP = 3.4;

  // the cities: a column of light fading upward, a bright foot, rings in the colours of its chapters, a ripple now and then
  const beamMat = (col, hdrK = 1.6) => new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { c: { value: new THREE.Color(col) }, a: { value: 1 }, hdr: { value: hdrK } },
    vertexShader: 'varying float vY; void main(){ vY = uv.y; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }',
    fragmentShader: 'uniform vec3 c; uniform float a; uniform float hdr; varying float vY; void main(){ float k = pow(1. - vY, 1.6) * a; gl_FragColor = vec4(c * k * hdr, k); }' });
  const dot = gradientTexture([[0, 'rgba(255,255,255,1)'], [.18, 'rgba(255,240,215,.85)'], [.5, 'rgba(255,220,170,.18)'], [1, 'rgba(255,220,170,0)']], 128);
  const marks = [];
  for (const c of cities) {
    if (!c.location) continue;
    const n = ll(c.location[1], c.location[0]);
    const all = [...new Set((c.chapters || []).map(x => x.color))];
    const cols = all.length > 6 ? [0, 1, 2, 3, 4, 5].map(i => all[Math.round(i * (all.length - 1) / 5)]) : all;   // (up to six, the first era innermost)
    const g = new THREE.Group(); g.position.copy(n.clone().multiplyScalar(R * 1.001)); g.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), n);
    const H = .5;   // (a cylinder's uv.y runs from its foot to its top: the beam fades upward)
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, H, 32, 1, true).rotateX(Math.PI / 2).translate(0, 0, H / 2), beamMat(cols[cols.length - 1] || '#ffd27a'));
    const core = new THREE.Mesh(new THREE.CylinderGeometry(.0045, .0045, H, 12, 1, true).rotateX(Math.PI / 2).translate(0, 0, H / 2), beamMat('#fff3dc', 2.4));
    const foot = new THREE.Sprite(new THREE.SpriteMaterial({ map: dot, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    foot.scale.setScalar(.11); foot.position.z = .008;
    const rings = cols.map((k, i) => {
      const r = new THREE.Mesh(new THREE.RingGeometry(.035 + i * .019, .0445 + i * .019, 96),
        new THREE.MeshBasicMaterial({ color: k, transparent: true, opacity: .95, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
      r.position.z = .004 + i * .0004; return r;
    });
    const ripple = new THREE.Mesh(new THREE.RingGeometry(.03, .034, 96), new THREE.MeshBasicMaterial({ color: '#ffe7c6', transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
    ripple.position.z = .006;
    const hit = new THREE.Mesh(new THREE.SphereGeometry(.09, 8, 6), new THREE.MeshBasicMaterial({ visible: false })); hit.position.z = .1;
    g.add(beam, core, foot, ripple, hit, ...rings); earth.add(g);
    marks.push({ c, g, beam, core, foot, rings, ripple, hit, H });
  }

  // drawing: bloom for the lights, where the machine can afford it
  let composer = null;
  if (!small) {
    // (half-float targets, so the lights bloom without banding; edges smoothed by SMAA: half-float targets with samples drew black on some GPUs)
    composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    composer.addPass(new UnrealBloomPass(new THREE.Vector2(1, 1), .55, .5, .78));
    composer.addPass(new OutputPass());
    composer.addPass(new SMAAPass(1, 1));
  }

  // turning: drag to spin (and, with a mouse, tip the view a little), inertia, a slow turn when idle; choosing a city eases it round
  let yaw = -THREE.MathUtils.degToRad((cities[0] && cities[0].location ? cities[0].location[0] : 100) + 24), elev = .1, vy = 0;
  let goal = null, drag = null, idle = 0, hover = null, held = false;
  let room = null, panelW = 0, off = 0, dist = 8.3;   // wide screens: the free space right of the words (px), the open panel's width
  const el = renderer.domElement;
  el.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, moved: 0, id: e.pointerId, type: e.pointerType }; goal = null; });
  addEventListener('pointermove', e => {
    if (drag && e.pointerId === drag.id) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY; drag.moved += Math.abs(dx) + Math.abs(dy);
      vy = dx * .0042; yaw += vy; if (drag.type !== 'touch') elev = THREE.MathUtils.clamp(elev + dy * .0022, -.32, .42); idle = 0;
    } else if (e.target === el) pointAt(e);
  });
  addEventListener('pointerup', e => {
    if (!drag || e.pointerId !== drag.id) return;
    const tap = drag.moved < 8; drag = null;
    if (tap && e.target === el) { pointAt(e); if (hover) onPick(hover.c.slug); }
  });
  addEventListener('pointercancel', () => { drag = null; });   // (a vertical swipe on a phone becomes a scroll)
  el.addEventListener('pointerleave', () => { if (!drag) setHover(null); });
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  function pointAt(e) {
    const r = el.getBoundingClientRect(); ndc.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObjects(marks.map(k => k.hit));
    setHover(hits.length ? marks.find(k => k.hit === hits[0].object) : null);
  }
  function setHover(k) { if (k === hover) return; hover = k; el.style.cursor = k ? 'pointer' : ''; onHover(k ? k.c.slug : null); }

  // where each city's label goes (the top of its column) and how squarely it faces us
  const a = new THREE.Vector3(), b = new THREE.Vector3();
  function places() {
    const out = [];
    for (const k of marks) {
      k.g.localToWorld(a.set(0, 0, k.H * .9)); a.project(camera);
      k.g.localToWorld(b.set(0, 0, 0)); const facing = b.sub(camera.position).normalize().dot(k.g.getWorldDirection(new THREE.Vector3())) * -1;
      out.push({ slug: k.c.slug, x: (a.x + 1) / 2 * W, y: (1 - a.y) / 2 * Hh, facing });
    }
    return out;
  }

  let W = 1, Hh = 1, wide = true;
  function resize() {
    const w = el.clientWidth, h = el.clientHeight; if (!w || !h) return; W = w; Hh = h;
    renderer.setSize(w, h, false); if (composer) composer.setSize(w, h);
    camera.aspect = w / h; wide = w / h > 1.1; place();
  }
  // the camera. Wide screens: the globe fills the space right of the words (or, with a city open, left of the panel), never under
  // either; it is sized to that space and to the height. Narrow screens: centred, far enough back that the ring fits the width.
  function aim() {
    if (!wide) return { d: Math.max(7.9, 1.52 * FIT / ((W / Hh) * TAN)), off: 0 };
    const [a, b] = held && panelW ? [0, W - panelW] : [room == null ? W * .42 : room, W - Math.min(64, W * .04)];
    const r = Math.max(120, Math.min(Hh * .34, (b - a) * .47));   // the globe's radius on screen (px)
    return { d: (Hh / 2) / (r * TAN) * FIT * .92, off: W / 2 - (a + b) / 2 };
  }
  function place(dt) {
    const g = aim(), k = dt == null ? 1 : 1 - Math.exp(-dt * 5);
    dist += (g.d - dist) * k; off += (g.off - off) * k;
    camera.position.set(0, Math.sin(elev) * dist, Math.cos(elev) * dist); camera.lookAt(0, wide ? -.16 : -.24, 0);
    if (wide) camera.setViewOffset(W, Hh, off, 0, W, Hh); else camera.clearViewOffset();
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(el); resize();

  // only draw while it can be seen
  let visible = true;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; }).observe(el);

  const t0 = performance.now(); let last = t0;
  function frame(now) {
    requestAnimationFrame(frame);
    if (!visible || document.hidden) { last = now; return; }
    const dt = Math.min(.05, (now - last) / 1000), t = (now - t0) / 1000; last = now;
    // the lamp strikes, as the films open: a flicker, a pause, then the light rises
    const strike = reduced ? 1 : t < .5 ? 0 : t < .6 ? .5 : t < .72 ? .08 : Math.min(1, ((t - .72) / 1.6) ** .8);
    lamp.intensity = LAMP * strike; pool.material.opacity = strike;
    for (const [i, k] of marks.entries()) {
      const s = reduced ? 1 : THREE.MathUtils.clamp((t - 2 - i * .2) / 1.1, 0, 1), e = 1 - (1 - s) ** 3;
      k.beam.scale.z = k.core.scale.z = Math.max(.001, e); k.beam.material.uniforms.a.value = .85 * e; k.core.material.uniforms.a.value = e;
      k.foot.material.opacity = e; k.rings.forEach((r, j) => { r.material.opacity = e * (.62 + .35 * Math.sin(t * 1.2 - j * .55) ** 2); });
      const p = reduced ? -1 : ((t - 2.6 - i * .4) % 3.2) / 3.2;
      if (p >= 0) { k.ripple.scale.setScalar(1 + p * 4.2); k.ripple.material.opacity = (1 - p) ** 2 * .7 * e; } else k.ripple.material.opacity = 0;
    }
    if (goal) {
      const q = 1 - Math.exp(-dt * 3.4); yaw += (goal.yaw - yaw) * q; elev += (goal.elev - elev) * q;
      if (Math.abs(goal.yaw - yaw) < 1e-3 && Math.abs(goal.elev - elev) < 1e-3) goal = null;
    } else if (!drag) {
      vy *= .93; yaw += vy; idle += dt;
      if (!reduced && idle > 2.4 && !held) yaw += dt * .045;
    }
    earth.rotation.y = yaw; place(dt);
    if (composer) composer.render(); else renderer.render(scene, camera);
    if (onFrame) onFrame(places(), t);
  }
  requestAnimationFrame(frame);

  return {
    focus(slug) {   // bring a city round to the front, the view tipped toward its latitude
      const k = marks.find(x => x.c.slug === slug); if (!k) return;
      let y = -THREE.MathUtils.degToRad(k.c.location[0]);
      y += Math.round((yaw - y) / (2 * Math.PI)) * 2 * Math.PI;   // the short way round
      const la = THREE.MathUtils.degToRad(k.c.location[1]);
      goal = { yaw: y, elev: THREE.MathUtils.clamp(Math.atan2(Math.cos(TILT) * Math.sin(la), Math.cos(la)) * .55, -.3, .42) }; idle = 0; vy = 0;
    },
    hold(on, width = 0) { held = on; panelW = width; },   // an open city: no idle turning; on wide screens the globe moves left of its panel
    setRoom(left) { room = left; },                         // where the words end (px from the left), so the globe stays clear of them
    blocks: count,
  };
}
