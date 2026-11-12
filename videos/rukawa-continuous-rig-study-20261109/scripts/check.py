from pathlib import Path
import subprocess,json,re,hashlib
R=Path(__file__).resolve().parents[1]
def call(args):return subprocess.run(args,cwd=R,check=True,capture_output=True,text=True).stdout
call(['node_modules/.bin/tsc','--noEmit'])
# Check authored runtime source paths. Normal system executables are permitted.
issues=[]
for folder in ['src','scripts']:
 for p in (R/folder).rglob('*'):
  if p.name=='check.py':continue
  if not p.is_file() or p.suffix not in ['.ts','.tsx','.mjs','.py']:continue
  s=p.read_text()
  for term in ['/videos/','/Users/','hurdles-110m','rukawa-anime-2d','rukawa-buzzer-beater','node_modules/../']:
   if term in s:issues.append([str(p.relative_to(R)),term])
  for ref in re.findall(r'(?:from\s*|import\s*\()[\'\"]([^\'\"]+)',s):
   if ref.startswith('.') and not (p.parent/ref).resolve().is_relative_to(R):issues.append([str(p.relative_to(R)),ref])
for folder in ['src','public','scripts']:
 for p in (R/folder).rglob('*'):
  if p.is_symlink():issues.append([str(p.relative_to(R)),'symlink'])
assert not issues,issues
out=R/'outputs/continuous-rig-study-5s.mp4'
meta=json.loads(call(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
v=next(x for x in meta['streams'] if x['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1280,720,'30/1',150)
assert abs(float(meta['format']['duration'])-5)<.02
call(['ffmpeg','-v','error','-i',str(out),'-f','null','-'])
a=json.loads((R/'outputs/checks/rig-audit.json').read_text())
assert a['frames']==150 and a['actors']==12
assert a['max_local_rotation_step_degrees']<30,a['max_local_rotation_step_degrees']
assert a['minimum_adjacent_quaternion_dot']>0
assert a['max_abs_planted_sole_bottom_z_m']<.001
assert not a['asset_paths']['linked_libraries']
for font in a['asset_paths']['fonts']:assert font['packed'] or font['filepath'].startswith('//')
for im in a['asset_paths']['images']:assert im['packed'] or not im['filepath']
for key in ['palm_target_error_max_m','ankle_target_error_max_m','segment_joint_gap_max_m','planted_shoe_vertex_step_max_m']:assert a[key]<.001,(key,a[key])
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'public/models/human-base.glb',R/'public/continuous-rig.blend',out]}
report={'typecheck':'pass','runtime_path_isolation':'pass','symlinks_in_authored_assets':0,'video':{'dimensions':'1280x720','fps':30,'frames':150,'duration':5,'decode':'pass'},'rig_contact_checks':'pass','quality_scope':'Contact checks do not certify anime likeness, natural acting or final 20s completion.','sha256':files}
(R/'outputs/checks/project-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
