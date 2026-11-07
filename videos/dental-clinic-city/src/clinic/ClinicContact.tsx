import {Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {configSchema, useMerchant, type ClinicProps} from './config';
import {Overlay, PaperCard} from './Overlay';
import {tween} from './motion';

const ClinicContactInner = ({configSrc, style}: ClinicProps) => {
  const config = useMerchant(configSrc);
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = frame / fps;
  if (!config) return null;
  return <Overlay config={config} time={time} duration={8} holdEnd stage="04" heading={<>{config.name}<br /><span style={{fontSize: 59, color: config.theme.brand, letterSpacing: 2}}>在身边，安心看牙</span></>} style={style}>
    <PaperCard style={{top: 1100, padding: '45px 46px 48px', transform: `translateY(${tween(time, 0.2, 0.95, 45, 0)}px)`}}>
      <div style={{fontSize: 35, color: '#749088', letterSpacing: 5, marginBottom: 20}}>门诊地址</div>
      <div style={{fontSize: 58, fontWeight: 700, lineHeight: 1.45}}>{config.city} · {config.district}<br />{config.address}</div>
      <div style={{height: 2, background: '#e6efea', margin: '32px 0'}} />
      <div style={{fontSize: 43, color: '#577b70', marginBottom: 34}}>{config.services.join('  /  ')}</div>
      <div style={{background: config.theme.brand, color: '#ffffff', borderRadius: 21, padding: '34px 20px', textAlign: 'center',
        fontSize: 53, fontWeight: 700, lineHeight: 1.45}}>{config.cta}</div>
    </PaperCard>
  </Overlay>;
};
export const ClinicContact = Interactive.withSchema({Component: ClinicContactInner, componentName: '<ClinicContact>', wrapInSequence: true, schema: configSchema});
