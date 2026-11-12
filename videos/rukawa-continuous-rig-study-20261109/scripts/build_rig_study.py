"""Continuous skeletal deformation study. Real weighted human mesh, no sprite swaps."""
import bpy,bmesh,math,json,sys,time
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];FPS=30;COUNT=150
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'public/models/human-base.glb'))
scene=bpy.context.scene
source_arm=next(o for o in scene.objects if o.type=='ARMATURE')
source_body=bpy.data.objects['AthleteBody'];source_eye=bpy.data.objects['Athletehigh-poly'];source_shoes=bpy.data.objects['Athleteshoes05']
for o in list(scene.objects):
 if o not in [source_arm,source_body,source_eye,source_shoes] and o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
rest={b.name:b.matrix_local.copy() for b in source_arm.data.bones}
rest_inv={n:m.inverted() for n,m in rest.items()}
bones=list(source_arm.data.bones)
head={b.name:b.head_local.copy() for b in bones};tail={b.name:b.tail_local.copy() for b in bones}
parent={b.name:b.parent.name if b.parent else None for b in bones}

def sat(x):return max(0.,min(1.,x))
def smooth(a,b,t):u=sat((t-a)/(b-a));return u*u*u*(10+u*(-15+6*u))
def mix(a,b,u):return Vector(a).lerp(Vector(b),u)
def hermite(t,a,b,va,vb,sa=0,sb=0):
 u=sat((t-a)/(b-a));d=b-a
 return (2*u**3-3*u*u+1)*va+(u**3-2*u*u+u)*d*sa+(-2*u**3+3*u*u)*vb+(u**3-u*u)*d*sb

def ballistic(t,start,height):
 duration=math.sqrt(8*height/9.81);u=t-start
 return (4*height/duration*u-4*height/duration**2*u*u) if 0<u<duration else 0.

def hip_delta(t,kind):
 if kind=='shooter':
  if t<.55:return 0.
  if t<1.25:return hermite(t,.55,1.25,0,-.20)
  if t<1.62:return hermite(t,1.25,1.62,-.20,0,0,math.sqrt(2*9.81*.41))
  land=1.62+math.sqrt(8*.41/9.81)
  if t<land:return ballistic(t,1.62,.41)
  if t<land+.17:return hermite(t,land,land+.17,0,-.18,-math.sqrt(2*9.81*.41),0)
  return hermite(t,land+.17,land+.68,-.18,0)
 if kind=='defender':
  start=1.88;height=.23;land=start+math.sqrt(8*height/9.81)
  if t<1.36:return -.05
  if t<start:return hermite(t,1.36,start,-.05,0,0,math.sqrt(2*9.81*height))-.09*math.sin(math.pi*sat((t-1.36)/(start-1.36)))**2
  if t<land:return ballistic(t,start,height)
  if t<land+.16:return hermite(t,land,land+.16,0,-.12,-math.sqrt(2*9.81*height),0)
  return hermite(t,land+.16,land+.56,-.12,-.04)
 return -.035-.016*math.sin(t*2.1)**2

def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);return m
skin=mat('Study / skin',(.72,.47,.32));ivory=mat('Study / ivory',(.86,.84,.75));black=mat('Study / ink',(.025,.032,.045));red=mat('Study / Shohoku red',(.62,.024,.036));navy=mat('Study / opponent navy',(.03,.07,.16));eyewhite=mat('Study / eye white',(.85,.84,.77));iris=mat('Study / iris',(.015,.025,.04))
source_body.data.materials.clear();source_body.data.materials.append(skin)
source_eye.data.materials.clear();source_eye.data.materials.append(eyewhite)
source_shoes.data.materials.clear();source_shoes.data.materials.append(ivory)
for p in source_body.data.polygons:p.use_smooth=True

def group_copy(src,dst):
 for g in src.vertex_groups:
  ng=dst.vertex_groups.new(name=g.name)
  for v in src.data.vertices:
   for gg in v.groups:
    if gg.group==g.index and gg.weight>0:ng.add([v.index],gg.weight,'REPLACE')

def shirt_cond(v):
 x=abs(v.x);u=smooth(.055,.115,x);upper=1.495+.091*u;return 1.09<v.z<upper and x<.235-.073*smooth(1.34,1.54,v.z)
def shorts_cond(v):return .775<v.z<1.10 and abs(v.x)<.34

