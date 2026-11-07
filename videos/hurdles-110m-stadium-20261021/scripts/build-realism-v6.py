"""Character look development. Renders, not an AI-generated photographic substitute."""
import bpy,bmesh,math,json,sys,random,bisect
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.kdtree import KDTree

P=Path.cwd();O=P/'outputs/realism-v6';O.mkdir(parents=True,exist_ok=True)
S=P/'sources/research/realism-v6/renderpeople/eric'
HEAD_LIFT=.055;NECK_Z=1.61+HEAD_LIFT;BODY_NECK_Z=NECK_Z-.025
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'build'

def look(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def basic(name,c,r=.6):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;return m
def setup_camera(s,kind):
 c=s.camera;c.animation_data_clear();c.data.dof.use_dof=True;c.data.dof.aperture_fstop=5.6;c.data.sensor_fit='VERTICAL';c.data.sensor_height=36
 focus=bpy.data.objects.get('Athlete focus');focus.animation_data_clear()
 if kind in ['portrait','baseline']:
  focus.location=(0,-4.30,1.69);c.location=(.30,-6.02,1.74);c.data.lens=128
 elif kind=='half':
  focus.location=(0,-4.30,1.37);c.location=(.82,-7.54,1.61);c.data.lens=94
 else:
  focus.location=(0,-4.30,1.00);c.location=(1.5,-9.95,1.53);c.data.lens=89
 c.data.dof.focus_object=focus;look(c,focus.location)
 s.render.resolution_x=1200;s.render.resolution_y=1500;s.render.resolution_percentage=100

def render(kind,samples=96):
 s=bpy.context.scene;setup_camera(s,kind);s.render.resolution_percentage=int(args[2]) if len(args)>2 else 100;s.cycles.samples=samples;s.render.filepath=str(O/(kind+'.png'));bpy.ops.render.render(write_still=True)

if mode!='build':
 bpy.ops.wm.open_mainfile(filepath=str(O/('baseline.blend' if mode=='baseline' else 'athlete-lookdev.blend')))
 bpy.context.scene.cycles.device='CPU';render(mode,int(args[1]) if len(args)>1 else 96);sys.exit(0)

bpy.ops.wm.open_mainfile(filepath=str(P/'outputs/offline/hurdles-cycles.blend'))
s=bpy.context.scene;s.frame_set(1);s.cycles.device='CPU';s.render.use_motion_blur=False;s.cycles.samples=96;s.cycles.adaptive_threshold=.025
s.cycles.max_bounces=8;s.cycles.transparent_max_bounces=12;s.render.use_persistent_data=True
arm=next(o for o in s.objects if o.type=='ARMATURE');arm.animation_data_clear()
for pb in arm.pose.bones:pb.matrix_basis=Matrix.Identity(4)

# Stage all character components together, in a neutral relaxed stance.
body=bpy.data.objects['AthleteBody'];pieces=[o for o in s.objects if o==arm or o.type=='MESH' and (o.name.startswith('Athlete') or o.name.startswith('Racing singlet') or o.name.startswith('Running shorts'))]
for name in ['Individual short hair','Race bib','Athlete number']:
 o=bpy.data.objects.get(name)
 if o:
  o.animation_data_clear();pieces.append(o)
hair=bpy.data.objects.get('Individual short hair')
if hair:hair.matrix_world=Matrix.Identity(4)
for name,pos in [('Race bib',(0,-.169,1.375)),('Athlete number',(0,-.171,1.375))]:
 o=bpy.data.objects.get(name)
 if o:
  o.location=pos;o.rotation_euler=(math.pi/2,0,0) if name=='Athlete number' else (0,0,0);o.scale=(1,1,1)
stage=bpy.data.objects.new('Character stage',None);bpy.context.collection.objects.link(stage)
for o in pieces:
 if o.parent==arm:continue
 old=o.matrix_world.copy();o.parent=stage;o.matrix_world=old
stage.location.y=-4.27

def rotate_world(name,axis,angle):
 pb=arm.pose.bones.get(name)
 if pb:
  local=pb.bone.matrix_local.to_3x3().inverted()@Vector(axis);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion(local.normalized(),math.radians(angle))
for n,a in [('upperarm01.L',29),('upperarm01.R',-25)]:rotate_world(n,(0,1,0),a)
for n in ['lowerarm01.L','lowerarm01.R']:rotate_world(n,(1,0,0),-8)
for pb in arm.pose.bones:
 if pb.name.startswith('finger'):
  f=(pb.bone.tail_local-pb.bone.head_local).normalized();bend=f.cross(Vector((0,-1,0)))
  if bend.length>.1:
   local=pb.bone.matrix_local.to_3x3().inverted()@bend.normalized();pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion(local,.20 if '-1.' in pb.name else .34)
bpy.context.view_layer.update()
setup_camera(s,'baseline');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'))
for name in ['Race bib','Athlete number']:
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)

