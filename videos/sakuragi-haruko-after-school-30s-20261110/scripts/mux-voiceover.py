"""Replace the current movie's audio while preserving its latest edited video."""
import project_env
from pathlib import Path
import subprocess,hashlib,json,os,shutil
ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'outputs/versions/sakuragi-haruko-30s-subtitles-only.mp4';new=ROOT/'outputs/sakuragi-haruko-30s.mp4';temp=ROOT/'.cache/tmp/voiced-movie.mp4'
def video_hash(file):return subprocess.check_output(['ffmpeg','-v','error','-i',str(file),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-'],text=True).strip()
# The current movie may contain reviewed lip-sync repairs. Never implicitly
# revert it to the older subtitles-only picture when updating the mix.
source=new if new.exists() else old
old_hash=video_hash(source)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-i',str(ROOT/'public/audio/dialogue-master.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','30','-movflags','+faststart',str(temp)],check=True,timeout=90)
os.replace(temp,new)
subprocess.run(['python3','scripts/final-audio.py'],cwd=ROOT,check=True)
new_hash=video_hash(new);assert old_hash==new_hash
voiced=ROOT/'outputs/sakuragi-haruko-30s-voiced.mp4';shutil.copy2(new,voiced)
shutil.copy2(new,ROOT/'outputs/sakuragi-haruko-30s-lipsync-v2.mp4')
(ROOT/'outputs/checks/voiceover/video-stream-preserved.json').write_text(json.dumps({'original':str(source.relative_to(ROOT)),'voiced':str(voiced.relative_to(ROOT)),'original_video_stream_hash':old_hash,'voiced_video_stream_hash':new_hash,'identical_video_packets':True,'duration':30},indent=2))
print(voiced)
