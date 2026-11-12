import bpy,sys,time,json,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['preview']
mode=args[0];sc=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 if os.environ.get('RUKAWA_CPU')=='1':raise RuntimeError('CPU continuation selected')
 prefs.compute_device_type='METAL';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='METAL'
 if any(d.use for d in prefs.devices):sc.cycles.device='GPU'
except Exception as e:
 print(e,flush=True);sc.cycles.device='CPU'
 if hasattr(sc.cycles,'denoising_use_gpu'):sc.cycles.denoising_use_gpu=False
sc.render.use_persistent_data=True;sc.render.threads_mode='FIXED';sc.render.threads=8
if hasattr(sc.cycles,'denoising_use_gpu'):sc.cycles.denoising_use_gpu=False
sc.render.resolution_percentage=65 if mode=='preview' else 100
sc.cycles.samples=12 if mode=='preview' else 24
sc.cycles.adaptive_threshold=.07 if mode=='preview' else .045
shard=next((int(a.split('=')[1]) for a in args if a.startswith('--shard=')),None)
frames=[int(a) for a in args[1:]] if len(args)>1 and shard is None else list(range(1,481)) if mode=='final' else [1,103,180,214,263,321,336,422]
if shard is not None:frames=[f for f in frames if (f-1)%2==shard]
folder=ROOT/('outputs/frames' if mode=='final' else 'outputs/checks/preview');folder.mkdir(exist_ok=True,parents=True)
hash=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
reportfile=ROOT/'outputs/checks'/('render-'+mode+('-shard'+str(shard) if shard is not None else '')+'.json')
manifest=folder/'scene-manifest.json'
if mode=='final':
 if manifest.exists() and (json.loads(manifest.read_text())['scene_sha256']!=hash or json.loads(manifest.read_text())['samples']!=sc.cycles.samples):raise RuntimeError('Scene changed: archive frame directory before rendering')
 manifest.write_text(json.dumps({'scene_sha256':hash,'samples':sc.cycles.samples}))
report={'device':sc.cycles.device,'scene_sha256':hash,'samples':sc.cycles.samples,'mode':mode,'frames':[]}
if reportfile.exists():
 old=json.loads(reportfile.read_text())
 if mode=='final' and any(folder.glob('frame_*.png')) and old['scene_sha256']!=hash:raise RuntimeError('Scene changed: archive old frames before rendering')
for f in frames:
 path=folder/('frame_%04d.png'%f)
 if mode=='final' and path.exists() and path.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
 sc.frame_set(f);sc.render.filepath=str(path);start=time.monotonic();bpy.ops.render.render(write_still=True)
 report['frames'].append({'frame':f,'seconds':round(time.monotonic()-start,2)});reportfile.write_text(json.dumps(report,indent=2));print('DONE_FRAME',f,flush=True)
