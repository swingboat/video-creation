"""Native MakeHuman topology + authored skin/eyes/hair/shoes. No scan projection."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path.cwd();A=P/'public/assets';S=P/'sources/makehuman-system'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
verts=[];faces=[];uvs=[];faceuv=[];group=''
for line in (A/'human-base.obj').read_text().splitlines():
 s=line.split()
 if not s:continue
 if s[0]=='v':verts.append(Vector(map(float,s[1:4])))
 elif s[0]=='vt':uvs.append(tuple(map(float,s[1:3])))
 elif s[0]=='g':group=s[1]
 elif s[0]=='f' and group=='body':faces.append([int(t.split('/')[0])-1 for t in s[1:]]);faceuv.append([int(t.split('/')[1])-1 for t in s[1:]])
for name,w in [('caucasian-male-young.target',1),('universal-male-young-maxmuscle-minweight.target',.35),('universal-male-young-maxmuscle-averageweight.target',.65)]:
 for line in (A/name).read_text().splitlines():
  q=line.split()
  if len(q)==4 and not line.startswith('#'):verts[int(q[0])]+=Vector(map(float,q[1:]))*w
ids=set(i for f in faces for i in f);lo=min(verts[i].y for i in ids);hi=max(verts[i].y for i in ids);scale=1.88/(hi-lo)
def conv(v):return Vector((v.x*scale,-v.z*scale,(v.y-lo)*scale))
rig=json.loads((A/'default.mhskel').read_text());weights=json.loads((A/'default_weights.mhw').read_text())['weights']
def joint(n):return conv(sum((verts[i] for i in rig['joints'][n]),Vector())/len(rig['joints'][n]))
arm=bpy.data.armatures.new('AthleteSkeleton');obj=bpy.data.objects.new('AthleteRig',arm);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n,b in rig['bones'].items():
 bone=arm.edit_bones.new(n);bone.head=joint(b['head']);bone.tail=joint(b['tail'])
 if (bone.tail-bone.head).length<.0001:bone.tail.z+=.001
for n,b in rig['bones'].items():
 if b['parent']:arm.edit_bones[n].parent=arm.edit_bones[b['parent']]
bpy.ops.object.mode_set(mode='OBJECT')
def material(name,texture,rough=.65,alpha=False,normal=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
 if texture:
  im=bpy.data.images.load(str(texture),check_existing=True);tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  if alpha:m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED';m.use_transparency_overlap=False
 if normal:
  im=bpy.data.images.load(str(normal),check_existing=True);im.colorspace_settings.name='Non-Color';tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.5;m.node_tree.links.new(tex.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
 return m
skin=material('AthleteSkin',S/'skins/young_caucasian_male2/young_lightskinned_male_diffuse2.jpg',.58)
hairmat=material('AthleteHair',S/'hair/short04/short04_diffuse.png',.82,True)
eyemat=material('AthleteEyes',S/'eyes/materials/brown_eye.png',.18,True)
shoemat=material('TrackShoes',S/'clothes/shoes05/shoes05_diffuse.jpg',.66)
def make_mesh(name,ps,fs,uvs,fu,mat):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(ps,[],fs);mesh.update();mesh.materials.append(mat);ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);uv=mesh.uv_layers.new(name='UVMap')
 for poly,ui in zip(mesh.polygons,fu):
  poly.use_smooth=True
  for li,ii in zip(poly.loop_indices,ui):uv.data[li].uv=uvs[ii]
 ob.parent=obj;mod=ob.modifiers.new('Armature','ARMATURE');mod.object=obj
 return ob
def bind(ob,w):
 for n,entries in w.items():
  vg=ob.vertex_groups.new(name=n)
  for i,value in entries:
   if i<len(ob.data.vertices) and value>0:vg.add([i],value,'REPLACE')
keep=[];fuv=[]
for f,uv in zip(faces,faceuv):
 av=sum((conv(verts[i]) for i in f),Vector())/len(f)
 if av.z<.09:continue
 keep.append(f);fuv.append(uv)
body=make_mesh('AthleteBody',[conv(v) for v in verts],keep,uvs,fuv,skin);bind(body,weights)
sub=body.modifiers.new('AnatomicalSurface','SUBSURF');sub.levels=1;sub.render_levels=1
# Fit authored assets with the official barycentric MakeHuman mapping.
# The offsets are scaled per axis to the deformed reference body.
def asset(folder,stem,mat,binding):
 path=S/folder;lines=(path/(stem+'.mhclo')).read_text().splitlines();axis_scale=[1.,1.,1.];mapping=[];reading=False
 for line in lines:
  s=line.split()
  if not s or s[0].startswith('#'):continue
  if s[0] in ['x_scale','y_scale','z_scale']:
   ax={'x_scale':0,'y_scale':1,'z_scale':2}[s[0]];axis_scale[ax]=abs(verts[int(s[1])][ax]-verts[int(s[2])][ax])/float(s[3])
  elif s[0]=='verts':reading=True
  elif reading:
   if len(s)==1 and s[0].isdigit():mapping.append(verts[int(s[0])].copy())
   elif len(s)==9:
    ids=list(map(int,s[:3]));ws=list(map(float,s[3:6]));offset=list(map(float,s[6:9]));mapping.append(sum((verts[i]*w for i,w in zip(ids,ws)),Vector())+Vector([offset[a]*axis_scale[a] for a in range(3)]))
   elif mapping:reading=False
 aps=[];afs=[];auv=[];afu=[]
 for line in (path/(stem+'.obj')).read_text().splitlines():
  s=line.split()
  if not s:continue
  if s[0]=='v':aps.append(Vector(map(float,s[1:4])))
  elif s[0]=='vt':auv.append(tuple(map(float,s[1:3])))
  elif s[0]=='f':afs.append([int(t.split('/')[0])-1 for t in s[1:]]);afu.append([int(t.split('/')[1])-1 for t in s[1:]])
 assert len(mapping)==len(aps),(stem,len(mapping),len(aps))
 ob=make_mesh('Athlete'+stem,[conv(v) for v in mapping],afs,auv,afu,mat)
 if binding=='head':bind(ob,{'head':[(i,1.) for i in range(len(mapping))]})
 elif binding=='eyes':bind(ob,{'eye.L':[(i,1.) for i,v in enumerate(mapping) if v.x>0],'eye.R':[(i,1.) for i,v in enumerate(mapping) if v.x<=0]})
 else:
  wfile=path/(stem+'.mhw')
  if wfile.exists():bind(ob,json.loads(wfile.read_text())['weights'])
  else:bind(ob,{'foot.L':[(i,1.) for i,v in enumerate(mapping) if v.x>0],'foot.R':[(i,1.) for i,v in enumerate(mapping) if v.x<=0]})
 return ob
hair=asset('hair/short04','short04',hairmat,'head')
eyes=asset('eyes/high-poly','high-poly',eyemat,'eyes')
shoes=asset('clothes/shoes05','shoes05',shoemat,'weights');sub=shoes.modifiers.new('ShoeSurface','SUBSURF');sub.levels=1
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'athlete-v2.glb'),export_format='GLB',export_animations=False,export_apply=True,export_yup=True)
print('V2_EXPORTED',len(body.data.vertices),len(arm.bones))
