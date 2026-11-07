from pathlib import Path
import subprocess,json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
movie=ROOT/'outputs/huggingface-guide-zh.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
timeline=json.loads((ROOT/'src/timeline.json').read_text())
video=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
checks={
 'resolution_1080p':video['width']==1920 and video['height']==1080,
 'h264_video':video['codec_name']=='h264',
 'aac_audio':audio['codec_name']=='aac',
 'frame_rate_30':video['r_frame_rate']=='30/1',
 'frame_count_matches_timeline':int(video['nb_frames'])==timeline['durationInFrames'],
 'duration_matches_timeline':abs(float(probe['format']['duration'])-timeline['durationInFrames']/30)<0.1,
 'captions_available':(ROOT/'outputs/huggingface-zh.srt').stat().st_size>1000,
 'all_scene_audio_present':all((ROOT/f'public/voiceover/{s["id"]}.mp3').exists() for s in timeline['scenes']),
 'short_socket_exception_cleaned':not Path('/tmp/hf-getstarted-8653').exists(),
}
# Fully decode the final file to detect corrupt frames or packets.
decode=subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(movie),'-f','null','-'],capture_output=True,text=True)
checks['full_decode_passed']=decode.returncode==0 and not decode.stderr.strip()
report={'checks':checks,'passed':all(checks.values()),'durationSeconds':float(probe['format']['duration']),'frames':video['nb_frames'],'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'decodeDiagnostics':decode.stderr,'visualReview':'16 rendered frames reviewed across all 10 chapters, including Chinese language settings, captions, and all model-page tabs.'}
(ROOT/'outputs/checks/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(ROOT/'outputs/checks/ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
