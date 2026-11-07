"""Project-local macOS TTS; --reuse-audio measures replacement sentence WAVs."""
import argparse, array, hashlib, json, math, pathlib, subprocess, wave

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIO = ROOT / 'public/unet/audio'
OUT = ROOT / 'outputs'
RATE = 48000
FPS = 30
TARGET = [15, 20, 25, 25, 30, 25, 10]

def read_wav(path):
    with wave.open(str(path)) as w:
        if (w.getframerate(), w.getnchannels(), w.getsampwidth()) != (RATE, 1, 2):
            raise ValueError(f'{path}: 需要48kHz、单声道、16bit PCM WAV')
        return array.array('h', w.readframes(w.getnframes()))

def write_wav(path, samples):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(samples.tobytes())

def trim(samples):
    block = 480
    active = [i for i in range(0, len(samples), block) if math.sqrt(sum(v*v for v in samples[i:i+block]) / max(1, len(samples[i:i+block]))) > 80]
    if not active: raise ValueError('旁白音频没有可检测的声音')
    x = samples[max(0, active[0] - 3840): min(len(samples), active[-1] + block + 4800)]
    peak = max(abs(v) for v in x)
    gain = min(1.6, 0.78 * 32767 / peak)
    return array.array('h', (round(v * gain) for v in x))

def wrap_caption(text):
    if len(text) <= 27: return text
    cut = text.find('，', max(8, len(text)//2-8), min(len(text)-7, len(text)//2+9))
    cut = cut+1 if cut >= 0 else len(text)//2
    return text[:cut] + '\n' + text[cut:]

def stamp(ms):
    n = round(ms); hours, n = divmod(n, 3600000); minutes, n = divmod(n, 60000); sec, n = divmod(n, 1000)
    return f'{hours:02}:{minutes:02}:{sec:02},{n:03}'

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--reuse-audio', action='store_true'); ap.add_argument('--voice', default='Tingting'); ap.add_argument('--rate', type=int, default=175)
    args = ap.parse_args(); AUDIO.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True); (OUT/'checks').mkdir(parents=True, exist_ok=True)
    lines = json.loads((ROOT/'public/unet/narration.json').read_text())
    spoken = []; records = []
    for i, line in enumerate(lines):
        tts = line.get('tts', line['text'].replace('U-Net', 'U net').replace('字母 U', '字母 U'))
        spoken.append(f'{i+1:02d}. {tts}')
        base = AUDIO / f'sentence-{i+1:02d}'
        signature = hashlib.sha256(f'{args.voice}|{args.rate}|{tts}'.encode()).hexdigest()
        key = base.with_suffix('.sha256')
        if not args.reuse_audio and (not base.with_suffix('.wav').exists() or not key.exists() or key.read_text() != signature):
            base.with_suffix('.txt').write_text(tts)
            subprocess.run(['say','-v',args.voice,'-r',str(args.rate),'-f',str(base.with_suffix('.txt')),'-o',str(base.with_suffix('.aiff'))],check=True)
            subprocess.run(['afconvert',str(base.with_suffix('.aiff')),str(base.with_suffix('.wav')),'-f','WAVE','-d','LEI16@48000'],check=True)
            write_wav(base.with_suffix('.wav'), trim(read_wav(base.with_suffix('.wav'))))
            key.write_text(signature)
        data = read_wav(base.with_suffix('.wav'))
        records.append({'scene':line['scene'], 'text':wrap_caption(line['text']), 'samples':data, 'file':str(base.with_suffix('.wav').relative_to(ROOT/'public'))})
        print(f'句子 {i+1:02d}/{len(lines)}：{len(data)/RATE:.2f}s',flush=True)
    timeline = {'fps':FPS,'audioAvailable':True,'voice':args.voice,'speechRate':args.rate,'scenes':[],'durationFrames':0}
    global_frames=0; srt=[]; audio_all=array.array('h'); waveform=[]
    for scene in range(7):
        entries=[r for r in records if r['scene']==scene]
        lengths=[math.ceil(len(r['samples'])/RATE*FPS) for r in entries]
        minimum=18+sum(lengths)+8*len(entries)+25
        duration=max(round(TARGET[scene]*FPS),minimum)
        extra=duration-minimum
        pauses=[8+extra//len(entries)+(1 if i<extra%len(entries) else 0) for i in range(len(entries))]
        data=array.array('h',[0]) * (duration*RATE//FPS)
        cursor=18; captions=[]
        for j,(r,length) in enumerate(zip(entries,lengths)):
            sample_start=cursor*RATE//FPS
            data[sample_start:sample_start+len(r['samples'])]=r['samples']
            start=cursor/FPS*1000; end=start+len(r['samples'])/RATE*1000
            cap={'text':r['text'],'startMs':round(start,3),'endMs':round(end,3),'timestampMs':None,'confidence':None}
            captions.append(cap)
            srt.append(f'{len(srt)+1}\n{stamp(global_frames/FPS*1000+start)} --> {stamp(global_frames/FPS*1000+end)}\n{r["text"]}\n')
            waveform.append({'sentenceFile':r['file'],'scene':scene,'startMs':round(global_frames/FPS*1000+start,3),'durationMs':round(len(r['samples'])/RATE*1000,3),
                'peak':round(max(abs(x) for x in r['samples'])/32768,4)})
            cursor+=length+pauses[j]
        src=f'unet/audio/scene-{scene+1}.wav'
        write_wav(ROOT/'public'/src,data); audio_all.extend(data)
        timeline['scenes'].append({'startFrame':global_frames,'durationFrames':duration,'audioSrc':src,'captions':captions})
        global_frames+=duration
    timeline['durationFrames']=global_frames
    (OUT/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'src/unet/timeline.generated.ts').write_text("// Generated by scripts/prepare-unet-audio.py; do not edit by hand.\nimport type {UnetTimeline} from './types';\nexport const timeline: UnetTimeline = "+json.dumps(timeline,ensure_ascii=False,indent=2)+';\n')
    (OUT/'unet-explainer.srt').write_text('\n'.join(srt))
    (OUT/'tts-narration.txt').write_text('\n'.join(spoken)+'\n')
    (OUT/'narration.txt').write_text('\n\n'.join('镜头 '+str(s+1)+'\n'+''.join(i['text'] for i in lines if i['scene']==s) for s in range(7))+'\n')
    write_wav(OUT/'narration.wav',audio_all)
    (OUT/'checks/audio-check.json').write_text(json.dumps({'voice':args.voice,'rate':args.rate,'sampleRate':RATE,'channels':1,'durationSeconds':global_frames/FPS,'sentences':waveform,
      'alignment':'逐句生成音频，按实际采样长度安排每句字幕；不做词级对齐','ttsPronunciation':'U-Net 在独立 TTS 文稿中写为 U net；屏幕与字幕保留 U-Net'},ensure_ascii=False,indent=2))
    print(f'配音与时间轴完成：{global_frames/FPS:.3f}s / {global_frames} 帧',flush=True)

if __name__=='__main__': main()
