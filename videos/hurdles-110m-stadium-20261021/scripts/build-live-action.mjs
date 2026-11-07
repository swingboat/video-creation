import fs from 'node:fs';
import {build} from 'esbuild';
const data=(name,mime)=>`data:${mime};base64,${fs.readFileSync('public/assets/live-action/'+name).toString('base64')}`;
fs.writeFileSync('.cache/live-action-assets.json',JSON.stringify({video:data('hurdle-training.mp4','video/mp4'),poster:data('poster.jpg','image/jpeg'),approach:data('approach.jpg','image/jpeg'),flight:data('flight.jpg','image/jpeg'),landing:data('landing.jpg','image/jpeg')}));
const r=await build({entryPoints:['src/live-action.js'],bundle:true,minify:true,format:'iife',target:'es2020',write:false});
const html=fs.readFileSync('src/live-action.html','utf8').replace('/*STYLE*/',fs.readFileSync('src/live-action.css','utf8')).replace('/*APP*/',()=>r.outputFiles[0].text.replaceAll('</script','<\\/script'));
for(const name of ['outputs/hurdle-110-reference.html','public/hurdle-110-reference.html'])fs.writeFileSync(name,html);
console.log(`Built live-action single HTML: ${(Buffer.byteLength(html)/1024/1024).toFixed(2)} MiB`);
