import {bundle} from '@remotion/bundler';
import {getCompositions,renderStill,renderMedia} from '@remotion/renderer';
import {readFile,writeFile,mkdir,readdir,realpath,lstat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const root=fileURLToPath(new URL('../',import.meta.url));process.chdir(root);
const project=JSON.parse(await readFile('project.json','utf8'));
const spec=JSON.parse(await readFile('package.json','utf8'));
await mkdir('.cache/tmp',{recursive:true});await mkdir('outputs/checks',{recursive:true});
process.env.TMPDIR=process.env.TMP=process.env.TEMP=path.join(root,'.cache/tmp');
process.env.NODE_COMPILE_CACHE=path.join(root,'.cache/node-compile-cache');
const inside=p=>p===path.resolve(root)||p.startsWith(path.resolve(root)+path.sep);
const packages={};
for(const name of Object.keys({...spec.dependencies,...spec.devDependencies})){
 const resolved=await realpath(path.join(root,'node_modules',name,'package.json'));assert.ok(inside(resolved),`${name} 必须安装在本目录`);
 packages[name]=resolved;
}
async function walk(dir){const files=[];for(const e of await readdir(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isSymbolicLink())assert.ok(inside(await realpath(p)),`禁止目录外链接 ${p}`);else if(e.isDirectory())files.push(...await walk(p));else files.push(p);}return files;}
for(const file of await walk(path.join(root,'src'))){const text=await readFile(file,'utf8');for(const m of text.matchAll(/(?:from\s*|import\s*)['"]([^'"]+)['"]/g)){
 const target=m[1];if(target.startsWith('.')){const resolved=path.resolve(path.dirname(file),target);assert.ok(inside(resolved),`禁止目录外导入 ${file}`);
 let exists=false;for(const ext of ['','.ts','.tsx','.js','/index.ts','/index.tsx']){try{if((await lstat(resolved+ext)).isFile()){assert.ok(inside(await realpath(resolved+ext)));exists=true;break;}}catch{}}
 assert.ok(exists,`缺少本地组件 ${target}`);
 }else{assert.ok(inside(await realpath(fileURLToPath(import.meta.resolve(target)))),`外部包必须本地安装 ${target}`);}
}}
for(const file of await walk(path.join(root,'public')))assert.ok(inside(await realpath(file)));
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts'),outDir:path.join(root,'.cache/isolation-bundle')});
const chromiumOptions=project.gl?{gl:project.gl}:{};
const compositions=await getCompositions(serveUrl,{chromiumOptions});const composition=compositions.find(c=>c.id===project.id);
assert.ok(composition);assert.deepEqual([composition.width,composition.height,composition.fps,composition.durationInFrames],[project.width,project.height,project.fps,project.frames]);
const image=path.join(root,'outputs/checks/isolated-preview.png');
await renderStill({serveUrl,composition,frame:project.reviewFrame,output:image,imageFormat:'png',chromiumOptions,logLevel:'error'});
const video=path.join(root,'outputs/checks/isolation-sample.mp4');
await renderMedia({serveUrl,composition,frameRange:[project.reviewFrame,project.reviewFrame+29],outputLocation:video,codec:'h264',audioCodec:'aac',pixelFormat:'yuv420p',concurrency:2,chromiumOptions,logLevel:'error'});
await writeFile('outputs/checks/isolation-report.json',JSON.stringify({project:project.id,ownDependencies:packages,importsStayWithinProject:true,localAssets:true,composition,registeredCompositions:compositions.map(c=>c.id),renderedFrame:project.reviewFrame,sampleFrames:30,sampleIsFullVideo:false,passed:true},null,2));
console.log(`PASS ${project.id}: 本地独立依赖、导入、素材、类型检查、构建、关键帧、30 帧 H.264 导出`);
