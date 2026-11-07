import { Config } from "@remotion/cli/config";
import { existsSync } from "node:fs";
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setConcurrency(2);
const chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
if (existsSync(chrome)) Config.setBrowserExecutable(chrome);
