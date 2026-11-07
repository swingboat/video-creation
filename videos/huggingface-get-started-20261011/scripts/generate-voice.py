"""Generate aligned Chinese narration. Run inside this video directory.
Dependencies: edge-tts==7.2.8, system ffmpeg/ffprobe.
One utterance per file makes caption timing measurable rather than estimated.
"""
import asyncio
import json
import math
import os
from pathlib import Path
import subprocess
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
for key in ('TMPDIR', 'TMP', 'TEMP'):
    os.environ[key] = str(ROOT / '.cache/tmp')
RAW = ROOT / '.cache/tts'
RAW.mkdir(parents=True, exist_ok=True)
OUT = ROOT / 'public/voiceover'
OUT.mkdir(parents=True, exist_ok=True)
scenes = json.loads((ROOT / 'docs/narration.json').read_text())
sem = asyncio.Semaphore(3)

def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)]))

async def utterance(scene, index, text):
    path = RAW / f'{scene}-{index:02d}.mp3'
    fingerprint = RAW / f'{scene}-{index:02d}.text'
    if not path.exists() or path.stat().st_size < 1000 or not fingerprint.exists() or fingerprint.read_text()!=text:
        async with sem:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(text, 'zh-CN-XiaoxiaoNeural', rate='+8%', pitch='-2Hz').save(str(path))
                    fingerprint.write_text(text)
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1 + attempt)
    wav = RAW / f'{scene}-{index:02d}.wav'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(path),'-ar','48000','-ac','1',str(wav)],check=True)
    print(f'{scene}/{index} {duration(wav):.2f}s',flush=True)
    return wav

async def main():
    await asyncio.gather(*(utterance(s['id'],i,text) for s in scenes for i,text in enumerate(s['lines'])))
    silence = RAW / 'silence.wav'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','0.35',str(silence)],check=True)
    manifest = []
    global_captions = []
    total_frames = 0
    for scene in scenes:
        elapsed = 0.6
        captions = []
        utterances = []
        concat = []
        for i,text in enumerate(scene['lines']):
            wav = RAW / f'{scene["id"]}-{i:02d}.wav'
            length = duration(wav)
            utterances.append({'text':text,'startMs':round(elapsed*1000),'endMs':round((elapsed+length)*1000)})
            # Split long subtitles at semantic punctuation, aligned within this exact utterance.
            import re
            pieces = [p for p in re.split(r'(?<=[，；：。！？])', text) if p]
            chunks=[]
            for p in pieces:
                if chunks and len(chunks[-1]+p) <= 30:
                    chunks[-1]+=p
                else:
                    chunks.append(p)
            weights=[max(1,len(p)) for p in chunks]
            cstart=elapsed
            for p,weight in zip(chunks,weights):
                clen=length*weight/sum(weights)
                cap={'text':p,'startMs':round(cstart*1000),'endMs':round((cstart+clen)*1000),'timestampMs':None,'confidence':None,'pageBreakAfter':True}
                captions.append(cap)
                global_captions.append({**cap,'startMs':cap['startMs']+round(total_frames/30*1000),'endMs':cap['endMs']+round(total_frames/30*1000)})
                cstart+=clen
            concat += [f"file '{wav}'",f"file '{silence}'"]
            elapsed += length+0.35
        listing=RAW/f'{scene["id"]}-concat.txt'
        listing.write_text('\n'.join(concat))
        scene_frames=math.ceil((elapsed+0.65)*30)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-af','adelay=600,apad','-t',str(scene_frames/30),'-c:a','libmp3lame','-b:a','160k',str(OUT/f'{scene["id"]}.mp3')],check=True)
        manifest.append({'id':scene['id'],'title':scene['title'],'startFrame':total_frames,'durationInFrames':scene_frames,'utterances':utterances,'captions':captions})
        total_frames+=scene_frames
    (ROOT/'src/timeline.json').write_text(json.dumps({'fps':30,'durationInFrames':total_frames,'scenes':manifest},ensure_ascii=False,indent=2))
    (ROOT/'docs/captions.json').write_text(json.dumps(global_captions,ensure_ascii=False,indent=2))
    def stamp(ms):
        seconds,milli=divmod(ms,1000); mins,sec=divmod(seconds,60); hours,mins=divmod(mins,60)
        return f'{hours:02d}:{mins:02d}:{sec:02d},{milli:03d}'
    (ROOT/'outputs/huggingface-zh.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["startMs"])} --> {stamp(c["endMs"])}\n{c["text"]}' for i,c in enumerate(global_captions)))
    print(f'TOTAL {total_frames} frames, {total_frames/30:.2f}s',flush=True)

asyncio.run(main())
