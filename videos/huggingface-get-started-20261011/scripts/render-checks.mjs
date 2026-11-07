import {bundle} from '@remotion/bundler';
import {getCompositions,openBrowser,renderStill} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve('.');
const chrome=process.env.REMOTION_BROWSER_EXECUTABLE || (fs.existsSync('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':null);
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts'),outDir:path.join(root,'outputs/checks/bundle'),enableCaching:true});
const browser=await openBrowser('chrome',{browserExecutable:chrome});
try{
 const compositions=await getCompositions(serveUrl,{puppeteerInstance:browser});
 const composition=compositions.find(c=>c.id==='HuggingFaceGuide');
 fs.writeFileSync('outputs/checks/compositions.json',JSON.stringify(compositions,null,2));
 const t=JSON.parse(fs.readFileSync('src/timeline.json','utf8'));
 const cue=(id,line,delay=1.3)=>{const s=t.scenes.find(s=>s.id===id);return s.startFrame+Math.round((s.utterances[line].startMs/1000+delay)*t.fps);};
 const frames=[210,cue('map',4),cue('home',1),cue('spaces',1),cue('spaces',2),cue('spaces',2,4.5),cue('spaces',3),cue('models',3),cue('card',1),cue('card',2),cue('card',3),cue('card',4),cue('data',2),cue('routes',3),cue('community',1),cue('outro',3)];
 for(let i=0;i<frames.length;i++){
  await renderStill({serveUrl,composition,frame:frames[i],output:path.join(root,`outputs/checks/frame-${String(i+1).padStart(2,'0')}.png`),puppeteerInstance:browser,imageFormat:'png'});
  console.log(`frame ${frames[i]} OK`);
 }
 fs.copyFileSync('outputs/checks/frame-01.png','outputs/poster.png');
}finally{await browser.close({silent:true});}
