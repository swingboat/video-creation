"""Record the saved scene's actual object hierarchy without modifying the .blend."""
import bpy,json,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;scene.frame_set(1)
items=[]
for o in sorted(scene.objects,key=lambda x:x.name):
    item={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'location':list(o.location),'world_location':list(o.matrix_world.translation),'scale':list(o.scale)}
    if o.type=='MESH':item.update({'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'materials':[s.material.name if s.material else None for s in o.material_slots],'shape_keys':[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []})
    if o.data and hasattr(o.data,'materials'):item['materials']=[m.name if m else None for m in o.data.materials]
    if o.type=='LIGHT':item.update({'light_type':o.data.type,'energy_at_frame_1':o.data.energy})
    if o.animation_data and o.animation_data.action:item['action']=o.animation_data.action.name
    items.append(item)
report={'blend_sha256':hashlib.sha256((ROOT/'public/bottle-storm.blend').read_bytes()).hexdigest(),'frame':1,'objects':len(items),'object_types':dict(Counter(o.type for o in scene.objects)),'camera':scene.camera.name,'units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length},'render':{'engine':scene.render.engine,'samples':scene.cycles.samples,'seed':scene.cycles.seed,'animated_seed':scene.cycles.use_animated_seed,'motion_blur_shutter':scene.render.motion_blur_shutter,'denoise':scene.cycles.use_denoising,'max_bounces':scene.cycles.max_bounces,'transmission_bounces':scene.cycles.transmission_bounces,'view_transform':scene.view_settings.view_transform},'items':items}
(ROOT/'docs/scene-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='items'},ensure_ascii=False,indent=2))
