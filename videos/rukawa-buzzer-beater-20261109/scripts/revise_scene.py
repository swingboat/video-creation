import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from motion import *
r=Path(__file__).resolve().parents[1];sc=bpy.context.scene
sc.view_settings.exposure=-.25
for ob in bpy.data.objects:
 if ob.type=='LIGHT' and ob.name.startswith('Overhead arena softbox'):ob.data.energy=1800
 if ob.type=='LIGHT' and ob.name.startswith('Rukawa face key'):ob.data.energy=300
 if ob.name.startswith('Center emblem'):ob.rotation_euler.z=0
 if ob.name.startswith('Courtside banner'):ob.rotation_euler.z=-ob.rotation_euler.z

def ik(a,b,l1,l2,pole):
 a,b=Vector(a),Vector(b);v=b-a;d=min(v.length,l1+l2-.001);vn=v.normalized();h=(l1*l1-l2*l2+d*d)/(2*d);q=Vector(pole);q=(q-vn*q.dot(vn)).normalized();return a+vn*h+q*math.sqrt(max(.00001,l1*l1-h*h))
def key(o,p,f):o.keyframe_insert(data_path=p,frame=f)
def seg(o,a,b,f):
 a,b=Vector(a),Vector(b);o.location=a;o.rotation_quaternion=(b-a).to_track_quat('Z','Y');o.scale.z=(b-a).length
 for p in ['location','rotation_quaternion','scale']:key(o,p,f)
ball=bpy.data.objects['Basketball authoritative trajectory'];cam=sc.camera;rt=bpy.data.objects['RUKAWA 11'];defender=bpy.data.objects['DEFENDER 7'];data=[]
for f in range(1,481):
 sc.frame_set(f);t=(f-1)/24;root=hero_root(t);bp=ball_at(t);ball.location=bp;key(ball,'location',f)
 hx,hy,hz=root
 if 6.1<=t<9.4:
  target=(hx,hy+.12,1.55+hz+ease((t-8.8)/.6));cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;key(cam,'rotation_euler',f);key(cam.data,'lens',f)
 if t>14:
  defender.location.x=hx+.2-3.2*ease((t-14)/1.2);key(defender,'location',f)
 for si,s in enumerate([-1,1]):
  hand=bpy.data.objects[f'RUKAWA 11 wrist {s}'];shoulder=(s*.23,0,1.48);wrist=tuple(hand.location)
  if t>=11.4:wrist=mix((s*.32,.09,1.02),(s*.29,.10,.99),ease((t-15.3)/1.4));hand.location=wrist;key(hand,'location',f)
  elbow=ik(shoulder,wrist,.34,.32,(s*.35,.8,-.3) if 6.5<t<10.5 else (s*.4,-.2,-.7))
  seg(bpy.data.objects[f'RUKAWA 11 {s} upper'],shoulder,elbow,f);seg(bpy.data.objects[f'RUKAWA 11 {s} fore'],elbow,wrist,f)
  eo=bpy.data.objects['RUKAWA 11elbow'+('' if si==0 else '.001')];eo.location=elbow;key(eo,'location',f)
  hand.rotation_quaternion=(Vector(wrist)-elbow).to_track_quat('Z','Y')
  if 9<=t<10.7 and s==1:hand.rotation_quaternion=Vector((0,.9,-.3)).to_track_quat('Z','Y')
  key(hand,'rotation_quaternion',f)
 data.append({'frame':f,'t':t,'ball':bp,'root':root,'clock':game_clock(t)})
sc.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(r/'public/rukawa.blend'));(r/'docs/trajectory.json').write_text(json.dumps(data,indent=2))
