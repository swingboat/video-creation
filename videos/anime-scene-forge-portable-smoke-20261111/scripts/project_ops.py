"""Project-local, standard-library helpers. Technical checks do not approve art."""
import project_env
import argparse,hashlib,json,math,re,subprocess,wave,zipfile
from fractions import Fraction
from pathlib import Path,PureWindowsPath

ROOT=Path(__file__).resolve().parents[1]

def require(ok,message):
    if not ok:raise ValueError(message)

def local(name,public=False):
    require(isinstance(name,str) and name and not Path(name).is_absolute() and not PureWindowsPath(name).is_absolute(),f'Use a local relative path: {name}')
    if public:require('\\' not in name,'Use forward slashes in browser-facing asset paths')
    base=ROOT/'public' if public else ROOT
    p=base/name
    require(p.resolve().is_relative_to(base.resolve()),f'Path escapes project: {name}')
    for q in [p,*p.parents]:
        if q==base.parent:break
        require(not q.is_symlink(),f'Symlink not allowed: {name}')
    return p

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()

def load():return json.loads((ROOT/'production.json').read_text())
def save(data):
    path=ROOT/'.cache/tmp/production-next.json';path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');path.replace(ROOT/'production.json')
def emit(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def integer(x):return isinstance(x,int) and not isinstance(x,bool)
def call(cmd):return subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
def probe(path):return json.loads(call(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]).stdout)
def video_info(path):
    m=probe(path);v=next(s for s in m['streams'] if s['codec_type']=='video')
    n=v.get('nb_read_frames',v.get('nb_frames'))
    require(n not in [None,'N/A'],f'Cannot count video frames: {path.name}')
    return m,v,int(n)
def pcm(path):
    with wave.open(str(path),'rb') as f:
        require((f.getframerate(),f.getnchannels(),f.getsampwidth())==(48000,2,2),f'Use 48kHz stereo PCM16 WAV: {path.name}')
        return f.readframes(f.getnframes())
def get_shot(data,name):
    shots=[s for s in data['shots'] if s['id']==name]
    require(len(shots)==1,f'Unknown or duplicate shot: {name}');return shots[0]

