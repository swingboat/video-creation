# Hugging Face 中文零基础使用指南

独立 Remotion 项目。1920 × 1080，16:9，30 fps，约 3 分 47 秒。包含中文女声旁白、同步字幕、官网截图和操作引导动画；10 个章节均可独立预览。

## 独立安装与运行

在本目录运行；需要 Node.js 22 或更高版本和 npm。预览与导出无需 Python，也无需重新生成配音。

```bash
mkdir -p .cache/tmp .cache/npm
export TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp"
export npm_config_cache="$PWD/.cache/npm"
npm ci
npm run dev
```

Studio 默认使用 3016 端口，完整视频是 `HuggingFaceGuide`，`Chapters` 下为独立章节。

```bash
npm run check
npm run audit-paths
npm run stills
npm run render
```

`render` 导出 `outputs/huggingface-guide-zh.mp4`，H.264、CRF 18，保留中文配音和烧录字幕。`outputs/huggingface-zh.srt` 是可单独使用的字幕文件。`stills` 生成检查帧和 `outputs/poster.png`。`build` 可生成 `outputs/bundle/`。

macOS 上若已安装 Google Chrome，导出直接使用系统工具；没有时，Remotion 把浏览器下载到本项目 `node_modules/.remotion/`。可用 `REMOTION_BROWSER_EXECUTABLE` 指定已安装浏览器。所有命令通过 `scripts/env.sh` 将临时目录指向本项目。

## 怎么修改

- **画面与文字**：编辑 `src/scenes/` 下对应章节。每个章节的 JSX 都有自己的音轨和内联字幕；Studio 可以直接跳转到该章节编辑。
- **截图、字体与音频**：在 `public/` 替换素材，保持原文件名即可。更新后的官网截图可放入 `public/screens/`，重新调整高亮框位置；需要保留网站的原始标签，中文提示为教学标注。
- **配音文案**：编辑 `docs/narration.json`。现有配音已包含在项目中，可直接导出；重新合成才需要 Python、ffmpeg/ffprobe、网络和 edge-tts。
- **时间轴**：主时间轴在 `src/Root.tsx`，每章均是单独的 `Series.Sequence`，帧数可直接修改。`src/timeline.json` 存储配音长度、句子时间和字幕，用于提示切换；改动章节时长应同步更新。
- **颜色与字号**：`src/theme.ts`、`src/components.tsx` 和 `src/style.css`。

重新合成旁白及同步时长：

```bash
export PIP_CACHE_DIR="$PWD/.cache/pip"
python3 -m venv .cache/voice-env
.cache/voice-env/bin/pip install -r scripts/voice-requirements.txt
bash scripts/env.sh .cache/voice-env/bin/python scripts/generate-voice.py
python3 scripts/sync-captions.py --dry-run
python3 scripts/sync-captions.py
npm run check
npm run stills
npm run render
```

合成脚本根据原句缓存音频，修改原句会自动重新生成对应文件。`sync-captions.py` 会更新字幕、各章时长和完整视频总时长，覆盖各章已有内联字幕；如在 Studio 手工改过字幕，应先保存副本。字幕逐句对齐实际音频，同一句较长时按标点分屏；分屏时间在句子内部按文字长度分配，可在 Studio 微调。

## 内容与交付

1. Hugging Face 是什么
2. Models / Datasets / Spaces
3. 首页导航与注册时机
4. 用 Whisper Web 体验语音转文字，包含中文语言设置
5. 按任务查找模型
6. Model card / Files / Use this model
7. 数据卡与 Data Studio
8. 网页、本地与 API 三条路径
9. 社区讨论、Collections 与发布 Space
10. 首次体验清单

官网来源和素材许可见 `docs/sources.md`；核实日期为 2026-10-11。视频为非官方入门介绍，页面布局和应用可用状态可能变化。

本项目不引用其他视频的源码、素材、配置、脚本或依赖。项目包排除 `node_modules`、`.cache`、检查用 bundle 和运行日志；包含源码、锁文件、文档、所有播放素材、MP4、SRT 和海报。解压后在本目录执行 `npm ci` 即可恢复依赖。

网页截图工具的 macOS socket 受短路径限制，曾临时使用 `/tmp/hf-getstarted-8653`；专用会话结束后已清理。第一次自动生成的系统会话记录已移回本目录。详见 `docs/sources.md` 的路径隔离记录。
