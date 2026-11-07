"""Procedural recreation study. Run with Blender's bundled Python, from project root."""
import bpy
import math
import random
import json
import os
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
random.seed(20261106)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in bpy.data.materials:
    bpy.data.materials.remove(block)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 336
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.use_persistent_data = True
scene.render.filepath = str(ROOT / 'outputs/frames/frame_')
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = 0.065
scene.cycles.max_bounces = 8
scene.cycles.transmission_bounces = 6
scene.cycles.transparent_max_bounces = 8
scene.cycles.diffuse_bounces = 2
scene.cycles.glossy_bounces = 2
scene.cycles.sample_clamp_indirect = 3
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0.1
scene.world.color = (0.10, 0.10, 0.10)
world_nodes = scene.world.node_tree if scene.world.use_nodes else None
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.13, 0.17, 0.24, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.18

def mat(name, color, rough=.5, metallic=0, transmission=0, ior=1.45, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Transmission Weight'].default_value = transmission
    bs.inputs['IOR'].default_value = ior
    if emission:
        bs.inputs['Emission Color'].default_value = (*color, 1)
        bs.inputs['Emission Strength'].default_value = emission
    return m

def assign(obj, material):
    obj.data.materials.append(material)
    return obj

def smooth(obj):
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def cube(name, loc, dims, material, bevel=.03, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, material)
    if bevel:
        md=o.modifiers.new('Soft crafted edges', 'BEVEL'); md.width=bevel; md.segments=3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    if parent: o.parent=parent
    return o

def sphere(name, loc, scale, material, parent=None, segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    assign(o,material); smooth(o)
    if parent: o.parent=parent
    return o

def cyl(name, loc, radius, depth, material, parent=None, vertices=32, rtop=None):
    if rtop is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=rtop, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; assign(o,material); smooth(o)
    md=o.modifiers.new('Edge glints','BEVEL');md.width=min(.018,radius/6);md.segments=2
    if parent:o.parent=parent
    return o

def mesh(name, verts, faces, material, parent=None):
    me=bpy.data.meshes.new(name+' geometry');me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);assign(o,material)
    if parent:o.parent=parent
    return o

def curve(name, points, radius, material, parent=None):
    cu=bpy.data.curves.new(name+' spline','CURVE');cu.dimensions='3D';cu.resolution_u=12
    spl=cu.splines.new('POLY');spl.points.add(len(points)-1)
    for p,co in zip(spl.points,points):p.co=(*co,1)
    cu.bevel_depth=radius;cu.bevel_resolution=2
    o=bpy.data.objects.new(name,cu);scene.collection.objects.link(o);assign(o,material)
    if parent:o.parent=parent
    return o

def empty(name,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.location=loc;return o

def lamp(name,typ,loc,power,color,size=1,target=None):
    data=bpy.data.lights.new(name,typ);data.energy=power;data.color=color
    if typ=='AREA':data.shape='DISK';data.size=size
    else:data.shadow_soft_size=size
    o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc
    o.visible_glossy=False
    o.visible_transmission=False
    if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o

ivory=mat('Warm porcelain',(.79,.70,.56),.66)
pink=mat('Dusty rose',(.43,.16,.17),.73)
blush=mat('Blush pink fabric',(.57,.26,.25),.88)
wall=mat('Warm plaster',(.44,.34,.22),.92)
wood=mat('Honey oak',(.37,.20,.085),.42)
darkwood=mat('Walnut hull',(.105,.046,.019),.37)
gold=mat('Aged brass',(.42,.25,.09),.29,.65)
navy=mat('Midnight blue',(.017,.046,.085),.85)
teal=mat('Muted blue',(.19,.39,.46),.6)
yellow=mat('Butter yellow',(.76,.48,.15),.72)
black=mat('Ink',(.012,.009,.007),.38)
red=mat('Vermilion pennants',(.38,.045,.027),.6)
cloth=mat('Cream canvas sails',(.75,.72,.59),.9)
cloth.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(.75,.72,.59,1)
cloth.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=.045
rope=mat('Hemp cord',(.20,.13,.065),.83)
grass=mat('Seagrass',(.12,.23,.10),.75)
rock=mat('Blue slate',(.065,.105,.13),.85)
bulb=mat('Amber bulbs',(1,.68,.29),.35,emission=4)
glass=mat('Bottle optical glass',(.97,.99,1),.035,transmission=1,ior=1.46)

# Procedural wood: no external textures.
n=wood.node_tree.nodes;l=wood.node_tree.links;bs=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=3
coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(.45,22,6)
l.new(coord.outputs['Generated'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.13;ramp.color_ramp.elements[0].color=(.27,.17,.085,1)
ramp.color_ramp.elements[1].position=.86;ramp.color_ramp.elements[1].color=(.48,.32,.17,1)
l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.025
l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])

# Desk, quiet bedroom, and Memphis-style decorative shapes.
cube('Oak desk',(0,-.5,-.12),(15,6,.24),wood,.065)
cube('Desk blue apron',(0,-3.46,-.31),(14.95,.06,.15),teal,.018)
cube('Room floor',(0,3,-.69),(20,20,.12),darkwood,.02)
for j in range(8):curve('Desk plank seam %02d'%j,[(-7.4,-3.45+j*.82,.006),(7.4,-3.45+j*.82,.006)],.003,wood)
cube('Back plaster wall',(0,4.3,3.9),(17,.2,8),wall,.02)
cube('Rose wainscot',(0,4.14,1.28),(17,.10,2.56),pink,.015)
for j in range(57):cube('Panel batten %02d'%j,(-8.4+j*.30,4.055,1.28),(.045,.075,2.56),blush,.01)
cube('Panel top rail',(0,3.99,2.60),(17,.13,.09),ivory,.02)
cube('Baseboard',(0,4.00,.14),(17,.16,.22),ivory,.025)

# An upholstered arched headboard, bed and pillows.
verts=[(-5.9,3.78,.25),(-2.35,3.78,.25),(-2.35,3.78,2.6)]
for j in range(41):
    a=j*math.pi/40;verts.append((-4.125+1.775*math.cos(a),3.78,2.6+1.775*math.sin(a)))
head=mesh('Arched pink headboard',verts,[tuple(range(len(verts)))],blush)
sol=head.modifiers.new('Upholstery depth','SOLIDIFY');sol.thickness=.18
curve('Headboard piping',[(-4.125+1.83*math.cos(j*math.pi/60),3.65,2.6+1.83*math.sin(j*math.pi/60)) for j in range(61)],.025,ivory)
cube('Bed base',(-4.15,2.6,.52),(3.5,2.25,.52),wood,.14)
cube('Mattress',(-4.15,2.55,.91),(3.55,2.3,.33),ivory,.15)
cube('Rose duvet',(-4.15,2.05,1.11),(3.6,1.25,.15),blush,.09)
p=cube('Blue pillow',(-4.75,3.25,1.24),(1.3,.6,.34),teal,.16);p.rotation_euler.z=-.05
p=cube('Ivory pillow',(-3.55,3.23,1.26),(1.1,.62,.35),ivory,.16);p.rotation_euler.z=.07

# Warm bedside lamp.
cyl('Lamp foot',(-3.80,2.55,1.14),.34,.08,gold)
cyl('Lamp stem',(-3.80,2.55,1.77),.047,1.22,gold)
shade=cyl('Linen lamp shade',(-3.80,2.55,2.65),.65,.82,ivory,rtop=.37)
shade.data.materials.clear();shade_mat=mat('Glowing linen',(.85,.66,.39),.88,emission=.16);assign(shade,shade_mat)
lamp('Bedside warm pool','POINT',(-3.8,2.38,2.35),45,(1,.64,.32),.4)

# Wall print faces the camera (negative Y).
cube('Picture oak frame',(.10,4.00,4.21),(2.05,.12,2.70),wood,.035)
cube('Picture ivory paper',(.10,3.91,4.21),(1.91,.035,2.56),ivory,.003)
def wall_disk(name,x,z,r,material):
    o=cyl(name,(x,3.875,z),r,.015,material,vertices=64);o.rotation_euler.x=math.pi/2;return o
wall_disk('Print blue circle',-.29,4.56,.56,teal)
poly=[(.72,3.86,3.82),(-.18,3.86,3.82)]+[(.27+.45*math.cos(math.pi-j*math.pi/32),3.86,3.82+.45*math.sin(math.pi-j*math.pi/32)) for j in range(33)]
mesh('Print yellow semicircle',poly,[tuple(range(len(poly)))],yellow)
purple=mat('Lavender',(.39,.30,.46),.77)
curve('Print lavender squiggle',[(-.52+.07*math.sin(j*.45),3.83,3.26+j*.041) for j in range(39)],.023,purple)
for x,z in [(.45,4.97),(.72,4.65),(.52,3.40),(-.02,3.27)]:wall_disk('Print ink dot',x,z,.025,black)
for x,z in [(-1.4,5.35),(1.8,5.38)]:
    mesh('Wall triangle',[(x-.12,4.05,z-.1),(x+.12,4.05,z-.1),(x,4.05,z+.14)],[(0,1,2)],blush if x<0 else purple)
curve('Wall turquoise wiggle',[(2.0+.09*math.sin(j*.35),4.02,3.5+j*.04) for j in range(30)],.027,teal)

# Night window with crossbars and gathered pink curtains.
cube('Night window',(4.9,4.08,4.25),(3.75,.08,4.22),navy,.015)
for x in [3.0,4.9,6.8]:cube('Window vertical frame',(x,3.98,4.25),(.085,.16,4.38),wood,.018)
for z in [2.12,4.25,6.38]:cube('Window horizontal frame',(4.9,3.96,z),(3.9,.18,.09),wood,.018)
cube('Window sill',(4.9,3.81,2.10),(4.15,.45,.12),wood,.025)
moon=mat('Moon ivory',(.82,.85,.71),.5,emission=.5)
pts=[]
for j in range(41):
    a=math.radians(63.7)+math.radians(232.6)*j/40;pts.append((5.55+.25*math.cos(a),3.89,5.65+.25*math.sin(a)))
for j in range(41):
    a=math.radians(265.1)-math.radians(170.2)*j/40;pts.append((5.68+.225*math.cos(a),3.89,5.65+.225*math.sin(a)))
mesh('Crescent moon',pts,[(j,j+1,80-j,81-j) for j in range(40)],moon)
for side in [2.73,7.05]:
    for j in range(8):
        x=side+(j-3.5)*.075
        cube('Pleated curtain',(x,3.74+.035*math.cos(j*math.pi),4.31),(.095,.14,4.4),blush,.045)
    curve('Curtain golden tie',[(side-.38,3.57,3.16),(side,3.48,3.08),(side+.38,3.57,3.16)],.026,yellow)

# Festoon cable and individual emissive bulbs.
wire_points=[]
for j in range(81):
    u=j/80;x=-4.1+6.2*u;z=5.05-.48*math.sin(math.pi*u);wire_points.append((x,3.65,z))
curve('String light cable',wire_points,.012,rope)
for j in range(18):
    u=(j+.2)/18;x=-4.1+6.2*u;z=5.05-.48*math.sin(math.pi*u)
    cyl('Bulb socket %02d'%j,(x,3.65,z-.028),.025,.06,gold)
    sphere('Fairy light %02d'%j,(x,3.65,z-.085),(.047,.047,.067),bulb,segments=16)
for x in [-5,-2,.2]:lamp('Fairy light bounce','POINT',(x,3.5,4.7),5,(1,.65,.30),.6)

# Desk props on right.
bookcolors=[teal,blush,purple]
for j,m in enumerate(bookcolors):
    z=.12+j*.19
    b=cube('Book pages %d'%j,(5.40,.85,z),(1.7,.86,.13),ivory,.015)
    cube('Book lower cover %d'%j,(5.40,.85,z-.076),(1.77,.91,.027),m,.012)
    cube('Book upper cover %d'%j,(5.40,.85,z+.076),(1.77,.91,.027),m,.012)
    cube('Book spine %d'%j,(4.54,.85,z),(.05,.91,.17),m,.012)
bunny=empty('Porcelain bunny',(5.27,-.25,.02))
sphere('Bunny body',(0,0,.40),(.24,.18,.33),ivory,bunny)
sphere('Bunny head',(0,-.02,.86),(.25,.20,.235),ivory,bunny)
for x in [-.13,.13]:
    o=sphere('Bunny ear',(x,.005,1.23),(.073,.064,.30),ivory,bunny);o.rotation_euler.y=x*.9
    sphere('Bunny pink ear',(x,-.055,1.25),(.033,.008,.18),blush,bunny)
    sphere('Bunny foot',(x,-.12,.12),(.14,.17,.11),ivory,bunny)
    sphere('Bunny eye',(x*.7,-.203,.88),(.020,.013,.023),black,bunny,16)
sphere('Bunny nose',(0,-.220,.82),(.022,.013,.016),blush,bunny,16)
for x in [-.09,.09]:sphere('Bunny blue bow',(x,-.17,.64),(.10,.04,.055),teal,bunny)
for x,y,z,m in [(4.75,-.92,.18,blush),(5.35,-.96,.17,teal),(5.02,-.83,.45,yellow)]:cube('Painted toy block',(x,y,z),(.31,.31,.31),m,.035)

# Child's drawing and pencil, left foreground.
paper=cube('Drawing paper',(-4.75,-1.55,.022),(1.85,1.12,.025),ivory,.007);paper.rotation_euler.z=.12
sphere('Drawing sun',(-5.08,-1.43,.045),(.16,.16,.003),yellow)
for j in range(9):
    a=j*math.tau/9;curve('Sun crayon ray',[(-5.08+.20*math.cos(a),-1.43+.20*math.sin(a),.048),(-5.08+.28*math.cos(a),-1.43+.28*math.sin(a),.048)],.008,yellow)
curve('Blue crayon sea',[(-5.4+j*.055,-1.83+.055*math.sin(j*.65),.047) for j in range(23)],.012,teal)
curve('Pink crayon heart',[(-4.27+.13*math.sin(j*.2)**3,-1.42+.10*(math.cos(j*.2)-.35*math.cos(2*j*.2)),.048) for j in range(33)],.012,blush)
curve('Blue pencil',[(-5.75,-.83,.045),(-4.15,-.72,.045)],.028,teal)
curve('Pencil tip',[(-5.75,-.83,.045),(-5.89,-.84,.045)],.027,wood)

# Hollow glass bottle, rotated profile around its horizontal X axis.
ZC=1.75
PROFILE=[(-4.04,.01),(-4.02,.43),(-3.98,.91),(-3.90,1.24),(-3.77,1.47),(-3.55,1.58),(-3.25,1.60),(1.90,1.60),(2.17,1.57),(2.42,1.47),(2.65,1.30),(2.86,1.07),(3.04,.80),(3.22,.58),(3.43,.44),(3.70,.425),(4.08,.425)]
def rad_at(x):
    for j in range(len(PROFILE)-1):
        xa,ra=PROFILE[j];xb,rb=PROFILE[j+1]
        if xa<=x<=xb:
            u=(x-xa)/(xb-xa);u=u*u*(3-2*u);return ra*(1-u)+rb*u
    return PROFILE[0][1] if x<PROFILE[0][0] else PROFILE[-1][1]

xs=[PROFILE[0][0]+(PROFILE[-1][0]-PROFILE[0][0])*j/160 for j in range(161)]
N=96;verts=[]
for inner in [False,True]:
    for x in xs:
        radius=max(.004,rad_at(x)-(.047 if inner else 0))
        xx=x+(.055*max(0,1-(x+4.04)/.3) if inner else 0)
        for j in range(N):
            a=math.tau*j/N;verts.append((xx,radius*math.cos(a),ZC+radius*math.sin(a)))
faces=[];nr=len(xs);offset=nr*N
for layer in range(2):
    for k in range(nr-1):
        for j in range(N):
            a=layer*offset+k*N+j;b=layer*offset+k*N+(j+1)%N;c=b+N;d=a+N
            faces.append((a,b,c,d) if layer==0 else (d,c,b,a))
for j in range(N):
    a=(nr-1)*N+j;b=(nr-1)*N+(j+1)%N;faces.append((a,a+offset,b+offset,b))
    a=j;b=(j+1)%N;faces.append((a,b,b+offset,a+offset))
bottle=smooth(mesh('Bottle • solid optical shell',verts,faces,glass))
# Correct shell normals via mesh operator.
bpy.context.view_layer.objects.active=bottle;bottle.select_set(True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');bottle.select_set(False)

corkmat=mat('Cork',(.28,.16,.055),.93)
nt=corkmat.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=23
bu=nt.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.4;bu.inputs['Distance'].default_value=.06
nt.links.new(noise.outputs['Fac'],bu.inputs['Height']);nt.links.new(bu.outputs[0],nt.nodes['Principled BSDF'].inputs['Normal'])
o=cyl('Cork stopper',(4.25,0,ZC),.40,.72,corkmat);o.rotation_euler.y=math.pi/2
for x in [3.46,3.51,3.56]:curve('Neck cord',[(x,.448*math.cos(j*math.tau/64),ZC+.448*math.sin(j*math.tau/64)) for j in range(65)],.014,rope)

# A real closed water volume, with analytic shape-key waves on the top surface.
watermat=mat('Clear blue water volume',(.76,.88,.92),.065,transmission=.98,ior=1.333)
nt=watermat.node_tree
absorb=nt.nodes.new('ShaderNodeVolumeAbsorption');absorb.inputs['Color'].default_value=(.54,.76,.80,1);absorb.inputs['Density'].default_value=.018
# Clear water color comes from surface transmission. No participating medium
# is needed for this small bottle, avoiding unnecessary volume path work.
topmat=watermat.copy();topmat.name='Water surface • foam veins'
nt=topmat.node_tree;n=nt.nodes;l=nt.links;waterbs=n.get('Principled BSDF')
waterbs.inputs['Base Color'].default_value=(.27,.47,.58,1)
waterbs.inputs['Transmission Weight'].default_value=.58
waterbs.inputs['Roughness'].default_value=.12
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4.6;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65
coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],noise.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.53;ramp.color_ramp.elements[1].position=.67
l.new(noise.outputs['Fac'],ramp.inputs[0])
foam=n.new('ShaderNodeBsdfPrincipled');foam.inputs['Base Color'].default_value=(.80,.87,.84,1);foam.inputs['Roughness'].default_value=.6
factor=n.new('ShaderNodeMath');factor.operation='MULTIPLY';l.new(ramp.outputs[0],factor.inputs[0])
for fr in range(1,337):
    factor.inputs[1].default_value=.15+.70*math.sin(math.pi*(fr-1)/336)**.8;factor.inputs[1].keyframe_insert(data_path='default_value',frame=fr)
mix=n.new('ShaderNodeMixShader');l.new(factor.outputs[0],mix.inputs[0]);l.new(waterbs.outputs[0],mix.inputs[1]);l.new(foam.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n['Material Output'].inputs['Surface'])
SEA=1.60
MODES=[(.17,2.5,.38,2.6),(.08,4.2,-1.2,3.7),(.045,7.3,2.0,5.1)]
def envelope(t):return .18+.82*max(0,math.sin(math.pi*min(1,max(0,t/14))))**.8
def fade(x,y):
    r=max(.01,rad_at(x)-.075);return min(1,max(0,(x+3.98)/.5))*min(1,max(.05,(3.55-x)/1.2))*(.7+.3*max(0,1-(y/r)**2))
def wave(x,y,t):return SEA+fade(x,y)*envelope(t)*sum(a*math.sin(kx*x+ky*y-w*t) for a,kx,ky,w in MODES)
NX=110;NY=36;verts=[];topcoords=[]
for i in range(NX+1):
    x=-3.97+(7.98)*i/NX;r=max(.08,rad_at(x)-.068);half=math.sqrt(max(.001,r*r-(SEA-ZC)**2))
    for j in range(NY+1):
        y=(j/NY*2-1)*half
        verts.append((x,y,SEA));topcoords.append((x,y))
count=len(verts)
for x,y in topcoords:
    r=max(.08,rad_at(x)-.065);verts.append((x,y,ZC-math.sqrt(max(.002,r*r-y*y))+.012))
faces=[]
for i in range(NX):
    for j in range(NY):
        a=i*(NY+1)+j;b=a+NY+1;faces.append((a,b,b+1,a+1));faces.append((a+count,a+1+count,b+1+count,b+count))
perim=[j for j in range(NY+1)]+[i*(NY+1)+NY for i in range(1,NX+1)]+[NX*(NY+1)+j for j in range(NY-1,-1,-1)]+[i*(NY+1) for i in range(NX-1,0,-1)]
for a,b in zip(perim,perim[1:]+perim[:1]):faces.append((a,a+count,b+count,b))
water=smooth(mesh('Ocean • closed volume and analytic waves',verts,faces,watermat));water.data.materials.append(topmat)
for i in range(NX*NY):water.data.polygons[2*i].material_index=1
water.shape_key_add(name='Basis')
for idx,(am,kx,ky,w) in enumerate(MODES):
    for trig in ['sin','cos']:
        key=water.shape_key_add(name='Wave_%d_%s'%(idx,trig),from_mix=False);key.slider_min=-1;key.slider_max=1
        for i,(x,y) in enumerate(topcoords):
            spatial=math.sin(kx*x+ky*y) if trig=='sin' else math.cos(kx*x+ky*y)
            key.data[i].co.z+=am*fade(x,y)*spatial
        for fr in range(1,337):
            t=(fr-1)/24;key.value=envelope(t)*(math.cos(w*t) if trig=='sin' else -math.sin(w*t));key.keyframe_insert(data_path='value',frame=fr)

# Curved seabed and underwater plants.
sand=mat('Dark golden seabed',(.17,.115,.044),.93)
verts=[];faces=[]
for i in range(61):
    x=-3.6+6.2*i/60;r=max(.2,rad_at(x)-.11)
    for j in range(13):
        y=(j/12*2-1)*min(.78,r*.62);z=ZC-math.sqrt(max(.03,r*r-y*y))+.045
        verts.append((x,y,z))
for i in range(60):
    for j in range(12):
        a=i*13+j;faces.append((a,a+13,a+14,a+1))
sandbed=smooth(mesh('Curved sand bed',verts,faces,sand))
for j in range(28):
    x=random.uniform(-3.4,2.3);y=random.uniform(-.65,.65);r=rad_at(x)-.11;z=ZC-math.sqrt(max(.04,r*r-y*y))+.055
    height=random.uniform(.20,.57)
    for leaf in range(random.choice([2,3])):
        points=[(x+.05*leaf+.055*math.sin(k*.38+j),y+.025*math.sin(k*.4+leaf),z+k*height/12) for k in range(13)]
        cv=curve('Seagrass blade %02d'%j,points,.018,grass)
        for k,point in enumerate(cv.data.splines[0].points):point.radius=1-k/13

# School of stylised fish, animated independently inside the bottle.
fishmats=[mat('Fish warm gold',(.73,.31,.045),.36,.16),mat('Fish coral',(.63,.16,.045),.46),mat('Fish bronze',(.21,.16,.073),.43,.2)]
for fm in fishmats:
    fbs=fm.node_tree.nodes['Principled BSDF'];fbs.inputs['Emission Color'].default_value=fbs.inputs['Base Color'].default_value;fbs.inputs['Emission Strength'].default_value=.20
for j in range(9):
    root=empty('Fish %02d • swim path'%j);fm=fishmats[j%3]
    sphere('Fish body',(0,0,0),(.26,.072,.12),fm,root)
    mesh('Fish tail',[(-.20,0,0),(-.40,0,.16),(-.40,0,-.16)],[(0,1,2)],fm,root)
    mesh('Fish dorsal fin',[(-.09,0,.08),(.03,0,.20),(.12,0,.08)],[(0,1,2)],fm,root)
    sphere('Fish eye',(.17,-.065,.04),(.022,.012,.022),black,root,16)
    base=-2.8+j*.57
    for fr in range(1,337):
        t=(fr-1)/24;root.location=(base+.32*math.sin(t*.55+j),-.35+.18*math.sin(t*.34+j*1.4),.66+.22*math.sin(j*1.7)+.055*math.sin(t*2+j))
        root.rotation_euler=(.04*math.sin(t*2+j),.07*math.cos(t*1.7+j),.18*math.sin(t*.55+j))
        root.keyframe_insert(data_path='location',frame=fr);root.keyframe_insert(data_path='rotation_euler',frame=fr)

# Lighthouse on the island, warm light always on.
sphere('Lighthouse island',(-2.51,.17,SEA+.045),(.51,.38,.20),rock)
cyl('Lighthouse tower',(-2.51,.17,SEA+.54),.145,.92,ivory,rtop=.105)
for z in [SEA+.27,SEA+.57,SEA+.78]:
    cube('Tower front window',(-2.51,.023,z),(.055,.017,.073),navy,.008)
cyl('Lighthouse lantern floor',(-2.51,.17,SEA+1.02),.19,.055,gold)
cyl('Lighthouse glowing lantern',(-2.51,.17,SEA+1.14),.13,.20,bulb)
for a in range(6):
    ang=a*math.tau/6;cyl('Lantern upright',(-2.51+.14*math.cos(ang),.17+.14*math.sin(ang),SEA+1.14),.009,.23,gold,vertices=12)
cyl('Lighthouse red roof',(-2.51,.17,SEA+1.31),.22,.21,red,rtop=0)
lamp('Lighthouse amber glow','POINT',(-2.51,-.02,SEA+1.15),3,(1,.49,.17),.13)
sphere('Small right rock',(2.01,.24,SEA-.02),(.27,.21,.13),rock)

# Detailed two-masted sailing vessel with native baked buoyancy keys.
boat=empty('Schooner • four-point baked buoyancy')
stations=[(-1.13,.015),(-.96,.17),(-.65,.27),(-.15,.31),(.35,.30),(.75,.24),(1.05,.08),(1.15,.015)]
section=[(0,-.24),(.68,-.16),(1,.03),(.99,.16),(-.99,.16),(-1,.03),(-.68,-.16)]
verts=[(x,sy*w,sz*(.72+.28*w/.31)) for x,w in stations for sy,sz in section]
faces=[];ns=len(section)
for i in range(len(stations)-1):
    for j in range(ns):faces.append((i*ns+j,(i+1)*ns+j,(i+1)*ns+(j+1)%ns,i*ns+(j+1)%ns))
faces.extend([tuple(range(ns-1,-1,-1)),tuple((len(stations)-1)*ns+j for j in range(ns))])
hull=smooth(mesh('Schooner walnut hull',verts,faces,darkwood,boat));mod=hull.modifiers.new('Hull crafted bevel','BEVEL');mod.width=.012;mod.segments=2
cube('Schooner deck',(0,0,.15),(1.91,.48,.055),wood,.04,boat)
for sy in [-1,1]:
    for z in [-.08,.015,.11,.27]:curve('Hull strake and rail',[(x,sy*w*(1.02 if z<.2 else 1.00),z) for x,w in stations],.010 if z<.2 else .014,wood,boat)
    for x in [-.85,-.55,-.25,.05,.35,.65,.9]:
        width=.28*math.sqrt(max(.05,1-(x/1.2)**2))
        cyl('Rail stanchion',(x,sy*width,.22),.009,.18,gold,boat,12)
for x in [-.42,.48]:
    tall=1.37 if x<0 else 1.12
    cyl('Schooner mast',(x,0,.18+tall/2),.022,tall,wood,boat,20)
    curve('Mast stay',[(x,0,.18+tall),(-1.03,0,.20)],.005,rope,boat)
    curve('Mast stay',[(x,0,.18+tall),(1.08,0,.20)],.005,rope,boat)
    for sy in [-1,1]:curve('Side shroud',[(x,0,.18+tall),(x+.19,sy*.26,.20)],.005,rope,boat)
    mesh('Scarlet mast pennant',[(x,0,.18+tall),(x-.28,.015,.22+tall),(x-.24,.02,.12+tall)],[(0,1,2)],red,boat)

def sail(name,corners):
    verts=[];faces=[];K=12
    for i in range(K+1):
        u=i/K
        for j in range(K+1):
            v=j/K;p=(Vector(corners[0])*(1-u)+Vector(corners[1])*u)*(1-v)+(Vector(corners[3])*(1-u)+Vector(corners[2])*u)*v
            p.y-=.13*math.sin(math.pi*u)*math.sin(math.pi*v);verts.append(tuple(p))
    for i in range(K):
        for j in range(K):
            a=i*(K+1)+j;faces.append((a,a+K+1,a+K+2,a+1))
    s=smooth(mesh(name,verts,faces,cloth,boat));m=s.modifiers.new('Sail cloth thickness','SOLIDIFY');m.thickness=.006
    for i in range(4):curve(name+' stitched edge',[corners[i],corners[(i+1)%4]],.006,rope,boat)
    for u in [.25,.5,.75]:
        points=[]
        for j in range(21):
            v=j/20;p=(Vector(corners[0])*(1-u)+Vector(corners[1])*u)*(1-v)+(Vector(corners[3])*(1-u)+Vector(corners[2])*u)*v;p.y-=.13*math.sin(math.pi*u)*math.sin(math.pi*v)+.005;points.append(tuple(p))
        curve(name+' vertical seam',points,.0019,rope,boat)
sail('Main cream gaff sail',[(-1.02,-.014,.47),(-.44,-.014,.47),(-.44,-.014,1.49),(-.72,-.014,1.41)])
sail('Fore cream sail',[(-.27,-.018,.45),(.93,-.018,.45),(.48,-.018,1.26),(.45,-.018,1.26)])
curve('Main boom',[(-1.03,-.04,.43),(-.41,-.04,.43)],.014,wood,boat)
curve('Fore boom',[(-.30,-.04,.42),(.98,-.04,.42)],.014,wood,boat)
for fr in range(1,337):
    t=(fr-1)/24;x=.04+.12*math.sin(t*.43);y=-.10
    heights=[wave(x-.73,y,t),wave(x+.73,y,t),wave(x,y-.23,t),wave(x,y+.23,t)]
    boat.location=(x,y,sum(heights)/4-.05)
    boat.rotation_euler=(math.atan2(heights[3]-heights[2],.46)*.68,-math.atan2(heights[1]-heights[0],1.46)*.85,.025*math.sin(t*.7))
    boat.keyframe_insert(data_path='location',frame=fr);boat.keyframe_insert(data_path='rotation_euler',frame=fr)

# Rain remains inside the bottle above the waterline.
rainmat=mat('Rain silver',(.57,.74,.86),.28,metallic=.15,emission=.08)
rain=empty('Rain • looping streaks')
for j in range(95):
    x=random.uniform(-3.2,2.3);y=random.uniform(-.7,.65);z=random.uniform(1.85,2.85)
    cv=curve('Rain streak %03d'%j,[(0,0,0),(-.015,.005,-random.uniform(.035,.085))],.0025,rainmat,rain)
    for fr in range(1,337,2):
        t=(fr-1)/24;cv.location=(x+.035*math.sin(t+j),y,1.77+((z-1.77-t*1.7)%1.12));cv.keyframe_insert(data_path='location',frame=fr)
for fr in range(1,337):
    a=.12+.88*envelope((fr-1)/24);rain.scale=(a,a,a);rain.keyframe_insert(data_path='scale',frame=fr)

# Eight lightning events: curve emission and two spatial light sources share keys.
EVENTS=[2.05,3.84,5.02,6.92,8.27,9.48,10.84,12.02]
lightningmat=mat('Lightning white-blue',(.64,.79,1),.3,emission=18)
insideflash=lamp('Flash • bottle scatter','POINT',(.7,-.1,2.8),0,(.64,.80,1),.75)
roomflash=lamp('Flash • room bounce','AREA',(.5,-2.8,4.6),0,(.65,.79,1),5,(0,2,2))
lightning=[]
for idx,event in enumerate(EVENTS):
    x=random.uniform(-1.65,1.9);y=random.uniform(.20,.50)
    pts=[(x+random.uniform(-.12,.12),y+random.uniform(-.04,.04),2.97-j*.145) for j in range(9)]
    cv=curve('Lightning %02d • trunk'%idx,pts,.009,lightningmat);lightning.append((cv,event))
    for branch in [3,5]:
        p=pts[branch];sign=random.choice([-1,1]);br=[p,(p[0]+sign*.19,p[1],p[2]-.11),(p[0]+sign*.34,p[1]+.04,p[2]-.26)]
        lightning.append((curve('Lightning %02d • branch'%idx,br,.0045,lightningmat),event))
for o,event in lightning:
    for fr in range(1,337):
        dt=(fr-1)/24-event;strength=1 if 0<=dt<.083 or .16<=dt<.20 else .00001
        o.scale=(strength,)*3;o.keyframe_insert(data_path='scale',frame=fr)
for fr in range(1,337):
    t=(fr-1)/24;strength=0
    for event in EVENTS:
        d=t-event
        if 0<=d<.34:strength=max(strength,math.exp(-d*17)+(.65 if .16<=d<.21 else 0))
    insideflash.data.energy=650*strength;insideflash.data.keyframe_insert(data_path='energy',frame=fr)
    roomflash.data.energy=1600*strength;roomflash.data.keyframe_insert(data_path='energy',frame=fr)

# Soft studio illumination, balanced to retain a warm, dim bedroom.
lamp('Warm key','AREA',(-4,-5,7),450,(1,.79,.58),5,(0,0,1.4))
lamp('Cool window rim','AREA',(5,2,5.6),120,(.53,.69,1),3,(0,0,1.7))
lamp('Soft bottle edge','AREA',(-1,1,6.5),160,(1,.89,.73),4,(0,0,1.5))
lamp('Underwater visibility','AREA',(0,-1.0,1.05),22,(.67,.85,.92),3,(0,.3,.45))
strip=lamp('Controlled bottle highlight','AREA',(0,2.5,6),65,(1,.92,.80),4,(0,0,1.8))
strip.data.shape='RECTANGLE';strip.data.size=4;strip.data.size_y=.09;strip.visible_glossy=True;strip.visible_transmission=True

# Lower the wall decor to preserve the reference framing while lifting the desk into view.
wall_prefixes=('Arched pink','Headboard piping','Picture ','Print ','Wall triangle','Wall turquoise','Night window','Window ','Crescent moon','Pleated curtain','Curtain golden','String light','Bulb socket','Fairy light')
for o in list(bpy.data.objects):
    if o.name.startswith(wall_prefixes):o.location.z-=.84
    if o.name.startswith(('Arched pink','Headboard piping')):o.location.x+=1.45
    if o.name.startswith(('Picture ','Print ')):o.location.x+=.75
    if o.name.startswith(('Night window','Window ','Crescent moon','Pleated curtain','Curtain golden')):o.location.x+=1.1
    if o.name.startswith(('Lighthouse','Tower front','Lantern upright')):
        o.location.z=SEA+(o.location.z-SEA)*.83
        if o.type!='LIGHT':o.scale.z*=.83

bpy.ops.object.camera_add(location=(-.65,-18.5,6.6))
camera=bpy.context.object;camera.name='Camera • gentle push in';scene.camera=camera
target=Vector((.05,.55,1.47));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=52
camera.data.dof.use_dof=False
camera.keyframe_insert(data_path='location',frame=1)
camera.location.y+=.50;camera.location.x+=.12;camera.keyframe_insert(data_path='location',frame=336)

# Linear baked animation, with hard flash edges; no Python handlers required to play the blend.
for obj in bpy.data.objects:
    if obj.animation_data and obj.animation_data.action:
        try:
            for fc in obj.animation_data.action.fcurves:
                for kp in fc.keyframe_points:kp.interpolation='LINEAR'
        except AttributeError:pass

for colname in ['Reference assets are not used for rendering']:
    scene[colname]=True
scene['production_note']='All models, geometry, lighting and animation generated locally. Reference study of guanmo_ai / bottle storm.'
scene['wave_coupling']='Ship location/pitch/roll baked from the same analytic height field as water shape keys.'
scene['reference_url']='https://x.com/guanmo_ai/status/2118258208045494688'
scene.frame_set(1)
scene.render.filepath='//../outputs/frames/frame_'
scene.render.image_settings.color_mode='RGB'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'public/bottle-storm.blend'))
(ROOT/'docs/timeline.json').write_text(json.dumps({'fps':24,'duration':14,'frames':336,'lightning_seconds':EVENTS,'thunder_delay_seconds':.09,'modes':MODES},indent=2))
print('SCENE_READY',len(bpy.data.objects),'objects',flush=True)
