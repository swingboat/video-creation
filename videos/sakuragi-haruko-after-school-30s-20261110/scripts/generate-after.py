"""Continue a local production queue only after the preceding GPU inference has exited."""
import project_env
from pathlib import Path
import argparse,json,subprocess,sys,time,os
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
p=argparse.ArgumentParser();p.add_argument('after');p.add_argument('scene');p.add_argument('--suffix',default='-v1');a=p.parse_args()
marker=ROOT/'outputs/checks'/f'generation-{a.after}.json';assert marker.resolve().is_relative_to(ROOT)
while True:
 if marker.exists():
  try:record=json.loads(marker.read_text())
  except json.JSONDecodeError:time.sleep(1);continue
  if 'exit_code' in record:
   if record['exit_code']!=0:raise SystemExit('Preceding inference failed, next GPU task was not started.')
   break
 time.sleep(5)
with (ROOT/'outputs/checks'/f'{a.scene}{a.suffix}.log').open('w') as log:
 result=subprocess.run([sys.executable,'-u','scripts/generate-clip.py',a.scene,f'--suffix={a.suffix}'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
if result.returncode:raise SystemExit(result.returncode)
subprocess.run([sys.executable,'scripts/review-clip.py',f'{a.scene}-native24{a.suffix}'],cwd=ROOT,check=True)
print('Candidate ready for visual acceptance:',a.scene,flush=True)
