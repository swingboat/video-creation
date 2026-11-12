# 流川枫 · 修正原画蓄力微动作预览

当前活动版本使用用户确认的完整修正图 `public/art/correctives/rukawa-gather-anatomy-v1.png`，输出 2 秒、1280×720、30 fps 的小幅动作预览。

本轮替换了旧版畸变的人物，保留原画中的脸、手型、篮球和腿部轮廓。头部、双手与篮球共用刚性变换，脚部固定，身体仅有约 5 像素的轻微重心变化。蓄力过渡发生在 0.2–0.7 秒，随后恢复。它不包含完整抬臂、起跳或出手，也不是完整 20 秒比赛视频。那些动作仍需补绘相应姿态和过渡。

旧版样片和失败的绑定代码保留在工作区，已退出默认预览、导出与本轮打包流程。

## 独立安装与预览

需要 Node.js 22.18+、系统 Google Chrome。FFmpeg/ffprobe 用于文件检查。

```sh
cd rukawa-2d-mesh-shot-20261109
mkdir -p .cache/tmp .cache/npm
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" npm ci --cache .cache/npm
npm run dev
```

打开 http://localhost:3095/RukawaGatherPreview 。所有运行素材在本项目中，预览不调用在线服务。

## 导出、检查与打包

```sh
npm run render
npm run check
npm run still -- outputs/checks/review.png --frame=25
npm run package
```

当前视频：`outputs/rukawa-corrected-gather-2s.mp4`。

独立工程包：`outputs/rukawa-corrected-gather-project.zip`。只包含当前活动版本的源代码、素材、依赖锁文件、视频和检查报告。旧版失败视频、旧绑定代码、node_modules 和缓存不进入本轮压缩包。

`run.mjs` 固定当前工作目录，将 TMPDIR、TMP、TEMP、XDG_CACHE_HOME、npm cache 指向本视频目录，使用系统 Chrome，不下载浏览器。

## 修改素材、动作、声音和时间轴

- `src/gatherMotion.ts`：重心变化、衣物微动和足部锁定；头脸、双手与球所在区域保持刚性。大幅度动作不应通过放大这些参数来实现。
- `src/CorrectedGather.tsx`：完整原画纹理、球馆背景、脚底阴影与绘制。前景只读取一张完整修正图。
- `src/Root.tsx`：2 秒时间轴、标题和画幅。修改时长后同步检查脚本里的帧数和持续时间。
- `public/art/correctives/rukawa-gather-anatomy-v1.png`：已确认修正图。请保留透明通道和完整人物。
- `docs/corrective-pose-prompt.txt`：生成修正图的完整提示词，使用内置 image_gen；本轮没有重新生成该图。
- 当前无音频。需要音效或配音时，将有权使用的文件放在本项目 `public/audio/`，通过 `@remotion/media` 的 Audio 引用，并按新时间轴定位。

## 验证范围与素材来源

`outputs/checks/corrected-gather-audit.json` 检查上身距离保持、脚部位移、局部变形幅度及网格翻转；`corrected-project-check.json` 检查类型、当前运行路径与视频解码。数值检查不能替代对画面自然程度的观看判断。

背景是本项目内的独立球馆插画副本，当前画面裁切到看台以下。Noto Sans SC 许可见 `docs/NOTO-OFL.txt`。内置图像工具保留的生成源位置见 `docs/generation-origin.md`，不构成运行依赖。
