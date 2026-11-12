# 篮球连续蒙皮动作测试

当前交付是 5 秒、1280×720、30 fps 的本地绑定验证，包含 6 名球员与 6 名观众。它用于检查持球、屈膝、起跳、出手、落地及多人反应的衔接；尚未完成流川枫的动漫脸型、发型、宽松球服，也不是最终的 20 秒成片。已确认的造型图保存在 `public/references/rukawa-approved.png`。

每个人物使用同一个连续人体网格及原生 163 骨骼权重，衣服也绑定到骨骼；动作使用世界坐标脚底约束、双段 IK 和连续轨迹烘焙。没有切换角色姿态图片。两支球队、看台与机位均为动作检查占位。

## 独立安装与预览

需要系统已安装 Node.js、Blender 5.2、FFmpeg 和 Google Chrome。依赖版本锁定在本目录。解压工程后，在其父目录执行以下命令；当前工作区也可直接进入这个视频目录。

```sh
cd rukawa-continuous-rig-study-20261109
mkdir -p .cache/tmp .cache/npm
TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp" npm ci --cache .cache/npm
npm run dev
```

打开 http://localhost:3094/ContinuousRigStudy 。现成的本地画面素材已包含在 `public/rig-study-picture.mp4`，预览不需要重新渲染 Blender。

## 重建、检查与导出

```sh
npm run scene                         # 重建绑定与 150 帧动作，约 30 MB 的 .blend
node scripts/run.mjs preview           # 关键姿态 PNG
node scripts/run.mjs audit             # 从实际骨骼、蒙皮鞋面采样接触误差
npm run render:scene                   # 本地 Blender 渲染 150 帧
npm run encode                         # 将帧序列合成画面素材
npm run render                         # Remotion 导出带测试标签的 MP4
npm run check                          # 类型、路径隔离、视频解码与接触误差检查
npm run package                        # 当前工程的独立 ZIP
```

`run.mjs` 将工作目录、临时文件、npm 缓存、XDG 缓存及 Blender 用户配置限定在本视频目录；使用系统已安装 Chrome，不下载浏览器。直接运行 npm 安装时使用上面的环境变量。所有生成文件和日志保留在本目录。压缩包排除可重建的 `node_modules`、缓存和 PNG 全帧序列，保留锁文件、源素材、绑定工程、成片及检查报告。

## 修改素材、动作和时间轴

- `scripts/build_rig_study.py`：`specs` 定义角色、球队与位置；`root_position`/`foot_plan` 定义支撑脚和移动；`hip_delta` 定义起跳与落地；`held_ball`/`ball_world` 定义持球和抛物线；逐帧绑定段定义手腕和肘膝 IK。动作曲线使用连续插值，并修正相邻四元数的符号以避免插值翻转。
- `public/models/human-base.glb`：独立复制的人体基础网格与蒙皮权重。重新生成场景不读取任何其他视频。
- `src/Root.tsx`：测试标签、阶段说明、Remotion 5 秒时间轴。改变长度时须同步 Blender 帧数、渲染脚本和编码帧数。
- `public/fonts/NotoSansSC.ttf`：本地测试标签字体。
- 本片没有配音或配乐。需要音频时将有权使用的文件放入本目录 `public/audio/`，在 Root 中通过 `@remotion/media` 的 Audio 引用，并按新时间轴调整。

## 验证边界

`outputs/checks/rig-audit.json` 采样真实绑定结果，检查脚底在支撑期的滑动、手掌目标、骨骼连接和尺度稳定性。它不能证明动作已经达到成片的自然程度。需要结合视频确认肩肘姿态、着地节奏、手指和球的关系。该测试保留占位外观，不能作为已完成动漫造型或 20 秒故事的证明。

基础人体来源与许可见 `docs/provenance.md`。已确认的动漫参考仅作为本项目制作参考。
