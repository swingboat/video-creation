"""Inspect actual export frames at every edit boundary and key palm contact."""
import project_env
from pathlib import Path
import subprocess,json,shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'outputs/checks/final-frames';out.mkdir(parents=True,exist_ok=True)
frames=[0,36,95,96,144,191,192,216,243,244,260,277,278,302,373,374,405,433,434,439,448,457,466,527,528,564,623,624,660,683,684,700,719]
expression='select='+'+'.join(f'eq(n\\,{n})' for n in frames)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'outputs/sakuragi-haruko-30s.mp4'),'-vf',expression,'-fps_mode','passthrough',str(out/'frame-%04d.jpg')],check=True,timeout=90)
cols=4;w,h=400,245;sheet=Image.new('RGB',(cols*w,((len(frames)+cols-1)//cols)*h),'#222');draw=ImageDraw.Draw(sheet)
for i,frame in enumerate(frames):
 file=out/f'frame-{i+1:04d}.jpg';im=Image.open(file).convert('RGB');im.thumbnail((400,225));x=i%cols*w;y=i//cols*h;sheet.paste(im,(x,y));draw.text((x+5,y+227),f'Frame {frame} / {frame/24:.3f}s',fill='white')
sheet.save(out/'overview.jpg',quality=94)
shutil.copy2(out/f'frame-{frames.index(660)+1:04d}.jpg',ROOT/'outputs/cover.jpg')
(out/'frames.json').write_text(json.dumps({'export':'outputs/sakuragi-haruko-30s.mp4','frames':frames,'note':'Every edit boundary, key clap contacts and caption/ending samples. Read alongside source-frame reviews and actual 1x full playback.'},indent=2))
print(out/'overview.jpg')
