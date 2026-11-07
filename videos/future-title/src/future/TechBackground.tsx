import type {CSSProperties} from 'react';
import {AbsoluteFill, Interactive, random, useCurrentFrame, useVideoConfig} from 'remotion';

type BackgroundProps = {readonly style?: CSSProperties};

const stars = Array.from({length: 95}, (_, i) => ({
  x: random(`star-x-${i}`) * 1920,
  y: random(`star-y-${i}`) * 920,
  radius: 0.6 + random(`star-r-${i}`) * 1.4,
  phase: random(`star-phase-${i}`) * Math.PI * 2,
}));

const TechBackgroundInner = ({style}: BackgroundProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;

  return (
    <AbsoluteFill style={{background: '#040713', overflow: 'hidden', ...style}}>
      <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <defs>
          <radialGradient id="future-left-glow">
            <stop stopColor="#1269ff" stopOpacity="0.28" />
            <stop offset="1" stopColor="#1269ff" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="future-right-glow">
            <stop stopColor="#9649ff" stopOpacity="0.31" />
            <stop offset="1" stopColor="#9649ff" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="future-stream" x1="0" x2="1" y1="0" y2="0">
            <stop stopColor="#258aff" stopOpacity="0" />
            <stop offset="0.3" stopColor="#4ac4ff" />
            <stop offset="0.7" stopColor="#ab6aff" />
            <stop offset="1" stopColor="#9c43ff" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="future-floor" x1="0" x2="0" y1="0" y2="1">
            <stop stopColor="#7974ff" stopOpacity="0.03" />
            <stop offset="0.6" stopColor="#636fff" stopOpacity="0.30" />
            <stop offset="1" stopColor="#48a4ff" stopOpacity="0.12" />
          </linearGradient>
          <pattern id="future-grid" width="80" height="80" patternUnits="userSpaceOnUse"
            patternTransform={`translate(${time * 3} ${time * 6})`}>
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="#6374cd" strokeWidth="0.75" strokeOpacity="0.12" />
            <circle cx="0" cy="0" r="1.5" fill="#7999e4" opacity="0.15" />
          </pattern>
          <filter id="future-ribbon-blur" x="-20%" y="-100%" width="140%" height="300%">
            <feGaussianBlur stdDeviation="16" />
          </filter>
          <radialGradient id="future-vignette">
            <stop offset="0.2" stopColor="#000" stopOpacity="0" />
            <stop offset="1" stopColor="#000" stopOpacity="0.6" />
          </radialGradient>
        </defs>
        <ellipse cx={560 + Math.sin(time * 0.5) * 140} cy="485" rx="830" ry="670" fill="url(#future-left-glow)" />
        <ellipse cx={1440 + Math.cos(time * 0.45) * 130} cy="465" rx="750" ry="670" fill="url(#future-right-glow)" />
        <rect width="1920" height="1080" fill="url(#future-grid)" />
        {stars.map((star, i) => (
          <circle key={i} cx={star.x} cy={star.y - time * (i % 3 + 1)} r={star.radius}
            fill={i % 3 ? '#99baff' : '#c2a0ff'} opacity={0.18 + (Math.sin(time * 0.7 + star.phase) + 1) * 0.18} />
        ))}
        <g fill="none" stroke="url(#future-floor)">
          {Array.from({length: 25}, (_, i) => (
            <path key={i} d={`M ${960 + (i - 12) * 30} 635 L ${(i - 12) * 190 + 960} 1180`} strokeWidth="1.2" />
          ))}
          {Array.from({length: 15}, (_, i) => {
            const distance = ((i / 15 + time * 0.035) % 1);
            const y = 638 + distance * distance * 530;
            return <path key={i} d={`M 0 ${y} L 1920 ${y}`} strokeWidth={0.5 + distance} opacity={0.25 + distance * 0.65} />;
          })}
        </g>
        {[0, 1, 2].map((i) => {
          const y = 640 + i * 95 + Math.sin(time * 0.6 + i) * 35;
          const d = `M -180 ${y + 220} C 420 ${y - 380} 760 ${y + 180} 1120 ${y - 70} S 1720 ${y - 210} 2140 ${y - 40}`;
          return (
            <g key={i} fill="none">
              <path d={d} stroke="url(#future-stream)" strokeWidth="17" opacity="0.20" filter="url(#future-ribbon-blur)" />
              <path d={d} stroke="url(#future-stream)" strokeWidth={i === 0 ? 2.2 : 1.1} opacity={0.4 - i * 0.09} />
              <path d={d} stroke="#b8ddff" strokeWidth="2.4" opacity="0.5"
                strokeDasharray="18 1900" strokeDashoffset={-time * 260 - i * 500} />
            </g>
          );
        })}
        <ellipse cx="960" cy="585" rx="805" ry="205" fill="none" stroke="url(#future-stream)"
          strokeWidth="1" opacity="0.15" transform={`rotate(${-12 + Math.sin(time * 0.3) * 2} 960 585)`} />
        <rect width="1920" height="1080" fill="url(#future-vignette)" />
      </svg>
    </AbsoluteFill>
  );
};

export const TechBackground = Interactive.withSchema({
  Component: TechBackgroundInner,
  componentName: '<TechBackground>',
  schema: {},
  wrapInSequence: true,
});
