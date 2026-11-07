import {Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {Frame, type SceneProps} from '../Frame';
import {UNetDiagram} from '../UNetDiagram';
import {FeatureMapStack} from '../FeatureMapStack';
import {channels, palette, spatialSizes} from '../settings';
import {move} from '../motion';
import {timeline} from '../timeline.generated';
const EncoderSceneInner = ({still, style}: SceneProps) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = still ? 1000 : frame / fps;
  const captions = timeline.scenes[2].captions;
  const step = Math.min(4, Math.floor(move(time, captions[1].startMs / 1000 - 0.4, captions[2].endMs / 1000) * 4.99));
  const size = [280, 235, 190, 145, 110][step];
  return <Frame scene={2} style={style}>
    <div style={{position: 'absolute', left: 65, top: 285, width: 945, height: 510}}><UNetDiagram focus="encoder" selected={step} /></div>
    <div style={{position: 'absolute', left: 1045, top: 278, width: 760}}>
      <div style={{fontSize: 44, color: palette.encoder, fontWeight: 700}}>卷积提取特征 → 下采样</div>
      <svg width="700" height="340" viewBox="0 0 700 340" style={{marginTop: 18}}><FeatureMapStack x={280 - size / 2} y={175 - size / 2 + 30} size={size} color={palette.encoder} layers={2 + step * 2} seed={30 + step * 19} /></svg>
      <div style={{fontSize: 48, fontWeight: 700, color: palette.encoder}}>空间：{spatialSizes[step]} × {spatialSizes[step]}</div>
      <div style={{fontSize: 40, marginTop: 17}}>通道：{channels[step]} <span style={{color: palette.muted, fontSize: 28}}>· 特征示意</span></div>
    </div>
    <div style={{position: 'absolute', left: 111, top: 818, fontSize: 31, color: palette.muted}}>空间分辨率降低，通道数增加；较粗尺度可能丢失精细定位信息。</div>
  </Frame>;
};
export const EncoderScene = Interactive.withSchema({Component: EncoderSceneInner, componentName: '<EncoderScene>', wrapInSequence: true, schema: {}});
