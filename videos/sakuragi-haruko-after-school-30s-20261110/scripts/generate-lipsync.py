"""Generate an audio-driven candidate, preserving every prior take."""
import project_env
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('scene')
p.add_argument('--take', default='v1')
p.add_argument('--seed', type=int, default=11210)
p.add_argument('--frames', type=int, default=97)
p.add_argument('--anchors', help='Project-relative JSON list of extra image anchors')
p.add_argument('--inputs-dir', default='public/lipsync/inputs', help='Use a new local input directory when changing dialogue')
a = p.parse_args()
for part in (a.scene, a.take):
    if not part.replace('-', '').replace('_', '').isalnum():
        raise SystemExit('Use a simple scene/take identifier')
inputs=ROOT/a.inputs_dir
assert inputs.resolve().is_relative_to(ROOT)
image = inputs / f'{a.scene}.png'
audio = inputs / f'{a.scene}.wav'
prompt_path = ROOT / f'docs/lipsync/{a.scene}-{a.take}-prompt.txt'
target = ROOT / f'public/lipsync/candidates/{a.scene}-{a.take}.mp4'
metadata = ROOT / f'outputs/checks/lipsync/{a.scene}-{a.take}-generation.json'
if target.exists():
    raise SystemExit('Candidate exists; select a new take.')
prompt = prompt_path.read_text().strip()
anchors=[]
if a.anchors:
    anchor_path=ROOT/a.anchors
    assert anchor_path.resolve().is_relative_to(ROOT)
    anchors=json.loads(anchor_path.read_text())
    for anchor in anchors:
        path=ROOT/anchor['image'];assert path.resolve().is_relative_to(ROOT) and path.is_file()
record = {'scene': a.scene, 'take': a.take, 'frames': a.frames, 'fps': 24,
          'width': 1024, 'height': 576, 'seed': a.seed,
          'pipeline': 'A2VidDistilledPipeline; LTX-2.3 q4; frozen source audio in both stages',
          'reference': str(image.relative_to(ROOT)),
          'audio': str(audio.relative_to(ROOT)), 'prompt': prompt,
          'inputs_sha256': {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
                            for f in (image, audio, prompt_path)},
          'output': str(target.relative_to(ROOT))}
if anchors:
    record['anchors']=anchors
    for anchor in anchors:
        file=ROOT/anchor['image'];record['inputs_sha256'][anchor['image']]=hashlib.sha256(file.read_bytes()).hexdigest()
metadata.write_text(json.dumps(record, ensure_ascii=False, indent=2))
cmd = [sys.executable, '-u', 'scripts/ltx-entry.py', 'a2v', '--distilled',
       '--model', str(ROOT / '.cache/models/ltx-q4'),
       '--gemma', str(ROOT / '.cache/models/gemma-q4'), '--prompt', prompt,
       '--image', str(image), '0', '1.0', '--audio', str(audio),
       '--frames', str(a.frames), '--width', '1024', '--height', '576',
       '--frame-rate', '24', '--seed', str(a.seed), '--low-ram', '--output', str(target)]
for anchor in anchors:
    cmd+=['--image',str(ROOT/anchor['image']),str(anchor['frame']),str(anchor['strength']),anchor.get('binding','guide')]
start = time.monotonic()
result = subprocess.run(cmd, cwd=ROOT, env=os.environ)
record.update(exit_code=result.returncode, wall_seconds=round(time.monotonic()-start, 2),
              output_exists=target.exists())
metadata.write_text(json.dumps(record, ensure_ascii=False, indent=2))
print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
raise SystemExit(result.returncode)
