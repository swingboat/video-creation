import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[1];sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH';sc.render.use_motion_blur=False;sc.render.resolution_percentage=65
sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True
for f in [103,214,422]:
 sc.frame_set(f);sc.render.filepath=str(r/f'outputs/checks/blocking-{f}.png');bpy.ops.render.render(write_still=True)
