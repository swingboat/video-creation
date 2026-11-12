"""Five seconds of original synthesized gym ambience and shot Foley; stdlib only."""
import math,random,wave,array,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];sr=48000;duration=5;n=sr*duration;rng=random.Random(11)
left=[0.0]*n;right=[0.0]*n;slow=0.
for i in range(n):
 t=i/sr;v=rng.uniform(-1,1);slow=.98*slow+.02*v
 amp=.018 if t<1.2 else .006 if t<3.4 else .05*min(1,(t-3.4)/.2)
 left[i]=v*amp+slow*.1;right[i]=rng.uniform(-1,1)*amp+slow*.08

def add(start,length,kind,gain):
 for j in range(int(length*sr)):
  i=int(start*sr)+j
  if i>=n:break
  u=j/sr
  if kind=='shoe':v=math.sin(2*math.pi*(1250*u+400*u*u))*math.exp(-u*22)*min(1,u/.015)
  elif kind=='buzzer':v=(math.sin(2*math.pi*360*u)+.3*math.sin(2*math.pi*1080*u))*min(1,u/.02)*min(1,(length-u)/.04)
  elif kind=='net':v=rng.uniform(-1,1)*math.exp(-u*9)*min(1,u/.02)
  elif kind=='thump':v=math.sin(2*math.pi*(80*u-15*u*u))*math.exp(-u*27)
  elif kind=='clap':v=rng.uniform(-1,1)*math.exp(-u*70)
  else:v=math.sin(2*math.pi*160*u)*math.exp(-u*14)
  left[i]+=v*gain;right[i]+=v*gain*.92
add(.45,.12,'shoe',.11);add(.68,.18,'shoe',.08);add(1.44,.18,'thump',.19)

for when in [.39,.58,.77,1.20,1.45,1.68,1.90]:add(when,.10,'thump',.065)
add(1.18,.22,'buzzer',.10);add(3.35,.45,'net',.21)
for when in [3.60,3.71,3.90,4.03,4.17,4.33,4.41,4.58,4.73,4.85]:add(when,.07,'clap',.12)
# Diffuse arena cheer built from many slowly detuned voices/tones.
for j,freq in enumerate([191,233,277,349,417,511,673]):
 for i in range(int(3.48*sr),n):
  t=(i/sr-3.48);env=min(1,t/.22)*(.65+.35*math.sin(t*(4+j*.4))**2)
  v=math.sin(2*math.pi*(freq*t+.8*math.sin(t*(3+j*.3))))*.014*env
  left[i]+=v;right[i]+=v*math.cos(j*.3)
raw=array.array('h');peak=0.
for i,(l,rr) in enumerate(zip(left,right)):
 t=i/sr;fade=min(1,t/.04)*min(1,(duration-t)/.15)
 l=math.tanh(l*1.7)*fade;rr=math.tanh(rr*1.7)*fade;peak=max(peak,abs(l),abs(rr));raw.extend((int(l*32767),int(rr*32767)))
with wave.open(str(r/'public/soundscape.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(raw.tobytes())
(r/'outputs/checks/audio.json').write_text(json.dumps({'seconds':duration,'sample_rate':sr,'channels':2,'peak':peak,'events':{'release':1,'buzzer':1.18,'swish':3.35,'cheer':3.48}},indent=2))
print('AUDIO_GENERATED',duration,peak)
