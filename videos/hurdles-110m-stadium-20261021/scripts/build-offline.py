"""Deterministic local CG: no stock footage and no video generation API."""
import bpy,bmesh,json,math,random,sys,os
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
P=Path.cwd();O=P/"outputs/offline";O.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
mode=args[0] if args else "build"
def device():
 if os.environ.get('HURDLE_CPU')=='1':
  bpy.context.scene.cycles.device='CPU';return
 cp=bpy.context.preferences.addons["cycles"].preferences
 try:
  cp.compute_device_type="METAL";cp.get_devices()
  for d in cp.devices:d.use=d.type=="METAL"
  bpy.context.scene.cycles.device="GPU"
 except Exception:bpy.context.scene.cycles.device="CPU"
def look(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(name,color,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def cube(name,loc,size,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if m:o.data.materials.append(m)
 if bevel:
  b=o.modifiers.new('Rounded manufactured edges','BEVEL');b.width=bevel;b.segments=2;o.modifiers.new('Surface normals','WEIGHTED_NORMAL')
 return o
def text(name,content,loc,size,rotation,m):
 d=bpy.data.curves.new(name,'FONT');d.body=content;d.size=size;d.align_x='CENTER';d.align_y='CENTER';d.extrude=.0002;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation;d.materials.append(m);return o
def noise_bump(m,scale,strength,distance):
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=3;bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal']);return tex
if mode in ['still','frames']:
 bpy.ops.wm.open_mainfile(filepath=str(O/'hurdles-cycles.blend'));device();s=bpy.context.scene
 if mode=='still':
  f=int(args[1]) if len(args)>1 else 35;s.frame_set(f);s.cycles.samples=64;s.render.filepath=str(P/f'outputs/checks/offline/cycles-{f:03d}.png');bpy.ops.render.render(write_still=True)
 else:
  s.frame_start=int(args[1]) if len(args)>1 else 1;s.frame_end=int(args[2]) if len(args)>2 else 66;s.cycles.samples=int(args[3]) if len(args)>3 else 24;s.render.filepath=str(O/'frames/frame_');(O/'frames').mkdir(exist_ok=True);bpy.ops.render.render(animation=True)
 sys.exit(0)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(P/'public/assets/athlete-v2.glb'))
for o in list(bpy.data.objects):
 if o.name.startswith('Icosphere'):bpy.data.objects.remove(o,do_unlink=True)
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');body=bpy.data.objects['AthleteBody']
skin=bpy.data.materials['AthleteSkin'];p=skin.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.43;p.inputs['IOR'].default_value=1.42;p.inputs['Subsurface Weight'].default_value=.12;p.inputs['Subsurface Radius'].default_value=(1.,.42,.22);p.inputs['Subsurface Scale'].default_value=.0035;p.inputs['Specular IOR Level'].default_value=.32;p.inputs['Coat Weight'].default_value=.045;p.inputs['Coat Roughness'].default_value=.3
noise_bump(skin,760,.24,.00024)
eye=bpy.data.materials['AthleteEyes'].node_tree.nodes.get('Principled BSDF');eye.inputs['Roughness'].default_value=.13;eye.inputs['Coat Weight'].default_value=.6;eye.inputs['Coat Roughness'].default_value=.08
for poly in body.data.polygons:poly.use_smooth=True
red=mat('Technical red knit',(.35,.018,.012),.66);black=mat('Graphite performance fabric',(.014,.020,.021),.58)
for m in [red,black]:
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Sheen Weight'].default_value=.24;noise_bump(m,1250,.12,.00012)
def garment(name,cond,material,padding):
 polys=[f for f in body.data.polygons if cond(f.center)]
 # Rebuild clean topology, weld glTF UV seams and preserve native skin weights.
 used=sorted({i for f in polys for i in f.vertices});mapping={i:j for j,i in enumerate(used)}
 points=[body.data.vertices[i].co+body.data.vertices[i].normal*padding for i in used]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(points,[],[[mapping[i] for i in f.vertices] for f in polys]);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 for group in body.vertex_groups:
  vg=o.vertex_groups.new(name=group.name)
  for old,new in mapping.items():
   for item in body.data.vertices[old].groups:
    if item.group==group.index and item.weight>0:vg.add([new],item.weight,'REPLACE')
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 for poly in mesh.polygons:poly.use_smooth=True
 mod=o.modifiers.new('Native skeleton','ARMATURE');mod.object=arm
 solid=o.modifiers.new('Fabric thickness','SOLIDIFY');solid.thickness=.0015;solid.offset=0
 return o

def smooth(a,b,x):t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def shirt(v):
 x=abs(v.x);return v.z>1.09 and v.z<1.495+.091*smooth(.055,.115,x) and x<.235-.073*smooth(1.34,1.54,v.z)
garment('Racing singlet - separate garment',shirt,red,.006)
garment('Running shorts - separate garment',lambda v:.79<v.z<1.10 and abs(v.x)<.34,black,.007)
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if shirt(f.calc_center_median()) or (.792<f.calc_center_median().z<1.095 and abs(f.calc_center_median().x)<.335)],context='FACES')
bm.to_mesh(body.data);bm.free();body.data.update()
hair_under=bpy.data.materials['AthleteHair'].node_tree.nodes.get('Principled BSDF');hair_under.inputs['Roughness'].default_value=.63
hairmat=mat('Black hair strands',(.012,.008,.006),.42);cur=bpy.data.curves.new('Groomed short strands','CURVE');cur.dimensions='3D';cur.resolution_u=2;cur.bevel_depth=.00011;cur.bevel_resolution=0;cur.materials.append(hairmat);rng=random.Random(721)
for i in range(6200):
 phi=rng.random()*math.tau;max_theta=1.5+.4*max(0,math.sin(phi))-.50*max(0,-math.sin(phi));theta=math.acos(1-rng.random()*(1-math.cos(max_theta)))
 root=Vector((.079*math.sin(theta)*math.cos(phi),-.048+.093*math.sin(theta)*math.sin(phi),1.771+.111*math.cos(theta)));normal=Vector((root.x/.079,(root.y+.048)/.093,(root.z-1.771)/.111)).normalized();length=.005+.013*max(0,math.cos(theta))+rng.random()*.005;spline=cur.splines.new('POLY');spline.points.add(4)
 for k,pnt in enumerate(spline.points):
  u=k/4;v=root+normal*length*math.sin(u*1.4)+Vector((-.002*u,.009*u*u,.001*math.sin(u*math.pi)));pnt.co=(*v,1);pnt.radius=1-u*.88
