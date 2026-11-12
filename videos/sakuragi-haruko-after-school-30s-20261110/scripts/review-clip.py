"""Extract every frame plus overview and hand-contact sheets inside the project."""
import project_env
import argparse,subprocess,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--contact',nargs=4,type=int);a=p.parse_args()
source=ROOT/'public/video'/(a.stem+'.mp4');out=ROOT/'outputs/checks'/a.stem;out.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),str(out/'frame-%04d.jpg')],check=True,timeout=90)
files=sorted(out.glob('frame-*.jpg'))
selected=list(range(0,len(files),3));cols=5;w,h=384,234
sheet=Image.new('RGB',(cols*w,((len(selected)+cols-1)//cols)*h),'#222222');draw=ImageDraw.Draw(sheet)
for n,k in enumerate(selected):
 im=Image.open(files[k]).convert('RGB');im.thumbnail((w,216));x=n%cols*w;y=n//cols*h;sheet.paste(im,(x,y));draw.text((x+5,y+216),f'Frame {k} / {k/24:.3f}s',fill='white')
sheet.save(out/'overview.jpg',quality=92)
if a.contact:
 x,y,cw,ch=a.contact;w,h=240,260;cols=8
 sheet=Image.new('RGB',(cols*w,((len(files)+cols-1)//cols)*h),'#222222');draw=ImageDraw.Draw(sheet)
 for n,f in enumerate(files):
  im=Image.open(f).crop((x,y,x+cw,y+ch)).resize((240,240));px=n%cols*w;py=n//cols*h;sheet.paste(im,(px,py));draw.text((px+4,py+240),str(n),fill='white')
 sheet.save(out/'contact-every-frame.jpg',quality=95)
metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]));(out/'probe.json').write_text(json.dumps(metadata,indent=2))
print(out/'overview.jpg')
