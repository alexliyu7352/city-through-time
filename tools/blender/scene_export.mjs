// The film's scene at one moment, out of the page for an offline render (tools/blender/film_still.py): what the colour look draws
// there, within `radius` metres of the camera's target, as a glTF of plain triangles in world space (instances expanded, each
// mesh its world matrix applied), a group per mesh named by what it is; beside it the camera (position, target, fov, near) and
// a picture from that camera: its colours under an even white light with no
// sun, occlusion, blur or grade (`albedo.png`: laid back on the geometry from the camera, it gives every visible surface the
// colour the page's shaders give it; some shading of the page's own stays in it).
// usage: node tools/blender/scene_export.mjs <city> <t> --out <dir> [--q 'cam=...'] [--radius 900] [--list]
// What a vertex shader moves is taken as it stands at full: an era city's buildings as built, the land as laid (its relief is
// light, not height). So a moment while a city rises or is taken back is not exported right; today's city (CITYMESH) is left
// out (the city mesh's period buildings kept), as it steps aside wherever a period city stands.
import fs from 'fs'; import path from 'path';
import { openFilm, closeServer, shot } from '../../render/page.mjs';

// the even light the colour pictures are taken under (mini.js FILM_PIC through ?pic=): no sun, a white sky all round, no
// occlusion, blur, vignette or grade; the geometry the page draws does not depend on it
const EVEN = { sun: .001, sunEl: 89.5, sky: 3, skyC: '#ffffff', skyGround: '#ffffff', ao: .001, vignette: .001, sat: 1, contrast: .001, dof: { Ak: 1e-6, k: 1e-4, max: .001 }, fogNear: 1000, fogFar: 2000 };
const args = process.argv.slice(2), take = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
const out = take('--out'), q = take('--q', '') + '&pic=' + encodeURIComponent(JSON.stringify(EVEN)), radius = +take('--radius', 900), list = args.includes('--list');
const [city, t] = args.filter(a => !a.startsWith('--'));
if (!city || !t || (!out && !list)) { console.error('usage: node tools/blender/scene_export.mjs <city> <t> --out <dir> [--q ...] [--radius m] [--list]'); process.exit(2); }

const { browser, page } = await openFilm(city, { q: (q ? q + '&' : '') + 'clean&export' });
const res = await page.evaluate(async ({ t, radius, list }) => {
  await window.render(+t); const cam = window.CAMAT(+t);
  const { S, THREE, CITYMESH } = window.EXPORT, scale = S.U.uScaleM.value, R = radius * scale, [tx, , tz] = cam.tg;
  const layer = new THREE.Layers(); layer.set(1);   // (the colour look's layer, mini.js L)
  const shown = o => { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; };
  const meshes = []; S.scene.updateMatrixWorld(true);
  S.scene.traverse(o => { if ((o.isMesh || o.isInstancedMesh) && o.layers.test(layer) && shown(o) && o.geometry && o.geometry.attributes.position && !o.material.transparent) meshes.push(o); });
  if (list) return { cam, scale, list: meshes.map(o => [o.name || '', o.type, o.isInstancedMesh ? o.count : 1, o.geometry.attributes.position.count, o.material.type, o.material.name || '', o.parent && o.parent.name || '']) };
  const groups = [], m4 = new THREE.Matrix4(), v = new THREE.Vector3(), c = new THREE.Color();
  for (const o of meshes) {
    const g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry, P = g.attributes.position, VC = g.attributes.color, AD = o === CITYMESH ? g.attributes.aData : null, n = o.isInstancedMesh ? o.count : 1, pos = [], col = [];
    const base = o.material.color ? o.material.color.clone() : new THREE.Color(1, 1, 1);
    for (let i = 0; i < n; i++) {
      if (o.isInstancedMesh) { o.getMatrixAt(i, m4); m4.premultiply(o.matrixWorld); } else m4.copy(o.matrixWorld);
      if (o.isInstancedMesh) { v.setFromMatrixPosition(m4); if (Math.hypot(v.x - tx, v.z - tz) > R) continue; if (o.instanceColor) o.getColorAt(i, c); else c.setRGB(1, 1, 1); } else c.setRGB(1, 1, 1);
      for (let j = 0; j < P.count; j += 3) {
        if (AD && !(AD.getW(j) > 2.5)) continue;   // (the city mesh: its period cities' buildings, not today's, which step aside where one stands)
        const tri = [0, 1, 2].map(k => v.fromBufferAttribute(P, j + k).applyMatrix4(m4).toArray());
        if (!o.isInstancedMesh && Math.hypot((tri[0][0] + tri[1][0] + tri[2][0]) / 3 - tx, (tri[0][2] + tri[1][2] + tri[2][2]) / 3 - tz) > R) continue;
        for (let k = 0; k < 3; k++) { pos.push(...tri[k]); const vc = VC ? [VC.getX(j + k), VC.getY(j + k), VC.getZ(j + k)] : [1, 1, 1]; col.push(base.r * c.r * vc[0], base.g * c.g * vc[1], base.b * c.b * vc[2]); }
      }
    }
    if (pos.length) groups.push({ name: (o.name || o.material.name || (o.isInstancedMesh ? 'field' : o.type)) + '_' + groups.length + (o.isInstancedMesh ? '~' + P.count : ''), pos, col });   // (~n: an instance's vertices, in order)
  }
  // the glb: one mesh a group, positions in metres about the target (x east, y up, z south as three.js has them)
  const root = new THREE.Scene();
  for (const G of groups) { const geo = new THREE.BufferGeometry(), p = new Float32Array(G.pos.length);
    for (let i = 0; i < p.length; i += 3) { p[i] = (G.pos[i] - tx) / scale; p[i + 1] = G.pos[i + 1] / scale; p[i + 2] = (G.pos[i + 2] - tz) / scale; }
    geo.setAttribute('position', new THREE.BufferAttribute(p, 3)); geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(G.col), 3)); geo.computeVertexNormals();
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true })); m.name = G.name; root.add(m); }
  const { GLTFExporter } = await import('three/addons/exporters/GLTFExporter.js');
  const glb = await new GLTFExporter().parseAsync(root, { binary: true });
  let s = ''; const b = new Uint8Array(glb); for (let i = 0; i < b.length; i += 32768) s += String.fromCharCode(...b.subarray(i, i + 32768));
  const rel = a => [(a[0] - tx) / scale, a[1] / scale, (a[2] - tz) / scale];
  return { cam: { p: rel(cam.p), tg: rel(cam.tg), fov: cam.fov, near: cam.near / scale }, scale, glb: btoa(s), groups: groups.map(G => [G.name, G.pos.length / 9]) };
}, { t, radius, list });
if (list) { console.log(JSON.stringify(res.cam)); for (const r of res.list) console.log(r.join('  ')); await browser.close(); closeServer(); process.exit(0); }
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, 'scene.glb'), Buffer.from(res.glb, 'base64'));
fs.writeFileSync(path.join(out, 'camera.json'), JSON.stringify({ city, t: +t, q, ...res.cam, groups: res.groups }, null, 1));
await page.evaluate(t => window.render(+t), t); await shot(page, { path: path.join(out, 'albedo.png') }, true);
await browser.close();
console.log(`${out}: scene.glb ${(fs.statSync(path.join(out, 'scene.glb')).size / 1e6).toFixed(1)} MB, ${res.groups.length} groups, ${res.groups.reduce((a, g) => a + g[1], 0)} triangles`);
closeServer();
