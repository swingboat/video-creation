from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
base='https://raw.githubusercontent.com/davidhckh/portfolio-2025/f331fe16f507d52b60348fee73d56ab7ec330e56/'
assets=['models/avatar.glb','models/room.glb','models/contact.glb','models/lab.glb','textures/room.webp','textures/contact.webp','textures/head.webp','textures/face-spritesheet.png','textures/matcap-black.webp','textures/matcap-gray.webp','textures/matcap-skin.webp','textures/matcap-white.webp','textures/desktops.webp','textures/room-shadow.webp','textures/contact-shadow.webp','thumbnails/cubewar.webp','thumbnails/quibbo.webp','thumbnails/sharkie.webp','thumbnails/particles.webp']
sources=['src/three/shaders/avatar-face/vertex.glsl','src/three/shaders/avatar-face/fragment.glsl','src/three/shaders/avatar-head/vertex.glsl','src/three/shaders/avatar-head/fragment.glsl','src/three/shaders/avatar-matcap/vertex.glsl','src/three/shaders/avatar-matcap/fragment.glsl','src/animations/waypoints.ts','src/three/objects/room/shadow.ts','src/three/objects/avatar/hologram.ts','src/three/objects/lab/base.ts','src/utils/resources.ts']
def fetch(pair):
 p,d=pair;dest=Path(d);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(urlopen(base+p,timeout=60).read());return str(dest)+' '+str(dest.stat().st_size)
pairs=[('src/assets/'+a,'public/upstream/'+a) for a in assets]+[(p,'docs/research/source/'+p) for p in sources]+[('public/fonts/urbanist-900.woff2','public/fonts/urbanist-900.woff2'),('public/fonts/urbanist-700.woff2','public/fonts/urbanist-700.woff2'),('public/fonts/urbanist-400.woff2','public/fonts/urbanist-400.woff2')]
with ThreadPoolExecutor(max_workers=8) as ex:
 for res in ex.map(fetch,pairs):print(res,flush=True)