# Restore the complete body beneath the re-tailored neckline. V5 had removed
# skin polygons under its original clothing, which must not become exposed.
old_skin=bpy.data.materials['AthleteSkin'];before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(P/'public/assets/athlete-v2.glb'))
imported=[o for o in bpy.data.objects if o not in before];native=next(o for o in imported if o.type=='MESH' and o.name.startswith('AthleteBody'))
body.vertex_groups.clear();body.data=native.data.copy()
for group in native.vertex_groups:body.vertex_groups.new(name=group.name)
body.data.materials.clear();body.data.materials.append(old_skin)
for o in imported:bpy.data.objects.remove(o,do_unlink=True)

# A scanned head keeps its authored surface and UVs; no nearest-point projection.
before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(S/'rp_eric_rigged_001_zup_t.fbx'))
added=[o for o in bpy.data.objects if o not in before];src=next(o for o in added if o.type=='MESH');eye_indices={g.index for g in src.vertex_groups if g.name in ['eye_l','eye_r']}
mesh=src.data.copy();mesh.transform(src.matrix_world)
bm=bmesh.new();bm.from_mesh(mesh)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,0,1.61),plane_no=(0,0,1),clear_inner=True,clear_outer=False)
for v in bm.verts:v.co+=Vector((.006,0,HEAD_LIFT))
for v in bm.verts:
 t=max(0,min(1,(NECK_Z+.025-v.co.z)/.025));t=t*t*(3-2*t)
 if t:
  a=math.atan2(v.co.y+.015,v.co.x);v.co.x=v.co.x*(1-t)+math.cos(a)*.060*t;v.co.y=v.co.y*(1-t)+(-.015+math.sin(a)*.062)*t
neck_ring=sorted((math.atan2(v.co.y+.015,v.co.x),math.hypot(v.co.x,v.co.y+.015)) for v in bm.verts if abs(v.co.z-NECK_Z)<.0001)
assert len(neck_ring)>10,'Missing scan neck boundary'
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
head=bpy.data.objects.new('Eric scan - original head surface',mesh);bpy.context.collection.objects.link(head);head.parent=stage;head.data.uv_layers.active.name='UVMap'
eye_faces=[f.index for f in mesh.polygons if sum(sum(g.weight for g in mesh.vertices[i].groups if g.group in eye_indices) for i in f.vertices)/len(f.vertices)>.65]
for o in added:bpy.data.objects.remove(o,do_unlink=True)
for f in head.data.polygons:f.use_smooth=True
head.data.materials.clear();skin=basic('Scanned skin and authored hair',(.3,.2,.15),.55);head.data.materials.append(skin)
nt=skin.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF')
p.inputs['IOR'].default_value=1.4;p.inputs['Subsurface Weight'].default_value=.065;p.inputs['Subsurface Radius'].default_value=(1,.42,.22);p.inputs['Subsurface Scale'].default_value=.0018;p.inputs['Specular IOR Level'].default_value=.32
def image(stem,color=True):
 tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(S/'tex'/('rp_eric_rigged_001_'+stem+'.jpg')),check_existing=True)
 if not color:tex.image.colorspace_settings.name='Non-Color'
 return tex
