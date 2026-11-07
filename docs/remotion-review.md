## 上游代码审阅

审阅日期：2026-10-10。版本：[v4.0.534](https://github.com/remotion-dev/remotion/tree/v4.0.534)，提交 `4d9ff70e1f489cd671045d8a2e944e4b8853c63d`。

范围覆盖核心注册/Composition、CLI 依赖与命令分发、打包器、浏览器下载与缓存、渲染参数验证及异常清理、相关测试样例和官方空白模板。属于针对本地集成的代码审阅，未进行整个 monorepo 的完整安全审计，也未执行上游全套测试。

### 发现：P2，打包异常可能遗留改变后的进程工作目录

[`packages/bundler/src/bundle.ts:284`](https://github.com/remotion-dev/remotion/blob/4d9ff70e1f489cd671045d8a2e944e4b8853c63d/packages/bundler/src/bundle.ts#L284-L365) 在主线程调用 `process.chdir(resolvedRemotionRoot)` 后，仅在部分成功路径恢复原目录，缺少包围整个流程的 `finally`。如果 `getConfig()` / 用户打包配置覆盖函数抛错，或打包 promise 拒绝，进程可能继续停留在 Remotion 项目目录。对从其他工作目录调用 Node.js `bundle()` 的长期服务，后续相对路径操作可能指向错误位置。

已用本地安装的 `@remotion/bundler@4.0.534` 复现：从 `.cache/remotion-review/repro-start/` 调用 `bundle()`，让 `webpackOverride` 抛出测试异常，捕获后 cwd 遗留为项目根目录。复现结果保存在 `.cache/remotion-review/cwd-repro.json`。

建议上游用 `try/finally` 恢复工作目录。本项目使用独立 CLI 子进程，并在启动时固定 cwd，避免将此状态传播给调用进程。没有修改上游依赖源码。

### 集成结论

核心与渲染器包含 Composition、尺寸、帧率、编码参数校验；浏览器下载有缓存版本检查和下载锁；渲染失败路径包含编码进程取消和资源清理。审阅范围内未发现阻止本地安装和基础渲染的其他问题，具体可用性以本项目实际测试为准。

官方文档要求 Remotion 包保持相同的精确版本：[现有项目安装说明](https://www.remotion.dev/docs/brownfield)。上游仓库是 Bun workspace 开发 monorepo，因此本项目使用发布的 npm 包集成。

### 许可

Remotion 使用[专用许可证](https://github.com/remotion-dev/remotion/blob/4d9ff70e1f489cd671045d8a2e944e4b8853c63d/LICENSE.md)，个人、最多 3 名员工的营利组织、非营利组织，以及非商业评估可适用免费许可；其他组织需要公司许可。不要将其视为 MIT/Apache 许可证项目。

