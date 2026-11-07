import fs from 'node:fs';import path from 'node:path';import{build}from'esbuild';
const project=process.cwd();for(const d of ['.cache','outputs','public'])fs.mkdirSync(path.join(project,d),{recursive:true});
function data(file,mime){return `data:${mime};base64,${fs.readFileSync(path.join(project,'public/assets',file)).toString('base64')}`;}
fs.writeFileSync('.cache/packed-assets.json',JSON.stringify({body:data('athlete-v2.glb','model/gltf-binary')}));
const r=await build({entryPoints:['src/app.js'],bundle:true,minify:true,format:'iife',target:'es2020',write:false,legalComments:'inline'});
const html=fs.readFileSync('src/shell.html','utf8').replace('/*STYLE*/',fs.readFileSync('src/style.css','utf8')).replace('/*APP*/',()=>r.outputFiles[0].text.replaceAll('</script','<\\/script'));
fs.writeFileSync('outputs/hurdle-110-3d.html',html);fs.writeFileSync('public/hurdle-110-3d.html',html);console.log(`Built 3D standalone HTML: ${(Buffer.byteLength(html)/1024/1024).toFixed(2)} MiB`);


if(fs.existsSync('public/assets/offline/hurdles-cycles.mp4'))await import('./build-cg.mjs');
