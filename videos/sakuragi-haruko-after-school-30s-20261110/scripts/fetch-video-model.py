"""Fetch the exact recorded model revisions, never a moving latest revision."""
import project_env
import json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for key,sub in [('HF_HOME','.cache/huggingface'),('TMPDIR','.cache/tmp'),('TMP','.cache/tmp'),('TEMP','.cache/tmp'),('XDG_CACHE_HOME','.cache')]:
 (ROOT/sub).mkdir(parents=True,exist_ok=True);os.environ[key]=str(ROOT/sub)
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import snapshot_download
for model in json.loads((ROOT/'docs/local-models.json').read_text()):
 snapshot_download(repo_id=model['repo'],revision=model['revision'],allow_patterns=[f['name'] for f in model['files']],local_dir=ROOT/model['local'],max_workers=2)
 print('READY',model['repo'],model['revision'],flush=True)
