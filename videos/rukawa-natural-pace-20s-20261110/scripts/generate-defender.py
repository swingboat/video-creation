"""Wait for the crowd GPU worker, then generate the defender reaction."""
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
metadata=ROOT/'outputs/checks/generation-crowd-natural4.json'
while True:
 if metadata.exists():
  try:record=json.loads(metadata.read_text())
  except json.JSONDecodeError:record={}
  if 'exit_code' in record:
   assert record['exit_code']==0,'Crowd generation failed'
   break
 time.sleep(5)
with (ROOT/'outputs/checks/defender-natural-generation.log').open('w') as log:
 subprocess.run([sys.executable,'-u','scripts/generate-clip.py','defender','--suffix=-natural3'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run([sys.executable,'scripts/select-native-clips.py','defender'],cwd=ROOT,check=True)
subprocess.run([sys.executable,'scripts/review-clip.py','defender'],cwd=ROOT,check=True)
