> 历史方案，已被用户后续确认的本地代码渲染方案取代。未执行 imagegen，也未生成 AI 视频。当前要求见 CODE-RENDER.md。

# 当前目标：提示词生成原创写实动画

2026-10-21 用户澄清并确认：使用 AI 视频模型根据提示词生成全新的人物、场景与跨栏动作，再通过 HTML 播放。不得把已拍好的库存视频当作生成成果。默认正常速度（1×）。之前的实拍页面仅为旧版参考，不满足此次生成目标。

## 执行状态

- 原创人物参考首帧：准备通过内置 imagegen 生成。
- 原创动态视频：尚未生成。
- 当前会话发现的 Runway、Higgsfield 等视频插件均为管理员禁用，不能调用。等待用户确认可使用的视频平台或生成通道。
- 参考图与分镜不能替代动态视频；对图片平移缩放也不能算跨栏动作生成。

## 首帧生成提示词

Use case: photorealistic-natural.
Asset type: original reference first frame for an AI-generated sports film, landscape 16:9.
Create a completely original fictional adult East Asian male hurdler, approximately 25 years old, with a lean powerful sprinter's physique and anatomically natural proportions. He has short textured black hair, a focused natural face, realistic skin pores, slight perspiration, subtle skin tone variation and natural muscle definition. He wears a red technical running singlet, fitted black track shorts, a small white bib reading "04", and realistic track spikes, with natural fabric folds.
An outdoor athletics stadium in soft morning sidelight: textured red rubber track with accurate straight white lane markings, a green infield and distant stadium seating. The athlete is in the left half of the frame running from left to right, about three metres before a single white-and-dark-metal men's hurdle in the right half. He is one stride before his approach to the hurdle, running at normal speed, one forefoot pushing against the track, the opposite knee driving forward, arms naturally counterbalancing. The hurdle is physically planted on the track and has no brand name. Show his entire body, both feet, head and the full hurdle with comfortable margins. Track, person and hurdle share a consistent perspective and natural contact shadows.
Camera at waist height, a three-quarter side view that reveals his face and body, 50 mm sports cinema lens, restrained depth of field with the entire athlete and hurdle sharp. Convincing documentary sports photography, unretouched skin and believable outdoor exposure. Natural motion blur only at extremities, not the face. Realistic materials and anatomy; the scene should look like a frame from a high-end live-action sports film. No collage, UI, watermark, stylized rendering, waxy skin, glamour retouching, duplicated limbs, deformed hands or identity of any real athlete. Only the bib has text.

## 动态生成主提示词（图生视频）

Use the supplied first frame as the visual reference. A single continuous photorealistic sports-film shot. The same adult hurdler runs left to right at natural real-time speed, approaches the hurdle, clears it once with an efficient low trajectory, lands and continues sprinting. His lead knee drives up before the lower leg extends over the hurdle; his bent trail leg sweeps sideways and recovers forward, his torso inclines naturally, and his arms balance the movement. His lead foot snaps down to contact the track and he continues with grounded, rhythmic strides. The camera tracks smoothly alongside him at waist height, keeping his whole body and the hurdle visible during clearance. Natural muscle motion, subtle facial effort, believable cloth movement, consistent sunlight and contact shadows. Preserve his face, red singlet, black shorts and shoes throughout the shot. The hurdle stays physically stable in the same lane. Normal speed, continuous forward movement, documentary sports cinematography.

## 首次生成设置与验收

- 第一轮只生成一个完整过栏动作，建议约 6–8 秒。实际时长与分辨率使用所选平台支持的设置。
- 画幅优先 16:9。先验证动作，再决定是否需要竖屏构图；禁止拉伸画面。
- 正常速度，关闭慢动作或自动变速；不添加旁白、字幕与片内 UI。
- 人物面容、服装、手脚和身材在整段中一致。
- 起跨、越栏、落地必须连续；栏架不融化，手脚不穿栏，接地不滑行，不漂浮。
- 动态视频生成后逐帧检查过栏与落地，再集成 HTML。无法通过的样片记录问题并迭代，不以提示词中的“4K”“超写实”等词代替验收。

## 后续镜头

在主过栏镜头通过后，再以同一角色参考图制作短暂起跑准备、连续栏间跑、冲线减速等镜头。每个独立动作单独生成和检查，再剪辑；不要求一个短镜头凭空覆盖完整 110 米或十个栏。

## 官方参考

- Runway 的图生视频说明要求提示词重点描述运动：[Creating with Gen-4.5](https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5)。
- 提示词与迭代：[Runway Academy Prompting Guide](https://academy.runwayml.com/guides/prompting-guide)。
- API 接入需要服务账户与凭据：[Runway API Getting Started](https://docs.dev.runwayml.com/guides/using-the-api/)。不要把凭据写入前端 HTML 或提交到项目源码。
