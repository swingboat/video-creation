import {bundle} from '@remotion/bundler';
import {selectComposition, renderStill} from '@remotion/renderer';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url)); process.chdir(root);
await mkdir('.cache/tmp',{recursive:true}); process.env.TMPDIR=process.env.TMP=process.env.TEMP=path.join(root,'.cache/tmp');
const timeline=JSON.parse(await readFile('outputs/timeline.json','utf8'));
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts'),outDir:path.join(root,'.cache/unet-final-bundle')});
const composition=await selectComposition({serveUrl,id:'UnetExplainer'});
assert.deepEqual([composition.width,composition.height,composition.fps,composition.durationInFrames],[1920,1080,30,timeline.durationFrames]);
const at=(scene,p)=>timeline.scenes[scene].startFrame+Math.round((timeline.scenes[scene].durationFrames-1)*p);
const cue=(scene,index,ratio=0.5)=>{
  const s=timeline.scenes[scene];const c=s.captions[index];
  return s.startFrame+Math.floor((c.startMs+(c.endMs-c.startMs)*ratio)/1000*timeline.fps);
};
const jobs=[['opening',cue(0,3)],['whole-u',at(1,0.83)],['encoder',cue(2,2)],['decoder',cue(3,3)],
  ['concat-before',cue(4,2)],['concat-after',cue(4,4,0.99)],['concat-fused',cue(4,5,0.99)],
  ['training',at(5,0.66)],['inference',cue(5,4)],['ending',cue(6,3)],['determinism-repeat',cue(4,4,0.99)]];
const results=[];
for(const[label,frame]of jobs){
  const output=path.join(root,`outputs/checks/${label}.png`);
  await renderStill({serveUrl,composition,frame,output,imageFormat:'png',logLevel:'error'});
  const bytes=await readFile(output); assert.equal(bytes.readUInt32BE(16),1920);assert.equal(bytes.readUInt32BE(20),1080);
  results.push({label,frame,output,sha256:createHash('sha256').update(bytes).digest('hex')}); console.log(`PASS ${label} / ${frame}`);
}
assert.equal(results[5].sha256,results[10].sha256,'重复帧渲染应完全一致');
for(const[s,scene]of timeline.scenes.entries()){
  let last=0;
  for(const c of scene.captions){assert.ok(c.startMs>=last&&c.endMs>c.startMs); assert.ok(c.endMs<=scene.durationFrames/timeline.fps*1000);
    assert.ok(c.text.split('\n').length<=2);last=c.endMs;}
  assert.equal(scene.startFrame,timeline.scenes.slice(0,s).reduce((n,x)=>n+x.durationFrames,0));
}
const srt=await readFile('outputs/unet-explainer.srt','utf8'); assert.equal((srt.match(/-->/g)||[]).length,32);
await writeFile('outputs/checks/keyframes-report.json',JSON.stringify({composition:{width:composition.width,height:composition.height,fps:composition.fps,durationInFrames:composition.durationInFrames},results,deterministic:true,captionCount:32,subtitleTimeRangeValid:true},null,2));
console.log('PASS: 构建、Composition 参数、关键帧、字幕范围、重复帧一致性。');
