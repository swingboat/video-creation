import fs from 'node:fs';
import {build} from 'esbuild';
const data=(name,mime)=>'data:'+mime+';base64,'+fs.readFileSync('public/assets/offline/'+name).toString('base64');
fs.writeFileSync('.cache/cg-assets.json',JSON.stringify({video:data('hurdles-cycles.mp4','video/mp4'),poster:data('poster.jpg','image/jpeg'),approach:data('approach.jpg','image/jpeg'),flight:data('flight.jpg','image/jpeg'),landing:data('landing.jpg','image/jpeg')}));
const r=await build({entryPoints:['src/cg-player.js'],bundle:true,minify:true,format:'iife',target:'es2020',write:false});
const html=fs.readFileSync('src/cg-shell.html','utf8').replace('/*STYLE*/',fs.readFileSync('src/style-cg.css','utf8')).replace('/*APP*/',()=>r.outputFiles[0].text.replaceAll('</script','<\\/script'));
for(const p of ['outputs/hurdle-110.html','public/hurdle-110.html'])fs.writeFileSync(p,html);
console.log('Built code-rendered HTML: '+(Buffer.byteLength(html)/1048576).toFixed(2)+' MiB');
