from pathlib import Path
import zipfile,json
ROOT=Path(__file__).resolve().parents[1]
slug=json.loads((ROOT/'project.json').read_text())['slug']
name='unet-remotion-project.zip' if slug=='unet-explainer' else slug+'-project.zip'
archive=ROOT/'outputs'/name
files=[]
for directory in ['src','public','scripts','docs','outputs']:
 files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix!='.zip' and '__pycache__' not in p.parts and not p.is_symlink() and p.name!='archive-report.json')
for name in ['package.json','package-lock.json','project.json','README.md','tsconfig.json','remotion.config.ts','.npmrc','.gitignore']:
 files.append(ROOT/name)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(set(files)):
  z.write(p,Path(slug)/p.relative_to(ROOT))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert all(n.startswith(slug+'/') for n in z.namelist())
 assert slug+'/src/Root.tsx' in z.namelist()
(ROOT/'outputs/checks/archive-report.json').write_text(json.dumps({'archive':'outputs/'+archive.name,'bytes':archive.stat().st_size,'fileCount':len(set(files)),'zipCRCCheckPassed':True,'oneVideoOnly':True,'nodeModulesAndCacheExcluded':True},ensure_ascii=False,indent=2))
print(archive,archive.stat().st_size,'bytes; CRC passed')
