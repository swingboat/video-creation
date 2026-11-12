import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];records=json.loads((R/'docs/motion-trace.json').read_text());scene=bpy.context.scene
arms=[o for o in scene.objects if o.type=='ARMATURE'];base=bpy.data.objects['Shooter 11 / deform rig'];rest={b.name:b.head_local.copy() for b in base.data.bones};palm={s:(rest['finger3-1.'+s]-rest['wrist.'+s])*.52 for s in ['L','R']}
last={};max_jump={};planted={};palmerr=[];ankerr=[];scaleerr=0.;enderr=0.;solez=[];solechange=[];perframe=[];lastquat={};mindot=1.;maxangle=0.;rotation_peaks=[];plant_min=[]
for rec in records:
 scene.frame_set(rec['frame']);bpy.context.view_layer.update();frame={}
 for ar in rec['actors']:
  arm=bpy.data.objects[ar['name']+' / deform rig'];M=arm.matrix_world;wp={}
  for side in ['L','R']:
   for part in ['wrist.','foot.','lowerarm01.','lowerleg01.']:
    b=arm.pose.bones[part+side];key=arm.name+'/'+part+side;v=M@b.head;wp[part+side]=list(v)
    if key in last:max_jump[key]=max(max_jump.get(key,0),(v-last[key]).length)
    last[key]=v
   foot=M@arm.pose.bones['foot.'+side].head;ankerr.append((foot-Vector(ar['feet'][side]['ankle'])).length)
   for pn,cn in [('lowerleg02.','foot.'),('lowerarm02.','wrist.')]:enderr=max(enderr,(arm.pose.bones[pn+side].tail-arm.pose.bones[cn+side].head).length)
   if ar['hand_contacts']:
    wb=arm.pose.bones['wrist.'+side];p=M@(wb.matrix@base.data.bones['wrist.'+side].matrix_local.inverted()@(rest['wrist.'+side]+palm[side]));palmerr.append((p-Vector(ar['hand_contacts'][side]['palm'])).length)
  for b in arm.pose.bones:
   scaleerr=max(scaleerr,max(abs(x-1) for x in b.scale));q=b.rotation_quaternion.normalized();key=arm.name+b.name
   if key in lastquat:
    dot=q.dot(lastquat[key]);mindot=min(mindot,dot);angle=2*math.acos(min(1,abs(dot)));maxangle=max(maxangle,angle)
    if angle>.3:rotation_peaks.append([round(math.degrees(angle),3),rec['frame'],key])
   lastquat[key]=q.copy()
  # Evaluate actual weighted shoe vertices, not only planned contacts.
  shoe=next(o for o in scene.objects if o.name.startswith(ar['name']+' / Athleteshoes05'))
  dg=bpy.context.evaluated_depsgraph_get();ev=shoe.evaluated_get(dg);me=ev.to_mesh()
  for side,sign in [('L',1),('R',-1)]:
   ids=[v.index for v in shoe.data.vertices if v.co.x*sign>0 and v.co.z<.004]
   if not ids:ids=[v.index for v in shoe.data.vertices if v.co.x*sign>0 and v.co.z<.015]
   vs=[ev.matrix_world@me.vertices[i].co for i in ids];key=arm.name+side
   if ar['feet'][side]['planted']:
    solez.extend(v.z-ar['root'][2] for v in vs);plant_min.append(min(v.z-ar['root'][2] for v in vs))
    if key in planted:solechange.extend((a-b).length for a,b in zip(vs,planted[key]))
    planted[key]=vs
   else:planted.pop(key,None)
  ev.to_mesh_clear();frame[ar['name']]=wp
 perframe.append(frame)
report={'frames':len(records),'actors':len(arms),'bones_each':len(base.data.bones),'palm_target_error_max_m':max(palmerr),'ankle_target_error_max_m':max(ankerr),'segment_joint_gap_max_m':enderr,'pose_scale_error_max':scaleerr,'planted_shoe_vertex_step_max_m':max(solechange),'planted_shoe_selected_vertex_z_range_m':[min(solez),max(solez)],'largest_rotation_steps':sorted(rotation_peaks,reverse=True)[:15],'minimum_adjacent_quaternion_dot':mindot,'max_local_rotation_step_degrees':math.degrees(maxangle),'max_abs_planted_sole_bottom_z_m':max(abs(z) for z in plant_min),'largest_joint_steps_m':sorted(max_jump.items(),key=lambda x:-x[1])[:12],'asset_paths':{'linked_libraries':[l.filepath for l in bpy.data.libraries],'fonts':[{'name':f.name,'filepath':f.filepath,'packed':bool(f.packed_file)} for f in bpy.data.fonts],'images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]},'scope':'Numerical rig/contact checks only; naturalness and approved anime appearance require visual review.'}
(R/'outputs/checks/rig-audit.json').write_text(json.dumps(report,indent=2));(R/'outputs/checks/evaluated-joints.json').write_text(json.dumps(perframe));print(json.dumps(report,indent=2))
