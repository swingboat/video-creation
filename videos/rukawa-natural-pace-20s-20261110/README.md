# 流川枫三分绝杀 · 自然节奏版

20秒，1280×720，24fps。人物片段采用原速，入网段采用2秒受控合成；新增控球、防守反应、看台及终场连续镜头，补足时长。素材均保存在本目录。

本轮实际技术、失败原因、修正方案、模型版本、耗时和以后制作同类视频的步骤，见 [制作复盘与复用流程](docs/production-method.md)。

## 独立安装与预览

需要 Node.js 22或更新版本、npm、Python 3、ffmpeg、ffprobe 和 Chrome。

```sh
mkdir -p .cache/tmp .cache/npm
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" npm ci --cache .cache/npm
npm run dev
```

预览：`http://localhost:3099/RukawaNaturalPace`。制作中未就绪的镜头显示“原画预览”，导出脚本会拒绝把它们作为成片。

## 检查、导出和打包

```sh
npm run render
npm run check
npm run package
```

成片：`outputs/rukawa-natural-pace-20s.mp4`；工程包：`outputs/rukawa-natural-pace-project.zip`。导出后调整声音响度，复制视频流以保留画面。检查包括类型、独立路径、源片段时长、480帧、24fps、音视频编码及全片解码。画面与动作质量另见 `docs/visual-review.md`。

## 修改素材与时间轴

`src/Root.tsx` 中的八个 `Series.Sequence` 是独立可编辑镜头，时长为1.5、2.5、2、2、2、2、4、4秒。`src/timing.ts` 控制终场声和记分时刻。`src/BasketAction.tsx` 控制固定篮圈、单球轨迹与球网回弹。`public/art/` 存完整原画，`public/video/` 存连续动画；`public/audio/` 是本地补充音效。没有解说配音；环境声保存在各镜头视频中。修改相应组件的 `volume` 可调整声音。字体来自本目录 `public/fonts/`，许可在 `docs/NOTO-OFL.txt`。

`src/media-status.ts` 标记素材是否准备完成。`scripts/select-native-clips.py` 从本目录的候选视频中按1倍速选择原帧，没有慢放、光流补帧、冻结补时或反向循环。

## 本地重新生成

普通预览与导出使用已保存的片段，不需要模型。重新生成连续片段需要 Apple Silicon Mac、Python 3.13、uv、git 及约30GB模型空间。模型、环境和缓存均在本目录。制作时每次只运行一个推理进程。

```sh
python3 scripts/setup-generator.py
.venv/bin/python scripts/fetch-video-model.py
.venv/bin/python scripts/generate-clip.py dribble --suffix=-natural4
.venv/bin/python scripts/select-native-clips.py dribble
.venv/bin/python scripts/generate-clip.py defender --suffix=-natural3
.venv/bin/python scripts/select-native-clips.py defender
.venv/bin/python scripts/generate-clip.py crowd --suffix=-natural4
.venv/bin/python scripts/select-native-clips.py crowd
.venv/bin/python scripts/generate-clip.py hero --suffix=-natural4
.venv/bin/python scripts/select-native-clips.py hero
```

新增动作提示词在 `docs/new-motion-prompts.json`，其他提示词在 `docs/video-prompts.json`，新增原画提示词在 `docs/new-image-prompts.json`。`select-native-clips.py` 也可处理 `close`、`shot`、`rim` 和 `celebrate`。

ZIP包含源码、锁定依赖、原画、已生成的连续片段和成片。可重新安装或下载的 `node_modules/`、`.venv/`、模型和工具缓存不打包。所有运行依赖在当前工程内；从旧版复用的内容均是本地独立副本。
