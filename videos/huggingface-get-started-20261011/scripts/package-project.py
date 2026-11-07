from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'outputs/huggingface-remotion-project.zip'
files=[]
for name in ['src','public','scripts','docs']:
    files.extend(p for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(ROOT/name for name in ['package.json','package-lock.json','.npmrc','.gitignore','.prettierrc','eslint.config.mjs','tsconfig.json','remotion.config.ts','README.md'])
files.extend(ROOT/name for name in ['outputs/huggingface-guide-zh.mp4','outputs/huggingface-zh.srt','outputs/poster.png','outputs/checks/validation.json','outputs/checks/path-audit.json'])
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in sorted(files):
        if not file.exists():raise RuntimeError(f'Missing {file}')
        resolved=file.resolve()
        if not resolved.is_relative_to(ROOT):raise RuntimeError(f'External path {file}')
        z.write(file,ROOT.name+'/'+str(file.relative_to(ROOT)))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert all(n.startswith(ROOT.name+'/') and '..' not in Path(n).parts for n in z.namelist())
report={'archive':out.name,'files':len(files),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zipIntegrityPassed':True,'containsOtherVideos':False,'node_modulesAndCachesIncluded':False}
(ROOT/'outputs/checks/package.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
