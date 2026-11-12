"""Generate versioned character dialogue locally with a pinned Qwen3 voice-design model."""
import project_env
from pathlib import Path
import argparse,json,time,wave,hashlib,os
import numpy as np
import mlx.core as mx
from mlx_audio.tts.utils import load_model
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
os.environ['HF_HUB_OFFLINE']='1'
p=argparse.ArgumentParser();p.add_argument('--lines',nargs='*');p.add_argument('--take',default='v1');p.add_argument('--seed-offset',type=int,default=0);a=p.parse_args()
script=json.loads((ROOT/'docs/voiceover/dialogue.json').read_text());info=json.loads((ROOT/'docs/voiceover/model-info.json').read_text())
assert info.get('verified_file_sizes'),'Finish the pinned model download first'
mx.set_memory_limit(8*1024**3);mx.set_cache_limit(256*1024**2)
model=load_model(str(ROOT/info['local']))
output=ROOT/'public/audio/voices/raw';output.mkdir(parents=True,exist_ok=True)
for line in script['lines']:
 if a.lines and line['id'] not in a.lines:continue
 target=output/f"{line['id']}-{a.take}.wav"
 if target.exists():print('Preserving existing candidate',target.name,flush=True);continue
 profile=script['characters'][line['character']];seed=profile['seed']+a.seed_offset
 instruct=profile['voice_description']+' 本句表演：'+line['emotion']+' 自然说出文字，不朗读表演说明。'
 mx.random.seed(seed);start=time.monotonic();print('SYNTHESIZING',line['id'],line['text'],flush=True)
 results=list(model.generate_voice_design(text=line['text'],instruct=instruct,language='Chinese',temperature=.7,top_p=.95,top_k=50,repetition_penalty=1.05,max_tokens=140,verbose=True))
 assert results,'No speech generated'
 values=mx.concatenate([r.audio for r in results],axis=0);mx.eval(values);audio=np.asarray(values,dtype=np.float32).reshape(-1);rate=results[0].sample_rate
 peak=float(np.max(np.abs(audio)));assert len(audio)>rate*.35 and peak>.001
 audio*=min(1,.98/max(peak,1e-9))
 with wave.open(str(target),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes((np.clip(audio,-1,1)*32767).astype('<i2').tobytes())
 record={**line,'take':a.take,'seed':seed,'instruct':instruct,'model_repo':info['repo'],'model_revision':info['revision'],'mlx_audio_version':'0.6.5','sample_rate':rate,'samples':len(audio),'raw_seconds':len(audio)/rate,'wall_seconds':round(time.monotonic()-start,3),'mlx_peak_gib':mx.get_peak_memory()/1024**3,'file':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 (ROOT/'outputs/checks/voiceover'/f"generation-{line['id']}-{a.take}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2))
 print('GENERATED',line['id'],record['raw_seconds'],'seconds',flush=True);mx.clear_cache()
