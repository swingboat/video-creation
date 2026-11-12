import {Config} from '@remotion/cli/config';
import {existsSync} from 'node:fs';
Config.setRspack(true);
Config.setOverwriteOutput(true);
Config.setVideoImageFormat('jpeg');
const chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if(existsSync(chrome))Config.setBrowserExecutable(chrome);
