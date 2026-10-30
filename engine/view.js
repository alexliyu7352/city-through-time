// The period cities' viewer (play.html?city=<slug>&view): the film's own scene, materials and light without its timeline. The
// period cities ticked stand whole at their places on the plate, today's city is hidden (or shown dimmed, as while a period city
// stands), and the camera is the viewer's: drag to turn round, right-drag to move, the wheel to come closer, the arrow keys to
// turn, a double click to look at that point. Two looks: 成片 (film: the era's colour in the light, its glow and edge line, depth
// of field, the key light beside the camera as in the film) and 檢查 (check: plain white in white light, everything sharp, the key
// light fixed in the room, so a face is seen to turn from lit to shade as the camera goes round: a face drawn inside out shows at once).
// Each city stands as it does at a moment of the film: a city that loses parts while it stands (lose:) has no moment with every
// part up (a house and the forum laid where it stood), so it has several moments (engine/eralife.js), the buttons 時刻 1, 2 .. under
// it; a city that loses nothing, one, once all of it has risen.
// URL: &eras=qin,han (ticked; default the first), &look=check, &today, &bare (no panel), &quality=low (faster, no shadows of the
// period cities), &at=<seconds> (every city ticked as it stands at that moment of the film instead).
// &free: the public mode, for visitors (with the film's bundle, &bundle=): one period at a time, chosen like a hall of a museum
// (&era=<id>; the cities standing at its moment, an imperial capital over the city it grew from), in the film's look but sharp
// (no depth of field, no vignette), the whole window, mouse and touch, down to a low eye over the streets; a landmark with a
// museum page (build/museum/index.json, tools/museum.py) is marked and opens it. No timeline, no film camera: that is the film.
// window.VIEW({ eras, look, today, at, target: <era id> | [x, z] (on the ground) | [x, y, z], az, el, d }) sets it from a script and draws
// (tools/eraview.mjs; at: a moment of the film, null for each city's own); window.VIEWINFO() lists the period cities with their
// centres, sizes and moments ({ t, dense }); a target 'qin:dense' is the densest 200 m square of that city at its moment, where its
// houses stand closest.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { words } from '../site/i18n.js';
import { REPO } from './overlay.js';

const FIXED_AZ = 355, WHITE = new THREE.Color(1, 1, 1);   // check: the key light (50 degrees left of this bearing, 45 up) stands in the south-west of the room (bearings as the camera keys count them: 0 south, 90 east)

