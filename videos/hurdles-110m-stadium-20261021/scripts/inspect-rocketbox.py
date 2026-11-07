import bpy,json
from pathlib import Path
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(Path.cwd()/'sources/research/rocketbox/Male_Adult_01.fbx'))
j=[]
for o in bpy.data.objects:
 d={'name':o.name,'type':o.type,'scale':list(o.scale),'rotation':list(o.rotation_euler),'parent':o.parent.name if o.parent else None}
 if o.type=='MESH':d.update(vertices=len(o.data.vertices),materials=[m.name for m in o.data.materials],bounds=[list(o.matrix_world@__import__('mathutils').Vector(v)) for v in o.bound_box])
 if o.type=='ARMATURE':d['bones']=[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in o.data.bones]
 j.append(d)
Path('outputs/checks/rocketbox-inspection.json').write_text(json.dumps(j,indent=2));print([(o.name,o.type) for o in bpy.data.objects])