def validate(stage='final'):
    data=load();require(data.get('schemaVersion')==1,'Unsupported production schema version');fmt=data['format'];fps=fmt['fps'];total=fmt['durationFrames']
    require(all(integer(fmt[k]) and fmt[k]>0 for k in ['fps','width','height','durationFrames']),'Format requires positive integers')
    require(fmt['width']%2==fmt['height']%2==0,'Video dimensions must be even')
    require(data['shots'] and sum(s['frames'] for s in data['shots'])==total,'Shot durations must sum to durationFrames')
    ids=[s['id'] for s in data['shots']]
    require(len(ids)==len(set(ids)) and all(re.fullmatch(r'[a-zA-Z0-9-]+',s) for s in ids),'Use unique alphanumeric/hyphen shot IDs')
    for folder in ['src','public','scripts']:
        for p in (ROOT/folder).rglob('*'):
            require(not p.is_symlink() and p.resolve().is_relative_to(ROOT),f'Nonlocal file: {p}')
            if p.is_file():require(p.stat().st_nlink==1,f'Hard link not allowed: {p}')
    for s in data['shots']:
        require(integer(s['frames']) and s['frames']>0,f'Invalid duration: {s["id"]}')
        if s.get('art'):require(local(s['art'],True).is_file(),f'Missing artwork: {s["id"]}')
        if s.get('clip'):
            path=local(s['clip'],True);require(path.is_file(),f'Missing clip: {s["id"]}')
            _,v,n=video_info(path)
            require(Fraction(v['avg_frame_rate'])==fps and n==s['frames'],f'Wrong native fps or frame count: {s["id"]}')
            require((v['width'],v['height'])==(fmt['width'],fmt['height']),f'Wrong clip dimensions: {s["id"]}')
        elif stage!='scaffold':raise ValueError(f'Missing footage: {s["id"]}')
        c=s.get('caption')
        if c:
            require(isinstance(c['text'],str) and 0<=c['startFrame']<c['endFrame']<=s['frames'],f'Invalid caption: {s["id"]}')
            if stage=='final' and any(ord(x)>127 for x in c['text']):require(data.get('fontFile'),'Provide a project-local font for non-ASCII captions')
        d=s.get('dialogue')
        if d:
            require(d.get('sync') in ['on-screen','voiceover'] and isinstance(d.get('text'),str) and d['text'].strip(),f'Invalid dialogue description: {s["id"]}')
            require(integer(d['fromFrame']) and 0<=d['fromFrame']<s['frames'],f'Invalid dialogue start: {s["id"]}')
            if not d.get('file'):
                require(stage=='scaffold',f'Missing voice: {s["id"]}');continue
            voice=pcm(local(d['file'],True));spf=Fraction(48000,fps)
            require(spf.denominator==1,'Dialogue driver requires an integer sample count per frame')
            offset=d['fromFrame']*int(spf)*4
            require(offset+len(voice)<=s['frames']*int(spf)*4,f'Voice exceeds selected shot: {s["id"]}')
            if d.get('driverFile'):
                driver_path=local(d['driverFile'],True);driver=pcm(driver_path)
                require(sha(driver_path)==d['driverSha256'],'Driver changed; regenerate the speaking clip')
                require(driver[:offset]==bytes(offset) and driver[offset:offset+len(voice)]==voice and driver[offset+len(voice):]==bytes(len(driver)-offset-len(voice)),'Driver differs from final voice or timing')
                require(sha(local(d['file'],True))==d['voiceSha256'],'Voice changed; create a new driver and speaking take')
            if d['sync']=='on-screen' and stage!='scaffold':
                require(d.get('driverFile') and s.get('generation'),f'Missing A2V provenance: {s["id"]}')
                g=json.loads(local(s['generation']).read_text())
                require(g['mode']=='a2v' and g['audioSha256']==d['driverSha256'],f'Voice/footage mismatch: {s["id"]}')
                raw=local(g['output']);require(sha(raw)==g['outputSha256'],'Raw candidate changed')
        if stage=='final':
            require(s.get('status')=='approved' and s.get('review'),f'Visual review pending: {s["id"]}')
            review=json.loads(local(s['review']).read_text())
            require(review.get('visualReviewed') is True and review.get('normalSpeedReviewed') is True and review.get('reviewer') and review.get('observations'),f'Incomplete visual record: {s["id"]}')
            require(review['clipSha256']==sha(local(s['clip'],True)),f'Stale visual review: {s["id"]}')
    if data.get('fontFile'):require(local(data['fontFile'],True).is_file(),'Missing font')
    if data.get('background'):
        b=data['background'];require(local(b['file'],True).is_file() and isinstance(b['volume'],(int,float)) and math.isfinite(b['volume']) and b['volume']>=0,'Invalid background')
    for e in data.get('sfx',[]):
        require(integer(e['frame']) and 0<=e['frame']<total and local(e['file'],True).is_file(),'Invalid sound event')
    return data

def select(a):
    data=load();s=get_shot(data,a.shot);source=local(a.source)
    _,v,n=video_info(source);fmt=data['format'];fps=fmt['fps']
    require(Fraction(v['avg_frame_rate'])==fps,'Source fps differs; choose native timeline fps or explicitly redesign conversion')
    require(a.start>=0 and a.start+s['frames']<=n,'Selected interval exceeds source')
    w,h=v['width'],v['height'];filters=[]
    if a.crop:
        x,y,w,h=a.crop;require(min(x,y)>=0 and min(w,h)>0 and x+w<=v['width'] and y+h<=v['height'],'Invalid crop')
        filters.append(f'crop={w}:{h}:{x}:{y}')
    require(abs(w/h-fmt['width']/fmt['height'])<.01,'Aspect differs: provide an intentional crop or regenerate the correct framing')
    filters+= [f'scale={fmt["width"]}:{fmt["height"]}:flags=lanczos','setsar=1']
    target=ROOT/f'public/video/{s["id"]}-{a.take}.mp4';require(not target.exists(),'Preserving existing selection; use a new take')
    if a.generation:
        g=json.loads(local(a.generation).read_text());require(g['outputSha256']==sha(source),'Generation record is for different source footage')
    call(['ffmpeg','-y','-v','error','-ss',f'{a.start/fps:.12f}','-i',str(source),'-map','0:v:0','-an','-frames:v',str(s['frames']),'-vf',','.join(filters),'-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p','-fps_mode','passthrough','-movflags','+faststart',str(target)])
    record={'source':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(source),'startFrame':a.start,'frames':s['frames'],'fps':fps,'speed':1,'crop':a.crop,'output':target.relative_to(ROOT).as_posix(),'outputSha256':sha(target)}
    emit(ROOT/f'docs/selections/{s["id"]}-{a.take}.json',record)
    s.update(clip=target.relative_to(ROOT/'public').as_posix(),status='candidate',review=None,generation=a.generation)
    save(data);print(json.dumps(record,indent=2))

