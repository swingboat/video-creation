import {mkdirSync} from 'node:fs';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const temporaryDirectory = path.join(root, '.cache', 'tmp');
mkdirSync(temporaryDirectory, {recursive: true});

const child = spawn(
  process.execPath,
  [path.join(root, 'node_modules/@remotion/cli/remotion-cli.js'), ...process.argv.slice(2)],
  {
    cwd: root,
    stdio: 'inherit',
    env: {...process.env, TMPDIR: temporaryDirectory, TMP: temporaryDirectory, TEMP: temporaryDirectory, NODE_COMPILE_CACHE: path.join(root, '.cache/node-compile-cache')},
  },
);

child.on('error', (error) => {
  console.error(error);
  process.exitCode = 1;
});
child.on('exit', (code, signal) => {
  process.exitCode = code ?? (signal ? 1 : 0);
});