def garment(name,cond,pad,material):
 fs=[f for f in source_body.data.polygons if cond(f.center)];used=sorted({i for f in fs for i in f.vertices});mp={i:j for j,i in enumerate(used)}
 d=bpy.data.meshes.new(name);d.from_pydata([source_body.data.vertices[i].co+source_body.data.vertices[i].normal*pad for i in used],[],[[mp[i] for i in f.vertices] for f in fs]);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);d.materials.append(material)
 for g in source_body.vertex_groups:
  vg=o.vertex_groups.new(name=g.name)
  for old,new in mp.items():
   for item in source_body.data.vertices[old].groups:
    if item.group==g.index and item.weight>0:vg.add([new],item.weight,'REPLACE')
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 for p in d.polygons:p.use_smooth=True
 am=o.modifiers.new('Continuous cloth skinning','ARMATURE');am.object=source_arm;am.use_deform_preserve_volume=True
 solid=o.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.002;solid.offset=0
 o.parent=source_arm;return o
shirt=garment('Continuous jersey',shirt_cond,.014,red);shorts=garment('Continuous shorts',shorts_cond,.022,red)
# Remove only the hidden body faces; keep each deform layer with the mesh.
bm=bmesh.new();bm.from_mesh(source_body.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if shirt_cond(f.calc_center_median()) or shorts_cond(f.calc_center_median())],context='FACES')
bm.to_mesh(source_body.data);bm.free();source_body.data.update()
for o in [source_body,source_eye,source_shoes]:
 for mod in o.modifiers:
  if mod.type=='ARMATURE':mod.use_deform_preserve_volume=True
# A simple scalp and eyes keep this motion-study model readable; appearance is not final.
scalp=garment('Study scalp',lambda v:v.z>1.825 or (v.z>1.75 and v.y>-.025),.006,black)
# scalp uses a rigid head weight to avoid deforming with unrelated nearby bones.
scalp.vertex_groups.clear();g=scalp.vertex_groups.new(name='head');g.add(list(range(len(scalp.data.vertices))),1,'REPLACE')
for side in ['L','R']:
 center=head['eye.'+side]+Vector((0,-.011,0))
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=center)
 o=bpy.context.object;o.name='Study iris '+side;o.scale=(.006,.003,.006);bpy.ops.object.transform_apply(location=True,rotation=False,scale=True);o.data.materials.append(iris);o.parent=source_arm
 vg=o.vertex_groups.new(name='eye.'+side);vg.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('Eye bone','ARMATURE');mod.object=source_arm
source_meshes=[o for o in scene.objects if o.type=='MESH']
# Shoe contact data is read from the actual source mesh, separately for each foot.
foot_data={}
for side,sign in [('L',1),('R',-1)]:
 vs=[v.co.copy() for v in source_shoes.data.vertices if v.co.x*sign>0]
 zmin=min(v.z for v in vs);ymin=min(v.y for v in vs)
 pivot=Vector((head['foot.'+side].x,ymin,zmin))
 foot_data[side]={'sole_min':zmin,'pivot':pivot}

