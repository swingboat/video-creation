"""Check actual exported AAC dialogue positions against the frozen voice WAVs.

240 Hz energy-envelope correlation checks mix timing, not lip phonemes.
Uses only the standard library and the system ffmpeg.
"""
import project_env
import array,hashlib,json,math,subprocess,sys,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
movie=ROOT/'outputs/sakuragi-haruko-30s.mp4'
decoded=ROOT/'.cache/tmp/lipsync-export-audio.wav'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(movie),'-vn','-ar','48000','-ac','2','-c:a','pcm_s16le',str(decoded)],check=True)
def read(path):
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(48000,2,2)
        a=array.array('h',f.readframes(f.getnframes()))
    if sys.byteorder!='little':a.byteswap()
    return a[::2]
def envelope(a):
    return [math.sqrt(sum(x*x for x in a[i:i+200])/200) for i in range(0,len(a)-199,200)]
actual=read(decoded);records=[]
lines=json.loads((ROOT/'docs/voiceover/dialogue.json').read_text())['lines']
for line in lines:
    voice=read(ROOT/f"public/audio/voices/{line['id']}.wav")
    nominal=line['start_frame']*2000;left=min(nominal,48000)
    y=envelope(actual[nominal-left:nominal+len(voice)+48000]);x=envelope(voice)
    mean=sum(x)/len(x);xc=[v-mean for v in x];xx=sum(v*v for v in xc)
    prefix=[0.];squares=[0.]
    for v in y:prefix.append(prefix[-1]+v);squares.append(squares[-1]+v*v)
    best=(-2.,0)
    for k in range(len(y)-len(x)+1):
        sy=prefix[k+len(x)]-prefix[k]
        yy=squares[k+len(x)]-squares[k]-sy*sy/len(x)
        score=sum(v*y[k+i] for i,v in enumerate(xc))/math.sqrt(max(1e-20,xx*yy))
        if score>best[0]:best=(score,k)
    offset=(best[1]*200-left)/48000
    records.append({'scene':line['id'],'expected_start_frame':line['start_frame'],'offset_seconds':round(offset,6),'offset_frames_at_24fps':round(offset*24,4),'energy_envelope_correlation':round(best[0],6)})
    assert abs(offset)<=1/24+1e-6 and best[0]>.85,records[-1]
report={'status':'passed','scope':'Actual AAC mix timing, within one 24fps frame. Energy-envelope correlation is not a phoneme or perceptual lip-sync score.','movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'lines':records}
(ROOT/'outputs/checks/lipsync/export-dialogue-timing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
