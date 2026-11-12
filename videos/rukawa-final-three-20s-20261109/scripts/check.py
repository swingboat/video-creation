"""Verify the standalone project and the actual exported media."""
import hashlib,json,re,subprocess,wave
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/checks'
OUT.mkdir(parents=True,exist_ok=True)
report={'checks':{},'limitations':'Technical checks do not certify anatomy or natural character animation. This is a limited-animation trial.'}

def run(args):
    p=subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(' '.join(map(str,args))+'\n'+p.stdout+'\n'+p.stderr)
    return p

def inside(path):
    return path.resolve().is_relative_to(ROOT)

try:
    p=run([str(ROOT/'node_modules/.bin/tsc'),'--noEmit'])
    (OUT/'typecheck.log').write_text(p.stdout+p.stderr)
    report['checks']['typescript']='passed'
    package=json.loads((ROOT/'package.json').read_text())
    lock=json.loads((ROOT/'package-lock.json').read_text())
    assert package['name']==lock['name']==lock['packages']['']['name']
    for name,version in package['dependencies'].items():
        installed=json.loads((ROOT/'node_modules'/name/'package.json').read_text())
        assert installed['version']==version,(name,installed['version'],version)
    report['checks']['independent_locked_dependencies']='passed'
    checked=[]
    sources=list((ROOT/'src').rglob('*.ts'))+list((ROOT/'src').rglob('*.tsx'))
    for f in sources+list((ROOT/'scripts').glob('*'))+[ROOT/'remotion.config.ts']:
        assert inside(f) and not f.is_symlink(),str(f)
        text=f.read_text()
        if f.suffix in ['.ts','.tsx','.mjs']:
            assert not re.search(r'(?:https?://|/Users/|/videos/|file:)',text),str(f)
        for imp in re.findall(r'(?:from\s*|import\s*)[\'"]([^\'"]+)',text):
            if imp.startswith('.'):
                ref=(f.parent/imp)
                assert inside(ref),(f,imp)
                candidates=[ref,ref.with_suffix('.ts'),ref.with_suffix('.tsx'),ref/'index.ts']
                assert any(c.exists() for c in candidates),(f,imp)
            elif f in sources:
                name='/'.join(imp.split('/')[:2]) if imp.startswith('@') else imp.split('/')[0]
                assert name in package['dependencies'] or name in package['devDependencies'],(f,imp)
        checked.append(str(f.relative_to(ROOT)))
    paths=re.findall(r"'(art/[^']+)'",(ROOT/'src/gpu.ts').read_text())
    paths+=['audio/arena.wav','fonts/NotoSansSC.ttf']
    for name in paths:
        f=ROOT/'public'/name
        assert f.is_file() and inside(f) and not f.is_symlink(),name
    for f in (ROOT/'public').rglob('*'):
        assert not f.is_symlink(),str(f)
    report['checks']['local_runtime_paths']={'status':'passed','source_files':len(checked),'assets':len(paths)}
    with wave.open(str(ROOT/'public/audio/arena.wav')) as wav:
        assert wav.getnframes()/wav.getframerate()==20
        assert wav.getnchannels()==2
    report['checks']['source_audio']='20.0s, stereo'
    video=ROOT/'outputs/rukawa-final-three-20s.mp4'
    metadata=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]).stdout)
    v=next(s for s in metadata['streams'] if s['codec_type']=='video')
    a=next(s for s in metadata['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'])==(1280,720)
    assert v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==600
    assert v['codec_name']=='h264' and a['codec_name']=='aac' and a['channels']==2
    assert abs(float(metadata['format']['duration'])-20)<.05
    assert abs(float(a['duration'])-20)<.05
    decode=run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'])
    assert not decode.stderr.strip(),decode.stderr
    report['checks']['full_decode']='passed'
    report['video']={'file':str(video.relative_to(ROOT)),'width':1280,'height':720,'fps':30,'frames':600,'duration':float(metadata['format']['duration']),'audio':a['codec_name'],'channels':a['channels'],'sha256':hashlib.sha256(video.read_bytes()).hexdigest()}
    (OUT/'media-metadata.json').write_text(json.dumps(metadata,indent=2))
    report['status']='passed'
except Exception as e:
    report['status']='failed'
    report['error']=str(e)
finally:
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report['status']=='passed' else 1)
