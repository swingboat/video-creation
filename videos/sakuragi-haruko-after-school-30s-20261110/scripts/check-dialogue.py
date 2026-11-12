"""Transcribe the actual spoken WAVs; content verification does not certify actor resemblance."""
import project_env
from pathlib import Path
import json,re,os,time,argparse,subprocess
import mlx.core as mx
from mlx_audio.stt import load
ROOT=Path(__file__).resolve().parents[1];os.environ['HF_HUB_OFFLINE']='1'
p=argparse.ArgumentParser();p.add_argument('--mix-only',action='store_true');a=p.parse_args()
info=json.loads((ROOT/'docs/voiceover/asr-model-info.json').read_text());assert info['verified_file_sizes']
mx.set_memory_limit(6*1024**3);mx.set_cache_limit(128*1024**2)
model=load(str(ROOT/info['local']));script=json.loads((ROOT/'docs/voiceover/dialogue.json').read_text());rows=[]
for line in script['lines']:
 if a.mix_only:break
 path=ROOT/'public/audio/voices'/f"{line['id']}.wav";start=time.monotonic()
 result=model.generate(str(path),language='Chinese',max_tokens=128)
 text=result.text;row={'id':line['id'],'expected':line['text'],'transcribed':text,'seconds':time.monotonic()-start};rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True);mx.clear_cache()
if not a.mix_only:(ROOT/'outputs/checks/voiceover/asr-transcripts.json').write_text(json.dumps({'model':info['repo'],'revision':info['revision'],'lines':rows,'scope':'Automated transcript check only, not a perceptual or original-cast resemblance judgment.'},ensure_ascii=False,indent=2))
mix=ROOT/'outputs/checks/voiceover/final-mix.wav'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'outputs/sakuragi-haruko-30s-voiced.mp4'),'-vn','-ar','16000','-ac','1',str(mix)],check=True,timeout=30)
result=model.generate(str(mix),language='Chinese',max_tokens=256)
report={'model':info['repo'],'revision':info['revision'],'transcribed':result.text,'scope':'Actual AAC mix transcribed after muxing; no text prompt or hotword hints supplied.'}
(ROOT/'outputs/checks/voiceover/final-mix-transcript.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True)