hair=bpy.data.objects.new('Individual short hair',cur);bpy.context.collection.objects.link(hair)
cream=mat('Race bib woven paper',(.8,.8,.74),.85);ink=mat('Bib number ink',(.016,.022,.018),.8);bib=cube('Race bib',(0,-.169,1.375),(.17,.002,.165),cream,.002);number=text('Athlete number','04',(0,-.171,1.375),.103,(math.pi/2,0,0),ink)
track=mat('Red granular rubber',(.28,.073,.042),.92);nt=track.node_tree;grain=noise_bump(track,560,.7,.0012);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(.16,.035,.019,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.42,.132,.073,1);nt.links.new(grain.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
cube('Track surface',(55,-4.88,-.065),(190,9.76,.12),track)
white=mat('Painted lane markings',(.74,.76,.69),.9);steel=mat('Satin aluminum',(.43,.47,.49),.3,.8);dark=mat('Hurdle black stripes',(.018,.024,.025),.63)
for lane in range(9):cube('Lane boundary',(55,-lane*1.22,.0005),(190,.045,.002),white)
for x in [0,110]:cube('Start finish line',(x,-4.88,.002),(.055,9.76,.003),white)
for i in range(10):
 x=13.72+i*9.14;y=-4.27
 for dy in [-.53,.53]:
  cube('Hurdle foot',(x+.3,y+dy,.022),(.84,.06,.045),steel,.01);cube('Telescopic post',(x,y+dy,.53),(.047,.047,1.02),steel,.006);cube('Post red sleeve',(x,y+dy,.20),(.053,.053,.34),red,.005)
 cube('Hurdle crossbar',(x,y,1.0295),(.065,1.18,.075),white,.006)
 for k in range(5):cube('Hurdle stripe',(x-.0332,y-.5+k*.225,1.030),(.001,.105,.075),dark)
 for lane in range(8):cube('Hurdle track mark',(x,-lane*1.22-.15,.003),(.045,.14,.003),white)
grass=mat('Stadium turf',(.10,.20,.045),.95);g=grass.node_tree;n=noise_bump(grass,250,.45,.003);c=g.nodes.new('ShaderNodeValToRGB');c.color_ramp.elements[0].color=(.045,.09,.018,1);c.color_ramp.elements[1].color=(.20,.30,.055,1);g.links.new(n.outputs['Fac'],c.inputs['Fac']);g.links.new(c.outputs['Color'],g.nodes.get('Principled BSDF').inputs['Base Color']);cube('Infield',(55,40,-.07),(190,80,.11),grass)
s=bpy.context.scene;s.world=bpy.data.worlds.new('Stadium environment');s.world.use_nodes=True;w=s.world.node_tree;env=w.nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(P/'public/assets/offline/stadium_01_2k.hdr'));coord=w.nodes.new('ShaderNodeTexCoord');mapping=w.nodes.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=.9;w.links.new(coord.outputs['Generated'],mapping.inputs['Vector']);w.links.new(mapping.outputs['Vector'],env.inputs['Vector']);w.links.new(env.outputs['Color'],w.nodes.get('Background').inputs['Color']);w.nodes.get('Background').inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('Morning sun','SUN');ld.energy=1.5;ld.angle=.045;ld.color=(1,.89,.76);sun=bpy.data.objects.new('Morning sun',ld);bpy.context.collection.objects.link(sun);sun.location=(-20,-30,40);look(sun,(0,0,0))
bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='Tracking camera';camera.data.lens=53;camera.data.sensor_width=36;s.camera=camera;focus=bpy.data.objects.new('Athlete focus',None);bpy.context.collection.objects.link(focus);camera.data.dof.use_dof=True;camera.data.dof.focus_object=focus;camera.data.dof.aperture_fstop=4.0
data=json.loads((P/'sources/offline/poses.json').read_text());C=Matrix.Rotation(math.pi/2,4,'X');Ci=C.inverted()
def conv(a):return C@Matrix([a[i::4] for i in range(4)])@Ci
rest=data['rest'];fix={n:conv(rest[n]).inverted()@(arm.matrix_world@arm.data.bones[n].matrix_local) for n in data['names']};rest_head=arm.matrix_world@arm.data.bones['head'].matrix_local;rest_chest=arm.matrix_world@arm.data.bones['spine02'].matrix_local
attached=[(hair,'head',rest_head.inverted(),hair.matrix_world.copy()),(bib,'spine02',rest_chest.inverted(),bib.matrix_world.copy()),(number,'spine02',rest_chest.inverted(),number.matrix_world.copy())]
curl={}
for pb in arm.pose.bones:
 pb.rotation_mode='QUATERNION'
 if pb.name.startswith('finger'):
  parts=pb.name.split('-');joint=int(parts[1].split('.')[0]);digit=int(parts[0].replace('finger',''))
  forward=(pb.bone.tail_local-pb.bone.head_local).normalized()
  toward=Vector((0,-1,0))
  if digit==1:
   middle=arm.data.bones.get('finger3-1.'+pb.name[-1])
   if middle:toward=(middle.head_local-pb.bone.head_local).normalized()
  bend=forward.cross(toward)
  if bend.length>.01:
   local=pb.bone.matrix_local.to_3x3().inverted()@bend.normalized()
   angle=([0,.40,.8,.55][min(joint,3)] if digit!=1 else .4)
   curl[pb.name]=Quaternion(local,angle)

