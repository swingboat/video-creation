"""Synchronize regenerated narration timing with editable JSX nodes.
Run after generate-voice.py; use --dry-run to inspect first.
"""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'src/timeline.json').read_text())
files={'intro':'Intro','map':'Map','home':'Home','spaces':'Spaces','models':'Models','card':'Card','data':'Data','routes':'Routes','community':'Community','outro':'Outro'}
for scene in manifest['scenes']:
    p=ROOT/'src/scenes'/f'{files[scene["id"]]}.tsx'
    source=p.read_text()
    literal=json.dumps(scene['captions'],ensure_ascii=False,indent=2)
    marker=f'__CAPTIONS_{scene["id"]}__'
    if marker in source:updated=source.replace(marker,literal)
    else:updated=re.sub(r'captions=\{\[.*?\]\}',lambda _:f'captions={{{literal}}}',source,flags=re.S)
    if '--dry-run' in sys.argv:print(p.name,'would change' if updated!=source else 'unchanged')
    else:p.write_text(updated)
root=ROOT/'src/Root.tsx';source=root.read_text()
for scene in manifest['scenes']:
    component=files[scene['id']]
    if component=='Map':component='MapScene'
    source=re.sub(r'(durationInFrames=\{)\d+(\} premountFor=\{fps\}><'+component+r'/>)',lambda m:m[1]+str(scene['durationInFrames'])+m[2],source)
    source=re.sub(r'(<Composition id="[^"]+" component=\{'+component+r'\}.*?durationInFrames=\{)\d+(\})',lambda m:m[1]+str(scene['durationInFrames'])+m[2],source)
source=re.sub(r'(<Composition id="HuggingFaceGuide".*?durationInFrames=\{)\d+(\})',lambda m:m[1]+str(manifest['durationInFrames'])+m[2],source)
if '--dry-run' not in sys.argv:root.write_text(source)