diff=image('dif');l.new(diff.outputs['Color'],p.inputs['Base Color'])
# The source wore a shirt. Neutralize the tiny collar rim retained below the jaw.
geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);low=n.new('ShaderNodeMath');low.operation='LESS_THAN';low.inputs[1].default_value=1.665+HEAD_LIFT;l.new(sep.outputs['Z'],low.inputs[0]);bright=n.new('ShaderNodeRGBToBW');l.new(diff.outputs['Color'],bright.inputs[0]);white=n.new('ShaderNodeMath');white.operation='GREATER_THAN';white.inputs[1].default_value=.48;l.new(bright.outputs[0],white.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(low.outputs[0],mul.inputs[0]);l.new(white.outputs[0],mul.inputs[1]);mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.39,.21,.13,1);l.new(mul.outputs[0],mix.inputs[0]);l.new(diff.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
gloss=image('gloss',False);r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=0;r.inputs['From Max'].default_value=1;r.inputs['To Min'].default_value=.73;r.inputs['To Max'].default_value=.28;l.new(gloss.outputs['Color'],r.inputs['Value']);l.new(r.outputs['Result'],p.inputs['Roughness'])
normal=image('norm',False);norm=n.new('ShaderNodeNormalMap');norm.inputs['Strength'].default_value=.65;l.new(normal.outputs['Color'],norm.inputs['Color']);l.new(norm.outputs['Normal'],p.inputs['Normal'])
eye_mat=skin.copy();eye_mat.name='Scanned eyes with wet corneal reflection';ep=eye_mat.node_tree.nodes.get('Principled BSDF')
for link in list(ep.inputs['Roughness'].links):eye_mat.node_tree.links.remove(link)
ep.inputs['Roughness'].default_value=.12;ep.inputs['Coat Weight'].default_value=.85;ep.inputs['Coat Roughness'].default_value=.035;ep.inputs['Subsurface Weight'].default_value=0
head.data.materials.append(eye_mat)
for i in eye_faces:head.data.polygons[i].material_index=1
sub=head.modifiers.new('Preserve scan silhouette smoothness','SUBSURF');sub.levels=1;sub.render_levels=1
bm=bmesh.new();bm.from_mesh(mesh);deform=bm.verts.layers.deform.active
if deform:
 for v in bm.verts:v[deform].clear()
 bm.to_mesh(mesh)
bm.free()
group=head.vertex_groups.new(name='head');group.add(list(range(len(mesh.vertices))),1,'REPLACE');mod=head.modifiers.new('Athlete native skeleton','ARMATURE');mod.object=arm

# Short surface-following strands break the scanned hair's rigid silhouette.
import numpy as np
small=diff.image.copy();small.scale(512,512);pixels=np.asarray(small.pixels[:],dtype=np.float32).reshape(512,512,4);bpy.data.images.remove(small)
hairmat=basic('Fine dark-brown hair fibers',(.018,.009,.005),.42)
cur=bpy.data.curves.new('Short groom on scanned scalp','CURVE');cur.dimensions='3D';cur.bevel_depth=.000055;cur.bevel_resolution=0;cur.resolution_u=1;cur.materials.append(hairmat)
uv=mesh.uv_layers.active.data;triangles=[]
for f in mesh.polygons:
 if f.center.z<1.755+HEAD_LIFT:continue
 for k in range(1,len(f.vertices)-1):triangles.append(([mesh.vertices[f.vertices[j]] for j in [0,k,k+1]],[uv[f.loop_indices[j]].uv.copy() for j in [0,k,k+1]]))
rng=random.Random(61021);count=0
for _ in range(100000):
 if count>=8500:break
 vs,us=rng.choice(triangles);a=rng.random();b=rng.random()
 if a+b>1:a=1-a;b=1-b
 w=[1-a-b,a,b];t=sum((u*ww for u,ww in zip(us,w)),Vector((0,0)));col=pixels[max(0,min(511,int(t.y*511))),max(0,min(511,int(t.x*511)))];root=sum((v.co*ww for v,ww in zip(vs,w)),Vector());normal=sum((v.normal*ww for v,ww in zip(vs,w)),Vector()).normalized()
 if root.z<1.755+HEAD_LIFT or float(max(col[:3]))>.29:continue
 flow=Vector((.22,.85,.12));flow=(flow-normal*normal.dot(flow)).normalized();length=.004+rng.random()*.013;lift=.0005+rng.random()*.0015
 if rng.random()<.035:lift+=.003
 sp=cur.splines.new('POLY');sp.points.add(4)
 for k,point in enumerate(sp.points):
  u=k/4;v=root+normal*(.00015+lift*math.sin(u*math.pi))+flow*length*u;point.co=(*v,1);point.radius=1-u*.88
 count+=1
groom=bpy.data.objects.new('Scalp individual fibers',cur);bpy.context.collection.objects.link(groom);groom.parent=stage

# Remove old eyes/hair and old head polygons only after saving a fair baseline.
for o in list(s.objects):
 if o!=head and (o.name.startswith('Athletehigh-poly') or o.name.startswith('Athleteshort04') or o.name=='Individual short hair'):bpy.data.objects.remove(o,do_unlink=True)
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000025)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,0,BODY_NECK_Z),plane_no=(0,0,1),clear_outer=True,clear_inner=False)
ring=[(neck_ring[-1][0]-math.tau,neck_ring[-1][1])]+neck_ring+[(neck_ring[0][0]+math.tau,neck_ring[0][1])];angles=[a for a,r in ring]
for v in bm.verts:
 t=max(0,min(1,(v.co.z-(BODY_NECK_Z-.035))/.035))*.6 if abs(v.co.x)<.095 else 0;t=t*t*(3-2*t)
 if t:
  a=math.atan2(v.co.y+.015,v.co.x);j=bisect.bisect_right(angles,a);aa,ra=ring[j-1];ab,rb=ring[j];r=ra+(rb-ra)*(a-aa)/(ab-aa);v.co.x=v.co.x*(1-t)+math.cos(a)*r*t;v.co.y=v.co.y*(1-t)+(-.015+math.sin(a)*r)*t
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free();body.data.update()
for poly in body.data.polygons:poly.use_smooth=True
sub=body.modifiers.new('Fine anatomical surface','SUBSURF');sub.levels=1;sub.render_levels=2
bs=bpy.data.materials['AthleteSkin'];nt=bs.node_tree;bp=nt.nodes.get('Principled BSDF')
bp.inputs['Subsurface Weight'].default_value=.075;bp.inputs['Subsurface Scale'].default_value=.002;bp.inputs['Roughness'].default_value=.49;bp.inputs['Coat Weight'].default_value=0
if bp.inputs['Base Color'].links:
 old=bp.inputs['Base Color'].links[0].from_socket;nt.links.remove(bp.inputs['Base Color'].links[0]);mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.76,.61,.52,1);nt.links.new(old,mix.inputs[1])
 geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);fac=nt.nodes.new('ShaderNodeMapRange');fac.inputs['From Min'].default_value=1.50;fac.inputs['From Max'].default_value=1.61;fac.inputs['To Max'].default_value=.2;nt.links.new(sep.outputs['Z'],fac.inputs['Value']);shade=nt.nodes.new('ShaderNodeMixRGB');shade.blend_type='MULTIPLY';shade.inputs[2].default_value=(.76,.64,.55,1);nt.links.new(fac.outputs[0],shade.inputs[0]);nt.links.new(mix.outputs[0],shade.inputs[1]);nt.links.new(shade.outputs[0],bp.inputs['Base Color'])

