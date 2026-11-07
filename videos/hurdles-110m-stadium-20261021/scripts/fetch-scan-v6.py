"""Download the vendor's public free sample directly into this video project."""
from pathlib import Path
import urllib.request,zipfile,io,hashlib,json
P=Path.cwd();D=P/'sources/research/realism-v6';D.mkdir(parents=True,exist_ok=True)
url='https://renderpeople.com/sample/free/renderpeople_free_rigged_people_FBX.zip'
archive=D/'renderpeople-free-rigged-fbx.zip'
if not archive.exists():urllib.request.urlretrieve(url,archive)
target=D/'renderpeople/eric';target.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive) as outer:
 with zipfile.ZipFile(io.BytesIO(outer.read('rp_eric_rigged_001_FBX.zip'))) as inner:
  for name in inner.namelist():
   if name=='rp_eric_rigged_001_zup_t.fbx' or name.startswith('tex/') or name=='rp_eric_rigged_001_A.jpg':
    dest=(target/name).resolve()
    if not dest.is_relative_to(target.resolve()):raise ValueError('Unsafe archive path')
    if not name.endswith('/'):
     dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(inner.read(name))
(D/'download.json').write_text(json.dumps({'url':url,'sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'source':'https://renderpeople.com/free-3d-people/','terms':'https://renderpeople.com/general-terms-and-conditions/'},indent=2))
print('Eric scan downloaded to',target)
