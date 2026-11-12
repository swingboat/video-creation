import {Config} from '@remotion/cli/config';
import {existsSync} from 'node:fs';
import path from 'node:path';
Config.setRspack(true);
Config.setOverwriteOutput(true);
const candidates=[process.env.CHROME_BIN,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser',
  process.env.PROGRAMFILES?path.join(process.env.PROGRAMFILES,'Google','Chrome','Application','chrome.exe'):undefined,
  process.env.LOCALAPPDATA?path.join(process.env.LOCALAPPDATA,'Google','Chrome','Application','chrome.exe'):undefined];
const chrome=candidates.find((p):p is string=>Boolean(p&&existsSync(p)));
if(!chrome)throw new Error('Chrome required: set CHROME_BIN to an installed Chrome or a browser downloaded inside this project.');
Config.setBrowserExecutable(chrome);
