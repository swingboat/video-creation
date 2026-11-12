# 流川枫 二维投篮动作样片 v2

当前质量状态：v2 的动作连贯性未通过用户验收。现有媒体参数、解码与区域差异检查仅表示文件可播放和画面有变化，不代表人物动作连贯。诊断见 docs/continuity-review/audit.json；下一阶段需改用连续变形的人物绑定或连续视频生成流程。


5 秒 / 1280×720 / 30fps / 150 帧。按已认可的流川枫原型，制作投篮、篮球飞行与入网的二维有限动画样片，同时检查湘北队友、对手、球馆和观众的画风。此轮交付 5 秒样片，尚未扩展为原定 20 秒版本。

## 安装、预览、检查、导出

需要 Node.js 24、Python 3、FFmpeg / ffprobe 和系统 Chrome。从本目录执行：

```bash
mkdir -p .cache/tmp .cache/npm
export TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp"
npm ci
npm run dev
npm run check
npm run render
npm run package
```

预览为 http://localhost:3091/RukawaAnimeSample 。默认导出 outputs/rukawa-anime-sample-v2-5s.mp4；工程包 outputs/rukawa-anime-sample-v2-project.zip。音轨已包含在 public/，无需重新合成；要重建原创拟音可执行 npm run audio。类型检查：node_modules/.bin/tsc。构建：npm run build。

## 修改素材与时间轴

- public/references/rukawa-approved.png：用户认可的造型原型。本目录保留独立副本。
- public/art/court-clean-v2.png：移除场内球员后的独立球馆背景。
- public/art/court-cheer-v2.png 和 hoop-cheer-v2.png：两个镜头的观众反应姿态；原有对应背景提供另一姿态。
- public/art/support-players-v2.png：5 行 × 3 列的配角动作格，共 15 个姿态。
- src/SupportingPlayers.tsx：五名配角独立安排跑动、起跳、落地与篮板动作。src/support-bounds.json 是透明通道分析得到的裁切和脚部对齐数据。
- src/Crowd.tsx：两处看台各划分六组，以错开的时序切换手掌、手臂和毛巾的绘制状态。建筑、地板和篮架保留在固定底图。
- public/art/rukawa-poses-v2.png：九格透明投篮关键姿态，3×3，1254×1254。每格 418×418。v1 为本目录内的生成中间稿。
- public/art/hoop-crowd.png：篮筐近景和观众背景；篮网由代码绘制并响应进球。
- src/CourtShot.tsx：动作格时间、角色位置、跳跃高度和手部持球点。替换动作素材后，需要校准每格尺寸及 handX / handY。
- src/HoopShot.tsx：篮球通过篮圈的时间、前后遮挡和篮网摆动。替换篮筐画面需同时调整 cx、cy、rx、ry 和前缘遮挡区域。
- src/Basketball.tsx：独立的连续篮球图层，线条、颜色、位置与旋转。
- src/Root.tsx：两段镜头各有独立 JSX 时间节点；起跳镜头 0–2.2 秒，篮筐近景 2.2–5 秒；比分在 3.55 秒从 74∶76 变为 77∶76。
- scripts/audio.py：Python 标准库合成 48kHz 立体声球馆底噪、鞋声、蜂鸣、篮网和欢呼，无旁白。要加配音，将录音放在本目录 public/ 并在 Root.tsx 添加独立 Audio 节点。

如改变 fps 或时长，同时修改 Root.tsx、CourtShot.tsx 动作格帧数、audio.py、check.py，随后重建声音、检查与导出。

## 素材生成与范围

使用内置 image_gen 生成二维素材，并用当前目录中的造型原型作为身份与画风参考。完整提示词：

- docs/prompts/court.txt
- docs/prompts/poses.txt
- docs/prompts/poses-edge-cleanup.txt
- docs/prompts/hoop.txt

生成输出从工具默认目录移入本视频目录，未留下本次生成图片的外部临时副本；来源与路径见 docs/assets.json。没有调用 AI 视频服务，也没有使用现成《灌篮高手》视频片段。

这是九个绘制关键姿态与独立篮球、篮网图层组合的有限动画。流川枫有动作变化，篮球和篮网连续运动；v2 增加了五名配角的独立位置轨迹与每人三个绘制姿态；观众按六个区域错时切换两个绘制手势状态。观众未逐人独立绑定，整片仍属有限关键帧动画。此样片用于检查画风、镜头、接球/出手接触与节奏，不能称作已完成完整逐帧动画。上一版样片保存在 outputs/versions/v1/，源码快照保存在 src/versions/v1/。

## 独立性与打包

所有受控素材、脚本、依赖、缓存、临时文件、声音、导出和检查报告均位于本目录。运行时不读取其他视频或项目根目录；系统工具属于外部软件依赖。系统 Chrome 必须已安装，配置优先使用该安装；系统工具自身的系统缓存未声称完全隔离。

npm 缓存指向 .cache/npm/；run.mjs 固定工作目录，并设置 TMPDIR / TMP / TEMP / XDG_CACHE_HOME。工程包包含此项目文件和本地素材，排除 node_modules、.cache 和可重建的 bundle；解压后可独立 npm ci、预览和导出。

## v2 修复验证

新增提示词保存在 docs/prompts/v2/。使用内置 image_gen 生成，四张新素材都已从工具默认输出目录移入本视频目录，生成的外部临时副本未保留。

检查会解码实际成片，对比五个配角区域、运球镜头和篮筐镜头的观众区域，要求各区域有可测变化；另检查无角色的墙面区域保持稳定，避免用整个背景移动代替角色动作。区域变化是画面层检查，人物互相遮挡时不代表每一个角色的每个像素都独立可见。
