import {spawnSync} from 'node:child_process';
import {existsSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
process.chdir(root);
for(const p of ['.cache/tmp','.cache/npm','outputs/checks'])mkdirSync(p,{recursive:true});
const env={...process.env,TMPDIR:path.join(root,'.cache/tmp'),TMP:path.join(root,'.cache/tmp'),TEMP:path.join(root,'.cache/tmp'),XDG_CACHE_HOME:path.join(root,'.cache'),npm_config_cache:path.join(root,'.cache/npm'),HF_HOME:path.join(root,'.cache/huggingface'),UV_CACHE_DIR:path.join(root,'.cache/uv'),PYTHONDONTWRITEBYTECODE:'1'};
const candidates=process.env.PYTHON_BIN?[process.env.PYTHON_BIN]:process.platform==='win32'?['python','python3']:['python3','python'];
const python=candidates.find(c=>spawnSync(c,['-c','import sys;sys.exit(sys.version_info<(3,10))'],{cwd:root,env}).status===0);
if(!python)throw Error('Python 3.10+ required. Set PYTHON_BIN if needed.');
function run(command,args){const r=spawnSync(command,args,{cwd:root,env,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status??1);}
const action=process.argv[2],extra=process.argv.slice(3);
const ops=args=>run(python,['scripts/project_ops.py',...args]);
const cli=path.join(root,'node_modules/@remotion/cli/remotion-cli.js');
const tsc=()=>run(process.execPath,['node_modules/typescript/bin/tsc','--noEmit']);
if(action==='dev'){ops(['validate','--stage','scaffold']);run(process.execPath,[cli,'studio','src/index.ts',...extra]);}
else if(action==='source-check'){tsc();ops(['validate','--stage','scaffold']);}
else if(action==='render'||action==='render-draft'){
  ops(['validate','--stage',action==='render'?'final':'draft']);
  const file=action==='render'?'outputs/final.mp4':'outputs/review-candidate.mp4';
  run(process.execPath,[cli,'render','src/index.ts','Episode',file,'--codec=h264','--crf=18','--concurrency=2',...extra]);
  if(action==='render')ops(['verify-export','--rendered']);
}
else if(action==='check'){tsc();ops(['validate','--stage','final']);ops(['verify-export']);}
else if(action==='package'){ops(['package']);}
else throw Error('Unknown action');
