"""Original 20 s synthesized court Foley, arena ambience and restrained musical pulse."""
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile
SR=48000;D=20;n=SR*D;t=np.arange(n)/SR;rng=np.random.default_rng(11)
a=np.zeros((n,2))
def noise(low,high,size=n):return signal.sosfilt(signal.butter(3,[low,high],btype='bandpass',fs=SR,output='sos'),rng.normal(size=size))
def add(x,when,gain=1,pan=0):
 start=int(when*SR);count=min(len(x),n-start)
 if count>0:a[start:start+count,0]+=x[:count]*gain*(1-pan*.4);a[start:start+count,1]+=x[:count]*gain*(1+pan*.4)
# Air and diffuse crowd, with a narrow hush during flight.
bed=noise(180,2600);env=.020+.012*np.sin(t*.7)**2;env*=1-.66*np.clip((t-8.8)/.7,0,1)*(1-np.clip((t-13.6)/.25,0,1))
a[:,0]+=bed*env;a[:,1]+=(.8*np.roll(bed,757)+.2*noise(400,4400))*env
# Court dribbles match minima of |cos(pi*1.25*t)|.
for when in np.arange(.4,5.15,.8):
 u=np.arange(int(.32*SR))/SR
 hit=np.sin(2*np.pi*(76*u-25*u*u))*np.exp(-u*24)+noise(400,1600,len(u))*.16*np.exp(-u*70)
 add(hit,when,.28,-.25)
for when in [.18,.69,1.12,1.62,2.1,2.55,3.02,3.46,4.0,4.48,5.16,5.63,6.1,7.65,10.42]:
 u=np.arange(int(.16*SR))/SR
 squeak=np.sin(2*np.pi*(1400*u+230*u*u))*np.sin(np.pi*np.minimum(1,u/.16))**2*np.exp(-u*13)
 add(squeak,when,.055,.15);add(noise(70,350,len(u))*np.exp(-u*44),when,.18)
# Low pulse, original synthetic score, fades under the shot.
for when in np.arange(0,8.2,.75):
 u=np.arange(int(.45*SR))/SR;add(np.sin(2*np.pi*(48*u-12*u*u))*np.exp(-u*13),when,.10)
# Breathy release/flight and heartbeat suspense.
u=np.arange(int(.35*SR))/SR;add(noise(1000,9000,len(u))*np.sin(np.pi*u/.35)**2,8.91,.065)
for when in [9.9,11.3,12.4]:
 u=np.arange(int(.4*SR))/SR;add(np.sin(2*np.pi*44*u)*np.exp(-u*17),when,.11)
# Buzzer after release, before score; controlled relative to net swish.
u=np.arange(int(.42*SR))/SR;buzz=signal.sawtooth(2*np.pi*380*u)*.45+np.sin(2*np.pi*760*u)*.2;add(buzz*np.minimum(1,u/.02)*np.minimum(1,(.42-u)/.08),9.15,.12)
u=np.arange(int(.6*SR))/SR;add(noise(2200,12500,len(u))*np.exp(-u*9)*np.minimum(1,u/.025),13.60,.28)
# Cheering is an original synthetic broad crowd with vowel-like resonances.
u=np.arange(int(6.25*SR))/SR;raw=rng.normal(size=len(u));cheer=np.zeros_like(u)
for fq in [420,670,970,1500]:cheer+=signal.lfilter(*signal.iirpeak(fq,3,fs=SR),raw)
cheer*=np.minimum(1,u/.35)*(.8+.2*np.sin(u*5)**2);add(cheer,13.7,.50,-.25);add(np.roll(cheer,1703),13.7,.40,.3)
# Scattered applause transients.
for when in rng.uniform(14,19.8,65):
 u=np.arange(int(.08*SR))/SR;add(noise(700,11000,len(u))*np.exp(-u*65),when,.08,rng.uniform(-1,1))
# Bright concluding chord, made from simple sine partials.
u=np.arange(int(5.9*SR))/SR
for fq in [146.83,220,293.66,369.99,440]:
 x=(np.sin(2*np.pi*fq*u)+.2*np.sin(4*np.pi*fq*u))*np.exp(-u*.5)*np.minimum(1,u/.04);add(x,14.05,.028)
# Reverb taps inside the 20-second output.
for delay,gain in [(.073,.12),(.149,.07),(.287,.04)]:
 ds=int(delay*SR);a[ds:]+=a[:-ds]*gain
fade=np.minimum(1,t/.06)*np.minimum(1,(20-t)/.45);a*=fade[:,None]
a=np.tanh(a*1.3);a*=.88/max(.88,np.max(np.abs(a)))
root=Path(__file__).resolve().parents[1];wavfile.write(root/'public/court-soundscape.wav',SR,(a*32767).astype(np.int16))
print('AUDIO',a.shape,'peak',np.max(np.abs(a)))
