import {AbsoluteFill, Interactive, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {TechBackground} from './future/TechBackground';
import {ParticleTitle} from './future/ParticleTitle';
import {LogoReveal} from './future/LogoReveal';
import './future/fonts';

export type FutureTitleProps = {
  readonly title: string;
  readonly subtitle: string;
  readonly logoText: string;
  readonly logoSrc: string;
};

export const FutureTitle = ({title, subtitle, logoText, logoSrc}: FutureTitleProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill style={{backgroundColor: '#040713', fontFamily: 'MiSans', overflow: 'hidden'}}>
      <TechBackground name="流动光效与动态网格" durationInFrames={10 * fps} premountFor={fps} />
      <ParticleTitle name="MiSans 粒子标题" from={0} durationInFrames={7.4 * fps} premountFor={fps}
        title={title} subtitle={subtitle} />
      <LogoReveal name="Logo 缩放入场" from={7.2 * fps} durationInFrames={2.8 * fps} premountFor={fps}
        logoText={logoText} logoSrc={logoSrc} />
      <Interactive.Div name="序章标识" premountFor={fps} style={{
        position: 'absolute', top: 134, width: '100%', textAlign: 'center', color: '#889dcc',
        fontSize: 27, fontWeight: 400, letterSpacing: 12,
        opacity: interpolate(frame, [0, 0.8 * fps, 6.2 * fps, 6.7 * fps], [0, 0.8, 0.8, 0], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
      }}>未来序章</Interactive.Div>
      <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', pointerEvents: 'none'}}>
        <g fill="none" stroke="#7d9dda" strokeWidth="1" opacity="0.38">
          <path d="M 138 206 L 138 138 L 206 138 M 1714 138 L 1782 138 L 1782 206" />
          <path d="M 138 874 L 138 942 L 206 942 M 1714 942 L 1782 942 L 1782 874" />
        </g>
        <path d="M 898 938 L 1022 938" stroke="#858aff" strokeWidth="1" opacity="0.45" />
        <circle cx={898 + frame / (10 * fps - 1) * 124} cy="938" r="3" fill="#b1caff" />
      </svg>
      <AbsoluteFill style={{backgroundColor: '#040713', pointerEvents: 'none',
        opacity: interpolate(frame, [0, 0.55 * fps], [1, 0], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
      }} />
    </AbsoluteFill>
  );
};
