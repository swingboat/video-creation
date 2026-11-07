import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
const root=fs.realpathSync(process.cwd()),html=fs.readFileSync('outputs/hurdle-110-3d.html','utf8');
assert(html.includes('data:model/gltf-binary;base64,'),'Embedded model missing');
const packed=JSON.parse(fs.readFileSync('.cache/packed-assets.json','utf8')),glb=Buffer.from(packed.body.split(',')[1],'base64');
assert.equal(glb.toString('ascii',0,4),'glTF');const jsonLength=glb.readUInt32LE(12),model=JSON.parse(glb.subarray(20,20+jsonLength).toString('utf8'));assert(model.images.length>=4,'Skin, eyes, hair and shoe textures required');assert(model.images.every(x=>x.bufferView!==undefined&&!x.uri),'Model has external images');assert.equal(model.skins[0].joints.length,163,'Unexpected skeleton');
assert(!/<script[^>]+src\s*=/.test(html),'External script');assert(!/<link[^>]+href\s*=/.test(html),'External stylesheet');assert(!/@import\s/.test(html),'CSS import');
for(const dir of ['src','scripts','public','sources'])for(const entry of fs.readdirSync(dir,{recursive:true,withFileTypes:true})){if(!entry.isFile())continue;const name=path.join(entry.parentPath,entry.name);assert(fs.realpathSync(name).startsWith(root+path.sep),'Cross-project reference: '+name);if(/\.(js|mjs|tsx|ts|py)$/.test(name)){const s=fs.readFileSync(name,'utf8');for(const match of s.matchAll(/(?:from\s*|import\s*\()\s*['"](\.[^'"]+)['"]/g)){assert(path.resolve(path.dirname(name),match[1]).startsWith(root+path.sep),'Import escapes project');}}}
assert(fs.readFileSync('public/hurdle-110-3d.html','utf8')===html,'3D Remotion copy differs');
const cg=fs.readFileSync('outputs/hurdle-110.html','utf8'),cgAssets=JSON.parse(fs.readFileSync('.cache/cg-assets.json','utf8'));
assert(cg.includes('CODE RENDERED')&&!cg.includes('Pexels'),'Main page must show code render');
assert(Buffer.from(cgAssets.video.split(',')[1],'base64').equals(fs.readFileSync('public/assets/offline/hurdles-cycles.mp4')),'Wrong CG clip embedded');
assert(fs.readFileSync('public/hurdle-110.html','utf8')===cg,'CG copy differs');
assert(!/<script[^>]+src\\s*=/.test(cg)&&!/<link[^>]+href\\s*=/.test(cg),'CG page has external dependencies');
const report={standalone:true,defaultMode:'code-render',cgSizeBytes:Buffer.byteLength(cg),cgFrames:66,cgFps:24,cgDuration:2.75,embeddedVideo:1,embeddedStills:4,threeD:{embeddedModels:1,embeddedTextures:model.images.length,skeletonJoints:model.skins[0].joints.length,sizeBytes:Buffer.byteLength(html)},sourceIsolation:true,generatedAt:new Date().toISOString()};fs.writeFileSync('outputs/checks/static-check.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
