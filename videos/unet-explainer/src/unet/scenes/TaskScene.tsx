import {Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {Frame, type SceneProps} from '../Frame';
import {PixelZoom, SegmentationExample} from '../SegmentationExample';
import {palette} from '../settings';
import {move} from '../motion';
import {timeline} from '../timeline.generated';
const TaskSceneInner = ({still, style}: SceneProps) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = still ? 1000 : frame / fps;
  const captions = timeline.scenes[0].captions;
  const mask = move(time, captions[2].startMs / 1000 - 0.35, captions[2].startMs / 1000 + 0.5);
  const zoom = move(time, captions[3].startMs / 1000 - 0.35, captions[3].startMs / 1000 + 0.5);
  return <Frame scene={0} style={style}>
    <div style={{position: 'absolute', left: 160, top: 285}}><SegmentationExample size={420} />
      <div style={{fontSize: 35, fontWeight: 700, marginTop: 21}}>细胞图像</div><div style={{fontSize: 25, color: palette.muted}}>分割示意 · 合成素材</div></div>
    <div style={{position: 'absolute', left: 770, top: 285, opacity: mask}}><SegmentationExample mode="mask" size={420} />
      <div style={{fontSize: 35, fontWeight: 700, marginTop: 21}}>前景 / 背景掩码</div><div style={{fontSize: 25, color: palette.muted}}>分割示意</div></div>
    <div style={{position: 'absolute', left: 620, top: 475, fontSize: 64, color: palette.output, opacity: mask}}>→</div>
    <div style={{position: 'absolute', left: 1395, top: 308, opacity: zoom}}>
      <div style={{fontSize: 34, fontWeight: 700, marginBottom: 12}}>放大：像素标签</div><PixelZoom />
      <div style={{fontSize: 32, color: palette.output, marginTop: 9}}>● 前景：细胞</div><div style={{fontSize: 32, color: palette.ink, marginTop: 12}}>● 背景：其他区域</div>
    </div>
    <div style={{position: 'absolute', left: 160, top: 808, fontSize: 33, color: palette.muted}}>分类：整张图是什么？<span style={{marginLeft: 70, color: palette.output, fontWeight: 700}}>分割：每个像素属于哪一类？</span></div>
  </Frame>;
};
export const TaskScene = Interactive.withSchema({Component: TaskSceneInner, componentName: '<TaskScene>', wrapInSequence: true, schema: {}});
