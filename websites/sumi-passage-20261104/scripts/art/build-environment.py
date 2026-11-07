"""Author the original stone / cedar / shrine asset kit in Blender.

World input uses Three.js x/y-up/z. Files and temporary work stay in this project.
Run: blender --background --factory-startup --python scripts/art/build-environment.py
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector, noise

ROOT = Path(__file__).resolve().parents[2]
random.seed(11052026)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)

def point(x, y, z): return Vector((x, -z, y))
def material(name, color, texture=False, roughness=1):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Roughness'].default_value=roughness
    if texture:
        image=bpy.data.images.load(str(ROOT/'public/textures/limestone-ink-v2.webp'),check_existing=True)
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='REPEAT'
        m.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    return m

limestone=material('MountainLimestone',(.56,.55,.49),True)
edge_stone=material('StoneEdge',(.36,.38,.32),True)
ink=material('InkCrevices',(.055,.073,.063))
cedar=material('OldCedar',(.13,.16,.115))
redwood=material('WeatheredVermilion',(.34,.075,.042))
redlight=material('VermilionWear',(.44,.14,.078))
woodwear=material('ExposedOldWood',(.23,.19,.12))
rope=material('HempRope',(.34,.29,.18))
paper=material('WarmPaper',(.74,.70,.57))
pine_mats=[material('PineNeedle'+str(i),c) for i,c in enumerate([(.06,.105,.067),(.09,.14,.085),(.13,.18,.10)])]
pine_cards=material('PineFoliageCards',(.18,.22,.12))
pine_tex=pine_cards.node_tree.nodes.new('ShaderNodeTexImage');pine_tex.image=bpy.data.images.load(str(ROOT/'public/textures/pine-canopy-v2.png'),check_existing=True)
pine_shader=pine_cards.node_tree.nodes.get('Principled BSDF')
pine_cards.node_tree.links.new(pine_tex.outputs['Color'],pine_shader.inputs['Base Color'])
pine_cards.node_tree.links.new(pine_tex.outputs['Alpha'],pine_shader.inputs['Alpha'])
moss=material('Lichen',(.20,.24,.12))
lamp=material('LanternPaper',(.76,.57,.26))
lamp_bsdf=lamp.node_tree.nodes.get('Principled BSDF');lamp_bsdf.inputs['Emission Color'].default_value=(.85,.38,.07,1);lamp_bsdf.inputs['Emission Strength'].default_value=.55

def apply_modifiers(obj):
    bpy.context.view_layer.objects.active=obj
    for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)

def mesh(name, verts, faces, mat, smooth=False, uv_scale=4):
    data=bpy.data.meshes.new(name);data.from_pydata([point(*v) for v in verts],[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(mat)
    uv=data.uv_layers.new(name='UVMap')
    for poly in data.polygons:
        poly.use_smooth=smooth
        n=poly.normal
        for li in poly.loop_indices:
            v=data.vertices[data.loops[li].vertex_index].co
            if abs(n.z)>.65:u,t=v.x/uv_scale,v.y/uv_scale
            elif abs(n.x)>abs(n.y):u,t=-v.y/uv_scale,v.z/uv_scale
            else:u,t=v.x/uv_scale,v.z/uv_scale
            uv.data[li].uv=(u,t)
    return obj

def cube(name, loc, dims, mat, bevel=.025, rotate=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=point(*loc))
    obj=bpy.context.object;obj.name=name;obj.dimensions=(dims[0],dims[2],dims[1]);obj.rotation_euler.z=-rotate
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod=obj.modifiers.new('WornEdges','BEVEL');mod.width=bevel;mod.segments=2
        mod=obj.modifiers.new('FaceNormals','WEIGHTED_NORMAL')
        apply_modifiers(obj)
    return obj

def cylinder(name, a, b, radius, mat, end=None, sides=10):
    va,vb=point(*a),point(*b);delta=vb-va
    bpy.ops.mesh.primitive_cone_add(vertices=sides,radius1=radius,radius2=radius if end is None else end,depth=delta.length,location=(va+vb)/2)
    obj=bpy.context.object;obj.name=name;obj.rotation_euler=delta.to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
    for poly in obj.data.polygons:poly.use_smooth=True
    return obj

def line(name, points, radius, mat):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=2;curve.bevel_depth=radius;curve.bevel_resolution=1
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*point(*co),1)
    obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH');obj.select_set(False)
    return obj

def rock(name,x,y,z,w,d,depth,seed):
    r=random.Random(seed);n=64;layers=14
    outline=[]
    for i in range(n):
        a=i/n*math.tau;c,s=math.cos(a),math.sin(a)
        xx=math.copysign(abs(c)**.25,c)*w/2
        zz=math.copysign(abs(s)**.25,s)*d/2
        # Conservative erosion never expands the collision footprint.
        erosion=.025+.055*(.5+.5*math.sin(i*1.7+seed))
        outline.append((xx*(1-erosion/w),zz*(1-erosion/d)))
    is_rear=name.startswith('Rear')
    def skyline(a,b):return (2.5*math.sin((x+a)*.22+seed)+1.1*math.sin((x+a)*.53+b*.18)) if is_rear else 0
    verts=[]
    for j in range(layers+1):
        t=j/layers
        yy=y-depth*t
        for i,(xx,zz) in enumerate(outline):
            a=i/n*math.tau
            ridge=math.sin(a*13+seed)*.11+math.sin(a*27)*.035
            strat=.16*math.sin(t*19+seed)+.08*math.sin(t*51+a*3)
            deformation=(ridge+strat)*math.sin(min(1,t*8)*math.pi/2)
            taper=1-.1*t
            verts.append((x+xx*taper+math.cos(a)*deformation,
                          yy+skyline(xx,zz)*max(0,1-t*1.7)+(.035*math.sin(i*2.13) if j==0 else .14*math.sin(i*.9+j)),
                          z+zz*taper+math.sin(a)*deformation))
    faces=[]
    for j in range(layers):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;e=(j+1)*n+i
            faces.append((a,b,c,e))
    side=mesh(name+'_Cliff',verts,faces,limestone,smooth=False)
    # Slightly rounded lip, plus a complete flat cap for predictable foot contact.
    topverts=[(x,y+.018+skyline(0,0),z)]+[(x+a,y+.012+skyline(a,b),z+b) for a,b in outline]
    topfaces=[(0,(i+1)%n+1,i+1) for i in range(n)]
    mesh(name+'_Plateau',topverts,topfaces,limestone,uv_scale=3.5)
    rim=[(x+a,y+.023+skyline(a,b),z+b) for a,b in outline]
    line(name+'_InkRim',rim+[rim[0]],.009,ink)
    # Small detached flakes catch directional light near the top edge.
    for k in range(max(6,int(w*2))):
        i=r.randrange(n);a,b=outline[i]
        slab=cube(name+'_RimFlake',(x+a*.985,y+skyline(a,b)-.09-r.random()*.18,z+b*.985),(.25+r.random()*.4,.10+r.random()*.16,.2+r.random()*.3),edge_stone,.045,r.random()*3)
    # Deep vertical splits have physical recess marks and irregular paths.
    for k in range(max(5,int(w))):
        i=r.randrange(n);a,b=outline[i]
        if abs(b)>d*.4:
            pts=[(x+a+.07*math.sin(t*4+k),y-.1-t*depth*.65,z+b*1.003) for t in [0,.06,.13,.24,.35,.49,.65]]
        else:
            pts=[(x+a*1.003,y-.1-t*depth*.65,z+b+.05*math.sin(t*6+k)) for t in [0,.06,.13,.24,.35,.49,.65]]
        line(name+'_Fracture',pts,.007,ink)
    return side

platforms=[(0,0,0,8.8,7,15),(7.1,.65,-1.3,3.2,3.4,13),(11.7,1.15,-2.5,3.4,3.7,16),
           (17.5,1.6,-3.3,6.9,6.5,19),(23.8,2.2,-4.3,3.2,3.5,18),(28.5,2.8,-5.5,3.8,3.9,20),(35,3.3,-6.5,7.3,7,22)]
for i,p in enumerate(platforms):rock('WalkableIsland'+str(i),*p,271+i*37)

# The distant wall gives the route a place in the mountain rather than a row of toys.
rock('RearEscarpment',12,7.6,-17,34,11,35,882)
rock('RearEscarpmentWest',-14,3.5,-22,13,13,30,112)
rock('RearEscarpmentEast',41,10,-29,18,16,39,902)

def torii(x,y,z,scale=1):
    def P(a,b,c=0):return(x+a*scale,y+b*scale,z+c*scale)
    for sign in [-1,1]:
        cylinder('GatePost',P(sign*1.72,.12),P(sign*1.58,4.68),.23*scale,redwood,.17*scale,16)
        cylinder('GateFoot',P(sign*1.72,.10),P(sign*1.70,.45),.29*scale,ink,.27*scale,12)
        cube('GateFoundation',P(sign*1.72,.08),(.78*scale,.16*scale,.76*scale),edge_stone,.06)
        for j in range(6):
            xx=sign*1.72+(random.random()-.5)*.26
            line('GateGrain',[P(xx,.55+j*.57,.23),P(xx+.02,1.0+j*.57,.22)],.004*scale,woodwear)
    cube('GateLowerBeam',P(0,3.66), (4.55*scale,.24*scale,.29*scale),redwood,.035)
    # Curved beam cross section, extruded in depth.
    profile=[]
    for i in range(25):
        a=-2.8+i/24*5.6;profile.append((a,4.52+.27*(abs(a)/2.8)**2))
    profile += [(a,4.80+.30*(abs(a)/2.8)**2) for a,_ in reversed(profile)]
    v=[P(a,b,dep) for dep in [-.24,.24] for a,b in profile];m=len(profile)
    f=[tuple(range(m-1,-1,-1)),tuple(range(m,2*m))]+[(i,(i+1)%m,(i+1)%m+m,i+m) for i in range(m)]
    mesh('GateCurvedCrown',v,f,redwood)
    line('GateDarkCap',[P(-2.9+i/36*5.8,4.86+.30*(abs(-2.9+i/36*5.8)/2.9)**2,0) for i in range(37)],.075*scale,cedar)
    cube('GateCentralPlaque',P(0,4.06,.09),(.4*scale,.74*scale,.13*scale),ink,.015)
    for i in range(6):
        cube('GatePlaqueCarving',P((-.07 if i%2 else .05),3.85+i*.075,.165),(.14*scale,.018*scale,.005*scale),paper,.002)
    curve=[P(-1.6+i/40*3.2,3.36-.28*math.sin(i/40*math.pi),.12) for i in range(41)]
    line('ShrineSacredRope',curve,.035*scale,rope)
    for i in range(5):
        a=-1.15+i*.57;b=3.16-.1*math.sin(i)
        q=[(-.08,0),(.09,-.09),(.015,-.16),(.10,-.25),(-.03,-.40),(-.10,-.30),(-.02,-.20),(-.10,-.11)]
        mesh('ShidePaper',[P(a+c,b+d,.14) for c,d in q],[tuple(range(len(q)))],paper)
torii(.3,0,-1.5,1.0)
torii(35,3.3,-7.2,1.1)

def pine(x,y,z,scale=1,sign=1,seed=1):
    r=random.Random(seed)
    def P(a,b,c):return(x+a*scale,y+b*scale,z+c*scale)
    trunk=[(-.1,0,0),(-.34*sign,.9,.04),(-.05*sign,1.8,.12),(.52*sign,2.7,.05),(1.25*sign,3.6,-.08),(1.5*sign,4.05,-.15)]
    for j in range(len(trunk)-1):
        cylinder('PineTrunk',P(*trunk[j]),P(*trunk[j+1]),(.21-j*.035)*scale,cedar,(.18-j*.033)*scale,10)
    needle_verts=[[],[],[]];needle_faces=[[],[],[]]
    for j in range(12):
        side=1 if j%2==0 else -1
        start=(.15*sign,1.25+j*.19,0)
        end=((.85+j*.07)*side*sign,1.6+j*.2,r.uniform(-.85,.85))
        mid=((start[0]+end[0])*.52,(start[1]+end[1])*.5-.1,(start[2]+end[2])*.5)
        cylinder('PineBranch',P(*start),P(*mid),.055*scale,cedar,.035*scale,7)
        cylinder('PineTwig',P(*mid),P(*end),.035*scale,cedar,.011*scale,6)
        # Crossed alpha-tested needle cards retain a dense silhouette at game distance.
        for card in range(3):
            a=card*math.pi/3+r.random()*.35;ww=1.75+r.random()*.35;hh=.60+r.random()*.12
            cx=end[0]+r.uniform(-.15,.15);cy=end[1]+.10;cz=end[2]
            dx,dz=math.cos(a)*ww/2,math.sin(a)*ww/2
            verts=[P(cx-dx,cy-hh/2,cz-dz),P(cx+dx,cy-hh/2,cz+dz),P(cx+dx,cy+hh/2,cz+dz),P(cx-dx,cy+hh/2,cz-dz)]
            obj=mesh('PineBoughCard',verts,[(0,1,2,3)],pine_cards)
            for li,uv in enumerate([(0,0),(1,0),(1,1),(0,1)]):obj.data.uv_layers.active.data[li].uv=uv
        for cluster in range(7):
            cx=end[0]+r.uniform(-.65,.65);cy=end[1]+r.uniform(-.06,.10);cz=end[2]+r.uniform(-.40,.40)
            for spray in range(17):
                angle=r.random()*math.tau;length=r.uniform(.13,.32);tilt=r.uniform(-.12,.17)
                color=r.randrange(3);vs=needle_verts[color];fs=needle_faces[color];base=len(vs)
                tip=(cx+math.cos(angle)*length,cy+tilt,cz+math.sin(angle)*length)
                width=.012
                vs.extend([P(cx-math.sin(angle)*width,cy,cz+math.cos(angle)*width),P(*tip),P(cx+math.sin(angle)*width,cy,cz-math.cos(angle)*width)])
                fs.append((base,base+1,base+2))
    for color in range(3):mesh('PineNeedles',needle_verts[color],needle_faces[color],pine_mats[color])
    # Exposed roots bind the tree to the rock.
    for i in range(5):
        a=i*math.tau/5+r.random()*.4
        cylinder('PineRoot',P(0,.18,0),P(math.cos(a)*.55,.02,math.sin(a)*.5),.10*scale,cedar,.02*scale,7)
for args in [(-3,0,-1.3,1.10,1,8),(3,0,-2.5,.72,-1,16),(15.5,1.6,-5.2,1.1,-1,21),(20.1,1.6,-2.8,.75,1,31),(32.5,3.3,-8.5,1.1,1,45),(38,3.3,-7,.75,-1,55)]:pine(*args)

def lantern(x,y,z):
    cube('LanternPlinth',(x,y+.1,z),(.65,.20,.65),limestone,.065)
    cylinder('LanternStem',(x,y+.17,z),(x,y+.71,z),.19,edge_stone,.12,8)
    cube('LanternShelf',(x,y+.74,z),(.50,.15,.50),limestone,.04)
    cube('LanternWarmCore',(x,y+1.03,z),(.29,.40,.29),lamp,.01)
    for a in [-1,1]:
        for b in [-1,1]:cube('LanternFrame',(x+a*.19,y+1.02,z+b*.19),(.055,.43,.055),cedar,.008)
    # Squat hipped roof has a gently flaring eave.
    v=[(x+a*.54,y+1.31,z+b*.54) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]+[(x,y+1.57,z)]
    mesh('LanternRoof',v,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],limestone)
    cylinder('LanternFinial',(x,y+1.52,z),(x,y+1.69,z),.065,edge_stone,.025,8)
for x,y,z in [(-2.5,0,1.7),(2.8,0,.1),(15.8,1.6,-1.5),(36.8,3.3,-5.0)]:lantern(x,y,z)

# Individually worn stone paving, sparse grass and clinging lichen.
for platform_i,(x,y,z,w,d,_) in enumerate(platforms):
    if platform_i in [0,3,6]:
        for j in range(7 if platform_i==0 else 4):
            px=x-2.2+j*.76;pz=z+.95-j*.12
            cube('OldPathSlab',(px,y+.031,pz),(.71,.055,.59),limestone,.055,random.uniform(-.07,.07))
    for k in range(int(w*d*2)):
        a=random.uniform(-w*.43,w*.43);b=random.uniform(-d*.43,d*.43)
        if abs(b)<.6 and abs(a)<w*.35:continue
        if k%5==0:
            cube('RockDebris',(x+a,y+.025,z+b),(random.uniform(.07,.18),.06,random.uniform(.07,.20)),edge_stone,.025,random.random()*3)
        else:
            verts=[(x+a-.012,y,z+b),(x+a+.012,y,z+b),(x+a+random.uniform(-.04,.04),y+random.uniform(.09,.22),z+b)]
            mesh('GrassBlade',verts,[(0,1,2)],moss)
    for k in range(8):
        a=random.uniform(-w*.46,w*.46);b=random.uniform(-d*.46,d*.46)
        rr=random.uniform(.04,.15)
        verts=[(x+a,y+.025,z+b)]+[(x+a+math.cos(j/8*math.tau)*rr,y+.025,z+b+math.sin(j/8*math.tau)*rr*.5) for j in range(8)]
        mesh('LichenPatch',verts,[(0,(j+1)%8+1,j+1) for j in range(8)],moss)

# Merge by material for inexpensive static rendering; terrain keeps meaningful names.
bpy.ops.object.select_all(action='DESELECT')
groups={}
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH' and len(obj.data.materials)==1:
        key=obj.data.materials[0].name
        groups.setdefault(key,[]).append(obj)
for key,objs in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:obj.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();objs[0].name='Environment_'+key
    # Some thin leaves / paper need two-sided rendering.
    objs[0].data.materials[0].use_backface_culling=False
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for image in bpy.data.images:
    if image.source=='FILE':image.pack()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.world.color=(.3,.3,.3)
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
blend=ROOT/'docs/art/mountain-environment-v2.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/mountain-environment-v2.glb'),export_format='GLB',export_yup=True,export_materials='EXPORT',export_image_format='JPEG',export_jpeg_quality=92,export_normals=True,export_texcoords=True,export_cameras=False,export_lights=False,export_animations=False)
report={'meshes':len([o for o in scene.objects if o.type=='MESH']),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'materials':list(groups),'source':'Original authored Blender geometry; generated limestone texture; no reference video pixels.'}
(ROOT/'outputs/checks/v2/environment-assets.json').write_text(json.dumps(report,indent=2))
print('ENVIRONMENT_REPORT',report)
