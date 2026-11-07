import {type CSSProperties, type ReactNode} from 'react';
import {AbsoluteFill} from 'remotion';
import {useMiSans} from '../fonts';
import {type MerchantConfig} from './config';
import {fade, tween} from './motion';

export const ink = '#223d38';
export const Overlay = ({config, time, duration, stage, heading, children, style, holdEnd = false}: {
  config: MerchantConfig; time: number; duration: number; stage: string; heading: ReactNode; children?: ReactNode; style?: CSSProperties; holdEnd?: boolean;
}) => {
  const ready = useMiSans();
  if (!ready) return null;
  return <AbsoluteFill style={{fontFamily: 'MiSans, sans-serif', color: ink, opacity: holdEnd ? tween(time, 0, 0.55) : fade(time, duration), ...style}}>
    <div style={{position: 'absolute', top: 116, left: 78, right: 78, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 17, fontSize: 39, fontWeight: 700, color: config.theme.brand}}>
        <span style={{display: 'inline-block', width: 13, height: 13, backgroundColor: config.theme.brand, borderRadius: '50%'}} />
        {config.city} · {config.district}
      </div>
      <div style={{fontSize: 29, color: '#79938b', letterSpacing: 4}}>{stage} / 04</div>
    </div>
    <div style={{position: 'absolute', top: 200, left: 78, right: 78, fontWeight: 700, fontSize: 100,
      lineHeight: 1.22, letterSpacing: -3, transform: `translateY(${tween(time, 0, 0.9, 35, 0)}px)`}}>{heading}</div>
    {children}
  </AbsoluteFill>;
};

export const PaperCard = ({children, style}: {children: ReactNode; style?: CSSProperties}) => <div style={{
  position: 'absolute', left: 78, right: 78, borderRadius: 30, background: '#ffffff',
  border: '2px solid #e6eeea', boxShadow: '0 18px 52px rgba(23,65,54,0.055)', ...style,
}}>{children}</div>;
