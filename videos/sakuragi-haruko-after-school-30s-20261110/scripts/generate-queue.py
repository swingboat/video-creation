"""Sequential local queue: one GPU inference process, restartable candidates."""
import project_env
from pathlib import Path
import subprocess,sys,json,time,os
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
scenes=[('practice','-v2'),('opening','-v1'),('haruko','-v1'),('shy','-v1'),('cheer','-v1'),('resolve','-v1'),('ending','-v1'),('epilogue','-v1')]
for scene,suffix in scenes:
 metadata=ROOT/'outputs/checks'/f'generation-{scene}{suffix}.json'
 if metadata.exists() and json.loads(metadata.read_text()).get('exit_code')==0:
  print('SKIP existing candidate',scene,flush=True);continue
 with (ROOT/'outputs/checks'/f'{scene}{suffix}.log').open('w') as log:
  result=subprocess.run([sys.executable,'-u','scripts/generate-clip.py',scene,f'--suffix={suffix}'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise SystemExit(f'{scene} failed, see its log')
 print('GENERATED',scene,time.strftime('%Y-%m-%dT%H:%M:%S%z'),flush=True)
 subprocess.run([sys.executable,'scripts/review-clip.py',f'{scene}-native24{suffix}'],cwd=ROOT,check=True)
print('ALL CANDIDATES GENERATED; visual acceptance is separate',flush=True)
