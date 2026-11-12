"""Move a built-in generated image immediately into this project's asset tree."""
import project_env
import sys,json,shutil,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]);dest=root/'public/art'/sys.argv[2]
if dest.exists():raise SystemExit('Refusing to overwrite an existing candidate')
shutil.move(str(source),dest)
manifest=root/'docs/image-assets.json';rows=json.loads(manifest.read_text()) if manifest.exists() else []
rows.append({'asset':str(dest.relative_to(root)),'tool':'built-in image_gen','tool_original':str(source),'original_moved_into_project':True,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
manifest.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(dest)
