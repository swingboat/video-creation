"""Package only this video's portable deliverables; no external project files."""
from pathlib import Path
import zipfile
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
sources=['package.json','package-lock.json','.npmrc','.gitignore','.prettierrc','tsconfig.json','remotion.config.ts','eslint.config.mjs','README.md','requirements.txt','src','scripts','docs','public','outputs/checks','outputs/bottle-storm-bunny-fish-20s.mp4','outputs/versions/v1/bottle-storm.blend','outputs/versions/v1/timeline.json','outputs/versions/bunny-v2/bottle-storm.blend','outputs/versions/bunny-v2/timeline.json']
files=[]
for rel in sources:
    p=ROOT/rel
    if not p.exists():continue
    files.extend([f for f in p.rglob('*') if f.is_file()] if p.is_dir() else [p])
files=[p for p in files if not p.name.endswith(('.blend1','.pyc','.ips')) and '__pycache__' not in p.parts and 'preview' not in p.relative_to(ROOT).parts and p.name not in {'package-manifest.json','package-check.json','archive-check.json'}]
for p in files:
    if p.is_symlink() or not p.resolve().is_relative_to(ROOT.resolve()):raise RuntimeError('Escaping file: '+str(p))
manifest={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
mp=ROOT/'docs/package-manifest.json';mp.write_text(json.dumps(manifest,indent=2));files.append(mp)
out=ROOT/'outputs/bottle-storm-bunny-fish-project.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in files:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(out) as z:
    bad=z.testzip()
    if bad:raise RuntimeError('Archive CRC error: '+bad)
print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'files':len(files),'crc_ok':True},indent=2))
