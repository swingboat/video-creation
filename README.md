# Video Creation

当前工作区按视频拆分为独立 Remotion 项目。每个项目都有自己的源码、素材、依赖、脚本、临时目录、检查结果和成品；不同视频之间不引用彼此的文件。执行规则见 [AGENTS.md](AGENTS.md)。

Git 仓库保存源码、配置、文档及非视频制作素材。视频文件（包括成片、预览和参考视频）、`outputs/` 等输出目录、项目压缩包、依赖、缓存及研究用第三方仓库副本由 `.gitignore` 排除，仍保留在本地。下表的成片链接指向本地产物；克隆后需自行准备项目所需的视频素材，并按各视频 README 导出。

| 视频 | 独立项目 | 规格 | 完整 MP4 | 默认预览 |
|---|---|---|---|---|
| U-Net 中文讲解 | [unet-explainer](videos/unet-explainer/README.md) | 1920×1080 / 30fps / 158.33s | [unet-explainer.mp4](videos/unet-explainer/outputs/unet-explainer.mp4) | http://localhost:3210/UnetExplainer |
| 未来科技标题 | [future-title](videos/future-title/README.md) | 1920×1080 / 30fps / 10s | [future-title.mp4](videos/future-title/outputs/future-title.mp4) | http://localhost:3213/FutureTitle |
| 海边滑板手绘动画 | [seaside-skate](videos/seaside-skate/README.md) | 1920×1080 / 30fps / 10s | [seaside-skate.mp4](videos/seaside-skate/outputs/seaside-skate.mp4) | http://localhost:3214/SeasideSkate |
| 3D 口腔门诊宣传 | [dental-clinic-city](videos/dental-clinic-city/README.md) | 1080×1920 / 30fps / 30s | [dental-clinic-city.mp4](videos/dental-clinic-city/outputs/dental-clinic-city.mp4) | http://localhost:3215/DentalClinicCity |
| 基础示例 | [hello-remotion](videos/hello-remotion/README.md) | 1280×720 / 30fps / 3s | [hello-remotion.mp4](videos/hello-remotion/outputs/hello-remotion.mp4) | http://localhost:3212/HelloRemotion |

## 使用各视频

进入所需的视频目录，例如：

```bash
cd videos/unet-explainer
npm ci
npm run dev
npm run check
npm run render
npm run pack
```

已安装的依赖均位于各自 `node_modules/`。运行 `npm ci` 可按本目录锁定文件重新安装。`npm run check` 检查类型、依赖与导入隔离、构建、Composition 参数、关键帧和 1 秒导出片段。完整视频输出在 `outputs/`，检查片段位于 `outputs/checks/`，不要将检查片段当作完整视频。

`npm run pack` 在本视频 `outputs/` 中生成项目 ZIP，仅包含本视频的源码、配置、素材、脚本、说明和输出，排除安装依赖及缓存。解压后在该项目目录运行 `npm ci` 即可独立预览和导出。

根目录 `npm run dev` 仅是启动 U-Net 的快捷入口。其他快捷入口为 `npm run dev:future`、`dev:seaside`、`dev:clinic`、`dev:hello`；每个视频本身均不依赖这些快捷入口。其他预览服务需分别启动，对应端口已在各自脚本中设置。

## 迁移与资料

原有视频源码、素材、旁白、字幕、MP4、截图、分镜和检查报告已归入各视频目录。口腔门诊和 U-Net 的字体加载代码已分别复制到本视频 `src/fonts.ts`，本地字体各自保存在 `public/fonts/`。共享 Composition 注册和运行脚本已经拆分，原来的根目录 `src/`、`public/`、`scripts/`、`out/` 和 `outputs/` 已整理清除。

U-Net 的 MP4、旁白 WAV 和 SRT 已用 SHA-256 确认迁移前后内容一致。未来标题、海边滑板和口腔门诊的完整 MP4 来自迁移后的独立项目导出。各项目的迁移记录在 `outputs/checks/migration-report.json`，独立检查结果在 `outputs/checks/isolation-report.json`。

Remotion 原始集成的代码审阅资料独立保留在 [docs/remotion-review.md](docs/remotion-review.md) 和 `.cache/remotion-review/`，供工作区查阅；视频运行不使用这些资料。已安装的 Remotion Skills 保留在工作区 `.agents/skills/`。
