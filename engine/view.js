// The period cities' viewer (play.html?city=<slug>&view): the film's own scene, materials and light without its timeline. The
// period cities ticked stand whole at their places on the plate, today's city is hidden (or shown dimmed, as while a period city
// stands), and the camera is the viewer's: drag to turn round, right-drag to move, the wheel to come closer, the arrow keys to
// turn, a double click to look at that point. Two looks: 成片 (film: the era's colour in the light, its glow and edge line, depth
// of field, the key light beside the camera as in the film) and 檢查 (check: plain white in white light, everything sharp, the key
// light fixed in the room, so a face is seen to turn from lit to shade as the camera goes round: a face drawn inside out shows at once).
// URL: &eras=qin,han (ticked; default the first), &look=check, &today, &bare (no panel), &quality=low (faster, no shadows of the
// period cities). window.VIEW({ eras, look, today, target: <era id> | [x, z] (on the ground) | [x, y, z], az, el, d }) sets it from a script and draws
// (tools/eraview.mjs); window.VIEWINFO() lists the period cities with their centres and sizes; a target 'qin:dense' is the densest
// 200 m square of that city, where its houses stand closest.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const FIXED_AZ = 355, WHITE = new THREE.Color(1, 1, 1);   // check: the key light (50 degrees left of this bearing, 45 up) stands in the south-west of the room (bearings as the camera keys count them: 0 south, 90 east)

