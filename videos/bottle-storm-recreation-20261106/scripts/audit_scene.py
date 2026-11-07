"""Validate actual saved geometry and native animation, without rebuilding the scene."""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
boat=bpy.data.objects['Schooner • four-point baked buoyancy']
water=bpy.data.objects['Ocean • closed volume and analytic waves']
results=[]
errors=[]
for frame in [1,49,97,145,169,217,265,313,336,409,469,480]:
    scene.frame_set(frame)
    graph=bpy.context.evaluated_depsgraph_get()
    evaluated=water.evaluated_get(graph)
    x,y=boat.location.x,boat.location.y
    samples=[]
    for xx,yy in [(x-.73,y),(x+.73,y),(x,y-.23),(x,y+.23)]:
        hit,point,normal,index=evaluated.ray_cast(Vector((xx,yy,5)),Vector((0,0,-1)))
        if not hit:errors.append('Water ray missed frame '+str(frame));continue
        samples.append(point.z)
    if len(samples)!=4:continue
    delta=abs(sum(samples)/4-.05-boat.location.z)
    if delta>.012:errors.append('Buoyancy mismatch frame '+str(frame))
    results.append({'frame':frame,'sampled_surface_heights':samples,'boat_z':boat.location.z,'height_error':delta,'pitch_degrees':math.degrees(boat.rotation_euler.y),'roll_degrees':math.degrees(boat.rotation_euler.x)})

external=[]
for image in bpy.data.images:
    if image.source!='FILE' or not image.filepath:continue
    p=Path(bpy.path.abspath(image.filepath)).resolve()
    if not image.packed_file and not p.is_relative_to(ROOT):external.append(str(p))
if external:errors.append('External image dependencies')
report={'passed':not errors,'errors':errors,'blend_sha256':hashlib.sha256((ROOT/'public/bottle-storm.blend').read_bytes()).hexdigest(),'objects':len(bpy.data.objects),'engine':scene.render.engine,'fps':scene.render.fps,'frames':scene.frame_end-scene.frame_start+1,'size':[scene.render.resolution_x,scene.render.resolution_y],'external_image_dependencies':external,'wave_shape_keys':list(water.data.shape_keys.key_blocks.keys()),'samples':results,'geometry_note':'Buoyancy checked against ray casts on actual evaluated animated water mesh.'}
(ROOT/'outputs/checks/scene-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'passed':report['passed'],'errors':errors,'max_height_error':max(r['height_error'] for r in results)},indent=2),flush=True)
if errors:raise RuntimeError('Scene audit failed')
