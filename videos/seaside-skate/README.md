# SeasideSkate

独立 Remotion 视频项目：1920×1080，30 fps，10 秒。仅包含本视频的组件、素材与脚本。

```bash
npm ci
npm run dev
npm run typecheck
npm run check
npm run still
npm run render
npm run verify
npm run pack
```

预览地址：http://localhost:3214/SeasideSkate。最终视频输出至 `outputs/seaside-skate.mp4`；缓存和临时文件位于 `.cache/`。本目录的 `package-lock.json` 锁定依赖，npm 缓存和浏览器均在本目录内。项目不能依赖其他视频或上层工作区文件。

修改 `src/SeasideSkate.tsx` 及本视频的子组件、`public/` 素材；Composition 注册与时长在 `src/Root.tsx`。
音效在 `public/seaside/`；`npm run prepare:audio` 使用固定种子重新生成海浪、海风、滑板滚动声。

迁移后已从独立项目导出完整 MP4，保存在 `outputs/`。需要重新导出时执行 `npm run render`。

原始制作说明及可编辑参数见 [docs/production-notes.md](docs/production-notes.md)。
