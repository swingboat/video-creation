import bpy,json,math
from pathlib import Path
from mathutils import Quaternion
R=Path(__file__).resolve().parents[1];o=[];min_dot=1.
for arm in [o for o in bpy.context.scene.objects if o.type=='ARMATURE']:
 a=arm.animation_data.action;channels={}
 for l in a.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     if fc.data_path.endswith('rotation_quaternion'):channels.setdefault(fc.data_path,{})[fc.array_index]=fc
 for path,cs in channels.items():
  prev=None
  for f in range(1,151):
   q=Quaternion([cs[i].evaluate(f) for i in range(4)]).normalized()
   if prev:
    dot=q.dot(prev);min_dot=min(min_dot,dot);angle=math.degrees(2*math.acos(min(1,abs(dot))))
    if angle>15:o.append([round(angle,2),f,arm.name,path])
   prev=q
out={'min_dot':min_dot,'largest':sorted(o,reverse=True)[:30]};(R/'outputs/checks/rotation-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
