import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
const root = process.cwd();
process.env.TMPDIR = path.join(root, ".cache/tmp");
process.env.TMP = process.env.TMPDIR;
process.env.TEMP = process.env.TMPDIR;
const { bundle } = await import("@remotion/bundler");
const { selectComposition, renderStill, openBrowser } = await import(
  "@remotion/renderer"
);
mkdirSync("outputs/checks", { recursive: true });
const serveUrl = await bundle({
  entryPoint: path.join(root, "src/index.ts"),
  outDir: path.join(root, ".cache/check-bundle"),
});
const browser = await openBrowser("chrome", {
  browserExecutable:
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  chromiumOptions: { gl: "angle" },
});
const result = [];
try {
  const composition = await selectComposition({
    serveUrl,
    id: "PortfolioFilm",
    puppeteerInstance: browser,
  });
  for (const frame of [
    0, 60, 179, 180, 240, 300, 359, 360, 420, 539, 540, 570, 630, 719,
  ]) {
    const output = path.join(
      root,
      `outputs/checks/frame-${String(frame).padStart(3, "0")}.png`,
    );
    await renderStill({
      serveUrl,
      composition,
      frame,
      output,
      imageFormat: "png",
      puppeteerInstance: browser,
      chromiumOptions: { gl: "angle" },
      logLevel: "warn",
    });
    result.push({ frame, seconds: frame / 30, output });
    console.log("Checked frame", frame);
  }
  writeFileSync(
    "outputs/checks/frames.json",
    JSON.stringify(
      {
        composition: composition.id,
        width: composition.width,
        height: composition.height,
        fps: composition.fps,
        durationInFrames: composition.durationInFrames,
        frames: result,
      },
      null,
      2,
    ),
  );
} finally {
  await browser.close({ silent: true });
}
