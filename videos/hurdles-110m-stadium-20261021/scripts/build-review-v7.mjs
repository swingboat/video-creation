import fs from 'node:fs';
const files={oldFace:'outputs/realism-v6/portrait.jpg',oldFull:'outputs/realism-v6/full.jpg',portrait:'outputs/realism-v7/portrait.jpg',half:'outputs/realism-v7/half.jpg',full:'outputs/realism-v7/full.jpg',flex:'outputs/realism-v7/flex.jpg'};
let html=fs.readFileSync('src/lookdev-v7.html','utf8');for(const [name,file] of Object.entries(files))html=html.replaceAll('{{'+name+'}}','data:image/jpeg;base64,'+fs.readFileSync(file).toString('base64'));
if(html.includes('{{'))throw Error('Unresolved asset');for(const f of ['outputs/hurdle-character-v7.html','public/hurdle-character-v7.html'])fs.writeFileSync(f,html);console.log('Free character comparison:',Buffer.byteLength(html),'bytes');
