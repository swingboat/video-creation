"""Package only this video's reproducible project, local media, checks and final export."""
import project_env
from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1];report=json.loads((ROOT/'outputs/checks/verification.json').read_text());assert report['status']=='passed'
movie=ROOT/'outputs/sakuragi-haruko-30s.mp4';assert hashlib.sha256(movie.read_bytes()).hexdigest()==report['video']['sha256']
files=[ROOT/name for name in ['README.md','package.json','package-lock.json','.npmrc','.gitignore','remotion.config.ts','tsconfig.json','requirements-local-video.txt','requirements-tts.txt']]
for name in ['src','scripts','public','docs']:
 files.extend(f for f in (ROOT/name).rglob('*') if f.is_file() and '__pycache__' not in f.parts)
files.append(movie)
files.append(ROOT/'outputs/sakuragi-haruko-30s-voiced.mp4')
files.append(ROOT/'outputs/review.html')
files.append(ROOT/'outputs/review-voiced.html')
files.append(ROOT/'outputs/review-lipsync.html')
lip_movie=ROOT/'outputs/sakuragi-haruko-30s-lipsync-v2.mp4'
if lip_movie.exists():files.append(lip_movie)
files.extend((ROOT/'outputs/checks/lipsync').glob('*-comparison.mp4'))
files.append(ROOT/'outputs/cover.jpg')
files.extend(p for p in (ROOT/'outputs/checks').rglob('*.json') if p.name!='package-report.json')
for name in ['overview.jpg','contact-every-frame.jpg','hand-contacts-first36.jpg','face-every-frame.jpg','listener-every-frame.jpg','clap-contact-keyframes.jpg','clap-onset-frames7-14.jpg']:
 files.extend((ROOT/'outputs/checks').rglob(name))
target=ROOT/'outputs/sakuragi-haruko-project.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for file in sorted(set(files)):
  assert not file.is_symlink() and file.resolve().is_relative_to(ROOT),str(file)
  archive.write(file,str(Path(ROOT.name)/file.relative_to(ROOT)))
with zipfile.ZipFile(target) as archive:
 assert archive.testzip() is None
 assert hashlib.sha256(archive.read(str(Path(ROOT.name)/movie.relative_to(ROOT)))).hexdigest()==report['video']['sha256']
summary={'archive':str(target.relative_to(ROOT)),'files':len(set(files)),'bytes':target.stat().st_size,'crc':'passed','final_video_sha256_matches':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(ROOT/'outputs/checks/package-report.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
