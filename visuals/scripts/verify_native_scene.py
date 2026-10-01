"""Blender background verification: load native scene, export GLB and render on GPU.

Arguments after -- are SOURCE.blend OUTPUT_DIRECTORY. Retained sources are read-only.
"""
from pathlib import Path
import hashlib
import json
import sys
import bpy

source, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()))
scene = bpy.context.scene
preferences = bpy.context.preferences.addons['cycles'].preferences
devices = []
for backend in ('OPTIX', 'CUDA'):
    try:
        preferences.compute_device_type = backend
        preferences.get_devices()
        devices = [d for d in preferences.devices if d.type == backend]
        if devices:
            break
    except (TypeError, RuntimeError):
        continue
if not devices:
    raise RuntimeError('No supported GPU found; this verification requires a real GPU render')
for device in preferences.devices:
    device.use = device in devices
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.render.resolution_percentage = 25
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str((output / 'native-scene-gpu.png').resolve())
bpy.ops.render.render(write_still=True)
meshes = [o for o in scene.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
product = [o for o in meshes if any(c.name[:2] in ('01', '02', '03', '04', '05') for c in o.users_collection)]
if not product:
    raise RuntimeError('Product collections missing from native scene')
for obj in product:
    obj.select_set(True)
glb = output / 'native-scene-roundtrip.glb'
bpy.ops.export_scene.gltf(filepath=str(glb.resolve()), export_format='GLB', use_selection=True, export_apply=False, export_extras=True)
record = {
    'passed': True, 'source': source.name,
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'blender': bpy.app.version_string, 'backend': backend,
    'gpu': [d.name for d in devices], 'product_meshes': len(product),
    'render': 'native-scene-gpu.png', 'export': glb.name,
    'export_bytes': glb.stat().st_size,
    'scope': 'Actual retained native scene import, GPU render and GLB export; no physical qualification',
}
(output / 'native-scene-validation.json').write_text(json.dumps(record, indent=2), encoding='utf-8', newline='\n')
print(json.dumps(record))
