import {bundle} from '@remotion/bundler';
import {getCompositions, renderStill, renderMedia, selectComposition} from '@remotion/renderer';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url)); process.chdir(root);
await mkdir('outputs/storyboard', {recursive: true}); await mkdir('outputs/checks', {recursive: true});
await mkdir('.cache/tmp', {recursive: true}); process.env.TMPDIR = process.env.TMP = process.env.TEMP = path.join(root, '.cache/tmp');
const url = await bundle({entryPoint: path.join(root, 'src/index.ts'), outDir: path.join(root, '.cache/unet-review-bundle')});
const compositions = await getCompositions(url);
const files = [];
for (let scene = 0; scene < 7; scene++) {
  const inputProps = {scene}; const composition = await selectComposition({serveUrl: url, id: 'UnetStoryboard', inputProps});
  const output = path.join(root, 'outputs/storyboard', `scene-${scene + 1}.png`);
  await renderStill({serveUrl: url, composition, inputProps, output, frame: 0, imageFormat: 'png', logLevel: 'error'});
  files.push(output); console.log(`静态分镜 ${scene + 1}/7 完成`);
}
await writeFile('outputs/checks/static-review.json', JSON.stringify({files, dimensions: [1920, 1080]}, null, 2));
if (process.argv.includes('--sample')) {
  const composition = compositions.find((c) => c.id === 'UnetSkipSample');
  await renderMedia({serveUrl: url, composition, outputLocation: path.join(root, 'outputs/skip-connection-sample.mp4'), codec: 'h264', concurrency: 2, crf: 20});
  for (const frame of [60, 228, 330]) await renderStill({serveUrl: url, composition, output: path.join(root, `outputs/checks/skip-${frame}.png`), frame, imageFormat: 'png', logLevel: 'error'});
  console.log('12 秒跳跃连接样片完成');
}
