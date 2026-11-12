"""Original procedural anime sculpture and arena, baked to native Blender animation."""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from motion import *
ROOT=Path(__file__).resolve().parents[1]
random.seed(11)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
sc.cycles.max_bounces=4;sc.cycles.diffuse_bounces=2;sc.cycles.glossy_bounces=2
sc.cycles.seed=11;sc.cycles.use_animated_seed=False
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.render.fps=24;sc.frame_start=1;sc.frame_end=480
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.render.use_motion_blur=True;sc.render.motion_blur_shutter=.28
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.25
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.07,.10,.17,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3

def mat(n,c,rough=.5,metal=0,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
red=mat('Shohoku crimson woven jersey',(.56,.012,.025),.62);black=mat('Black ink piping',(.008,.012,.02));white=mat('Ivory uniform trim',(.91,.90,.82));skin=mat('Rukawa warm skin',(.72,.45,.29),.56);hair=mat('Blue black sculpted hair',(.009,.016,.032),.34);eye=mat('Dark indigo eyes',(.012,.027,.045),.3)
navy=mat('Opponent ivory',(.82,.85,.8),.6);blue=mat('Opponent navy trim',(.018,.04,.1));steel=mat('Stadium midnight',(.025,.046,.07),.45,.5);teal=mat('Paint muted ocean',(.018,.12,.15),.36);gold=mat('Warm brass',(.65,.4,.13),.3,.6);line=mat('Court ivory markings',(.92,.83,.6),.35);rubber=mat('Basketball black channels',(.017,.012,.008),.8);orange=mat('Pebbled burnt orange leather',(.66,.19,.027),.72);netmat=mat('Braided cotton net',(.92,.9,.79),.75);led=mat('Warm white luminaire',(.8,.88,1),.3,0,5);redled=mat('Buzzer crimson emission',(.9,.008,.015),.3,0,3)
# Leather microtexture, and fine jersey weave.
for m,scale,strength in [(orange,170,.22),(red,140,.09)]:
 nt=m.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=.012;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
def finish(o,n,m,parent=None):
 o.name=n
 if m:o.data.materials.append(m)
 if parent:o.parent=parent
 return o
def empty(n,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(n,None);sc.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def cube(n,loc,size,m,bevel=0,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=finish(bpy.context.object,n,m,parent);o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def uv(n,loc,scale,m,parent=None,segments=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=12,location=loc);o=finish(bpy.context.object,n,m,parent);o.scale=scale
 for p in o.data.polygons:p.use_smooth=True
 return o
def mesh(n,verts,faces,m,parent=None):
 d=bpy.data.meshes.new(n);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.parent=parent
 if m:d.materials.append(m)
 return o
def curve(n,pts,r,m,parent=None,closed=False):
 d=bpy.data.curves.new(n,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=2;d.resolution_u=1
 s=d.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 s.use_cyclic_u=closed;o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.parent=parent;d.materials.append(m);return o
def rod(n,a,b,r,m,parent=None):return curve(n,[a,b],r,m,parent)
def ring(n,center,r,thick,m,parent=None):return curve(n,[(center[0]+r*math.cos(i*math.tau/96),center[1]+r*math.sin(i*math.tau/96),center[2]) for i in range(96)],thick,m,parent,True)
font=bpy.data.fonts.load(str(ROOT/'public/fonts/Arial-Bold.ttf'))
def text(n,body,loc,size,m,rot=(math.pi/2,0,math.pi),parent=None):
 d=bpy.data.curves.new(n,'FONT');d.body=body;d.align_x='CENTER';d.size=size;d.extrude=.0007;d.font=font
 o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=rot;o.parent=parent;d.materials.append(m);return o
# Layered polished maple boards.
wood=mat('Maple satin lacquer',(.44,.23,.075),.3)
nt=wood.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=2
coord=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(4,90,8);nt.links.new(coord.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],tex.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.21,.085,.022,1);ramp.color_ramp.elements[1].color=(.63,.36,.12,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
cube('Maple playing surface',(0,0,-.08),(15.2,28.2,.16),wood)
cube('Arena surround',(0,0,-.2),(25,38,.2),steel)
# Board joints and subtle alternating plank tones.
for x in range(-25,26):
 xx=x*.3
 rod('Long maple seam', (xx,-14,.003),(xx,14,.003),.0025,gold)
 for y in range(-14,15,3):
  yy=y+(x%3)
  if yy<14:rod('Staggered plank joint',(xx,yy,.003),(xx+.3,yy,.003),.002,gold)
for s in [-1,1]:
 cube('Painted key',(0,s*11,.006),(4.9,5.8,.012),teal)
 curve('Baseline',[(-7.5,s*14,.021),(7.5,s*14,.021)],.035,line)
 curve('Sideline',[(s*7.5,-14,.021),(s*7.5,14,.021)],.035,line)
 curve('Key border',[(-2.45,s*14,.025),(-2.45,s*8.2,.025),(2.45,s*8.2,.025),(2.45,s*14,.025)],.03,line)
 ring('Free throw circle',(0,s*8.2,.026),1.8,.028,line)
 # 6.75 m arc centered on rim projection, plus straight corner segments.
 pts=[(6.75*math.cos(a),s*(12-6.75*math.sin(a)),.027) for a in [i*math.pi/150 for i in range(151)]]
 curve('Three point arc',pts,.035,line)
 for sx in [-1,1]:rod('Corner three line',(sx*6.75,s*12,.027),(sx*6.75,s*14,.027),.035,line)
ring('Center circle',(0,0,.027),1.8,.035,line);rod('Half court',(-7.5,0,.027),(7.5,0,.027),.035,line)
text('Center emblem','SHOHOKU',(0,.35,.029),.63,line,rot=(0,0,0))
# Hoops: transparent backboard, regulation 0.45 m ring, animated cotton net.
glass=mat('Backboard optical glass',(.35,.6,.64),.13);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.82;p.inputs['IOR'].default_value=1.46
nets=[];buzzer=[]
for side in [-1,1]:
 yy=side*12
 cube('Padded hoop base',(0,side*15,.55),(1.2,1.2,1.1),teal,.1)
 rod('Hoop stanchion',(0,side*15,1),(0,side*14.7,4),.13,steel)
 rod('Cantilever hoop support',(0,side*14.7,3.8),(0,side*12.5,3.8),.095,steel)
 cube('Tempered glass backboard',(0,side*12.43,3.52),(1.83,.045,1.07),glass,.015)
 for sx in [-1,1]:rod('Backboard frame',(sx*.915,side*12.4,3),(sx*.915,side*12.4,4.055),.022,white)
 for z in [3,4.055]:rod('Backboard frame',(-.915,side*12.4,z),(.915,side*12.4,z),.022,white)
 curve('Backboard target rectangle',[(-.295,side*12.39,3.05),(-.295,side*12.39,3.5),(.295,side*12.39,3.5),(.295,side*12.39,3.05)],.018,white,closed=True)
 ring('Orange steel rim',(0,yy,3.05),.225,.018,orange)
 rod('Rim mount',(0,yy,3.05),(0,side*12.42,3.05),.035,orange)
 for j in range(12):
  a=j*math.tau/12
  for direction in [-1,1]:
   pts=[]
   for k in range(9):
    u=k/8;aa=a+direction*u*.42;r=.225*(1-.40*u);pts.append((r*math.cos(aa),yy+r*math.sin(aa),3.05-.43*u))
   o=curve('Cotton net weave',pts,.006,netmat)
   if side==1:nets.append((o,[tuple(p) for p in pts]))
 for z in range(4):ring('Net horizontal weave',(0,yy,3.05-z*.13),.225*(1-z*.12),.004,netmat)
 b=cube('Backboard red buzzer',(0,side*12.44,4.10),(1.9,.055,.035),redled,.01);buzzer.append(b)
 text('Backboard shot clock','4Q',(0,side*12.42,4.45),.26,redled,rot=(math.pi/2,0,0) if side==1 else (math.pi/2,0,math.pi))
# Tiered grandstands and instanced seats/crowd. All original geometry.
seatm=mat('Muted red seats',(.22,.025,.04),.68);crowdm=[mat('Crowd coat '+str(i),c) for i,c in enumerate([(.13,.19,.24),(.32,.08,.07),(.54,.44,.3),(.035,.08,.1),(.3,.31,.29)])]
for side in [-1,1]:
 for row in range(6):
  xx=side*(9.1+row*.9);zz=.45+row*.58
  cube('Concrete terrace',(xx,0,zz-.2),(.92,32,.4),steel)
  for col in range(33):
   yy=-15.2+col*.95
   cube('Stadium seat',(xx,yy,zz+.1),(.57,.6,.15),seatm,.06)
   if random.random()<.88:
    cm=random.choice(crowdm);uv('Audience torso',(xx,yy,zz+.54),(.19,.2,.32),cm,segments=8);uv('Audience head',(xx,yy,zz+.94),(.115,.11,.14),skin,segments=8)
 # Ribbed architectural beams, ribbon lighting.
 for yy in [-15,-10,-5,0,5,10,15]:
  cube('Arena pilaster',(side*15,yy,5),(.25,.3,10),steel)
 cube('Arena sidewall',(side*15.3,0,6),(.2,36,12),steel)
 rod('Gold grandstand ribbon',(side*9.0,-16,1),(side*9.0,16,1),.045,gold)
 for yy in [-8,3,12]:
  text('Courtside banner','SHOHOKU  /  BASKETBALL',(side*8,yy,.60),.24,white,rot=(math.pi/2,0,-side*math.pi/2))
cube('End wall',(0,17.7,5.4),(30,.25,11),steel)
text('Arena championship lettering','INTER HIGH  /  FINAL QUARTER',(0,17.5,6.2),.58,gold,rot=(math.pi/2,0,0))
cube('Scoreboard housing',(0,17.3,4.9),(5.8,.3,1.5),black,.08)
text('Scoreboard teams','SHOHOKU     GUEST',(0,17.1,5.3),.32,white,rot=(math.pi/2,0,0))
score=text('Scoreboard live result','74    -    76',(0,17.08,4.62),.60,led,rot=(math.pi/2,0,0))
# Use two separate text objects, keyframed visibility, because font body is not animatable.
score2=text('Scoreboard winning result','77    -    76',(0,17.07,4.62),.60,led,rot=(math.pi/2,0,0))
# Athletic sculpt meshes, articulated by two-bone IK, wrists and ankles retain own controls.
def profile(n,rings,m,parent=None,segments=24):
 v=[];f=[]
 for z,rx,ry in rings:
  for j in range(segments):
   a=j*math.tau/segments;v.append((rx*math.cos(a),ry*math.sin(a),z))
 for k in range(len(rings)-1):
  for j in range(segments):a=k*segments+j;b=k*segments+(j+1)%segments;f.append((a,b,b+segments,a+segments))
 f.extend([tuple(reversed(range(segments))),tuple((len(rings)-1)*segments+j for j in range(segments))]);o=mesh(n,v,f,m,parent)
 for p in o.data.polygons:p.use_smooth=True
 return o

def limb(n,r1,r2,m,parent):
 return profile(n,[(0,r1*.78,r1*.78),(.07,r1,r1),(.35,r1*.95,r1*.95),(.8,r2,r2),(1,r2*.72,r2*.72)],m,parent,16)
def setseg(o,a,b):
 a,b=Vector(a),Vector(b);o.location=a;o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');o.scale.z=(b-a).length

def ik(a,b,l1,l2,pole):
 a,b=Vector(a),Vector(b);v=b-a;d=min(v.length,l1+l2-.001);vn=v.normalized();h=(l1*l1-l2*l2+d*d)/(2*d);q=Vector(pole);q=(q-vn*q.dot(vn)).normalized();return a+vn*h+q*math.sqrt(max(.00001,l1*l1-h*h))

def character(n,col,trim,num,hero=False):
 rt=empty(n);tor=empty(n+' torso',parent=rt)
 profile(n+' shaped sleeveless jersey',[(.98,.17,.12),(1.08,.18,.13),(1.29,.22,.13),(1.48,.245,.11),(1.54,.18,.09)],col,tor)
 # Piping follows neckline and arm holes as real geometry.
 curve(n+' V neck',[(-.11,.095,1.53),(0,.137,1.39),(.11,.095,1.53)],.014,trim,tor)
 curve(n+' neck dark inner',[(-.09,.096,1.54),(0,.138,1.43),(.09,.096,1.54)],.006,black,tor)
 for s in [-1,1]:
  curve(n+' armhole piping',[(s*.19,-.07,1.52),(s*.245,0,1.47),(s*.21,.106,1.32)],.013,trim,tor)
  rod(n+' side panel',(s*.183,.04,1.02),(s*.22,.04,1.32),.014,trim,tor)
 cube(n+' waistband',(0,0,1.015),(.36,.25,.045),black,.01,tor)
 uv(n+' neck',(0,0,1.57),(.073,.072,.105),skin,tor)
 text(n+' chest team','SHOHOKU' if hero else 'GUEST',(0,.139,1.315),.065,trim,parent=tor)
 text(n+' jersey number',str(num),(0,.141,1.105),.19,trim,parent=tor)
 text(n+' back number',str(num),(0,-.141,1.12),.23,trim,rot=(math.pi/2,0,0),parent=tor)
 text(n+' back name','RUKAWA' if hero else 'GUEST',(0,-.139,1.38),.052,trim,rot=(math.pi/2,0,0),parent=tor)
 hd=empty(n+' head',(0,0,1.77),rt)
 face=profile(n+' tapered manga face',[(-.16,.045,.06),(-.12,.085,.085),(-.04,.12,.105),(.07,.124,.11),(.14,.10,.095),(.17,.05,.06)],skin,hd)
 for s in [-1,1]:
  uv(n+' ear',(s*.127,-.005,-.015),(.026,.025,.045),skin,hd)
  # Angular anime eye whites are flush on the front face, with slim dark lids.
  verts=[(s*.026,.107,.036),(s*.104,.087,.042),(s*.095,.096,.016),(s*.033,.109,.015)]
  mesh(n+' narrow eye white',verts,[(0,1,2,3)],white,hd)
  uv(n+' indigo iris',(s*.063,.109,.027),(.014,.006,.012),eye,hd)
  curve(n+' upper eyelid',[(s*.026,.112,.038),(s*.070,.110,.042),(s*.104,.093,.044)],.0045,black,hd)
  curve(n+' stern eyebrow',[(s*.025,.104,.063),(s*.095,.09,.075)],.006,hair,hd)
 mesh(n+' nose',[(0,.101,.025),(-.018,.101,-.031),(0,.143,-.026),(.018,.101,-.031)],[(0,1,2),(0,2,3),(1,3,2)],skin,hd)
 curve(n+' mouth',[(-.03,.091,-.082),(0,.098,-.085),(.028,.091,-.08)],.0028,black,hd)
 uv(n+' hair crown',(0,-.015,.10),(.13,.115,.106),hair,hd)
 if hero:
  for i in range(14):
   a=i*2.399;bx=.105*math.cos(a);by=.078*math.sin(a)-.01
   tip=(bx*1.6,by*1.5,.19+random.uniform(-.015,.075))
   mesh(n+' pointed hair lock',[(bx-.045,by-.04,.10),(bx+.045,by-.04,.10),(bx+.035,by+.035,.11),(bx-.035,by+.035,.11),tip],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],hair,hd)
  for s in [-1,1]:
   for i in range(3):
    xx=s*(.025+i*.038);mesh(n+' swept fringe',[(xx-.032,.065,.145),(xx+.032,.065,.145),(xx+s*.015,.116,.038-i*.015)],[(0,1,2)],hair,hd)
 else:uv(n+' cropped hair',(0,-.02,.13),(.128,.11,.066),hair,hd)
 limbs={};hands={};feet={}
 for s in [-1,1]:
  short=profile(n+' shorts leg',[(0,.105,.115),(.19,.12,.125),(.27,.115,.12)],col,rt);short.location=(s*.108,0,.73)
  ring(n+' shorts ivory hem',(s*.108,0,.742),.106,.012,trim,rt)
  for name,r1,r2,ma in [('thigh',.086,.065,skin),('calf',.063,.036,skin),('upper',.063,.05,skin),('fore',.047,.028,skin)]:limbs[(s,name)]=limb(n+f' {s} '+name,r1,r2,ma,rt)
  for name,r in [('knee',.065),('elbow',.049)]:limbs[(s,name)]=uv(n+name,(0,0,0),(r,r,r),skin,rt)
  hand=empty(n+f' wrist {s}',parent=rt);hands[s]=hand
  uv(n+' palm',(0,0,.037),(.037,.022,.055),skin,hand)
  for j in range(4):
   uv(n+' finger',((j-1.5)*.017,0,.094),(.009,.012,.035-(abs(j-1.5)*.003)),skin,hand,segments=12)
  uv(n+' thumb',(-s*.039,.012,.045),(.014,.017,.03),skin,hand,segments=12)
  foot=empty(n+f' ankle {s}',parent=rt);feet[s]=foot
  uv(n+' sock',(0,0,.10),(.039,.045,.10),white,foot)
  cube(n+' sneaker outsole',(0,.045,.035),(.105,.245,.055),white,.02,foot)
  uv(n+' red and white sneaker',(0,.045,.075),(.054,.115,.056),white,foot)
  cube(n+' sneaker crimson panel',(s*.052,.035,.08),(.008,.12,.036),col,.006,foot)
  for j in range(3):rod(n+' laces',(-.035,.045+j*.022,.123),(.035,.045+j*.022,.123),.003,black,foot)
 return {'rt':rt,'tor':tor,'head':hd,'limbs':limbs,'hands':hands,'feet':feet,'hero':hero}
hero=character('RUKAWA 11',red,white,11,True)
defender=character('DEFENDER 7',navy,blue,7)
extras=[character('PLAYER '+str(i),red if i%2 else navy,white if i%2 else blue,[4,10,8,5][i]) for i in range(4)]
# Ball channels are attached to a single continuous trajectory control.
ball=empty('Basketball authoritative trajectory');uv('Basketball leather',(0,0,0),(.122,.122,.122),orange,ball,32)
for axis in range(3):
 pts=[]
 for i in range(128):
  a=i*math.tau/128;v=[.123*math.cos(a),.123*math.sin(a),0]
  if axis==1:v=[v[0],0,v[1]]
  if axis==2:v=[0,v[0],v[1]]
  pts.append(tuple(v))
 curve('Recessed ball channel',pts,.0022,rubber,ball,True)
for s in [-1,1]:curve('Curved basketball seam',[(.123*math.cos(a)*math.cos(s*.6*math.sin(a)),.123*math.sin(a),.123*math.cos(a)*math.sin(s*.6*math.sin(a))) for a in [i*math.tau/128 for i in range(128)]],.002,rubber,ball,True)
# Softbox arena lighting, visible ceiling strips.
def area(n,loc,target,power,color,size):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for yy in [-8,1,9]:
 area('Overhead arena softbox',(0,yy,10),(0,yy,0),1800,(1,.81,.59),7)
 for sx in [-1,1]:cube('Ceiling light',(sx*5,yy,10.5),(3,.3,.04),led,.02)
area('Rukawa face key',(3,7,5),(-1,4.5,1.4),300,(1,.73,.47),4)
area('Cool rim light',(-4,4,5),(-1,5,1),800,(.48,.67,1),3)
# Camera positions and focal lengths are baked per frame.
d=bpy.data.cameras.new('Editorial cinema lens');cam=bpy.data.objects.new('Camera',d);sc.collection.objects.link(cam);sc.camera=cam;d.sensor_width=36;d.clip_end=100

def key(o,prop,f):o.keyframe_insert(data_path=prop,frame=f)
def pose(c,t,index=0):
 ishero=c['hero'];rt=c['rt'];li=c['limbs'];w=c['hands'];feet=c['feet']
 if ishero:root=hero_root(t)
 elif c is defender:
  hx,hy,hz=hero_root(t);root=(hx+.20-3.2*ease((t-14)/1.2),hy+1.5, .18*math.sin(math.pi*clamp((t-8.1)/1.8)) if 8.1<t<9.9 else 0)
 else:
  poses=[(-3.7,9.4),(3.3,8.8),(-4.3,5.7),(2.5,11)]
  xx,yy=poses[index];root=(xx+.15*math.sin(t*1.5+index),yy+.25*math.sin(t+index),0)
 rt.location=root
 rt.rotation_euler.z=0 if ishero else math.pi if c is defender else .3*math.sin(t*.3+index)
 z=0;walk=(1-ease((t-4.7)/.7)) if ishero else .4 if t<6 else 0
 # Small stance shifts with explicit ground contacts in planted shooting phase.
 legcrouch=-min(root[2],0) if ishero else 0
 for s in [-1,1]:
  stride=math.sin(t*7+s*math.pi/2)*.18*walk;lift=max(0,math.cos(t*7+s*math.pi/2))*.09*walk
  ankle=(s*.115,.10+stride,.09+lift+legcrouch)
  if ishero and t>10.4:ankle=(s*.115,.1,.09)
  hip=(s*.105,0,.98);knee=ik(hip,ankle,.46,.44,(s*.05,1,.1));setseg(li[s,'thigh'],hip,knee);setseg(li[s,'calf'],knee,ankle);li[s,'knee'].location=knee;feet[s].location=(ankle[0],ankle[1],ankle[2]-.09)
  shoulder=(s*.23,0,1.48)
  if ishero:
   if t<4.8:
    bp=ball_at(t);rel=(bp[0]-root[0],bp[1]-root[1],bp[2]-root[2])
    wrist=(rel[0],rel[1],max(.84,rel[2]+.105)) if s==1 else (-.35,.13,1.03+.08*math.sin(t*7))
   elif t<9:
    bp=ball_at(t);rel=Vector(bp)-Vector(root)
    wrist=(rel.x+s*.10,rel.y-.07,rel.z-.17 if s==1 else min(rel.z-.02,2.04))
   elif t<11.4:
    u=ease((t-10.4)/1);wrist=mix((.16,.35,2.13) if s==1 else (-.29,.3,1.87),(s*.32,.09,1.02),u)
   else:
    u=ease((t-15.3)/1.4);wrist=mix((s*.32,.09,1.02),(s*.29,.10,.99),u)
  elif c is defender:
   u=ease((t-7.4)/1.1)*(1-ease((t-10)/.7));wrist=mix((s*.48,.14,1.15),(s*.31,.15,2.0),u)
  else:
   u=ease((t-14)/1) if index%2 else 0;wrist=mix((s*.33,.1,1.04),(s*.34,.1,2.05),u)
  elbow=ik(shoulder,wrist,.34,.32,(s*.35,.8,-.3) if ishero and 6.5<t<10.5 else (s*.4,-.2,-.7));setseg(li[s,'upper'],shoulder,elbow);setseg(li[s,'fore'],elbow,wrist);li[s,'elbow'].location=elbow;w[s].location=wrist
  dr=Vector(wrist)-elbow;w[s].rotation_mode='QUATERNION';w[s].rotation_quaternion=dr.to_track_quat('Z','Y')
  if ishero and 9<=t<10.7 and s==1:w[s].rotation_quaternion=Vector((0,.9,-.3)).to_track_quat('Z','Y')
 # Subtle gaze follows hoop / airborne basketball.
 c['head'].rotation_euler.x=-.10 if t<9 else -.28 if t<13.6 else -.015
 for o in [rt,c['head'],*li.values(),*w.values(),*feet.values()]:
  for p in ['location','rotation_quaternion' if o.rotation_mode=='QUATERNION' else 'rotation_euler','scale']:key(o,p,frame)

trajectory=[]
for frame in range(1,481):
 t=(frame-1)/24
 for i,c in enumerate([hero,defender,*extras]):pose(c,t,max(0,i-2))
 bp=ball_at(t);ball.location=bp;ball.rotation_euler=(t*3.7,t*.9,t*1.2)
 key(ball,'location',frame);key(ball,'rotation_euler',frame)
 trajectory.append({'frame':frame,'t':t,'ball':bp,'root':hero_root(t),'clock':game_clock(t)})
 # Pull the net downward and relax following passage; individual strand coordinates have native keys.
 pulse=math.exp(-max(0,t-13.6)*4)*math.sin(max(0,t-13.6)*10) if t>13.6 else 0
 for o,pts in nets:
  for p,base in zip(o.data.splines[0].points,pts):
   depth=(3.05-base[2])/.43;p.co=(base[0]*(1+.35*pulse*depth),base[1]+.025*pulse*depth,base[2]-.13*pulse*depth,1);p.keyframe_insert('co',frame=frame)
 for o in buzzer:
  o.scale=(1,1,1) if t>=9.15 else (.001,.001,.001);key(o,'scale',frame)
 for o,show in [(score,t<13.85),(score2,t>=13.85)]:o.scale=(1,1,1) if show else (.0001,.0001,.0001);key(o,'scale',frame)
 hx,hy,hz=hero_root(t)
 if t<3.2:
  u=t/3.2;loc=mix((11,-5.5,7.2),(9,-2.5,6),ease(u));target=(-.5,6.2,1.1);lens=37
 elif t<6.1:
  u=(t-3.2)/2.9;loc=(hx+2.9,hy+3.0,1.35+.25*u);target=(hx,hy,1.06);lens=43
 elif t<9.4:
  u=(t-6.1)/3.3;loc=(hx-3.2,hy+3.25,1.65+u*.5);target=(hx,hy+.12,1.55+hz+ease((t-8.8)/.6));lens=45
 elif t<12.7:
  u=(t-9.4)/3.3;loc=(-5.5+u*1.5,7.7+u*2.8,4.1+u*.8);target=mix(bp,(0,12,3.1),.16);lens=43
 elif t<15.4:
  loc=(2.4,9.0,4.05);target=(0,12,2.95);lens=58
 else:
  u=(t-15.4)/4.6;loc=(hx+2.5-u*.4,hy+3.45-u*.45,1.78);target=(hx,hy,1.37);lens=58
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
 key(cam,'location',frame);key(cam,'rotation_euler',frame);key(d,'lens',frame)
# Linear interpolation makes camera cuts exact, avoids overshoot across shot changes.
for datablocks in [bpy.data.objects,bpy.data.cameras]:
 for ob in datablocks:
  if ob.animation_data and ob.animation_data.action:
   for layer in ob.animation_data.action.layers:
    for strip in layer.strips:
     for bag in strip.channelbags:
      for fc in bag.fcurves:
       for k in fc.keyframe_points:k.interpolation='LINEAR'
sc.frame_set(1);sc.render.filepath='//../outputs/frames/frame_'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'public/rukawa.blend'))
(ROOT/'docs/trajectory.json').write_text(json.dumps(trajectory,indent=2))
(ROOT/'docs/scene-inventory.json').write_text(json.dumps({'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'materials':len(bpy.data.materials),'frames':480,'release':9,'swish':13.6,'three_point_distance':math.hypot(RELEASE_POINT[0],RELEASE_POINT[1]-12),'release_point':RELEASE_POINT,'external_assets':[f.filepath for f in bpy.data.fonts if f.filepath]},indent=2))
print('SCENE_BUILT',len(bpy.data.objects),flush=True)
