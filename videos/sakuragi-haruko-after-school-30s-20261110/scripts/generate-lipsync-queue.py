"""Sequential GPU generation only. Candidates still require separate visual approval."""
import project_env
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
queue=[('haruko',97),('shy',89),('opening',97),('ending',65),('cheer',97)]
report=[]
for scene,frames in queue:
    target=ROOT/f'public/lipsync/candidates/{scene}-v1.mp4'
    if target.exists():raise SystemExit(f'Preserving existing take: {target}')
    log=ROOT/f'outputs/checks/lipsync/{scene}-v1.log'
    start=time.monotonic()
    with log.open('w') as f:
        result=subprocess.run([sys.executable,'-u','scripts/generate-lipsync.py',scene,'--frames',str(frames)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    report.append({'scene':scene,'exit_code':result.returncode,'seconds':round(time.monotonic()-start,2)})
    (ROOT/'outputs/checks/lipsync/queue.json').write_text(json.dumps(report,indent=2))
    if result.returncode:raise SystemExit(result.returncode)
    print('Generated candidate; not yet approved:',scene,flush=True)
