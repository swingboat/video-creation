import bpy,json
from pathlib import Path
P=Path.cwd();S=P/'sources/research/realism-v6/renderpeople/eric'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(S/'rp_eric_rigged_001_zup_t.fbx'))
out=[]
for o in bpy.context.scene.objects:
 d={'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'dimensions':list(o.dimensions)}
 if o.type=='MESH':d.update(vertices=len(o.data.vertices),groups=[g.name for g in o.vertex_groups],materials=[m.name for m in o.data.materials])
 if o.type=='ARMATURE':
  d['bones']=[{'name':b.name,'head':list(o.matrix_world@b.head_local),'tail':list(o.matrix_world@b.tail_local)} for b in o.data.bones]
 out.append(d)
(P/'outputs/checks/realism-v6/scan-inspect.json').write_text(json.dumps({'objects':out,'images':[{'name':i.name,'path':i.filepath,'size':list(i.size)} for i in bpy.data.images]},indent=2))
print('SCAN_INSPECTED',[(d['name'],d['type'],d['dimensions']) for d in out])
mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
for z in [1.58,1.60,1.62,1.64,1.7,1.85]:
 vs=[mesh.matrix_world@v.co for v in mesh.data.vertices if abs((mesh.matrix_world@v.co).z-z)<.008]
 print('SCAN_SECTION',z,[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)] if vs else [])
bpy.ops.wm.open_mainfile(filepath=str(P/'outputs/offline/hurdles-cycles.blend'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
print('BASE_ARM',list(arm.location),[list(r) for r in arm.matrix_world])
for b in arm.data.bones:
 if any(x in b.name for x in ['head','neck','clavicle','upperarm','spine']):print('BASE_BONE',b.name,list(arm.matrix_world@b.head_local),list(arm.matrix_world@b.tail_local))
