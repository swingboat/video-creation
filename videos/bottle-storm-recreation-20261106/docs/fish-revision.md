# 鱼群优化记录

参考：<https://x.com/guanmo_ai/status/2118258208045494688>。逐半秒观察原帖画面，重点对照游动距离、双向穿行、纵深遮挡和侧身转向。参考帧在 public/reference/fish-motion/，未导入原帖三维模型或运动数据。

旧版使用刚性椭球鱼身和单片三角尾鳍，身体固定朝向，位置只在各自的窄区域内摆动。新版保留小兔、相机和雷雨时间轴，替换九条鱼的形体和运动。

- 有厚度的鱼身带暗背、亮腹、细鳞片凹凸；补全双侧眼睛、鳃线、嘴、分叉尾鳍、背鳍、胸鳍与鳍条。使用反射和柔和补光塑造体积，鱼身没有自发光。
- 身体按由前向后传播的弯曲波变形，尾部振幅更明显，横截面随曲线转动。20 个循环形态混合为连续动作；胸鳍和背鳍带轻微滞后摆动。
- 两层路线反向穿行。路径采用圆滑回转和长距离游过，按弧长推进；朝向沿速度方向，转弯时带身体弯曲和倾斜。速度平滑变化、摆尾频率随游速调整，九条鱼相位不同。
- 全部保存为 Blender 原生形态关键帧和变换关键帧，打开 .blend 即可播放，不依赖 Python 帧回调。

运动检查覆盖 480 帧的真实求值网格，包含鱼鳍：与玻璃、砂床、水面保持间距；鱼身网格之间没有检测到相交；形态混合权重有效；朝向与运动切线一致。检查报告为 outputs/checks/fish/motion-audit.json。帧间形态权重另见 outputs/checks/fish/subframe-check.json，九条鱼均为线性混合，权重和的最大数值误差小于 9×10⁻⁸。

outputs/checks/fish/before-after-8s.mp4 是同一时刻、同一画面区域的放大对比。正式成片采用 1280×720、24fps、Cycles 32 samples、固定噪声种子、降噪和 0.3 快门运动模糊，与小兔版本保持同一套画面设置。

技术资料：

- Blender relative shape keys: <https://docs.blender.org/manual/en/4.4/animation/shape_keys/shape_keys_panel.html>
- Body-wave kinematic model: <https://pmc.ncbi.nlm.nih.gov/articles/PMC6748450/>
- Tail-beat frequency and speed: <https://pubmed.ncbi.nlm.nih.gov/34847768/>
