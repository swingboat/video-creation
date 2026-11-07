# U-Net 中文讲解视频

本视频已迁移为独立 Remotion 项目。Composition 为 `UnetExplainer`：1920×1080、30 fps、4750 帧，时长 158.33 秒。七个镜头围绕同一张 U 形结构图展开，使用本地 MiSans 字体。中文普通话旁白由本机 macOS Tingting 生成，无背景音乐，无付费 API。

## 交付文件

- `unet-explainer.mp4`：H.264 / yuv420p，含 AAC 旁白与烧录中文字幕。
- `unet-explainer.srt`：32 条句级字幕，来自逐句音频的实测时间。
- `narration.txt`：完整旁白；`tts-narration.txt`：发音调整版，U-Net 统一写为 `U net`。
- `narration.wav`：48 kHz、单声道完整配音。
- `storyboard.md`、`storyboard/`：七段分镜与静态关键帧。
- `skip-connection-sample.mp4`：12 秒无声拼接样片。
- `timeline.json`：实测时间轴。
- `unet-remotion-project.zip`：可编辑完整项目，包含源代码、本地字体、逐句与逐镜头音频、锁定依赖清单；不包含 node_modules 和渲染缓存。
- `checks/`：视觉关键帧、音频与时间轴检查记录、最终媒体检查记录。
- `preview.html`：本地成品播放器，支持跳转章节；可直接打开，或通过本地 HTTP 服务播放。

## 安装、预览与重新导出

解压项目后进入 `unet-explainer` 目录。需要 Node.js 22 或更高版本；本次使用 Node.js 24.13.1。依赖只安装在项目内：

```bash
npm ci
npm run dev
```

在浏览器打开 `http://localhost:3210/UnetExplainer`。逐段 Composition 位于 `Unet-Scenes` 文件夹。

```bash
npm run typecheck
npm run render:unet
```

最终视频输出至 `outputs/unet-explainer.mp4`。第一次渲染时 Remotion 可能自动下载官方 Chrome Headless Shell。已附带配音，常规预览和导出不需要 macOS TTS。

成品播放器：运行 `python3 scripts/serve-unet.py`，打开 `http://localhost:3211/preview.html`。服务仅绑定本机，并支持视频章节跳转所需的字节范围请求。

```bash
node scripts/render-unet-review.mjs --sample
node scripts/render-unet-keyframes.mjs
node scripts/verify-unet.mjs
```

前两条重新生成分镜/样片与完整关键帧；最后一条检查已导出的 MP4 并完整解码、抽取成品帧。

## 修改内容

- `public/unet/narration.json`：逐句旁白与镜头归属，字幕保留正确术语。
- `src/unet/settings.ts`：集中管理配色、字号、空间尺寸、通道数和标题。
- `src/unet/scenes/`：七个独立镜头；`src/UnetExplainer.tsx`：镜头编排。
- `src/unet/UNetDiagram.tsx`、`FeatureMapStack.tsx`、`ConcatDemo.tsx`、`SegmentationExample.tsx`、`TrainingDemo.tsx`、`CaptionOverlay.tsx`：可复用图形与字幕组件。
- `scripts/prepare-unet-audio.py`：语音生成、实测音频时间、停顿与镜头时长计算。`TARGET` 为各镜头最短教学时长。
- `src/unet/timeline.generated.ts`：生成的最终时间轴，请通过脚本更新。Root 的 `calculateMetadata` 自动采用总帧数。

所有动画依照帧号计算；镜头内部使用局部帧。特征纹理使用固定的数学种子，同一帧确定。字幕位于单独底部安全区域。

## 配音替换与时间轴更新

在已安装中文 Tingting 声音的 macOS 上重新生成：

```bash
npm run prepare:unet
# 可选：指定已安装的声音与语速
npm run prepare:unet -- --voice Tingting --rate 175
```

脚本调用系统 `say` / `afconvert`，按句生成，缓存未变的文本；只裁去外部空白并调整电平，不加速。字幕起止取实际采样长度。

替换真人或其他旁白时，将 `public/unet/audio/sentence-01.wav` 至 `sentence-32.wav` 替换为对应短句的 **48 kHz、单声道、16 位 PCM WAV**，再执行：

```bash
npm run prepare:unet -- --reuse-audio
npm run typecheck
node scripts/render-unet-keyframes.mjs
npm run render:unet
node scripts/verify-unet.mjs
```

脚本重新测量 WAV，生成镜头音频、完整 WAV、SRT 和时间轴；保留必要停顿，不强行压至固定总时长。新增、删除或重排句子时，也应更新 Task/Encoder/Decoder/Skip 场景中的字幕提示索引，让动画继续对应讲解内容。

## 教学简化与素材标注

空间尺寸为 256→128→64→32→16→32→64→128→256，采用同尺寸填充。通道配置用于教学，不代表原论文精确配置。原始 U-Net 使用不填充卷积，发生尺寸变化，并在跳跃连接前裁剪；视频中明确说明省略这些细节，重点解释信息流。参考原始论文：https://arxiv.org/abs/1505.04597 与作者项目：https://lmb.informatik.uni-freiburg.de/people/ronneber/u-net/。

跳跃连接是沿通道维拼接，两路空间尺寸均为 64×64、各 64 通道，拼接为 128 通道，再卷积融合。画面明确“+ 只表示通道数计数；特征值没有逐元素相加”。最后 1×1 卷积映射为前景/背景两类；上采样不保证恢复全部边界信息。

细胞图与标注掩码为 React/SVG 合成示意，标注“分割示意”；纹理标注“特征示意”；故意带误差的预测标注“预测示意”，红线强调与标注边界的差异。没有训练真实模型、使用真实激活或声称实际准确率。

## 验证与限制

已经进行 TypeScript 检查、Remotion 构建、七个静态分镜和拼接样片检查、完整动画关键帧人工视觉检查，以及重复帧一致性和字幕时间范围检查。最终编码、全片解码和播放检查的实测结果见 `checks/final-media-report.json` 与 `checks/playback-report.json`。

旁白文件有效、时长与电平均经过检查；U-Net 在 TTS 文稿中统一读法。未进行逐句人工听校或词级强制对齐，字幕采用实测句级时间戳。这是本版保留的质量检查限制；项目、配音、字幕和 MP4 均已制作。

独立目录迁移检查：`npm run check`；完整成品参数与解码检查：`npm run verify`；本视频单独打包：`npm run pack`。
