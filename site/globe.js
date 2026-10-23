// The entry page's earth: the land as a white massing model on a dark plinth, lit by a projector, the way the films build a city
// (site/land.json, tools/portal_land.py). A city with a film stands up as a lit column, ringed at its foot by the colours of its
// chapters. Drag to turn it; it turns slowly on its own when left alone; choosing a city brings it round to the front.
import * as THREE from 'three';

const R = 1;                                  // the globe
const ll = (lat, lon) => {                    // lon 0 faces the camera (+z)
  const a = THREE.MathUtils.degToRad(lat), b = THREE.MathUtils.degToRad(lon);
  return new THREE.Vector3(Math.cos(a) * Math.sin(b), Math.sin(a), Math.cos(a) * Math.cos(b));
};
const hash = n => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };

export async function makeGlobe(canvas, cities, { onPick, onHover, reduced }) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });   // (throws without WebGL: the page lists the cities)
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const land = await fetch('site/land.json').then(r => r.json());
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(28, 1, .1, 50);
  const tilt = new THREE.Group(), world = new THREE.Group(); tilt.add(world); scene.add(tilt);

  // the sea: a dark core under the blocks
  world.add(new THREE.Mesh(new THREE.SphereGeometry(R * .985, 96, 64), new THREE.MeshStandardMaterial({ color: 0x1e2731, roughness: .9, metalness: 0 })));

  // the land: one block per lattice point, standing on the sphere, north up; taller where many people live
  const box = new THREE.BoxGeometry(1, 1, 1); box.translate(0, 0, .5);
  const plaster = new THREE.MeshStandardMaterial({ color: 0xf4f2ee, roughness: .8, metalness: 0 });
  const blocks = new THREE.InstancedMesh(box, plaster, land.points.length);
  const m = new THREE.Matrix4(), up = new THREE.Vector3(0, 1, 0);
  land.points.forEach(([lat, lon, h], i) => {
    const n = ll(lat, lon), e = new THREE.Vector3().crossVectors(up, n).normalize(), north = new THREE.Vector3().crossVectors(n, e);
    const w = .0118 * (.86 + .14 * hash(i)), hh = .004 + .003 * hash(i + 7) + .085 * h * h;
    m.makeBasis(e.multiplyScalar(w), north.multiplyScalar(w), n.clone().multiplyScalar(hh)).setPosition(n.multiplyScalar(R * .985));
    blocks.setMatrixAt(i, m);
  });
  world.add(blocks);

  // the plinth below, with the projector's pool of light on its top
  const plinth = new THREE.Mesh(new THREE.CylinderGeometry(.92, .98, .16, 96), new THREE.MeshStandardMaterial({ color: 0x262c33, roughness: .95 }));
  plinth.position.y = -1.36; scene.add(plinth);
  const pool = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
    const r = g.createRadialGradient(128, 128, 0, 128, 128, 128); r.addColorStop(0, 'rgba(255,233,196,.55)'); r.addColorStop(1, 'rgba(255,233,196,0)');
    g.fillStyle = r; g.fillRect(0, 0, 256, 256);
    const s = new THREE.Mesh(new THREE.CircleGeometry(.9, 64), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
    s.rotation.x = -Math.PI / 2; s.position.y = -1.278; return s;
  })();
  scene.add(pool);

  // the light: a low fill, a cool rim from behind, and the projector, which strikes when the page opens
  scene.add(new THREE.HemisphereLight(0x8494a8, 0x0b0f18, .5));
  const rim = new THREE.DirectionalLight(0x7f9cc4, 1.1); rim.position.set(2.5, 1.2, -4); scene.add(rim);
  const lamp = new THREE.DirectionalLight(0xfff1dc, 0); lamp.position.set(-3.2, 3.0, 4.2); scene.add(lamp);
  const LAMP = 3.2;

  // the cities: a lit column and its chapters' rings
  const glow = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.25, 'rgba(255,255,255,.5)'); r.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = r; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c);
  })();
  const marks = [];
  for (const c of cities) {
    if (!c.location) continue;
    const n = ll(c.location[1], c.location[0]);
    const all = [...new Set((c.chapters || []).map(x => x.color))], cols = all.length > 6 ? [0, 1, 2, 3, 4, 5].map(i => all[Math.round(i * (all.length - 1) / 5)]) : all;   // (up to six, the first era innermost)
    const g = new THREE.Group(); g.position.copy(n.clone().multiplyScalar(R * .99)); g.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), n);
    const top = cols[cols.length - 1] || '#ffd27a';
    const col = new THREE.Mesh(new THREE.CylinderGeometry(.008, .008, .34, 12).rotateX(Math.PI / 2).translate(0, 0, .17),
      new THREE.MeshBasicMaterial({ color: '#fff4dc' }));   // (the lit core; its glow in the latest era's colour)
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, .34, 24, 1, true).rotateX(Math.PI / 2).translate(0, 0, .17),
      new THREE.MeshBasicMaterial({ color: top, transparent: true, opacity: .32, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
    const cap = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, color: '#ffe9c4', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    cap.position.z = .34; cap.scale.setScalar(.075);
    const rings = cols.map((k, i) => {
      const r = new THREE.Mesh(new THREE.RingGeometry(.032 + i * .019, .044 + i * .019, 72),
        new THREE.MeshBasicMaterial({ color: k, transparent: true, opacity: .85, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
      r.position.z = .004 + i * .0005; return r;
    });
    const hit = new THREE.Mesh(new THREE.SphereGeometry(.07, 8, 6), new THREE.MeshBasicMaterial({ visible: false })); hit.position.z = .12;
    g.add(col, beam, cap, hit, ...rings); g.scale.setScalar(reduced ? 1 : .001); world.add(g);
    marks.push({ c, g, n, rings, hit });
  }

  // turning: drag, inertia, a slow turn when idle; choosing a city eases it to the front
  // (it opens with the first city a little to the west of the front, turning towards it the way the earth turns)
  let yaw = -THREE.MathUtils.degToRad((cities[0] && cities[0].location ? cities[0].location[0] : 100) + 22), pitch = .06, vy = 0;
  let goal = null, drag = null, idle = 0, hover = null, paused = false;
  const el = renderer.domElement;
  el.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, moved: 0 }; el.setPointerCapture(e.pointerId); goal = null; });
  el.addEventListener('pointermove', e => {
    if (drag) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY; drag.moved += Math.abs(dx) + Math.abs(dy);
      vy = dx * .0045; yaw += vy; pitch = THREE.MathUtils.clamp(pitch + dy * .0035, -.7, .9); idle = 0;
    } else pointAt(e);
  });
  el.addEventListener('pointerup', e => { const tap = drag && drag.moved < 6; drag = null; if (tap) { pointAt(e); if (hover) onPick(hover.c.slug); } });
  el.addEventListener('pointerleave', () => { if (!drag) setHover(null); });
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  function pointAt(e) {
    const r = el.getBoundingClientRect(); ndc.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObjects(marks.map(k => k.hit));
    setHover(hits.length ? marks.find(k => k.hit === hits[0].object) : null);
  }
  function setHover(k) {
    if (k === hover) return; hover = k; el.style.cursor = k ? 'pointer' : 'grab';
    onHover(k ? k.c.slug : null);
  }
  const screenOf = slug => {   // where a city stands on the canvas (for its name tag)
    const k = marks.find(x => x.c.slug === slug); if (!k) return null;
    const p = k.g.localToWorld(new THREE.Vector3(0, 0, .36)).project(camera), front = k.g.localToWorld(new THREE.Vector3()).normalize().dot(camera.position.clone().normalize()) > .15;
    const r = el.getBoundingClientRect(); return { x: (p.x + 1) / 2 * r.width, y: (1 - p.y) / 2 * r.height, front };
  };

  function resize() {
    const w = el.clientWidth, h = el.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h;
    const wide = w / h > 1.15, fit = wide ? 6.6 : 7.4 / Math.min(1, w / h) ** .6;   // (narrow screens: further away, so the whole globe shows)
    camera.position.set(0, .5, fit); camera.lookAt(0, -.2, 0);
    if (wide) camera.setViewOffset(w, h, (paused ? .06 : -.17) * w, 0, w, h); else camera.clearViewOffset();   // (wide screens: right of the words; left of an open city)
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(el); resize();

  const t0 = performance.now(); let last = t0;
  function frame(now) {
    const dt = Math.min(.05, (now - last) / 1000), t = (now - t0) / 1000; last = now;
    // the lamp strikes: a flicker, then the light rises (the films open the same way)
    const strike = reduced ? 1 : t < .35 ? 0 : t < .45 ? .55 : t < .55 ? .1 : Math.min(1, (t - .55) / 1.4);
    lamp.intensity = LAMP * strike; pool.material.opacity = strike;
    for (const [i, k] of marks.entries()) {
      const s = reduced ? 1 : THREE.MathUtils.clamp((t - 1.6 - i * .15) / .9, 0, 1);
      k.g.scale.setScalar(Math.max(.001, 1 - (1 - s) ** 3));
      k.rings.forEach((r, j) => { r.material.opacity = .6 + .4 * Math.sin(t * 1.4 - j * .6) ** 2; });
    }
    if (goal) {
      yaw += (goal.yaw - yaw) * Math.min(1, dt * 3.2); pitch += (goal.pitch - pitch) * Math.min(1, dt * 3.2);
      if (Math.abs(goal.yaw - yaw) < 1e-3 && Math.abs(goal.pitch - pitch) < 1e-3) goal = null;
    } else if (!drag) {
      vy *= .94; yaw += vy; idle += dt;
      if (!reduced && idle > 2.5 && !paused) yaw += dt * .05;
    }
    world.rotation.y = yaw; tilt.rotation.x = pitch;
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  return {
    focus(slug) {   // bring a city round to the front
      const k = marks.find(x => x.c.slug === slug); if (!k) return;
      let y = -THREE.MathUtils.degToRad(k.c.location[0]);
      y += Math.round((yaw - y) / (2 * Math.PI)) * 2 * Math.PI;   // the short way round
      goal = { yaw: y, pitch: THREE.MathUtils.degToRad(k.c.location[1]) * .9 - .45 }; idle = 0; vy = 0;   // (a little above the middle, so its column is seen rising)
    },
    hold(on) { paused = on; resize(); },   // no idle turning while a city is open, and the globe steps aside for it
    screenOf,
  };
}
