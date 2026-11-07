"""Original deterministic 24-second electronic cue; no third-party audio."""
from pathlib import Path
import math,wave,array,random
SR=48000;DURATION=24;N=SR*DURATION
left=array.array('f',[0])*N;right=array.array('f',[0])*N
rng=random.Random(273)
def add(start,dur,fn,pan=0):
 begin=int(start*SR);end=min(N,begin+int(dur*SR))
 for i in range(begin,end):
  t=(i-begin)/SR;v=fn(t);left[i]+=v*(1-pan*.3);right[i]+=v*(1+pan*.3)
chords=[(146.832,220,261.626,329.628),(130.813,195.998,261.626,329.628),(164.814,220,293.665,391.995),(130.813,195.998,261.626,349.228)]
for j,chord in enumerate(chords):
 for k,f in enumerate(chord):
  add(j*6,6,lambda t,f=f:.026*min(1,t/.4)*min(1,(6-t)/.7)*(math.sin(2*math.pi*f*t)+.22*math.sin(2*math.pi*f*1.002*t)),(k-1.5)/2)
for b in range(48):
 start=b*.5
 add(start,.22,lambda t:.17*math.exp(-t*22)*math.sin(2*math.pi*(48*t+3*(1-math.exp(-t*25)))))
 if b%2==1:add(start,.1,lambda t:.014*math.exp(-t*44)*(math.sin(t*7921)+math.sin(t*12187)),.3)
 chord=chords[min(3,int(start/6))];f=chord[b%4]*2
 add(start+.25,.38,lambda t,f=f:.048*min(1,t/.005)*math.exp(-t*10)*math.sin(2*math.pi*f*t),(-1)**b*.6)
for j in (6,12,18):
 add(j-.28,.65,lambda t:.027*math.sin(2*math.pi*(300*t+1100*t*t))*math.sin(math.pi*t/.65)**2,-.4)
 add(j,.6,lambda t:.05*math.exp(-t*7)*math.sin(2*math.pi*880*t),.4)
peak=max(max(abs(x) for x in left),max(abs(x) for x in right))
raw=array.array('h')
for i,(l,r) in enumerate(zip(left,right)):
 fade=min(1,i/(SR*.12),(N-i)/(SR*1.1));raw.append(int(l/peak*.62*fade*32767));raw.append(int(r/peak*.62*fade*32767))
Path('public/audio').mkdir(parents=True,exist_ok=True)
with wave.open('public/audio/studio-score.wav','wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(raw.tobytes())
print('24s stereo, 48kHz, normalized peak -4.15 dBFS')
