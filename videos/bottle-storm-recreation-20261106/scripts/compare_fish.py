"""Create a synchronized, enlarged before/after motion inspection clip."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess
ROOT=Path(__file__).resolve().parents[1]
labels=Image.new('RGBA',(1024,400),(0,0,0,0));d=ImageDraw.Draw(labels);font=ImageFont.load_default(size=23)
d.text((20,8),'BEFORE | rigid body, fixed heading',font=font,fill='#e3ded2')
d.text((20,208),'AFTER | flexible body, tail beat, continuous turns',font=font,fill='#e3ded2')
p=ROOT/'outputs/checks/fish/comparison-labels.png';labels.save(p)
f="[0:v]trim=duration=8,setpts=PTS-STARTPTS,crop=720:104:245:403,scale=1024:148[b];[1:v]trim=duration=8,setpts=PTS-STARTPTS,crop=720:104:245:403,scale=1024:148[a];color=c=0x151a1e:s=1024x400:r=24:d=8[bg];[bg][b]overlay=0:40[t];[t][a]overlay=0:240[t2];[t2][2:v]overlay=0:0[v]"
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(ROOT/'public/bunny-artist-picture.mp4'),'-i',str(ROOT/'public/previews/fish-motion-hq-8s.mp4'),'-i',str(p),'-filter_complex',f,'-map','[v]','-t','8','-r','24','-an','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'outputs/checks/fish/before-after-8s.mp4')],cwd=ROOT,check=True)
