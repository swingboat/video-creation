import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
const root=process.cwd(),html=fs.readFileSync('outputs/hurdle-character-v6.html','utf8'),report={images:{}};
assert.equal(html,fs.readFileSync('public/hurdle-character-v6.html','utf8'));assert(!html.includes('{{'));assert(!/<script[^>]+src=|<link[^>]+stylesheet/i.test(html));
for(const name of ['baseline','portrait','half','full']){
 const png=fs.readFileSync(`outputs/realism-v6/${name}.png`),jpg=fs.readFileSync(`outputs/realism-v6/${name}.jpg`);assert.equal(png.readUInt32BE(16),1200);assert.equal(png.readUInt32BE(20),1500);assert.equal(jpg.readUInt16BE(0),0xffd8);assert(html.includes(jpg.toString('base64')));
 const scene=`outputs/realism-v6/${name==='baseline'?'baseline':'athlete-lookdev'}.blend`;assert(fs.statSync(`outputs/realism-v6/${name}.png`).mtimeMs>fs.statSync(scene).mtimeMs,'Stale render: '+name);
 report.images[name]={width:1200,height:1500,jpegBytes:jpg.length,sha256:createHash('sha256').update(jpg).digest('hex')};
}
const source=fs.readFileSync('scripts/build-realism-v6.py','utf8');assert(source.includes("P/'outputs/offline/hurdles-cycles.blend'"));assert(!source.includes('/Users/'));assert(fs.statSync('outputs/realism-v6/athlete-lookdev.blend').size>1e6);
report.standalone=true;report.originalV5Present=fs.existsSync('outputs/hurdle-110-code.mp4');report.phase='character-static-review';report.motionValidated=false;report.photorealismAccepted=false;report.htmlBytes=Buffer.byteLength(html);
fs.writeFileSync(path.join(root,'outputs/checks/realism-v6/static-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
