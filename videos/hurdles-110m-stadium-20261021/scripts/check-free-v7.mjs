import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
const root=process.cwd(),html=fs.readFileSync('outputs/hurdle-character-v7.html','utf8'),report={images:{}};
assert.equal(html,fs.readFileSync('public/hurdle-character-v7.html','utf8'));assert(!html.includes('{{'));assert(!/<script[^>]+src=|<link[^>]+stylesheet/i.test(html));
for(const kind of ['portrait','half','full','flex']){
 const file=`outputs/realism-v7/${kind}.png`,png=fs.readFileSync(file),jpg=fs.readFileSync(`outputs/realism-v7/${kind}.jpg`);
 assert.equal(png.readUInt32BE(16),1200);assert.equal(png.readUInt32BE(20),1500);assert.equal(jpg.readUInt16BE(0),0xffd8);assert(html.includes(jpg.toString('base64')));
 assert(fs.statSync(file).mtimeMs>fs.statSync('outputs/realism-v7/complete-free-athlete.blend').mtimeMs,'Stale render: '+kind);report.images[kind]={width:1200,height:1500,jpegBytes:jpg.length,sha256:createHash('sha256').update(jpg).digest('hex')};
}
const downloads=JSON.parse(fs.readFileSync('sources/research/realism-v7/rocketbox/download.json','utf8'));
for(const item of downloads){
 const real=fs.realpathSync(item.file);assert(real.startsWith(root+path.sep),'Asset outside this video');assert.equal(createHash('sha256').update(fs.readFileSync(real)).digest('hex'),item.sha256);
}
const source=fs.readFileSync('scripts/build-free-v7.py','utf8');assert(!source.includes('/Users/'));assert(source.includes('Sports_Male_04.fbx'));assert(fs.readFileSync('sources/research/realism-v7/rocketbox/LICENSE.md','utf8').includes('MIT License'));
assert(html.includes('真人感仍未通过'));assert(html.includes('不是跨栏动作'));
Object.assign(report,{standalone:true,htmlBytes:Buffer.byteLength(html),asset:'Microsoft Rocketbox Sports_Male_04',license:'MIT',cost:0,phase:'complete-free-character-static-and-rig-pose-review',motionValidated:false,photorealismAccepted:false,originalV5Present:fs.existsSync('outputs/hurdle-110-code.mp4')});
fs.writeFileSync('outputs/checks/realism-v7/static-check.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
