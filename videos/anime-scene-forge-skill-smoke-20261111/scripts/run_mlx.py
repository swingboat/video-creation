"""Run versioned I2V/A2V through the fixed MLX adapter; --dry-run is CPU-only."""
import project_env
import argparse,json,subprocess,time,sys
from project_ops import ROOT,local,sha,load,get_shot,require,emit
from gpu_lock import gpu_task

def main():
    p=argparse.ArgumentParser();p.add_argument('shot');p.add_argument('--mode',choices=['i2v','a2v'],required=True)
    p.add_argument('--image',required=True);p.add_argument('--prompt',required=True);p.add_argument('--take',required=True)
    p.add_argument('--frames',type=int,default=97);p.add_argument('--width',type=int,default=1024);p.add_argument('--height',type=int,default=576)
    p.add_argument('--seed',type=int,default=11210);p.add_argument('--anchors');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    import re
    require(re.fullmatch(r'[a-zA-Z0-9-]+',a.take),'Use a safe take identifier')
    data=load();s=get_shot(data,a.shot);profile=json.loads((ROOT/'docs/mlx-profile.json').read_text())
    require(data['format']['fps']==24,'This reference profile is validated at native 24fps')
    require(a.frames>=s['frames'] and (a.frames-1)%8==0 and min(a.width,a.height)>0 and a.width%64==a.height%64==0,'Use frames=8k+1 and dimensions divisible by64')
    image=local(a.image);prompt_path=local(a.prompt);prompt=prompt_path.read_text().strip();require(image.is_file() and prompt,'Image/prompt missing')
    target=ROOT/f'public/candidates/{s["id"]}-{a.take}.mp4';require(not target.exists(),'Preserving existing candidate; use a new take')
    models={m['role']:m for m in profile['models']};python=ROOT/'.venv/bin/python'
    cmd=[str(python),'-u','scripts/ltx_entry.py','a2v' if a.mode=='a2v' else 'generate','--distilled','--model',str(local(models['video']['local'])),'--gemma',str(local(models['text']['local'])),'--prompt',prompt,'--image',str(image),'0','1.0','--frames',str(a.frames),'--width',str(a.width),'--height',str(a.height),'--frame-rate','24','--seed',str(a.seed),'--low-ram','--output',str(target)]
    record={'mode':a.mode,'backend':'ltx-2-mlx','sourceCommit':profile['source']['commit'],'modelRevisions':{m['repo']:m['revision'] for m in models.values() if m['role'] in ['video','text']},'image':image.relative_to(ROOT).as_posix(),'imageSha256':sha(image),'promptFile':prompt_path.relative_to(ROOT).as_posix(),'promptSha256':sha(prompt_path),'prompt':prompt,'frames':a.frames,'width':a.width,'height':a.height,'fps':24,'seed':a.seed,'output':target.relative_to(ROOT).as_posix()}
    if a.mode=='a2v':
        d=s.get('dialogue');require(d and d.get('driverFile'),'Prepare the adopted voice/driver first')
        audio=local(d['driverFile'],True);require(sha(audio)==d['driverSha256'],'Driver changed')
        import wave
        with wave.open(str(audio),'rb') as f:require(f.getnframes()/f.getframerate()>=a.frames/24-1e-6,'Driver shorter than source render')
        cmd+=['--audio',str(audio)];record.update(audio=audio.relative_to(ROOT).as_posix(),audioSha256=sha(audio))
    if a.anchors:
        anchors=json.loads(local(a.anchors).read_text());record['anchors']=anchors
        for anchor in anchors:
            path=local(anchor['image']);require(path.is_file() and 0<=anchor['frame']<a.frames,'Invalid anchor')
            cmd+=['--image',str(path),str(anchor['frame']),str(anchor['strength']),anchor.get('binding','guide')]
    if a.dry_run:
        print(json.dumps({'executed':False,'command':cmd,'record':record,'python_exists':python.exists()},ensure_ascii=False,indent=2));return
    require(python.exists(),'Install the project-local MLX environment first')
    for role in ['video','text']:require(local(models[role]['local']).is_dir(),'Fetch the fixed model pack first')
    metadata=ROOT/f'docs/generation/{s["id"]}-{a.take}.json';emit(metadata,record)
    start=time.monotonic()
    with gpu_task('video'):
        with (ROOT/f'outputs/checks/{s["id"]}-{a.take}-generation.log').open('w') as log:
            result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    record.update(exitCode=result.returncode,wallSeconds=round(time.monotonic()-start,2))
    if target.is_file():record['outputSha256']=sha(target)
    emit(metadata,record);print(json.dumps(record,ensure_ascii=False,indent=2));raise SystemExit(result.returncode)

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,FileNotFoundError) as e:raise SystemExit(str(e))
