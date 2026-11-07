import {Interactive} from 'remotion';
import {Frame, type SceneProps} from '../Frame';
import {UNetDiagram} from '../UNetDiagram';
import {palette} from '../settings';
import {move, useSceneProgress} from '../motion';
const SummarySceneInner = ({still, sceneFrames, style}: SceneProps) => {
  const p = useSceneProgress(still, sceneFrames);
  return <Frame scene={6} style={style}>
    <div style={{position: 'absolute', left: 170, top: 217, width: 1580, height: 540}}><UNetDiagram focus={p < 0.27 ? 'encoder' : p < 0.53 ? 'decoder' : p < 0.77 ? 'skip' : 'all'} /></div>
    <div style={{position: 'absolute', left: 236, right: 236, top: 776, display: 'flex', justifyContent: 'space-between', fontSize: 43, fontWeight: 700}}>
      <span style={{color: palette.encoder, opacity: move(p, 0, 0.14)}}>提取特征</span>
      <span style={{color: palette.decoder, opacity: move(p, 0.27, 0.41)}}>提高分辨率</span>
      <span style={{color: palette.skip, opacity: move(p, 0.53, 0.67)}}>融合两侧信息</span>
    </div>
  </Frame>;
};
export const SummaryScene = Interactive.withSchema({Component: SummarySceneInner, componentName: '<SummaryScene>', wrapInSequence: true, schema: {}});
