"""Replace rigid fish with volumetric fish, flexible fins and native baked swim cycles.
Load outputs/versions/bunny-v2/bottle-storm.blend before running this script.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Euler
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;scene.frame_set(1)
paths=json.loads((ROOT/'docs/fish-paths.json').read_text())
for o in list(bpy.data.objects):
    if o.name.startswith('Fish '):bpy.data.objects.remove(o,do_unlink=True)
collection=bpy.data.collections.new('School • articulated fish');scene.collection.children.link(collection)

# Vertex colour carries a dark back, gold flank and pale belly; no self illumination.
def material(name,color,rough=.3,metal=.18,trans=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metal;b.inputs['Coat Weight'].default_value=.28;b.inputs['Coat Roughness'].default_value=.22
    b.inputs['Transmission Weight'].default_value=trans
    return m
bodymat=material('Fish v3 • pearlescent scales',(1,.5,.1))
n=bodymat.node_tree.nodes;l=bodymat.node_tree.links;b=n['Principled BSDF']
vc=n.new('ShaderNodeVertexColor');vc.layer_name='FishColor';l.new(vc.outputs['Color'],b.inputs['Base Color'])
tex=n.new('ShaderNodeTexVoronoi');tex.inputs['Scale'].default_value=82;tex.feature='DISTANCE_TO_EDGE'
coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,2.5,1.4)
l.new(coord.outputs['Generated'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.003
l.new(tex.outputs['Distance'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
finmat=material('Fish v3 • fine fin membranes',(.82,.38,.075),.32,.10,.30)
raymat=material('Fish v3 • fin rays',(.52,.28,.055),.35,.18)
ink=material('Fish v3 • obsidian pupils',(.007,.012,.012),.16,.05)
iris=material('Fish v3 • copper irises',(.73,.49,.12),.24,.35)
gill=material('Fish v3 • gill crease',(.16,.065,.018),.43,0)
white=material('Fish v3 • eye highlights',(.88,.92,.85),.19,.1)
materials=[bodymat,finmat,raymat,ink,iris,gill,white]
palette=[((.96,.38,.055),(.32,.12,.025),(.85,.67,.35)),((.18,.43,.45),(.035,.12,.15),(.51,.67,.60)),((.92,.55,.12),(.29,.20,.055),(.88,.75,.48)),((.80,.25,.055),(.30,.075,.018),(.83,.56,.26)),((.80,.51,.12),(.23,.17,.045),(.83,.72,.45)),((.21,.39,.40),(.04,.12,.14),(.54,.65,.58)),((.82,.64,.37),(.29,.25,.13),(.89,.81,.60)),((.91,.36,.075),(.27,.12,.028),(.85,.66,.33)),((.63,.36,.12),(.16,.13,.07),(.72,.61,.39))]
prof=[(-.24,.012,.025),(-.19,.025,.041),(-.13,.043,.075),(-.06,.064,.107),(.02,.073,.115),(.09,.068,.104),(.16,.047,.076),(.215,.025,.045),(.242,.003,.012)]
def profile(x):
    for i in range(len(prof)-1):
        if x<=prof[i+1][0]:
            a=prof[i];b=prof[i+1];t=max(0,(x-a[0])/(b[0]-a[0]));t=t*t*(3-2*t)
            return (a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t)
    return prof[-1][1:]
class Geometry:
    def __init__(self):self.v=[];self.faces=[];self.mats=[];self.colors=[];self.flex=[]
    def vertex(self,p,c=(1,1,1),flex=0):
        self.v.append(tuple(p));self.colors.append((*c,1));self.flex.append(flex);return len(self.v)-1
    def face(self,idx,mat):self.faces.append(tuple(idx));self.mats.append(mat)
    def sphere(self,p,s,mat,seg=16,rings=9):
        start=len(self.v)
        for j in range(rings+1):
            a=math.pi*j/rings
            for k in range(seg):
                b=math.tau*k/seg;self.vertex((p[0]+s[0]*math.sin(a)*math.cos(b),p[1]+s[1]*math.sin(a)*math.sin(b),p[2]+s[2]*math.cos(a)))
        for j in range(rings):
            for k in range(seg):self.face((start+j*seg+k,start+j*seg+(k+1)%seg,start+(j+1)*seg+(k+1)%seg,start+(j+1)*seg+k),mat)
    def tube(self,pts,r,mat,flex=0):
        start=len(self.v);steps=5
        for j,p in enumerate(pts):
            tangent=Vector(pts[min(j+1,len(pts)-1)])-Vector(pts[max(0,j-1)])
            q=tangent.to_track_quat('Z','Y')
            for k in range(steps):
                co=Vector(p)+q@Vector((r*math.cos(k*math.tau/steps),r*math.sin(k*math.tau/steps),0))
                self.vertex(co,flex=flex*(j/max(1,len(pts)-1)))
        for j in range(len(pts)-1):
            for k in range(steps):self.face((start+j*steps+k,start+j*steps+(k+1)%steps,start+(j+1)*steps+(k+1)%steps,start+(j+1)*steps+k),mat)
    def grid(self,nu,nv,fn,mat,flex=0):
        start=len(self.v)
        for j in range(nu+1):
            for k in range(nv+1):self.vertex(fn(j/nu,k/nv),flex=flex*j/nu)
        for j in range(nu):
            for k in range(nv):
                a=start+j*(nv+1)+k;self.face((a,a+1,a+nv+2,a+nv+1),mat)

def mix(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))
def create_geometry(colors):
    g=Geometry();flank,back,belly=colors
    nr=60;ns=32
    for j in range(nr+1):
        x=-.24+.482*j/nr;w,h=profile(x)
        for k in range(ns):
            a=math.tau*k/ns;z=h*math.sin(a);y=w*math.cos(a)
            shade=math.sin(a)
            c=mix(flank,back,max(0,shade)**2*.80) if shade>=0 else mix(flank,belly,(-shade)**1.2*.82)
            # A restrained, irregular shoulder marking adds volume without bold painted stripes.
            m=.94+.06*math.sin(x*70+math.cos(a)*4)
            g.vertex((x,y,z),tuple(v*m for v in c))
    for j in range(nr):
        for k in range(ns):g.face((j*ns+k,j*ns+(k+1)%ns,(j+1)*ns+(k+1)%ns,(j+1)*ns+k),0)
    g.face(tuple(range(ns-1,-1,-1)),0);g.face(tuple(nr*ns+k for k in range(ns)),0)
    def tail(u,v):
        v=v*2-1;end=-.365-.075*abs(v)**.75
        return (-.237*(1-u)+end*u,.012*math.sin(math.pi*u)*(v*v-.25),(.024*(1-u)+.153*u)*v)
    g.grid(16,22,tail,1,.35)
    for k in range(13):g.tube([tail(j/16,k/12) for j in range(17)],.0011,2,.35)
    def dorsal(u,v):
        x=.11-.29*u;h=profile(x)[1];rise=.10*math.sin(math.pi*u)**.8
        return (x-v*.025,0,h+v*rise)
    g.grid(22,6,dorsal,1,.65)
    for k in range(1,12):g.tube([dorsal(k/12,j/6) for j in range(7)],.00095,2,.5)
    for side in (-1,1):
        def pec(u,v):
            angle=(v-.5)*1.5
            return (.075-.125*u+.025*math.sin(angle)*u,side*(.061+.10*u*math.cos(angle)),-.020-.065*u+.018*math.sin(angle)*u)
        g.grid(9,10,pec,1,side*1.6)
        for k in range(7):g.tube([pec(j/9,k/6) for j in range(10)],.001,2,side*1.6)
        def pelvic(u,v):return (-.10-.085*u+.04*(v-.5)*u,side*(.042+.045*u),-.068-.055*u*(1-abs(v-.5)))
        g.grid(7,8,pelvic,1,side*.8)
        g.sphere((.155,side*.047,.036),(.025,.011,.026),4)
        g.sphere((.160,side*.056,.038),(.016,.005,.018),3)
        g.sphere((.166,side*.061,.046),(.0045,.0015,.0045),6,10,6)
        # Swept gill crease follows the cheek contour.
        points=[]
        for k in range(15):
            a=-.85+1.7*k/14;x=.094-.018*math.cos(a);w,h=profile(x)
            points.append((x,side*w*math.cos(a)*1.012,h*math.sin(a)*.90))
        g.tube(points,.0018,5)
    g.tube([(.239,-.013,-.009),(.244,0,-.014),(.239,.013,-.009)],.002,5)
    return g

# 20 poses preserve cross sections while a travelling bend runs towards the tail.
# All poses and weights are stored in the .blend: no Python playback handlers.
def deform(p,phase,flex,turn=0):
    x,y,z=p;u=max(0,min(1,(.19-x)/.63));amp=.084*(.025+.975*u*u)
    wave=phase-math.tau*.92*u
    dy=amp*math.sin(wave)
    # Local tangent rotates the cross section instead of shearing it.
    slope=-(.084*(1.95*u)*math.sin(wave)-amp*math.tau*.92*math.cos(wave))/.63
    theta=math.atan(slope)
    # Shortening approximates an inextensible centerline at these modest curvatures.
    xx=x+.018*u*u*(.5+.5*math.cos(2*wave))
    yy=dy+y*math.cos(theta)
    xx-=y*math.sin(theta)
    yy+=.5*turn*min(0,x-.12)**2
    yy+=flex*.008*math.sin(phase-.6-u*1.7)
    zz=z+abs(flex)*.006*math.sin(phase-.8-u*1.6)
    return (xx,yy,zz)
records=[]
for spec in paths['fish']:
    i=spec['id'];g=create_geometry(palette[i])
    me=bpy.data.meshes.new('Fish v3 %02d • flowing mesh'%i);me.from_pydata(g.v,[],g.faces);me.update()
    obj=bpy.data.objects.new('Fish v3 %02d • flexible body and fins'%i,me);collection.objects.link(obj)
    for m in materials:me.materials.append(m)
    for p,mi in zip(me.polygons,g.mats):p.material_index=mi;p.use_smooth=True
    color=me.color_attributes.new(name='FishColor',type='FLOAT_COLOR',domain='POINT')
    for d,c in zip(color.data,g.colors):d.color=c
    root=bpy.data.objects.new('Fish v3 %02d • tangent swim rig'%i,None);collection.objects.link(root);obj.parent=root
    root.scale=(spec['scale'],)*3;root.rotation_mode='QUATERNION'
    basis=obj.shape_key_add(name='Basis',from_mix=False);keys=[];N=20
    for k in range(N):
        key=obj.shape_key_add(name='Swim phase %02d'%k,from_mix=False)
        for v,p,flex in zip(key.data,g.v,g.flex):v.co=deform(p,k*math.tau/N,flex)
        keys.append(key)
    turnkey=obj.shape_key_add(name='Steering body bend',from_mix=False);turnkey.slider_min=-2;turnkey.slider_max=2
    for v,p in zip(turnkey.data,g.v):v.co=(p[0],p[1]+.5*min(0,p[0]-.12)**2,p[2])
    prev=None
    for frame,s in enumerate(spec['samples'],1):
        root.location=s['p'];q=Euler((s['bank'],s['pitch'],s['yaw']),'XYZ').to_quaternion()
        if prev and prev.dot(q)<0:q.negate()
        prev=q.copy();root.rotation_quaternion=q
        root.keyframe_insert(data_path='location',frame=frame);root.keyframe_insert(data_path='rotation_quaternion',frame=frame)
        phase=s['phase']/math.tau*N;ix=math.floor(phase);w=phase-ix
        for k,key in enumerate(keys):
            key.value=(1-w) if k==ix%N else w if k==(ix+1)%N else 0
            key.keyframe_insert(data_path='value',frame=frame)
        turnkey.value=s['turn'];turnkey.keyframe_insert(data_path='value',frame=frame)
    obj['swim_technique']='20 cyclic shape poses; posterior travelling wave; flexible fin membranes and rays; native keys.'
    root['route']='Continuous arc-length rounded pass; quaternion follows tangent; curvature-linked bank and body bend.'
    records.append({'id':i,'vertices':len(g.v),'faces':len(g.faces),'poses':N,'scale':spec['scale']})
    print('FISH_READY',i,len(g.v),'vertices',flush=True)
# Linear weights keep the cycle bounded and reproduce baked samples without overshoot.
for action in bpy.data.actions:
    if not action.name.startswith('Fish'):continue
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:kp.interpolation='LINEAR'
bpy.data.lights['Underwater visibility'].energy=32
scene['fish_revision']='v3: volumetric scales, eyes on both sides, gills, forked flexible caudal fin, dorsal/pectoral fin rays; continuous tangent-followed 3D schooling.'
scene.render.filepath='//../outputs/frames-fish/frame_'
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'public/bottle-storm.blend'))
timeline=json.loads((ROOT/'docs/timeline.json').read_text());timeline['fish_revision']='v3';timeline['frame_dir']='outputs/frames-fish';timeline['picture']='bunny-fish-picture.mp4';timeline['final_video']='outputs/bottle-storm-bunny-fish-20s.mp4'
(ROOT/'docs/timeline.json').write_text(json.dumps(timeline,indent=2))
(ROOT/'outputs/checks/fish/build.json').write_text(json.dumps({'fish':records,'frames':480,'spacing':paths['spacing']},indent=2))
print('FISH_SCENE_READY',flush=True)
