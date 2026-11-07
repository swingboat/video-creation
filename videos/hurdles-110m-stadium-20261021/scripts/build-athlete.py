"""Build a continuous, weighted athlete from MakeHuman CC0 anatomy.
Run: blender -b --python scripts/build-athlete.py
All paths resolve inside the current project.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path.cwd();A=P/'public/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
verts=[];faces=[];uvs=[];fuv=[];group=''
for line in (A/'human-base.obj').read_text().splitlines():
 s=line.split()
 if not s:continue
 if s[0]=='v':verts.append(Vector(map(float,s[1:4])))
 elif s[0]=='vt':uvs.append(tuple(map(float,s[1:3])))
 elif s[0]=='g':group=s[1]
 elif s[0]=='f' and group=='body':
  faces.append([int(t.split('/')[0])-1 for t in s[1:]]);fuv.append([int(t.split('/')[1])-1 if '/' in t else 0 for t in s[1:]])
# The macro targets sculpt an adult, lean athletic male; local muscle targets
# add definition without turning the runner into a bodybuilder.
for name,w in [('caucasian-male-young.target',1),('universal-male-young-maxmuscle-minweight.target',0.72),('universal-male-young-maxmuscle-averageweight.target',0.28)]+[(s+'-muscle-incr.target',.18) for s in ['l-upperarm','r-upperarm','l-lowerleg','r-lowerleg','l-upperleg','r-upperleg']]:
 for line in (A/name).read_text().splitlines():
  q=line.split()
  if len(q)==4 and not line.startswith('#'):
   i=int(q[0]);verts[i]+=Vector(map(float,q[1:]))*w
bodyids=set(i for f in faces for i in f);lo=min(verts[i].y for i in bodyids);hi=max(verts[i].y for i in bodyids);scale=1.88/(hi-lo)
# Original Y-up -> Blender Z-up. glTF export restores Y-up.
def conv(v):return Vector((v.x*scale,-v.z*scale,(v.y-lo)*scale))
rig=json.loads((A/'default.mhskel').read_text());weights=json.loads((A/'default_weights.mhw').read_text())['weights']
def joint(n):
 ids=rig['joints'][n];v=sum((verts[i] for i in ids),Vector())/len(ids);return conv(v)
arm=bpy.data.armatures.new('AthleteSkeleton');obj=bpy.data.objects.new('AthleteRig',arm);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n,b in rig['bones'].items():
 bone=arm.edit_bones.new(n);bone.head=joint(b['head']);bone.tail=joint(b['tail'])
 if (bone.tail-bone.head).length<.0001:bone.tail.z+=.001
for n,b in rig['bones'].items():
 if b['parent']:arm.edit_bones[n].parent=arm.edit_bones[b['parent']]
bpy.ops.object.mode_set(mode='OBJECT')
# Keep the full original weighted topology below the scanned head, excluding
# bare feet, which are replaced by anatomically shaped track spikes.
keep=[];keepuv=[]
for f,uv in zip(faces,fuv):
 av=sum((conv(verts[i]) for i in f),Vector())/len(f)
 if av.z<.105:continue
 keep.append(f);keepuv.append(uv)
mesh=bpy.data.meshes.new('ContinuousAthleticAnatomy');mesh.from_pydata([conv(v) for v in verts],[],keep);mesh.update();body=bpy.data.objects.new('AthleteBody',mesh);bpy.context.collection.objects.link(body)
uv=mesh.uv_layers.new(name='UVMap')
for poly,ids in zip(mesh.polygons,keepuv):
 for li,ui in zip(poly.loop_indices,ids):uv.data[li].uv=uvs[ui]
def mat(name,col,rough=.6):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
 return m
skin=mat('Skin',(.52,.31,.20),.58);headmat=mat('ScannedFace',(.8,.62,.47),.62);vest=mat('RacingSinglet',(.72,.055,.025),.78);shorts=mat('CompressionShorts',(.015,.024,.029),.75)
for m in [skin,vest,shorts,headmat]:body.data.materials.append(m)
# Fit the scanned facial surface onto the continuous MakeHuman topology.
# The neck remains the original weighted, continuous surface: no rigid seam.
from mathutils.bvhtree import BVHTree
bpy.ops.import_scene.gltf(filepath=str(A/'lee-head.glb'))
scan_objects=[o for o in bpy.context.selected_objects if o.type=='MESH']
scan=scan_objects[0];bpy.context.view_layer.update()
points=[scan.matrix_world@v.co for v in scan.data.vertices];mn=Vector((min(v.x for v in points),min(v.y for v in points),min(v.z for v in points)));mx=Vector((max(v.x for v in points),max(v.y for v in points),max(v.z for v in points)))
ss=.315/(mx.z-mn.z);center=(mn+mx)/2
sv=[Vector(((v.x-center.x)*ss,(v.y-center.y)*ss-.018,1.885-(mx.z-v.z)*ss)) for v in points]
scan.data.calc_loop_triangles();tris=[list(t.vertices) for t in scan.data.loop_triangles]
bvh=BVHTree.FromPolygons(sv,tris,all_triangles=True)
sourceuv=scan.data.uv_layers.active.data
triuv=[[sourceuv[li].uv.copy() for li in t.loops] for t in scan.data.loop_triangles]
def bary(p,a,b,c):
 v0=b-a;v1=c-a;v2=p-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-14:return (1,0,0)
 v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;return 1-v-w,v,w
mapped={}
for vertex in mesh.vertices:
 if vertex.co.z<1.58 or (vertex.co.z<1.65 and abs(vertex.co.x)>.115):continue
 point,normal,ti,dist=bvh.find_nearest(vertex.co)
 if point is None:continue
 # Full fit above the chin, smooth blend through the original neck.
 blend=max(0,min(1,(vertex.co.z-1.58)/.075));blend=blend*blend*(3-2*blend)
 vertex.co=vertex.co.lerp(point,blend)
 a,b,c=[sv[i] for i in tris[ti]];w=bary(point,a,b,c);u=triuv[ti]
 mapped[vertex.index]=u[0]*w[0]+u[1]*w[1]+u[2]*w[2]
for poly in mesh.polygons:
 if sum(mesh.vertices[i].co.z for i in poly.vertices)/len(poly.vertices)>1.67:
  poly.material_index=3
  for li in poly.loop_indices:
   vi=mesh.loops[li].vertex_index
   if vi in mapped:uv.data[li].uv=mapped[vi]
 else:poly.material_index=0
 poly.use_smooth=True
for o in scan_objects:bpy.data.objects.remove(o,do_unlink=True)
mesh.update()
for n,entries in weights.items():
 vg=body.vertex_groups.new(name=n)
 for i,w in entries:
  if i<len(verts):vg.add([i],w,'REPLACE')
body.parent=obj;mod=body.modifiers.new('Armature','ARMATURE');mod.object=obj
sub=body.modifiers.new('Smooth anatomical surface','SUBSURF');sub.levels=1;sub.render_levels=1
# Track spikes: cross-section loft, curved upper, separate outsole, laces.
white=mat('ShoeUpper',(.86,.88,.79),.6);lime=mat('ShoeOutsole',(.62,.82,.04),.5)
for side in ['L','R']:
 foot=joint(rig['bones']['foot.'+side]['head']);cx=foot.x;cz=-foot.y
 for sole in [False,True]:
  vs=[];fs=[];N=24;R=14
  for j in range(R):
   u=j/(R-1);long=-.105+.31*u;wid=.028+.028*math.sin(math.pi*u)**.6;h=.042+.042*math.sin(math.pi*u)
   for k in range(N):
    ang=2*math.pi*k/N
    x=cx+wid*math.cos(ang);z=.055+(.018 if sole else h)*math.sin(ang);z=max(.018,z)
    if sole:z=.019+.009*math.sin(ang)
    vs.append((x,-(cz+long),z))
  for j in range(R-1):
   for k in range(N):a=j*N+k;b=j*N+(k+1)%N;fs.append((a,b,b+N,a+N))
  fs += [tuple(reversed(range(N))),tuple((R-1)*N+k for k in range(N))]
  me=bpy.data.meshes.new('TrackSpike');me.from_pydata(vs,[],fs);me.materials.append(lime if sole else white);o=bpy.data.objects.new('SpikeSole.'+side if sole else 'SpikeUpper.'+side,me);bpy.context.collection.objects.link(o)
  for p in me.polygons:p.use_smooth=True
  vg=o.vertex_groups.new(name='foot.'+side);vg.add(list(range(len(vs))),1,'REPLACE');o.parent=obj;mod=o.modifiers.new('Armature','ARMATURE');mod.object=obj
  sub=o.modifiers.new('Shoe smoothing','SUBSURF');sub.levels=1
# Document the actual rest-joint coordinates for inspection and IK.
meta={n:{'head':list(joint(b['head'])),'tail':list(joint(b['tail'])),'parent':b['parent']} for n,b in rig['bones'].items()}
(P/'outputs/checks/rig-rest-blender.json').write_text(json.dumps(meta,indent=2))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(A/'athlete-body.glb'),export_format='GLB',export_animations=False,export_apply=True,export_yup=True)
print('ATHLETE_EXPORTED',len(mesh.vertices),len(mesh.polygons),len(rig['bones']))
