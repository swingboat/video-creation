"""Load the preserved original scene, add articulated toy animation, bake all keys."""
import bpy
import sys
import math
import json
from pathlib import Path
from mathutils import Vector,Quaternion,Euler

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bunny_motion as M

scene=bpy.context.scene
scene.frame_set(1)
scene.frame_end=M.FRAMES
scene.cycles.samples=32
scene.cycles.adaptive_threshold=.035
scene.cycles.seed=20261106
scene.cycles.use_animated_seed=False
scene.render.fps=M.FPS
if hasattr(scene.render,'use_motion_blur'):scene.render.use_motion_blur=True
scene.render.motion_blur_shutter=.30

def material(name,color,rough=.58):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough
    return m

ivory=bpy.data.materials['Warm porcelain'].copy();ivory.name='Rabbit warm porcelain';ivory.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value=.045
pink=bpy.data.materials['Blush pink fabric'];teal=bpy.data.materials['Muted blue'];ink=bpy.data.materials['Ink']
blue=material('Rabbit drawing blue',(.075,.27,.40),.78)
white=material('Eye catchlights',(.96,.93,.83),.28)
new_objects=[]

def empty(name,parent=None,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.parent=parent;o.location=loc;new_objects.append(o);return o

def sphere(name,loc,scale,mat,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale;o.parent=parent;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    new_objects.append(o);return o

def cylinder(name,z,r,depth,mat,parent,r1=None,r2=None):
    if r1 is None:bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=(0,0,z))
    else:bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=r1,radius2=r2,depth=depth,location=(0,0,z))
    o=bpy.context.object;o.name=name;o.parent=parent;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def curve(name,points,r,mat):
    cu=bpy.data.curves.new(name+' path','CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for p,v in zip(sp.points,points):p.co=(*v,1)
    o=bpy.data.objects.new(name,cu);scene.collection.objects.link(o);o.data.materials.append(mat);return o

def key(o,frame,loc=None,quat=None,scale=None):
    if loc is not None:o.location=loc;o.keyframe_insert(data_path='location',frame=frame)
    if quat is not None:o.rotation_mode='QUATERNION';o.rotation_quaternion=quat;o.keyframe_insert(data_path='rotation_quaternion',frame=frame)
    if scale is not None:o.scale=scale;o.keyframe_insert(data_path='scale',frame=frame)

def limb(o,a,b,r,frame):
    d=b-a;key(o,frame,(a+b)/2,d.to_track_quat('Z','Y'),(r,r,d.length/2+r*.32))

# Preserve all bottle / bedroom assets; replace only the static rabbit and pencil.
for o in list(bpy.data.objects):
    if o.name=='Porcelain bunny' or o.name.startswith('Bunny ') or o.name in {'Blue pencil','Pencil tip'}:
        bpy.data.objects.remove(o,do_unlink=True)

root=empty('Rabbit rig • root')
pelvis=empty('Rabbit rig • pelvis')
chest=empty('Rabbit rig • chest')
head=empty('Rabbit rig • head')
sphere('Rabbit soft body',(0,0,0),(.25,.195,.31),ivory,chest)
sphere('Rabbit tummy',(0,-.153,-.015),(.19,.065,.235),ivory,chest)
sphere('Rabbit cotton tail',(0,.18,-.10),(.10,.09,.105),ivory,chest)
sphere('Rabbit head',(0,0,0),(.255,.205,.245),ivory,head)
sphere('Rabbit muzzle left',(-.052,-.187,-.066),(.070,.040,.052),ivory,head)
sphere('Rabbit muzzle right',(.052,-.187,-.066),(.070,.040,.052),ivory,head)
sphere('Rabbit nose',(0,-.223,-.045),(.024,.015,.017),pink,head)
eyes=[];eye_glints=[]
for side in [-1,1]:
    eye=sphere('Rabbit eye '+str(side),(side*.094,-.190,.010),(.021,.015,.025),ink,head);eyes.append(eye)
    eye_glints.append(sphere('Rabbit eye glint '+str(side),(side*.091,-.205,.018),(.0055,.004,.006),white,head))
ear_controls=[]
for side in [-1,1]:
    ear=empty('Rabbit ear base '+str(side),head,(side*.125,.01,.175));ear_controls.append((side,ear))
    sphere('Rabbit ear '+str(side),(0,.005,.23),(.072,.061,.29),ivory,ear)
    sphere('Rabbit inner ear '+str(side),(0,-.050,.24),(.031,.012,.19),pink,ear)
for side in [-1,1]:sphere('Rabbit blue bow '+str(side),(side*.078,-.185,.145),(.092,.039,.05),teal,chest)
sphere('Rabbit bow knot',(0,-.201,.145),(.037,.031,.039),teal,chest)

arms={};legs={};hands={};feet={}
for side in [-1,1]:
    arms[side]=[sphere('Rabbit upper arm '+str(side),(0,0,0),(1,1,1),ivory),sphere('Rabbit forearm '+str(side),(0,0,0),(1,1,1),ivory)]
    legs[side]=[sphere('Rabbit thigh '+str(side),(0,0,0),(1,1,1),ivory),sphere('Rabbit shin '+str(side),(0,0,0),(1,1,1),ivory)]
    hand=empty('Rabbit wrist '+str(side));hands[side]=hand
    sphere('Rabbit mitten '+str(side),(0,0,0),(.072,.073,.085),ivory,hand)
    sphere('Rabbit thumb '+str(side),(side*.047,.018,-.004),(.033,.041,.045),ivory,hand)
    foot=empty('Rabbit ankle '+str(side));feet[side]=foot
    sphere('Rabbit planted paw '+str(side),(0,-.045,0),(.125,.19,.101),ivory,foot)

box=min((o for o in bpy.data.objects if o.name.startswith('Painted toy block')),key=lambda o:(o.location-Vector((4.75,-.92,.18))).length)
box.name='Rabbit carried pink block'
pen=empty('Rabbit pencil • grip constrained')
pen.scale=(M.PEN_SCALE,)*3
cylinder('Pencil wood tip',.055,.028,.11,bpy.data.materials['Honey oak'],pen,r1=0,r2=.028)
cylinder('Pencil graphite point',.010,.008,.020,blue,pen,r1=0,r2=.009)
cylinder('Pencil blue shaft',.410,.028,.60,teal,pen)
cylinder('Pencil end cap',.725,.031,.03,blue,pen)
stem=curve('Rabbit new drawing • stem',M.STEM,.007,blue)
flower=curve('Rabbit new drawing • flower',M.FLOWER,.007,blue)
for o in [stem,flower]:
    if hasattr(o.cycles,'use_motion_blur'):o.cycles.use_motion_blur=False

# Existing storm stays in the bottle. Soften the all-room flash contribution.
for name,ratio in [('Flash • room bounce',.30),('Flash • bottle scatter',.72)]:
    light=bpy.data.objects[name]
    for frame in range(1,337):
        scene.frame_set(frame);light.data.energy*=ratio;light.data.keyframe_insert(data_path='energy',frame=frame)

# Extend the native water, boat, fish and rain animation beyond the original 14s.
water=bpy.data.objects['Ocean • closed volume and analytic waves']
MODES=[(.17,2.5,.38,2.6),(.08,4.2,-1.2,3.7),(.045,7.3,2.0,5.1)]
def rad_at(x):
    points=[(-4.04,.01),(-4.02,.43),(-3.98,.91),(-3.90,1.24),(-3.77,1.47),(-3.55,1.58),(-3.25,1.60),(1.90,1.60),(2.17,1.57),(2.42,1.47),(2.65,1.30),(2.86,1.07),(3.04,.80),(3.22,.58),(3.43,.44),(3.70,.425),(4.08,.425)]
    for (xa,ra),(xb,rb) in zip(points,points[1:]):
        if xa<=x<=xb:
            u=(x-xa)/(xb-xa);u=u*u*(3-2*u);return ra*(1-u)+rb*u
    return .425
def wave(x,y,t):
    radius=max(.01,rad_at(x)-.075);fade=min(1,max(0,(x+3.98)/.5))*min(1,max(.05,(3.55-x)/1.2))*(.7+.3*max(0,1-(y/radius)**2))
    return 1.60+fade*.18*sum(a*math.sin(kx*x+ky*y-w*t) for a,kx,ky,w in MODES)
boat=bpy.data.objects['Schooner • four-point baked buoyancy']
scene.frame_set(1)
rain_bases=[]
for j in range(95):
    o=bpy.data.objects.get('Rain streak %03d'%j)
    if o:rain_bases.append((j,o,o.location.x-.035*math.sin(j),o.location.y,o.location.z-1.77))
for frame in range(337,M.FRAMES+1):
    t=(frame-1)/24
    for idx,(a,kx,ky,w) in enumerate(MODES):
        for trig,value in [('sin',.18*math.cos(w*t)),('cos',-.18*math.sin(w*t))]:
            kb=water.data.shape_keys.key_blocks['Wave_%d_%s'%(idx,trig)];kb.value=value;kb.keyframe_insert(data_path='value',frame=frame)
    x=.04+.12*math.sin(t*.43);y=-.10;hs=[wave(x-.73,y,t),wave(x+.73,y,t),wave(x,y-.23,t),wave(x,y+.23,t)]
    boat.location=(x,y,sum(hs)/4-.05);boat.rotation_euler=(math.atan2(hs[3]-hs[2],.46)*.68,-math.atan2(hs[1]-hs[0],1.46)*.85,.025*math.sin(t*.7))
    boat.keyframe_insert(data_path='location',frame=frame);boat.keyframe_insert(data_path='rotation_euler',frame=frame)
    for j in range(9):
        fish=bpy.data.objects['Fish %02d • swim path'%j];base=-2.8+j*.57
        fish.location=(base+.32*math.sin(t*.55+j),-.35+.18*math.sin(t*.34+j*1.4),.66+.22*math.sin(j*1.7)+.055*math.sin(t*2+j))
        fish.rotation_euler=(.04*math.sin(t*2+j),.07*math.cos(t*1.7+j),.18*math.sin(t*.55+j))
        fish.keyframe_insert(data_path='location',frame=frame);fish.keyframe_insert(data_path='rotation_euler',frame=frame)
    for j,o,x,y,zphase in rain_bases:
        o.location=(x+.035*math.sin(t+j),y,1.77+((zphase-t*1.7)%1.12));o.keyframe_insert(data_path='location',frame=frame)

# Start with the original framing; follow the carry, then orbit into a drawing
# close-up from the open left side of the bottle. The shot is continuous.
camera=scene.camera
original_cameras=[]
for frame in range(1,M.FRAMES+1):
    scene.frame_set(frame);original_cameras.append(camera.location.copy())
camera.animation_data_clear()
for frame in range(1,M.FRAMES+1):
    t=(frame-1)/M.FPS;pan=M.ease(8.0,12.80,t);close=M.ease(13.15,16.55,t)
    wide=original_cameras[frame-1]+Vector((-1.30*pan,0,0))
    focus_u=1-(1-close)**2
    target=Vector((.05-1.30*pan,.55,1.47)).lerp(Vector((-5.10,-1.76,.65)),focus_u)
    camera_pos=wide.lerp(Vector((-6.30,.85,3.05)),close)
    key(camera,frame,camera_pos,(target-camera_pos).to_track_quat('-Z','Y'))
    camera.data.lens=M.mix(52-3*pan,34,close)-6*math.sin(math.pi*close)**2;camera.data.keyframe_insert(data_path='lens',frame=frame)
    camera.data.dof.use_dof=True;camera.data.dof.focus_distance=(target-camera_pos).length
    camera.data.dof.aperture_fstop=M.mix(64,8,close)
    camera.data.dof.keyframe_insert(data_path='focus_distance',frame=frame);camera.data.dof.keyframe_insert(data_path='aperture_fstop',frame=frame)

audit=[];max_arm_error=0;max_leg_error=0
for frame in range(1,M.FRAMES+1):
    t=(frame-1)/M.FPS;pos=M.root_at(t);yaw=M.yaw_at(t);post=M.posture(t);r=M.R(yaw);f=M.F(yaw)
    q=Euler((0,0,yaw),'XYZ').to_quaternion();key(root,frame,pos,q)
    hip_center=pos+r*post['sway']+Vector((0,0,post['pelvis_z']))
    chest_center=hip_center+f*post['lean']+Vector((0,0,.18))
    tilt=.11*(post['lean']/.20)+.025*post['walk']
    chest_q=q@Euler((tilt,0,.025*post['walk']*math.sin(post['phase']*math.tau)),'XYZ').to_quaternion()
    key(pelvis,frame,hip_center,q);key(chest,frame,chest_center,chest_q)
    headpos=hip_center+f*(post['lean']+.015)+Vector((0,0,.65))
    paper_gaze=(Vector((-4.8,-1.5,.9))-headpos).normalized()
    box_gaze=(M.box_at(t)[0]-headpos).normalized()
    path_gaze=(f+Vector((0,0,-.08))).normalized()
    pen_gaze=(M.pen_at(t)[0]-headpos).normalized()
    if t<3.75:gaze=paper_gaze.lerp(box_gaze,M.ease(1.55,2.70,t)).normalized()
    elif t<12.25:gaze=box_gaze.lerp(path_gaze,M.ease(3.75,4.55,t)).normalized()
    elif t<14.40:gaze=path_gaze.lerp(box_gaze,M.ease(12.25,13.10,t)).normalized()
    else:gaze=box_gaze.lerp(pen_gaze,M.ease(14.40,15.45,t)).normalized()
    head_yaw=math.atan2(gaze.x,-gaze.y)
    delta=math.atan2(math.sin(head_yaw-yaw),math.cos(head_yaw-yaw))
    # Head anticipates turns, without the body making a sudden spin.
    delta=max(-.40,min(.40,delta))*M.ease(0,.55,t);pitch=max(-.10,min(.68,-math.asin(gaze.z)*.65))
    hq=Euler((pitch,0,yaw+delta),'XYZ').to_quaternion();key(head,frame,headpos,hq)
    for eye in eyes:eye.scale.z=.025*M.blink(t);eye.keyframe_insert(data_path='scale',frame=frame)
    for glint in eye_glints:glint.hide_render=M.blink(t)<.3;glint.keyframe_insert(data_path='hide_render',frame=frame)
    for side,ear in ear_controls:
        ear.rotation_euler=(.045*math.sin(t*2.1-side*.3)-.09*post['walk']*math.sin(post['phase']*math.tau-.5),side*.11+.05*math.sin(t*1.7+side),side*.025*math.sin(t*1.6))
        ear.keyframe_insert(data_path='rotation_euler',frame=frame)
    boxpos,byaw=M.box_at(t);key(box,frame,boxpos,Euler((0,0,byaw),'XYZ').to_quaternion())
    tip,axis=M.pen_at(t);key(pen,frame,tip,axis.to_track_quat('Z','Y'))
    targets=M.hand_targets(t)
    frame_audit={'frame':frame,'time':t,'root':list(pos),'feet':[],'arm_errors':[],'pen_tip':list(tip),'box_center':list(boxpos)}
    for side in [-1,1]:
        foot,fyaw,fpitch,stance=M.foot_at(t,side)
        key(feet[side],frame,foot,Euler((fpitch,0,fyaw),'XYZ').to_quaternion())
        hip=hip_center+r*side*.14
        knee,err=M.two_bone(hip,foot,hip+f*.35+r*side*.05,.255,.265)
        limb(legs[side][0],hip,knee,.095,frame);limb(legs[side][1],knee,foot,.077,frame)
        max_leg_error=max(max_leg_error,err)
        shoulder=chest_center+chest_q@Vector((side*.235,0,.205))
        wrist=targets[side]
        elbow,err=M.two_bone(shoulder,wrist,shoulder+r*side*.33-f*.10+Vector((0,0,-.20)),.28,.27)
        max_arm_error=max(max_arm_error,err)
        limb(arms[side][0],shoulder,elbow,.074,frame);limb(arms[side][1],elbow,wrist,.063,frame)
        rest_q=f.to_track_quat('Y','Z')
        box_q=(boxpos-wrist).normalized().to_track_quat('Y','Z')
        contact_weight=M.ease(2.30,3.0,t)*(1-M.ease(14.15,14.45,t))
        palm_q=rest_q.slerp(box_q,contact_weight)
        if side==1:
            writing_q=Vector((.15,.12,-1)).normalized().to_track_quat('Y','Z')
            palm_q=palm_q.slerp(writing_q,M.ease(15.25,15.80,t))
        key(hands[side],frame,wrist,palm_q)
        frame_audit['feet'].append({'side':side,'position':list(foot),'stance':stance,'leg_overreach':max(0,(foot-hip).length-.52)})
        frame_audit['arm_errors'].append(err)
    for obj,begin,end in [(stem,16.85,17.75),(flower,17.75,19.75)]:
        obj.data.bevel_factor_end=M.ease(begin,end,t);obj.data.keyframe_insert(data_path='bevel_factor_end',frame=frame)
        obj.hide_render=t<begin;obj.keyframe_insert(data_path='hide_render',frame=frame)
    audit.append(frame_audit)

scene['rabbit_action']='Look, approach, squat, grip, lift, carry with planted feet, place, release, pick pencil, draw progressive flower.'
scene['animation_controls']='World-space stance feet; analytic two-bone IK; box/pencil single transform trajectories; contact-constrained wrists; native baked keys.'
scene.render.filepath='//../outputs/frames-bunny/frame_'
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'public/bottle-storm.blend'))
timeline=json.loads((ROOT/'outputs/versions/v1/timeline.json').read_text());timeline.update({'duration':M.DURATION,'frames':M.FRAMES,'version':'bunny-artist','room_flash_scale':.30,'bottle_flash_scale':.72})
(ROOT/'docs/timeline.json').write_text(json.dumps(timeline,indent=2))
report={'frames':M.FRAMES,'fps':M.FPS,'duration':M.DURATION,'max_arm_overreach':max_arm_error,'max_leg_overreach':max_leg_error,'foot_contacts':[e['end'] for side in [-1,1] for e in M.FOOT_EVENTS[side]],'drawing_start':16.85,'block_grounded':14.15,'states':audit}
(ROOT/'outputs/checks/bunny/motion-audit.json').write_text(json.dumps(report,indent=2))
print('BUNNY_SCENE_READY',M.FRAMES,'frames','arm_overreach',max_arm_error,'leg_overreach',max_leg_error,flush=True)
