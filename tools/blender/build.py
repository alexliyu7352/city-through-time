"""Build a landmark's detailed model in Blender and write it as glTF, and optionally a still of it (docs/MUSEUM.md "Detailed
models"). Blender's path is local/config.json `blender`; run headless:
    <blender> -b --factory-startup --python tools/blender/build.py -- --kind amphitheatre [--landmark L.json] [--spec spec.json]
        --out model.glb [--theta -22] [--render still.png --cam az,el,d,fov,tx,ty,tz --size 1672x941 --samples 48]
--landmark: the landmark as the film has it (city.yaml): the kind takes the sizes the film gives (its from_landmark); --spec: the
page's own settings over those (a museum page's `detailed.spec`); what neither gives is the kind's default, an estimate.
--cam: as a museum page's viewpoint (az 0 south of the target, 90 east; el degrees up; d metres; fov vertical degrees; the target
tx east, ty north, tz up, metres). The glTF keeps one node per part (its object's name), metres, y up."""
import json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Euler, Vector

import kit

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = sorted(f[:-3] for f in os.listdir(HERE) if f.endswith('.py') and f not in ('build.py', 'kit.py'))   # (a kind: a module here with build(spec) and from_landmark(L))


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    o = {'kind': None, 'landmark': None, 'spec': None, 'out': None, 'theta': 0.0, 'render': None, 'cam': None, 'size': '1672x941', 'samples': 48}
    i = 0
    while i < len(a):
        k = a[i].lstrip('-'); o[k] = a[i + 1]; i += 2
    return o


def camera(cam, size):
    az, el, d, fov, tx, ty, tz = map(float, cam.split(','))
    w, h = map(int, size.split('x'))
    A, E = math.radians(az), math.radians(el)
    pos = Vector((tx + d * math.sin(A) * math.cos(E), ty - d * math.cos(A) * math.cos(E), tz + d * math.sin(E)))
    c = bpy.data.cameras.new('cam'); c.sensor_fit = 'VERTICAL'; c.angle_y = math.radians(fov); c.clip_start = .5; c.clip_end = 20000
    o = bpy.data.objects.new('cam', c); bpy.context.collection.objects.link(o); o.location = pos
    o.rotation_euler = (Vector((tx, ty, tz)) - pos).to_track_quat('-Z', 'Y').to_euler()
    sc = bpy.context.scene; sc.camera = o; sc.render.resolution_x, sc.render.resolution_y = w, h


def studio(samples):
    """a bright neutral room: a sky light, a sun high from the south-east (the museum page's key), a light floor"""
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(samples); sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('room'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.82, .84, .87, 1); w.node_tree.nodes['Background'].inputs[1].default_value = .9
    sun = bpy.data.lights.new('key', 'SUN'); sun.energy = 3.2; sun.angle = math.radians(3)
    so = bpy.data.objects.new('key', sun); bpy.context.collection.objects.link(so)
    az, el = math.radians(135), math.radians(45)   # (from the south-east, 45 degrees up: the light's +z toward it)
    so.rotation_euler = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))).to_track_quat('Z', 'Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, 0)); fl = bpy.context.active_object; fl.name = '_floor'
    fl.data.materials.append(kit.material('floor', (.72, .71, .69)))


def main():
    o = args()
    if o['kind'] not in KINDS: sys.exit(f'build: --kind one of {", ".join(KINDS)}')
    kit.reset()
    mod = __import__(o['kind'])
    spec = {**(mod.from_landmark(json.load(open(o['landmark']))) if o['landmark'] else {}), **(json.load(open(o['spec'])) if o['spec'] else {})}
    print('build: spec ' + json.dumps(spec, sort_keys=True))
    parts = mod.build(spec)
    for p in parts: p.rotation_euler = (0, 0, math.radians(float(o['theta'])))
    tris = sum(sum(len(f.vertices) - 2 for f in p.data.polygons) for p in parts)
    print(f"build: {o['kind']}: {len(parts)} parts, {tris} triangles: " + ', '.join(p.name for p in parts))
    if o['out']:
        for ob in bpy.data.objects: ob.select_set(ob in parts)
        bpy.ops.export_scene.gltf(filepath=o['out'], export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                                  export_normals=True, export_texcoords=False, export_materials='EXPORT',
                                  export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
                                  export_draco_position_quantization=14, export_draco_normal_quantization=8)   # (Draco: three's DRACOLoader reads it; a page of a few MB, not tens)
        print(f"build: wrote {o['out']} ({os.path.getsize(o['out']) / 1e6:.1f} MB)")
    if o['render']:
        studio(o['samples']); camera(o['cam'], o['size'])
        bpy.context.scene.render.filepath = o['render']; bpy.ops.render.render(write_still=True)
        print(f"build: rendered {o['render']}")


main()
