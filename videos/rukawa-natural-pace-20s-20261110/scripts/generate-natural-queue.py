"""Generate new native-duration footage serially, after the hero job ends."""
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
hero=ROOT/'outputs/checks/generation-hero-natural4.json'
while True:
 if hero.exists():
  try:record=json.loads(hero.read_text())
  except json.JSONDecodeError:record={}
  if 'exit_code' in record:
   assert record['exit_code']==0,'Hero generation failed; do not overlap inference jobs.'
   break
 time.sleep(5)
for name in ['dribble','crowd']:
 print('Starting serial native footage:',name,flush=True)
 log=ROOT/'outputs/checks'/f'{name}-natural-generation.log'
 with log.open('w') as output:
  subprocess.run([sys.executable,'-u','scripts/generate-clip.py',name,'--suffix=-natural4'],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True)
 subprocess.run([sys.executable,'scripts/select-native-clips.py',name],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'scripts/review-clip.py',name],cwd=ROOT,check=True)
print('Native footage queue finished',flush=True)
