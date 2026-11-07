import type {CSSProperties} from 'react';
import {AbsoluteFill, Easing, Img, Interactive, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import './fonts';

type LogoProps = {readonly logoText: string; readonly logoSrc: string; readonly style?: CSSProperties};

const LogoRevealInner = ({logoText, logoSrc, style}: LogoProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill style={{fontFamily: 'MiSans', alignItems: 'center', justifyContent: 'center', ...style}}>
      <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <defs>
          <linearGradient id="future-logo-gradient" x1="0" x2="1" y1="0" y2="1">
            <stop stopColor="#54c8ff" /><stop offset="1" stopColor="#ab71ff" />
          </linearGradient>
          <radialGradient id="future-logo-halo">
            <stop stopColor="#747aff" stopOpacity="0.22" />
            <stop offset="1" stopColor="#747aff" stopOpacity="0" />
          </radialGradient>
        </defs>
        <ellipse cx="960" cy="475" rx="650" ry="380" fill="url(#future-logo-halo)"
          opacity={interpolate(frame, [0, 0.6 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
        <circle cx="960" cy="450" r={interpolate(frame, [0, 1.6 * fps], [80, 320], {
          easing: Easing.bezier(0.16, 1, 0.3, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        })} fill="none" stroke="url(#future-logo-gradient)" strokeWidth="1.2"
          opacity={interpolate(frame, [0, 0.2 * fps, 1.6 * fps], [0, 0.45, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      </svg>
      <Interactive.Div name="Logo 缩放" premountFor={fps} style={{
        position: 'absolute', top: 316, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center',
        opacity: interpolate(frame, [0, 0.7 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
        scale: interpolate(frame, [0, 1.15 * fps], [0.55, 1], {
          easing: Easing.spring({damping: 22, stiffness: 110}), output: 'perceptual-scale',
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
      }}>
        {logoSrc ? (
          <Img src={/^https?:/.test(logoSrc) ? logoSrc : staticFile(logoSrc)}
            style={{width: 300, height: 190, objectFit: 'contain'}} />
        ) : (
          <svg width="148" height="170" viewBox="0 0 148 170">
            <defs><linearGradient id="future-logo-mark" x1="0" x2="1" y1="0" y2="1">
              <stop stopColor="#63d6ff" /><stop offset="1" stopColor="#9a65ff" />
            </linearGradient></defs>
            <path d="M 74 8 L 132 43 L 132 111 L 74 146 L 16 111 L 16 43 Z"
              fill="#0d1830" stroke="url(#future-logo-mark)" strokeWidth="3" />
            <path d="M 48 108 L 48 46 L 103 46 L 103 59 L 62 59 L 62 72 L 92 72 L 92 85 L 62 85 L 62 108 Z"
              fill="url(#future-logo-mark)" />
            <path d="M 92 93 L 104 93 L 104 108 L 92 108 Z" fill="#c6a9ff" />
          </svg>
        )}
        <div style={{marginTop: 24, color: '#e5e9ff', fontSize: 66, fontWeight: 700, letterSpacing: 18, paddingLeft: 18}}>
          {logoText}
        </div>
      </Interactive.Div>
      <Interactive.Div name="结尾文字" premountFor={fps} style={{
        position: 'absolute', top: 653, width: '100%', textAlign: 'center', fontSize: 34,
        letterSpacing: 10, color: '#95a8d0',
        opacity: interpolate(frame, [0.7 * fps, 1.5 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
      }}>让想象，成为现实</Interactive.Div>
    </AbsoluteFill>
  );
};

export const LogoReveal = Interactive.withSchema({
  Component: LogoRevealInner,
  componentName: '<LogoReveal>',
  schema: {
    logoText: {type: 'text-content', default: 'FUTURE', description: 'Logo 名称'},
    logoSrc: {type: 'asset', default: '', assetType: 'image', description: 'Logo 图片（可选）'},
  },
  wrapInSequence: true,
});
