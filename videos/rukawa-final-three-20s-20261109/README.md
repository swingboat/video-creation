# 流川枫 · 压哨三分（20秒试作）

完整视频：`outputs/rukawa-final-three-20s.mp4`。1280×720、30fps、600帧、20秒，含立体声现场音效。湘北以77–78落后，流川枫出手后终场蜂鸣器响，篮球入网，最终80–78获胜。

本版采用完整人物原画、分镜剪辑、有限动画、独立篮球轨迹和程序球网。持球、跳投、封盖分别使用完整造型；身体主要保持刚性，出手仅有小幅手腕变化。配角、观众和旗帜有连续的小幅运动。它仍是有限动画试作，起跳和收球之间通过镜头切换连接，没有逐帧重绘全部人体动作。图集中的配角分辨率低于主角原画。

## 独立安装与预览

需要Node.js 22或更新版本、npm，以及检查与打包时使用的Python 3、ffmpeg、ffprobe。解压后在本目录执行：

```sh
mkdir -p .cache/tmp .cache/npm
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" npm ci --cache .cache/npm
npm run dev
```

预览地址为 `http://localhost:3096/RukawaFinalThree`。macOS默认使用系统Google Chrome；其他位置可设置 `CHROME_BIN`。没有设置可用Chrome时，Remotion自行下载浏览器至本工程的 `node_modules/.remotion/`。全部npm依赖在本目录安装，不需要项目根目录或其他视频的文件。

## 检查、导出与打包

```sh
npm run render
npm run check
npm run package
```

`render`导出完整20秒MP4；`check`执行TypeScript检查、本地资源与路径检查、视频规格检查和完整解码检查；`package`生成 `outputs/rukawa-final-three-project.zip`，包含源码、全部素材、锁定依赖清单、最终MP4和检查报告，不包含可重建的 `node_modules/` 与缓存。

辅助检查关键帧：`node scripts/run.mjs checks`。导出指定帧：`npm run still -- outputs/checks/frame.png --frame=232`。所有脚本都将工作目录、npm缓存与临时目录限定在本工程内部。

## 修改素材与时间轴

- `public/art/`保存持球图、跳投图、防守者、球馆、观众、配角图集与篮球。`public/references/`保存造型参考。新生成的两张原画提示词在 `docs/new-asset-prompts.json`，生成来源和工具保留文件说明在 `docs/generation-origin.md`。
- `src/Root.tsx`中的七个 `Series.Sequence` 控制镜头长度，总和保持600帧；同处管理比分和文字。每个镜头也注册为独立Composition，便于在Studio预览。
- `src/scenes/drawScenes.ts`控制景别、人物、球网与观众运动。`src/math.ts`控制球轨迹和关键时刻：7.55秒离手、7.9秒蜂鸣器、11.55秒球心抵达篮圈、11.75秒更新比分。
- `public/audio/arena.wav`是程序合成的20秒立体声环境音、球鞋声、蜂鸣器和入网声。修改 `scripts/audio.py` 后运行 `node scripts/run.mjs audio`，再重新导出。没有旁白或外部音乐采样。
- 中文字体位于 `public/fonts/`，授权文本在 `docs/NOTO-OFL.txt`。

目录内的所有运行资源均为独立副本。历史作品没有移动或修改。本轮图片生成工具的原始输出已移入本工程 `.cache/generation-originals/`，运行素材在 `public/art/`；原始工具输出位置和移动记录保存在 `docs/generation-origin.md`。
