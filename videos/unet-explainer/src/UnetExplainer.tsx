import {Series, useVideoConfig} from 'remotion';
import {timeline} from './unet/timeline.generated';
import {TaskScene} from './unet/scenes/TaskScene';
import {OverviewScene} from './unet/scenes/OverviewScene';
import {EncoderScene} from './unet/scenes/EncoderScene';
import {DecoderScene} from './unet/scenes/DecoderScene';
import {SkipScene} from './unet/scenes/SkipScene';
import {TrainingScene} from './unet/scenes/TrainingScene';
import {SummaryScene} from './unet/scenes/SummaryScene';

export const UnetExplainer = () => {
  const {fps} = useVideoConfig();
  const duration = (scene: number) => Math.round(timeline.scenes[scene].durationFrames / timeline.fps * fps);
  return <Series>
    <Series.Sequence name="01・图像分类与分割" durationInFrames={duration(0)} premountFor={fps}>
      <TaskScene sceneFrames={duration(0)} premountFor={fps} />
    </Series.Sequence>
    <Series.Sequence name="02・完整 U 形信息流" durationInFrames={duration(1)} premountFor={fps}>
      <OverviewScene sceneFrames={duration(1)} premountFor={fps} />
    </Series.Sequence>
    <Series.Sequence name="03・编码器与特征尺度" durationInFrames={duration(2)} premountFor={fps}>
      <EncoderScene sceneFrames={duration(2)} premountFor={fps} />
    </Series.Sequence>
    <Series.Sequence name="04・解码器与像素预测" durationInFrames={duration(3)} premountFor={fps}>
      <DecoderScene sceneFrames={duration(3)} premountFor={fps} />
    </Series.Sequence>
    <Series.Sequence name="05・跳跃连接与通道拼接" durationInFrames={duration(4)} premountFor={fps}>
      <SkipScene sceneFrames={duration(4)} premountFor={fps} />
    </Series.Sequence>
    <Series.Sequence name="06・训练与推理" durationInFrames={duration(5)} premountFor={fps}>
      <TrainingScene sceneFrames={duration(5)} premountFor={fps} />
    </Series.Sequence>
    <Series.Sequence name="07・三个动作总结" durationInFrames={duration(6)} premountFor={fps}>
      <SummaryScene sceneFrames={duration(6)} premountFor={fps} />
    </Series.Sequence>
  </Series>;
};
