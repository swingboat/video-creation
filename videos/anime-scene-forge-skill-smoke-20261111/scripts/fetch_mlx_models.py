import project_env
import argparse,json,os
from project_ops import ROOT,local,require
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import snapshot_download
p=argparse.ArgumentParser();p.add_argument('mode',choices=['video','voice']);a=p.parse_args()
profile=json.loads((ROOT/'docs/mlx-profile.json').read_text())
for model in profile['models']:
    if model['role'] not in (['video','text'] if a.mode=='video' else ['voice']):continue
    dest=local(model['local'])
    snapshot_download(repo_id=model['repo'],revision=model['revision'],allow_patterns=[f['path'] for f in model['files']],local_dir=dest,max_workers=2)
    for file in model['files']:
        path=dest/file['path'];require(path.is_file() and path.stat().st_size==file['bytes'],f'Incomplete model file: {file["path"]}')
    print('Fetched fixed revision:',model['repo'],model['revision'],flush=True)
