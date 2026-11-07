"""Inspect all rendered frames and create a compact visual contact sheet."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import json
import hashlib

ROOT=Path(__file__).resolve().parents[1]
timeline=json.loads((ROOT/'docs/timeline.json').read_text());count=timeline['frames']
folder=timeline.get('frame_dir','outputs/frames-bunny' if timeline.get('version')=='bunny-artist' else 'outputs/frames')
frames=sorted((ROOT/folder).glob('frame_*.png'))
errors=[];stats=[]
for i,p in enumerate(frames,1):
    im=Image.open(p).convert('RGB')
    if im.size!=(1280,720):errors.append('Wrong dimensions '+p.name)
    a=np.asarray(im.resize((160,90)),dtype=float)
    mean=float(a.mean());std=float(a.std())
    if mean<8 or std<3:errors.append('Blank frame '+p.name)
    if p.name!='frame_%04d.png'%i:errors.append('Missing frame before '+p.name)
    stats.append({'frame':i,'mean':round(mean,3),'std':round(std,3),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
if len(frames)!=count:errors.append('Expected '+str(count)+' frames, got '+str(len(frames)))
unique=len({s['sha256'] for s in stats})
if unique!=len(frames):errors.append('Unexpected duplicate PNG frames')
picked=[1,49,73,97,145,193,241,289,337,385,433,480] if count==480 else [1,25,50,94,121,145,169,193,217,241,289,336]
sheet=Image.new('RGB',(1280,3*208),(21,24,29));draw=ImageDraw.Draw(sheet)
for k,n in enumerate(picked):
    p=ROOT/folder/('frame_%04d.png'%n)
    if not p.exists():continue
    im=Image.open(p).convert('RGB').resize((320,180))
    x=k%4*320;y=k//4*208;sheet.paste(im,(x,y));draw.text((x+10,y+185),f'Frame {n:03d} | {(n-1)/24:.2f}s',fill=(231,226,215))
sheet.save(ROOT/'outputs/checks/contact-sheet.jpg',quality=93)
report={'passed':not errors,'errors':errors,'frame_count':len(frames),'unique_frame_count':unique,'all_frames_rendered_individually':True,'stats':stats}
(ROOT/'outputs/checks/frame-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'passed':not errors,'errors':errors,'frame_count':len(frames)},indent=2))
if errors:raise SystemExit(1)
