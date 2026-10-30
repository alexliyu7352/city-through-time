// A museum page's model (museum.html, site/museum.js; docs/MUSEUM.md): one landmark as a model of its own (tools/museum.py), in
// a bright neutral room, turned and zoomed freely, everything sharp. The film's white model and shaders (studio.js), not its
// lens: no depth of field, no vignette, no bloom, no tone mapping, so a viewpoint's picture, projected back onto the model from
// the camera it was made from (the living moments' projector: uPI, uPM, uPA, aimProjector), shows exactly as the picture.
// The picture is exact only from its own camera: it is full within FULL_DEG of it and gone by GONE_DEG (and as the distance
// leaves it), and comes back by itself near any viewpoint. Each part of the model is its own mesh: it can be picked, and
// tinted by whether it rests on sources or is estimated.
// startMuseum({ stage, base, meta, model, clean, vp, on }) -> the page's handle: { flyToNearest, tones, select, view }.
// clean (tools/museum.mjs, tools/living.py ref): the model alone at viewpoint vp in the reference look (dark room, grey stand),
// no picture: the still an image tool paints over.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { makeStudio } from './studio.js';
import { ss, seg, lerp, clamp, frameOf } from './lib.js';

const FULL_DEG = 10, GONE_DEG = 25;          // the picture by the angle from its camera
const FULL_D = .14, GONE_D = .45;            // and by the distance (|ln| of the ratio to its own: within 15 %, gone past about 50 %)
const EYE_M = 1.6, FLY_S = 1.4;              // the lowest the eye goes over the ground; a flight's seconds
const KEY_AZ = 95;                           // the key light: 50 degrees left of this bearing (studio followShadow), 45 up: from the south-east
const TONE = { sourced: '#e9c08a', estimated: '#8fa6c6' }, WHITE = '#f4f2ee', PICK = new THREE.Color('#ffb347');
const STAND = { look: '#efede8', clean: '#8c8c8c' };   // the stand: a light floor in the room; mid grey in the reference, so the model stands clear of it
const ROOM = { look: [['#eef0f1', 0], ['#e3e6e8', .55], ['#d2d6da', 1]], clean: [['#3a3f47', 0], ['#22262c', 1]] };   // the room behind: exhibition, reference

