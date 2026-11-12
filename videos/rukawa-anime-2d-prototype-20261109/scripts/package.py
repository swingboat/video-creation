from pathlib import Path
import zipfile
r=Path(__file__).resolve().parents[1];dest=r/'outputs/rukawa-anime-sample-v2-project.zip';items=[]
for p in r.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(r)
 if any(x in rel.parts for x in ['node_modules','.cache','__pycache__','remotion-bundle']):continue
 if p.suffix=='.zip':continue
 items.append(p)
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in items:z.write(p,Path(r.name)/p.relative_to(r))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
print('PACKAGE',str(dest),dest.stat().st_size,len(items))
