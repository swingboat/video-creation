import {Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {Frame, type SceneProps} from '../Frame';
import {UNetDiagram} from '../UNetDiagram';
import {FeatureMapStack} from '../FeatureMapStack';
import {SegmentationExample} from '../SegmentationExample';
import {channels, palette, spatialSizes} from '../settings';
import {move} from '../motion';
import {timeline} from '../timeline.generated';
const DecoderSceneInner = ({still, style}: SceneProps) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = still ? 1000 : frame / fps;
  const captions = timeline.scenes[3].captions;
  const step = Math.min(4, Math.floor(move(time, captions[0].startMs / 1000, captions[0].endMs / 1000) * 4.99)); const idx = 4 + step;
  const output = move(time, captions[1].startMs / 1000 - 0.4, captions[1].startMs / 1000 + 0.35); const size = [100, 135, 170, 205, 240][step];
  return <Frame scene={3} style={style}>
    <div style={{position: 'absolute', left: 65, top: 285, width: 945, height: 510}}><UNetDiagram focus="decoder" selected={idx} /></div>
    <div style={{position: 'absolute', left: 1060, top: 278}}>
      <div style={{fontSize: 44, fontWeight: 700, color: palette.decoder}}>上采样 + 卷积</div>
      <svg width="600" height="327" viewBox="0 0 600 327" style={{opacity: 1 - output, marginTop: 12}}><FeatureMapStack x={260 - size / 2} y={170 - size / 2 + 20} size={size} color={palette.decoder} layers={7 - step} seed={108 + step * 13} /></svg>
      <div style={{position: 'absolute', left: 180, top: 80, opacity: output}}><SegmentationExample mode="mask" size={260} /><div style={{fontSize: 24, color: palette.muted, marginTop: 10}}>预测示意 · 两个类别</div></div>
      <div style={{fontSize: 43, fontWeight: 700}}>空间：{spatialSizes[idx]} × {spatialSizes[idx]}</div>
      <div style={{fontSize: 34, marginTop: 16, color: output > 0.5 ? palette.output : palette.decoder}}>{output > 0.5 ? '1×1 卷积 → 前景 / 背景' : `通道：${channels[idx]} · 特征示意`}</div>
    </div>
    <div style={{position: 'absolute', left: 111, top: 818, fontSize: 31, color: palette.muted}}>上采样提高分辨率，准确边界还需要来自编码器的细致信息。</div>
  </Frame>;
};
export const DecoderScene = Interactive.withSchema({Component: DecoderSceneInner, componentName: '<DecoderScene>', wrapInSequence: true, schema: {}});
