import {Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {configSchema, useMerchant, type ClinicProps} from './config';
import {Overlay} from './Overlay';
import {tween} from './motion';

const CityIntroInner = ({configSrc, style}: ClinicProps) => {
  const config = useMerchant(configSrc);
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = frame / fps;
  if (!config) return null;
  return <Overlay config={config} time={time} duration={5} stage="01" heading={<><span style={{fontSize: 58, color: config.theme.brand}}>{config.city} · </span><br />{config.name}</>} style={style}>
    <div style={{position: 'absolute', top: 1432, left: 78, right: 78, opacity: tween(time, 0.8, 1.6)}}>
      <div style={{fontSize: 70, fontWeight: 700, lineHeight: 1.35}}>口腔照护，就在身边</div>
      <div style={{marginTop: 28, fontSize: 43, color: '#6e8880', letterSpacing: 3}}>{config.services.join('  /  ')}</div>
    </div>
  </Overlay>;
};
export const CityIntro = Interactive.withSchema({Component: CityIntroInner, componentName: '<CityIntro>', wrapInSequence: true, schema: configSchema});