export async function startMuseum({ stage, base, meta, model, clean = false, vp: vp0 = null, on = {} }) {
  const W0 = Math.max(1, stage.clientWidth), H0 = Math.max(1, stage.clientHeight);
  const S = makeStudio(W0, H0, { size: model.size, scale: model.scale }, {}, { low: false });
  const { U, camera, post, renderer, scene, house, hemi } = S, SC = model.scale;
  renderer.toneMapping = THREE.NoToneMapping;   // (the picture shows as it is: its pixels in, its pixels out)
  post.bloom.enabled = false; post.vig.uniforms.amt.value = 0; post.dof.aper = 0; post.dof.maxCoc = 0; post.weather.enabled = false;
  camera.far = 2; camera.updateProjectionMatrix();   // (the sky card stands .3 behind a viewpoint)
  { // the room: a soft light wall (the reference look: a dark one, so the model's outline is clear to the image tool)
    const c = document.createElement('canvas'); c.width = 16; c.height = 256; const g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 256);
    for (const [col, k] of ROOM[clean ? 'clean' : 'look']) gr.addColorStop(k, col);
    g.fillStyle = gr; g.fillRect(0, 0, 16, 256);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; scene.background = t; scene.backgroundIntensity = 1;
  }
  // exhibition light: a key high up from the south-east, fixed in the room (shadows stay put as the visitor walks round), a light
  // sky and floor, the room's soft light; no projector (it is the film's light)
  house.intensity = 2.6; hemi.intensity = .5; hemi.color.set('#f3f4f6'); hemi.groundColor.set('#a39d93'); scene.environmentIntensity = .2;
  U.uProj.value = 0; U.uBase.value = 0; U.uToday.value = 1; U.uFootM.value = 2.5;
  U.uPRR.value = 1e3; U.uPF.value = 0; U.uPRC.value.set(0, 0);   // the picture over the whole model: no ring, no far land
  const edge = post.dof.coc.material.uniforms.edgeAmt;
  // the parts, each a mesh of its own (a period city's: risen at once, standing, in white light)
  const parts = [];
  for (const p of model.parts.concat([{ id: '_stand', prims: model.stand }])) {
    const E = S.addEra(p.id, p.prims, WHITE), u = E.u;
    u.uEraT.value = 1e6; u.uEraSpan.value = 1; u.uEraGrow.value = 1; u.uEraA.value = 0; u.uEraGlow.value = 0;
    u.uEraCol.value.set(1, 1, 1); u.uEraCol0.value.set(1, 1, 1); u.uEraInk.value = u.uEraInk0.value = 0;
    E.mesh.visible = true; E.mesh.castShadow = true;
    E.mesh.material.shadowSide = THREE.DoubleSide;   // (from its back faces alone, the default, the model cast no shadow on its stand)
    parts.push({ id: p.id, mesh: E.mesh, status: (meta.parts.find(q => q.id === p.id) || {}).status });
  }
  const pickable = parts.filter(p => p.id !== '_stand');
  // the viewpoints and their pictures (the main one is on screen already, as the page's first picture)
  const VP = meta.viewpoints.map(v => ({ ...v, tex: null, A: v.picture ? v.picture.w / v.picture.h : 16 / 9 }));
  const loader = new THREE.TextureLoader(); loader.setCrossOrigin('anonymous');
  const loads = clean ? [] : VP.filter(v => v.picture).map(v => loader.loadAsync(base + v.picture.file).then(t => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; v.tex = t; }));
  const main = VP.find(v => v.id === vp0) || VP.find(v => v.main) || VP[0];

  // the camera: a target and a place round it (az, el as the film's camera keys count them: 0 south of the target, 90 east)
  const controls = new OrbitControls(camera, renderer.domElement);
  Object.assign(controls, { enableDamping: !clean, dampingFactor: .12, screenSpacePanning: false, zoomToCursor: false, rotateSpeed: .55,
    minDistance: 12 * SC, maxDistance: 1100 * SC, maxPolarAngle: THREE.MathUtils.degToRad(98), enabled: !clean });
  const pose = () => { const v = camera.position.clone().sub(controls.target), d = v.length();
    return { t: controls.target.clone(), az: THREE.MathUtils.radToDeg(Math.atan2(v.x, v.z)), el: THREE.MathUtils.radToDeg(Math.asin(clamp(v.y / d, -1, 1))), d }; };
  const put = (t, az, el, d) => { const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el);
    controls.target.copy(t); camera.position.set(t.x + d * Math.sin(a) * Math.cos(e), t.y + d * Math.sin(e), t.z + d * Math.cos(a) * Math.cos(e)); camera.lookAt(t); };
  const camOf = v => ({ t: new THREE.Vector3(v.cam[0], v.cam[1], v.cam[2]), az: v.cam[3], el: v.cam[4], d: v.cam[5] });
  // the lens follows a viewpoint: its picture fills the stage as frameOf places it (the page shows the first picture the same way)
  let lensVp = main, W = W0, H = H0;
  const fovFor = v => 2 * THREE.MathUtils.radToDeg(Math.atan(Math.tan(THREE.MathUtils.degToRad(v.cam[6] / 2)) * H / frameOf(W, H, v.A).h));
  const setFov = f => { camera.fov = f; camera.updateProjectionMatrix(); };
  const half = { x: model.size[0] / 2, z: model.size[1] / 2 };
  function keep() {   // the eye stays over the stand and above the ground, the target on the stand
    const t = controls.target; t.x = clamp(t.x, -half.x, half.x); t.z = clamp(t.z, -half.z, half.z); t.y = clamp(t.y, 0, 40 * SC);
    if (camera.position.y < EYE_M * SC) camera.position.y = EYE_M * SC;
  }

  // the picture now: the viewpoint the camera is nearest, by the angle from its camera and by the distance -> { v, a }
  function pictureNow() {
    let best = { v: null, a: 0, ang: 180 };
    const p = camera.position;
    for (const v of VP) {
      if (!v.tex) continue;
      const c = camOf(v), dv = p.clone().sub(c.t), d = dv.length(); if (d < 1e-9) continue;
      const a0 = THREE.MathUtils.degToRad(c.az), e0 = THREE.MathUtils.degToRad(c.el);
      const ang = THREE.MathUtils.radToDeg(dv.normalize().angleTo(new THREE.Vector3(Math.sin(a0) * Math.cos(e0), Math.sin(e0), Math.cos(a0) * Math.cos(e0))));
      const a = (1 - ss(seg(ang, FULL_DEG, GONE_DEG))) * (1 - ss(seg(Math.abs(Math.log(d / c.d)), FULL_D, GONE_D)));
      if (a > best.a || (best.a === 0 && ang < best.ang)) best = { v, a, ang };
    }
    return best;
  }
  let shown = null, toned = false, picked = null;   // (shown: the viewpoint whose picture is in the projector)
  function paint() {   // the parts' tones and the picked one
    for (const p of parts) {
      const m = p.mesh.material, c = p.id === '_stand' ? STAND[clean ? 'clean' : 'look'] : toned && p.status ? TONE[p.status] : WHITE;
      m.color.set(c); m.emissive.copy(PICK).multiplyScalar(p.id === picked ? .28 : 0);
    }
  }
  function draw() {
    keep(); camera.lookAt(controls.target);
    const { t, d } = pose();
    camera.near = clamp(d * .04, .00002, .002); camera.updateProjectionMatrix(); camera.updateMatrixWorld();   // (close up to the walls the near plane follows)
    const P = clean ? { v: null, a: 0 } : pictureNow();
    if (P.v && P.v !== shown) { S.aimProjector(P.v.cam, P.v.A); U.uPI.value = P.v.tex; shown = P.v; }
    U.uPA.value = P.v ? P.a : 0; S.liveSky.material.uniforms.uA.value = U.uPA.value; S.liveSky.visible = U.uPA.value > 0;
    U.uPE.value = .035;   // (the picture's edges feathered: on a narrow stage the band of the picture shows them)
    edge.value = .55 * (1 - U.uPA.value);   // fine lines on the white model, none over the picture
    S.followShadow(t.x, t.y, t.z, Math.max(d, 60 * SC), KEY_AZ);   // the key light fixed in the room
    house.shadow.normalBias = 1.2 * SC; house.shadow.bias = -.0006;   // (followShadow sizes its bias by the film's plate: here a building's, metres not kilometres)
    renderer.shadowMap.needsUpdate = true; post.composer.render();
    if (on.picture) on.picture({ vp: P.v && P.a > .02 ? P.v.id : null, a: P.a });
  }
  let dirty = true, fly = null;
  controls.addEventListener('change', () => { dirty = true; });
  function tick(now) {
    if (fly) {
      const e = ss(clamp((now - fly.t0) / (FLY_S * 1000)));
      const t = fly.a.t.clone().lerp(fly.b.t, e), daz = ((fly.b.az - fly.a.az) % 360 + 540) % 360 - 180;
      put(t, fly.a.az + daz * e, lerp(fly.a.el, fly.b.el, e), Math.exp(lerp(Math.log(fly.a.d), Math.log(fly.b.d), e))); setFov(lerp(fly.f0, fly.f1, e));
      if (e >= 1) { fly = null; controls.enabled = true; }
      dirty = true;
    } else if (controls.enabled && controls.update()) dirty = true;
    if (dirty) { dirty = false; draw(); }
    requestAnimationFrame(tick);
  }

  // picking: a click (not a drag) on a part; a mouse over one shows the hand
  const ray = new THREE.Raycaster();
  const partAt = e => { const r = renderer.domElement.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, 1 - (e.clientY - r.top) / r.height * 2), camera);
    const hit = ray.intersectObjects(pickable.map(p => p.mesh), false)[0]; return hit ? pickable.find(p => p.mesh === hit.object).id : null; };
  let down = null, hoverT = 0;
  renderer.domElement.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
  renderer.domElement.addEventListener('pointermove', e => { if (e.pointerType !== 'mouse' || e.buttons || performance.now() - hoverT < 80) return; hoverT = performance.now();
    renderer.domElement.style.cursor = partAt(e) ? 'pointer' : ''; });
  renderer.domElement.addEventListener('pointerup', e => {
    if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6 || performance.now() - down.t > 600) return;
    picked = partAt(e); paint(); dirty = true; if (on.pick) on.pick(picked);
  });

  function size() {
    W = Math.max(1, stage.clientWidth); H = Math.max(1, stage.clientHeight);
    S.resize(W, H, clean ? 1 : Math.min(devicePixelRatio || 1, 2));
    if (W < 700) house.shadow.mapSize.set(2048, 2048);
    setFov(fovFor(lensVp)); dirty = true;
  }
  addEventListener('resize', size);

  // start at the viewpoint: the page's first picture is this very frame
  const c0 = camOf(main); put(c0.t, c0.az, c0.el, c0.d); size(); paint();
  await Promise.all(loads);   // (the pictures in: the projector shows the main one on the first frame)
  draw(); dirty = false; requestAnimationFrame(tick);

  return {
    flyToNearest() {   // the viewpoint with a picture nearest the camera's bearing: fly there
      const p = pose(); let best = null, ba = 1e9;
      for (const v of VP) { if (!v.tex) continue; const c = camOf(v), a = Math.abs(((c.az - p.az) % 360 + 540) % 360 - 180) + Math.abs(c.el - p.el); if (a < ba) { ba = a; best = v; } }
      if (!best) return;
      lensVp = best; controls.enabled = false; fly = { t0: performance.now(), a: p, b: camOf(best), f0: camera.fov, f1: fovFor(best) };
    },
    studio: S, redraw: draw,   // (for a look from the console, window.MUSEUM.m)
    tones(v) { toned = !!v; paint(); dirty = true; },
    select(id) { picked = id; paint(); dirty = true; },
    // tools/museum.mjs: the camera turned `turn` degrees round from a viewpoint (and `up` degrees higher), drawn now
    view({ vp = main.id, turn = 0, up = 0, tones, pick } = {}) {
      const v = VP.find(q => q.id === vp) || main, c = camOf(v); lensVp = v;
      put(c.t, c.az + turn, c.el + up, c.d); setFov(fovFor(v)); controls.update();
      if (tones != null) toned = !!tones; if (pick !== undefined) picked = pick; paint(); draw();
    },
  };
}
