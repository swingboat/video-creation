"""Audit baked contact, reach, camera framing and pencil/body clearance."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
motion=json.loads((ROOT/'outputs/checks/bunny/motion-audit.json').read_text())
scene=bpy.context.scene
errors=[];slip=0;grip_error=0;min_pen_clearance=100;clipped=[];collisions=[]
last={};body_meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Rabbit ') and 'drawing' not in o.name]
for state in motion['states']:
    fr=state['frame'];t=state['time'];scene.frame_set(fr)
    if max(state['arm_errors'])>.001:errors.append('Arm reach '+str(fr))
    for foot in state['feet']:
        if foot['leg_overreach']>.001:errors.append('Leg reach '+str(fr))
        o=bpy.data.objects['Rabbit ankle '+str(foot['side'])]
        if foot['stance'] and last.get(foot['side'],{}).get('stance'):
            delta=(o.location-Vector(last[foot['side']]['position'])).length;slip=max(slip,delta)
        last[foot['side']]=foot
    if 3.01<=t<=14.14:
        box=bpy.data.objects['Rabbit carried pink block'];right=box.rotation_quaternion@Vector((1,0,0))
        for side in [-1,1]:
            expected=box.location+right*side*.225+Vector((0,0,.015))
            err=(bpy.data.objects['Rabbit wrist '+str(side)].location-expected).length;grip_error=max(grip_error,err)
    if t>=15.8:
        pen=bpy.data.objects['Rabbit pencil • grip constrained']
        for name,radii in [('Rabbit rig • head',(.283,.233,.273)),('Rabbit rig • chest',(.278,.223,.338))]:
            inv=bpy.data.objects[name].matrix_world.inverted();vals=[]
            for k in range(16):
                pt=inv@(pen.matrix_world@Vector((0,0,.10+k*.042)))
                vals.append(math.sqrt(sum((pt[j]/radii[j])**2 for j in range(3))))
            clearance=min(vals);min_pen_clearance=min(min_pen_clearance,clearance)
            if clearance<.98:collisions.append({'frame':fr,'part':name,'ellipsoid_clearance':clearance})
    for o in body_meshes:
        # Once released, the box is a set prop; a moving close-up may crop it.
        # The character and held box must remain framed throughout the action.
        if o.name=='Rabbit carried pink block' and t>14.25:continue
        coords=[world_to_camera_view(scene,scene.camera,o.matrix_world@Vector(c)) for c in o.bound_box]
        if any(p.z>0 and (p.x<-.02 or p.x>1.02 or p.y<-.02 or p.y>1.02) for p in coords):
            clipped.append({'frame':fr,'object':o.name});break

if slip>.0001:errors.append('Stance foot sliding')
if grip_error>.004:errors.append('Box hand separation')
if collisions:errors.append('Pencil intersects head/body')
if clipped:errors.append('Rabbit clipped by camera')
report={'passed':not errors,'errors':list(dict.fromkeys(errors)),'max_stance_slide':slip,'max_box_grip_error':grip_error,'minimum_pencil_ellipsoid_clearance':min_pen_clearance,'pencil_collisions':collisions,'camera_clipped_frames':clipped,'framing_scope':'Character at all times; box while carried. Set props may be cropped during camera orbit.','frame_count':len(motion['states']),'max_arm_overreach':motion['max_arm_overreach'],'max_leg_overreach':motion['max_leg_overreach']}
(ROOT/'outputs/checks/bunny/contact-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in {'pencil_collisions','camera_clipped_frames'}},indent=2),flush=True)
if errors:raise RuntimeError('Rabbit contact / camera audit failed')
