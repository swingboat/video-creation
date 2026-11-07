import fs from 'node:fs';import path from 'node:path';
const root=process.cwd(),assets={};
for(const name of ['baseline','portrait','half','full']){const file=path.join(root,'outputs/realism-v6',name+'.jpg');if(!fs.existsSync(file))throw Error('Missing render: '+file);assets[name]='data:image/jpeg;base64,'+fs.readFileSync(file).toString('base64');}
let html=fs.readFileSync('src/lookdev-v6.html','utf8');for(const [name,url] of Object.entries(assets))html=html.replaceAll('{{'+name+'}}',url);if(html.includes('{{'))throw Error('Unresolved token');
for(const file of ['outputs/hurdle-character-v6.html','public/hurdle-character-v6.html'])fs.writeFileSync(file,html);
console.log('Character review built:',Buffer.byteLength(html),'bytes');
