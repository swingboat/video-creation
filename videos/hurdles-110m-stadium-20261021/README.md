# 110 米栏 · 代码生成 3D 动画

## 本轮 v7：只用免费资源的完整人物测试

打开 outputs/hurdle-character-v7.html，或 http://localhost:8110/outputs/hurdle-character-v7.html 。页面包含上一轮与完整人物的全身、面部对照，以及半身和骨骼弯曲检查。六张图片全部嵌入，可离线查看。

本轮采用 MIT 许可的 Microsoft Rocketbox Sports_Male_04，保留配套的头部、身体、蓝色无袖运动服、白色短裤、跑鞋与 80 骨骼，使用原生 2048×2048 贴图、本地 Cycles 渲染。素材支出为零。全身衔接和服装比 v6 更自然，但脸部细节较少，仍有游戏角色感，未通过真人实拍质感目标。不替换 v5 主动画，抬腿图仅检查骨骼，不是专业跨栏动作。

在本视频目录重建（需要本项目既有 v6 的 baseline.blend 场景；如缺失，先按下节运行 build:lookdev）：

    npm ci --cache .cache/npm
    npm run assets:free
    npm run build:free
    npm run render:free
    npm run review:free
    npm run check:free
    npm run preview

制作提示词和筛选结论见 docs/REALISM-V7-FREE.md。scripts/build-free-v7.py 修改人物材质、站姿、骨骼检查姿势与镜头；scripts/render-free-v7.mjs 修改采样与导出；src/lookdev-v7.html 修改对照页面。可编辑场景 outputs/realism-v7/complete-free-athlete.blend；渲染图同目录；日志与草稿位于 outputs/checks/realism-v7/。这一步没有新增动画时间轴或配音，主动画的修改方式仍按下文执行。

## 本轮 v6：人物静帧验证

打开 outputs/hurdle-character-v6.html，或预览服务中的 http://localhost:8110/outputs/hurdle-character-v6.html 。页面包含同机位的新旧人物面部对照、候选人物半身和全身，并支持查看原尺寸。四张画面均为本地 Cycles 渲染，页面内嵌图片，可离线查看。

这一阶段使用 Renderpeople 免费 Eric 扫描面部，保留面部曲面和 8K UV 贴图，适配本项目 MakeHuman 身体、短裤和跑鞋，制作红黑高领无袖训练上衣，添加眼球反射与短发细丝。它是新的候选人物，身份与旧人物不同。高领用于覆盖当前未完全解决的头颈皮肤连接；造型仍需要视觉验收，不能称为真人实拍级。专业跨栏动作与动作中的变形尚未验证。v5 动画未被替换。

本轮视觉结论：面部细节改善，全身与程序服装仍未达到真人实拍目标，未将候选接入主动画。用户已明确要求后续只使用免费资源，付费候选不再作为当前实施方案，未购买任何付费资产。筛选记录见 docs/REALISM-V6.md。

在本目录独立重建静帧（系统需已安装 Blender 及 FFmpeg）：

    npm ci --cache .cache/npm
    npm run assets:lookdev
    npm run build:lookdev
    npm run render:lookdev
    npm run review:lookdev
    npm run check:lookdev
    npm run preview

提示词与来源见 docs/REALISM-V6.md；人物场景为 outputs/realism-v6/athlete-lookdev.blend，旧人物同机位场景为 baseline.blend，PNG/JPG 同目录。scripts/build-realism-v6.py 修改造型与机位；src/lookdev-v6.html 修改审阅页面；scripts/render-lookdev-v6.mjs 修改采样和导出。此阶段没有新配音和动画时间轴，v5 时间轴仍按下文修改。

Renderpeople 免费资产可用于渲染，仍受其官方许可约束；原始模型、纹理与打包场景仅供本地制作，不应随公开页面或项目压缩包再次分发。公开静帧页面只包含渲染图片，不暴露 3D 资产。下载脚本、原始资料、日志和中间图均保存在本视频目录。

当前主交付 outputs/hurdle-110.html：通过本地代码构建与驱动三维场景，在 Blender Cycles 中逐帧渲染，再嵌入单个 HTML 播放。没有使用现成拍摄视频，也没有调用 AI 视频生成服务，不需要视频模型账号。

这是2.75 秒、24fps、1280×720、默认正常速度的验证样片，含加速跑、两次过栏与落地继续跑动。人物基础网格、皮肤照片纹理和环境全景贴图使用授权资产，不能声称所有原材料都从零生成。人物与动作仍有 CG 感，尚未达到真人实拍级。详见 docs/CODE-RENDER.md。

