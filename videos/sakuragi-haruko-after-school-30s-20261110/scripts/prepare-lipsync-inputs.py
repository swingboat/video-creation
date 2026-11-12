"""Create local first-frame anchors and frame-accurate isolated dialogue tracks."""
import project_env
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scenes',nargs='*')
p.add_argument('--inputs-dir',default='public/lipsync/inputs');a=p.parse_args()
layout={'opening':(0,97),'haruko':(96,97),'shy':(192,89),'cheer':(434,97),'resolve':(528,97),'ending':(624,65)}
dialogue=json.loads((ROOT/'docs/voiceover/dialogue.json').read_text())
out=ROOT/a.inputs_dir;assert out.resolve().is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
manifest={}
for line in dialogue['lines']:
    scene=line['id']
    if a.scenes and scene not in a.scenes:continue
    start,frames=layout[scene];offset=(line['start_frame']-start)/24
    image=out/f'{scene}.png';audio=out/f'{scene}.wav'
    source=ROOT/f'public/video/{scene}.mp4'
    voice=ROOT/f'public/audio/voices/{scene}.wav'
    manifest[scene]={'frames':frames,'fps':24,'audio_start_frame':line['start_frame']-start,'text':line['text'],'source':str(source.relative_to(ROOT)),'voice':str(voice.relative_to(ROOT))}
    if image.exists() or audio.exists():
        assert image.exists() and audio.exists(),'Incomplete inputs; restore or use a new candidate folder.'
        print('Already prepared; preserving',scene);continue
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vf','scale=1024:576','-frames:v','1','-update','1',str(image)],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(voice),'-af',f'adelay={offset*1000:.9f}:all=1,apad,atrim=duration={frames/24:.9f}','-ar','48000','-ac','2',str(audio)],check=True)
    print('Prepared',scene)
dest=ROOT/'docs/lipsync/input-layout.json'
previous=json.loads(dest.read_text()) if dest.exists() else {}
dest.write_text(json.dumps({**previous,**manifest},ensure_ascii=False,indent=2))
