import {Interactive} from 'remotion';
import {Frame, type SceneProps} from '../Frame';
import {UNetDiagram} from '../UNetDiagram';
import {palette} from '../settings';
import {move, useSceneProgress} from '../motion';
const OverviewSceneInner = ({still, sceneFrames, style}: SceneProps) => {
  const p = useSceneProgress(still, sceneFrames);
  return <Frame scene={1} style={style}>
    <div style={{position: 'absolute', left: 150, top: 235, width: 1620, height: 520}}><UNetDiagram reveal={still ? 1 : move(p, 0, 0.62)} flow={move(p, 0.14, 0.58)} /></div>
    <div style={{position: 'absolute', left: 410, top: 778, padding: '10px 24px', borderRadius: 15, background: '#FFFFFF',
      fontSize: 23, lineHeight: 1.4, color: palette.muted, opacity: move(p, 0.7, 0.8)}}>原始 U-Net 使用不填充卷积，尺寸会变化，跳跃连接前需要裁剪。<br />本片省略这些细节，采用同尺寸填充，重点讲解信息流。</div>
  </Frame>;
};
export const OverviewScene = Interactive.withSchema({Component: OverviewSceneInner, componentName: '<OverviewScene>', wrapInSequence: true, schema: {}});
