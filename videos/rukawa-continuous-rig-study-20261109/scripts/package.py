from pathlib import Path
import zipfile,json
R=Path(__file__).resolve().parents[1];dest=R/'outputs/continuous-rig-study-project.zip'
paths=[]
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R)
 if any(x in ['node_modules','.cache','__pycache__','.git'] for x in rel.parts):continue
 if rel.parts[:2]==('outputs','frames') or p.suffix in ['.zip','.blend1'] or p.name=='.DS_Store' or p.name=='Arial-Unicode.ttf':continue
 if p.is_symlink():raise SystemExit('Unexpected symlink: '+str(rel))
 paths.append(p)
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for p in paths:z.write(p,R.name+'/'+str(p.relative_to(R)))
with zipfile.ZipFile(dest) as z:
 bad=z.testzip()
 if bad:raise SystemExit('ZIP corrupt: '+bad)
print(json.dumps({'zip':str(dest.relative_to(R)),'files':len(paths),'bytes':dest.stat().st_size}))
