"""Download only the local I2V inference weights needed for this project."""
import json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for key,sub in [('HF_HOME','.cache/huggingface'),('TMPDIR','.cache/tmp'),('TMP','.cache/tmp'),('TEMP','.cache/tmp'),('XDG_CACHE_HOME','.cache')]:
 os.environ[key]=str(ROOT/sub)
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['HF_HUB_DOWNLOAD_TIMEOUT']='120'
os.environ['HF_HUB_ETAG_TIMEOUT']='30'
from huggingface_hub import HfApi,snapshot_download

plans=[('dgrauet/ltx-2.3-mlx-q4','ltx-q4',['config.json','embedded_config.json','quantize_config.json','split_model.json','transformer-distilled-1.1.safetensors','connector.safetensors','vae_encoder.safetensors','vae_decoder.safetensors','audio_vae.safetensors','vocoder.safetensors','spatial_upscaler_x2_v1_1.safetensors','spatial_upscaler_x2_v1_1_config.json','LICENSE']),('mlx-community/gemma-3-12b-it-4bit','gemma-q4',['*.json','*.safetensors','*.model','LICENSE*','README.md'])]
manifest=[]
for repo,name,patterns in plans:
 info=HfApi().model_info(repo,files_metadata=True)
 import fnmatch
 selected=[s for s in info.siblings if any(fnmatch.fnmatch(s.rfilename,p) for p in patterns)]
 size=sum(s.size or 0 for s in selected)
 free=shutil.disk_usage(ROOT).free
 print(json.dumps({'repo':repo,'revision':info.sha,'download_bytes':size,'free_bytes':free,'files':[s.rfilename for s in selected]}),flush=True)
 assert size<free-8*1024**3,'Insufficient disk space with 8GB reserve'
 folder=ROOT/'.cache/models'/name
 snapshot_download(repo,revision=info.sha,allow_patterns=patterns,local_dir=folder,max_workers=3)
 manifest.append({'repo':repo,'revision':info.sha,'local':str(folder.relative_to(ROOT)),'files':[{'name':s.rfilename,'bytes':s.size} for s in selected]})
(ROOT/'docs/local-models.json').write_text(json.dumps(manifest,indent=2))
print('LOCAL_MODELS_READY',flush=True)
