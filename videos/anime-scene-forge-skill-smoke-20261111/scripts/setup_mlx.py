"""Materialized optional MLX environment. --plan performs no installs/downloads."""
import project_env
import argparse,json,platform,shutil,subprocess,sys
from pathlib import Path
from project_ops import ROOT,local,require

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['video','voice']);p.add_argument('--download',action='store_true');p.add_argument('--plan',action='store_true');a=p.parse_args()
    info=json.loads((ROOT/'docs/mlx-profile.json').read_text())
    models=[m for m in info['models'] if m['role'] in (['video','text'] if a.mode=='video' else ['voice'])]
    size=sum(f['bytes'] for m in models for f in m['files'])
    plan={'mode':a.mode,'model_bytes':size,'model_gib':round(size/1024**3,2),'free_disk_bytes':shutil.disk_usage(ROOT).free,'model_revisions':{m['repo']:m['revision'] for m in models},'will_download':a.download,'executed':False}
    print(json.dumps(plan,indent=2),flush=True)
    if a.plan:return
    require(platform.system()=='Darwin' and platform.machine()=='arm64','This adapter requires Apple Silicon macOS; select another backend')
    uv=shutil.which('uv');require(uv,'Install uv as a system tool or make it available on PATH')
    envdir='.venv' if a.mode=='video' else '.venv-tts';python=ROOT/envdir/'bin/python'
    if a.mode=='video':
        vendor=ROOT/'.cache/vendor/ltx-2-mlx';vendor.parent.mkdir(parents=True,exist_ok=True)
        if not vendor.exists():subprocess.run(['git','clone','--filter=blob:none','--no-checkout',info['source']['url'],str(vendor)],cwd=ROOT,check=True)
        subprocess.run(['git','-C',str(vendor),'checkout',info['source']['commit']],cwd=ROOT,check=True)
    if not python.exists():subprocess.run([uv,'venv',envdir,'--python','3.13'],cwd=ROOT,check=True)
    req='requirements-local-video.txt' if a.mode=='video' else 'requirements-tts.txt'
    subprocess.run([uv,'pip','install','--python',str(python),'-r',req],cwd=ROOT,check=True)
    if a.download:
        missing=sum(f['bytes'] for m in models for f in m['files'] if not (local(m['local'])/f['path']).exists())
        require(shutil.disk_usage(ROOT).free>missing*1.2+2*1024**3,'Insufficient space for requested models plus download/runtime headroom')
        subprocess.run([str(python),'scripts/fetch_mlx_models.py',a.mode],cwd=ROOT,check=True)
    print(json.dumps({'environment_ready':python.exists(),'downloaded_models':a.download,'mode':a.mode}),flush=True)

if __name__=='__main__':
    try:main()
    except (ValueError,subprocess.CalledProcessError) as e:raise SystemExit(str(e))
