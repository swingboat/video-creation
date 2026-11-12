"""Generate one native-speed whole-scene candidate; only one GPU task at a time."""
import project_env
import argparse,json,os,subprocess,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
PRESETS={'opening':('01-two-shot.png',97),'haruko':('02-haruko.png',97),'shy':('03-shy.png',97),'practice':('04-stance-v2.png',97),'gather':('05-gather.png',73),'cheer':('06-cheer.png',97),'resolve':('07-resolve.png',97),'ending':('08-ending.png',97),'epilogue':('09-epilogue.png',49)}
p=argparse.ArgumentParser();p.add_argument('scene',choices=PRESETS);p.add_argument('--seed',type=int,default=11210);p.add_argument('--suffix',default='-v1');p.add_argument('--frames',type=int);args=p.parse_args()
image,frames=PRESETS[args.scene];frames=args.frames or frames
source=ROOT/'public/art'/image
prompt=json.loads((ROOT/'docs/video-prompts.json').read_text())[args.scene]
target=ROOT/'public/video'/f'{args.scene}-native24{args.suffix}.mp4'
if target.exists():raise SystemExit('Candidate exists. Use a new --suffix to preserve prior versions.')
env={**os.environ,'TMPDIR':str(ROOT/'.cache/tmp'),'TMP':str(ROOT/'.cache/tmp'),'TEMP':str(ROOT/'.cache/tmp'),'HF_HOME':str(ROOT/'.cache/huggingface'),'XDG_CACHE_HOME':str(ROOT/'.cache'),'PYTHONDONTWRITEBYTECODE':'1','HF_HUB_OFFLINE':'1'}
cmd=[sys.executable,'-u','scripts/ltx-entry.py','generate','--distilled','--model',str(ROOT/'.cache/models/ltx-q4'),'--gemma',str(ROOT/'.cache/models/gemma-q4'),'--prompt',prompt,'--image',str(source),'0','1.0','--frames',str(frames),'--width','1024','--height','576','--frame-rate','24','--seed',str(args.seed),'--low-ram','--output',str(target)]
record={'scene':args.scene,'output':str(target.relative_to(ROOT)),'frames':frames,'width':1024,'height':576,'fps':24,'seed':args.seed,'source_image':str(source.relative_to(ROOT)),'source_image_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'prompt':prompt,'method':'LTX-2.3 q4 / MLX whole-scene I2V, float32 default compute, block streaming, sequential Gemma/connector'}
metadata=ROOT/'outputs/checks'/f'generation-{args.scene}{args.suffix}.json';metadata.write_text(json.dumps(record,ensure_ascii=False,indent=2))
start=time.monotonic();print('GENERATING',args.scene,frames,flush=True)
result=subprocess.run(cmd,cwd=ROOT,env=env)
record.update(exit_code=result.returncode,wall_seconds=round(time.monotonic()-start,2),output_exists=target.exists())
metadata.write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2),flush=True)
raise SystemExit(result.returncode)
