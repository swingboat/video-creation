from pathlib import Path
import zipfile,json
r=Path(__file__).resolve().parents[1];out=r/'outputs/rukawa-project.zip';files=[]
for p in r.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(r)
 if any(x in rel.parts for x in ['node_modules','.cache','.venv','__pycache__','frames','remotion-bundle','versions']):continue
 if p.suffix in ['.zip','.blend1'] or rel.parts[:3]==('outputs','checks','preview'):continue
 files.append(p)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path(r.name)/p.relative_to(r))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PACKAGED',out,out.stat().st_size,len(files))
