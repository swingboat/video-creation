# Immersive Studio · 3D Portfolio Study

24 秒、1920×1080、30fps 的 Remotion 学习试作。参考 Berryxia 分享的 [David Heckhoff portfolio](https://david-hckh.com)，依次展示 3D 办公室、全息角色、作者作品和联系场景。

[技术收集与 Review](docs/review-and-tech.md) · [分镜](docs/storyboard.md) · [原许可](docs/research/original-license.md)

## 独立安装

在本目录执行，需 Node.js 22+、npm；静帧检查/导出默认使用系统安装的 Google Chrome。

```bash
mkdir -p .cache/tmp .cache/npm
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" npm_config_cache="$PWD/.cache/npm" npm ci
```

`.npmrc` 已将 npm 缓存设置在本目录；所有直接依赖固定版本，lockfile 完整。`legacy-peer-deps` 用于跳过 R3F 可选的 React Native/Expo peer 解析；本项目只在浏览器运行。

## 预览

```bash
npm run studio
```

打开终端给出的 URL，默认 [PortfolioFilm](http://localhost:3124/PortfolioFilm)。总片及四个场景可分别选择和拖动时间轴；服务保持运行时，修改源码会热更新。

## 检查与导出

```bash
npm run check
npm run check:frames
npm run still -- --frame=60 --image-format=png
npm run render
```

- `check`：TypeScript 与独立性检查。
- `check:frames`：14 个关键帧，覆盖四个镜头、三个转场及首尾；写入 `outputs/checks/`，不生成 MP4。
- `still`：单帧 `outputs/checks/frame.png`。
- `render`：完整 H.264 MP4，写入 `outputs/immersive-portfolio.mp4`。本次默认交付 Studio 预览，未预先运行整片导出。
- `bundle`：独立网页 bundle，写入 `outputs/bundle/`，之后由 HTTP 服务托管（不能用 file:// 直接打开）。

`run.mjs` 为 Remotion 子进程设置 TMPDIR/TMP/TEMP；检查脚本将 webpack bundle、临时文件放到 `.cache/`。`remotion.config.ts` 及 `scripts/check-frames.mjs` 使用系统 Chrome；如果你的 Chrome 路径不同，需要同时修改这两处。没有下载渲染浏览器到其他目录。Codex 内置预览浏览器的应用级缓存没有可配置的项目路径，不将其宣称为已隔离。

## 修改素材、配音和时间轴

- 镜头顺序和时长：`src/Root.tsx` 中四个独立 `<Sequence>`，目前各 6 秒；改时长后同步修改主合成 `durationInFrames`、转场 `Wipe at`、分镜及配乐时长。
- 办公室和角色动画：`src/World.tsx`。Three.js 的 AnimationMixer 以绝对时间定位；GSAP timeline 暂停并按当前帧 seek。
- 全息效果：`World.tsx` 顶部 vertex/fragment GLSL、扫描环和粒子。
- 标题和位置：`Office.tsx`、`Hologram.tsx`、`Projects.tsx`、`Contact.tsx`；颜色和页眉页脚：`theme.tsx`。
- 模型与贴图：`public/upstream/` 本地副本。替换 GLB 后需核对 mesh 名称、UV、朝向和动画片段名。不能直接将不同骨架的 GLB 替换后假设原动作可用。
- 音乐：`public/audio/studio-score.wav`。`python3 scripts/synthesize-score.py` 可重建原创合成配乐，不依赖 Python 外部库。
- 配音：当前无旁白。可把自己的音频放到 `public/audio/`，在 `Root.tsx` 添加独立 `<Audio>`，以 `from` 和 `trimBefore` 调整时点；若新增字幕，应单独编辑文字和时间轴。
- 字体：`public/fonts/`，Urbanist 使用 OFL；`theme.tsx` 声明本地字体，不在播放时请求 Google Fonts。

## Credits & Attribution

**Original portfolio, reused character/office/contact models, related textures and project thumbnails were created and designed by David Heckhoff.**

Original portfolio: https://david-hckh.com

Original repository: https://github.com/davidhckh/portfolio-2025

本试作保留片内可见署名、源码注释和原许可。原资产限个人与教育用途，商用、转售或大部分内容再分发需作者书面许可。CubeWar、Quibbo、Sharkie、Particles 为原作者作品，本试作未将它们标记为用户自己的作品。参考帖视频仅保存于研究目录，不进入试作画面。

本项目新增的 Remotion 时间轴、排版、GLSL 全息材质与电子配乐用于本次学习试作。所有运行资源均在当前视频目录内，不引用其他视频或仓库根目录的文件。
