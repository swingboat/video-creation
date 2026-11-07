"""Deterministic stereo ocean, wind, rain and delayed rolling thunder (NumPy/SciPy)."""
from pathlib import Path
import json
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
SR=48000
timeline=json.loads((ROOT/'docs/timeline.json').read_text())
DURATION=timeline['duration']
rng=np.random.default_rng(20261106)
t=np.arange(SR*DURATION)/SR
storm=.18+.82*np.sin(np.pi*t/DURATION)**.8

def filtered_noise(low=None,high=None):
    x=rng.standard_normal(t.size)
    if low and high:
        sos=signal.butter(3,[low,high],fs=SR,btype='bandpass',output='sos')
    else:
        sos=signal.butter(3,low or high,fs=SR,btype='highpass' if low else 'lowpass',output='sos')
    y=signal.sosfilt(sos,x)
    return y/max(np.std(y),1e-8)

ocean=filtered_noise(45,430)*(.052+.022*np.sin(2*np.pi*.34*t)+.008*np.sin(2*np.pi*.83*t))
wind=filtered_noise(240,1800)*(.013+.026*storm)*(1+.25*np.sin(2*np.pi*.21*t))
rain=filtered_noise(2100,12500)*(.010+.026*storm)
bed=ocean+wind+rain
left=bed.copy();right=.87*np.roll(bed,47)+.13*filtered_noise(800,5500)*.025*storm
for i,event in enumerate(timeline['lightning_seconds']):
    tau=t-(event+timeline['thunder_delay_seconds'])
    active=np.maximum(tau,0)
    envelope=(1-np.exp(-active*90))*np.exp(-active/1.1)*(tau>=0)
    rumble=filtered_noise(28,230)
    rolling=.55+.25*np.sin(2*np.pi*3.2*active+i)+.2*np.sin(2*np.pi*7.1*active+i*.4)
    body=rumble*envelope*rolling*.22
    crack=filtered_noise(900,6500)*np.exp(-active/.035)*(tau>=0)*.12
    echo1=np.roll(body,int(.12*SR))*.3
    echo2=np.roll(body,int(.29*SR))*.2
    thunder=(body+crack+echo1+echo2)*.72
    pan=(-.45 if i%2 else .4)
    left+=thunder*(.85-pan*.25)
    right+=np.roll(thunder,90)*( .85+pan*.25)
if timeline.get('version')=='bunny-artist':
    # Quiet miniature foley follows the baked foot contacts, block landing and pencil.
    motion=json.loads((ROOT/'outputs/checks/bunny/motion-audit.json').read_text())
    contacts=motion['foot_contacts']
    taps=np.zeros_like(t)
    grain=filtered_noise(400,4200)
    for event in contacts:
        tau=t-event;u=np.maximum(tau,0)
        taps+=(np.sin(math.tau*185*u)*.020+grain*.009)*np.exp(-u/.022)*(tau>=0)
    u=np.maximum(t-14.15,0);taps+=(.045*np.sin(math.tau*125*u)+.018*grain)*np.exp(-u/.045)*(t>=14.15)
    scratch=filtered_noise(1700,7500)*.013*((t>=16.85)&(t<=19.75))*(.65+.35*np.sin(t*31)**2)
    focus=1-.50*np.clip((t-14.5)/2,0,1)
    left=left*focus+taps+scratch;right=right*focus+np.roll(taps,35)+scratch*.8
fade=np.minimum(1,t/.12)*np.minimum(1,(DURATION-t)/.32)
audio=np.stack([left,right],axis=1)*fade[:,None]
audio=np.tanh(audio*1.15)
audio*=.86/max(np.max(np.abs(audio)),1e-8)
wavfile.write(ROOT/'public/storm-soundscape.wav',SR,(audio*32767).astype(np.int16))
report={'sample_rate':SR,'channels':2,'duration':DURATION,'peak':float(np.max(np.abs(audio))),'rms':float(np.sqrt(np.mean(audio**2))),'source':'Locally synthesized. No external audio or music.','thunder_delay_seconds':.09}
(ROOT/'outputs/checks/audio.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
