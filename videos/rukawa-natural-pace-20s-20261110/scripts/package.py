import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];verification=json.loads((ROOT/'outputs/checks/verification.json').read_text());assert verification['status']=='passed'
movie=ROOT/'outputs/rukawa-natural-pace-20s.mp4';assert hashlib.sha256(movie.read_bytes()).hexdigest()==verification['video']['sha256']
files=[ROOT/n for n in ['README.md','package.json','package-lock.json','.npmrc','.gitignore','remotion.config.ts','tsconfig.json','requirements-local-video.txt']]
for folder in ['src','scripts','public','docs']:files.extend(f for f in (ROOT/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts)
files.extend([movie,ROOT/'outputs/review.html',ROOT/'outputs/checks/verification.json'])
for relative in ['cadence/report.json','audio-normalization.json','media-metadata.json']:
 report=ROOT/'outputs/checks'/relative
 if report.exists():files.append(report)
for name in ['dribble','defender','defender-natural3','close','shot','rim','celebrate','crowd','hero','hero-natural4','dribble-natural4','crowd-natural4']:
 p=ROOT/'outputs/checks'/f'generation-{name}.json'
 if p.exists():files.append(p)
target=ROOT/'outputs/rukawa-natural-pace-project.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(set(files)):
  assert not f.is_symlink() and f.resolve().is_relative_to(ROOT),str(f)
  z.write(f,str(Path(ROOT.name)/f.relative_to(ROOT)))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert hashlib.sha256(z.read(str(Path(ROOT.name)/movie.relative_to(ROOT)))).hexdigest()==verification['video']['sha256']
report={'archive':str(target.relative_to(ROOT)),'files':len(set(files)),'bytes':target.stat().st_size,'crc_test':'passed','video_hash_matches':True};(ROOT/'outputs/checks/package-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
