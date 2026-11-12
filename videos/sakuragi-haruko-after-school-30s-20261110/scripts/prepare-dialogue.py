"""Trim only silence, fit each dialogue window and mix dialogue with a ducked score."""
import project_env
from pathlib import Path
import json,wave,subprocess,math,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];SR=48000;N=30*SR
script=json.loads((ROOT/'docs/voiceover/dialogue.json').read_text());takes=json.loads((ROOT/'docs/voiceover/selected-takes.json').read_text())
def read(path):
 with wave.open(str(path),'rb') as f:
  assert f.getsampwidth()==2
  rate=f.getframerate();channels=f.getnchannels();data=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float64)/32768
 return data.reshape(-1,channels),rate
def write(path,values,rate):
 values=np.asarray(values);channels=1 if values.ndim==1 else values.shape[1]
 with wave.open(str(path),'wb') as f:f.setnchannels(channels);f.setsampwidth(2);f.setframerate(rate);f.writeframes((np.clip(values,-1,1)*32767).astype('<i2').tobytes())
bed,rate=read(ROOT/'public/audio/soundtrack.wav');assert rate==SR and len(bed)==N
dialogue=np.zeros((N,2));duck=np.ones(N);records=[]
for line in script['lines']:
 raw=ROOT/'public/audio/voices/raw'/f"{line['id']}-{takes[line['id']]}.wav";audio,rate=read(raw);raw_rate=rate;mono=audio.mean(axis=1)
 step=max(1,rate//100);rms=np.array([np.sqrt(np.mean(mono[i:i+step]**2)) for i in range(0,len(mono),step)])
 active=np.flatnonzero(rms>max(.0003,float(rms.max())*.025));assert len(active),line['id']
 begin=max(0,int(active[0]*step)-int(.065*rate));end=min(len(mono),int((active[-1]+1)*step)+int(.11*rate))
 trimmed=mono[begin:end];trimfile=ROOT/'.cache/tmp'/f"voice-{line['id']}-trim.wav";write(trimfile,trimmed,rate)
 window=(line['end_frame']-line['start_frame'])/24
 speed=max(1,len(trimmed)/rate/max(.1,window-.13));assert speed<1.28,f"{line['id']} too long; regenerate a faster take ({speed:.3f})"
 filters=[]
 if speed>1.001:filters.append(f'atempo={speed:.8f}')
 filters.extend(['highpass=f=65','loudnorm=I=-20:TP=-2:LRA=7','aresample=48000'])
 normalized=ROOT/'.cache/tmp'/f"voice-{line['id']}-normalized.wav"
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(trimfile),'-af',','.join(filters),'-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(normalized)],check=True,timeout=45)
 clean,rate=read(normalized);mono=clean[:,0]
 # A subtle, short gym reflection; the spoken signal remains foremost.
 reverbed=np.zeros(len(mono)+int(.10*SR));reverbed[:len(mono)]+=mono
 for delay,gain in [(.043,.055),(.087,.025)]:
  offset=round(delay*SR);reverbed[offset:offset+len(mono)]+=mono*gain
 pan=-.12 if line['character']=='sakuragi' else .12
 stereo=np.column_stack([reverbed*math.sqrt((1-pan)/2),reverbed*math.sqrt((1+pan)/2)])
 target=ROOT/'public/audio/voices'/f"{line['id']}.wav";write(target,stereo,SR)
 start=round(line['start_frame']*SR/24);stop=start+len(stereo);assert stop<=round(line['end_frame']*SR/24),line['id']
 dialogue[start:stop]+=stereo
 lo=max(0,start-round(.075*SR));hi=min(N,stop+round(.24*SR))
 curve=np.interp(np.arange(lo,hi),[lo,start,stop,hi-1],[1,.25,.25,1]);duck[lo:hi]=np.minimum(duck[lo:hi],curve)
 records.append({**line,'take':takes[line['id']],'raw_file':str(raw.relative_to(ROOT)),'raw_seconds':len(audio)/raw_rate,'trim_start_seconds':begin/raw_rate,'trim_end_seconds':end/raw_rate,'tempo_factor':speed,'processed_seconds':len(stereo)/SR,'processed_file':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'actual_end_frame':stop/SR*24})
background=bed*2*duck[:,None];master=background+dialogue;peak=float(np.max(np.abs(master)));assert peak<.98,f'Mix peak too high: {peak}'
write(ROOT/'public/audio/background-ducked.wav',background,SR);write(ROOT/'public/audio/dialogue-master.wav',master,SR)
(ROOT/'outputs/checks/voiceover/alignment.json').write_text(json.dumps({'duration':30,'sample_rate':SR,'channels':2,'dialogue_target_lufs':-20,'background_gain_db':6.02,'duck_gain':.25,'pre_master_peak':peak,'lines':records},ensure_ascii=False,indent=2))
print('Prepared six independent voice clips and 30-second mix')
