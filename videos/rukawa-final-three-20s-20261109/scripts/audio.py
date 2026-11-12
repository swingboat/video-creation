import math,random,wave,array,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];SR=44100;DUR=20;N=SR*DUR;rng=random.Random(7711)
def smooth(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def hit(t,start,duration,amp,freq):
 a=t-start
 return amp*math.exp(-a*18)*math.sin(2*math.pi*(freq*a-45*a*a)) if 0<=a<duration else 0.
def squeak(t,start):
 a=t-start
 return .055*math.sin(2*math.pi*(1700*a+2200*a*a))*(math.sin(math.pi*a/.16)**2) if 0<=a<.16 else 0.
left=array.array('h');right=array.array('h');lp=lp2=rp=0.;peak=0.
for i in range(N):
 t=i/SR;noise=rng.uniform(-1,1);other=rng.uniform(-1,1);lp+=.09*(noise-lp);lp2+=.012*(noise-lp2);rp+=.07*(other-rp)
 cheer=smooth(11.60,12.1,t)*(1-.35*smooth(18.8,20,t));tension=1-.63*smooth(5.8,6.8,t)+.63*smooth(11.55,12,t)
 crowd=(.055*tension+.22*cheer)*(lp-lp2*.4);l=crowd+rp*(.018+.075*cheer);rr=crowd-rp*(.014+.067*cheer)
 tonal=0.
 if cheer>0:
  tonal=cheer*.004*(math.sin(2*math.pi*(183*t+2*math.sin(t*3)))+math.sin(2*math.pi*(271*t+3*math.sin(t*2.2)))+math.sin(2*math.pi*(387*t+2*math.sin(t*2.7))))
 s=tonal
 for st in [.12,3.02]:s+=hit(t,st,.32,.23,94)
 for st in [1.1,3.5,5.94]:s+=squeak(t,st)
 for st in [0.7,2.35,4.18,6.02]:s+=hit(t,st,.30,.10,58)
 if 7.90<=t<8.30:
  a=t-7.9;en=smooth(0,.018,a)*(1-smooth(.28,.4,a));s+=.12*en*(math.sin(2*math.pi*132*a)+.33*math.sin(2*math.pi*396*a))
 if 11.55<=t<11.85:
  a=t-11.55;s+=.15*noise*math.exp(-a*15)*smooth(0,.012,a)
 if 11.64<=t<12.0:
  a=t-11.64;s+=.035*math.exp(-a*10)*(math.sin(2*math.pi*660*a)+.5*math.sin(2*math.pi*990*a))
 end=1-smooth(19.55,20,t);l=math.tanh((l+s)*1.45)*end;rr=math.tanh((rr+s)*1.45)*end;peak=max(peak,abs(l),abs(rr));left.append(int(l*30000));right.append(int(rr*30000))
interleaved=array.array('h');interleaved.extend(v for pair in zip(left,right) for v in pair)
out=R/'public/audio/arena.wav'
with wave.open(str(out),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(interleaved.tobytes())
(R/'outputs/checks/audio-report.json').write_text(json.dumps({'seconds':DUR,'rate':SR,'channels':2,'sample_peak':peak,'source':'Locally synthesized arena ambience, squeaks, buzzer and net sound; no sampled music or voices.'},indent=2));print('AUDIO_READY',out.name,'PEAK',peak)
