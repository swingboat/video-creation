# 山有归途 · Sumi Passage

参考 [Shikhar 的 3D 游戏制作分享](https://x.com/xikhar/status/2117776295534997818)，重新设计制作的原创水墨山间冒险网页。先读 [Review 与实际实现](docs/review.md)。

这是独立网页项目，不是 Remotion 视频；源码、依赖、缓存、研究文件与检查结果均在本目录内，不引用工作区根目录或其他视频项目的文件。

2026-11-05 第二版已采用 **imagegen → Tripo → Blender → Three.js** 的资产流程：带纹理的旅人、六种骨骼动作、侵蚀岩壁、石板、针叶松与鸟居，配合接触阴影与较近的跟随镜头。详情见 [第二版制作记录](docs/art/production-v2.md)。第一版源码与构建保存在 `outputs/backups/v1-20261105/`。

## 独立安装与启动

需要 Node.js 22.18+ / npm，浏览器支持 WebGL 2。

```sh
mkdir -p .cache/tmp .cache/npm
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" npm ci
npm run dev
```

打开 http://127.0.0.1:4178 。开发服务默认仅本机访问。

## 检查、构建与发布

```sh
npm run check
npm run build
npm run preview
```

`check` 包含 TypeScript 与玩法检查（跳跃、暂停、移动速度、存档验证、终点条件和逐个平台的完整可达路径）。`build` 生成 `dist/` 静态站点，可放到任意支持静态网站的托管服务。运行时不依赖后端、CDN、远程字体或 AI 服务。

## 单文件 HTML

直接双击 `outputs/sumi-passage-standalone.html`，用支持 WebGL 2 的桌面浏览器打开即可游玩。该文件内嵌脚本、样式、图标与两个带贴图的模型，无需 npm、本地服务器或联网加载素材；可以单独复制、分享。模型经 Base64 内嵌，因此单文件比原始 GLB 稍大。浏览器的进度保存遵循其本地文件存储规则。

修改源码或模型后，在本目录重新打包：

```sh
npm run build:html
```

`dist/index.html` 是常规静态站点入口，仍需要旁边的 `assets/` 与 `models/`；单文件交付入口是 `outputs/sumi-passage-standalone.html`。

## 操作

- W A S D / 方向键：沿世界坐标移动。朝屏幕右前方越过山隙。
- 空格：跳跃；Shift：快跑。
- 拖动画面：旋转视角；滚轮：缩放；Q / E：键盘旋转；V：镜头复位。
- R：回到最近存档点；Esc / 旅人手记：暂停。
- 手机：屏幕方向键与跳跃按钮，支持多指同时操作。

收集「渡雾」「听松」「见山」三枚山印后，进入最高处朱色鸟居的区域。听松岛自动存档。进度保存于本机浏览器的 localStorage；手记内可重新开始。

## 修改方法

- `src/game.ts`：平台尺寸、路线、山印、移动速度、跳跃、重力与通关状态。修改平台间距后必须运行完整可达路径检查。
- `src/world.ts`：GLB 加载、骨骼动作切换、光影、云雾、镜头与相机避让。桌面采用 SSAO，手机关闭该效果并降低像素比。
- `scripts/art/build-environment.py`：在 Blender 制作山崖、松树、鸟居、石灯与石板，并按材质合并网格。
- `scripts/art/prepare-traveler.py`：整理合法导出的 Tripo 蒙皮模型，统一朝向与比例，制作 Idle / Walk / Run / Jump / Fall / Land 六种骨骼动作，压缩贴图并导出 GLB。
- `docs/art/*.blend`：可编辑的 Blender 模型。人物参考、Tripo 原始模型与减面后的源模型也在本目录。
- `public/models/`：网页实际使用的两个 GLB；材质与贴图均内嵌，没有外部资源路径。
- `src/main.ts`：页面文案、任务进度、手记、触屏输入、存档与完成页面。
- `src/style.css`：纸色、墨色、朱砂色、排版、响应式布局。
- `src/audio.ts`：浏览器 Web Audio 合成的原创风声与山印提示音，无外部音频文件。

本版没有旁白和视频时间轴。若需制作视频，应另建独立 `videos/<video-id>/` Remotion 项目，将需要的文件复制入该目录，不能跨目录引用本网页资源。

## 重新制作模型

需要系统安装 Blender 5.2。在本目录执行以下命令；全部源素材已经保存在项目内，重新整理与导出不需要再次调用 Tripo 或图像生成服务。

```sh
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" blender --background --factory-startup --python scripts/art/build-environment.py
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" blender --background --factory-startup --python scripts/art/prepare-traveler.py
npm run check
npm run build
```

人物约 1.94 万面；环境按 14 个材质合并。两个模型共约 11 MB，首次加载会显示进度。修改人物外形时需重新检查骨架朝向、蒙皮和动作；当前衣袍随蒙皮变形，没有真实布料求解器。

## 运行说明

本项目所有 npm 文件缓存由 `.npmrc` 指向 `.cache/npm/`。安装时将 TMPDIR/TMP/TEMP 指到本地 `.cache/tmp/`。检查截图与报告放在 `outputs/checks/`。Tabbit 浏览器使用其应用管理的缓存与临时截图路径，无法配置为项目目录；本次用于交付的截图会复制到本项目，不能将浏览器全局缓存宣称为项目内隔离。

本作使用本次原创生成及制作的资产；原视频仅作为研究资料，不构建或展示在网页中。Tripo 资产来自现有免费额度，公开且限非商用，本版作为个人学习试作。仍是七座山崖的短途探索，未实现参考视频的攀爬与索道。
