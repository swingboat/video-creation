"""Read actual baked scene for asset boundaries, shooting line, contacts and framing."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=Path(__file__).resolve().parents[1];sc=bpy.context.scene
report={'objects':len(bpy.data.objects),'external_dependencies':[],'shooting_framing':[],'planted_shoe_min_z':[]}
for font in bpy.data.fonts:
 if not font.filepath or font.filepath=='<builtin>':continue
 p=Path(bpy.path.abspath(font.filepath)).resolve()
 if not p.is_relative_to(r):report['external_dependencies'].append(str(p))
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  p=Path(bpy.path.abspath(im.filepath)).resolve()
  if not p.is_relative_to(r):report['external_dependencies'].append(str(p))
for f in range(169,227):
 sc.frame_set(f);ball=bpy.data.objects['Basketball authoritative trajectory'];pos=world_to_camera_view(sc,sc.camera,ball.matrix_world.translation)
 report['shooting_framing'].append({'frame':f,'ball_screen':[round(v,4) for v in pos]})
 assert 0<pos.x<1 and .05<pos.y<.98,(f,tuple(pos))
for f in range(151,184):
 sc.frame_set(f)
 for s in [-1,1]:
  ankle=bpy.data.objects[f'RUKAWA 11 ankle {s}'];z=ankle.matrix_world.translation.z;report['planted_shoe_min_z'].append(round(z,5))
assert not report['external_dependencies'];assert min(report['planted_shoe_min_z'])>=-.005
sc.frame_set(217);ball=bpy.data.objects['Basketball authoritative trajectory'];pos=ball.matrix_world.translation
report['three_point_distance']=math.hypot(pos.x,pos.y-12);assert report['three_point_distance']>6.75
report['passed']=True;(r/'outputs/checks/scene-audit.json').write_text(json.dumps(report,indent=2));print('SCENE_AUDIT_PASSED',report['three_point_distance'])
