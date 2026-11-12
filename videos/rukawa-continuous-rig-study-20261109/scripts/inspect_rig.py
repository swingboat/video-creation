import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(r/'public/models/human-base.glb'))
a=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
data={'objects':[{'name':o.name,'type':o.type,'matrix':[list(v) for v in o.matrix_world],'dimensions':list(o.dimensions)} for o in bpy.context.scene.objects],'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in a.data.bones}}
(r/'outputs/checks/source-rig.json').write_text(json.dumps(data,indent=2));print('ARM',a.name,'BONES',len(a.data.bones),flush=True)
for k in ['root','pelvis','spine01','spine02','head','upperleg01.L','upperleg02.L','lowerleg01.L','lowerleg02.L','foot.L','upperarm01.L','upperarm02.L','lowerarm01.L','lowerarm02.L','hand.L']:
 if k in data['bones']:print(k,data['bones'][k])
