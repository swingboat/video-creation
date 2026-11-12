"""Run the reviewed-plan shy retry only after the first GPU queue has exited."""
import project_env
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
deadline=time.monotonic()+3600
while True:
    if time.monotonic()>deadline:raise SystemExit('Queue wait timed out; no repair GPU job started.')
    try:report=json.loads((ROOT/'outputs/checks/lipsync/queue.json').read_text())
    except (FileNotFoundError,json.JSONDecodeError):report=[]
    if any(x['exit_code'] for x in report):raise SystemExit('Prior queue failed; no repair GPU job started.')
    if len(report)==5 and report[-1]['scene']=='cheer':break
    time.sleep(5)
log=ROOT/'outputs/checks/lipsync/shy-v2.log'
with log.open('w') as f:
    result=subprocess.run([sys.executable,'-u','scripts/generate-lipsync.py','shy','--take','v2','--frames','89','--seed','11211','--anchors','docs/lipsync/shy-v2-anchors.json'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
raise SystemExit(result.returncode)
