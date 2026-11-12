"""Frame-by-frame visual QA with the exact conditioning waveform, no pass inference."""
import project_env
import argparse, json, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scene');p.add_argument('--take',default='v1')
p.add_argument('--crop',nargs=4,type=int,default=[400,70,330,270])
p.add_argument('--label',default='face');a=p.parse_args()
assert a.label.replace('-','').isalnum()
source=ROOT/f'public/lipsync/candidates/{a.scene}-{a.take}.mp4'
out=ROOT/f'outputs/checks/lipsync/{a.scene}-{a.take}';out.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),str(out/'frame-%04d.jpg')],check=True)
generation=json.loads((ROOT/f'outputs/checks/lipsync/{a.scene}-{a.take}-generation.json').read_text())
audio_path=ROOT/generation['audio'];assert audio_path.resolve().is_relative_to(ROOT)
with wave.open(str(audio_path),'rb') as wav:
    assert wav.getsampwidth()==2
    sr=wav.getframerate()
    audio=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').reshape(-1,wav.getnchannels()).astype(np.float64)/32768
files=sorted(out.glob('frame-*.jpg'));rms=[]
for i in range(len(files)):
    chunk=audio[round(i*sr/24):round((i+1)*sr/24)]
    rms.append(float(np.sqrt(np.mean(chunk**2))) if len(chunk) else 0)
cols=8;w=240;h=228
sheet=Image.new('RGB',(cols*w,((len(files)+cols-1)//cols)*h),'#202020');d=ImageDraw.Draw(sheet)
cx,cy,cw,ch=a.crop
for i,f in enumerate(files):
    im=Image.open(f);im=im.crop((cx,cy,cx+cw,cy+ch));im.thumbnail((240,196))
    x=i%cols*w;y=i//cols*h;sheet.paste(im,(x,y))
    d.text((x+4,y+198),f'{i:02d} / {i/24:.3f}s',fill='white')
    d.rectangle((x+4,y+216,x+4+int(min(1,rms[i]/.12)*225),y+223),fill='#e0b25a')
sheet.save(out/f'{a.label}-every-frame.jpg',quality=94)
cols=5;w=384;h=234;selection=list(range(0,len(files),3))
sheet=Image.new('RGB',(cols*w,((len(selection)+cols-1)//cols)*h),'#202020');d=ImageDraw.Draw(sheet)
for n,i in enumerate(selection):
    im=Image.open(files[i]);im.thumbnail((384,216));x=n%cols*w;y=n//cols*h
    sheet.paste(im,(x,y));d.text((x+4,y+218),f'{i:02d} / {i/24:.3f}s',fill='white')
sheet.save(out/'overview.jpg',quality=92)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
(out/'probe.json').write_text(json.dumps(probe,indent=2))
(out/'audio-frame-rms.json').write_text(json.dumps({'fps':24,'rms':rms,'note':'Energy bars assist visual review; they do not measure phoneme or perceptual lip sync.'},indent=2))
print(out)
