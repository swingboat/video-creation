"""Download the selected complete free athlete from Microsoft's MIT repository."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json,hashlib

P=Path.cwd();D=P/'sources/research/realism-v7/rocketbox';D.mkdir(parents=True,exist_ok=True)
base='https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/'
folder='Assets/Avatars/Professions/Sports_Male_04/'
paths=[folder+'Export/Sports_Male_04.fbx']+[folder+'Textures/m026_'+part+'_'+kind+'.tga' for part in ['body','head'] for kind in ['color','normal','specular']]+['LICENSE.md','README.md']
def fetch(src):
 dest=D/Path(src).name;url=base+src
 if not dest.exists():urllib.request.urlretrieve(url,dest)
 return {'url':url,'file':str(dest.relative_to(P)),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
items=list(ThreadPoolExecutor(4).map(fetch,paths));(D/'download.json').write_text(json.dumps(items,indent=2));print('Free complete character ready:',len(items),'files')