def seam(garment,material):
 bm=bmesh.new();bm.from_mesh(garment.data);edges=[(e.verts[0].co.copy()+e.verts[0].normal*.001,e.verts[1].co.copy()+e.verts[1].normal*.001) for e in bm.edges if e.is_boundary];bm.free()
 curve=bpy.data.curves.new(garment.name+' tailored seams','CURVE');curve.dimensions='3D';curve.bevel_depth=.00035;curve.bevel_resolution=2
 for a,b in edges:
  sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
 o=bpy.data.objects.new(curve.name,curve);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 tree=KDTree(len(garment.data.vertices))
 for v in garment.data.vertices:tree.insert(v.co,v.index)
 tree.balance()
 groups={g.index:o.vertex_groups.new(name=g.name) for g in garment.vertex_groups}
 for v in o.data.vertices:
  idx=tree.find(v.co)[1]
  for g in garment.data.vertices[idx].groups:groups[g.group].add([v.index],g.weight,'REPLACE')
 mod=o.modifiers.new('Follow cloth pose','ARMATURE');mod.object=arm;o.parent=stage

stitch=basic('Burgundy stitched binding',(.23,.009,.006),.7)
for name in ['Racing singlet - separate garment','Running shorts - separate garment']:
 g=bpy.data.objects[name]
 bm=bmesh.new();bm.from_mesh(g.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000025)
 boundary=[v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
 for _ in range(12):
  updates={}
  for v in boundary:
   ns=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
   if len(ns)==2:updates[v]=v.co*.4+(ns[0].co+ns[1].co)*.3
  for v,co in updates.items():v.co=co
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g.data);bm.free()
 for v in g.data.vertices:
  z=v.co.z;amount=.0032*(.55+.45*math.sin(v.co.x*37+z*23))*math.exp(-((z-1.13)/.13)**2)
  v.co+=v.normal*(amount+.004)
 for mod in list(g.modifiers):
  if mod.type=='SOLIDIFY':g.modifiers.remove(mod)
 sub=g.modifiers.new('Cloth surface smoothing','SUBSURF');sub.levels=1;sub.render_levels=2
 solid=g.modifiers.new('Tailored fabric thickness','SOLIDIFY');solid.thickness=.0015;solid.offset=0
 seam(g,stitch if name.startswith('Racing') else basic('Shorts binding',(.008,.012,.014),.7))
 gm=g.data.materials[0];gp=gm.node_tree.nodes.get('Principled BSDF');gp.inputs['Roughness'].default_value=.72;gp.inputs['Sheen Weight'].default_value=.3
 if name.startswith('Racing'):gp.inputs['Base Color'].default_value=(.32,.012,.008,1)

