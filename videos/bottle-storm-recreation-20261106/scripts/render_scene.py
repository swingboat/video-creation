"""Render an existing self-contained .blend. All output and caches stay in this project."""
import bpy
import os
import sys
import json
import time
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'preview'
timeline=json.loads((ROOT/'docs/timeline.json').read_text())
count=timeline['frames']
is_bunny=timeline.get('version')=='bunny-artist'
scene.render.engine='BLENDER_WORKBENCH' if mode=='blocking' else 'CYCLES'
devices=[]
try:
    if mode=='blocking':raise RuntimeError('Workbench blocking: no Cycles device initialization needed')
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='METAL'
    prefs.get_devices()
    for device in prefs.devices:
        device.use=device.type=='METAL'
        devices.append({'name':device.name,'type':device.type,'enabled':device.use})
    if any(d['enabled'] for d in devices):scene.cycles.device='GPU'
except Exception as ex:print('GPU_SETUP',str(ex),flush=True)
print('RENDER_DEVICES',json.dumps(devices),flush=True)
scene.render.use_persistent_data=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_percentage=50 if mode in {'preview','blocking','fish-preview'} else 100
scene.cycles.samples=12 if mode in {'preview','fish-preview'} else 32
scene.cycles.adaptive_threshold=.10 if mode in {'preview','fish-preview'} else .035
if mode=='blocking':
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    bpy.data.objects['Bottle • solid optical shell'].hide_render=True
    bpy.data.objects['Ocean • closed volume and analytic waves'].hide_render=True
    scene.render.use_motion_blur=False
frames=list(range(1,145)) if mode=='fish-preview' else list(range(1,count+1)) if mode in {'final','blocking'} else [int(x) for x in args[1:]] or [1,73,193,313,409,469]
folder='outputs/checks/fish/preview' if mode=='fish-preview' else 'outputs/blocking-bunny' if mode=='blocking' else (timeline.get('frame_dir','outputs/frames-bunny') if mode=='final' and is_bunny else 'outputs/frames' if mode=='final' else 'outputs/checks/fish' if timeline.get('fish_revision') else 'outputs/checks/bunny')
(ROOT/folder).mkdir(parents=True,exist_ok=True)
scene_file=Path(bpy.data.filepath)
scene_hash=hashlib.sha256(scene_file.read_bytes()).hexdigest()
report={'blend_sha256':scene_hash,'frame_dir':folder,'mode':mode,'devices':devices,'frame_count':count,'samples':scene.cycles.samples,'frames':[]}
report_file=ROOT/'outputs/checks'/('render-'+mode+'.json')
old_records={}
if mode=='final' and list((ROOT/folder).glob('frame_*.png')) and not report_file.exists():
    raise RuntimeError('Existing frames have no render report. Archive them inside this video project before rendering.')
if report_file.exists():
    try:
        previous=json.loads(report_file.read_text());old_records={r['frame']:r for r in previous.get('frames',[])}
        existing=list((ROOT/folder).glob('frame_*.png')) if mode=='final' else []
        if existing:
            old_hash=previous.get('blend_sha256')
            if previous.get('samples')!=scene.cycles.samples or (old_hash and old_hash!=scene_hash) or (not old_hash and scene_file.stat().st_mtime>min(p.stat().st_mtime for p in existing)):
                raise RuntimeError('Scene changed since these frames were rendered. Archive this frame directory inside the video project before rendering again.')
    except (ValueError,KeyError):pass
for frame in frames:
    path=ROOT/folder/('frame_%04d.png'%frame)
    if mode in {'final','blocking'} and path.exists():
        with path.open('rb') as image_file:image_file.seek(-12,2);png_end=image_file.read()
        if png_end==b'\x00\x00\x00\x00IEND\xaeB`\x82':
            record=old_records.get(frame,{'frame':frame,'seconds':0,'path':str(path.relative_to(ROOT))}).copy();record['reused']=True
            report['frames'].append(record);report_file.write_text(json.dumps(report,indent=2));continue
    scene.frame_set(frame);scene.render.filepath=str(path)
    print('FRAME_START',frame,flush=True)
    started=time.monotonic();bpy.ops.render.render(write_still=True)
    elapsed=round(time.monotonic()-started,3)
    report['frames'].append({'frame':frame,'seconds':elapsed,'path':str(path.relative_to(ROOT))})
    report_file.write_text(json.dumps(report,indent=2))
    print('FRAME_DONE',frame,elapsed,flush=True)
print('RENDER_COMPLETE',mode,flush=True)
