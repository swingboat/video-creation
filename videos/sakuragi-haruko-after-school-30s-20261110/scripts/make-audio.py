"""Original 12-bar 96 BPM electric-piano cue, room tone and frame-aligned synthetic effects."""
import project_env
from pathlib import Path
import json,wave,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];SR=48000;DURATION=30;N=SR*DURATION
rng=np.random.default_rng(11210);mix=np.zeros((N,2),dtype=np.float64)
def add(sound,when,gain=1,pan=0):
 start=round(when*SR);sound=np.asarray(sound);end=min(N,start+len(sound))
 if end<=start:return
 segment=sound[:end-start]*gain
 mix[start:end,0]+=segment*math.sqrt((1-pan)/2);mix[start:end,1]+=segment*math.sqrt((1+pan)/2)
def piano(midi,duration=2.4):
 t=np.arange(round(duration*SR))/SR;f=440*2**((midi-69)/12)
 attack=1-np.exp(-t*90)
 return attack*(np.sin(2*np.pi*f*t)*np.exp(-t*1.8)+.25*np.sin(2*np.pi*f*2*t)*np.exp(-t*3.8)+.09*np.sin(2*np.pi*f*3.003*t)*np.exp(-t*6))*0.14
chords=[[48,55,59,64],[45,52,55,60],[41,48,52,57],[43,50,55,59]]
beat=.625;bar=2.5
for i in range(12):
 notes=chords[i%4]
 for j,note in enumerate(notes):add(piano(note),i*bar+j*.025,.30,(-.35+j*.23))
 for j,note in enumerate([notes[1]+12,notes[2]+12,notes[3]+12,notes[2]+12]):add(piano(note,1.6),i*bar+j*beat,.17,.18)
melody=[(0.5,76),(1.5,79),(3,81),(4.25,79),(5.5,76),(6.75,74),(8,72),(9,74),(10.5,76),(11.5,79),(13,81),(14.5,79),(16,76),(17,74),(18.5,72),(20,76),(21,79),(23,76),(24,74),(26,72),(27.5,76),(28.2,72)]
for time,note in melody:add(piano(note,1.9),time,.16,-.12)
# Subdued indoor air, low-frequency shaping without any sampled speech.
noise=rng.normal(0,1,N);spectrum=np.fft.rfft(noise);freq=np.fft.rfftfreq(N,1/SR);spectrum/=np.sqrt(1+(freq/900)**4);air=np.fft.irfft(spectrum,n=N);air/=max(1e-8,np.std(air));add(air,0,.0018)
def bounce():
 t=np.arange(round(.22*SR))/SR;freq=115-55*(1-np.exp(-t*45));tone=np.sin(2*np.pi*np.cumsum(freq)/SR)*np.exp(-t*30);noise=rng.normal(0,1,len(t))*np.exp(-t*90);return .55*tone+.18*noise
def clap():
 t=np.arange(round(.19*SR))/SR;noise=rng.normal(0,1,len(t));return noise*(1-np.exp(-t*800))*np.exp(-t*42)*.20
events=json.loads((ROOT/'docs/audio-events.json').read_text())
for time in events['dribbles']:add(bounce(),time,.14,-.3)
for time in events['claps']:add(clap(),time,.12,.35)
for delay,gain in [(.065,.12),(.12,.06)]:
 shift=round(delay*SR);mix[shift:]+=mix[:-shift].copy()*gain
fade=np.minimum(1,np.arange(N)/(SR*.5))*np.minimum(1,(N-1-np.arange(N))/(SR*.8));mix*=fade[:,None]
peak=float(np.max(np.abs(mix)));mix*=min(1,.65/max(peak,1e-9))
dest=ROOT/'public/audio/soundtrack.wav'
with wave.open(str(dest),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
(ROOT/'outputs/checks/audio-design.json').write_text(json.dumps({'duration_seconds':30,'sample_rate':SR,'channels':2,'tempo_bpm':96,'bars':12,'music':'Original procedural electric piano cue. No copyrighted song recording, voice or sampled dialogue.','events':events,'raw_peak_before_gain':peak},ensure_ascii=False,indent=2))
print(dest)
