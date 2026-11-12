"""Generate a native-speed whole-scene candidate inside this project."""
import argparse,json,os,subprocess,sys,time,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
PRESETS={'pilot':('gather-scene.png',49,768,448),'shot':('gather-scene.png',49,768,448),'close':('close-scene.png',73,1024,576),'rim':('rim-scene.png',49,1024,576),'celebrate':('celebrate-grounded-v2.png',49,1024,576),'hero':('hero-scene.png',97,1024,576),'dribble':('dribble-scene.png',97,1024,576),'crowd':('crowd-scene.png',97,1024,576),'defender':('defender-scene.png',73,1024,576)}
parser=argparse.ArgumentParser();parser.add_argument('scene',choices=list(PRESETS));parser.add_argument('--frames',type=int);parser.add_argument('--width',type=int);parser.add_argument('--height',type=int);parser.add_argument('--seed',type=int,default=7711);parser.add_argument('--suffix',default='');args=parser.parse_args()
assert (ROOT/'docs/local-models.json').is_file(),'Prepare local models first'
image,frames,width,height=PRESETS[args.scene];frames=args.frames or frames;width=args.width or width;height=args.height or height
out=ROOT/'public/video';out.mkdir(parents=True,exist_ok=True)
stem=args.scene+'-native24' if args.scene!='pilot' else 'pilot'
target=out/f'{stem}{args.suffix}.mp4'
prompts={**json.loads((ROOT/'docs/video-prompts.json').read_text()),**json.loads((ROOT/'docs/new-motion-prompts.json').read_text())}
prompt=prompts[args.scene]
env={**os.environ,'TMPDIR':str(ROOT/'.cache/tmp'),'TMP':str(ROOT/'.cache/tmp'),'TEMP':str(ROOT/'.cache/tmp'),'XDG_CACHE_HOME':str(ROOT/'.cache'),'HF_HOME':str(ROOT/'.cache/huggingface'),'PYTHONDONTWRITEBYTECODE':'1','HF_HUB_OFFLINE':'1'}
cmd=[sys.executable,'-u','scripts/ltx-entry.py','generate','--distilled','--model',str(ROOT/'.cache/models/ltx-q4'),'--gemma',str(ROOT/'.cache/models/gemma-q4'),'--prompt',prompt,'--image',str(ROOT/'public/art'/image),'0','1.0','--frames',str(frames),'--width',str(width),'--height',str(height),'--frame-rate','24','--seed',str(args.seed),'--low-ram','--output',str(target)]
if args.scene=='pilot':cmd.insert(-2,'--no-audio')
record={'scene':args.scene,'output':str(target.relative_to(ROOT)),'frames':frames,'width':width,'height':height,'fps':24,'seed':args.seed,'source_image':'public/art/'+image,'prompt':prompt,'method':'Native-speed whole-scene local LTX-2.3, q4, default float32 compute, low-ram block streaming'}
metadata=ROOT/'outputs/checks'/f'generation-{args.scene}{args.suffix}.json';metadata.write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('Starting native-speed',args.scene,frames,'frames',width,height,flush=True)
start=time.monotonic();p=subprocess.run(cmd,cwd=ROOT,env=env)
record.update(exit_code=p.returncode,wall_seconds=round(time.monotonic()-start,2),output_exists=target.exists())
metadata.write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2),flush=True)
raise SystemExit(p.returncode)
