"""Trim selected continuous source frames at 1x speed; never pad motion."""
import argparse,json,os,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES={'dribble':('dribble-native24-natural4.mp4',1.5,.5),'defender':('defender-native24-natural3.mp4',2.5),'close':('close-native24.mp4',2),'shot':('shot-short-v2.mp4',2),'rim':('rim-native24.mp4',2),'celebrate':('celebrate-native24.mp4',2),'crowd':('crowd-native24-natural4.mp4',4),'hero':('hero-native24-natural4.mp4',4)}
p=argparse.ArgumentParser();p.add_argument('scene',choices=list(SOURCES));args=p.parse_args();name=args.scene
choice=SOURCES[name];source_name,seconds=choice[:2];start=choice[2] if len(choice)>2 else 0;source=ROOT/'public/video'/source_name
ffmpeg=shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg';ffprobe=shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'
env={**os.environ,'TMPDIR':str(ROOT/'.cache/tmp'),'TMP':str(ROOT/'.cache/tmp'),'TEMP':str(ROOT/'.cache/tmp')}
meta=json.loads(subprocess.check_output([ffprobe,'-v','error','-show_streams','-of','json',str(source)],text=True,env=env));v=next(s for s in meta['streams'] if s['codec_type']=='video')
assert float(v['duration'])>=start+seconds and v['avg_frame_rate']=='24/1','Insufficient native frames; generate more footage.'
frames=round(seconds*24);video=ROOT/'.cache/tmp'/f'{name}-native-video.mp4';audio=ROOT/'.cache/tmp'/f'{name}-native-audio.wav';out=ROOT/'public/video'/f'{name}.mp4'
def run(args):subprocess.run([ffmpeg,'-v','error','-nostdin','-y',*args],env=env,cwd=ROOT,check=True,timeout=60)
portrait_crop='crop=864:486:0:0,' if name=='defender' else ''
run(['-filter_threads','1','-threads','2','-i',str(source),'-an','-vf',f'trim=start={start}:duration={seconds},setpts=PTS-STARTPTS,fps=24,{portrait_crop}scale=1024:576:force_original_aspect_ratio=increase:flags=lanczos,crop=1024:576','-frames:v',str(frames),'-c:v','libx264','-threads','2','-crf','17','-preset','medium','-pix_fmt','yuv420p',str(video)])
run(['-i',str(source),'-vn','-af',f'atrim=start={start}:duration={seconds},asetpts=PTS-STARTPTS','-t',str(seconds),'-c:a','pcm_s16le',str(audio)])
run(['-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-af','apad','-t',str(seconds),'-movflags','+faststart',str(out)])
status=ROOT/'src/media-status.ts';status.write_text(re.sub(r'\b'+name+r':false',name+':true',status.read_text()))
record={'scene':name,'source':str(source.relative_to(ROOT)),'output':str(out.relative_to(ROOT)),'frames':frames,'fps':24,'duration':seconds,'source_seconds_used':seconds,'source_start_seconds':start,'crop_source_rect':[0,0,864,486] if name=='defender' else None,'playback_speed':1.0,'motion_interpolation':False,'method':'Native source frames trimmed at 1x; no slow motion, frame repetition, optical flow or freeze padding.'}
(ROOT/'outputs/checks'/f'generation-{name}.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
