# 第二版制作记录

日期：2026-11-05。

## 资产与来源

- `traveler-reference-v2.png`：本次使用内置 imagegen 原创生成的人物建模参考。
- `public/textures/limestone-ink-v2.png`：内置 imagegen 生成的完整石材纹理；WebP 为网页使用的同内容格式转换。
- `mountain-environment-v2.blend`：本次 Blender 脚本创建的原创场景资产。包含侵蚀岩壁、石板、曲松针叶、鸟居、石灯及碎石。
- `public/models/mountain-environment-v2.glb`：从 Blender 导出的网页环境资产，14 个材质合并网格。
- `public/textures/pine-canopy-v2.png`：内置 imagegen 生成的透明松针簇，作为实际 3D 树冠的交叉裁切卡片材质，保留透明度。
- `traveler-tripo-h25-raw.glb`：使用上述人物参考在用户已登录的 Tripo Studio 生成，H2.5 模型。原始 453,394 面。
- Tripo 项目：`563da098-11b9-4319-baf0-58d30ab62857`，由本次制作创建。

## 当前已执行的 Tripo 操作

- 生成 H2.5 带纹理人物：40 免费积分。
- 将原始人物重拓扑至 19,375 面：35 免费积分。
- Tripo 自动绑骨：20 免费积分。
- 合计使用 **95 免费积分**，余额从 200 变为 105。
- 正常 GLB 导出实际包含蒙皮及 52 个源关节。UI 中的会员「Export Skeleton」开关一度被误判为阻止普通蒙皮导出；本次合法下载的 GLB 经解析与 Blender 导入确认带有完整蒙皮，未修改禁用控件或绕过导出限制。
- Blender 整理后有 53 个骨骼（包括导入端点骨），原创建立 Idle / Walk / Run / Jump / Fall / Land 六个独立动作片段。没有购买在线动作。
- 纹理优化为最高 2048 像素，人物网页 GLB 约 3.9 MB，环境 GLB 约 7.2 MB。原始 4K 材质与高面数源模型保留在 `docs/art/` 中。

所有操作均在现有免费额度内执行，没有购买会员或充值。免费账户的模型公开且限非商用；本次作品是个人学习试作。

## 图像提示词

模式：内置 imagegen；不是 CLI/API fallback。生成文件复制到本项目，原始工具输出按工具要求保留在 Codex generated_images 目录。

石材：`Seamless albedo texture for a real-time 3D game rock cliff material. Weathered Japanese pale limestone, hand-painted ink wash, irregular vertical charcoal-grey fissures and branching hairline cracks, subtle sedimentary striations, mineral grain, muted olive staining. Flat orthographic surface, even diffuse light, no perspective, objects, landscape, directional shadows, border, vignette, labels or watermark. Restrained cream-grey and charcoal palette.`

旅人：`One full-body adult wandering traveler in a relaxed A-pose, front three-quarter view, plain warm off-white background. Broad woven straw kasa hat, charcoal-indigo layered traveling robe with readable folds and hems, muted brick-red obi and trailing scarf, off-white calf wraps, dark split-toe sandals, wrist wraps, leather travel pouch, sheathed sword at back. Original restrained hand-painted Japanese ink wash game art, anatomically plausible adult proportions, soft studio illumination. Entire body visible, hands separated from torso, no pedestal, environment, text, multiple figures, logos or recognizable copyrighted character.`

松针：`One mature Japanese black pine foliage pad, broad asymmetrical umbrella-shaped cluster of dense fine needle sprays, shallow oblique view, irregular ragged silhouette and small natural gaps. Muted deep olive green and charcoal, subtle varied greens, thin twigs concealed inside foliage. Transparent alpha background and empty margin, no trunk, pot, landscape, ground, external cast shadows, text or watermark. Dense enough to read at medium distance in a real-time game.`

完整最终提示词见 [image-prompts-v2.json](image-prompts-v2.json)。图片保存于本目录的人物参考与本项目 `public/textures/`。内置工具原始输出按工具要求保留在 `/Users/huyin/.codex/generated_images/01a1a6a7-4ae9-7e12-b925-a8a46a64ef15/`，运行与重建只引用本项目副本。

## 已实现的第二版效果

- 两个独立本地 GLB，资产加载进度和失败重试提示。
- 裂隙岩壁、磨损边缘、旧石板、曲松、透明针叶簇、鸟居和石灯。
- 六动作混合、起落状态衔接；行走速度调整到与人体步态更匹配的 3.2 单位/秒，快跑 5.3 单位/秒。
- 可读性更好的跟随镜头、碰撞避让；桌面接触阴影，移动端简化渲染。
- 保留原有三枚山印、途中存档和通关循环。

披风与衣袍使用骨骼蒙皮，未实现真实布料物理；攀爬、索道等玩法仍属于后续关卡范围。
