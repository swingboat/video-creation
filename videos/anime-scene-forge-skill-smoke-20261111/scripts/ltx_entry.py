"""Run the pinned local video pipeline with bounded, project-only caches."""
import atexit,json,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if Path('/opt/homebrew/bin').exists():os.environ['PATH']='/opt/homebrew/bin'+os.pathsep+os.environ.get('PATH','')
for key,sub in [('HF_HOME','.cache/huggingface'),('TMPDIR','.cache/tmp'),('TMP','.cache/tmp'),('TEMP','.cache/tmp'),('XDG_CACHE_HOME','.cache')]:os.environ[key]=str(ROOT/sub)
os.environ['HF_HUB_OFFLINE']='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import mlx.core as mx
mx.set_memory_limit(11*1024**3)
mx.set_cache_limit(0)
start=time.monotonic()
def record():
 print(json.dumps({'elapsed_seconds':round(time.monotonic()-start,2),'mlx_peak_gib':round(mx.get_peak_memory()/1024**3,3)}),flush=True)
atexit.register(record)
from lowram_prompt import install
install(ROOT)
from ltx_pipelines_mlx.cli import main
main()
