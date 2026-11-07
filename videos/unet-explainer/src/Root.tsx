import {Composition, Folder} from 'remotion';
import {UnetStoryboard} from './unet/UnetStoryboard';
import {SkipScene} from './unet/scenes/SkipScene';
import {UnetExplainer} from './UnetExplainer';
import {timeline as unetTimeline} from './unet/timeline.generated';
import {TaskScene} from './unet/scenes/TaskScene';
import {OverviewScene} from './unet/scenes/OverviewScene';
import {EncoderScene} from './unet/scenes/EncoderScene';
import {DecoderScene} from './unet/scenes/DecoderScene';
import {TrainingScene} from './unet/scenes/TrainingScene';
import {SummaryScene} from './unet/scenes/SummaryScene';

export const RemotionRoot = () => (
  <>
  <Composition id="UnetExplainer" component={UnetExplainer} durationInFrames={4750} fps={30} width={1920} height={1080}
    calculateMetadata={() => ({durationInFrames: unetTimeline.durationFrames})} />
  <Folder name="Unet-Scenes">
    <Composition id="UnetTask" component={TaskScene} durationInFrames={617} fps={30} width={1920} height={1080} calculateMetadata={() => ({durationInFrames: unetTimeline.scenes[0].durationFrames})} />
    <Composition id="UnetOverview" component={OverviewScene} durationInFrames={600} fps={30} width={1920} height={1080} calculateMetadata={() => ({durationInFrames: unetTimeline.scenes[1].durationFrames})} />
    <Composition id="UnetEncoder" component={EncoderScene} durationInFrames={750} fps={30} width={1920} height={1080} calculateMetadata={() => ({durationInFrames: unetTimeline.scenes[2].durationFrames})} />
    <Composition id="UnetDecoder" component={DecoderScene} durationInFrames={750} fps={30} width={1920} height={1080} calculateMetadata={() => ({durationInFrames: unetTimeline.scenes[3].durationFrames})} />
    <Composition id="UnetSkip" component={SkipScene} durationInFrames={900} fps={30} width={1920} height={1080} calculateMetadata={() => ({durationInFrames: unetTimeline.scenes[4].durationFrames})} />
    <Composition id="UnetTraining" component={TrainingScene} durationInFrames={750} fps={30} width={1920} height={1080} calculateMetadata={() => ({durationInFrames: unetTimeline.scenes[5].durationFrames})} />
    <Composition id="UnetSummary" component={SummaryScene} durationInFrames={383} fps={30} width={1920} height={1080} calculateMetadata={() => ({durationInFrames: unetTimeline.scenes[6].durationFrames})} />
  </Folder>
  <Composition id="UnetStoryboard" component={UnetStoryboard} durationInFrames={1} fps={30} width={1920} height={1080} defaultProps={{scene: 0}} />
  <Composition id="UnetSkipSample" component={SkipScene} durationInFrames={360} fps={30} width={1920} height={1080} />
  </>
);
