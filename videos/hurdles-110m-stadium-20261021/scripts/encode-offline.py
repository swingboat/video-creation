from pathlib import Path
import os,subprocess,json,hashlib,shutil
root=Path.cwd();tmp=root/'.cache/tmp';tmp.mkdir(parents=True,exist_ok=True);os.environ.update(TMPDIR=str(tmp),TMP=str(tmp),TMP_DIR=str(tmp),TEMP=str(tmp))
frames=root/'outputs/offline/frames';out=root/'public/assets/offline';out.mkdir(parents=True,exist_ok=True)
expected=[frames/f'frame_{i:04d}.png' for i in range(1,67)]
missing=[str(p) for p in expected if not p.exists()]
if missing:raise SystemExit(f'{len(missing)} rendered frames are missing. Run npm run render:scene first.')
def run(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error',*map(str,args),'-y'],check=True)
run('-framerate',24,'-start_number',1,'-i',frames/'frame_%04d.png','-frames:v',66,'-an','-c:v','libx264','-preset','slow','-crf',17,'-pix_fmt','yuv420p','-movflags','+faststart',out/'hurdles-cycles.mp4')
for name,f in [('poster',35),('approach',28),('flight',35),('landing',40)]:
 run('-i',frames/f'frame_{f:04d}.png','-frames:v',1,'-q:v',2,out/f'{name}.jpg')
shutil.copyfile(out/'hurdles-cycles.mp4',root/'outputs/hurdle-110-code.mp4')
metadata={'renderSamples':24,'motionBlur':False,'backend':'CPU','frameHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in expected},'buildScriptHash':hashlib.sha256((root/'scripts/build-offline.py').read_bytes()).hexdigest(),'source':'Blender Cycles local code render','frames':66,'fps':24,'duration':2.75,'size':[1280,720],'videoSource':'No stock footage; no AI video generation service','motion':'Authored trajectory and two-segment IK','ingredients':['MakeHuman CC0 body and photo textures','Procedural garments, short hair, track and hurdles','Poly Haven Stadium 01 CC0 environment panorama'],'limitations':'Programmed movement and a generic base mesh still look computer-generated; no claim of live-action parity.'}
(out/'provenance.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
print('Encoded 66 locally rendered frames into a 2.75-second clip.')
