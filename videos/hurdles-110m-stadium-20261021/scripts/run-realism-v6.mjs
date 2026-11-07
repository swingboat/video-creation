import fs from 'node:fs';import path from 'node:path';import {spawnSync} from 'node:child_process';
const root=process.cwd(),tmp=path.join(root,'.cache/tmp');fs.mkdirSync(tmp,{recursive:true});
const env={...process.env,TMPDIR:tmp,TMP:tmp,TEMP:tmp,BLENDER_USER_RESOURCES:path.join(root,'.cache/blender')};
const r=spawnSync('blender',['-b','--python-exit-code','1','--python','scripts/build-realism-v6.py','--',...process.argv.slice(2)],{cwd:root,env,stdio:'inherit'});if(r.error)throw r.error;process.exit(r.status??1);
