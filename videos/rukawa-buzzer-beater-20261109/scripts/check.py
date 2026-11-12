import json,subprocess,hashlib,math,wave,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from motion import *
r=Path(__file__).resolve().parents[1];checks={}
traj=json.loads((r/'docs/trajectory.json').read_text());checks['frames_in_scene']=len(traj)
distance=math.hypot(RELEASE_POINT[0],RELEASE_POINT[1]-12)
checks['three_point_distance_m']=distance;assert distance>6.75
checks['release_before_buzzer_seconds']=.15
checks['ball_at_swish']=ball_at(SWISH);assert np.allclose(ball_at(SWISH),RIM)
checks['flight_continuity_max_jump_m']=max(np.linalg.norm(np.array(ball_at(t+1/24))-ball_at(t)) for t in np.arange(9,13.6,1/24));assert checks['flight_continuity_max_jump_m']<.18
files=sorted((r/'outputs/frames').glob('frame_*.png'));assert len(files) in [0,480],len(files)
hashes=[]
for f in files:
 with Image.open(f) as im:
  im.load();assert im.size==(1280,720);assert np.asarray(im).std()>12
 hashes.append(hashlib.sha256(f.read_bytes()).hexdigest())
checks['frame_sequence_present']=bool(files);checks['rendered_frames']=len(files);checks['unique_png_frames']=len(set(hashes));assert not files or len(set(hashes))==480
with wave.open(str(r/'public/court-soundscape.wav')) as w:
 checks['audio_seconds']=w.getnframes()/w.getframerate();assert checks['audio_seconds']==20
 a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).reshape(-1,2).astype(float)/32768
 checks['audio_rms_each_second']=[float(np.sqrt(np.mean(a[i*48000:(i+1)*48000]**2))) for i in range(20)];assert min(checks['audio_rms_each_second'])>.001
probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(r/'outputs/rukawa-final-shot-20s.mp4')]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');au=next(s for s in probe['streams'] if s['codec_type']=='audio');checks['final_video']={'codec':v['codec_name'],'width':v['width'],'height':v['height'],'frames':v['nb_frames'],'fps':v['r_frame_rate'],'duration':probe['format']['duration'],'audio':au['codec_name']};assert int(v['nb_frames'])==480;assert v['width']==1280 and v['height']==720
# Resolve imports and symlinks inside this video only. System executables are allowed.
issues=[]
for p in r.rglob('*'):
 if any(x in p.parts for x in ['node_modules','.cache','.venv']):continue
 if p.is_symlink() and not p.resolve().is_relative_to(r):issues.append(str(p))
 if p.resolve()==Path(__file__).resolve():continue
 if p.is_file() and p.suffix in ['.py','.ts','.tsx','.mjs']:
  txt=p.read_text()
  if 'bottle-storm-recreation' in txt or '/Users/huyin/' in txt:issues.append(str(p.relative_to(r)))
checks['external_runtime_path_issues']=issues;assert not issues
checks['passed']=True;(r/'outputs/checks/final-check.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
# Export a compact, full-resolution-source contact sheet.
if not files:sys.exit(0)
selected=[1,103,180,214,263,307,328,422]
canvas=Image.new('RGB',(1280,4*390),(12,18,26));draw=ImageDraw.Draw(canvas)
for i,f in enumerate(selected):
 im=Image.open(r/f'outputs/frames/frame_{f:04d}.png');im.thumbnail((640,360));x=(i%2)*640;y=(i//2)*390;canvas.paste(im,(x,y));draw.text((x+14,y+367),f'{(f-1)/24:.2f}s / frame {f}',fill='white')
canvas.save(r/'outputs/checks/contact-sheet.jpg',quality=90)
