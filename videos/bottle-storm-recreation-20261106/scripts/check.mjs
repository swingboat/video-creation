import {readFileSync, readdirSync, realpathSync, statSync, existsSync, writeFileSync, lstatSync} from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=realpathSync(process.cwd());
const timeline=JSON.parse(readFileSync('docs/timeline.json','utf8'));
const frameCount=timeline.frames;
const duration=timeline.duration;
const bunny=timeline.version==='bunny-artist';
const picture=timeline.picture?'public/'+timeline.picture:bunny?'public/bunny-artist-picture.mp4':'public/bottle-storm-picture.mp4';
const finalVideo=timeline.final_video??(bunny?'outputs/bottle-storm-bunny-20s.mp4':'outputs/bottle-storm-14s.mp4');
const errors=[];
const report={project:root,isolated:true,externalTools:['Blender','FFmpeg','system Chrome'],checks:[]};
const excluded=new Set(['node_modules','.venv','.cache','.git']);
const walk=(dir)=>readdirSync(dir).flatMap(name=>{
 const p=path.join(dir,name);
 if(lstatSync(p).isSymbolicLink()){errors.push('Unexpected symlink: '+p);return [];}
 if(statSync(p).isDirectory())return excluded.has(name)?[]:walk(p);
 return [p];
});
const files=walk(root);
for(const file of files.filter(p=>/\.(?:tsx?|m?js|py)$/.test(p))){
 const text=readFileSync(file,'utf8');
 if(/videos\/(?!bottle-storm-recreation-20261106)[A-Za-z0-9_-]+\//.test(text))errors.push('Cross-video path: '+file);
 for(const match of text.matchAll(/(?:from\s*|import\s*)["'](\.[^"']+)["']/g)){
  const resolved=path.resolve(path.dirname(file),match[1]);
  if(!resolved.startsWith(root+path.sep))errors.push('Escaping import '+match[1]);
 }
}
if(timeline.fish_revision){
 const p='outputs/checks/fish/motion-audit.json';
 const audit=existsSync(p)?JSON.parse(readFileSync(p,'utf8')):null;
 const hash=createHash('sha256').update(readFileSync('public/bottle-storm.blend')).digest('hex');
 if(!audit?.passed||audit.blend_sha256!==hash)errors.push('Fish audit failed or does not match current blend');
}
const pkg=JSON.parse(readFileSync('package.json','utf8'));
if(bunny){
 const p='outputs/checks/bunny/contact-audit.json';
 if(!existsSync(p)||!JSON.parse(readFileSync(p,'utf8')).passed)errors.push('Rabbit contact audit failed or missing');
}
if(existsSync('outputs/checks/scene-audit.json')&&existsSync('public/bottle-storm.blend')){
 const audit=JSON.parse(readFileSync('outputs/checks/scene-audit.json','utf8'));
 const digest=createHash('sha256').update(readFileSync('public/bottle-storm.blend')).digest('hex');
 const pass=audit.passed&&audit.blend_sha256===digest;
 report.checks.push({name:'Native Blender geometry and dependency audit',pass});
 if(!pass)errors.push('Scene audit failed or does not match current blend');
}else errors.push('Scene audit missing');
for(const [name,version] of Object.entries(pkg.dependencies)){
 if(!/^\d+\.\d+\.\d+$/.test(version))errors.push('Unpinned dependency: '+name);
}
const ts=spawnSync(path.join(root,'node_modules/.bin/tsc'),['--noEmit'],{encoding:'utf8'});
report.checks.push({name:'TypeScript',pass:ts.status===0,output:ts.stdout+ts.stderr});
if(ts.status!==0)errors.push('TypeScript check failed');
for(const file of ['public/bottle-storm.blend',picture,'public/storm-soundscape.wav',finalVideo]){
 if(!existsSync(file)){errors.push('Missing '+file);continue;}
 if(file.endsWith('.mp4')){
  const r=spawnSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file],{encoding:'utf8'});
  const info=JSON.parse(r.stdout);const video=info.streams.find(s=>s.codec_type==='video');
  const valid=video?.width===1280&&video?.height===720&&video?.r_frame_rate==='24/1'&&Math.abs(Number(info.format.duration)-duration)<.08;
  report.checks.push({name:file,pass:valid,video,format:info.format});
  if(!valid)errors.push('Media format mismatch: '+file);
  if(file.startsWith('outputs/')&&!info.streams.some(s=>s.codec_type==='audio'))errors.push('Final audio missing');
 }
}
const frameDir=timeline.frame_dir??(bunny?'outputs/frames-bunny':'outputs/frames');
const frames=existsSync(frameDir)?readdirSync(frameDir).filter(n=>/^frame_\d{4}\.png$/.test(n)):[];
const renderReport=existsSync('outputs/checks/render-final.json')?JSON.parse(readFileSync('outputs/checks/render-final.json','utf8')):null;
const nativeHash=createHash('sha256').update(readFileSync('public/bottle-storm.blend')).digest('hex');
const renderSourceValid=!timeline.fish_revision||(renderReport?.blend_sha256===nativeHash&&renderReport?.frame_dir===frameDir&&renderReport?.frames?.length===frameCount);
const frameCheck=(frames.length===frameCount||(frames.length===0&&!!renderReport))&&renderSourceValid;
report.checks.push({name:'Cycles frame sequence',pass:frameCheck,count:frames.length,note:frames.length===0?'Intermediate PNG sequence omitted from portable package.':''});
if(!frameCheck)errors.push('Incomplete Cycles frame sequence');
report.errors=errors;report.passed=errors.length===0;
writeFileSync('outputs/checks/final-check.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,errors,frames:frames.length},null,2));
process.exit(report.passed?0:1);
