# 樱木花道 × 晴子 · 放学后的练习

30秒，1280×720，24fps。以原漫画前期的红色飞机头樱木、长发晴子与湘北旧式球馆为视觉基准的原创同人小片段。

完整场景原画 → 本地 LTX-2.3 q4／MLX 连续表演 → 用角色对白驱动讲话镜头的嘴部与表情 → 原速选取 → Remotion 合成。人物表演来自连续生成；没有用冻结、倒放或慢放补足时长。经典国语风格的AI角色对白配合中文字幕、原创轻配乐、球馆环境音和音效。樱木偏低、略沙哑而热血；晴子清亮温柔。音色按角色气质设计，具体记录见[角色配音记录](docs/voiceover/method.md)与[口型修复记录](docs/lipsync/method.md)。

制作依据见 [前作方法 Review](docs/method-review.md)、[本片制作记录](docs/production-method.md)、[画面验收](docs/visual-review.md) 与 [制作要求](docs/production-brief.md)。

本次“配音与表情、嘴型不匹配”的用户反馈、问题原因、失败候选、修复验证及后续制作准则，集中记录在[口型与表情修复复盘](docs/lipsync/method.md)。后续可见角色对白按“先定配音与情绪 → 实际音轨驱动画面 → 视觉与技术分别检查”执行。

## 独立安装与预览

需要 Node.js 22或更新版本、npm、Python 3、系统 ffmpeg／ffprobe 与 Chrome。所有命令在本目录执行。

```sh
mkdir -p .cache/tmp .cache/npm
export TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp"
npm ci --cache .cache/npm
npm run dev
```

打开 `http://localhost:3101/SakuragiHaruko`。未就绪镜头会明确显示“原画预览”，导出脚本拒绝导出未通过画面检查的素材。

## 检查、导出与打包

```sh
npm run render
npm run check
npm run package
```

口型修复版为 `outputs/sakuragi-haruko-30s-lipsync-v2.mp4`（与 `outputs/sakuragi-haruko-30s.mp4`、`outputs/sakuragi-haruko-30s-voiced.mp4` 相同），工程包为 `outputs/sakuragi-haruko-project.zip`。检查包含独立路径、锁定版本、720帧／30秒／24fps、H.264／AAC、全片解码、原速选片与六条驱动音频的逐采样时点。打包检查ZIP CRC和包内成片SHA-256。包内包含本片源码、素材、原始视频候选、成片、提示词和制作记录；不打包可重新安装的 node_modules、.venv、模型和缓存。

## 修改素材、对白、声音与时间轴

- `public/art/`：完整同框与匹配机位的原画。`docs/image-prompts.json` 与 `docs/prompts/` 保存内置图像工具提示词；`docs/image-assets.json` 记录来源和哈希。
- `public/video/`：连续生成候选与经过审核的原速选片。修改选片范围后更新 `docs/edit-decisions.json`，完成画面检查并标记 approved，再运行 `.venv/bin/python scripts/select-clips.py 镜头名`。
- `src/Root.tsx`：八个独立可编辑叙事段及其时长，合计720帧。害羞段的两个组件可以接入同一连续源片段；收尾段接晴子微笑近景。每个分段另有单独的Composition。
- `src/Opening.tsx` 等场景文件：中文对白与出现时间。字幕来自本地 `public/fonts/NotoSansSC.ttf`，许可见 `docs/NOTO-OFL.txt`。
- `scripts/make-audio.py`：原创12小节、96BPM电钢琴配乐与环境音。`docs/audio-events.json` 保存运球和拍手在全片中的接触时刻。修改后运行 `.venv/bin/python scripts/make-audio.py`。配音参数与对白在 `docs/voiceover/dialogue.json`，逐句声音在 `public/audio/voices/`，六个场景内各有独立Audio节点。对白期间配乐自动压低，处理入口为 `scripts/prepare-dialogue.py`。
- `src/media-status.ts`：选片脚本自动更新的素材就绪状态。

## 重新生成连续动作

普通预览、导出和打包直接使用已有素材，不需要重新运行模型。重新生成需要 Apple Silicon Mac、Python 3.13、uv、git与约30GB模型空间。模型与Python环境都独立在本目录。

```sh
python3 scripts/setup-generator.py
.venv/bin/python scripts/fetch-video-model.py
.venv/bin/python scripts/generate-clip.py gather --suffix=-v2
.venv/bin/python scripts/review-clip.py gather-native24-v2 --contact 225 220 280 260
```

先核对逐帧图和正常速度播放，再修改选片记录、重新选择、导出与验收。每次只运行一个GPU推理进程。批量生成入口是 `scripts/generate-queue.py`，只创建候选和检查帧，不自动批准画面质量。

固定代码提交、模型修订和依赖见 `docs/local-generator-commit.txt`、`docs/local-models.json`、`requirements-local-video.txt` 与 `package-lock.json`。模型重新下载读取固定修订，不跟随最新版本。本片复用的工具、模型和字体均为当前目录的独立副本。

## 重新制作国语角色配音

直接预览和导出使用已有WAV，不需要语音模型。重新合成使用本目录独立的`.venv-tts`，模型修订固定在`docs/voiceover/model-info.json`，依赖固定在`requirements-tts.txt`。

```sh
python3 scripts/setup-tts.py
.venv-tts/bin/python scripts/fetch-tts-model.py
.venv-tts/bin/python scripts/synthesize-dialogue.py --take=v2
# 核对候选后，在 docs/voiceover/selected-takes.json 选择对应版本
.venv-tts/bin/python scripts/prepare-dialogue.py
python3 scripts/mux-voiceover.py
npm run check
npm run package
```

`prepare-dialogue.py`处理头尾静音、逐句响度、轻微球馆反射和配乐压低；当前六句都使用1倍语速。`mux-voiceover.py`复制既有视频流，只替换音轨；需要重新编辑画面时照常运行`npm run render`。

先前无角色配音的版本，以及口型修复前的配音版MP4与ZIP，在制作目录的`outputs/versions/`中保留。语音模型按文字设计音色，没有使用原版动画录音或原演员样本。当前对白镜头使用实际配音驱动画面，检查说话起止、开闭口与表情；不把技术检查称为逐音素精确匹配原版动画。

## 修改对白后重新驱动口型

更换配音后，使用新的输入目录和候选版本，保留旧输入与旧候选。示例只演示“天才”近景；其他对白按各自时长和提示词操作。

```sh
.venv/bin/python scripts/prepare-lipsync-inputs.py --inputs-dir public/lipsync/inputs/v3
cp docs/lipsync/resolve-v1-prompt.txt docs/lipsync/resolve-v3-prompt.txt
# 修改提示词中的对白和表演方向
.venv/bin/python scripts/generate-lipsync.py resolve --take v3 --inputs-dir public/lipsync/inputs/v3 --frames 97
.venv/bin/python scripts/review-lipsync.py resolve --take v3
.venv/bin/python scripts/preview-lipsync.py resolve --take v3
```

完成逐帧检查与1倍速播放，在`outputs/checks/lipsync/visual-decisions.json`记录结果后，运行`.venv/bin/python scripts/adopt-lipsync.py resolve --take v3`选入工程。生成脚本不会自动批准画面。当前选用版本在`docs/lipsync/selected-takes.json`。

修改时间轴时，同步修改`src/Root.tsx`、场景中的`Audio from`与字幕时间，以及`scripts/prepare-lipsync-inputs.py`中的`layout`，再制作新的输入与候选。改变拍手动作时也须重新标记`docs/audio-events.json`，生成配乐音效并运行`prepare-dialogue.py`，最后导出和检查。推理一次只运行一个GPU任务。
