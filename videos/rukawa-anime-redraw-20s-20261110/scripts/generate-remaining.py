"""Run remaining independent clips serially, after the shot worker exits."""
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
shot=ROOT/'outputs/checks/generation-shot-short-v2.json'
while True:
 if shot.exists():
  state=json.loads(shot.read_text())
  if state.get('exit_code')==0:break
  if state.get('exit_code') is not None:raise SystemExit('Shot generation failed; remaining queue stopped')
 time.sleep(5)
subprocess.run([sys.executable,'scripts/finish-motion-clip.py','shot'],cwd=ROOT,check=True)
for scene in ['close','rim','celebrate','hero']:
 print('START',scene,flush=True)
 with (ROOT/'outputs/checks'/f'{scene}-generation.log').open('w') as log:
  p=subprocess.run([sys.executable,'-u','scripts/generate-clip.py',scene],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 print('END',scene,'exit',p.returncode,flush=True)
 if p.returncode:raise SystemExit(p.returncode)
print('ALL_CONTINUOUS_CLIPS_READY',flush=True)
