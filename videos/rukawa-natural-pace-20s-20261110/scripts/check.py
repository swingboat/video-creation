"""Integration checks for standalone sources and the actual final movie."""
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/checks';OUT.mkdir(parents=True,exist_ok=True)
def binary(name):
 value=shutil.which(name)
 if value:return value
 p=Path('/opt/homebrew/bin')/name
 if p.exists():return str(p)
 raise RuntimeError(name+' must be installed and on PATH')
def run(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+'\n'+p.stderr)
 return p
def probe(f):return json.loads(run([binary('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(f)]).stdout)
report={'checks':{},'limitations':'Technical validation does not establish visual anatomy, natural movement, character identity or shot continuity. Those require actual frame and playback review.'}
try:
 node=binary('node');p=run([node,str(ROOT/'node_modules/typescript/bin/tsc'),'--noEmit']);(OUT/'typecheck.log').write_text(p.stdout+p.stderr);report['checks']['typescript']='passed'
 package=json.loads((ROOT/'package.json').read_text());lock=json.loads((ROOT/'package-lock.json').read_text());assert package['name']==lock['name']==lock['packages']['']['name']
 for name,v in package['dependencies'].items():assert json.loads((ROOT/'node_modules'/name/'package.json').read_text())['version']==v
 sources=list((ROOT/'src').rglob('*.ts'))+list((ROOT/'src').rglob('*.tsx'))
 for f in sources:
  assert not f.is_symlink() and f.resolve().is_relative_to(ROOT),str(f)
  s=f.read_text();assert not re.search(r'https?://|/Users/|file:|/videos/',s),str(f)
  for imp in re.findall(r'(?:from\s*|import\s*)[\'"]([^\'"]+)',s):
   if imp.startswith('.'):
    ref=f.parent/imp;assert ref.resolve().is_relative_to(ROOT)
    assert any(p.exists() for p in [ref,ref.with_suffix('.ts'),ref.with_suffix('.tsx'),ref/'index.ts']),imp
  for asset in re.findall(r"['\"]((?:art|video|fonts|audio)/[^'\"]+)['\"]",s):
   p=ROOT/'public'/asset;assert p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_symlink(),asset
 for f in (ROOT/'public').rglob('*'):assert not f.is_symlink(),str(f)
 runtime_files=[ROOT/n for n in ['package.json','package-lock.json','requirements-local-video.txt','.npmrc','remotion.config.ts','tsconfig.json']]
 runtime_files += [f for f in (ROOT/'scripts').iterdir() if f.suffix in ['.py','.mjs'] and f.name!='check.py']
 for f in runtime_files:
  assert not re.search(r'/Users/|file://',f.read_text()),str(f)
 for line in (ROOT/'requirements-local-video.txt').read_text().splitlines():
  if line.startswith('.cache/'):
   dependency=(ROOT/line).resolve();assert dependency.is_relative_to(ROOT),line
 report['checks']['runtime_configuration_paths']='passed'
 report['checks']['standalone_paths']='passed'
 status=(ROOT/'src/media-status.ts').read_text()
 clip_specs={'dribble':1.5,'defender':2.5,'close':2,'shot':2,'rim':2,'celebrate':2,'crowd':4,'hero':4}
 clips=[]
 for name,seconds in clip_specs.items():
  assert re.search(r'\b'+name+r':true',status),'Unfinished clip '+name
  f=ROOT/'public/video'/f'{name}.mp4';m=probe(f);v=next(s for s in m['streams'] if s['codec_type']=='video')
  assert float(v['duration'])>=seconds and v['avg_frame_rate']=='24/1',name
  selection=json.loads((OUT/f'generation-{name}.json').read_text())
  assert selection['playback_speed']==1 and selection['source_seconds_used']==seconds,name
  clips.append({'file':str(f.relative_to(ROOT)),'duration':v['duration'],'frames':v.get('nb_frames'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 report['checks']['continuous_source_media']=clips
 movie=ROOT/'outputs/rukawa-natural-pace-20s.mp4';m=probe(movie);v=next(s for s in m['streams'] if s['codec_type']=='video');a=next(s for s in m['streams'] if s['codec_type']=='audio')
 assert v['codec_name']=='h264' and (v['width'],v['height'])==(1280,720) and v['avg_frame_rate']=='24/1' and int(v['nb_frames'])==480
 assert abs(float(v['duration'])-20)<.01 and abs(float(m['format']['duration'])-20)<.05
 assert a['codec_name']=='aac' and abs(float(a['duration'])-20)<.05
 decoded=run([binary('ffmpeg'),'-v','error','-i',str(movie),'-f','null','-']);assert not decoded.stderr.strip(),decoded.stderr
 (OUT/'media-metadata.json').write_text(json.dumps(m,indent=2));report['checks']['full_decode']='passed'
 report['video']={'file':str(movie.relative_to(ROOT)),'frames':480,'fps':24,'duration':float(v['duration']),'width':1280,'height':720,'audio':a['codec_name'],'sha256':hashlib.sha256(movie.read_bytes()).hexdigest()};report['status']='passed'
except Exception as e:report.update(status='failed',error=str(e))
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['status']=='passed' else 1)
