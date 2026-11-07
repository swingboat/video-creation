# 真人感优先版本 / 2026-10-21

用户确认：接受将 HTML 主画面改为授权真人跨栏影像，保留播放、慢动作与时间轴，原 3D 为可选模式。

## 素材与来源

- 名称：[Male Athlete Hurdling on Outdoor Track](https://www.pexels.com/video/male-athlete-hurdling-on-outdoor-track-30997018/)
- 作者：Mharee Lynn Eulanda Guillena，Pexels。
- 官方许可：[Pexels License](https://www.pexels.com/license/)，2026-10-21 核对；允许免费下载、使用和修改。不可暗示画面中人物为本项目背书。
- 原片下载地址：`https://videos.pexels.com/video-files/30997018/13249548_1080_1920_28fps.mp4`。
- 原片保存在本视频目录的 `sources/live-action/hurdle-30997018-original.mp4`。
- 源片 1080×1920，约 12.86 秒、27.92 fps；保留原始竖屏比例，无横向拉伸。

## 编辑

选取源片约 6.15–12.35 秒，输出 6.20 秒的 30fps H.264 MP4。帧率整理仅丢弃或重复原帧，不使用生成式补帧、变脸、身体重绘或虚构动作。默认正常速度（1×）播放，观看时长为 6.20 秒；¼× 和 ½× 可手动切换。慢放不会增加源片细节。

这是真实训练素材的局部画面，不能确认画面涵盖完整 110 米、标准成年男子栏高或实测比赛成绩，因此页面不显示模拟距离、速度、过栏数量和虚构成绩。标题保留 110 米栏训练的作品主题。

原片没有使用音轨，页面不合成假现场声音；未用未经授权的赛事转播素材。画面中品牌与人物均不表示背书。

## 文件

- `src/live-action.html`、`src/live-action.css`、`src/live-action.js`：主页面与播放器。
- `scripts/prepare-live-action.py`：可重建剪辑与四张定格图。
- `scripts/build-live-action.mjs`：将视频与定格图作为 data URI 打包。播放器创建本地 Blob URL，支持 file:// 离线 seek。
- `outputs/hurdle-110.html`：新版单文件主交付。
- `outputs/hurdle-110-3d.html`：保留的可环绕实时 3D 版。
- `src/remotion.tsx`：真人版和原 3D 的独立导出入口。

全部运行资源内嵌。主页面中的旧版入口和署名外链属于导航，关闭联网不会影响真人影像播放。
