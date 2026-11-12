"""Apply deliberate slow-motion edits to reviewed continuous source clips."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('scene',choices=['shot','close','rim','celebrate','hero']);args=parser.parse_args();out=ROOT/'public/video'/f'{args.scene}.mp4'
if args.scene=='shot':source=ROOT/'public/video/shot-short-v2.mp4';take=2.;factor=2.;seconds=4.;frames=96
else:
 source=ROOT/'public/video'/f'{args.scene}-native24.mp4';take=2.
 if args.scene=='close':factor=1.5;seconds=3.;frames=72
 elif args.scene=='rim':factor=2.5;seconds=5.;frames=120
 else:factor=2.;seconds=4.;frames=96
ffmpeg=shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
vf=f'trim=duration={take},setpts={factor}*(PTS-STARTPTS),fps=24,scale=1024:576:force_original_aspect_ratio=increase:flags=lanczos,crop=1024:576'
tempo=1/factor;tempos=[]
while tempo<.5:tempos.append('atempo=0.5');tempo/=.5
while tempo>2:tempos.append('atempo=2');tempo/=2
tempos.append(f'atempo={tempo}')
af=f'atrim=duration={take},asetpts=PTS-STARTPTS,'+','.join(tempos)
env={**os.environ,'TMPDIR':str(ROOT/'.cache/tmp'),'TMP':str(ROOT/'.cache/tmp'),'TEMP':str(ROOT/'.cache/tmp')}
video_temp=ROOT/'.cache/tmp'/f'{args.scene}-retimed-video.mp4';audio_temp=ROOT/'.cache/tmp'/f'{args.scene}-retimed-audio.wav'
def run(cmd):subprocess.run([ffmpeg,'-v','error','-nostdin','-y',*cmd],check=True,cwd=ROOT,env=env,timeout=60)
print('Retiming video only',args.scene,flush=True)
run(['-filter_threads','1','-threads','2','-i',str(source),'-an','-vf',vf,'-frames:v',str(frames),'-t',str(seconds),'-c:v','libx264','-threads','2','-crf','17','-preset','medium','-pix_fmt','yuv420p',str(video_temp)])
print('Retiming audio only',args.scene,flush=True)
run(['-filter_threads','1','-i',str(source),'-vn','-af',af,'-t',str(seconds),'-c:a','pcm_s16le',str(audio_temp)])
print('Muxing finite streams',args.scene,flush=True)
run(['-i',str(video_temp),'-i',str(audio_temp),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-af','apad','-t',str(seconds),'-movflags','+faststart',str(out)])
status=ROOT/'src/media-status.ts';status.write_text(status.read_text().replace(args.scene+':false',args.scene+':true'))
record={'scene':args.scene,'output':str(out.relative_to(ROOT)),'native_source':str(source.relative_to(ROOT)),'source_seconds_used':take,'slow_motion_factor':factor,'frames':frames,'fps':24,'duration':seconds,'exit_code':0,'method':'Reviewed local whole-scene video; video timestamps and audio tempo retimed together, without optical-flow deformation.'}
(ROOT/'outputs/checks'/f'generation-{args.scene}.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
