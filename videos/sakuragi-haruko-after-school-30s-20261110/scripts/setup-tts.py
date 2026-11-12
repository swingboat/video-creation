"""Install the pinned, independent local voice environment in this video."""
import project_env
from pathlib import Path
import os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
os.environ['UV_PYTHON_INSTALL_DIR']=str(ROOT/'.cache/python');os.environ['UV_LINK_MODE']='copy'
uv=shutil.which('uv');assert uv,'Install uv as a system tool first'
if not (ROOT/'.venv-tts').exists():subprocess.run([uv,'venv','.venv-tts','--python','3.13'],check=True)
subprocess.run([uv,'pip','install','--python','.venv-tts/bin/python','-r','requirements-tts.txt'],check=True)