def pad(a):
    data=load();s=get_shot(data,a.shot);fps=data['format']['fps'];d=s.get('dialogue')
    require(d and d.get('text'),'Fill shot.dialogue text/sync before preparing its voice')
    require(a.from_frame>=0 and a.source_frames>=s['frames'] and 48000%fps==0,'Invalid source duration or audio offset')
    path=local(a.voice);voice=pcm(path);spf=48000//fps;offset=a.from_frame*spf*4
    require(offset+len(voice)<=s['frames']*spf*4,'Voice exceeds adopted shot; revise line/take/timeline at normal speed')
    target=ROOT/f'public/audio/drivers/{s["id"]}-{a.take}.wav';require(not target.exists(),'Preserving existing driver; use a new take')
    body=bytes(offset)+voice+bytes(a.source_frames*spf*4-offset-len(voice))
    with wave.open(str(target),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes(body)
    d.update(file=path.relative_to(ROOT/'public').as_posix(),fromFrame=a.from_frame,driverFile=target.relative_to(ROOT/'public').as_posix(),driverSha256=sha(target),voiceSha256=sha(path))
    s.update(status='candidate',review=None);save(data)
    print(json.dumps({'driver':d['driverFile'],'voiceSha256':d['voiceSha256'],'frames':a.source_frames,'speed':1},indent=2))

def sheet(a):
    data=load();s=get_shot(data,a.shot);require(s.get('clip'),'Select footage first')
    source=local(s['clip'],True);_,_,n=video_info(source)
    out=ROOT/f'outputs/checks/{s["id"]}/{a.label}';out.mkdir(parents=True,exist_ok=True)
    call(['ffmpeg','-y','-v','error','-i',str(source),str(out/'frame-%04d.png')])
    vf=[]
    if a.crop:
        x,y,w,h=a.crop;require(min(x,y)>=0 and min(w,h)>0,'Invalid review crop');vf+=[f'crop={w}:{h}:{x}:{y}']
    vf+=['scale=240:-1',f'tile=5x{math.ceil(n/5)}']
    call(['ffmpeg','-y','-v','error','-i',str(source),'-vf',','.join(vf),'-frames:v','1','-update','1',str(out/'all-frames.png')])
    emit(out/'index.json',{'clipSha256':sha(source),'crop':a.crop,'columns':5,'frames':[{'sourceFrame':i,'filename':f'frame-{i+1:04d}.png','tileRow':i//5,'tileColumn':i%5} for i in range(n)],'visualApproval':'not automatically assigned'})
    print(out/'all-frames.png')

def fingerprint(data):
    paths=[ROOT/n for n in ['production.json','package.json','package-lock.json','tsconfig.json','remotion.config.ts']]
    paths+=list((ROOT/'src').rglob('*.ts'))+list((ROOT/'src').rglob('*.tsx'))
    media=[]
    for s in data['shots']:
        media+=[s.get('clip')]
        if s.get('dialogue'):media+=[s['dialogue'].get('file')]
    media+=[data.get('fontFile')]
    if data.get('background'):media+=[data['background']['file']]
    media+=[e['file'] for e in data.get('sfx',[])]
    paths += [local(m,True) for m in media if m]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))}

def verify(rendered=False):
    data=validate();movie=ROOT/'outputs/final.mp4';require(movie.is_file(),'Export final.mp4 first')
    state=ROOT/'outputs/checks/export.json';inputs=fingerprint(data)
    if not rendered:
        require(state.is_file(),'No render provenance; export using npm run render')
        prior=json.loads(state.read_text());require(prior['inputs']==inputs and prior['sha256']==sha(movie),'Media/source changed after render; export again')
    meta,v,n=video_info(movie);fmt=data['format']
    require(v['codec_name']=='h264' and n==fmt['durationFrames'] and Fraction(v['avg_frame_rate'])==fmt['fps'],'Wrong export codec/fps/frames')
    require((v['width'],v['height'])==(fmt['width'],fmt['height']),'Wrong export dimensions')
    require(abs(float(v['duration'])-n/fmt['fps'])<.05,'Wrong export duration')
    if data.get('background') or data.get('sfx') or any(s.get('dialogue') for s in data['shots']):require(any(s['codec_type']=='audio' for s in meta['streams']),'Exported audio missing')
    call(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'])
    result={'status':'technical-pass','scope':'Visual status is read from authored reviews, not assessed by these checks.','file':'outputs/final.mp4','sha256':sha(movie),'frames':n,'fps':fmt['fps'],'duration':n/fmt['fps'],'inputs':inputs}
    emit(state,result);return result

def package():
    report=verify();files=[ROOT/n for n in ['package.json','package-lock.json','.npmrc','.gitignore','README.md','tsconfig.json','remotion.config.ts','production.json']]
    for folder in ['src','public','scripts','docs']:
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files += list(ROOT.glob('requirements*.txt'))+[ROOT/'outputs/final.mp4',ROOT/'outputs/checks/export.json']
    target=ROOT/'outputs/project.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(set(files)):
            require(p.resolve().is_relative_to(ROOT) and not p.is_symlink(),'Archive path escape');z.write(p,(Path(ROOT.name)/p.relative_to(ROOT)).as_posix())
    with zipfile.ZipFile(target) as z:
        require(z.testzip() is None,'ZIP CRC failed')
        require(hashlib.sha256(z.read((Path(ROOT.name)/'outputs/final.mp4').as_posix())).hexdigest()==report['sha256'],'Archived movie differs')
    result={'file':'outputs/project.zip','files':len(set(files)),'bytes':target.stat().st_size,'sha256':sha(target),'crc':'passed'}
    emit(ROOT/'outputs/checks/package.json',result);return result

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    v=sub.add_parser('validate');v.add_argument('--stage',choices=['scaffold','draft','final'],default='final')
    s=sub.add_parser('select');s.add_argument('shot');s.add_argument('--source',required=True);s.add_argument('--start',type=int,default=0);s.add_argument('--take',required=True);s.add_argument('--crop',nargs=4,type=int);s.add_argument('--generation')
    d=sub.add_parser('pad-voice');d.add_argument('shot');d.add_argument('--voice',required=True);d.add_argument('--from-frame',type=int,required=True);d.add_argument('--source-frames',type=int,required=True);d.add_argument('--take',required=True)
    f=sub.add_parser('sheet');f.add_argument('shot');f.add_argument('--crop',nargs=4,type=int);f.add_argument('--label',default='full')
    e=sub.add_parser('verify-export');e.add_argument('--rendered',action='store_true')
    sub.add_parser('package');a=p.parse_args()
    if hasattr(a,'take'):require(re.fullmatch(r'[a-zA-Z0-9-]+',a.take),'Use a safe take identifier')
    if hasattr(a,'label'):require(re.fullmatch(r'[a-zA-Z0-9-]+',a.label),'Use a safe label')
    if a.command=='validate':data=validate(a.stage);print(json.dumps({'status':'passed','stage':a.stage,'frames':data['format']['durationFrames'],'scope':'Technical and provenance checks only'},indent=2))
    elif a.command=='select':select(a)
    elif a.command=='pad-voice':pad(a)
    elif a.command=='sheet':sheet(a)
    elif a.command=='verify-export':print(json.dumps(verify(a.rendered),indent=2))
    elif a.command=='package':print(json.dumps(package(),indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,FileNotFoundError,wave.Error,subprocess.CalledProcessError) as e:raise SystemExit(str(e))
