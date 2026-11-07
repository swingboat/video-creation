# v7 免费完整人物测试（2026-10-21）

- 人物：[Microsoft Rocketbox / Sports_Male_04](https://github.com/microsoft/Microsoft-Rocketbox/tree/master/Assets/Avatars/Professions/Sports_Male_04)，Copyright (c) 2020 Microsoft，MIT。完整许可位于 sources/research/realism-v7/rocketbox/LICENSE.md；官方来源 URL、字节数、SHA256 位于同目录 download.json。保留原配头部、身体、运动服、跑鞋、骨骼、颜色/法线/反射贴图。项目新增两级细分、材质参数、站姿、骨骼检查姿势、短发细丝和本地渲染。
- 灯光及体育场远景继续使用项目已有 Poly Haven Stadium 01（CC0）；跑道与场景继续由本项目代码构建。
- v7 对照页内的 v6 旧图仍按下文 Renderpeople / MakeHuman 许可描述；新人物的 MIT 许可不改变旧图及旧模型的许可。
- Deep3DStudio Athletic African man walking 223 只核对了官方描述与下载登录要求，没有取得原始文件或用于渲染。不将供应商预览或静态扫描宣称为本项目原创动画。
- 当前预算约束：用户明确要求只用免费资源；未购买素材，新增人物费用为零。

# v6 人物静帧候选

面部及发型扫描：Renderpeople，Eric rigged 001 免费样本；原始 UV 和 8K diffuse/gloss/normal 贴图保留，切割并适配颈部。身体与鞋型为本项目既有 MakeHuman CC0 资产，服装与额外发丝由脚本调整或生成。扫描人物并非 CC0；使用遵循 https://renderpeople.com/general-terms-and-conditions/ ，只在审阅 HTML 中嵌入渲染图片，不分发原始 3D 数据。下载来源 https://renderpeople.com/free-3d-people/ 。详情见 REALISM-V6.md。

# v5 主动画：本地代码渲染的 3D 动画

人物使用本项目已有 MakeHuman CC0 网格、照片皮肤纹理、权重、眼睛、头发底层与跑鞋。新增服装网格、发丝、跑道、栏架、灯光、骨骼驱动和镜头由代码构建。环境照明与远景：[Stadium 01 / Sergej Majboroda / Poly Haven](https://polyhaven.com/a/stadium_01)，[CC0](https://polyhaven.com/license)。不使用现成动态视频；纹理和环境贴图包含摄影原料。详见 CODE-RENDER.md。下面是旧版历史记录。

# 旧版历史记录：真人训练影像（已停用）

2026-10-21，用户确认真人感优先。主页面使用 Mharee Lynn Eulanda Guillena 的 [Male Athlete Hurdling on Outdoor Track](https://www.pexels.com/video/male-athlete-hurdling-on-outdoor-track-30997018/)，遵循 [Pexels License](https://www.pexels.com/license/)。详情、剪辑范围和素材路径见 [LIVE-ACTION.md](LIVE-ACTION.md)。下文的 MakeHuman 资产继续用于保留的 3D 版本，未混入真人画面。

# 人物美化 v2 / v5 基础素材

当前运行模型为 `public/assets/athlete-v2.glb`。保留 MakeHuman 原生头颈拓扑和骨骼，已完全移除扫描头部投射。下列资产都来自官方系统资产包并共享 CC0：

- 官方说明与逐项许可：https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html
- 下载：https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip
- 下载包位于 `.cache/makehuman-system-assets.zip`；本项目使用的副本位于 `sources/makehuman-system/`。
- 皮肤：`skins/young_caucasian_male2`，原生全身 UV、照片纹理；运行副本转换为高质量 JPEG，原 PNG 保留。
- 头发：`hair/short04`，原生网格和带 alpha 的发丝纹理。
- 眼睛：`eyes/high-poly`、`eyes/materials/brown_eye.png`，保留透明通道，避免外层角膜遮盖虹膜。
- 跑鞋：`clothes/shoes05`，原生网格、鞋带、纹理与权重。
- 人体基础网格、男性形态和权重：同下文 MakeHuman 说明；本版不再对头部顶点进行扫描投射。
- 运动员服装外观、运动轨迹、IK、镜头与景深由本项目实现。
- 完整旧版 HTML、模型、脚本和模型构建器保存在 `outputs/backups/initial/`。

早期 Microsoft Rocketbox Male_Adult_01 候选保存在 `sources/research/rocketbox/`，未被 v5 主模型使用；本轮 v7 另采用 Sports_Male_04，来源与许可见本文顶部。

---

下面保留旧版素材溯源记录，供回溯使用；Lee Perry-Smith 扫描不再出现在当前版本。

# 素材来源与修改记录

## MakeHuman 人体

- 来源：https://github.com/makehumancommunity/makehuman
- 路径：makehuman/data/3dobjs/base.obj、data/rigs/default.mhskel、default_weights.mhw，以及本目录保存的体型形态 target。
- 许可：CC0，详见 MAKEHUMAN-ASSETS-LICENSE.md 与源文件头部。
- 修改：成年男性、精瘦肌肉形态；按 1.88 米规范化；保留连续人体拓扑与 163 个骨骼；平滑细分；田径服装使用局部坐标着色；增加跑鞋。用扫描头部对面部曲面及 UV 做近邻转移，保留连续颈部与身体权重。

## Lee Perry-Smith 面部扫描

- 作者：Lee Perry-Smith / Infinite-Realities，© I-R Entertainment Ltd.
- 下载来源：https://github.com/mrdoob/three.js/tree/r170/examples/models/gltf/LeePerrySmith
- 使用文件：LeePerrySmith.glb、Map-COL.jpg、Infinite-Level_02_Tangent_SmoothUV.jpg。
- 原始档案：https://casual-effects.com/data/ （Morgan McGuire Computer Graphics Archive）。档案的原始署名与许可信息保存在 LEE-PERRY-SMITH-SOURCE.js。
- 许可：CC BY 3.0，https://creativecommons.org/licenses/by/3.0/
- 修改：头部表面形状与 UV 转移至 MakeHuman 连续人体；调整材质肤色、粗糙度及法线强度，颈部颜色渐变。最终 HTML 内置可打开的素材署名窗口。

## 程序与原创部分

- Three.js 0.170.0，MIT，见 THREE-LICENSE.txt。
- 体育场、跑道、栏架、看台、灯柱、旗帜、草地和跑道纹理、号码布、服装着色、动作轨迹、IK 与界面：本项目实现。
- 声音：Web Audio 合成风声、脚步，不含外部录音。
- 字体：系统字体，不需要外部字体服务。

## 尺度参考

World Athletics《Track and Field Facilities Manual 2019》110m Men：10 栏、1.067 m 栏高、13.72 m 首栏距离、9.14 m 栏间距、14.02 m 末栏至终点。
https://worldathletics.org/responsive/download/downloaddirect?filename=7d39b677-8043-45f4-89f4-6c8814023057.pdf&urlslug=Track%2Band%2BField%2BFacilities%2BManual%2B2019%2BEdition%2B-%2BChapters%2B1-3
