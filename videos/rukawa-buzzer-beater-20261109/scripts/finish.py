"""Compose only after every scene frame exists; keep a log for each stage."""
import subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
assert len(list((r/'outputs/frames').glob('frame_*.png')))==480,'Wait for all Blender frames first'
def run(args,log):
 with (r/'outputs/checks'/log).open('w') as out:
  subprocess.run(args,cwd=r,stdout=out,stderr=subprocess.STDOUT,check=True)
 print('FINISHED',log,flush=True)
run(['node','scripts/run.mjs','encode'],'encode.log')
p=r/'src/Root.tsx';s=p.read_text().replace("source:'preview.png',preview:true","source:'picture.mp4',preview:false");p.write_text(s)
run([str(r/'node_modules/.bin/tsc')],'typescript.log')
run(['node','scripts/run.mjs','render'],'remotion-render.log')
run(['node','scripts/run.mjs','check'],'final-check.log')
run(['ffmpeg','-v','error','-i','outputs/rukawa-final-shot-20s.mp4','-f','null','-'],'decode-check.log')
run([str(r/'node_modules/.bin/remotion'),'still','src/index.ts','RukawaFinalShot','outputs/checks/poster.png','--frame=422'],'poster.log')
run(['node','scripts/run.mjs','package'],'package.log')
