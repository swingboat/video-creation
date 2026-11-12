"""Continue the current production queue with the revised stance, after ending releases the GPU."""
import project_env
from pathlib import Path
import json,subprocess,sys,time,os
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
marker=ROOT/'outputs/checks/generation-ending-v1.json'
while True:
 if marker.exists():
  try:record=json.loads(marker.read_text())
  except json.JSONDecodeError:
   time.sleep(1);continue
  if 'exit_code' in record:
   if record['exit_code']!=0:raise SystemExit('Ending generation failed; no next GPU task launched.')
   break
 time.sleep(5)
print('Ending inference has exited. Starting revised stance.',flush=True)
with (ROOT/'outputs/checks/practice-v2.log').open('w') as log:
 result=subprocess.run([sys.executable,'-u','scripts/generate-clip.py','practice','--suffix=-v2'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
if result.returncode:raise SystemExit(result.returncode)
subprocess.run([sys.executable,'scripts/review-clip.py','practice-native24-v2'],cwd=ROOT,check=True)
print('Revised stance candidate ready for visual acceptance.',flush=True)