export function startView(X) {
  const { S, FILM, QS, W, H, B, setLight, setLayers, eraShape, lens, cityMesh, eraBox, setDist, quiet, scale, takeChannel } = X;   // (takeChannel: a city ticked takes its shared channel; two ticked sharing one: the later)
  const { U, camera, post, renderer } = S;
  const FREE = QS.has('free'), EYE = 4 * scale;   // (free: the lowest eye, 4 m over the ground: the period cities stand twice or more their height)
  const LOOK = FILM.era_look || {}, LT = FILM.light, ERAS = (FILM.eras || []).filter(e => S.eras[e.id]);
  const TV = LT.lamp + 4;   // a moment with the projector on; what else the film shows then is cleared (quiet)
  const label = id => ((FILM.nodes || []).find(n => n.id === id) || {}).label || id;
  const ink = id => ((FILM.nodes || []).find(n => n.id === id) || {}).ink || 0;
  // a period city's centre and half-diagonal; 'id:dense' its densest 200 m square, where its houses stand closest
  const moment = id => eraBox[id].moments[Math.min(st.k[id] || 0, eraBox[id].moments.length - 1)];   // the city's moment chosen
  const timeOf = id => st.at ?? moment(id).t;
  const info = key => { const [id, part] = key.split(':'), b = eraBox[id].box, [x, z] = part === 'dense' ? moment(id).dense : [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
    return { x, y: S.ground(x, z), z, r: Math.hypot(b[2] - b[0], b[3] - b[1]) / 2 }; };
  let hud = null;   // (the panel's camera readout)
  const st = { on: new Set(QS.get('eras') ? QS.get('eras').split(',') : ERAS.slice(0, 1).map(e => e.id)), look: QS.get('look') === 'check' ? 'check' : 'film', today: QS.has('today'),
    at: QS.has('at') ? +QS.get('at') : null, k: {} };   // (k: each city's moment, by its number)

  // fit the 1920x1080 picture to the window
  const stage = document.getElementById('stage');
  const fit = () => { if (FREE) { S.resize(innerWidth, innerHeight, Math.min(devicePixelRatio || 1, 2)); return; }   // (free: the whole window, at the screen's pixels)
    const k = Math.min(innerWidth / W, innerHeight / H); stage.style.transformOrigin = 'top left'; stage.style.transform = `scale(${k})`; };
  fit(); window.addEventListener('resize', () => { fit(); ask(); });

  const controls = new OrbitControls(camera, renderer.domElement);
  Object.assign(controls, { enableDamping: false, screenSpacePanning: false, zoomToCursor: true, minDistance: .004, maxDistance: 4, maxPolarAngle: THREE.MathUtils.degToRad(88), rotateSpeed: .6 });
  if (FREE) Object.assign(controls, { minDistance: .0012, maxPolarAngle: THREE.MathUtils.degToRad(90) });   // (down to a street: 12 m from what it looks at, level)
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
      if (!on) { for (const b of e.basins || []) U.uBasinA.value[b.k] = 0; continue; }
      const u = E.u;   // as it stands at its moment (its fires out), in its own node's colour
      eraShape(e, timeOf(e.id)); u.uLossBurn.value.fill(0); u.uEraFallR.value = -1; u.uEraFallIn.value = 0; u.uEraFallW.value = -1;
      u.uEraA.value = film ? e.tint : 1; u.uEraBurn.value = 0; u.uEraGlow.value = film ? LOOK.glow ?? 1 : 0;   // check: the projector's light white at full strength
      u.uEraCol.value.copy(film ? E.base : WHITE); u.uEraCol0.value.copy(u.uEraCol.value); u.uEraInk.value = u.uEraInk0.value = film ? ink(e.id) : 0;
      if (e.hide != null) { takeChannel(e); U.uEdgeA.value[e.hide] = film ? 1 : 0; U.uHideCol.value[e.hide].copy(E.base); U.uHideT.value[e.hide] = st.today ? 1e3 : -1; }   // today's buildings step aside where it stands
    }
    cityMesh.visible = st.today;
    U.uToday.value = 1; U.uDimToday.value = U.uDimToday0.value = film ? LOOK.dim ?? .8 : .3;
  }
  let pending = false;
  function draw() {
    pending = false;
    const { az, el, d } = where(), t = controls.target, film = st.look === 'film';
    if (FREE) {   // the eye stays over the ground, what it looks at on it
      const t0 = controls.target, gt = S.ground(t0.x, t0.z), p = camera.position, gp = S.ground(p.x, p.z);
      if (t0.y < gt) t0.y = gt; if (p.y < gp + EYE) p.y = gp + EYE; camera.lookAt(t0);
    }
    camera.fov = FILM.fov || 30; camera.near = FREE ? Math.min(.02, Math.max(.00005, d * .04)) : Math.min(.02, Math.max(.0003, d * .04)); camera.updateProjectionMatrix(); camera.updateMatrixWorld();
    setDist(d, el); setLight(TV); setLayers(TV); apply(); S.groundsNow();
    S.followShadow(t.x, t.y, t.z, d, film ? az : FIXED_AZ);
    lens(d); if (!film) post.dof.aper = 0;
    if (FREE) { post.dof.aper = 0; post.dof.maxCoc = 0; }   // (everything sharp: the film's focus on its subject is the film's)
    renderer.shadowMap.needsUpdate = true; post.composer.render();
    if (pins) pins();
    const id0 = [...st.on][0];
    if (hud) hud.textContent = `az ${az.toFixed(0)}  el ${el.toFixed(0)}  d ${(d / scale).toFixed(0)} m` + (id0 && eraBox[id0] ? `  ${timeOf(id0).toFixed(1)} s` : '');
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
  let pins = null;
  if (FREE) pins = freePanel();
  else if (!QS.has('bare')) {
    const css = document.createElement('style');
    css.textContent = `.vw{position:fixed;left:16px;top:16px;z-index:9;width:250px;padding:14px 14px 12px;background:oklch(0.17 0.01 250 / .9);color:oklch(0.95 0.006 85);
      font:13px/1.45 system-ui,"PingFang TC","Noto Sans TC",sans-serif;border:1px solid oklch(0.95 0.006 85 / .14);border-radius:8px;user-select:none}
      .vw h1{margin:0 0 10px;font:600 14px/1.3 "Noto Serif TC",Georgia,serif;letter-spacing:.04em}
      .vw .seg{display:flex;gap:6px;margin:0 0 10px}.vw .seg button{flex:1;min-height:30px;border:1px solid oklch(0.95 0.006 85 / .25);border-radius:6px;background:none;color:inherit;font:inherit;cursor:pointer}
      .vw .seg button[aria-pressed=true],.vw .row button[aria-pressed=true]{background:oklch(0.86 0.11 80);border-color:transparent;color:oklch(0.2 0.02 80);font-weight:600}
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
      ${ERAS.map(e => `<div class="row"><label><input type="checkbox" data-era="${e.id}">${label(e.id)} <small style="display:inline">${e.id}</small></label><button type="button" data-go="${e.id}" title="整座城">全</button><button type="button" data-go="${e.id}:dense" title="房子最密的地方，近看" style="margin-left:4px">近</button></div>`
        + (eraBox[e.id].moments.length > 1 ? `<div class="row mo"><small style="flex:1">時刻</small>${eraBox[e.id].moments.map((m, k) => `<button type="button" data-mo="${e.id}:${k}" title="影片第 ${m.t} 秒" style="margin-left:4px">${k + 1}</button>`).join('')}</div>` : '')).join('')}
      <hr><div class="row"><label><input type="checkbox" data-today>今天的城（暗）</label></div><hr>
      <small>拖曳轉動 · 右鍵拖曳平移 · 滾輪遠近 · 方向鍵轉動 · 雙擊看那一點</small>
      <small><a href="?${q}">${low ? '成片畫質（較慢，有影子）' : '快速（低畫質，古城無影子）'}</a></small><div class="hud"></div>`;
    document.body.appendChild(box); hud = box.querySelector('.hud');
    const sync = () => {
      for (const b of box.querySelectorAll('[data-look]')) b.setAttribute('aria-pressed', String(b.dataset.look === st.look));
      for (const c of box.querySelectorAll('[data-era]')) c.checked = st.on.has(c.dataset.era);
      for (const b of box.querySelectorAll('[data-mo]')) { const [id, k] = b.dataset.mo.split(':'); b.setAttribute('aria-pressed', String(st.at == null && (st.k[id] || 0) === +k)); }
      box.querySelector('[data-today]').checked = st.today;
    };
    box.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.look) st.look = b.dataset.look;
      if (b.dataset.mo) { const [id, k] = b.dataset.mo.split(':'); st.k[id] = +k; st.at = null; st.on.add(id); }
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

  window.VIEWINFO = () => ERAS.map(e => ({ id: e.id, label: label(e.id), ...info(e.id), dense: [info(e.id + ':dense').x, info(e.id + ':dense').z], moments: eraBox[e.id].moments }));
  window.VIEW = async (o = {}) => {
    if (o.eras) st.on = new Set(o.eras.map(k => k.split(':')[0])); if (o.look) st.look = o.look; if (o.today != null) st.today = !!o.today; if ('at' in o) st.at = o.at ?? null;
    if (o.target) { const t = o.target, c = typeof t === 'string' ? info(t) : t.length === 2 ? { x: t[0], y: S.ground(t[0], t[1]), z: t[1] } : { x: t[0], y: t[1], z: t[2] }; controls.target.set(c.x, c.y, c.z); }
    const w = where(); place(o.az ?? w.az, o.el ?? w.el, o.d ?? w.d);
    if (window.__viewSync) window.__viewSync();
    draw(); await new Promise(r => requestAnimationFrame(r));
    return where();
  };
  if (FREE) { post.vig.uniforms.amt.value = 0; hall(ERAS.some(e => e.id === QS.get('era')) ? QS.get('era') : ERAS[0].id); }
  else goTo([...st.on][0] || ERAS[0].id);
  draw();

  // the public mode: a period chosen like a hall, the cities standing at its moment, its museum pages marked
  function hall(id) {
    const e = ERAS.find(q => q.id === id), m = eraBox[id].moments, t = m[m.length - 1].t;   // (its last moment: every part that stands has risen)
    st.at = t; st.on = new Set(ERAS.filter(q => q.on <= t && (q.off == null || t < q.off)).map(q => q.id)); st.on.add(e.id); st.hall = id;
    goTo(id); if (window.__viewSync) window.__viewSync();
  }
  function freePanel() {
    const lang = (QS.get('lang') || navigator.language || 'en').toLowerCase().startsWith('zh') ? 'zh' : 'en', Wd = words(lang === 'zh' ? 'zh-Hans' : 'en');
    const node = id => (FILM.nodes || []).find(n => n.id === id) || {}, name = id => lang === 'zh' ? node(id).label || id : node(id).label2 || node(id).label || id;
    const of = o => (o && (o[lang] || o.en)) || '';
    const city = QS.get('city'), bundle = QS.get('bundle'), keep = `&lang=${lang}${bundle ? '&bundle=' + encodeURIComponent(bundle) : ''}`;
    const css = document.createElement('style');
    css.textContent = `#stage canvas{touch-action:none}
      .fv{position:fixed;z-index:9;color:oklch(0.955 0.006 85);font:14px/1.45 "Albert Sans",system-ui,"PingFang SC","Noto Sans SC",sans-serif;-webkit-font-smoothing:antialiased}
      .fv a{color:inherit}.fv button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
      .fv :focus-visible{outline:2px solid oklch(0.865 0.115 80);outline-offset:3px;border-radius:6px}
      .fv-top{left:0;right:0;top:0;display:flex;align-items:flex-start;gap:14px;padding:max(14px,env(safe-area-inset-top)) 18px 0;pointer-events:none}.fv-top>*{pointer-events:auto}
      .fv-name{margin:0;padding:10px 16px;border-radius:12px;background:oklch(0.155 0.014 255 / .72);backdrop-filter:blur(10px)}
      .fv-name b{display:block;font:700 19px/1.25 "Noto Serif SC",serif;letter-spacing:.08em}.fv-name span{color:oklch(0.80 0.012 250);font-size:13px}
      .fv-tools{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
      .fv-pill{display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 14px;border-radius:999px;background:oklch(0.155 0.014 255 / .72);backdrop-filter:blur(10px);text-decoration:none;font-size:13.5px}
      .fv-pill input{accent-color:oklch(0.865 0.115 80);width:16px;height:16px;margin:0}
      .fv-bot{left:0;right:0;bottom:0;padding:0 18px max(14px,env(safe-area-inset-bottom));pointer-events:none}.fv-bot>*{pointer-events:auto}
      .fv-hint{margin:0 0 10px;color:oklch(0.80 0.012 250);font-size:13px;text-shadow:0 1px 2px #000}
      .fv-credit{display:block;margin:8px 0 0;color:oklch(0.80 0.012 250);font-size:12px;text-decoration:none;text-shadow:0 1px 2px #000;width:max-content}.fv-credit:hover{color:oklch(0.955 0.006 85)}
      .fv-halls{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}.fv-halls::-webkit-scrollbar{display:none}
      .fv-halls button{flex:none;min-height:52px;padding:7px 14px;border-radius:12px;background:oklch(0.155 0.014 255 / .72);backdrop-filter:blur(10px);text-align:left;border:1px solid oklch(0.955 0.006 85 / .12)}
      .fv-halls button small{display:block;color:oklch(0.80 0.012 250);font-size:12px;font-variant-numeric:tabular-nums}
      .fv-halls button b{font-weight:600;font-size:14.5px}
      .fv-halls button[aria-pressed=true]{background:oklch(0.865 0.115 80);color:oklch(0.22 0.035 75);border-color:transparent}.fv-halls button[aria-pressed=true] small{color:oklch(0.33 0.04 75)}
      .fv-pin{position:fixed;z-index:8;left:0;top:0;display:flex;align-items:center;gap:8px;translate:-11px -50%;padding:0;text-decoration:none;color:oklch(0.22 0.035 75);font:600 13.5px/1.3 "Albert Sans","PingFang SC","Noto Sans SC",sans-serif}
      .fv-pin i{width:22px;height:22px;border-radius:50%;background:oklch(0.865 0.115 80);box-shadow:0 0 0 5px oklch(0.865 0.115 80 / .3);flex:none}
      .fv-pin span{padding:6px 11px;border-radius:999px;background:oklch(0.955 0.006 85 / .94);white-space:nowrap}.fv-pin:hover span{background:#fff}.fv-pin[hidden]{display:none}
      .fv-name b,.fv-pill{white-space:nowrap}
      @media (max-width:640px){.fv-hint{display:none}.fv-name{padding:8px 12px}.fv-name b{font-size:16px}.fv-pill{min-height:36px;padding:0 11px;font-size:12.5px}.fv-tools{gap:6px}
        .fv-top{padding:max(10px,env(safe-area-inset-top)) 10px 0}.fv-bot{padding:0 10px max(10px,env(safe-area-inset-bottom))}}`;
    document.head.appendChild(css);
    const top = document.createElement('div'); top.className = 'fv fv-top';
    top.innerHTML = `<p class="fv-name"><b>${Wd.t('walkTitle')}</b><span>${lang === 'zh' ? (FILM.identity?.l1 || '').split(' · ')[0] : city}</span></p>
      <div class="fv-tools"><label class="fv-pill"><input type="checkbox" data-today>${Wd.t('walkToday')}</label>
      <a class="fv-pill" href="?city=${encodeURIComponent(city)}&view&free&era=${'{era}'}&lang=${lang === 'zh' ? 'en' : 'zh'}${bundle ? '&bundle=' + encodeURIComponent(bundle) : ''}" data-lang>${lang === 'zh' ? 'EN' : '中文'}</a>
      <a class="fv-pill" href="${lang === 'zh' ? 'zh-hans/' : ''}${encodeURIComponent(city)}/">${Wd.t('walkFilm')}</a></div>`;
    const bot = document.createElement('div'); bot.className = 'fv fv-bot';
    bot.innerHTML = `<p class="fv-hint">${Wd.t('walkHint')}</p><nav class="fv-halls" aria-label="${Wd.t('walkPeriods')}">${ERAS.map(e => `<button type="button" data-hall="${e.id}"><small>${Wd.year(Math.round((node(e.id).years || [0])[0]))}</small><b>${name(e.id)}</b></button>`).join('')}</nav>
      <a class="fv-credit" href="${REPO}" target="_blank" rel="noopener">一城春秋 · A City Through Time</a>`;   // (LICENSE, condition 2c)
    document.body.append(top, bot);
    const sync = () => {
      for (const b of bot.querySelectorAll('[data-hall]')) b.setAttribute('aria-pressed', String(b.dataset.hall === st.hall));
      top.querySelector('[data-today]').checked = st.today;
      const a = top.querySelector('[data-lang]'); a.href = a.href.replace(/era=[^&]*/, 'era=' + st.hall);
    };
    window.__viewSync = sync;
    bot.addEventListener('click', e => { const b = e.target.closest('[data-hall]'); if (b) { hall(b.dataset.hall); ask(); } });
    top.addEventListener('change', e => { if ('today' in e.target.dataset) { st.today = e.target.checked; ask(); } });
    // the museum pages: a mark over each landmark that has one, while its period stands; a click on it (or on the building) opens it
    const marks = [];
    fetch(B + 'museum/index.json').then(r => r.ok ? r.json() : []).catch(() => []).then(list => {
      for (const m of list) {
        const a = document.createElement('a'); a.className = 'fv-pin'; a.hidden = true;
        a.href = `museum.html?city=${encodeURIComponent(city)}&id=${encodeURIComponent(m.id)}${keep}`;
        a.innerHTML = `<i></i><span>${Wd.fmt('walkMuseum', { name: of(m.name) })}</span>`; document.body.appendChild(a); marks.push({ m, a });
      }
      ask();
    });
    const v = new THREE.Vector3(), ray = new THREE.Raycaster(); let down = null;
    renderer.domElement.addEventListener('pointerdown', e => { down = [e.clientX, e.clientY]; });
    renderer.domElement.addEventListener('pointerup', e => {   // a click (not a drag) on a building that has a museum page
      if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 6) return;
      const r = renderer.domElement.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, 1 - (e.clientY - r.top) / r.height * 2), camera);
      const hit = ray.intersectObjects(ERAS.filter(q => st.on.has(q.id)).map(q => S.eras[q.id].mesh), false)[0]; if (!hit) return;
      const k = marks.find(({ m }) => st.on.has(m.node) && Math.hypot(hit.point.x - m.x, hit.point.z - m.z) < m.r); if (k) location.href = k.a.href;
    });
    return () => {   // after each frame: the marks follow their landmarks, seen from above (low in the streets a mark would show through the walls)
      const p = camera.position, high = p.y - S.ground(p.x, p.z) > 60 * scale;
      for (const { m, a } of marks) {
        const on = st.on.has(m.node) && (high || Math.hypot(p.x - m.x, p.z - m.z) < 3 * m.r); v.set(m.x, S.ground(m.x, m.z) + 25 * scale * 2, m.z).project(camera);
        a.hidden = !on || v.z > 1 || Math.abs(v.x) > 1.05 || Math.abs(v.y) > 1.05;
        if (!a.hidden) a.style.transform = `translate(${(v.x * .5 + .5) * innerWidth}px, ${(-v.y * .5 + .5) * innerHeight}px)`;
      }
    };
  }
}
