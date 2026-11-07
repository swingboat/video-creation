## 10 秒未来科技标题动画

新增 `FutureTitle`：1920×1080，30 fps，共 300 帧（10 秒）。在 Codex 内置浏览器打开 [动画预览](http://localhost:3213/FutureTitle)，点击播放即可观看；若服务停止，运行 `npm run dev`。

动画节奏：0–3.3 秒蓝紫粒子聚合为中文标题；3.3–6.15 秒标题停留；6.15–7.4 秒粒子消散；7.2–10 秒 Logo 缩放出现。背景包含流动光带、漂移网格、透视地面网格和星点，所有运动由当前帧驱动。

当前文案为“未来，正在发生”，副标题为“向下一刻，出发”，结尾使用可替换的 `FUTURE` 几何占位 Logo。可以在 Studio 右侧 Default Props 修改 `title`、`subtitle`、`logoText`、`logoSrc`，或直接编辑 `src/Root.tsx` 中 `FutureTitle` 的 `defaultProps`。自己的 Logo 放入 `public/`，`logoSrc` 填相对该目录的路径，例如 `logo.png`。

MiSans Regular / Bold 原始 WOFF2 文件来自[小米官方 MiSans 下载](https://hyperos.mi.com/font/download)，保存于本项目 `public/fonts/`，来源和 SHA-256 见该目录的 `misans-source.json`。粒子轮廓在字体加载完成后采样，避免预览和渲染使用替代字体。

关键帧：`outputs/future-title-particles.png`（2.4 秒）、`outputs/future-title-main.png`（4.5 秒）、`outputs/future-title-logo.png`（9 秒）。已通过 TypeScript 检查、Composition 发现与关键帧渲染验证，并在 Studio 中播放检查。预览是本次交付；如需 MP4，可运行 `npm run render`，输出 `outputs/future-title.mp4`。重新生成标题截图可运行 `npm run still`。

