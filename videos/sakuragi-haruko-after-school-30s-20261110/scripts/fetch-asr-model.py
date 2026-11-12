"""Keep the small ASR model used for dialogue verification inside this video."""
import project_env
from pathlib import Path
import json,os
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import HfApi,snapshot_download
ROOT=Path(__file__).resolve().parents[1];manifest=ROOT/'docs/voiceover/asr-model-info.json'
if manifest.exists():info=json.loads(manifest.read_text())
else:
 model=HfApi().model_info('mlx-community/Qwen3-ASR-0.6B-4bit',files_metadata=True)
 info={'repo':model.id,'revision':model.sha,'local':'.cache/tts-models/qwen3-asr-4bit','files':[{'path':f.rfilename,'bytes':f.size} for f in model.siblings]};manifest.write_text(json.dumps(info,indent=2))
snapshot_download(info['repo'],revision=info['revision'],local_dir=ROOT/info['local'],allow_patterns=[f['path'] for f in info['files']],max_workers=3)
info['verified_file_sizes']=all((ROOT/info['local']/f['path']).stat().st_size==f['bytes'] for f in info['files']);assert info['verified_file_sizes']
manifest.write_text(json.dumps(info,indent=2));print('ASR verification model ready',info['revision'])
