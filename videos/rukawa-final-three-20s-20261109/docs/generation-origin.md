# 生成素材

本轮使用内置 image_gen，根据本目录的已确认原画生成跳投与封盖图。完整提示词保存在 new-asset-prompts.json。

- public/art/rukawa-release.png 的工具源文件：/Users/huyin/.codex/generated_images/01a1bf2e-120f-7a71-87d1-7345a8c053af/exec-55a01582-536d-4432-98b6-0721c3092f19.png
- public/art/defender-jump.png 的工具源文件：/Users/huyin/.codex/generated_images/01a1bf2e-120f-7a71-87d1-7345a8c053af/exec-4045c0f6-e911-4161-b2bf-5a8c61024b23.png

上述位置是工具最初的输出位置。确认与项目素材逐字节一致后，本轮两份工具原始文件已移入本目录 `.cache/generation-originals/`，外部原始文件已移走。运行素材在 `public/art/`；工程不依赖工具源目录。持球修正图、球馆、配角图集和篮球图集是之前已生成素材的独立副本；复制后不读取其他视频目录。
