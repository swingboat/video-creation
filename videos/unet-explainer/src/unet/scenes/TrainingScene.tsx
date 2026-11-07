import {Interactive} from 'remotion';
import {Frame, type SceneProps} from '../Frame';
import {TrainingDemo} from '../TrainingDemo';
import {useSceneProgress} from '../motion';
const TrainingSceneInner = ({still, sceneFrames, style}: SceneProps) => {
  const progress = useSceneProgress(still, sceneFrames);
  return <Frame scene={5} style={style}><TrainingDemo progress={still ? 0.66 : progress} /></Frame>;
};
export const TrainingScene = Interactive.withSchema({Component: TrainingSceneInner, componentName: '<TrainingScene>', wrapInSequence: true, schema: {}});
