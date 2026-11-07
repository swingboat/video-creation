/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";
import {existsSync} from 'node:fs';

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
const systemChrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const customChrome=process.env.REMOTION_BROWSER_EXECUTABLE;
if(customChrome) Config.setBrowserExecutable(customChrome);
else if(existsSync(systemChrome)) Config.setBrowserExecutable(systemChrome);
// Otherwise Remotion downloads into the local node_modules/.remotion cache.
