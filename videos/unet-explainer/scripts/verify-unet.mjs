import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const root=fileURLToPath(new URL('../',import.meta.url));process.chdir(root);
const exec=promisify(execFile);
const run=(tool,args)=>exec(process.execPath,['scripts/remotion.mjs',tool,...args],{cwd:root,maxBuffer:8*1024*1024});
const file='outputs/unet-explainer.mp4';
await mkdir('outputs/checks',{recursive:true});
const timeline=JSON.parse(await readFile('outputs/timeline.json','utf8'));
const {stdout}=await run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file]);
const probe=JSON.parse(stdout);const video=probe.streams.find(s=>s.codec_type==='video');const audio=probe.streams.find(s=>s.codec_type==='audio');
assert.equal(video.codec_name,'h264');assert.equal(video.width,1920);assert.equal(video.height,1080);
assert.equal(video.avg_frame_rate,'30/1');assert.equal(video.pix_fmt,'yuv420p');assert.equal(Number(video.nb_frames),timeline.durationFrames);
assert.equal(audio.codec_name,'aac');assert.equal(Number(audio.sample_rate),48000);
assert.ok(Math.abs(Number(probe.format.duration)-timeline.durationFrames/30)<0.1);
const srt=await readFile('outputs/unet-explainer.srt','utf8');
const toSec=(h,m,s,ms)=>Number(h)*3600+Number(m)*60+Number(s)+Number(ms)/1000;
let previous=0,count=0;
for(const match of srt.matchAll(/(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})/g)){
 const start=toSec(...match.slice(1,5)),end=toSec(...match.slice(5,9));assert.ok(start>=previous&&end>start&&end<=Number(probe.format.duration));previous=end;count++;
}
assert.equal(count,32);
await run('ffmpeg',['-v','error','-i',file,'-map','0:v:0','-map','0:a:0','-c:v','rawvideo','-c:a','pcm_s16le','-f','null','-']);
await run('ffmpeg',['-v','error','-y','-i',file,'-vn','-ac','1','-ar','48000','-c:a','pcm_s16le','.cache/unet-decoded.wav']);
const wav=await readFile('.cache/unet-decoded.wav');let pcm;
for(let offset=12;offset+8<wav.length;){const size=wav.readUInt32LE(offset+4);if(wav.toString('ascii',offset,offset+4)==='data'){pcm=wav.subarray(offset+8,offset+8+size);break;}offset+=8+size+(size%2);}
assert.ok(pcm,'解码 WAV 应包含 PCM 数据');let sum=0,peak=0;
for(let i=0;i<pcm.length;i+=2){const sample=pcm.readInt16LE(i)/32768;sum+=sample*sample;peak=Math.max(peak,Math.abs(sample));}
const meanVolumeDb=20*Math.log10(Math.sqrt(sum/(pcm.length/2)));const maxVolumeDb=20*Math.log10(peak);
assert.ok(peak>0.1&&peak<1,'配音应存在且无满幅削波');
const samples=[['opening',440],['concat-before',3057],['concat-after',3454],['training',4111],['ending',4683]];
for(const[label,frame]of samples){await run('ffmpeg',['-v','error','-y','-ss',String(frame/30),'-i',file,'-frames:v','1',`outputs/checks/mp4-${label}.png`]);}
const report={file,video:{codec:video.codec_name,width:video.width,height:video.height,fps:video.avg_frame_rate,pixelFormat:video.pix_fmt,frames:Number(video.nb_frames)},audio:{codec:audio.codec_name,sampleRate:Number(audio.sample_rate),channels:audio.channels,meanVolumeDb,maxVolumeDb,peak},durationSeconds:Number(probe.format.duration),fullVideoAndAudioDecodePassed:true,subtitleCount:count,subtitleLastEndSeconds:previous,subtitleRangesValid:true,extractedFrames:samples};
await writeFile('outputs/checks/final-media-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