# Join the two neck borders with actual connected geometry, so subdivision does
# not shrink two independent open borders into a visible horizontal crack.
head_count=len(head.data.vertices)
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.object.join()
bm=bmesh.new();bm.from_mesh(body.data);uv=bm.loops.layers.uv.get('UVMap');scan_uv=bm.loops.layers.uv.new('ScanNeckUV')
bottom=sorted([v for v in bm.verts if abs(v.co.z-BODY_NECK_Z)<.0001 and any(e.is_boundary for e in v.link_edges)],key=lambda v:math.atan2(v.co.y+.015,v.co.x))
top=sorted([v for v in bm.verts if abs(v.co.z-NECK_Z)<.0001 and any(e.is_boundary for e in v.link_edges)],key=lambda v:math.atan2(v.co.y+.015,v.co.x))
assert len(bottom)>10 and len(top)>10,(len(bottom),len(top))
body_uv={v:v.link_loops[0][uv].uv.copy() for v in bottom};head_uv={v:v.link_loops[0][uv].uv.copy() for v in top}
transition=basic('Continuous neck skin transition',(.18,.10,.06),.5);nt=transition.node_tree;np=nt.nodes.get('Principled BSDF');np.inputs['Subsurface Weight'].default_value=.075;np.inputs['Subsurface Radius'].default_value=(1,.42,.22);np.inputs['Subsurface Scale'].default_value=.002;np.inputs['IOR'].default_value=1.4
geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);r=nt.nodes.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=BODY_NECK_Z;r.inputs['From Max'].default_value=NECK_Z;nt.links.new(sep.outputs['Z'],r.inputs['Value']);blend=nt.nodes.new('ShaderNodeMixRGB');blend.inputs[1].default_value=(.20,.11,.07,1);blend.inputs[2].default_value=(.15,.075,.046,1);nt.links.new(r.outputs[0],blend.inputs[0]);nt.links.new(blend.outputs[0],np.inputs['Base Color'])
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1600;noise.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],noise.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00006;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],np.inputs['Normal'])
body.data.materials.append(transition);material_index=len(body.data.materials)-1
# Fade both neighboring skin shaders into the same neck colors instead of
# leaving a hard material boundary around the connecting surface.
for material,is_head in [(bs,False),(skin,True)]:
 tree=material.node_tree;nodes=tree.nodes;links=tree.links;principled=nodes.get('Principled BSDF');old_color=principled.inputs['Base Color'].links[0].from_socket
 geom=nodes.new('ShaderNodeNewGeometry');xyz=nodes.new('ShaderNodeSeparateXYZ');links.new(geom.outputs['Position'],xyz.inputs[0]);height=nodes.new('ShaderNodeMapRange')
 if is_head:
  height.inputs['From Min'].default_value=NECK_Z+.015;height.inputs['From Max'].default_value=NECK_Z+.050;height.inputs['To Min'].default_value=1;height.inputs['To Max'].default_value=0;color=(.15,.075,.046,1)
 else:
  height.inputs['From Min'].default_value=BODY_NECK_Z-.035;height.inputs['From Max'].default_value=BODY_NECK_Z;color=(.20,.11,.07,1)
 links.new(xyz.outputs['Z'],height.inputs['Value']);factor=height.outputs[0]
 if is_head:
  depth=nodes.new('ShaderNodeMapRange');depth.inputs['From Min'].default_value=-.105-4.27;depth.inputs['From Max'].default_value=-.065-4.27;links.new(xyz.outputs['Y'],depth.inputs['Value']);mult=nodes.new('ShaderNodeMath');mult.operation='MULTIPLY';links.new(height.outputs[0],mult.inputs[0]);links.new(depth.outputs[0],mult.inputs[1]);factor=mult.outputs[0]
 fade=nodes.new('ShaderNodeMixRGB');fade.inputs[2].default_value=color;links.new(factor,fade.inputs[0]);links.new(old_color,fade.inputs[1]);links.new(fade.outputs[0],principled.inputs['Base Color'])
