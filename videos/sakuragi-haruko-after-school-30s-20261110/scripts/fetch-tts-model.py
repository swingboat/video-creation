"""Download the pinned local character voice-design model into this project."""
import project_env
from pathlib import Path
import json,shutil,os
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import snapshot_download
ROOT=Path(__file__).resolve().parents[1]
info=json.loads((ROOT/'docs/voiceover/model-info.json').read_text())
folder=ROOT/'.cache/tts-models/qwen3-voicedesign-bf16'
size=sum(f.get('bytes',0) or 0 for f in info['files'])
assert shutil.disk_usage(ROOT).free>size+6*1024**3
snapshot_download(info['repo'],revision=info['revision'],local_dir=folder,allow_patterns=[f['path'] for f in info['files']],max_workers=3)
for item in info['files']:
 file=folder/item['path'];assert file.is_file() and file.stat().st_size==item['bytes'] and not file.is_symlink()
info.update(local=str(folder.relative_to(ROOT)),verified_file_sizes=True)
(ROOT/'docs/voiceover/model-info.json').write_text(json.dumps(info,indent=2))
print('Pinned TTS model ready:',info['revision'],flush=True)
