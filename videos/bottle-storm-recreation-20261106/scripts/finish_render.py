"""Finish the active local render, then validate, encode and compose its output."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
tmp=str(ROOT/'.cache/tmp')
os.environ.update({'TMPDIR':tmp,'TMP':tmp,'TEMP':tmp})
timeline=json.loads((ROOT/'docs/timeline.json').read_text());count=timeline['frames']
final=timeline.get('final_video','outputs/bottle-storm-bunny-20s.mp4')
checks='outputs/checks/fish' if timeline.get('fish_revision') else 'outputs/checks/bunny'
last=-1;last_progress=time.monotonic();last_print=0
while True:
    try:
        d=json.loads((ROOT/'outputs/checks/render-final.json').read_text());done=sum(1 for r in d['frames'] if r['path'].startswith(timeline.get('frame_dir','outputs/frames-bunny')+'/'))
    except (FileNotFoundError,json.JSONDecodeError):
        time.sleep(2);continue
    if done>=count:break
    if done!=last:last=done;last_progress=time.monotonic()
    if time.monotonic()-last_print>=45:
        print('CYCLES_PROGRESS',done,'/',count,flush=True);last_print=time.monotonic()
    if time.monotonic()-last_progress>900:raise RuntimeError('Cycles has made no progress for 15 minutes')
    time.sleep(5)

commands=[
    ('frame-qa',[sys.executable,'scripts/qa_frames.py']),
    ('encode',['node','scripts/run.mjs','encode']),
    ('remotion-render',['node','scripts/run.mjs','render']),
    ('final-check',['node','scripts/run.mjs','check']),
    ('decode-check',['ffmpeg','-v','error','-i',final,'-f','null','-']),
    ('final-frame-extract',['ffmpeg','-hide_banner','-loglevel','error','-y','-i',final,'-vf',"select='eq(n,0)+eq(n,72)+eq(n,192)+eq(n,336)+eq(n,396)+eq(n,444)+eq(n,479)'",'-fps_mode','vfr','-frames:v','7',checks+'/final-video-frame-%02d.png']),
]
for name,command in commands:
    print('START',name,flush=True)
    with (ROOT/checks/(name+'.log')).open('w') as log:
        result=subprocess.run(command,cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(name+' failed: inspect its log')
    print('PASS',name,flush=True)
print('FINAL_VIDEO_READY',flush=True)
