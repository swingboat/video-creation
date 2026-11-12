"""Project-local lock only. Agent must also serialize GPU work across projects."""
import contextlib,json,os,time
from project_ops import ROOT
@contextlib.contextmanager
def gpu_task(kind):
    path=ROOT/'.cache/tmp/gpu-task.lock'
    try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:raise SystemExit('A project GPU lock exists. Check its PID and task before retrying; do not remove a live lock.')
    try:
        with os.fdopen(fd,'w') as f:json.dump({'pid':os.getpid(),'kind':kind,'created':time.time()},f)
        yield
    finally:path.unlink(missing_ok=True)
