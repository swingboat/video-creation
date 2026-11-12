"""Read alpha bounds to register the fifteen supporting-player drawings; no raster edits."""
import subprocess,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];w,h=1024,1536
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(r/'public/art/support-players-v2.png'),'-f','rawvideo','-pix_fmt','rgba','pipe:1'])
cuts=[0,320,596,928,1251,1536];result=[]
for row in range(5):
 poses=[]
 for col in range(3):
  xs=[];ys=[]
  for y in range(cuts[row],cuts[row+1]):
   for x in range(round(col*w/3),round((col+1)*w/3)):
    if raw[(y*w+x)*4+3]>128:xs.append(x);ys.append(y)
  x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
  feet=[x for x,y in zip(xs,ys) if y>y1-11];anchor=sum(feet)/len(feet)
  poses.append({'x':x0,'y':y0,'w':x1-x0+1,'h':y1-y0+1,'footX':round(anchor,2),'opaquePixels':len(xs)})
 result.append(poses)
(r/'src/support-bounds.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
