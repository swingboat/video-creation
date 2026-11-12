from pathlib import Path
import subprocess,json,re,hashlib
R=Path(__file__).resolve().parents[1]
def run(args):return subprocess.run(args,cwd=R,check=True,capture_output=True,text=True).stdout
run(['node_modules/.bin/tsc','--noEmit'])
run(['node','--experimental-strip-types','scripts/audit-corrected.mjs'])
active=['src/index.ts','src/Root.tsx','src/CorrectedGather.tsx','src/gatherMotion.ts','scripts/run.mjs','scripts/audit-corrected.mjs','scripts/package.py','remotion.config.ts']
issues=[]
for f in active:
 p=R/f;s=p.read_text()
 for token in ['/Users/','/videos/','rukawa-anime-2d-prototype','rukawa-continuous-rig']:
  if token in s:issues.append([f,token])
 for ref in re.findall(r'(?:from\s*|import\s*\()[\'\"]([^\'\"]+)',s):
  if ref.startswith('.') and not (p.parent/ref).resolve().is_relative_to(R):issues.append([f,ref])
for d in ['src','scripts','public']:
 for p in (R/d).rglob('*'):
  if p.is_symlink():issues.append([str(p.relative_to(R)),'symlink'])
assert not issues,issues
out=R/'outputs/rukawa-corrected-gather-2s.mp4'
m=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]));v=next(x for x in m['streams'] if x['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1280,720,'30/1',60)
assert abs(float(m['format']['duration'])-2)<.01
run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'])
r={'typecheck':'pass','activeRuntimePathIsolation':'pass','videoDecode':'pass','durationSeconds':2,'frames':60,'fps':30,'rig':json.loads((R/'outputs/checks/corrected-gather-audit.json').read_text()),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scope':'Corrected drawing with restrained movement; not a completed jump shot or 20-second film.'}
(R/'outputs/checks/corrected-project-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
