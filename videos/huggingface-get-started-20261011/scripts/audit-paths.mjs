import fs from 'node:fs';
import path from 'node:path';
const root=fs.realpathSync('.');
const problems=[];
const inside=p=>p===root||p.startsWith(root+path.sep);
const files=[];
function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
 const p=path.join(dir,entry.name);
 if(entry.isSymbolicLink()){if(!inside(fs.realpathSync(p)))problems.push(`External symlink: ${p}`);}
 else if(entry.isDirectory())walk(p);
 else files.push(p);
}}
for(const folder of ['src','public','scripts','docs'])walk(path.join(root,folder));
for(const file of files.filter(p=>/\.(tsx?|mjs|py|sh|json|css)$/.test(p))){
 const text=fs.readFileSync(file,'utf8');
 if(file.includes('/src/')){
  for(const match of text.matchAll(/(?:from\s+|import\s*)['"](\.[^'"]+)['"]/g)){
   const resolved=path.resolve(path.dirname(file),match[1]);
   if(!inside(resolved))problems.push(`Import escapes video: ${file}: ${match[1]}`);
  }
  for(const match of text.matchAll(/staticFile\(['"]([^'"]+)['"]\)/g)){
   const asset=path.resolve(root,'public',match[1]);
   if(!inside(asset)||!fs.existsSync(asset))problems.push(`Missing/external asset: ${match[1]}`);
  }
 }
 if(/videos\/(hello-remotion|future-title|dental-clinic-city|unet-explainer|seaside-skate)/.test(text))problems.push(`Cross-video reference: ${file}`);
}
const manifest=JSON.parse(fs.readFileSync('src/timeline.json','utf8'));
let expected=0;
for(const s of manifest.scenes){
 if(s.startFrame!==expected)problems.push(`Timeline gap: ${s.id}`);
 expected+=s.durationInFrames;
 let prev=0;
 for(const c of s.captions){if(c.startMs<prev||c.endMs<=c.startMs||c.endMs>s.durationInFrames/manifest.fps*1000)problems.push(`Caption timing: ${s.id}`);prev=c.endMs;}
 if(!fs.existsSync(`public/voiceover/${s.id}.mp3`))problems.push(`Missing narration: ${s.id}`);
}
if(expected!==manifest.durationInFrames)problems.push('Duration mismatch');
const report={root,checkedFiles:files.length,scenes:manifest.scenes.length,durationSeconds:expected/manifest.fps,problems,allowedSystemTools:['Node/npm','Python','ffmpeg/ffprobe','system Google Chrome','global playwright-cli'],temporaryTransportException:'/tmp/hf-getstarted-8653 (cleaned after capture)'};
fs.mkdirSync('outputs/checks',{recursive:true});fs.writeFileSync('outputs/checks/path-audit.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));if(problems.length)process.exitCode=1;
