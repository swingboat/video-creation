from pathlib import Path
import json,sys,shutil
p=Path(sys.argv[1]);stem=sys.argv[2];j=json.loads(p.read_text());paths=[]
def collect(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='path' and isinstance(v,str) and 'Tabbit/LocalAgent/Runtime/artifacts/' in v and v not in paths:paths.append(v)
   else:collect(v)
 elif isinstance(x,list):
  for v in x:collect(v)
collect(j)
for i,v in enumerate(paths):
 dest=p.parent/(stem+(f'-{i+1}' if len(paths)>1 else '')+'.png');src=Path(v)
 if src.exists():shutil.move(src,dest)
 print(str(dest.resolve()))
value=j.get('result',{}).get('value')
print(json.dumps({'status':j.get('status'),'value':value if not paths else 'screenshots moved into project'},ensure_ascii=False))
