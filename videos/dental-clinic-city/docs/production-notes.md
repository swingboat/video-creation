## 30 秒竖屏 3D 门诊宣传

新增 `DentalClinicCity`：1080×1920、9:16、30 fps、900 帧。打开 [安心口腔门诊预览](http://localhost:3215/DentalClinicCity)，点击播放即可观看。若服务停止，运行 `npm run dev`。

0–5 秒从城市上空进入并展示名称；5–14 秒展示网格、道路、建筑和红色定位标记；14–22 秒镜头推进，门店材质发光，三个卖点依次出现；22–30 秒展示名称、地址和“私信预约，到店先检查”。当前地址是用户给出的占位地址，城市模型是位置示意，不对应真实杭州地图。输入中的 `svg` 已按笔误移除。

商家数据在 `public/business/clinic.json`：修改 `name`、`city`、`district`、`address`、`services`、三个 `highlights`、`cta` 和 `theme` 后刷新预览，即可更新文案与配色。`store.position`、建筑的 `position` 使用 `[x, z]` 地面坐标；尺寸和高度使用统一场景单位。`buildings` 数组控制楼房位置、尺寸和颜色。换门店时请同时避开其他建筑的位置。

也可以复制 JSON 到 `public/business/other.json`，在 `src/Root.tsx` 中将 `DentalClinicCity` 的 `defaultProps.configSrc` 改为 `business/other.json`，或通过导出参数选择数据文件：

```sh
npm run render -- --props='{"configSrc":"business/other.json"}'
```

代码入口是 `src/DentalClinicCity.tsx`。`src/clinic/CityScene.tsx` 使用 `ThreeCanvas`、React Three Fiber 和 Three.js；城市、树木、门店、定位点均由 box、plane、sphere 构成，招牌文字是本地 MiSans 生成的 canvas 纹理，没有下载 3D 模型。相机位置、标记、建筑进入、发光和卡片动画均由 `useCurrentFrame()` 驱动，没有使用 `useFrame()`。四个文案阶段和连续 3D 镜头分别注册在 `DentalClinic-Layers` 中，可单独查看时间线。

`@remotion/three@4.0.534`、`@react-three/fiber@9.8.1`、`three@0.186.1` 和 `@types/three@0.186.0` 均安装在当前项目。当前版本的 Fiber 使用 Three.js 内部 Clock 会输出弃用提示；它不参与本项目的动画计算，重复帧渲染已经验证一致。

`npm run check:clinic` 执行类型检查、Composition 参数检查、四段关键帧渲染、重复帧一致性与另一个 JSON 的替换验证。报告为 `outputs/clinic-check-report.json`。关键帧为 `outputs/clinic-intro.png`、`outputs/clinic-location.png`、`outputs/clinic-benefits.png` 和 `outputs/clinic-contact.png`。当前交付是可播放的 Studio 预览；需要 MP4 时运行 `npm run render`，输出 `outputs/dental-clinic-city.mp4`。`npm run still` 可以单独重新生成卖点镜头截图。

