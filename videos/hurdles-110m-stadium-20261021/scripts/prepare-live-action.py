"""Recreate the embedded film from the original authorized Pexels asset."""
from pathlib import Path
import os
import subprocess
import urllib.request

root = Path(__file__).resolve().parents[1]
os.chdir(root)
tmp = root / '.cache/tmp'
tmp.mkdir(parents=True, exist_ok=True)
os.environ.update(TMPDIR=str(tmp), TMP=str(tmp), TEMP=str(tmp))
source = root / 'sources/live-action/hurdle-30997018-original.mp4'
source.parent.mkdir(parents=True, exist_ok=True)
if not source.exists():
    urllib.request.urlretrieve(
        'https://videos.pexels.com/video-files/30997018/13249548_1080_1920_28fps.mp4',
        source,
    )
assets = root / 'public/assets/live-action'
assets.mkdir(parents=True, exist_ok=True)

def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', *map(str, args), '-y'], check=True)

ffmpeg('-ss', 6.15, '-i', source, '-t', 6.2, '-an', '-vf', 'fps=30',
       '-c:v', 'libx264', '-preset', 'medium', '-crf', 18, '-pix_fmt', 'yuv420p',
       '-movflags', '+faststart', assets / 'hurdle-training.mp4')
for name, time in [('poster', 5.47), ('approach', 5.10), ('flight', 5.47), ('landing', 5.80)]:
    ffmpeg('-ss', time, '-i', assets / 'hurdle-training.mp4', '-frames:v', 1,
           '-q:v', 2, assets / f'{name}.jpg')
print('Prepared 1080 × 1920 real footage, 6.20 seconds; no synthetic motion or audio.')
