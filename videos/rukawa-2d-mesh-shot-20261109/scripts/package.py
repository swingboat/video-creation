from pathlib import Path
import zipfile,json
R=Path(__file__).resolve().parents[1]
files=['package.json','package-lock.json','.npmrc','.gitignore','remotion.config.ts','tsconfig.json','README.md',
'src/index.ts','src/Root.tsx','src/CorrectedGather.tsx','src/gatherMotion.ts',
'scripts/run.mjs','scripts/check.py','scripts/audit-corrected.mjs','scripts/package.py',
'public/art/correctives/rukawa-gather-anatomy-v1.png','public/art/court-background.png','public/fonts/NotoSansSC.ttf',
'public/references/rukawa-approved.png','public/references/rejected-limb-pose.png','docs/corrective-pose-prompt.txt','docs/NOTO-OFL.txt','docs/generation-origin.md','docs/corrected-gather-notes.md',
'outputs/rukawa-corrected-gather-2s.mp4','outputs/checks/corrected-gather-audit.json','outputs/checks/corrected-project-check.json','outputs/checks/corrected-render.log','outputs/checks/corrected-video-poster.png']
out=R/'outputs/rukawa-corrected-gather-project.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for f in files:
  p=R/f
  if not p.is_file() or p.is_symlink():raise RuntimeError('Missing or linked package file: '+f)
  z.write(p,R.name+'/'+f)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps({'files':len(files),'bytes':out.stat().st_size,'zip':str(out.relative_to(R))}))
