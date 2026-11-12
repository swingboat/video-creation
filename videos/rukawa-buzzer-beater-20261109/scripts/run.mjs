import {spawnSync} from 'node:child_process';
import {mkdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
process.chdir(root);
for(const p of ['.cache/tmp','.cache/npm','.cache/python','.cache/blender/config','.cache/blender/scripts','outputs/checks','outputs/frames'])mkdirSync(p,{recursive:true});
const env={...process.env,TMPDIR:path.join(root,'.cache/tmp'),TMP:path.join(root,'.cache/tmp'),TEMP:path.join(root,'.cache/tmp'),npm_config_cache:path.join(root,'.cache/npm'),PIP_CACHE_DIR:path.join(root,'.cache/python'),XDG_CACHE_HOME:path.join(root,'.cache'),BLENDER_USER_CONFIG:path.join(root,'.cache/blender/config'),BLENDER_USER_SCRIPTS:path.join(root,'.cache/blender/scripts'),CYCLES_METAL_DISABLE_BINARY_ARCHIVES:'1',PYTHONDONTWRITEBYTECODE:'1'};
const rem=path.join(root,'node_modules/.bin/remotion'), py=path.join(root,'.venv/bin/python');
const a=process.argv[2],extra=process.argv.slice(3);
const cmds={
 dev:[rem,['studio','src/index.ts','--port=3088',...extra]],
 scene:['blender',['-b','--python-exit-code','1','--python','scripts/build_scene.py']],
 preview:['blender',['-b','public/rukawa.blend','--python-exit-code','1','--python','scripts/render_scene.py','--','preview',...extra]],
 frames:['blender',['-b','public/rukawa.blend','--python-exit-code','1','--python','scripts/render_scene.py','--','final',...extra]],
 patch:['blender',['-b','public/rukawa.blend','--python-exit-code','1','--python','scripts/revise_scene.py']],
 'fix-camera':['blender',['-b','public/rukawa.blend','--python-exit-code','1','--python','scripts/fix_camera.py']],
 audit:['blender',['-b','public/rukawa.blend','--python-exit-code','1','--python','scripts/audit_scene.py']],
 blocking:['blender',['-b','public/rukawa.blend','--python-exit-code','1','--python','scripts/blocking.py']],
 audio:[py,['scripts/audio.py']],
 encode:['ffmpeg',['-y','-framerate','24','-start_number','1','-i','outputs/frames/frame_%04d.png','-frames:v','480','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart','public/picture.mp4']],
 render:[rem,['render','src/index.ts','RukawaFinalShot','outputs/rukawa-final-shot-20s.mp4','--codec=h264','--crf=16','--concurrency=2',...extra]],
 bundle:[rem,['bundle','src/index.ts','outputs/remotion-bundle']],
 check:[py,['scripts/check.py']],
 'finish-when-ready':[py,['scripts/finish_when_ready.py']],
 finish:[py,['scripts/finish.py']],
 package:[py,['scripts/package.py']]
};
if(!cmds[a])throw Error('Unknown action '+a);
const [exe,args]=cmds[a];const c=spawnSync(exe,args,{cwd:root,env,stdio:'inherit'});if(c.error)throw c.error;process.exit(c.status??1);
