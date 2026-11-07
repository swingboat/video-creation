import {spawnSync} from 'node:child_process';
import {mkdirSync, existsSync, readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
process.chdir(root);
for(const dir of ['.cache/tmp','.cache/npm','.cache/blender/config','.cache/blender/scripts','.cache/python','.cache/browser','outputs/frames','outputs/checks'])mkdirSync(path.join(root,dir),{recursive:true});
const env={...process.env,CYCLES_METAL_DISABLE_BINARY_ARCHIVES:'1',TMPDIR:path.join(root,'.cache/tmp'),TMP:path.join(root,'.cache/tmp'),TEMP:path.join(root,'.cache/tmp'),npm_config_cache:path.join(root,'.cache/npm'),PIP_CACHE_DIR:path.join(root,'.cache/python'),XDG_CACHE_HOME:path.join(root,'.cache'),BLENDER_USER_CONFIG:path.join(root,'.cache/blender/config'),BLENDER_USER_SCRIPTS:path.join(root,'.cache/blender/scripts')};
const remotion=path.join(root,'node_modules/.bin/remotion');
const python=path.join(root,'.venv/bin/python');
const timeline=JSON.parse(readFileSync(path.join(root,'docs/timeline.json'),'utf8'));
const frameDir=timeline.frame_dir??'outputs/frames-bunny';
const picture=timeline.picture??'bunny-artist-picture.mp4';
const finalVideo=timeline.final_video??'outputs/bottle-storm-bunny-20s.mp4';
const action=process.argv[2];
const extra=process.argv.slice(3);
const commands={
 'dev':[remotion,['studio','src/index.ts','--port=3076',...extra]],
 'rebuild-scene':[python,['scripts/rebuild_scene.py']],
 'build-scene':['blender',['-b','--python-exit-code','1','--python','scripts/build_scene.py']],
 'upgrade-fish':['blender',['-b','outputs/versions/bunny-v2/bottle-storm.blend','--python-exit-code','1','--python','scripts/upgrade_fish.py']],
 'fish-paths':[python,['scripts/fish_motion.py']],
 'audit-fish':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/audit_fish.py']],
 'fish-preview':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/render_scene.py','--','fish-preview']],
 'animate-bunny':['blender',['-b','outputs/versions/v1/bottle-storm.blend','--python-exit-code','1','--python','scripts/animate_bunny.py']],
 'audit-bunny':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/audit_bunny.py']],
 'blocking':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/render_scene.py','--','blocking']],
 'audit-scene':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/audit_scene.py']],
 'finalize-scene':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python-expr',"import bpy; import json; from pathlib import Path; d=json.loads(Path('docs/timeline.json').read_text()); bpy.context.scene.render.filepath='//../'+d.get('frame_dir','outputs/frames-bunny')+'/frame_'; bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)"]],
 'preview-scene':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/render_scene.py','--','preview',...(extra.length?extra:['1','97','169','241','313'])]],
 'render-scene':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/render_scene.py','--','final']],
 'test-scene':['blender',['-b','public/bottle-storm.blend','--python-exit-code','1','--python','scripts/render_scene.py','--','test',...extra]],
 'audio':[python,['scripts/synthesize_audio.py']],
 'encode':['ffmpeg',['-y','-framerate','24','-start_number','1','-i',path.join(frameDir,'frame_%04d.png'),'-frames:v','480','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',path.join('public',picture)]],
 'render':[remotion,['render','src/index.ts','BottleStorm',finalVideo,'--props',JSON.stringify({source:picture}),'--codec=h264','--crf=17','--concurrency=2',...extra]],
 'still':[remotion,['still','src/index.ts','BottleStorm','outputs/checks/remotion-test.png','--frame=0',...extra]],
 'check':['node',['scripts/check.mjs']],
 'bundle':[remotion,['bundle','src/index.ts','outputs/remotion-bundle']],
};
if(!commands[action])throw new Error('Unknown action: '+action);
const [exe,args]=commands[action];
if(['audio'].includes(action)&&!existsSync(python))throw new Error('Run python3 -m venv .venv and install requirements.txt first.');
const child=spawnSync(exe,args,{cwd:root,env,stdio:'inherit'});
if(child.error)throw child.error;
process.exit(child.status??1);
