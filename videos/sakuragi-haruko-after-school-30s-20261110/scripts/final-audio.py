"""Normalize final soundtrack while copying the rendered video stream."""
import project_env
import json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];movie=ROOT/'outputs/sakuragi-haruko-30s.mp4';temp=ROOT/'.cache/tmp/normalized-movie.mp4'
def run(args):
 p=subprocess.run(['ffmpeg','-hide_banner',*args],cwd=ROOT,text=True,capture_output=True,timeout=90)
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stderr
scan=run(['-i',str(movie),'-vn','-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
stats=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',scan,re.S)[-1]);params='loudnorm=I=-18:TP=-1.5:LRA=11:linear=false:print_format=json'
for key,source in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')]:params+=f':{key}={stats[source]}'
log=run(['-y','-i',str(movie),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',params,'-ar','48000','-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart',str(temp)])
os.replace(temp,movie)
result=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',log,re.S)[-1]);(ROOT/'outputs/checks/audio-normalization.json').write_text(json.dumps({'target_lufs':-18,'video_stream_copied':True,'filter_report':result},indent=2))
(ROOT/'outputs/checks/audio-normalization.log').write_text(scan+'\n'+log)
print('Soundtrack normalized, video stream copied')