## 打开成品

直接用 Chrome 或 Edge 打开 outputs/hurdle-110.html。视频、封面、动作定格、脚本和样式全部内嵌，断网也能播放。也可在本目录运行：

    npm run preview
    # http://localhost:8110/outputs/hurdle-110.html

支持暂停、重播、时间轴、¼ / ½ / 1 倍速、逐帧、动作定格和沉浸观看。默认 1× 正常速度。空格播放/暂停，左右方向键逐帧，R 重播，H 沉浸，Esc 退出。无旁白或音轨。

## 独立安装、构建与检查

所有命令在本 README 所在目录执行，不引用其他视频目录或根目录的依赖。

    mkdir -p .cache/tmp .cache/npm
    export TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TMP_DIR="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp"
    export BLENDER_USER_RESOURCES="$PWD/.cache/blender"
    export PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/browsers"
    npm ci --cache .cache/npm
    npm run build
    npm run check
    npx tsc --noEmit

构建使用已经渲染的本地 MP4，无需再次渲染 Blender。依赖由 package-lock.json 锁定，npm 缓存在 .cache/npm/。静态检查验证视频和 3D 模型内嵌、来源标注、导入边界、文件真实路径与 public/ 副本一致性。浏览器检查结果在 outputs/checks/。

## 从代码重建三维动画

重渲染需要系统 Blender 和 FFmpeg，本机验证为 Blender 5.2.2。

    npm run build:scene
    # outputs/offline/hurdles-cycles.blend，可在 Blender 中编辑
    npm run render:scene
    # outputs/offline/frames/frame_0001.png … frame_0066.png
    npm run encode:scene
    # public/assets/offline/hurdles-cycles.mp4 和定格 JPG
    npm run build

脚本默认 CPU 渲染。本机 Metal 后端两次测试没有正常推进；HURDLE_CPU=0 可尝试硬件后端，但不保证可用。重渲染耗时明显高于实时 WebGL。

场景文件已打包纹理，可独立打开。scripts/run-offline.mjs 将 Blender 用户资源和临时目录指向项目内，不保存系统偏好。系统图形驱动自身的缓存不属于项目可完整控制的路径，不能声称所有操作系统缓存都已隔离。

## 修改人物、素材、配音与时间轴

- scripts/build-offline.py：材质、独立服装网格、发丝、跑道、栏架、灯光、镜头、景深、运动模糊与骨骼动画转换。
- sources/offline/poses.json：由本项目原实时动画导出的 163 骨骼矩阵、24fps、120 帧，源模拟时间 3.6–8.558 秒。动作来自 src/app.js 的轨迹、关键姿态与 IK，不是专业运动员动捕。修改动作后需重新导出骨骼数据并重建场景。
- public/assets/athlete-v2.glb 和 sources/makehuman-system/：MakeHuman 基础人物；换模型时需重新匹配权重和骨骼。
- public/assets/offline/stadium_01_2k.hdr：Poly Haven CC0 环境照明及远处背景图片。
- scripts/encode-offline.py：66 张 PNG 合成为2.75 秒正常速度视频，并导出封面和动作定格。
- src/cg-shell.html、src/style-cg.css、src/cg-player.js：HTML 播放器。动作按钮时码应与定格图同步。
- src/remotion.tsx：HurdleCG 使用本地代码渲染的视频。修改时长或帧率后同步更新合成元数据。
- 无旁白。新增录音放在本目录 public/，在 Remotion 中加独立音轨，不引用其他视频目录。

## Remotion 预览与导出

    npm run studio
    # 选择 HurdleCG，2.75 秒代码渲染版
    npm run render
    # outputs/hurdle-110.mp4

Remotion 读取本地 Blender 成片。remotion.config.ts 使用本机安装的 Chrome，其他系统改为本机浏览器路径；需下载浏览器时放在当前项目 .cache/。

原实时 3D 版保留为 Hurdle110。曾使用的库存参考成品与入口源码保留在 outputs/backups/，不是当前生成成果，主构建不依赖该拍摄视频。

## 旧版、来源与隔离

outputs/hurdle-110-3d.html 是原实时 3D 对照版；outputs/hurdle-110-reference.html 是之前的实拍素材参考，不满足当前目标；outputs/backups/ 保存历史备份。提示词见 docs/prompt.md，资产来源见 docs/ASSET-CREDITS.md。

本次源码、素材、动画数据、场景、依赖、缓存、日志、检查图和成品均在当前视频目录内。Tabbit 截图工具固定先写入其系统目录，之后立即移入 outputs/checks/ 并清理对应临时副本。
