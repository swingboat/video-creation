import {Interactive, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Frame, type SceneProps} from '../Frame';
import {UNetDiagram} from '../UNetDiagram';
import {ConcatDemo} from '../ConcatDemo';
import {palette} from '../settings';
import {useSceneProgress} from '../motion';
import {timeline} from '../timeline.generated';
const SkipSceneInner = ({still, sceneFrames, style}: SceneProps) => {
  const p = useSceneProgress(still, sceneFrames);
  const frame = useCurrentFrame(); const {fps, id} = useVideoConfig();
  const captions = timeline.scenes[4].captions;
  const aligned = !still && id !== 'UnetSkipSample' ? interpolate(frame / fps * 1000,
    [0, captions[3].startMs, captions[4].endMs, captions[5].startMs, captions[5].endMs, timeline.scenes[4].durationFrames / timeline.fps * 1000],
    [0, 0.35, 0.62, 0.73, 0.88, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : p;
  return <Frame scene={4} style={style}>
    <div style={{position: 'absolute', left: 42, top: 300, width: 725, height: 418}}><UNetDiagram focus="skip" /></div>
    <div style={{position: 'absolute', left: 105, top: 753, fontSize: 32, color: palette.skip, fontWeight: 700}}>对应层特征 → 解码器</div>
    <div style={{position: 'absolute', left: 792, top: 247, width: 1070, height: 607, borderLeft: '2px solid #E2E8F0'}}><ConcatDemo progress={aligned} /></div>
  </Frame>;
};
export const SkipScene = Interactive.withSchema({Component: SkipSceneInner, componentName: '<SkipScene>', wrapInSequence: true, schema: {}});
