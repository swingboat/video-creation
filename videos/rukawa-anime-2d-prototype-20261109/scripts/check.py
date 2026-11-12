import subprocess,json,wave,hashlib,struct,zlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];out=r/'outputs/rukawa-anime-sample-v2-5s.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(out)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1280,720);assert v['r_frame_rate']=='30/1';assert int(v['nb_frames'])==150
assert abs(float(probe['format']['duration'])-5)<.08
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-map','0:v','-f','framemd5','pipe:1'],text=True)
rows=[ln for ln in raw.splitlines() if not ln.startswith('#') and ln.strip()]
unique=len({ln.split(',')[-1].strip() for ln in rows});assert len(rows)==150 and unique>90
with wave.open(str(r/'public/soundscape.wav')) as w:assert w.getnframes()/w.getframerate()==5;assert w.getnchannels()==2
issues=[]
for folder in ['src','scripts']:
 for p in (r/folder).glob('*'):
  if not p.is_file() or p==Path(__file__).resolve():continue
  if p.suffix in ['.py','.tsx','.ts','.mjs']:
   s=p.read_text()
   if '/Users/huyin/' in s or 'buzzer-beater-20261109' in s:issues.append(str(p.relative_to(r)))
assert not issues
for p in r.joinpath('public').rglob('*'):assert not p.is_symlink()
# Inspect the actual sprite sheet header and nine cells using ffmpeg RGBA decoding.
p=r/'public/art/rukawa-poses-v2.png';b=p.read_bytes();w,h=struct.unpack('>II',b[16:24]);assert w==1254 and h==1254
pixels=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-pix_fmt','rgba','-f','rawvideo','pipe:1'])
counts=[0]*9
for y in range(h):
 for x in range(w):
  if pixels[(y*w+x)*4+3]>128:counts[(y//418)*3+x//418]+=1
assert min(counts)>5000
report={'passed':True,'duration':probe['format']['duration'],'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':len(rows),'unique_video_frames':unique,'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'sprite_sheet':[w,h],'pose_cell_opaque_pixels':counts,'external_runtime_path_issues':issues,'scope':'5-second limited-animation style and motion sample','release_seconds':1,'buzzer_seconds':1.18,'swish_seconds':3.35,'other_players_and_crowd':'five animated supporting players, three poses each; six staggered crowd sectors with two drawn gesture states per view'}
# Check actual decoded video pixels, not only authored layer metadata.
selected=[0,8,35,75,85]
cmd=['ffmpeg','-v','error','-i',str(out),'-vf','select='+ '+'.join('eq(n\\,'+str(n)+')' for n in selected),'-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
frames_raw=subprocess.check_output(cmd);stride=1280*720*3
assert len(frames_raw)==stride*len(selected)
frames=[frames_raw[i*stride:(i+1)*stride] for i in range(len(selected))]
def delta(a,b,rect):
 x,y,w,h=rect;total=0
 for yy in range(y,y+h):
  start=(yy*1280+x)*3;end=start+w*3
  total+=sum(abs(v-u) for u,v in zip(a[start:end],b[start:end]))
 return round(total/(w*h*3),4)
regions={'red_10':(510,300,200,240),'red_7':(735,295,95,195),'red_4':(1050,240,160,320),'white_6':(780,200,160,355),'white_5':(1000,310,230,280)}
changes={k:delta(frames[0],frames[2],v) for k,v in regions.items()};assert min(changes.values())>1,changes
court_crowd=delta(frames[0],frames[1],(440,120,72,75));assert court_crowd>1,court_crowd
hoop_crowd=delta(frames[3],frames[4],(580,560,100,110));assert hoop_crowd>1,hoop_crowd
wall=delta(frames[0],frames[2],(20,260,100,140));assert wall<1.5,wall
support=json.loads((r/'src/support-bounds.json').read_text());assert len(support)==5 and all(len(row)==3 for row in support)
assert min(pose['opaquePixels'] for row in support for pose in row)>5000
report['motion_regions_mean_rgb_delta']=changes
report['court_crowd_rgb_delta']=court_crowd;report['hoop_crowd_rgb_delta']=hoop_crowd;report['static_wall_rgb_delta']=wall
report['support_player_pose_cells']=15
(r/'outputs/checks/final-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