arm_inv=arm.matrix_world.inverted()
for f,frame in enumerate(data['frames'],1):
 targets={n:arm_inv@conv(a)@fix[n] for n,a in zip(data['names'],frame['bones'])}
 for pb in arm.pose.bones:
  m=targets[pb.name]
  if pb.parent:pb.matrix_basis=pb.bone.convert_local_to_pose(m,pb.bone.matrix_local,parent_matrix=targets[pb.parent.name],parent_matrix_local=pb.parent.bone.matrix_local,invert=True)
  else:pb.matrix_basis=pb.bone.convert_local_to_pose(m,pb.bone.matrix_local,invert=True)
  if pb.name in curl:pb.rotation_quaternion=curl[pb.name];pb.location=(0,0,0);pb.scale=(1,1,1)
  for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=f,group=pb.name)
 for o,bone,inv,base in attached:
  o.matrix_world=arm.matrix_world@targets[bone]@inv@base;o.rotation_mode='QUATERNION'
  for prop in ['location','rotation_quaternion','scale']:o.keyframe_insert(prop,frame=f)
 d=frame['d'];focus.location=(d+.06,-4.27,1.17);camera.location=(d+2.7,-10.2,1.72);look(camera,focus.location)
 for o in [focus,camera]:o.keyframe_insert('location',frame=f)
 camera.keyframe_insert('rotation_euler',frame=f)
s.render.engine='CYCLES';device();s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.065;s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.transparent_max_bounces=8
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=66;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.film_transparent=False;s.render.use_motion_blur=False;s.render.motion_blur_shutter=.32
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.0;s.render.use_persistent_data=True;s.frame_set(35)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'hurdles-cycles.blend'))
print('OFFLINE_SCENE_READY',len(bpy.data.objects),len(data['frames']),flush=True)
