"""Verify frozen conditioning WAVs match the actual six authored voice timings.

This checks media provenance and timing, not perceptual or phoneme accuracy.
"""
import project_env
import hashlib,json,re,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'docs/lipsync/input-layout.json').read_text())
reviews=json.loads((ROOT/'outputs/checks/lipsync/visual-decisions.json').read_text())
takes=json.loads((ROOT/'docs/lipsync/selected-takes.json').read_text())
def read(path):
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(48000,2,2),str(path)
        return f.readframes(f.getnframes())
records=[]
for scene,spec in layout.items():
    key=f'{scene}-{takes[scene]}';assert reviews[key]['decision']=='selected',scene
    generation=json.loads((ROOT/f'outputs/checks/lipsync/{key}-generation.json').read_text())
    voice=read(ROOT/f'public/audio/voices/{scene}.wav')
    padded=read(ROOT/generation['audio'])
    # 48 kHz / 24 fps = 2000 stereo samples per frame, four PCM bytes each.
    offset=spec['audio_start_frame']*2000*4
    assert len(padded)==spec['frames']*2000*4,scene
    assert padded[:offset]==bytes(offset),scene
    assert padded[offset:offset+len(voice)]==voice,scene
    assert padded[offset+len(voice):]==bytes(len(padded)-offset-len(voice)),scene
    component=(ROOT/f'src/{scene.capitalize()}.tsx').read_text()
    assert int(re.search(r'from=\{(\d+)\}',component).group(1))==spec['audio_start_frame'],scene
    for file,sha in generation['inputs_sha256'].items():
        path=ROOT/file;assert path.resolve().is_relative_to(ROOT)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==sha,file
    records.append({'scene':scene,'conditioning_matches_voice':True,'audio_start_frame':spec['audio_start_frame'],'frames':spec['frames'],'visual_review':key})
assert len(records)==6
result={'status':'passed','scope':'Conditioning provenance and exact frame/sample offsets only. Visual decisions and limitations are recorded separately.','clips':records}
(ROOT/'outputs/checks/lipsync/timing-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
