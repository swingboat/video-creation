import {Composition} from 'remotion';
import {HelloRemotion} from './HelloRemotion';

export const RemotionRoot = () => (
  <>
  <Composition
    id="HelloRemotion"
    component={HelloRemotion}
    durationInFrames={90}
    fps={30}
    width={1280}
    height={720}
  />
  </>
);