def cube(n,loc,dims,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o

def curve(n,pts,r,ma):
 d=bpy.data.curves.new(n,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=1;s=d.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(n,d);scene.collection.objects.link(o);d.materials.append(ma);return o
wood=mat('Court warm maple',(.55,.38,.21));green=mat('Court deep teal',(.08,.24,.25));gray=mat('Study wall',(.55,.61,.62));line=mat('Court line',(.89,.85,.72));orange=mat('Basketball',(.78,.27,.055))
cube('Court floor',(0,-1,-.05),(14,16,.1),wood);cube('Paint',(0,-4,.003),(4.9,4,.006),green)
for x in [-6.5,6.5]:curve('Sideline',[(x,-8,.012),(x,6,.012)],.022,line)
curve('Three point arc',[(6.75*math.cos(a),-5.3+6.75*math.sin(a),.012) for a in [i*math.pi/120 for i in range(121)]],.025,line)
curve('Key outline',[(-2.45,-6,.015),(-2.45,-2,.015),(2.45,-2,.015),(2.45,-6,.015)],.024,line)
for y in [-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5]:curve('Floor board seam',[(-6.5,y,.008),(6.5,y,.008)],.002,line)
cube('Back wall',(-5.6,-.7,1.8),(.15,14,3.6),gray)
for i in range(2):cube('Study stand',(-4.3-i*.7,-.4,.18+i*.4),(.8,11,.35),green)
# Native ring and a simple readable backboard in the same court space.
cube('Backboard',(0,-5.7,3.48),(1.83,.045,1.06),ivory)
curve('Orange rim',[(.225*math.cos(a),-5.3+.225*math.sin(a),3.05) for a in [i*math.tau/64 for i in range(65)]],.018,orange)
for i in range(12):
 a=i*math.tau/12;curve('Net cord',[(.225*math.cos(a),-5.3+.225*math.sin(a),3.05),(.14*math.cos(a+.3),-5.3+.14*math.sin(a+.3),2.64)],.005,ivory)

specs=[('Shooter 11','shooter',(-.8,2.4,0),0,red,11),('Defender 6','defender',(-.65,.85,0),math.pi,ivory,6),('Rebound 10','rebound',(-2.2,-1.0,0),-.18,red,10),('Guard 7','guard',(2.3,-.3,0),.22,red,7),('Center 4','center',(-.6,-3.5,0),.15,red,4),('Opponent 5','opponent',(.95,-3.0,0),-.45,ivory,5)]
for i in range(6):specs.append(('Spectator '+str(i+1),'crowd',(-4.25,-3.6+i*1.3,.45),math.pi/2,navy if i%2 else green,20+i))
font=bpy.data.fonts.load(str(R/'public/fonts/NotoSansSC.ttf'))
def number(arm,body,loc,rotation,size,material):
 d=bpy.data.curves.new('Uniform label','FONT');d.body=body;d.align_x='CENTER';d.size=size;d.font=font;d.extrude=.0004;o=bpy.data.objects.new('Uniform '+body,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation;d.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.select_set(False);o.parent=arm
 vg=o.vertex_groups.new(name='spine02');vg.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('Chest label binding','ARMATURE');mod.object=arm
 return o
actors=[]
for idx,(name,kind,origin,angle,col,num) in enumerate(specs):
 arm=source_arm.copy();arm.data=source_arm.data.copy();arm.name=name+' / deform rig';scene.collection.objects.link(arm);arm.animation_data_clear();arm.rotation_mode='XYZ'
 meshes=[]
 for src in source_meshes:
  ob=src.copy();ob.data=src.data;ob.name=name+' / '+src.name;scene.collection.objects.link(ob);ob.parent=arm;ob.animation_data_clear()
  for mod in ob.modifiers:
   if mod.type=='ARMATURE':mod.object=arm
  if src in [shirt,shorts]:
   for slot in ob.material_slots:slot.link='OBJECT';slot.material=col
  meshes.append(ob)
 labelmat=ivory if col==red else navy
 number(arm,str(num),(0,-.169,1.20),(math.pi/2,0,0),.15,labelmat)
 number(arm,str(num),(0,.145,1.20),(math.pi/2,0,math.pi),.17,labelmat)
 if kind!='crowd':number(arm,'SHOHOKU' if col==red else 'GUEST',(0,-.159,1.40),(math.pi/2,0,0),.036,labelmat)
 actors.append({'name':name,'kind':kind,'arm':arm,'origin':Vector(origin),'angle':angle,'meshes':meshes,'idx':idx})
for ob in source_meshes:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(source_arm,do_unlink=True)

# Motion helpers: planted world-space contacts, two-segment IK, skinning matrices.
ik_state={}
def ik(a,b,l1,l2,pole,key=None):
 a,b=Vector(a),Vector(b);dvec=b-a;dist=dvec.length;d=min(max(dist,.00001),l1+l2-.0001);v=dvec.normalized();h=(l1*l1-l2*l2+d*d)/(2*d);p=Vector(pole);p=(p-v*p.dot(v)).normalized()
 if key is not None:
  if key in ik_state:
   old=ik_state[key];old=(old-v*old.dot(v)).normalized();angle=math.atan2(v.dot(old.cross(p)),max(-1,min(1,old.dot(p))))
   # Transport the bend plane continuously; a preferred pole crossing the limb axis cannot flip the elbow.
   p=Quaternion(v,max(-.10,min(.10,angle*.35)))@old
  ik_state[key]=p.copy()
 return a+v*h+p*math.sqrt(max(0,l1*l1-h*h)),max(0,dist-l1-l2)

def segment(over,names,old_a,old_b,new_a,new_b,old_normal=None,new_normal=None):
 if old_normal is not None:
  oa=(old_b-old_a).normalized();na=(new_b-new_a).normalized();on=Vector(old_normal).normalized();nn=Vector(new_normal).normalized()
  of=Matrix((oa,on.cross(oa).normalized(),on)).transposed();nf=Matrix((na,nn.cross(na).normalized(),nn)).transposed();q=(nf@of.transposed()).to_quaternion()
 else:q=(old_b-old_a).rotation_difference(new_b-new_a)
 for n in names:
  m=q.to_matrix().to_4x4()@rest[n];m.translation=new_a+q@(head[n]-old_a);over[n]=m

def swing(t,a,b):u=sat((t-a)/(b-a));return smooth(a,b,t),math.sin(math.pi*u)**2 if a<t<b else 0.

def root_position(actor,t):
 o=actor['origin'].copy();k=actor['kind']
 if k=='defender':o.y+=.54*smooth(.25,1.48,t)
 if k=='rebound':o.x+=.30*smooth(.6,1.6,t);o.y-=.18*smooth(1.4,2.7,t)
 if k=='guard':o.x-=.25*smooth(.4,1.6,t)
 if k=='center':o.x+=.15*smooth(1.4,2.6,t)
 if k=='opponent':o.x-=.15*smooth(1.3,2.5,t)
 return o

def foot_plan(actor,side,t):
 o=actor['origin'];k=actor['kind'];rot=Matrix.Rotation(actor['angle'],3,'Z')
 offset=head['foot.'+side].copy();offset.x=.165 if side=='L' else -.165
 if k in ['center','opponent']:offset.x*=1.22
 offset.y=.035 if side=='L' else -.07;offset.z-=foot_data[side]['sole_min'];world=o+rot@offset;lift=0.;plant=True;pitch=0.
 moves=[]
 if k=='defender':moves=[(.25,.65,(0,.30,0))] if side=='R' else [(.72,1.15,(0,.38,0))]
 elif k=='rebound':moves=[(.65,1.10,(.25,-.10,0))] if side=='R' else [(1.22,1.72,(.32,-.15,0))]
 elif k=='guard':moves=[(.45,.90,(-.22,0,0))] if side=='L' else [(1.0,1.45,(-.25,0,0))]
 elif k=='center':moves=[(1.50,1.95,(.18,0,0))] if side=='L' else [(2.02,2.45,(.15,0,0))]
 elif k=='opponent':moves=[(1.4,1.85,(-.18,0,0))] if side=='R' else [(1.98,2.4,(-.15,0,0))]
 for a,b,delta in moves:
  u,arch=swing(t,a,b);world+=Vector(delta)*u
  if a<t<b:lift+=.085*arch;pitch=.10*math.sin(math.pi*sat((t-a)/(b-a)));plant=False
 if k in ['shooter','defender']:
  start,height=(1.62,.41) if k=='shooter' else (1.88,.23);end=start+math.sqrt(8*height/9.81)
  if start<t<end:lift+=ballistic(t,start,height);plant=False;pitch=.20*(1-smooth(start+.04,end-.04,t))
  elif start-.18<t<=start:pitch=.20*smooth(start-.18,start,t);plant=False
 world.z+=lift
 pivot=foot_data[side]['pivot']-head['foot.'+side]
 mapping=Matrix.Translation(world)@Matrix.Rotation(actor['angle'],4,'Z')@Matrix.Translation(pivot)@Matrix.Rotation(pitch,4,'X')@Matrix.Translation(-pivot)@Matrix.Translation(-head['foot.'+side])
 return mapping,plant

RELEASE=1.94

def held_ball(t):
 lift=smooth(1.13,1.84,t);z=1.30+.80*lift+hip_delta(t,'shooter');return Vector((-.08,-.34,z))
release_local=held_ball(RELEASE);shooter=actors[0];release_world=shooter['origin']+release_local
flight=1.22;rim=Vector((0,-5.3,3.05));swish=RELEASE+flight

def ball_world(t):
 if t<=RELEASE:return shooter['origin']+held_ball(t)
 u=(t-RELEASE)/flight
 if u<=1:
  p=release_world.lerp(rim,u);p.z+=4.905*flight*flight*u*(1-u);return p
 dt=t-swish;v=(rim-release_world)/flight;v.z-=4.905*flight;impact=(v.z+math.sqrt(v.z*v.z+19.62*(3.05-.12)))/9.81
 # Ring/net drag slows horizontal motion continuously; vertical velocity carries through the rim.
 xy=Vector((v.x,v.y,0))*((1-math.exp(-25*dt))/25)
 if dt<impact:return rim+xy+Vector((0,0,v.z*dt-4.905*dt*dt))
 age=dt-impact;dur=.54;hh=.35
 while age>dur and dur>.06:age-=dur;dur*=.62;hh*=.3844
 return Vector((xy.x,-5.3+xy.y,.12+4*hh*min(1,age/dur)*(1-min(1,age/dur))))

bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.12);ball=bpy.context.object;ball.name='Single continuous basketball';ball.data.materials.append(orange)
for poly in ball.data.polygons:poly.use_smooth=True
for axis in range(3):
 pts=[]
 for i in range(97):
  a=i*math.tau/96;v=(.121*math.cos(a),.121*math.sin(a),0)
  if axis==1:v=(v[0],0,v[1])
  if axis==2:v=(0,v[0],v[1])
  pts.append(v)
 ch=curve('Basketball channel',pts,.002,black);ch.parent=ball

finger_axes={}
for b in bones:
 if b.name.startswith('finger'):
  fw=(b.tail_local-b.head_local).normalized();tow=Vector((0,-1,0));axis=fw.cross(tow)
  if axis.length<.01:axis=Vector((1,0,0))
  finger_axes[b.name]=b.matrix_local.to_3x3().inverted()@axis.normalized()

palm_rest={s:(head['finger3-1.'+s]-head['wrist.'+s])*.52 for s in ['L','R']}

def hand_matrix(side,wrist,forward,normal):
 old=palm_rest[side].normalized();fw=Vector(forward).normalized();q=old.rotation_difference(fw)
 across=(head['finger2-1.'+side]-head['finger5-1.'+side]).normalized();oldn=old.cross(across).normalized();n=q@oldn;n=(n-fw*n.dot(fw)).normalized();nn=Vector(normal);nn=(nn-fw*nn.dot(fw))
 if nn.length>.001:
  nn.normalize();ang=math.atan2(fw.dot(n.cross(nn)),max(-1,min(1,n.dot(nn))));q=Quaternion(fw,ang)@q
 m=q.to_matrix().to_4x4()@rest['wrist.'+side];m.translation=wrist;return m

records=[];reach_max=0.;previous_rotation={}
for frame in range(1,COUNT+1):
 t=(frame-1)/FPS;ball.location=ball_world(t);ball.rotation_euler=(t*3.7,t*.9,t*.4)
 for pr in ['location','rotation_euler']:ball.keyframe_insert(pr,frame=frame)
 frame_record={'frame':frame,'time':t,'ball':list(ball.location),'actors':[]}
 for actor in actors:
  k=actor['kind'];arm=actor['arm'];origin=root_position(actor,t);arm.location=origin;arm.rotation_euler=(0,0,actor['angle']);M=Matrix.Translation(origin)@Matrix.Rotation(actor['angle'],4,'Z');Mi=M.inverted()
  arm.keyframe_insert('location',frame=frame);arm.keyframe_insert('rotation_euler',frame=frame)
  dz=hip_delta(t,k);lean=.07+.12*smooth(.55,1.2,t)*(1-smooth(1.3,1.8,t)) if k=='shooter' else .06 if k=='defender' else .02
  pivot=Vector((0,0,1.01));B=Matrix.Translation((0,0,dz))@Matrix.Translation(pivot)@Matrix.Rotation(lean,4,'X')@Matrix.Translation(-pivot)
  over={'root':B@rest['root']};contacts={};reach=[];hand_contacts={}
  for side,s in [('L',1),('R',-1)]:
   mapping,planted=foot_plan(actor,side,t);footLocal=Mi@mapping;ankle=footLocal@head['foot.'+side];hip=B@head['upperleg01.'+side]
   oldh=head['upperleg01.'+side];oldk=head['lowerleg01.'+side];olda=head['foot.'+side]
   knee,err=ik(hip,ankle,(oldk-oldh).length,(olda-oldk).length,(s*.04,-1,0));reach.append(err)
   segment(over,['upperleg01.'+side,'upperleg02.'+side],oldh,oldk,hip,knee);segment(over,['lowerleg01.'+side,'lowerleg02.'+side],oldk,olda,knee,ankle)
   over['foot.'+side]=footLocal@rest['foot.'+side]
   contacts[side]={'planted':planted,'ankle':list(M@ankle),'toe_pivot':list(mapping@foot_data[side]['pivot'])}
   grip=.13
   if k=='shooter':
    if t<=RELEASE:
     bp=held_ball(t);contact=bp+Vector((.105,0,-.06) if side=='L' else (0,0,-.12));fw=Vector((0,-.32,.95) if side=='L' else (0,-.55,.83)).normalized();wrist=contact-fw*palm_rest[side].length;normal=bp-contact;grip=.34
     hand_contacts[side]={'palm':list(M@contact),'ball_distance':(contact-bp).length}
    else:
     u=smooth(RELEASE,2.18,t);relax=smooth(2.76,3.55,t)
     pre_fw=Vector((0,-.32,.95) if side=='L' else (0,-.55,.83)).normalized();pre=held_ball(RELEASE)+Vector((.105,0,-.06) if side=='L' else (0,0,-.12))-pre_fw*palm_rest[side].length-Vector((0,0,hip_delta(RELEASE,'shooter')))
     follow=Vector((.27,-.27,1.77)) if side=='L' else Vector((-.08,-.28,1.955));a=pre.lerp(follow,u)
     wrist=a.lerp(Vector((s*.31,-.10,1.14)),relax)+Vector((s*.05*math.sin(math.pi*relax),-.22*math.sin(math.pi*relax),dz));fw=pre_fw.lerp(Vector((0,-1,-.35)),u) if side=='R' else pre_fw.lerp(Vector((s*.2,-.2,.9)),u);normal=Vector((0,-1,0));grip=.34*(1-u)+.08*u
   elif k=='defender':
    u=smooth(1.35,1.91,t)*(1-smooth(2.40,2.95,t));wrist=mix((s*.48,-.30,1.36),(s*.22,-.21,1.97),u)+Vector((0,-.18*math.sin(math.pi*u),dz));fw=Vector((0,-.12,1));normal=Vector((0,-1,0));grip=.05
   elif k=='crowd':
    phase=t*math.tau/1.12+actor['idx']*.9;separation=.04+.095*(.5+.5*math.cos(phase));wrist=Vector((s*separation,-.32,1.42+dz+.01*math.sin(phase)));fw=Vector((0,-.25,1));normal=Vector((-s,0,0));grip=.10
   else:
    ready=smooth(.5,1.5,t);win=smooth(3.25,3.9,t)
    if k=='center':low=(s*.35,-.30,1.38);up=(s*.20,-.22,1.92);u=smooth(2.35,3.2,t)
    elif k=='opponent':low=(s*.30,-.30,1.18);up=(s*.30,-.16,1.12);u=smooth(3.15,3.8,t)
    else:low=(s*.32,-.12,1.15);up=(s*.24,-.22,1.92 if side=='R' else 1.63);u=win
    wrist=mix(low,up,u)+Vector((0,(-.22*math.sin(math.pi*u)) if k!='opponent' else 0,dz));fw=mix((s*.1,-.35,-.75),(s*.15,-.25,.8),u);normal=Vector((0,-1,0))
   elevate=smooth(1.52,1.95,wrist.z-dz)*.24
   cl='clavicle.'+side;shoulderPivot=head[cl];SB=B@Matrix.Translation(shoulderPivot)@Matrix.Rotation(-s*elevate,4,'Y')@Matrix.Translation(-shoulderPivot)
   over[cl]=SB@rest[cl]
   shoulder=SB@head['upperarm01.'+side];olde=head['lowerarm01.'+side];oldw=head['wrist.'+side];olds=head['upperarm01.'+side]
   elbow,err=ik(shoulder,wrist,(olde-olds).length,(oldw-olde).length,mix((s*.10,.2,-1),(s*.75,-.45,-.25),smooth(1.36,1.75,wrist.z-dz)),key=(actor['name'],side));reach.append(err)
   on=(olde-olds).cross(oldw-olde);nn=(elbow-shoulder).cross(wrist-elbow)
   segment(over,['upperarm01.'+side,'upperarm02.'+side],olds,olde,shoulder,elbow,on,nn);segment(over,['lowerarm01.'+side,'lowerarm02.'+side],olde,oldw,elbow,wrist,on,nn)
   wm=hand_matrix(side,wrist,fw,normal)
   if k=='shooter' and t>RELEASE:
    pf=Vector((0,-.32,.95) if side=='L' else (0,-.55,.83)).normalized();pn=Vector((-.105,0,.06) if side=='L' else (0,0,.12))
    q0=hand_matrix(side,Vector((0,0,0)),pf,pn).to_quaternion()
    qfollow=Quaternion((1,0,0),1.3*u if side=='R' else .15*u)@q0
    qrest=hand_matrix(side,Vector((0,0,0)),(s*.1,-.2,-.8),(0,-1,0)).to_quaternion()
    wm=qfollow.slerp(qrest,relax).to_matrix().to_4x4();wm.translation=wrist
   elif k not in ['shooter','defender','crowd']:
    q0=hand_matrix(side,Vector((0,0,0)),(s*.1,-.35,-.75),(0,-1,0)).to_quaternion()
    q1=hand_matrix(side,Vector((0,0,0)),(s*.15,-.25,.8),(0,-1,0)).to_quaternion()
    wm=q0.slerp(q1,u).to_matrix().to_4x4();wm.translation=wrist
   over['wrist.'+side]=wm
   actor.setdefault('grip',{})[side]=grip
  # A small continuous gaze turn follows the ball flight, not a face-image replacement.
  gaze=smooth(RELEASE,2.6,t)*(1-smooth(3.5,4.4,t));hp=head['head'];over['head']=B@Matrix.Translation(hp)@Matrix.Rotation(-.10*gaze,4,'X')@Matrix.Translation(-hp)@rest['head']
  targets={}
  for b in bones:
   n=b.name;par=parent[n]
   if n in over:target=over[n]
   elif par:target=targets[par]@rest_inv[par]@rest[n]
   else:target=B@rest[n]
   if n in finger_axes:
    side=n[-1];bend=actor['grip'][side]*(.70 if '-1.' in n else 1.)
    target=target@Quaternion(finger_axes[n],bend).to_matrix().to_4x4()
   targets[n]=target
   if n not in over and n not in finger_axes:continue
   pb=arm.pose.bones[n];pb.rotation_mode='QUATERNION'
   if par:pb.matrix_basis=b.convert_local_to_pose(target,rest[n],parent_matrix=targets[par],parent_matrix_local=rest[par],invert=True)
   else:pb.matrix_basis=b.convert_local_to_pose(target,rest[n],invert=True)
   qkey=(actor['name'],n);q=pb.rotation_quaternion.copy()
   if qkey in previous_rotation and q.dot(previous_rotation[qkey])<0:q.negate();pb.rotation_quaternion=q
   previous_rotation[qkey]=q.copy()
   for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=frame,group=n)
  reach_max=max(reach_max,max(reach));frame_record['actors'].append({'name':actor['name'],'kind':k,'root':list(origin),'feet':contacts,'reach_error_max':max(reach),'hand_contacts':hand_contacts})
 records.append(frame_record)
 if frame%30==0:print('BAKED_FRAME',frame,'MAX_REACH',reach_max,flush=True)
# Avoid accidental spline overshoot of baked position/rotation values.
for ob in [ball,*[a['arm'] for a in actors]]:
 action=ob.animation_data.action if ob.animation_data else None
 if action:
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for kp in fc.keyframe_points:kp.interpolation='LINEAR'
# Workbench is a fast local geometry diagnostic renderer, not the final anime look.
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.45;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True;scene.display.shading.background_type='WORLD';scene.world.color=(.34,.39,.41)
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=COUNT;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [i.identifier for i in scene.view_settings.bl_rna.properties['look'].enum_items] else 'None'
bpy.ops.object.camera_add(location=(8.8,2.4,4.1));cam=bpy.context.object;cam.name='Locked motion study camera';cam.data.type='ORTHO';cam.data.ortho_scale=11.2;cam.rotation_euler=(Vector((0,-1,1.7))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.frame_set(1)
scene.render.filepath='//../outputs/frames/frame_';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'public/continuous-rig.blend'))
(R/'docs/motion-trace.json').write_text(json.dumps(records,indent=2));(R/'docs/rig-manifest.json').write_text(json.dumps({'frames':COUNT,'fps':FPS,'actors':len(actors),'players':6,'spectators':6,'deform_bones_per_actor':len(bones),'max_reach_error_m':reach_max,'release':RELEASE,'swish':swish,'source_model':'public/models/human-base.glb','animation_method':'Continuous world-contact IK baked to native deform-bone transforms; preserve-volume armature skinning; no sprite selection','appearance_status':'Motion-study placeholder; not yet adapted to approved Rukawa anime design'},indent=2))
print('RIG_STUDY_READY',len(actors),len(bones),'REACH_ERROR',reach_max,flush=True)
