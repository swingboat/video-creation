import {Composition, Folder, staticFile} from 'remotion';
import {SeasideSkate} from './SeasideSkate';
import {CoastalWorld} from './seaside/CoastalWorld';
import {Skater} from './seaside/Skater';

export const RemotionRoot = () => (
  <>
  <Composition id="SeasideSkate" component={SeasideSkate} durationInFrames={300} fps={30} width={1920} height={1080} />
  <Folder name="SeasideSkate-Layers">
    <Composition id="CoastalWorld" component={CoastalWorld} durationInFrames={300} fps={30} width={1920} height={1080} />
    <Composition id="Skater" component={Skater} durationInFrames={300} fps={30} width={800} height={1000}
      defaultProps={{spriteSrc: staticFile('seaside/girl-poses.png'), motionStrength: 1}} />
  </Folder>
  </>
);
