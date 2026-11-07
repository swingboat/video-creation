"""A complete free athlete candidate, preserving the authored head/body/clothes rig."""
import bpy,math,json,sys,random,bisect
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
P=Path.cwd();O=P/'outputs/realism-v7';O.mkdir(parents=True,exist_ok=True)
C=P/'outputs/checks/realism-v7';C.mkdir(parents=True,exist_ok=True)
S=P/'sources/research/realism-v7/rocketbox'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];mode=args[0] if args else 'build'

def look(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def rotate(arm,name,axis,degrees):
 pb=arm.pose.bones[name];local=(arm.matrix_world.to_3x3()@pb.bone.matrix_local.to_3x3()).inverted()@Vector(axis);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion(local.normalized(),math.radians(degrees))
def camera(s,kind):
 c=s.camera;c.animation_data_clear();c.data.dof.use_dof=True;c.data.dof.aperture_fstop=5.6;c.data.sensor_fit='VERTICAL';c.data.sensor_height=36
 f=bpy.data.objects['Athlete focus'];f.animation_data_clear()
 if kind=='portrait':f.location=(0,-4.30,1.69);c.location=(.30,-6.02,1.74);c.data.lens=128
 elif kind=='half':f.location=(0,-4.30,1.37);c.location=(.82,-7.54,1.61);c.data.lens=94
 else:f.location=(0,-4.30,1.00);c.location=(1.5,-9.95,1.53);c.data.lens=89
 c.data.dof.focus_object=f;look(c,f.location)
 s.render.resolution_x=1200;s.render.resolution_y=1500;s.render.resolution_percentage=int(args[2]) if len(args)>2 else 100

if mode!='build':
 bpy.ops.wm.open_mainfile(filepath=str(O/'complete-free-athlete.blend'));s=bpy.context.scene;s.cycles.device='CPU'
 if mode=='flex':
  arm=next(o for o in s.objects if o.type=='ARMATURE')
  rotate(arm,'Bip01 L Thigh',(1,0,0),-48);rotate(arm,'Bip01 L Calf',(1,0,0),86)
  rotate(arm,'Bip01 L UpperArm',(0,1,0),31);rotate(arm,'Bip01 L Forearm',(1,0,0),-45)
  rotate(arm,'Bip01 R UpperArm',(0,1,0),-31);rotate(arm,'Bip01 R Forearm',(1,0,0),-45)
  bpy.context.view_layer.update()
 camera(s,mode);s.cycles.samples=int(args[1]) if len(args)>1 else 64
 s.render.filepath=str(O/(mode+'.png'));bpy.ops.render.render(write_still=True);sys.exit(0)

# Retain the established physical track, HDRI, sun, and camera; replace all old character objects.
bpy.ops.wm.open_mainfile(filepath=str(P/'outputs/realism-v6/baseline.blend'))
s=bpy.context.scene;s.frame_set(1);s.cycles.device='CPU';s.render.use_motion_blur=False
oldstage=bpy.data.objects['Character stage'];remove=set(oldstage.children_recursive)|{oldstage}
for o in list(remove):bpy.data.objects.remove(o,do_unlink=True)
assert not any(o.type=='ARMATURE' for o in s.objects),'Old armature remains'
before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(S/'Sports_Male_04.fbx'))
added=[o for o in bpy.data.objects if o not in before];arm=next(o for o in added if o.type=='ARMATURE');mesh=next(o for o in added if o.type=='MESH')
arm.animation_data_clear()
for pb in arm.pose.bones:pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
# Uniformly normalize the complete asset without changing its proportions or internal transforms.
corners=[mesh.matrix_world@Vector(v) for v in mesh.bound_box];low=min(v.z for v in corners);height=max(v.z for v in corners)-low
stage=bpy.data.objects.new('Complete free athlete stage',None);bpy.context.collection.objects.link(stage)
for o in added:
 if o.parent in added:continue
 old=o.matrix_world.copy();o.parent=stage;o.matrix_world=old
stage.scale=(1.88/height,)*3;stage.location=(0,-4.27,-low*stage.scale.z+.002)
rotate(arm,'Bip01 L UpperArm',(0,1,0),23);rotate(arm,'Bip01 R UpperArm',(0,1,0),-23)
rotate(arm,'Bip01 L Forearm',(1,0,0),-6);rotate(arm,'Bip01 R Forearm',(1,0,0),-6)
def shift_face(name,delta):
 pb=arm.pose.bones[name];pb.location=(arm.matrix_world.to_3x3()@pb.bone.matrix_local.to_3x3()).inverted()@Vector(delta)
for side in ['L','R']:shift_face('Bip01 '+side+'EyeBlinkTop',(0,0,-.0011))
for name in ['Bip01 MBottomLip','Bip01 LMouthBottom','Bip01 RMouthBottom']:shift_face(name,(0,0,.0008))
bpy.context.view_layer.update()

def texture(nt,part,kind):
 t=nt.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(S/f'm026_{part}_{kind}.tga'),check_existing=True)
 if kind!='color':t.image.colorspace_settings.name='Non-Color'
 return t
