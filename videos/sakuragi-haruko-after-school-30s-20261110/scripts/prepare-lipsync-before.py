"""Reconstruct original accepted picture for repeatable same-audio comparisons."""
import project_env
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
decisions=json.loads((ROOT/'docs/lipsync/before-edit-decisions.json').read_text())
for scene in ['opening','haruko','shy','cheer','resolve','ending']:
    target=ROOT/f'public/lipsync/inputs/{scene}-before.mp4'
    if target.exists():continue
    specs=[decisions[k] for k in (['shy','smile'] if scene=='shy' else [scene])]
    cmd=['ffmpeg','-y','-v','error'];filters=[]
    for n,s in enumerate(specs):
        cmd+=['-i',str(ROOT/'public/video'/s['source'])]
        steps=[f"trim=start_frame={s['start_frame']}:end_frame={s['start_frame']+s['frames']}",'setpts=PTS-STARTPTS']
        if s.get('crop'):steps+=['crop='+':'.join(map(str,s['crop']))]
        steps+=['scale=1280:720:flags=lanczos','setsar=1']
        filters+=[f'[{n}:v]'+','.join(steps)+f'[v{n}]']
    if len(specs)>1:
        filters+=[''.join(f'[v{i}]' for i in range(len(specs)))+f'concat=n={len(specs)}:v=1:a=0[v]'];output='[v]'
    else:output='[v0]'
    cmd+=['-filter_complex',';'.join(filters),'-map',output,'-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-fps_mode','passthrough','-movflags','+faststart',str(target)]
    subprocess.run(cmd,cwd=ROOT,check=True);print('Archived original picture',scene,flush=True)
