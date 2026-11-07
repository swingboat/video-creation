import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const root = fs.realpathSync(process.cwd());
const inside = (p) => p === root || p.startsWith(root + path.sep);
const errors = [];
let count = 0;
const required = [
  "src/index.ts",
  "src/Root.tsx",
  "public/audio/studio-score.wav",
  "public/upstream/models/avatar.glb",
  "public/upstream/models/room.glb",
  "public/upstream/models/contact.glb",
  "README.md",
  "docs/review-and-tech.md",
];
for (const p of required) if (!fs.existsSync(p)) errors.push("Missing " + p);
function walk(dir) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name);
    if (ent.isSymbolicLink()) {
      if (!inside(fs.realpathSync(p))) errors.push("External symlink " + p);
    } else if (ent.isDirectory()) walk(p);
    else {
      count++;
      if (/\.(tsx?|mjs)$/.test(p)) {
        const s = fs.readFileSync(p, "utf8");
        for (const m of s.matchAll(
          /(?:from\s+|import\s*\()['"]([^'"]+)['"]/g,
        )) {
          const v = m[1];
          if (v.startsWith(".")) {
            const resolved = path.resolve(path.dirname(p), v);
            if (!inside(resolved))
              errors.push("External import " + p + ": " + v);
          }
        }
        if (/videos\/[a-z0-9-]+/.test(s)) errors.push("Cross-video path " + p);
        for (const m of s.matchAll(/staticFile\(['"]([^'"]+)['"]\)/g)) {
          if (!inside(path.resolve("public", m[1])))
            errors.push("Escaping asset " + m[1]);
          if (!fs.existsSync(path.join("public", m[1])))
            errors.push("Missing asset " + m[1]);
        }
      }
    }
  }
}
for (const d of ["src", "scripts", "public"]) walk(d);
const require = createRequire(path.join(root, "package.json"));
const pkg = JSON.parse(fs.readFileSync("package.json", "utf8"));
for (const [n, v] of Object.entries({
  ...pkg.dependencies,
  ...pkg.devDependencies,
})) {
  if (!/^\d+\.\d+\.\d+/.test(v)) errors.push("Unpinned dependency " + n);
  try {
    const p = fs.realpathSync(
      path.join(root, "node_modules", n, "package.json"),
    );
    if (!p.startsWith(path.join(root, "node_modules") + path.sep))
      errors.push("Outside dependency " + n);
  } catch (e) {
    if (
      n !== "@types/react" &&
      n !== "@types/react-dom" &&
      n !== "@types/three"
    )
      errors.push("Unresolved dependency " + n);
  }
}
for (const file of fs.readdirSync("public/upstream/models")) {
  const b = fs.readFileSync(path.join("public/upstream/models", file));
  const len = b.readUInt32LE(12);
  const gltf = JSON.parse(b.subarray(20, 20 + len).toString());
  for (const row of [...(gltf.buffers ?? []), ...(gltf.images ?? [])]) {
    if (row.uri && !row.uri.startsWith("data:"))
      errors.push("External GLB resource " + file + ": " + row.uri);
  }
}
const result = {
  passed: errors.length === 0,
  root,
  checkedProjectFiles: count,
  errors,
  scope:
    "Source imports, local assets, embedded GLB resources, exact direct dependencies, source symlinks. Normal npm packages and system Chrome are allowed.",
};
fs.mkdirSync("outputs/checks", { recursive: true });
fs.writeFileSync(
  "outputs/checks/isolation.json",
  JSON.stringify(result, null, 2),
);
console.log(JSON.stringify(result, null, 2));
if (errors.length) process.exit(1);
