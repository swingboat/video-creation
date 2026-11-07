# 瓶中风暴 · 小兔与鱼群（游动优化版）

20 秒 / 24fps / 1280×720 / 480 帧。Blender Cycles 逐帧渲染；全部模型、关节运动、玻璃折射、风雨与小型拟音均在本项目内制作。

鱼群 v3 使用有厚度的流线鱼身、珠光鳞片、双侧眼睛、鳃线、分叉尾鳍及细鳍条。每条鱼有 20 个循环形态，摆动从前身传到尾端；尾鳍、胸鳍和背鳍柔软跟随。九条鱼分两层反向游动，沿按弧长推进的圆滑路线连续游过瓶内。朝向跟随速度切线，转弯带倾斜和身体弯曲，摆尾相位独立，频率随游速变化。全部烘焙为原生关键帧，不依赖播放回调。

在原有瓶中风暴场景中，小兔看向画纸、走近积木、蹲下双手抱起、绕到瓶前搬到左侧、放稳、拿笔，再画出新的花朵。连续镜头跟随搬运，并在画画时推近。角色沿用原来暖白玩偶与蓝色领结的造型。

上一版小兔视频与工程包保留在 outputs/bottle-storm-bunny-20s.mp4 和 outputs/bottle-storm-bunny-project.zip；鱼群修改前的原生场景快照在 outputs/versions/bunny-v2/。

初版 14 秒视频与工程包仍保留在 outputs/bottle-storm-14s.mp4 和 outputs/bottle-storm-project.zip。旧视频和旧工程包不随新工程包重复打包。原始 Blender 场景快照在 outputs/versions/v1/；角色版本从本目录内的快照加载，不引用其他视频。

## 独立安装

系统工具：Node.js 20.19+ / 22.13+ / 24+、Blender 5.2、FFmpeg、Python 3.13。制作机使用 Blender 5.2.2、M3 Pro Metal GPU 与系统 Chrome。

在本视频目录执行：

