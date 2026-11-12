import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['dribble','defender','close','shot','rim','celebrate','crowd','hero']:
 selected=root/'outputs/checks'/f'generation-{name}.json'
 if selected.exists():
  state=json.loads(selected.read_text())
  if state.get('playback_speed')==1:
   print(name,'selected',state['duration'],'seconds at native speed');continue
 log=root/'outputs/checks'/f'{name}-natural-generation.log'
 if log.exists():
  lines=[s.strip() for s in log.read_text(errors='replace').replace('\r','\n').splitlines() if s.strip()]
  print(name,lines[-1][:160] if lines else 'waiting')
 else:print(name,'not generated yet')
