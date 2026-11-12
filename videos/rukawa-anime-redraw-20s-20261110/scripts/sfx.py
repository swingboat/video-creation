"""A short deterministic gym buzzer; all motion clips carry their own sound."""
import array,math,wave,random
from pathlib import Path
root=Path(__file__).resolve().parents[1];sr=48000;duration=.55;values=array.array('h')
for i in range(round(sr*duration)):
 t=i/sr;attack=min(1,t/.012);release=min(1,max(0,(duration-t)/.08));s=(math.sin(2*math.pi*132*t)+.35*math.sin(2*math.pi*396*t)+.14*math.sin(2*math.pi*660*t))*.18*attack*release
 values.append(round(32767*s))
with wave.open(str(root/'public/audio/buzzer.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(values.tobytes())
values=array.array('h');rng=random.Random(1179);smooth=0.
for i in range(round(sr*.4)):
 t=i/sr;smooth+=.32*(rng.uniform(-1,1)-smooth);env=min(1,t/.012)*math.exp(-12*t);values.append(round(32767*.28*smooth*env))
with wave.open(str(root/'public/audio/net.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(values.tobytes())
