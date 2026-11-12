import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'preview'
s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=6
s.display.render_aa='16'
frames=[1,25,44,58,63,69,85,100,120,150] if mode=='preview' else range(1,151)
out=R/('outputs/checks/poses' if mode=='preview' else 'outputs/frames');out.mkdir(parents=True,exist_ok=True)
for f in frames:
 s.frame_set(f);s.render.filepath=str(out/f'frame_{f:04d}.png');bpy.ops.render.render(write_still=True)
 print('RENDERED',f,flush=True)
