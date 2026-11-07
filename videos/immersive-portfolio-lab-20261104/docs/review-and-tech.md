# 参考帖 Review 与技术收集

参考：[Berryxia 帖子](https://x.com/berryxia/status/2055784649830670829) · [David Heckhoff 网站](https://david-hckh.com) · [源码](https://github.com/davidhckh/portfolio-2025)。核对日期：2026-11-04。

## Review 结论

这是交互式 portfolio 的约 17 秒操作录屏。它的吸引力来自有表演的角色、统一的 3D 美术和空间连续性，技术栈只是实现手段。参考素材为 1280×720，有音轨；本地 `research/reference.mp4` 仅供研究，未拼接进试作。

- 0–3 秒：奶油色办公室，角色在桌前挥手、转向屏幕。双显示器、植物、软阴影让场景有生活感。
- 约 3–7 秒：切入蓝色实验室，角色成为青色全息投影；身份与技能面板环绕人物。
- 约 7–10 秒：明亮项目列表，CubeWar、Quibbo、Sharkie、Particles 等卡片。
- 约 10–17 秒：联系场景、快递纸箱，角色由打盹转为站立抱臂，形成小型叙事收尾。

可改进的地方：原演示滚动很快，项目内容不易读；导航与正文较小，手机观看需要放大。因此本试作延长到 24 秒、1920×1080，保留大字标题并让项目页停留更久。

## 已核实的技术及职责

| 技术                             | 原项目声明版本 | 作用                                                 | 证据/学习入口                                                             |
| -------------------------------- | -------------- | ---------------------------------------------------- | ------------------------------------------------------------------------- |
| Three.js                         | ^0.181.0       | WebGL 场景、模型、相机与材质                         | [官方文档](https://threejs.org/docs/)；`src/three/`                       |
| GSAP / GreenSock                 | ^3.13.0        | 角色权重、相机路径、场景切换、交互反馈的时间编排     | [官方文档](https://gsap.com/docs/v3/)；`src/animations/`                  |
| Lenis                            | ^1.3.11        | 平滑滚动，并使 DOM 与 WebGL 由共同进度驱动           | [官方仓库](https://github.com/darkroomengineering/lenis)                  |
| Vue 3                            | ^3.5.22        | 导航、文本、项目列表和页面 UI                        | [官方指南](https://vuejs.org/guide/introduction.html)                     |
| TypeScript                       | ~5.9.3         | 类型与模块结构                                       | [官方手册](https://www.typescriptlang.org/docs/handbook/intro.html)       |
| Vite                             | ^7.1.7         | 开发服务和打包                                       | [官方指南](https://vite.dev/guide/)                                       |
| GLSL + vite-plugin-glsl          | ^1.5.4（插件） | 全息扫描线、透明度、角色渐变、网格和电子光效         | 仓库 `src/three/shaders/`                                                 |
| Howler                           | ^2.2.4         | 鼠标、键盘、通知、角色等音效与 audio sprite          | [官网](https://howlerjs.com/)；仓库 `sounds/`                             |
| GLB + AnimationMixer             | Three.js API   | 模型加载、角色骨骼动画与动画混合                     | [官方 AnimationMixer](https://threejs.org/docs/pages/AnimationMixer.html) |
| 烘焙贴图 + Matcap + Sprite atlas | 美术/渲染方法  | 办公室明暗预烘焙；身体使用 Matcap；表情使用 4×4 图集 | 仓库 `room.webp`、`matcap-*`、`face-spritesheet.png`                      |

版本来自抓取时的 `package.json`，不是建议盲目升级到这些版本。帖子中的“物理反馈”是视觉描述；依赖清单及本次阅读到的实现未发现 Rapier/Cannon 等物理引擎，不将其写成已证实的物理模拟。模型究竟用哪个 DCC 软件制作也未在本次核对中证实。

## 本试作实际采用

- Remotion 4.0.540 + React 19：固定帧率、可拖动时间轴、镜头独立预览和导出入口。
- Three.js 0.181.0 + React Three Fiber + ThreeCanvas：真实 3D，不是从帖子截取画面拼接。
- 角色与办公室、纸箱模型，以及相关贴图，使用作者允许的个人学习用途本地副本；各画面保留 David Heckhoff 署名。项目卡片展示的仍为作者作品。
- 角色用骨骼动画，以当前帧计算绝对动画时间；全息材质、扫描环、镜头运动及排版为本项目实现。
- GSAP 用暂停 timeline 的绝对 seek 编排相机/角色变换，以 Remotion 帧数为时钟，不用独立实时 ticker。
- 视频没有滚轮输入，故不安装 Lenis。没有把 Vue 网站整个搬进 React。
- 音乐为本项目代码合成的轻量电子配乐和转场音效，无旁白；可替换为本目录内的自有音频。

## 许可与署名

该公开仓库使用自定义许可，**不是 MIT**：允许个人、教育用途，要求保留作者署名与原站链接；商业用途、转售或大部分内容再分发需要作者许可。原许可快照见 `research/original-license.md`。本项目定位个人学习试作；不要把借用的角色、办公室和项目缩略图作为自有作品售卖。

David Heckhoff created and designed the original portfolio and the reused 3D assets.
Original portfolio: https://david-hckh.com
Original source: https://github.com/davidhckh/portfolio-2025
