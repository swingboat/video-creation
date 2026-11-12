"""Install the exact local generation runtime inside this video project."""
import project_env
import os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
env={**os.environ,'TMPDIR':str(ROOT/'.cache/tmp'),'TMP':str(ROOT/'.cache/tmp'),'TEMP':str(ROOT/'.cache/tmp'),'UV_CACHE_DIR':str(ROOT/'.cache/uv'),'PIP_CACHE_DIR':str(ROOT/'.cache/pip'),'HF_HOME':str(ROOT/'.cache/huggingface')}
env['UV_PYTHON_INSTALL_DIR']=str(ROOT/'.cache/python')
for p in ['.cache/tmp','.cache/uv','.cache/pip']:(ROOT/p).mkdir(parents=True,exist_ok=True)
uv=shutil.which('uv')
if not uv:raise SystemExit('Install uv or add the installed uv executable to PATH, then rerun this script.')
vendor=ROOT/'.cache/vendor/ltx-2-mlx';commit=(ROOT/'docs/local-generator-commit.txt').read_text().strip()
if not vendor.exists():subprocess.run(['git','clone','--filter=blob:none','--no-checkout','https://github.com/dgrauet/ltx-2-mlx.git',str(vendor)],check=True,env=env)
subprocess.run(['git','-C',str(vendor),'checkout',commit],check=True,env=env)
if not (ROOT/'.venv').exists():subprocess.run([uv,'venv','.venv','--python','3.13'],check=True,env=env)
subprocess.run([uv,'pip','install','--python','.venv/bin/python','-r','requirements-local-video.txt'],check=True,env=env)
print('Pinned local video runtime installed')
