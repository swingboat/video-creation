"""Select reviewed contiguous native frames, without retiming, frame looping or interpolation."""
import project_env
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scene',nargs='?');a=p.parse_args()
decisions=json.loads((ROOT/'docs/edit-decisions.json').read_text())
record=ROOT/'outputs/checks/selections.json';selected=json.loads(record.read_text()) if record.exists() else {}
for scene,spec in decisions.items():
 if a.scene and scene!=a.scene:continue
 if spec['review_status']!='approved':
  if a.scene:raise SystemExit(f'{scene} has not passed visual review')
  continue
 source=ROOT/'public/video'/spec['source'];target=ROOT/'public/video'/f'{scene}.mp4'
 assert source.resolve().is_relative_to(ROOT) and not source.is_symlink(),str(source)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(source)]))
 video=next(s for s in info['streams'] if s['codec_type']=='video')
 assert video['avg_frame_rate']=='24/1' and int(video['nb_frames'])>=spec['start_frame']+spec['frames']
 filters=[]
 if spec.get('crop'):filters.append('crop='+':'.join(map(str,spec['crop'])))
 filters.extend(['scale=1280:720:flags=lanczos','setsar=1'])
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(spec['start_frame']/24),'-i',str(source),'-map','0:v:0','-an','-frames:v',str(spec['frames']),'-vf',','.join(filters),'-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-fps_mode','passthrough','-movflags','+faststart',str(target)],check=True,timeout=90)
 selected[scene]={**spec,'playback_speed':1,'source_seconds_used':spec['frames']/24,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'output':str(target.relative_to(ROOT)),'audio':'Muted. Original synthesized score and synchronized effects are authored separately.'}
 record.write_text(json.dumps(selected,ensure_ascii=False,indent=2))
 print('SELECTED',scene,spec['frames'],'native frames')
ready={name:(ROOT/'public/video'/f'{name}.mp4').exists() and name in selected for name in decisions}
(ROOT/'src/media-status.ts').write_text('export const ready='+json.dumps(ready,separators=(',',':'))+';\n')
