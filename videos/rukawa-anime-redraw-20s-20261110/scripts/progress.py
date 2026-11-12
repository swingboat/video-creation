import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['shot','close','rim','celebrate','hero']:
 f=root/'outputs/checks'/f'{name}-generation.log'
 if not f.exists():continue
 raw=f.read_text(errors='replace').replace('\r','\n');lines=[s.strip() for s in raw.splitlines() if s.strip()]
 meta=root/'outputs/checks'/f'generation-{name}.json'
 state=json.loads(meta.read_text()) if meta.exists() else {}
 if state.get('exit_code')==0:print(name,'READY',state.get('wall_seconds'),'seconds')
 else:
  tail=[s for s in lines if not s.startswith(('"prompt"','"method"'))][-6:]
  print(name,'\n'+'\n'.join(tail))
