"""Extract evenly spaced source frames for actual anatomy/continuity review."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('scene');args=parser.parse_args()
source=ROOT/'public/video'/f'{args.scene}.mp4';out=ROOT/'outputs/checks/clip-frames'/args.scene;out.mkdir(parents=True,exist_ok=True)
env={**os.environ,'TMPDIR':str(ROOT/'.cache/tmp'),'TMP':str(ROOT/'.cache/tmp'),'TEMP':str(ROOT/'.cache/tmp')}
def binary(n):return shutil.which(n) or str(Path('/opt/homebrew/bin')/n)
meta=json.loads(subprocess.check_output([binary('ffprobe'),'-v','error','-show_streams','-of','json',str(source)],text=True,env=env))
v=next(s for s in meta['streams'] if s['codec_type']=='video');count=int(v['nb_frames']);positions=sorted(set(round((count-1)*i/8) for i in range(9)))
select='+'.join(f'eq(n\\,{i})' for i in positions)
subprocess.run([binary('ffmpeg'),'-v','error','-y','-i',str(source),'-vf','select='+select,'-fps_mode','vfr',str(out/'frame-%03d.png')],check=True,env=env)
(out/'source-frames.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'positions':positions,'fps':v['avg_frame_rate'],'width':v['width'],'height':v['height']},indent=2));print(json.dumps({'scene':args.scene,'source_positions':positions,'output':str(out.relative_to(ROOT))}))
