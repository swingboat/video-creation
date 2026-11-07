import {TaskScene} from './scenes/TaskScene';
import {OverviewScene} from './scenes/OverviewScene';
import {EncoderScene} from './scenes/EncoderScene';
import {DecoderScene} from './scenes/DecoderScene';
import {SkipScene} from './scenes/SkipScene';
import {TrainingScene} from './scenes/TrainingScene';
import {SummaryScene} from './scenes/SummaryScene';
export const UnetStoryboard = ({scene}: {scene: number}) => {
  const Scene = [TaskScene, OverviewScene, EncoderScene, DecoderScene, SkipScene, TrainingScene, SummaryScene][scene];
  return <Scene still />;
};
