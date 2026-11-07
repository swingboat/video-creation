import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, statSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const runner = path.join(root, 'scripts/remotion.mjs');
const output = path.join(root, 'outputs/smoke-test.mp4');
mkdirSync(path.dirname(output), {recursive: true});

const run = (args, capture = false) => {
  const result = spawnSync(process.execPath, [runner, ...args], {
    cwd: root,
    encoding: 'utf8',
    stdio: capture ? 'pipe' : 'inherit',
    timeout: 300_000,
    maxBuffer: 20 * 1024 * 1024,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`Remotion command failed: ${args.join(' ')}\n${result.stdout ?? ''}\n${result.stderr ?? ''}`);
  }
  return result.stdout;
};

const packageVersions = Object.fromEntries(
  ['remotion', '@remotion/cli', '@remotion/renderer', '@remotion/bundler'].map((name) => {
    const file = realpathSync(path.join(root, 'node_modules', name, 'package.json'));
    assert.ok(file.startsWith(`${root}node_modules${path.sep}`), `${name} must be project-local`);
    return [name, JSON.parse(readFileSync(file, 'utf8')).version];
  }),
);
assert.equal(new Set(Object.values(packageVersions)).size, 1, 'Remotion package versions must match');

run(['versions']);
run(['compositions', 'src/index.ts']);
run(['render', 'src/index.ts', 'HelloRemotion', output, '--codec=h264', '--concurrency=2']);
assert.ok(statSync(output).size > 1000, 'Rendered video must not be empty');

const probe = JSON.parse(run([
  'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
  '-show_entries', 'stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration',
  '-of', 'json', output,
], true));
const stream = probe.streams[0];
assert.equal(stream.codec_name, 'h264');
assert.equal(stream.width, 1280);
assert.equal(stream.height, 720);
assert.equal(stream.r_frame_rate, '30/1');
assert.equal(Number(stream.nb_read_frames), 90);
assert.ok(Math.abs(Number(probe.format.duration) - 3) < 0.05);

// Decode all frames and confirm the rendered animation actually changes.
const frameDirectory = mkdtempSync(path.join(root, '.cache/tmp/smoke-frames-'));
let hashes;
try {
  run(['ffmpeg', '-v', 'error', '-i', output, '-map', '0:v:0', '-vf', 'scale=160:90',
    '-c:v', 'png', '-f', 'image2', path.join(frameDirectory, 'frame-%03d.png')]);
  hashes = readdirSync(frameDirectory).filter((name) => name.endsWith('.png'))
    .map((name) => createHash('sha256').update(readFileSync(path.join(frameDirectory, name))).digest('hex'));
  assert.equal(hashes.length, 90);
  assert.ok(new Set(hashes).size > 1, 'Animation must contain different decoded frames');
} finally {
  rmSync(frameDirectory, {recursive: true, force: true});
}

const report = {packageVersions, video: probe, decodedFrames: hashes.length, distinctFrames: new Set(hashes).size};
writeFileSync(path.join(root, 'outputs/smoke-test-report.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log('PASS: project-local packages, composition discovery, H.264 rendering, 90-frame decoding, and animation.');
