"""A still of the film's colour picture rendered in Blender from the scene the page had at that moment (tools/blender/scene_export.mjs:
scene.glb, camera.json, albedo.png), as a model on a table: the scene at 1:1000, a warm sun and a sky, light bounced between
the buildings, the camera and its depth of field as the page's. Blender's path is local/config.json `blender`; run headless:
    <blender> -b --factory-startup --python tools/blender/film_still.py -- --dir <export dir> --out still.png
        [--variant A|B] [--engine cycles|eevee] [--samples 96] [--threads 12] [--size 1920x1080]
A: the page's geometry and colours (the colours laid on from the camera, albedo.png; the pieces with colours of their own,
their own), only the light new. B: A with what reads at this distance: round full crowns in place of the faceted ones, edges
rounded where they catch the light (a bevel at render), a rammed-earth or plaster grain on the walls."""
import bpy, bmesh, json, math, os, sys, time
import numpy as np
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
arg = lambda k, d=None: a[a.index(k) + 1] if k in a else d
D, OUT, VAR, ENG = arg('--dir'), arg('--out'), arg('--variant', 'A'), arg('--engine', 'cycles')
SAMPLES, THREADS, (W, H) = int(arg('--samples', 96)), int(arg('--threads', 12)), map(int, arg('--size', '1920x1080').split('x'))
K = .001   # the model's scale: a metre of the city a millimetre of the model
cam = json.load(open(os.path.join(D, 'camera.json')))
bl = lambda p: Vector((p[0] * K, -p[2] * K, p[1] * K))   # (three.js x, y up, z south -> Blender x, y north, z up)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(D, 'scene.glb'))
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in objs: o.scale = (K, K, K); o.location.z = float(arg('--dz', 0)) * K   # (the importer turned y up into z up already; dz: a lift in metres)
bpy.context.view_layer.update()

# the camera: the page's, its vertical field of view, focused a little beyond its target (the page's lens, mini.js FILM_PIC dof)
cd = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cd); bpy.context.scene.collection.objects.link(co)
P, T = bl(cam['p']), bl(cam['tg']); co.location = P; co.rotation_euler = (T - P).to_track_quat('-Z', 'Y').to_euler()
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.lens = 12 / math.tan(math.radians(cam['fov']) / 2); cd.clip_start = cam['near'] * K * .5; cd.clip_end = 50
cd.dof.use_dof = True; cd.dof.focus_distance = (T - P).length * 1.1; cd.dof.aperture_fstop = float(arg('--fstop', 5.6))
bpy.context.scene.camera = co

# the light: a warm sun low to the camera's right, a sky's cool fill
dirc = (T - P).normalized(); az = math.atan2(dirc.y, dirc.x)
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = float(arg('--sun', 4.2)); sun.color = (1.0, .9, .76); sun.angle = math.radians(1.2)
so = bpy.data.objects.new('sun', sun); bpy.context.scene.collection.objects.link(so)
so.rotation_euler = (math.radians(90 - 36), 0, az + math.radians(90 + 120))   # (36 degrees up, from the right and a little behind the eye)
wd = bpy.data.worlds.new('w'); bpy.context.scene.world = wd; wd.use_nodes = True
bg = wd.node_tree.nodes['Background']; bg.inputs[0].default_value = (.55, .68, .9, 1); bg.inputs[1].default_value = float(arg('--sky', .9))

# the materials: the colours laid on from the camera where the page's shaders gave them (no colours of their own in the glb),
# the pieces' own colours otherwise
img = bpy.data.images.load(os.path.join(D, 'albedo.png')); img.colorspace_settings.name = 'sRGB'
def material(name, own, tree=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L_ = nt.nodes, nt.links; bsdf = N['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = .85
    if own: src = N.new('ShaderNodeVertexColor'); src.layer_name = 'Color'; out = src.outputs['Color']
    else:
        tc = N.new('ShaderNodeTexCoord'); tx = N.new('ShaderNodeTexImage'); tx.image = img; tx.extension = 'EXTEND'; L_.new(tc.outputs['Window'], tx.inputs['Vector'])
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
        L_.new(tx.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (.62, .62, .62, 1); out = mx.outputs['Result']   # (the even light's picture down to a surface's own colour)
    hs = N.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = 1.18; L_.new(out, hs.inputs['Color']); L_.new(hs.outputs['Color'], bsdf.inputs['Base Color'])   # (the page's muted paint lifted back)
    if VAR == 'B' and not tree:   # edges rounded where they catch the light; the walls' grain
        bv = N.new('ShaderNodeBevel'); bv.inputs['Radius'].default_value = .35 * K; bv.samples = 6
        nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900; bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = .12
        L_.new(nz.outputs['Fac'], bm.inputs['Height']); L_.new(bv.outputs['Normal'], bm.inputs['Normal']); L_.new(bm.outputs['Normal'], bsdf.inputs['Normal'])
    return m

TREES = ('crown', 'cone')
for o in objs:
    tree = any(t in o.name for t in TREES)
    own = o.name.startswith(('detail:', 'field'))   # (the pieces coloured per instance; the land and the city's own mesh coloured by the page's shaders)
    o.data.materials.clear(); o.data.materials.append(material(o.name, own, tree))

# B: each faceted crown (an instance's run of vertices, the glb's ~n) made a round, full one of the same size, smooth, a little lumpy
def crowns(o):
    if '~' not in o.name or not ('crown' in o.name or o.name.startswith('field') and o.name.split('~')[1].split('.')[0] == '60'): return None
    return int(o.name.split('~')[1].split('.')[0])
if VAR == 'B':
    ico = bmesh.new(); bmesh.ops.create_icosphere(ico, subdivisions=2, radius=1.0); iv = np.array([x.co[:] for x in ico.verts]); iface = [[x.index for x in fc.verts] for fc in ico.faces]; ico.free()
    rng = np.random.default_rng(1)
    for o in objs:
        n = crowns(o)
        if not n: continue
        me = o.data; v = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', v); v = v.reshape(-1, 3)
        if len(v) % n: continue
        col = np.ones(len(me.vertices) * 4, np.float32)
        if me.color_attributes: me.color_attributes[0].data.foreach_get('color', col)
        v = v.reshape(-1, n, 3); col = col.reshape(-1, n, 4); cen = v.mean(1); ext = np.linalg.norm(v - cen[:, None], axis=2).max(1); cc = col.mean(1)
        bm_ = bmesh.new(); cl = bm_.loops.layers.color.new('Color')
        for c, e, g in zip(cen, ext, cc):
            vs = [bm_.verts.new(Vector(c + p)) for p in iv * (e * .95 * (1 + .1 * rng.standard_normal(len(iv))))[:, None] * np.array([1, 1, .88])]
            g = g * np.array([.8, .95, .75, 1])   # (a deeper, fuller green)
            for fc in iface:
                ff = bm_.faces.new([vs[j] for j in fc]); ff.smooth = True
                for lp in ff.loops: lp[cl] = g
        me2 = bpy.data.meshes.new(o.name + '_round'); bm_.to_mesh(me2); bm_.free()
        o.data = me2; me2.materials.append(material(o.name + '_round', True, True))

sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.filepath = OUT
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
if ENG == 'eevee':
    sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.eevee.taa_render_samples = SAMPLES; sc.eevee.use_shadows = True
    try: sc.eevee.use_raytracing = True
    except Exception: pass
else:
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    sc.render.threads_mode = 'FIXED'; sc.render.threads = THREADS
t0 = time.time(); bpy.ops.render.render(write_still=True); print(f'film_still: {OUT} {VAR} {ENG} {time.time() - t0:.1f} s')