for slot,part in zip(mesh.material_slots,['body','head']):
 m=bpy.data.materials.new('V7 native '+part);m.use_nodes=True;slot.material=m
 nt=m.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF')
 col=texture(nt,part,'color');l.new(col.outputs['Color'],p.inputs['Base Color'])
 norm=texture(nt,part,'normal');nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.7;l.new(norm.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],p.inputs['Normal'])
 spec=texture(nt,part,'specular');r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.82 if part=='body' else .69;r.inputs['To Max'].default_value=.38 if part=='body' else .32;l.new(spec.outputs['Color'],r.inputs['Value']);l.new(r.outputs['Result'],p.inputs['Roughness'])
 p.inputs['Specular IOR Level'].default_value=.25;p.inputs['IOR'].default_value=1.4
 if part=='head':p.inputs['Subsurface Weight'].default_value=.055;p.inputs['Subsurface Radius'].default_value=(1,.42,.22);p.inputs['Subsurface Scale'].default_value=.0015
 else:p.inputs['Sheen Weight'].default_value=.12;p.inputs['Sheen Roughness'].default_value=.8
eye_mat=mesh.material_slots[1].material.copy();eye_mat.name='V7 native wet eyes';ep=eye_mat.node_tree.nodes.get('Principled BSDF')
for link in list(ep.inputs['Roughness'].links):eye_mat.node_tree.links.remove(link)
ep.inputs['Roughness'].default_value=.09;ep.inputs['Coat Weight'].default_value=.75;ep.inputs['Coat Roughness'].default_value=.03;ep.inputs['Subsurface Weight'].default_value=0
mesh.data.materials.append(eye_mat);eye_ids={g.index for g in mesh.vertex_groups if g.name in ['Bip01 LEye','Bip01 REye']};eye_faces=0
for f in mesh.data.polygons:
 weight=sum(sum(g.weight for g in mesh.data.vertices[i].groups if g.group in eye_ids) for i in f.vertices)/len(f.vertices)
 if weight>.55:f.material_index=2;eye_faces+=1
 f.use_smooth=True
sub=mesh.modifiers.new('Smooth authored surface','SUBSURF');sub.levels=2;sub.render_levels=2

# Short fibers follow the original scalp rather than a generic helmet mesh.
# Texture/position sampling excludes eyebrows and retains the authored native haircut.
head_img=bpy.data.images.load(str(S/'m026_head_color.tga'),check_existing=True);W,H=head_img.size;pixels=list(head_img.pixels);uv=mesh.data.uv_layers.active.data
def lum(u,v):
 x=min(W-1,max(0,int(u*W)));y=min(H-1,max(0,int(v*H)));i=(y*W+x)*4;return sum(pixels[i:i+3])/3
triangles=[];total=0
for poly in mesh.data.polygons:
 if poly.material_index!=1:continue
 ids=list(poly.vertices);loops=list(poly.loop_indices)
 for j in range(1,len(ids)-1):
  vi=[ids[0],ids[j],ids[j+1]];li=[loops[0],loops[j],loops[j+1]];vs=[mesh.matrix_world@mesh.data.vertices[i].co for i in vi];us=[uv[i].uv.copy() for i in li]
  # World surface before stage scaling: scalp back/top, no eyebrows.
  if min(v.z for v in vs)<1.735*1.88/1.804-0.025:continue
  if lum(sum(u.x for u in us)/3,sum(u.y for u in us)/3)>.22:continue
  area=(vs[1]-vs[0]).cross(vs[2]-vs[0]).length/2
  if area>0:total+=area;triangles.append((total,vs,us))
cur=bpy.data.curves.new('V7 short hair fibers','CURVE');cur.dimensions='3D';cur.resolution_u=1;cur.bevel_depth=.00007;cur.bevel_resolution=0
hm=bpy.data.materials.new('V7 matte dark brown hair');hm.use_nodes=True;hp=hm.node_tree.nodes.get('Principled BSDF');hp.inputs['Base Color'].default_value=(.026,.016,.011,1);hp.inputs['Roughness'].default_value=.64;cur.materials.append(hm)
rng=random.Random(1107);count=0
if triangles:
 weights=[t[0] for t in triangles]
 for _ in range(7000):
  _,vs,us=triangles[bisect.bisect_left(weights,rng.random()*total)];a=rng.random();b=rng.random()
  if a+b>1:a=1-a;b=1-b
  root=vs[0]*(1-a-b)+vs[1]*a+vs[2]*b;tex=us[0]*(1-a-b)+us[1]*a+us[2]*b
  if lum(tex.x,tex.y)>.24:continue
  normal=(vs[1]-vs[0]).cross(vs[2]-vs[0]).normalized();length=rng.uniform(.001,.003);sp=cur.splines.new('POLY');sp.points.add(2)
  for j,p in enumerate(sp.points):
   t=j/2;v=root+normal*(.0003+length*t)+Vector((.001*t*t,.004*t*t,0));p.co=(*v,1)
  count+=1
hair=bpy.data.objects.new('V7 original scalp fine hair',cur);bpy.context.collection.objects.link(hair)
# Keep fibers in world space for static look development. Dynamic hair is not claimed validated.
s.cycles.samples=64;s.cycles.adaptive_threshold=.025;s.cycles.max_bounces=8;s.cycles.use_denoising=True
camera(s,'portrait');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'complete-free-athlete.blend'))
report={'asset':'Microsoft Rocketbox Sports_Male_04','license':'MIT','cost':0,'completeMatchedCharacter':True,'vertices':len(mesh.data.vertices),'bones':len(arm.data.bones),'textureSize':list(head_img.size),'eyeFaces':eye_faces,'hairFibers':count,'sourceHeight':height,'renderHeight':1.88,'motionValidated':False,'photorealismAccepted':False}
(C/'build-report.json').write_text(json.dumps(report,indent=2));print('FREE_ATHLETE_BUILT',json.dumps(report))
