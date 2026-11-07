"""Audit evaluated native fish poses, water/glass/sand bounds and continuity."""
import bpy,math,json,hashlib
from mathutils.bvhtree import BVHTree
from mathutils import Vector
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
paths=json.loads((ROOT/'docs/fish-paths.json').read_text())
profile=[(-4.04,.01),(-4.02,.43),(-3.98,.91),(-3.90,1.24),(-3.77,1.47),(-3.55,1.58),(-3.25,1.60),(1.90,1.60),(2.17,1.57),(2.42,1.47),(2.65,1.30),(2.86,1.07),(3.04,.80),(3.22,.58),(3.43,.44),(3.70,.425),(4.08,.425)]
def radii(x):
    result=np.zeros_like(x)
    for a,b in zip(profile,profile[1:]):
        mask=(x>=a[0])&(x<=b[0]);u=np.clip((x-a[0])/(b[0]-a[0]),0,1);u=u*u*(3-2*u)
        result[mask]=(a[1]*(1-u)+b[1]*u)[mask]
    return result
modes=[(.17,2.5,.38,2.6),(.08,4.2,-1.2,3.7),(.045,7.3,2.,5.1)]
meshes=[bpy.data.objects['Fish v3 %02d • flexible body and fins'%i] for i in range(9)]
minimum={'glass':10.,'sand':10.,'water':10.};worst={};errors=[]
centers=[];heading=[];tail_excursion=[];head_excursion=[]
penetrations=[];max_penetration=0.0
body_faces=[tuple(p.vertices) for p in meshes[0].data.polygons[:1922]]
for fr in range(1,481):
    bodies=[]
    scene.frame_set(fr);graph=bpy.context.evaluated_depsgraph_get();t=(fr-1)/24
    for i,obj in enumerate(meshes):
        ev=obj.evaluated_get(graph);me=ev.to_mesh();co=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',co);co=co.reshape(-1,3)
        mat=np.array(ev.matrix_world);world=co@mat[:3,:3].T+mat[:3,3];x,y,z=world.T;r=radii(x)
        bodies.append(world[:1952].copy())
        glass=r-.075-np.sqrt(y*y+(z-1.75)**2)
        sand=z-(1.75-np.sqrt(np.maximum(.04,(r-.11)**2-y*y))+.045)
        env=.18+.82*math.sin(math.pi*min(1,t/14))**.8
        fade=np.minimum(1,np.maximum(0,(x+3.98)/.5))*np.minimum(1,np.maximum(.05,(3.55-x)/1.2))*(.7+.3*np.maximum(0,1-(y/(r-.075))**2))
        wave=1.6+fade*env*sum(a*np.sin(kx*x+ky*y-w*t) for a,kx,ky,w in modes)
        water=wave-z
        for name,values in [('glass',glass),('sand',sand),('water',water)]:
            m=float(values.min())
            if m<minimum[name]:minimum[name]=m;worst[name]=[fr,i]
        # Pose weights must blend exactly two adjacent cyclic phases and sum to one.
        weights=[k.value for k in obj.data.shape_keys.key_blocks if k.name.startswith('Swim phase')]
        if abs(sum(weights)-1)>1e-5 or min(weights)<-1e-6 or max(weights)>1.00001:errors.append('Invalid phase weights %d/%d'%(fr,i))
        if fr<=96 and i==0:
            tail_excursion.append(float(co[np.argmin(co[:,0]),1]));head_excursion.append(float(co[np.argmax(co[:,0]),1]))
        ev.to_mesh_clear()
    for i in range(9):
        for j in range(i):
            a=bodies[i];b=bodies[j]
            if np.any(a.max(axis=0)<b.min(axis=0)) or np.any(b.max(axis=0)<a.min(axis=0)):continue
            tree=BVHTree.FromPolygons([Vector(p) for p in b],body_faces,all_triangles=False)
            depth=0.
            for p in a:
                co,normal,index,distance=tree.find_nearest(Vector(p))
                if co is not None and (Vector(p)-co).dot(normal)<-.001:depth=max(depth,distance)
            if depth>.002:
                penetrations.append({'frame':fr,'fish':[j,i],'depth':depth});max_penetration=max(max_penetration,depth)
for spec in paths['fish']:
    p=np.array([s['p'] for s in spec['samples']]);v=np.diff(p,axis=0)*24
    maxstep=float(np.linalg.norm(np.diff(p,axis=0),axis=1).max())
    minforward=1.;maxyaw=0
    for k,s in enumerate(spec['samples'][:-1]):
        direction=np.array([math.cos(s['yaw'])*math.cos(s['pitch']),math.sin(s['yaw'])*math.cos(s['pitch']),-math.sin(s['pitch'])])
        minforward=min(minforward,float(v[k]@direction/np.linalg.norm(v[k])))
        d=spec['samples'][k+1]['yaw']-s['yaw'];maxyaw=max(maxyaw,abs(math.atan2(math.sin(d),math.cos(d)))*24)
    heading.append({'fish':spec['id'],'minimum_forward_alignment':minforward,'max_frame_displacement':maxstep,'max_turn_rad_per_second':maxyaw})
    if minforward<.98:errors.append('Fish does not face its velocity')
    if maxstep>.08:errors.append('Abrupt fish translation')
for name,m in minimum.items():
    if m<.004:errors.append('Fish penetrates '+name)
if penetrations:errors.append('Fish body intersection')
report={'body_intersections':penetrations,'max_body_penetration':max_penetration,'passed':not errors,'errors':errors,'blend_sha256':hashlib.sha256((ROOT/'public/bottle-storm.blend').read_bytes()).hexdigest(),'frames':480,'fish':9,'min_clearance_world_units':minimum,'closest_frames':worst,'spacing':paths['spacing'],'heading':heading,'tail_lateral_range':max(tail_excursion)-min(tail_excursion),'head_lateral_range':max(head_excursion)-min(head_excursion),'note':'Bounds checked on every evaluated vertex, including fins. Projected overlaps can occur between fish at different depths.'}
(ROOT/'outputs/checks/fish/motion-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
if errors:raise RuntimeError('Fish motion audit failed')
