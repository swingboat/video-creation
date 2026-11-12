"""Optional character voice design; source text/config is project-local JSON."""
import project_env
import argparse,json,time,wave
from project_ops import ROOT,local,require,sha,emit
from gpu_lock import gpu_task

def main():
    p=argparse.ArgumentParser();p.add_argument('--script',default='docs/dialogue.json');p.add_argument('--take',required=True);a=p.parse_args()
    import re
    require(re.fullmatch(r'[a-zA-Z0-9-]+',a.take),'Use a safe take identifier')
    data=json.loads(local(a.script).read_text());profile=json.loads((ROOT/'docs/mlx-profile.json').read_text())
    info=next(m for m in profile['models'] if m['role']=='voice');model_path=local(info['local'])
    require(model_path.exists(),'Fetch the optional voice model first')
    import os
    os.environ['HF_HUB_OFFLINE']='1'
    with gpu_task('voice'):
        import numpy as np
        import mlx.core as mx
        from mlx_audio.tts.utils import load_model
        mx.set_memory_limit(8*1024**3);mx.set_cache_limit(256*1024**2)
        model=load_model(str(model_path))
        for line in data['lines']:
            require(re.fullmatch(r'[a-zA-Z0-9-]+',line['id']),'Use a safe line ID')
            character=data['characters'][line['character']]
            target=ROOT/f'public/audio/voices/{line["id"]}-{a.take}-raw.wav';require(not target.exists(),'Preserving old voice take')
            seed=character['seed'];mx.random.seed(seed);start=time.monotonic()
            instruction=character['description']+'\nDelivery: '+line['emotion']+'\nSpeak only the supplied text.'
            values=list(model.generate_voice_design(text=line['text'],instruct=instruction,language=data['language'],temperature=.7,top_p=.95,top_k=50,repetition_penalty=1.05,max_tokens=140,verbose=True))
            require(bool(values),'Voice model returned no audio')
            audio=mx.concatenate([v.audio for v in values],axis=0);mx.eval(audio);audio=np.asarray(audio,dtype=np.float32).reshape(-1)
            rate=values[0].sample_rate;peak=float(np.max(np.abs(audio)));require(len(audio)>rate*.1 and peak>.001,'Empty/quiet speech')
            audio*=min(1,.98/max(peak,1e-9))
            with wave.open(str(target),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes((np.clip(audio,-1,1)*32767).astype('<i2').tobytes())
            emit(ROOT/f'docs/generation/{line["id"]}-{a.take}-voice.json',{**line,'characterDescription':character['description'],'language':data['language'],'model':info['repo'],'revision':info['revision'],'seed':seed,'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'sampleRate':rate,'seconds':len(audio)/rate,'wallSeconds':round(time.monotonic()-start,2)})
            mx.clear_cache()

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,FileNotFoundError) as e:raise SystemExit(str(e))
