# 官网核实与素材来源

核实日期：2026-10-11。网站界面可能更新，视频不固定总模型数、价格或热门排名。

| 画面 / 主张 | 官方来源 |
| --- | --- |
| HF 是模型、数据集与应用的协作平台；三个核心入口 | https://huggingface.co/ ，https://huggingface.co/docs/hub/index |
| 任务、语言、许可等模型筛选 | https://huggingface.co/docs/hub/models-the-hub |
| 模型说明、预期用途、限制、评测与许可 | https://huggingface.co/docs/hub/model-cards |
| 模型卡、Files、Use this model 的具体示例 | https://huggingface.co/openai/whisper-small |
| 公开模型下载及不同客户端 | https://huggingface.co/docs/hub/models-downloading |
| Spaces 的应用托管；Gradio、Docker、静态页面 | https://huggingface.co/docs/hub/spaces-overview |
| 语音转文字示例页面 | https://huggingface.co/spaces/Xenova/whisper-web |
| 数据预览的当前名称 Data Studio | https://huggingface.co/docs/hub/data-studio |
| 推理服务及支持的模型 | https://huggingface.co/docs/inference-providers/index |
| 私有/受限资源访问、token 权限 | https://huggingface.co/docs/hub/security-tokens |
| 模型/数据/Space 社区协作与 Collections | https://huggingface.co/docs/hub/index |

## 制作说明

- 所有网站截图均通过实际访问官网抓取，保存在 `public/screens/`；截图上的鼠标、黄色框和中文提示为后期教学标注。
- Whisper Web 的步骤遵循实际界面；播放器截图使用应用内默认公开样例，只展示操作，没有虚构转录结果。通过加载此样例核实了 Transcribe Audio 和 Settings 的实际位置。
- 当前 Whisper Web 默认是英语模式；中文录音需勾选 Multilingual、选择 Chinese、任务选择 Transcribe。已在旁白和设置截图中补充此步骤。
- 未创建 Hugging Face 账号、未填写表单、未上传用户文件、未申请访问、未创建 token、未调用付费推理。
- 使用许可和算力要求因模型而异；在线演示可能需要下载、排队或登录。只介绍选择方法，不承诺所有模型可免费在线运行。
- HF 标志取自官网 `/front/assets/huggingface_logo-noborder.svg`，用于识别介绍对象，非官方出品。
- 中文字体为 Google Fonts 的 Noto Sans SC，字体与 OFL 许可位于 `public/fonts/`。
- 中文旁白为 `zh-CN-XiaoxiaoNeural`，通过 edge-tts 生成。原句见 `narration.json`。
- Remotion BasicCaptions 来源保存于 `basic-captions-source.md`，组件按官网源代码复制。

## 路径隔离例外

Playwright CLI 的 Unix socket 在 macOS 上受短路径限制，视频目录绝对路径超过限制，传输 socket 临时使用 `/tmp/hf-getstarted-8653/`。素材、浏览器 profile、快照、会话数据和日志均指向本视频目录。抓取结束时关闭专用会话并清理该 socket 目录。

首次 CLI 启动在默认系统缓存生成了本次 workspace 的会话目录；已立即移入 `.cache/failed-browser/`。这里如实记录工具初始化行为，不声称它从未使用系统缓存。
