"""Validate this isolated project and the actual 720-frame final export."""
import project_env
from pathlib import Path
import argparse,hashlib,json,re,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/checks';OUT.mkdir(parents=True,exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
def run(args,timeout=120):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
 return p
def probe(path):return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]).stdout)
report={'checks':{},'scope':'technical checks only; visual acceptance is recorded separately'}
try:
 result=run(['node','node_modules/typescript/bin/tsc','--noEmit']);(OUT/'typecheck.log').write_text(result.stdout+result.stderr);report['checks']['typescript']='passed'
 package=json.loads((ROOT/'package.json').read_text());lock=json.loads((ROOT/'package-lock.json').read_text());assert package['name']==lock['name']==lock['packages']['']['name']
 for key,version in {**package['dependencies'],**package['devDependencies']}.items():assert json.loads((ROOT/'node_modules'/key/'package.json').read_text())['version']==version,key
 report['checks']['locked_dependencies']='passed'
 for folder in ['src','public','scripts']:
  for file in (ROOT/folder).rglob('*'):assert not file.is_symlink() and file.resolve().is_relative_to(ROOT),str(file)
 runtime=[ROOT/name for name in ['package.json','package-lock.json','remotion.config.ts','tsconfig.json','requirements-local-video.txt','requirements-tts.txt','.npmrc']]
 runtime+=list((ROOT/'src').rglob('*.ts'))+list((ROOT/'src').rglob('*.tsx'))+[f for f in (ROOT/'scripts').glob('*.py') if f.name!='check.py']+list((ROOT/'scripts').glob('*.mjs'))
 for file in runtime:
  content=file.read_text();assert not re.search(r'/Users/|file://|videos/rukawa',content),str(file)
  if file.suffix in ['.ts','.tsx']:
   for imp in re.findall(r'(?:from\s*|import\s*)[\'"]([^\'"]+)',content):
    if imp.startswith('.'):
     ref=file.parent/imp;assert ref.resolve().is_relative_to(ROOT),imp
     assert any(p.exists() for p in [ref,ref.with_suffix('.ts'),ref.with_suffix('.tsx'),ref/'index.ts']),imp
 for line in (ROOT/'requirements-local-video.txt').read_text().splitlines():
  if line.startswith('.cache/'):assert (ROOT/line).resolve().is_relative_to(ROOT),line
 report['checks']['standalone_runtime_paths']='passed'
 if not a.source_only:
  decisions=json.loads((ROOT/'docs/edit-decisions.json').read_text());selections=json.loads((OUT/'selections.json').read_text());assert sum(d['frames'] for d in decisions.values())==720
  ready=(ROOT/'src/media-status.ts').read_text();clips=[]
  for scene,spec in decisions.items():
   assert spec['review_status']=='approved' and re.search(r'\b'+scene+r'":true',ready),scene
   selection=selections[scene];assert selection['playback_speed']==1 and selection['frames']==spec['frames']
   source=ROOT/'public/video'/spec['source'];assert source.is_file() and source.resolve().is_relative_to(ROOT)
   assert hashlib.sha256(source.read_bytes()).hexdigest()==selection['source_sha256'],scene
   file=ROOT/'public/video'/f'{scene}.mp4';meta=probe(file);video=next(s for s in meta['streams'] if s['codec_type']=='video')
   assert int(video['nb_frames'])==spec['frames'] and video['avg_frame_rate']=='24/1',scene
   assert hashlib.sha256(file.read_bytes()).hexdigest()==selection['output_sha256'],scene
   clips.append({'scene':scene,'frames':spec['frames'],'source':spec['source'],'source_start_frame':spec['start_frame']})
  report['checks']['reviewed_native_speed_selections']=clips
  voice_timing=json.loads((OUT/'voiceover/alignment.json').read_text());assert len(voice_timing['lines'])==6
  dialogue=json.loads((ROOT/'docs/voiceover/dialogue.json').read_text())
  for spec,voice in zip(dialogue['lines'],voice_timing['lines']):
   assert voice['id']==spec['id'] and voice['text']==spec['text'] and voice['tempo_factor']==1
   f=ROOT/voice['processed_file'];assert f.resolve().is_relative_to(ROOT)
   assert hashlib.sha256(f.read_bytes()).hexdigest()==voice['sha256']
   assert voice['actual_end_frame']<=spec['end_frame']
  report['checks']['six_natural_speed_dialogue_windows']='passed'
  run(['python3','scripts/check-lipsync.py'])
  report['checks']['six_audio_conditioned_clip_inputs']='passed'
  file=ROOT/'outputs/sakuragi-haruko-30s.mp4';meta=probe(file);v=next(s for s in meta['streams'] if s['codec_type']=='video');audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
  assert v['codec_name']=='h264' and v['avg_frame_rate']=='24/1' and int(v['nb_frames'])==720
  assert (v['width'],v['height'])==(1280,720) and abs(float(v['duration'])-30)<.01
  assert abs(float(meta['format']['duration'])-30)<.05 and audio['codec_name']=='aac' and abs(float(audio['duration'])-30)<.05
  decoded=run(['ffmpeg','-v','error','-i',str(file),'-f','null','-']);assert not decoded.stderr.strip(),decoded.stderr
  report['checks']['full_audio_video_decode']='passed';(OUT/'media-metadata.json').write_text(json.dumps(meta,indent=2))
  run(['python3','scripts/check-export-dialogue-timing.py'])
  report['checks']['actual_export_dialogue_timing']='passed'
  report['video']={'file':str(file.relative_to(ROOT)),'frames':720,'fps':24,'duration':30,'width':1280,'height':720,'audio':'aac','sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
  assert hashlib.sha256((ROOT/'outputs/sakuragi-haruko-30s-voiced.mp4').read_bytes()).hexdigest()==report['video']['sha256']
  report['checks']['voiced_delivery_copy_matches']='passed'
  assert hashlib.sha256((ROOT/'outputs/sakuragi-haruko-30s-lipsync-v2.mp4').read_bytes()).hexdigest()==report['video']['sha256']
  report['checks']['lipsync_delivery_copy_matches']='passed'
 report['status']='passed'
except Exception as error:report.update(status='failed',error=str(error))
dest=OUT/('source-verification.json' if a.source_only else 'verification.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['status']=='passed' else 1)