export function startView(X) {
  const { S, FILM, QS, W, H, setLight, setLayers, lens, cityMesh, eraBox, setDist, quiet, scale } = X;
  const { U, camera, post, renderer } = S;
  const LOOK = FILM.era_look || {}, LT = FILM.light, ERAS = (FILM.eras || []).filter(e => S.eras[e.id]);
  const TV = LT.lamp + 4;   // a moment with the projector on; what else the film shows then is cleared (quiet)
  const label = id => ((FILM.nodes || []).find(n => n.id === id) || {}).label || id;
  const ink = id => ((FILM.nodes || []).find(n => n.id === id) || {}).ink || 0;
  // a period city's centre and half-diagonal; 'id:dense' its densest 200 m square, where its houses stand closest
  const info = key => { const [id, part] = key.split(':'), { box: b, dense } = eraBox[id], [x, z] = part === 'dense' ? dense : [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
    return { x, y: S.ground(x, z), z, r: Math.hypot(b[2] - b[0], b[3] - b[1]) / 2 }; };
  let hud = null;   // (the panel's camera readout)
  const st = { on: new Set(QS.get('eras') ? QS.get('eras').split(',') : ERAS.slice(0, 1).map(e => e.id)), look: QS.get('look') === 'check' ? 'check' : 'film', today: QS.has('today') };

  // fit the 1920x1080 picture to the window
  const stage = document.getElementById('stage');
  const fit = () => { const k = Math.min(innerWidth / W, innerHeight / H); stage.style.transformOrigin = 'top left'; stage.style.transform = `scale(${k})`; };
  fit(); window.addEventListener('resize', () => { fit(); ask(); });

  const controls = new OrbitControls(camera, renderer.domElement);
  Object.assign(controls, { enableDamping: false, screenSpacePanning: false, zoomToCursor: true, minDistance: .004, maxDistance: 4, maxPolarAngle: THREE.MathUtils.degToRad(88), rotateSpeed: .6 });
  const sph = new THREE.Spherical();
  const where = () => { const v = camera.position.clone().sub(controls.target); sph.setFromVector3(v); return { az: THREE.MathUtils.radToDeg(Math.atan2(v.x, v.z)), el: 90 - THREE.MathUtils.radToDeg(sph.phi), d: sph.radius }; };
  const place = (az, el, d) => { const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(Math.max(1, Math.min(88, el))), t = controls.target;
    camera.position.set(t.x + d * Math.sin(a) * Math.cos(e), t.y + d * Math.sin(e), t.z + d * Math.cos(a) * Math.cos(e)); controls.update(); };
  const goTo = key => { const c = info(key); controls.target.set(c.x, c.y, c.z); key.endsWith(':dense') ? place(305, 20, .045) : place(305, 30, Math.min(2.8, Math.max(.04, c.r * 2.2))); };   // the whole city, or a close-up of its houses

  // the scene for the period cities ticked, in the look chosen
  function apply() {
    const film = st.look === 'film';
    quiet();
    for (const e of ERAS) {
      const E = S.eras[e.id], on = st.on.has(e.id);
      E.mesh.visible = on;
      if (S.edges[e.id]) S.edges[e.id].set(on && film ? LOOK.line ?? 1 : 0, E.base, 1);
      if (S.fires[e.id]) S.fires[e.id].set(0, TV, 1e3, [0, 0]);
      if (!on) continue;
      const u = E.u;   // standing whole, in its own node's colour
      u.uEraT.value = 1e6; u.uEraSpan.value = e.span; u.uEraGrow.value = e.grow; u.uEraFallR.value = -1; u.uEraFallIn.value = 0; u.uEraFallW.value = -1;
      u.uEraA.value = film ? e.tint : 1; u.uEraBurn.value = 0; u.uEraGlow.value = film ? LOOK.glow ?? 1 : 0;   // check: the projector's light white at full strength
      u.uEraCol.value.copy(film ? E.base : WHITE); u.uEraCol0.value.copy(u.uEraCol.value); u.uEraInk.value = u.uEraInk0.value = film ? ink(e.id) : 0;
      if (e.hide != null) { U.uEdgeA.value[e.hide] = film ? 1 : 0; U.uHideCol.value[e.hide].copy(E.base); U.uHideT.value[e.hide] = st.today ? 1e3 : -1; }   // today's buildings step aside where it stands
    }
    cityMesh.visible = st.today;
    U.uToday.value = 1; U.uDimToday.value = U.uDimToday0.value = film ? LOOK.dim ?? .5 : .3;
  }
  let pending = false;
  function draw() {
    pending = false;
    const { az, el, d } = where(), t = controls.target, film = st.look === 'film';
    camera.fov = FILM.fov || 30; camera.near = Math.min(.02, Math.max(.0003, d * .04)); camera.updateProjectionMatrix(); camera.updateMatrixWorld();
    setDist(d, el); setLight(TV); setLayers(TV); apply();
    S.followShadow(t.x, t.y, t.z, d, film ? az : FIXED_AZ);
    lens(d); if (!film) post.dof.aper = 0;
    renderer.shadowMap.needsUpdate = true; post.composer.render();
    if (hud) hud.textContent = `az ${az.toFixed(0)}  el ${el.toFixed(0)}  d ${(d / scale).toFixed(0)} m`;
  }
  const ask = () => { if (!pending) { pending = true; requestAnimationFrame(draw); } };
  controls.addEventListener('change', ask);

  // turning with the keys, looking at a point with a double click
  window.addEventListener('keydown', e => {
    const k = { ArrowLeft: [-10, 0], ArrowRight: [10, 0], ArrowUp: [0, 5], ArrowDown: [0, -5] }[e.code]; if (!k) return;
    e.preventDefault(); const w = where(); place(w.az + k[0], w.el + k[1], w.d);
  });
  const ray = new THREE.Raycaster();
  renderer.domElement.addEventListener('dblclick', e => {
    const r = renderer.domElement.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, 1 - (e.clientY - r.top) / r.height * 2), camera);
    const hit = ray.intersectObjects(S.scene.children.filter(o => o.isMesh && o.visible), false)[0]; if (!hit) return;
    const off = camera.position.clone().sub(controls.target); controls.target.copy(hit.point); camera.position.copy(hit.point).add(off.multiplyScalar(.6)); controls.update();
  });

  // the panel
  if (!QS.has('bare')) {
    const css = document.createElement('style');
    css.textContent = `.vw{position:fixed;left:16px;top:16px;z-index:9;width:250px;padding:14px 14px 12px;background:oklch(0.17 0.01 250 / .9);color:oklch(0.95 0.006 85);
      font:13px/1.45 system-ui,"PingFang TC","Noto Sans TC",sans-serif;border:1px solid oklch(0.95 0.006 85 / .14);border-radius:8px;user-select:none}
      .vw h1{margin:0 0 10px;font:600 14px/1.3 "Noto Serif TC",Georgia,serif;letter-spacing:.04em}
      .vw .seg{display:flex;gap:6px;margin:0 0 10px}.vw .seg button{flex:1;min-height:30px;border:1px solid oklch(0.95 0.006 85 / .25);border-radius:6px;background:none;color:inherit;font:inherit;cursor:pointer}
      .vw .seg button[aria-pressed=true]{background:oklch(0.86 0.11 80);border-color:transparent;color:oklch(0.2 0.02 80);font-weight:600}
      .vw label{display:flex;align-items:center;gap:8px;min-height:28px;cursor:pointer;flex:1}.vw .row{display:flex;align-items:center}
      .vw .row button{min-height:26px;padding:0 9px;border:1px solid oklch(0.95 0.006 85 / .22);border-radius:5px;background:none;color:inherit;font:12px/1 inherit;cursor:pointer}
      .vw .row button:hover,.vw .seg button:hover{border-color:oklch(0.95 0.006 85 / .55)}.vw button:focus-visible{outline:2px solid oklch(0.86 0.11 80);outline-offset:2px}
      .vw small{display:block;color:oklch(0.95 0.006 85 / .6);font-size:12px}.vw hr{border:0;border-top:1px solid oklch(0.95 0.006 85 / .12);margin:8px 0}
      .vw .hud{font:12px/1.4 ui-monospace,monospace;color:oklch(0.95 0.006 85 / .7);margin-top:6px}.vw a{color:oklch(0.86 0.11 80)}`;
    document.head.appendChild(css);
    const box = document.createElement('div'); box.className = 'vw';
    const q = new URLSearchParams(location.search), low = q.get('quality') === 'low'; low ? q.delete('quality') : q.set('quality', 'low');
    box.innerHTML = `<h1>古城檢視 · ${(FILM.identity?.l1 || '').split(' · ')[0]}</h1>
      <div class="seg"><button type="button" data-look="film">成片</button><button type="button" data-look="check">檢查</button></div>
      ${ERAS.map(e => `<div class="row"><label><input type="checkbox" data-era="${e.id}">${label(e.id)} <small style="display:inline">${e.id}</small></label><button type="button" data-go="${e.id}" title="整座城">全</button><button type="button" data-go="${e.id}:dense" title="房子最密的地方，近看" style="margin-left:4px">近</button></div>`).join('')}
      <hr><div class="row"><label><input type="checkbox" data-today>今天的城（暗）</label></div><hr>
      <small>拖曳轉動 · 右鍵拖曳平移 · 滾輪遠近 · 方向鍵轉動 · 雙擊看那一點</small>
      <small><a href="?${q}">${low ? '成片畫質（較慢，有影子）' : '快速（低畫質，古城無影子）'}</a></small><div class="hud"></div>`;
    document.body.appendChild(box); hud = box.querySelector('.hud');
    const sync = () => {
      for (const b of box.querySelectorAll('[data-look]')) b.setAttribute('aria-pressed', String(b.dataset.look === st.look));
      for (const c of box.querySelectorAll('[data-era]')) c.checked = st.on.has(c.dataset.era);
      box.querySelector('[data-today]').checked = st.today;
    };
    box.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.look) st.look = b.dataset.look;
      if (b.dataset.go) { st.on.add(b.dataset.go.split(':')[0]); goTo(b.dataset.go); }
      sync(); ask();
    });
    box.addEventListener('change', e => {
      const c = e.target; if (c.dataset.era) c.checked ? st.on.add(c.dataset.era) : st.on.delete(c.dataset.era);
      if ('today' in c.dataset) st.today = c.checked;
      ask();
    });
    sync(); window.__viewSync = sync;
  }

  window.VIEWINFO = () => ERAS.map(e => ({ id: e.id, label: label(e.id), ...info(e.id), dense: [info(e.id + ':dense').x, info(e.id + ':dense').z] }));
  window.VIEW = async (o = {}) => {
    if (o.eras) st.on = new Set(o.eras.map(k => k.split(':')[0])); if (o.look) st.look = o.look; if (o.today != null) st.today = !!o.today;
    if (o.target) { const t = o.target, c = typeof t === 'string' ? info(t) : t.length === 2 ? { x: t[0], y: S.ground(t[0], t[1]), z: t[1] } : { x: t[0], y: t[1], z: t[2] }; controls.target.set(c.x, c.y, c.z); }
    const w = where(); place(o.az ?? w.az, o.el ?? w.el, o.d ?? w.d);
    if (window.__viewSync) window.__viewSync();
    draw(); await new Promise(r => requestAnimationFrame(r));
    return where();
  };
  goTo([...st.on][0] || ERAS[0].id); draw();
}
