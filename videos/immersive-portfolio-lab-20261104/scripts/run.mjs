import { spawn } from "node:child_process";
import { mkdirSync } from "node:fs";
import path from "node:path";
const root = process.cwd();
mkdirSync(".cache/tmp", { recursive: true });
const command = process.argv[2] ?? "studio";
const rest = process.argv.slice(3);
const defaults =
  command === "studio"
    ? ["src/index.ts", "--port=3124", "--no-open"]
    : command === "still"
      ? ["src/index.ts", "PortfolioFilm", "outputs/checks/frame.png"]
      : command === "render"
        ? ["src/index.ts", "PortfolioFilm", "outputs/immersive-portfolio.mp4"]
        : ["src/index.ts", "outputs/bundle"];
const child = spawn(
  process.execPath,
  ["node_modules/@remotion/cli/remotion-cli.js", command, ...defaults, ...rest],
  {
    cwd: root,
    stdio: "inherit",
    env: {
      ...process.env,
      TMPDIR: path.join(root, ".cache/tmp"),
      TMP: path.join(root, ".cache/tmp"),
      TEMP: path.join(root, ".cache/tmp"),
      npm_config_cache: path.join(root, ".cache/npm"),
    },
  },
);
child.on("exit", (code) => process.exit(code ?? 1));