angles_b=[math.atan2(v.co.y+.015,v.co.x) for v in bottom];angles_t=[math.atan2(v.co.y+.015,v.co.x) for v in top]
faces=[];i=j=0
while i<len(bottom) or j<len(top):
 nb=angles_b[i+1] if i+1<len(bottom) else angles_b[0]+math.tau
 nh=angles_t[j+1] if j+1<len(top) else angles_t[0]+math.tau
 if i<len(bottom) and (j==len(top) or nb<=nh):verts=[bottom[i%len(bottom)],bottom[(i+1)%len(bottom)],top[j%len(top)]];i+=1
 else:verts=[bottom[i%len(bottom)],top[(j+1)%len(top)],top[j%len(top)]];j+=1
 f=bm.faces.new(verts);f.material_index=material_index;f.smooth=True;faces.append(f)
 for loop in f.loops:
  v=loop.vert;b=min(bottom,key=lambda q:(q.co.xy-v.co.xy).length_squared);h=min(top,key=lambda q:(q.co.xy-v.co.xy).length_squared)
  loop[uv].uv=body_uv[b];loop[scan_uv].uv=head_uv[h]
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
for poly in body.data.polygons:poly.use_smooth=True
for edge in body.data.edges:edge.use_edge_sharp=False
body.data.normals_split_custom_set([(0,0,0)]*len(body.data.loops))
body.data.uv_layers.active=body.data.uv_layers['UVMap']

# A complete, newly tailored compression top replaces the cut-out old vest.
# Its ribbed high collar is an explicit wardrobe choice for this candidate.
for o in list(s.objects):
 if o.name.startswith('Racing singlet - separate garment'):bpy.data.objects.remove(o,do_unlink=True)
