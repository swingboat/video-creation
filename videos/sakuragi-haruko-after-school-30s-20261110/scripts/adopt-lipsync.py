"""Adopt one separately reviewed audio-driven take, at original speed."""
import project_env
import argparse,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scene');p.add_argument('--take',default='v1');a=p.parse_args()
key=f'{a.scene}-{a.take}'
reviews=json.loads((ROOT/'outputs/checks/lipsync/visual-decisions.json').read_text())
review=reviews[key];assert review['decision']=='selected' and review['playback_1x_complete']
candidate=ROOT/f'public/lipsync/candidates/{key}.mp4'
source_name=f'{a.scene}-a2v-{a.take}.mp4'
shutil.copy2(candidate,ROOT/'public/video'/source_name)
p=ROOT/'docs/edit-decisions.json';decisions=json.loads(p.read_text())
scenes=['shy','smile'] if a.scene=='shy' else [a.scene]
for scene in scenes:
    spec=decisions[scene]
    spec.update(source=source_name,start_frame=52 if scene=='smile' else 0,
                review_status='approved',note=review['observations'])
    spec.pop('crop',None)
p.write_text(json.dumps(decisions,ensure_ascii=False,indent=2))
for scene in scenes:
    subprocess.run([sys.executable,'scripts/select-clips.py',scene],cwd=ROOT,check=True)
selection=ROOT/'docs/lipsync/selected-takes.json'
takes=json.loads(selection.read_text()) if selection.exists() else {}
takes[a.scene]=a.take
selection.write_text(json.dumps(takes,indent=2))
