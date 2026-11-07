import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile, unlink} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {getCompositions, renderStill, selectComposition} from '@remotion/renderer';

const root = fileURLToPath(new URL('../', import.meta.url));
process.chdir(root);
await mkdir(path.join(root, '.cache/tmp'), {recursive: true});
process.env.TMPDIR = process.env.TMP = process.env.TEMP = path.join(root, '.cache/tmp');
const variantName = `.clinic-check-${process.pid}.json`;
const variantPath = path.join(root, 'public/business', variantName);
const baseConfig = JSON.parse(await readFile(path.join(root, 'public/business/clinic.json'), 'utf8'));
await writeFile(variantPath, JSON.stringify({...baseConfig, name: '示例口腔门诊', city: '宁波', district: '鄞州区', address: '示例路 66 号',
  theme: {...baseConfig.theme, brand: '#926744'}, store: {...baseConfig.store, position: [1.5, 0.1]}, buildings: baseConfig.buildings.slice(0, 8)}));
try {
const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts'), outDir: path.join(root, '.cache/clinic-bundle')});
const compositions = await getCompositions(serveUrl, {chromiumOptions: {gl: 'angle'}});
const composition = compositions.find((c) => c.id === 'DentalClinicCity');
assert.ok(composition, '3D 门诊 composition 已注册');
assert.deepEqual([composition.width, composition.height, composition.fps, composition.durationInFrames], [1080, 1920, 30, 900]);
const frames = [[75, 'intro'], [285, 'location'], [600, 'benefits'], [795, 'contact'], [285, 'seek-repeat']];
const images = [];
for (const [frame, label] of frames) {
  const output = path.join(root, 'outputs', `clinic-${label}.png`);
  await renderStill({serveUrl, composition, output, frame, imageFormat: 'png', chromiumOptions: {gl: 'angle'},
    inputProps: {configSrc: 'business/clinic.json'}, logLevel: 'error'});
  const bytes = await readFile(output);
  assert.equal(bytes.readUInt32BE(16), 1080); assert.equal(bytes.readUInt32BE(20), 1920);
  images.push({frame, label, output, sha256: createHash('sha256').update(bytes).digest('hex')});
  console.log(`PASS: ${label} / frame ${frame} / 1080×1920`);
}
assert.equal(images[1].sha256, images[4].sha256, '相同帧号重复渲染必须一致');
const variantOutput = path.join(root, 'outputs/clinic-config-variant.png');
const variantProps = {configSrc: `business/${variantName}`};
const variantComposition = await selectComposition({serveUrl, id: composition.id, inputProps: variantProps, chromiumOptions: {gl: 'angle'}});
await renderStill({serveUrl, composition: variantComposition, output: variantOutput, frame: 795, imageFormat: 'png',
  inputProps: variantProps, chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
const variantHash = createHash('sha256').update(await readFile(variantOutput)).digest('hex');
assert.notEqual(variantHash, images[3].sha256, '更换 JSON 后应生成不同商家画面');
const sourceFiles = ['DentalClinicCity.tsx', 'clinic/CityScene.tsx', 'clinic/CityIntro.tsx', 'clinic/CityLocation.tsx', 'clinic/ClinicBenefits.tsx', 'clinic/ClinicContact.tsx'];
for (const file of sourceFiles) assert.ok(!/\buseFrame\s*\(/.test(await readFile(path.join(root, 'src', file), 'utf8')), '禁止 useFrame 动画');
const packages = {};
for (const name of ['remotion', '@remotion/three', '@react-three/fiber', 'three']) {
  packages[name] = JSON.parse(await readFile(path.join(root, 'node_modules', name, 'package.json'), 'utf8')).version;
}
assert.equal(packages.remotion, packages['@remotion/three']);
await writeFile(path.join(root, 'outputs/clinic-check-report.json'), JSON.stringify({
  composition: {id: composition.id, width: composition.width, height: composition.height, fps: composition.fps, durationInFrames: composition.durationInFrames},
  packages, images, deterministicSeek: true, externalModels: false,
  configReplacement: {name: '示例口腔门诊', city: '宁波', output: variantOutput, sha256: variantHash},
}, null, 2) + '\n');
console.log('PASS: 30 秒参数、四段关键帧、重复帧一致性、JSON 替换、项目内 3D 依赖。');
} finally {
  await unlink(variantPath);
}
