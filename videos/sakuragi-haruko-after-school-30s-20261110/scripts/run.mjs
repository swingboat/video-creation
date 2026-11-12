import {spawnSync} from 'node:child_process';
import {mkdirSync,existsSync,readFileSync,copyFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
process.chdir(root);
for(const dir of ['.cache/tmp','.cache/npm','outputs/checks'])mkdirSync(dir,{recursive:true});
const env={...process.env,TMPDIR:path.join(root,'.cache/tmp'),TMP:path.join(root,'.cache/tmp'),TEMP:path.join(root,'.cache/tmp'),XDG_CACHE_HOME:path.join(root,'.cache'),npm_config_cache:path.join(root,'.cache/npm'),HF_HOME:path.join(root,'.cache/huggingface'),UV_CACHE_DIR:path.join(root,'.cache/uv'),PYTHONDONTWRITEBYTECODE:'1'};
env.PATH=path.dirname(process.execPath)+path.delimiter+(process.env.PATH||'');
const rem=path.join(root,'node_modules/.bin/remotion');
const action=process.argv[2];
if(action==='render')for(const [scene,spec] of Object.entries(JSON.parse(readFileSync('docs/edit-decisions.json','utf8'))))if(!existsSync(`public/video/${scene}.mp4`)||spec.review_status!=='approved')throw Error(`${scene} has not been generated, reviewed and selected`);
const commands={dev:[rem,['studio','src/index.ts','--port=3101','--no-open']],render:[rem,['render','src/index.ts','SakuragiHaruko','outputs/sakuragi-haruko-30s.mp4','--codec=h264','--crf=16','--concurrency=2']],still:[rem,['still','src/index.ts','SakuragiHaruko']],check:['python3',['scripts/check.py']],package:['python3',['scripts/package.py']]};
const cmd=commands[action];if(!cmd)throw Error('Unknown action');
const p=spawnSync(cmd[0],[...cmd[1],...process.argv.slice(3)],{cwd:root,env,stdio:'inherit'});
if(p.error)throw p.error;
if(p.status===0&&action==='render'){const audio=spawnSync('python3',['scripts/final-audio.py'],{cwd:root,env,stdio:'inherit'});if(audio.error)throw audio.error;if(audio.status===0){copyFileSync('outputs/sakuragi-haruko-30s.mp4','outputs/sakuragi-haruko-30s-voiced.mp4');copyFileSync('outputs/sakuragi-haruko-30s.mp4','outputs/sakuragi-haruko-30s-lipsync-v2.mp4');}process.exit(audio.status??1);}
process.exit(p.status??1);
