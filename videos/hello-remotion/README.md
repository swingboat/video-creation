# HelloRemotion

独立 Remotion 视频项目：1280×720，30 fps，3 秒。仅包含本视频的组件、素材与脚本。

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

预览地址：http://localhost:3212/HelloRemotion。最终视频输出至 `outputs/hello-remotion.mp4`；缓存和临时文件位于 `.cache/`。本目录的 `package-lock.json` 锁定依赖，npm 缓存和浏览器均在本目录内。项目不能依赖其他视频或上层工作区文件。

修改 `src/HelloRemotion.tsx` 及本视频的子组件、`public/` 素材；Composition 注册与时长在 `src/Root.tsx`。

已保留原有 MP4。