def ease(a,b,x):t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
polys=[f for f in body.data.polygons if 1.09<f.center.z<1.69 and abs(f.center.x)<.24-.155*ease(1.54,1.605,f.center.z)]
used=sorted({i for f in polys for i in f.vertices});mapping={i:j for j,i in enumerate(used)};points=[]
for i in used:
 v=body.data.vertices[i];co=v.co+v.normal*.009;t=ease(1.585,1.625,co.z)
 if t:
  a=math.atan2(co.y+.015,co.x);co.x=co.x*(1-t)+math.cos(a)*.068*t;co.y=co.y*(1-t)+(-.015+math.sin(a)*.075)*t
 points.append(co)
cloth=bpy.data.meshes.new('Performance top continuous surface');cloth.from_pydata(points,[],[[mapping[i] for i in f.vertices] for f in polys]);cloth.update();top_obj=bpy.data.objects.new('Red graphite high-collar training top',cloth);bpy.context.collection.objects.link(top_obj);top_obj.parent=stage
for group in body.vertex_groups:
 vg=top_obj.vertex_groups.new(name=group.name)
 for old,new in mapping.items():
  for item in body.data.vertices[old].groups:
   if item.group==group.index and item.weight>0:vg.add([new],item.weight,'REPLACE')
bm=bmesh.new();bm.from_mesh(cloth);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000025);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,0,1.675),plane_no=(0,0,1),clear_outer=True)
boundary=[v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
for _ in range(24):
 updates={}
 for v in boundary:
  near=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
  if len(near)==2:updates[v]=v.co*.5+(near[0].co+near[1].co)*.25
 for v,co in updates.items():v.co=co
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cloth);bm.free()
for f in cloth.polygons:f.use_smooth=True
tech=basic('Red graphite training knit',(.23,.006,.004),.85);cloth.materials.append(tech);nt=tech.node_tree;np=nt.nodes.get('Principled BSDF');np.inputs['Sheen Weight'].default_value=.35;np.inputs['Specular IOR Level'].default_value=.18
geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0]);zone=nt.nodes.new('ShaderNodeMath');zone.operation='GREATER_THAN';zone.inputs[1].default_value=1.57;nt.links.new(xyz.outputs['Z'],zone.inputs[0]);col=nt.nodes.new('ShaderNodeMixRGB');col.inputs[1].default_value=(.23,.006,.004,1);col.inputs[2].default_value=(.012,.018,.019,1);nt.links.new(zone.outputs[0],col.inputs[0]);nt.links.new(col.outputs[0],np.inputs['Base Color'])
wave=nt.nodes.new('ShaderNodeTexWave');wave.bands_direction='X';wave.inputs['Scale'].default_value=800;nt.links.new(geo.outputs['Position'],wave.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.00012;nt.links.new(wave.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs[0],np.inputs['Normal'])
mod=top_obj.modifiers.new('Follow athlete skeleton','ARMATURE');mod.object=arm;sub=top_obj.modifiers.new('Tailored smooth surface','SUBSURF');sub.levels=2;sub.render_levels=2;solid=top_obj.modifiers.new('Knit thickness','SOLIDIFY');solid.thickness=.0012;solid.offset=0
# Hide only the neck skin enclosed by this finished collar, with a small margin
# below its upper hem. This prevents the Adam's apple penetrating the fabric.
bm=bmesh.new();bm.from_mesh(body.data);covered=[f for f in bm.faces if 1.595<f.calc_center_median().z<1.670 and abs(f.calc_center_median().x)<.09];bmesh.ops.delete(bm,geom=covered,context='FACES');bm.to_mesh(body.data);bm.free()
setup_camera(s,'portrait');bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'athlete-lookdev.blend'))
(P/'outputs/checks/realism-v6/build-report.json').write_text(json.dumps({'scanVertices':head_count,'scanTextureResolution':list(diff.image.size),'originalScanSurface':True,'neckBoundaryVertices':len(neck_ring),'neckBridgeFaces':len(faces),'groomStrands':count,'eyeSurfaceFaces':len(eye_faces),'baseBody':'existing MakeHuman CC0','headAsset':'Renderpeople Eric free rigged 001','renderMode':'local Cycles CPU','originalV5Preserved':True,'motionValidated':False},indent=2))
print('V6_SCENE_READY',head_count,flush=True)
