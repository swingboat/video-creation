# 流川枫三分绝杀 · 重制工程

工程目标为20秒、1280×720、24fps（480帧）的独立Remotion作品。整幅原画驱动本地连续视频生成，再用Remotion编辑分镜、比分与终场文字。制作方法、来源与限制见 `docs/production-method.md`。

## 独立安装、预览与导出

需要 Node.js 22或更新版本、npm、Python 3、ffmpeg 和 ffprobe。解压后在本目录执行：

```sh
mkdir -p .cache/tmp .cache/npm
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" npm ci --cache .cache/npm
npm run dev
```

预览地址为 `http://localhost:3097/RukawaRemake`。Studio中的各镜头也可独立打开。制作时没有生成完成的镜头会明确显示“原画预览”；它们不是最终动画。

所有连续镜头生成并检查后，执行：

```sh
npm run render
npm run check
npm run package
```

导出后脚本会统一声音响度，视频流保持不变。最终MP4路径为 `outputs/rukawa-anime-remake-20s.mp4`。脚本会将工作目录、npm缓存、临时目录和输出限定在本项目。macOS默认使用系统Google Chrome，也可通过 `CHROME_BIN` 指定浏览器；需要由Remotion下载浏览器时，其缓存位于本目录的 `node_modules/.remotion/`。

## 修改素材和时间轴

`public/art/`是完整场景原画，`public/video/`是实际生成的连续镜头，`public/audio/`保存补充音效，`public/fonts/`是本地中文字体。字体授权在 `docs/NOTO-OFL.txt`。

五个镜头的顺序和帧数在 `src/Root.tsx` 的独立 `Series.Sequence` 节点里，时长为3、4、5、4、4秒，总和480帧。`src/BasketAction.tsx` 控制固定篮筐、单个篮球轨迹和球网回弹；看台运动来自本地生成的视频。庆祝镜头的源图是 `public/art/celebrate-grounded-v2.png`，采用保持脚下位置的上身表演。各镜头的独立组件控制视频和声音，`src/timing.ts`记录终场声与记分时刻。`src/media-status.ts`记录连续素材是否准备完成。全片按慢镜节奏剪辑，投篮等镜头保留连续源帧、延长每帧显示时间，没有光流补帧对人体做额外变形。

如需重新生成连续镜头，需要Apple Silicon Mac、Python 3.13、uv、git、ffmpeg及足够内存和磁盘空间。初次准备会下载数十GB模型，全部放在本目录内。源图和提示词也位于本目录：

```sh
python3 scripts/setup-generator.py
.venv/bin/python scripts/fetch-video-model.py
.venv/bin/python scripts/generate-clip.py pilot
.venv/bin/python scripts/generate-clip.py shot --suffix=-short-v2
.venv/bin/python scripts/finish-motion-clip.py shot
.venv/bin/python scripts/generate-clip.py close
.venv/bin/python scripts/generate-clip.py rim
.venv/bin/python scripts/generate-clip.py celebrate
.venv/bin/python scripts/generate-clip.py hero
```

生成时每次只运行一个视频推理任务。修改 `docs/video-prompts.json` 可调整动作描述；`--seed`可更换随机种子，`--suffix=-v2`可另存候选版本。开场、篮筐、庆祝和结尾的正常生成会自动应用已记录的慢放剪辑；另存候选版本则保留原始时间，供人工选择。正常导出已保存的连续素材不需要重新加载本地生成模型。

项目ZIP包含源码、配置、锁定依赖、场景素材、已生成的视频片段和最终成片；可重建的 `node_modules/`、`.venv/`、模型缓存及工具缓存不包含在ZIP内。ZIP的安装和导出不引用其他视频或项目根目录的文件。
