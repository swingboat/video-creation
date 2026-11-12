import time,subprocess
from pathlib import Path
r=Path(__file__).resolve().parents[1]
while True:
 frames=list((r/'outputs/frames').glob('frame_*.png'))
 if len(frames)==480:
  try:
   if all(p.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82' for p in frames):break
  except OSError:pass
 time.sleep(5)
subprocess.run(['node','scripts/run.mjs','finish'],cwd=r,check=True)
