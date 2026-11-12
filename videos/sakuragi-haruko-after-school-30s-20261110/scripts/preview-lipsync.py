"""Render a same-audio, same-speed before/after review movie for a candidate."""
import project_env
import argparse,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scene');p.add_argument('--take',default='v1');a=p.parse_args()
candidate=ROOT/f'public/lipsync/candidates/{a.scene}-{a.take}.mp4'
before=ROOT/f'public/lipsync/inputs/{a.scene}-before.mp4'
generation=json.loads((ROOT/f'outputs/checks/lipsync/{a.scene}-{a.take}-generation.json').read_text())
audio=ROOT/generation['audio'];assert audio.resolve().is_relative_to(ROOT)
out=ROOT/f'outputs/checks/lipsync/{a.scene}-{a.take}-comparison.mp4'
font='public/fonts/NotoSansSC.ttf'
filters=(f'[0:v]scale=640:360,setsar=1,pad=640:408:0:48:color=0x151820,'
         f'drawtext=fontfile={font}:text=修复前:x=24:y=8:fontcolor=white:fontsize=25[a];'
         f'[1:v]scale=640:360,setsar=1,pad=640:408:0:48:color=0x151820,'
         f'drawtext=fontfile={font}:text=音频驱动候选:x=24:y=8:fontcolor=white:fontsize=25[b];'
         '[a][b]hstack=shortest=1[v];[2:a]loudnorm=I=-18:TP=-1.5:LRA=9[audio]')
subprocess.run(['ffmpeg','-y','-v','error','-i',str(before),'-i',str(candidate),'-i',str(audio),
    '-filter_complex',filters,'-map','[v]','-map','[audio]','-c:v','libx264','-crf','17',
    '-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000',
    '-shortest','-movflags','+faststart',str(out)],cwd=ROOT,check=True)
print(out)
