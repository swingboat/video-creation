import {AbsoluteFill, Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {CityScene} from './clinic/CityScene';
import {CityIntro} from './clinic/CityIntro';
import {CityLocation} from './clinic/CityLocation';
import {ClinicBenefits} from './clinic/ClinicBenefits';
import {ClinicContact} from './clinic/ClinicContact';
import {useMerchant, type ClinicProps} from './clinic/config';
import {useMiSans} from './fonts';

export const DentalClinicCity = ({configSrc, style}: ClinicProps) => {
  const config = useMerchant(configSrc);
  const fonts = useMiSans();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const time = frame / fps;
  if (!config || !fonts) return null;
  const stage = time < 5 ? 0 : time < 14 ? 1 : time < 22 ? 2 : 3;
  return <AbsoluteFill style={{background: config.theme.background, overflow: 'hidden', fontFamily: 'MiSans, sans-serif', ...style}}>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 45% 44%, #ffffff 0%, transparent 67%)'}} />
    <CityScene name="低多边形城市・连续镜头" configSrc={configSrc} durationInFrames={30 * fps} premountFor={fps} />
    <CityIntro name="01・俯视城市进入" configSrc={configSrc} durationInFrames={5 * fps} premountFor={fps} />
    <CityLocation name="02・城市道路与门店定位" configSrc={configSrc} from={5 * fps} durationInFrames={9 * fps} premountFor={fps} />
    <ClinicBenefits name="03・推进门店与卖点卡片" configSrc={configSrc} from={14 * fps} durationInFrames={8 * fps} premountFor={fps} />
    <ClinicContact name="04・地址与预约引导" configSrc={configSrc} from={22 * fps} durationInFrames={8 * fps} premountFor={fps} />
    <Interactive.Div name="四段进度与位置说明" premountFor={fps} style={{position: 'absolute', bottom: 96, left: 78, right: 78}}>
      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 32, fontSize: 29, color: '#7d948b'}}>
        <span>{config.locationNote}</span><span>{config.city} / {config.name}</span>
      </div>
      <div style={{display: 'flex', gap: 14}}>{[0, 1, 2, 3].map((n) => <div key={n} style={{height: 7, flex: 1, borderRadius: 4,
        background: n <= stage ? config.theme.brand : '#d5e3db'}} />)}</div>
    </Interactive.Div>
  </AbsoluteFill>;
};
