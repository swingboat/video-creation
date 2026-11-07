## 10 秒海边滑板手绘动画

新增 `SeasideSkate`：1920×1080、30 fps、300 帧。Codex 预览地址：[海边滑板动画](http://localhost:3214/SeasideSkate)。若 Studio 已停止，运行 `npm run dev`，在画面下方点击播放；扬声器按钮可控制声音。

这是由手绘位图素材编排的分层动画：0–2 秒女孩滑入海边公路；2–3.3 秒蹬地；3.3–4.8 秒双脚站稳；4.8–7 秒张开双臂滑行；7–10 秒拉远并滑向弯曲海岸公路。女孩保持同一套人物设计，前脚与滑板贴合，轮子转动，头发、裙摆与后腿采用逐帧变形。背景包含海面波光、云层和海鸥，野花前景移动速度快于远景，形成视差。

内置 imagegen 生成的海岸全景、人物三姿态透明素材和野花透明素材保存在本项目 `public/seaside/`。完整提示词、最终文件路径与 SHA-256 见 `public/seaside/asset-prompts.json`；保留原始素材，动画变形在代码中完成。

声音由本项目的 `scripts/create-seaside-audio.py` 合成，包含海浪、海风和滑板滚动三条 44.1 kHz 双声道 WAV，随距离变化调整滑板音量。它们是原创声音设计，并非现场录音。画面不含标题、字幕或 Logo。

代码入口为 `src/SeasideSkate.tsx`；海岸与人物可以从 Studio 的 `SeasideSkate-Layers` 文件夹打开独立时间线。当前预览已完成 TypeScript、Composition 发现、关键帧尺寸与音频长度/电平检查，并检查了 Studio 播放和运行日志。

`npm run still` 生成第 165 帧截图；如需导出 MP4，运行 `npm run render`，输出 `outputs/seaside-skate.mp4`。迁移前交付为可播放预览；迁移时已补齐独立项目的完整 MP4。

