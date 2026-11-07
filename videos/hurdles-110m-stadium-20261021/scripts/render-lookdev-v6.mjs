import fs from 'node:fs';import path from 'node:path';import {spawnSync} from 'node:child_process';
const root=process.cwd(),tmp=path.join(root,'.cache/tmp'),logs=path.join(root,'outputs/checks/realism-v6');fs.mkdirSync(logs,{recursive:true});
const env={...process.env,TMPDIR:tmp,TMP:tmp,TEMP:tmp,BLENDER_USER_RESOURCES:path.join(root,'.cache/blender')};
for(const kind of ['portrait','half','full','baseline']){
 console.log('Rendering',kind);const log=fs.openSync(path.join(logs,kind+'.log'),'w');
 const r=spawnSync(process.execPath,['scripts/run-realism-v6.mjs',kind,'64'],{cwd:root,env,stdio:['ignore',log,log]});fs.closeSync(log);if(r.status!==0)throw Error('Render failed: '+kind);
 const jpgLog=fs.openSync(path.join(logs,kind+'-jpeg.log'),'w');const encoded=spawnSync('ffmpeg',['-y','-i',`outputs/realism-v6/${kind}.png`,'-frames:v','1','-q:v','2','-update','1',`outputs/realism-v6/${kind}.jpg`],{cwd:root,env,stdio:['ignore',jpgLog,jpgLog]});fs.closeSync(jpgLog);if(encoded.status!==0)throw Error('JPEG conversion failed: '+kind);
}
console.log('All four character review images ready.');
