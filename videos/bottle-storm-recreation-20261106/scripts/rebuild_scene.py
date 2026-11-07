"""Rebuild the current revision from this video's own base snapshot."""
from pathlib import Path
import subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def run(name):subprocess.run(['node','scripts/run.mjs',name],cwd=ROOT,check=True)
run('animate-bunny')
base=ROOT/'outputs/versions/bunny-v2';base.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'public/bottle-storm.blend',base/'bottle-storm.blend')
shutil.copy2(ROOT/'docs/timeline.json',base/'timeline.json')
run('fish-paths');run('upgrade-fish')
