import {Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {configSchema, useMerchant, type ClinicProps} from './config';
import {Overlay, PaperCard} from './Overlay';
import {tween} from './motion';

const ClinicBenefitsInner = ({configSrc, style}: ClinicProps) => {
  const config = useMerchant(configSrc);
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = frame / fps;
  if (!config) return null;
  return <Overlay config={config} time={time} duration={8} stage="03" heading={<>让每次就诊<br /><span style={{color: config.theme.brand}}>更从容</span></>} style={style}>
    {config.highlights.map((item, i) => {
      const enter = tween(time, 0.6 + i * 0.95, 1.3 + i * 0.95);
      return <PaperCard key={i} style={{top: 1105 + i * 190, height: 164, padding: '30px 36px', display: 'flex', gap: 28,
        alignItems: 'center', opacity: enter, transform: `translateY(${(1 - enter) * 48}px)`}}>
        <div style={{flexShrink: 0, width: 75, height: 75, borderRadius: 22, background: '#e9f4ef', color: config.theme.brand,
          fontSize: 39, fontWeight: 700, display: 'grid', placeItems: 'center'}}>0{i + 1}</div>
        <div>
          <div style={{fontSize: i === 0 ? 48 : 55, fontWeight: 700, whiteSpace: 'nowrap'}}>{item.title}</div>
          <div style={{fontSize: 38, marginTop: 8, color: '#6e847c'}}>{item.detail}</div>
        </div>
      </PaperCard>;
    })}
  </Overlay>;
};
export const ClinicBenefits = Interactive.withSchema({Component: ClinicBenefitsInner, componentName: '<ClinicBenefits>', wrapInSequence: true, schema: configSchema});
