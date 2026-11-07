import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const root=process.cwd(),tmp=path.join(root,'.cache/tmp');
for(const d of [tmp,'.cache/blender','outputs/offline/frames'])fs.mkdirSync(d,{recursive:true});
const env={...process.env,TMPDIR:tmp,TMP:tmp,TMP_DIR:tmp,TEMP:tmp,BLENDER_USER_RESOURCES:path.join(root,'.cache/blender'),HURDLE_CPU:process.env.HURDLE_CPU||'1'};
const args=process.argv.slice(2),r=spawnSync('blender',['-b','--python','scripts/build-offline.py','--',...args],{cwd:root,env,stdio:'inherit'});
if(r.error)throw r.error;process.exit(r.status??1);
