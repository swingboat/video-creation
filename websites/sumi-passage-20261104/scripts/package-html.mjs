import assert from 'node:assert/strict';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const project = fileURLToPath(new URL('../', import.meta.url));
const dist = path.join(project, 'dist');
const output = path.join(project, 'outputs/sumi-passage-standalone.html');
let html = await readFile(path.join(dist, 'index.html'), 'utf8');
const scriptTag = html.match(/<script\b[^>]*\bsrc="([^"]+)"[^>]*><\/script>/);
const styleTag = html.match(/<link\b[^>]*\brel="stylesheet"[^>]*>/);
assert(scriptTag && styleTag, 'Expected one bundled script and stylesheet');
const styleUrl = styleTag[0].match(/\bhref="([^"]+)"/)?.[1];
assert(styleUrl, 'Stylesheet URL is missing');

function localAsset(url) {
  assert(url.startsWith('/') && !url.startsWith('//'), `Expected local asset: ${url}`);
  const resolved = path.resolve(dist, `.${url}`);
  assert(resolved.startsWith(`${dist}${path.sep}`), 'Asset must remain inside dist');
  return resolved;
}

let script = await readFile(localAsset(scriptTag[1]), 'utf8');
const style = await readFile(localAsset(styleUrl), 'utf8');
const embeddedModels = [];
for (const name of ['mountain-environment-v2.glb', 'traveler-v2.glb']) {
  const url = `/models/${name}`;
  assert.equal(script.split(url).length - 1, 1, `Expected one model reference: ${name}`);
  const bytes = await readFile(localAsset(url));
  script = script.replace(url, `data:model/gltf-binary;base64,${bytes.toString('base64')}`);
  embeddedModels.push({name, bytes: bytes.length});
}

assert(!/<\/style/i.test(style), 'Unexpected closing style tag');
script = script.replace(/<\/script/gi, '<\\/script');
html = html.replace(scriptTag[0], () => `<script type="module">${script}</script>`);
html = html.replace(styleTag[0], () => `<style>${style}</style>`);
const favicon = await readFile(path.join(dist, 'favicon.svg'));
html = html.replace('href="/favicon.svg"', `href="data:image/svg+xml;base64,${favicon.toString('base64')}"`);
assert(!/<script\b[^>]*\bsrc=/i.test(html), 'External script remained');
assert(!/<link\b[^>]*\b(?:href|src)="\//i.test(html), 'External asset link remained');
assert(!/\/models\/(?:mountain-environment|traveler)-v2\.glb/.test(html), 'Model reference remained');

await mkdir(path.dirname(output), {recursive: true});
await writeFile(output, html);
const report = {file: path.relative(project, output), bytes: Buffer.byteLength(html), embeddedModels};
await writeFile(path.join(project, 'outputs/standalone-build.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(`Standalone HTML: ${report.file} (${(report.bytes / 1024 / 1024).toFixed(2)} MiB)`);
console.log('Embedded JavaScript, CSS, favicon, and both GLB models.');
