# 流川枫 三分绝杀

《灌篮高手》背景的程序化三维手办风格同人动画，20 秒 / 24 fps / 1280×720。流川枫身穿湘北 11 号球衣，运球后撤、三分线外跳投，在终场蜂鸣前出手，空心入网，以 77∶76 反超获胜。

沿用《瓶中风暴》制作会话的技术：Python + bpy / mathutils 制作模型、IK 动作及镜头；Blender Cycles + Metal 逐帧渲染；NumPy / SciPy 合成完整声音；FFmpeg 编码；Remotion / React / TypeScript 合成导出。

## 独立安装

需要 Node 24、Python 3.13、Blender 5.2、FFmpeg 和系统 Chrome。所有命令从本目录执行：

```bash
mkdir -p .cache/tmp .cache/npm .cache/python
export TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp"
export PIP_CACHE_DIR="$PWD/.cache/python"
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 预览、检查、导出

```bash
npm run dev
npm run check
npm run render
```

Studio 默认 http://localhost:3088/RukawaFinalShot 。选择 RukawaFinalShot，可编辑画面、音轨和比分信息。成片为 outputs/rukawa-final-shot-20s.mp4；可编辑 Blender 工程为 public/rukawa.blend；工程包为 outputs/rukawa-project.zip。已有 public/picture.mp4 时无需重渲三维，即可预览及导出。

`npm run check` 检查 480 张帧图、出手位置、飞行连续性、入网终点、20 秒音轨、每秒声音能量、最终媒体参数与工程路径隔离。帧序列属于可重建产物，不放进工程压缩包；如只解压工程包且未重渲三维，检查会明确跳过未包含的逐帧 PNG；媒体、声音和路径检查仍可运行。执行重建步骤后可再次检查帧完整性。成片媒体参数也可用 `ffprobe outputs/rukawa-final-shot-20s.mp4` 独立读取。

## 重建或修改

```bash
npm run scene
npm run preview:scene
npm run render:scene
npm run encode
npm run audio
npm run render
npm run check
npm run package
```

- scripts/build_scene.py：人物轮廓、发型、球衣、球场、灯光、看台、镜头，以及双段 IK 和烘焙。
- scripts/motion.py：米制坐标、跑动与后撤路径、篮球轨迹、起跳、出手和慢动作时间重映射。出手为 9.0 秒、蜂鸣为 9.15 秒、入网为 13.6 秒。
- scripts/audio.py：运球、脚步、鞋底摩擦、蜂鸣、篮网、欢呼及合成音乐。无旁白；如需旁白，将录音放进 public/ 并在 src/Root.tsx 单独添加 Audio 节点。
- public/fonts/Arial-Unicode.ttf：片中中文图层使用的工程内字体，由 FontFace 加载并等待就绪后导出。
- public/fonts/Arial-Bold.ttf：从系统复制的工程内字体，用于 Blender 球衣、标牌及比分。
- src/Root.tsx：画面和音轨各自独立，比分、时钟、片尾身份信息可修改。替换画面用本目录 public/ 中的文件，并修改 Composition 的 source。
- scripts/render_scene.py：24 samples、固定噪声种子、降噪、轻微运动模糊。支持断点续渲；如显存紧张，可在命令前设置 `RUKAWA_CPU=1` 使用 Cycles CPU 继续。支持场景指纹检查，场景指纹改变后拒绝混用旧帧。修改场景后先把 outputs/frames 和 render-final.json 移到本目录中的版本文件夹，再重渲。

时长与帧率修改时，同步 motion.py、build_scene.py、Root.tsx、audio.py、run.mjs 的帧数和编码参数，然后重新生成画面和声音。详细模型关联和分镜见 docs/production-plan.md；场景清单见 docs/scene-inventory.json。

## 路径与打包

本目录声明自己的 npm / Python 依赖和锁文件，所有受控缓存、临时文件、Blender 配置、素材、帧图、日志、视频和压缩包均放在本目录。没有符号链接或跨视频运行依赖。run.mjs 固定工作目录并设置 TMPDIR/TMP/TEMP、npm/pip 缓存、Blender 用户配置和 XDG 缓存。

系统安装的 Blender、FFmpeg、Chrome 属于系统工具；macOS Metal 驱动系统缓存以及已安装浏览器自身缓存不能完全由项目控制。脚本设置 CYCLES_METAL_DISABLE_BINARY_ARCHIVES=1，沿用既有作品的 Metal 编译归档兼容处理。

工程包包含当前工程源码、锁文件、已生成画面和声音、Blender 场景、文档、检查报告和成片；排除 node_modules、.venv、缓存、逐帧 PNG、旧 .blend1 和压缩包自身。重新解压后可独立 npm ci、预览、导出；更改三维动作才需 Blender 重建。
