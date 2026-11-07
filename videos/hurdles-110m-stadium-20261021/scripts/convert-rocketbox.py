import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path.cwd();A=P/'sources/research/rocketbox'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(A/'Male_Adult_01.fbx'))
mesh=next(o for o in bpy.data.objects if o.type=='MESH');arm=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh.hide_render=False
# Fix source FBX's platform-specific material references and bake exported image files.
for m in mesh.data.materials:
 m.use_nodes=True;m.node_tree.nodes.clear();out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Roughness'].default_value=.7
 kind='head' if 'head' in m.name else 'opacity' if 'opacity' in m.name else 'body';im=bpy.data.images.load(str(A/('m002_'+kind+'_color.tga')),check_existing=False)
 # PNG/JPEG embedded into glTF; no TGA dependencies at runtime.
 im.filepath_raw=str(A/(kind+'-color.png'));im.file_format='PNG';im.save();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if kind=='opacity':
  m.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED';p.inputs['Roughness'].default_value=.9
 else:
  norm=bpy.data.images.load(str(A/('m002_'+kind+'_normal.tga')),check_existing=False);norm.colorspace_settings.name='Non-Color';norm.filepath_raw=str(A/(kind+'-normal.png'));norm.file_format='PNG';norm.save();nt=m.node_tree.nodes.new('ShaderNodeTexImage');nt.image=norm;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;m.node_tree.links.new(nt.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
for p in mesh.data.polygons:p.use_smooth=True
# Apply source scale to skeleton and mesh; keep their shared, authored bind pose.
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=arm;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
# Slight athletic silhouette, while retaining complete authored facial anatomy.
sub=mesh.modifiers.new('Surface polish','SUBSURF');sub.levels=1;sub.render_levels=1
# Canonical runtime names, direct bones (no twist bridges).
rename={'Bip01 Pelvis':'root','Bip01 Head':'head','Bip01 Neck':'neck01','Bip01 Spine':'spine04','Bip01 Spine1':'spine03','Bip01 Spine2':'spine02'}
for side in ['L','R']:
 for source,target in [('Thigh','upperleg01'),('Calf','lowerleg01'),('Foot','foot'),('UpperArm','upperarm01'),('Forearm','lowerarm01'),('Hand','wrist')]:rename['Bip01 '+side+' '+source]=target+'.'+side
for old,new in rename.items():
 if arm.data.bones.get(old):arm.data.bones[old].name=new
 for vg in mesh.vertex_groups:
  if vg.name==old:vg.name=new
bpy.context.view_layer.update()
meta={n:{'head':list(arm.matrix_world@b.head_local),'tail':list(arm.matrix_world@b.tail_local)} for n,b in arm.data.bones.items()}
(P/'outputs/checks/rocketbox-rest.json').write_text(json.dumps(meta,indent=2))
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);mesh.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'public/assets/rocketbox-athlete.glb'),export_format='GLB',use_selection=True,export_animations=False,export_apply=True)
# Render the complete model before integrating it.
bpy.ops.object.camera_add(location=(2.7,-4.5,2.1));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.2;bpy.context.scene.camera=cam
for loc,power,size in [((3,-4,5),500,4),((-3,-1,3),350,4),((0,3,4),500,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=700;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.world.color=(.15,.15,.15);sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'outputs/checks/rocketbox-neutral.png');bpy.ops.render.render(write_still=True)
