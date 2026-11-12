"""Generate one whole-scene motion clip locally after model preparation."""
import argparse,json,os,subprocess,sys,time,shutil,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
parser=argparse.ArgumentParser();parser.add_argument('scene',choices=['pilot','shot','close','rim','celebrate','hero']);parser.add_argument('--frames',type=int,default=None);parser.add_argument('--width',type=int,default=None);parser.add_argument('--height',type=int,default=None);parser.add_argument('--seed',type=int,default=7711);parser.add_argument('--suffix',default='');args=parser.parse_args()
print('Waiting for local model preparation if necessary',flush=True)
while not (ROOT/'docs/local-models.json').exists():time.sleep(5)
presets={'pilot':('gather-scene.png',49,768,448),'shot':('gather-scene.png',49,768,448),'close':('close-scene.png',73,1024,576),'rim':('rim-scene.png',49,1024,576),'celebrate':('celebrate-grounded-v2.png',49,1024,576),'hero':('hero-scene.png',49,1024,576)}
image,frames,width,height=presets[args.scene];frames=args.frames or frames;width=args.width or width;height=args.height or height
out=ROOT/('outputs/checks' if args.scene=='pilot' else 'public/video');out.mkdir(parents=True,exist_ok=True)
stem=args.scene+'-native24' if args.scene in ['close','rim','celebrate','hero'] else args.scene
target=out/f'{stem}{args.suffix}.mp4'
prompts=json.loads((ROOT/'docs/video-prompts.json').read_text());prompt=prompts[args.scene]
env={**os.environ,'TMPDIR':str(ROOT/'.cache/tmp'),'TMP':str(ROOT/'.cache/tmp'),'TEMP':str(ROOT/'.cache/tmp'),'XDG_CACHE_HOME':str(ROOT/'.cache'),'HF_HOME':str(ROOT/'.cache/huggingface'),'PYTHONDONTWRITEBYTECODE':'1','HF_HUB_OFFLINE':'1'}
cmd=[sys.executable,'-u','scripts/ltx-entry.py','generate','--distilled','--model',str(ROOT/'.cache/models/ltx-q4'),'--gemma',str(ROOT/'.cache/models/gemma-q4'),'--prompt',prompt,'--image',str(ROOT/'public/art'/image),'0','1.0','--frames',str(frames),'--width',str(width),'--height',str(height),'--frame-rate','24','--seed',str(args.seed),'--low-ram','--no-audio','--output',str(target)]
if args.scene!='pilot':cmd.remove('--no-audio')
record={'scene':args.scene,'output':str(target.relative_to(ROOT)),'frames':frames,'width':width,'height':height,'fps':24,'seed':args.seed,'prompt':prompt,'method':'whole-scene local LTX-2.3 image-to-video, q4, block streaming','dit_compute_dtype':os.environ.get('LTX2_COMPUTE_DTYPE','default-float32')}
(ROOT/'outputs/checks'/f'generation-{args.scene}{args.suffix}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('Starting',args.scene,frames,'frames',width,height,flush=True)
start=time.monotonic();p=subprocess.run(cmd,cwd=ROOT,env=env)
record.update(exit_code=p.returncode,wall_seconds=round(time.monotonic()-start,2),output_exists=target.exists())
if p.returncode==0 and target.exists():
 if args.scene=='pilot':
  (ROOT/'public/video').mkdir(exist_ok=True);shutil.copy2(target,ROOT/'public/video/pilot.mp4')
 if args.scene in ['close','rim','celebrate','hero'] and not args.suffix:
  native_record=record.copy()
  (ROOT/'outputs/checks'/f'generation-{args.scene}-native.json').write_text(json.dumps(native_record,ensure_ascii=False,indent=2))
  subprocess.run([sys.executable,'scripts/finish-motion-clip.py',args.scene],cwd=ROOT,check=True)
  record=json.loads((ROOT/'outputs/checks'/f'generation-{args.scene}.json').read_text());record['native_generation']=native_record;record['wall_seconds']=native_record['wall_seconds']
 if not args.suffix:
  status=ROOT/'src/media-status.ts';raw=status.read_text();raw=re.sub(r'\b'+args.scene+r':false',args.scene+':true',raw);status.write_text(raw)
(ROOT/'outputs/checks'/f'generation-{args.scene}{args.suffix}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2),flush=True)
raise SystemExit(p.returncode)
