import {Composition, Folder} from 'remotion';
import {FutureTitle} from './FutureTitle';
import {ParticleTitle} from './future/ParticleTitle';
import {LogoReveal} from './future/LogoReveal';
import {TechBackground} from './future/TechBackground';

export const RemotionRoot = () => (
  <>
  <Composition
    id="FutureTitle"
    component={FutureTitle}
    durationInFrames={300}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{title: '未来，正在发生', subtitle: '向下一刻，出发', logoText: 'FUTURE', logoSrc: ''}}
  />
  <Folder name="FutureTitle-Layers">
    <Composition id="ParticleTitle" component={ParticleTitle} width={1920} height={1080}
      fps={30} durationInFrames={222} defaultProps={{title: '未来，正在发生', subtitle: '向下一刻，出发'}} />
    <Composition id="LogoReveal" component={LogoReveal} width={1920} height={1080}
      fps={30} durationInFrames={84} defaultProps={{logoText: 'FUTURE', logoSrc: ''}} />
    <Composition id="TechBackground" component={TechBackground} width={1920} height={1080}
      fps={30} durationInFrames={300} />
  </Folder>
  </>
);
