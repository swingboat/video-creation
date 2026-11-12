"""All generated/cache/temp files belong to this project."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
for key,sub in [('TMPDIR','.cache/tmp'),('TMP','.cache/tmp'),('TEMP','.cache/tmp'),('XDG_CACHE_HOME','.cache'),('HF_HOME','.cache/huggingface'),('UV_CACHE_DIR','.cache/uv'),('UV_PYTHON_INSTALL_DIR','.cache/python'),('PIP_CACHE_DIR','.cache/pip')]:
    folder=ROOT/sub;folder.mkdir(parents=True,exist_ok=True);os.environ[key]=str(folder)
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['UV_LINK_MODE']='copy'
