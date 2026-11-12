"""Package this project's sources, local assets and verified final movie."""
import hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
verification=json.loads((ROOT/'outputs/checks/verification.json').read_text())
assert verification['status']=='passed','Run npm run check first'
movie=ROOT/'outputs/rukawa-final-three-20s.mp4'
assert hashlib.sha256(movie.read_bytes()).hexdigest()==verification['video']['sha256']
target=ROOT/'outputs/rukawa-final-three-project.zip'
files=[ROOT/f for f in ['README.md','package.json','package-lock.json','.npmrc','remotion.config.ts','tsconfig.json']]
for dirname in ['src','scripts','public','docs']:
    files.extend(f for f in (ROOT/dirname).rglob('*') if f.is_file() and '__pycache__' not in f.parts)
files+=[movie,ROOT/'outputs/checks/verification.json',ROOT/'outputs/checks/audio-report.json']
poster=ROOT/'outputs/checks/final-release.png'
if poster.exists():files.append(poster)
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in sorted(set(files)):
        assert f.resolve().is_relative_to(ROOT) and not f.is_symlink(),str(f)
        z.write(f,str(Path(ROOT.name)/f.relative_to(ROOT)))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    packed=z.read(str(Path(ROOT.name)/movie.relative_to(ROOT)))
    assert hashlib.sha256(packed).hexdigest()==verification['video']['sha256']
report={'archive':str(target.relative_to(ROOT)),'files':len(set(files)),'bytes':target.stat().st_size,'crc_test':'passed','included_movie_sha256_matches':True}
(ROOT/'outputs/checks/package-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