```bash
mkdir -p .cache/tmp .cache/npm .cache/python
export TMPDIR="$PWD/.cache/tmp"
export TMP="$PWD/.cache/tmp"
export TEMP="$PWD/.cache/tmp"
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

预览选择 BottleStorm，默认 http://localhost:3076/BottleStorm 。成片为 outputs/bottle-storm-bunny-fish-20s.mp4。正式画面 public/bunny-fish-picture.mp4；音轨 public/storm-soundscape.wav。压缩包含已生成素材，可独立安装、预览与导出，不必重渲三维。

Remotion 优先使用系统 Chrome。其他平台在 remotion.config.ts 指定本机 Chrome；下载浏览器时须下载到本视频自己的目录。npm run build 输出 outputs/remotion-bundle/。

## 修改动作并重建

```bash
npm run scene
node scripts/run.mjs audit-bunny
node scripts/run.mjs audit-fish
node scripts/run.mjs audit-scene
npm run preview:scene -- 73 193 313 397 445
npm run render:scene
npm run encode
npm run audio
npm run render
```

- scripts/fish_motion.py：九条鱼的巡游路线、空间层次、速度与摆尾相位，输出 docs/fish-paths.json。改变鱼速、尺寸、方向和轨迹后，运行 `node scripts/run.mjs fish-paths` 再运行 `node scripts/run.mjs upgrade-fish`，即可保留现有小兔动作而重新生成鱼群。
- scripts/upgrade_fish.py：从本目录 outputs/versions/bunny-v2/bottle-storm.blend 加载场景，移除旧鱼，制作鱼身、鳍膜和鳍条，烘焙连续游动与身体变形。
- `npm run scene`：依次从 v1 快照重建小兔、更新本目录兔子场景快照、再生成新版鱼群。
- scripts/bunny_motion.py：行动时间、路线、脚步接触点、重心、抓握、积木与笔轨迹。站立期足底锁在世界坐标，抬脚期使用连续弧线；手臂与双腿由双段 IK 计算后烘焙为原生关键帧。
- scripts/animate_bunny.py：加载本目录内原始场景，替换静态兔子，生成关节部件、眨眼与耳朵跟随，烘焙全部动作，并保存 public/bottle-storm.blend。积木和笔各使用单一连续变换轨迹，手跟随物体接触点；新画线随笔尖进度出现。
- 相机：先保留全景，再跟随左移，最后平缓进入画画近景；景深随推近渐变。
- scripts/render_scene.py：预览低采样；正式版本 32 samples、固定噪声种子、降噪、适量运动模糊，输出 outputs/frames-fish/。已有有效帧可续渲；渲染报告带场景 SHA-256 指纹。修改动作后应先将旧帧移入本项目内的版本目录，场景与旧帧不一致时脚本会拒绝续渲，防止新旧混用。
- scripts/synthesize_audio.py：NumPy/SciPy 合成 48kHz 立体声风雨、海浪、雷声、足音、积木落桌和画笔摩擦。没有旁白、字幕和配乐。需要旁白时，将本视频自己的录音放进 public/ 并在 src/Composition.tsx 添加 Audio 层。
- src/Composition.tsx：最终视频与声音的时间轴、音量；画面与音轨为独立 JSX 节点。

更改时长或 fps 时，需同步 bunny_motion.py、Remotion Composition、run.mjs 编码帧数与 docs/timeline.json，并重新生成声音和三维帧。

## 闪光说明与检查

旧版明显的整屋亮暗变化由瓶内闪电及同步辅助光引起，亮度与闪电强度相关系数约 0.99，并非窗外闪电。角色版本将全屋闪光降到原来的 30%，瓶内补光降到 72%，保留雷雨气氛。采样由 16 提高到 32，以减少细碎的渲染噪声闪烁。

outputs/checks/bunny/contact-audit.json 记录手脚可达性、站立脚滑动、抓握偏差、笔杆与头/身体的间距、角色及手持积木的镜头范围。积木放下后成为布景道具，镜头转向画纸时允许短暂裁切；最终画画近景能看见积木与画纸。

outputs/checks/fish/before-after-8s.mp4 提供前 8 秒鱼群运动的同步放大对比，便于观察旧版原地漂移与新版游动的区别。

outputs/checks/fish/motion-audit.json 检查全部 480 帧的鱼身及鱼鳍与玻璃、砂床、水面的距离、鱼身之间的相交、形态混合权重和朝向连续性。屏幕上前后鱼的遮挡属于不同深度的正常投影。

outputs/checks/scene-audit.json 检查原生波浪与船体耦合及外部素材依赖；frame-qa.json 检查 480 帧完整性、空帧与重复帧；final-check.json 检查代码、路径与最终视频元数据。

动作预演 public/previews/bunny-blocking.mp4 使用简化的 Workbench，隐藏玻璃和水面以检查四肢与地面接触。正式成片使用完整 Cycles 材质与光照。

## 隔离与打包

scripts/run.mjs 把受控临时目录、缓存、Blender 配置和输出指向本视频目录。没有跨视频运行依赖或素材链接。系统 Blender、FFmpeg、Python、Chrome 属于允许的系统工具。

制作机发生过 Metal 二进制编译归档崩溃；run.mjs 设置 CYCLES_METAL_DISABLE_BINARY_ARCHIVES=1 绕过该归档路径，仍使用 Metal GPU 的 Cycles。相关崩溃报告已移入 outputs/checks/fish/ 并清理系统日志副本。

macOS Metal 驱动的系统级编译缓存、既有浏览器自身缓存不接受本项目路径控制，未声称它们已隔离。初版制作时的 Metal 编译崩溃报告已移入本项目输出目录并清理原副本。

```bash
.venv/bin/python scripts/package_project.py
```

工程包 outputs/bottle-storm-bunny-fish-project.zip 包含源码、锁文件、可编辑 Blender 工程、生成素材、制作说明、检查报告、成片及重建所需的原场景快照；不包含可重建的依赖、缓存、逐帧 PNG 和旧动作预演帧。
