import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from motion import *
r=Path(__file__).resolve().parents[1];ball=bpy.data.objects['Basketball authoritative trajectory'];data=[]
for f in range(1,481):
 t=(f-1)/24;ball.location=ball_at(t);ball.keyframe_insert('location',frame=f);data.append({'frame':f,'t':t,'ball':ball_at(t),'root':hero_root(t),'clock':game_clock(t)})
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(r/'public/rukawa.blend'));(r/'docs/trajectory.json').write_text(json.dumps(data,indent=2))
