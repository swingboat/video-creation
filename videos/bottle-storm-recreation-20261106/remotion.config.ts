/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";
import { existsSync } from "node:fs";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);
// A system installation is allowed; never use another video's downloaded browser.
const installedChrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
if (existsSync(installedChrome)) Config.setBrowserExecutable(installedChrome);
