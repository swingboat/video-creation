import {Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {configSchema, useMerchant, type ClinicProps} from './config';
import {Overlay, PaperCard} from './Overlay';
import {tween} from './motion';

const CityLocationInner = ({configSrc, style}: ClinicProps) => {
  const config = useMerchant(configSrc);
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = frame / fps;
  if (!config) return null;
  return <Overlay config={config} time={time} duration={9} stage="02" heading={<>沿着城市街道<br /><span style={{color: config.theme.brand}}>找到安心</span></>} style={style}>
    <PaperCard style={{top: 1395, padding: '42px 45px', transform: `translateY(${tween(time, 0.3, 1.1, 45, 0)}px)`}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 23}}>
        <span style={{width: 23, height: 23, borderRadius: '50%', background: config.theme.marker}} />
        <div style={{fontSize: 57, fontWeight: 700}}>{config.name}</div>
      </div>
      <div style={{fontSize: 47, color: '#6b837b', marginTop: 23}}>{config.district}{config.address}</div>
    </PaperCard>
  </Overlay>;
};
export const CityLocation = Interactive.withSchema({Component: CityLocationInner, componentName: '<CityLocation>', wrapInSequence: true, schema: configSchema});
