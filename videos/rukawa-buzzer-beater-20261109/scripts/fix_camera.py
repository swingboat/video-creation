import bpy,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from motion import *
r=Path(__file__).resolve().parents[1];sc=bpy.context.scene;cam=sc.camera
for f in range(148,227):
 t=(f-1)/24
 if not 6.1<=t<9.4:continue
 sc.frame_set(f);hx,hy,hz=hero_root(t);target=(hx,hy+.12,1.55+hz+ease((t-8.8)/.6));cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('rotation_euler',frame=f)
sc.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(r/'public/rukawa.blend'))
