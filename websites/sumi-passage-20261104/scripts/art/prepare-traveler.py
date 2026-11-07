"""Normalize the legally exported Tripo GLB and author six in-place skeletal clips."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Quaternion

ROOT=Path(__file__).resolve().parents[2]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'docs/art/traveler-tripo-retopo.glb'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
hero=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o!=hero:bpy.data.objects.remove(o,do_unlink=True)
hero.name='TravelerSkinnedBody'
root=bpy.data.objects.new('TravelerRoot',None);bpy.context.collection.objects.link(root)
for obj in list(bpy.context.scene.objects):
    if obj!=root and obj.parent is None:obj.parent=root
# Honor the glTF armature's existing orientation instead of rotating it twice.
left=arm.data.bones.get('mixamorig:LeftUpLeg');right=arm.data.bones.get('mixamorig:RightUpLeg')
left_axis=(arm.matrix_world.to_3x3()@(left.head_local-right.head_local)).normalized()
forward=left_axis.cross(Vector((0,0,1))).normalized()
root.rotation_euler.z=-math.pi/2-math.atan2(forward.y,forward.x)
root.scale=(2.06,2.06,2.06)
for image in bpy.data.images:
    if image.size[0]>2048:image.scale(2048,2048)
    if image.source=='FILE':image.pack()
for mat in hero.data.materials:
    if not mat or not mat.node_tree:continue
    bsdf=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bsdf:
        bsdf.inputs['Roughness'].default_value=.9
        for link in list(bsdf.inputs['Alpha'].links):mat.node_tree.links.remove(link)
        bsdf.inputs['Alpha'].default_value=1
        if 'Transmission Weight' in bsdf.inputs:bsdf.inputs['Transmission Weight'].default_value=0
        if 'Subsurface Weight' in bsdf.inputs:bsdf.inputs['Subsurface Weight'].default_value=0
    mat.name='Traveler_WovenIndigoAndStraw'
    mat.use_backface_culling=False

scene=bpy.context.scene;scene.render.fps=30
names={b.name.split(':')[-1]:b.name for b in arm.pose.bones}
identity=Quaternion((1,0,0,0))
def bone(name):return arm.pose.bones.get(names.get(name,''))
def local_axis_quat(name,axis,angle):
    pb=bone(name)
    if not pb:return identity.copy()
    transform=pb.bone.matrix_local.to_3x3()
    return Quaternion((transform.inverted()@Vector(axis)).normalized(),angle)
def set_rot(name,axis,angle,base=None):
    pb=bone(name)
    if pb:
        pb.rotation_mode='QUATERNION';pb.rotation_quaternion=local_axis_quat(name,axis,angle)@(base or identity)
def translate(name,xyz):
    pb=bone(name)
    if pb:pb.location=pb.bone.matrix_local.to_3x3().inverted()@Vector(xyz)

# Lower A-pose upper arms into a relaxed silhouette without changing the skin bind.
arm_base={}
for side,sign in [('Left',1),('Right',-1)]:
    name=side+'Arm';pb=bone(name)
    direction=(pb.bone.tail_local-pb.bone.head_local).normalized()
    target=Vector((.02,sign*.16,-1)).normalized()
    world=direction.rotation_difference(target);orientation=pb.bone.matrix_local.to_quaternion()
    arm_base[side]=orientation.inverted()@world@orientation

arm.animation_data_create()
clips=[('Idle',91),('Walk',21),('Run',16),('Jump',11),('Fall',31),('Land',10)]
for name,end in clips:
    arm.animation_data.action=None
    action=bpy.data.actions.new(name);action.use_fake_user=True;arm.animation_data.action=action
    for frame in range(1,end+1):
        t=(frame-1)/(end-1);phase=t*math.tau
        for pb in arm.pose.bones:pb.location=(0,0,0);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=identity
        for side in ['Left','Right']:set_rot(side+'Arm',(0,1,0),0,arm_base[side])
        # The shoulder has a quiet breath, fingers rest slightly curved.
        set_rot('Spine2',(0,1,0),.012*math.sin(phase))
        for key in names:
            if 'Hand' in key and any(s in key for s in ['Index','Middle','Ring','Pinky']) and key[-1:] in ['1','2','3']:
                pb=bone(key);pb.rotation_quaternion=Quaternion((1,0,0),.09)
        if name=='Idle':
            translate('Hips',(0,0,.002*math.sin(phase)))
            set_rot('Head',(0,0,1),.018*math.sin(phase))
        elif name in ['Walk','Run']:
            running=name=='Run';amplitude=.83 if running else .57
            for side,offset in [('Left',0),('Right',math.pi)]:
                p=phase+offset;hip=-amplitude*math.cos(p)
                knee=.08+(1.05 if running else .72)*max(0,-math.sin(p))
                set_rot(side+'UpLeg',(0,1,0),hip)
                set_rot(side+'Leg',(0,1,0),knee)
                # Ankle compensation prevents a stiff foot arc on planted steps.
                set_rot(side+'Foot',(0,1,0),-hip-knee+(.13 if running else .05)*math.sin(p))
                set_rot(side+'ToeBase',(0,1,0),-.17*max(0,math.sin(p)))
                swing=(.52 if running else .32)*math.cos(p)
                set_rot(side+'Arm',(0,1,0),swing,arm_base[side])
                set_rot(side+'ForeArm',(0,1,0),-(.78 if running else .19)-.10*max(0,-math.cos(p)))
            translate('Hips',(0,.004*math.sin(phase),(.010 if running else .006)*(1-math.cos(phase*2))))
            set_rot('Hips',(0,0,1),.035*math.sin(phase))
            set_rot('Spine',(0,1,0),-.08 if running else -.02)
            set_rot('Spine2',(0,0,1),-.055*math.sin(phase))
        elif name=='Jump':
            ease=math.sin(t*math.pi/2)
            translate('Hips',(0,0,-.018*(1-ease)))
            set_rot('LeftUpLeg',(0,1,0),-.58*ease);set_rot('RightUpLeg',(0,1,0),.22*ease)
            set_rot('LeftLeg',(0,1,0),.84*ease);set_rot('RightLeg',(0,1,0),.60*ease)
            for side in ['Left','Right']:set_rot(side+'Arm',(0,1,0),-.42*ease,arm_base[side]);set_rot(side+'ForeArm',(0,1,0),-.32*ease)
            set_rot('Spine',(0,1,0),-.09*ease)
        elif name=='Fall':
            set_rot('LeftUpLeg',(0,1,0),-.15);set_rot('RightUpLeg',(0,1,0),.12)
            set_rot('LeftLeg',(0,1,0),.25);set_rot('RightLeg',(0,1,0),.36)
            for side,sign in [('Left',1),('Right',-1)]:
                set_rot(side+'Arm',(1,0,0),sign*.23,arm_base[side]);set_rot(side+'ForeArm',(0,1,0),-.22)
            set_rot('Spine2',(0,1,0),.04)
        elif name=='Land':
            impact=math.sin(math.pi*t)*(1-t)
            translate('Hips',(0,0,-.07*impact))
            for side in ['Left','Right']:
                set_rot(side+'UpLeg',(0,1,0),-.65*impact);set_rot(side+'Leg',(0,1,0),1.1*impact);set_rot(side+'Foot',(0,1,0),-.45*impact)
                set_rot(side+'Arm',(0,1,0),.14*impact,arm_base[side])
            set_rot('Spine',(0,1,0),-.12*impact)
        for pb in arm.pose.bones:
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
            if pb.name==names.get('Hips'):pb.keyframe_insert('location',frame=frame,group=pb.name)
    track=arm.animation_data.nla_tracks.new();track.name=name
    strip=track.strips.new(name,1,action);strip.action_frame_start=1;strip.action_frame_end=end;strip.extrapolation='NOTHING'
    arm.animation_data.action=None

# Export each NLA track as a separate animation, including the inherited skin.
scene.frame_start=1;scene.frame_end=91;scene.frame_set(1)
for track in arm.animation_data.nla_tracks:track.mute=track.name!='Idle'
blend_path=ROOT/'docs/art/traveler-animated-v2.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
for track in arm.animation_data.nla_tracks:track.mute=False
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/traveler-v2.glb'),export_format='GLB',export_yup=True,export_image_format='JPEG',export_jpeg_quality=90,export_materials='EXPORT',export_animations=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_force_sampling=True,export_anim_slide_to_zero=True,export_cameras=False,export_lights=False)
report={'source':'Tripo H2.5 / retopology / automatic skin; original Blender authored skeletal clips','vertices':len(hero.data.vertices),'faces':len(hero.data.polygons),'bones':len(arm.data.bones),'clips':[name for name,_ in clips],'height_m':2.06,'texture_max':2048}
(ROOT/'outputs/checks/v2/traveler-assets.json').write_text(json.dumps(report,indent=2))
print('TRAVELER_REPORT',report)
