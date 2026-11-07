import fs from 'node:fs';import path from 'node:path';import {spawnSync} from 'node:child_process';
const root=process.cwd(),tmp=path.join(root,'.cache/tmp'),logs=path.join(root,'outputs/checks/realism-v7');fs.mkdirSync(tmp,{recursive:true});fs.mkdirSync(logs,{recursive:true});
const env={...process.env,TMPDIR:tmp,TMP:tmp,TEMP:tmp,BLENDER_USER_RESOURCES:path.join(root,'.cache/blender')};
for(const kind of ['portrait','half','full','flex']){
 console.log('Rendering free candidate:',kind);const log=fs.openSync(path.join(logs,kind+'.log'),'w');
 const r=spawnSync(process.execPath,['scripts/run-free-v7.mjs',kind,'64'],{cwd:root,env,stdio:['ignore',log,log]});fs.closeSync(log);if(r.status!==0)throw Error('Render failed: '+kind);
 const jpeg=fs.openSync(path.join(logs,kind+'-jpeg.log'),'w');const j=spawnSync('ffmpeg',['-y','-i',`outputs/realism-v7/${kind}.png`,'-frames:v','1','-q:v','2','-update','1',`outputs/realism-v7/${kind}.jpg`],{cwd:root,env,stdio:['ignore',jpeg,jpeg]});fs.closeSync(jpeg);if(j.status!==0)throw Error('JPEG failed: '+kind);
}
console.log('Free complete character: four review stills rendered.');
