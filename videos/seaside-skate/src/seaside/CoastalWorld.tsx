import type {CSSProperties} from 'react';
import {AbsoluteFill, CanvasImage, Easing, Interactive, interpolate, random, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type WorldProps = {readonly style?: CSSProperties};
const glints = Array.from({length: 70}, (_, i) => ({
  x: random(`sea-x-${i}`) * 1080 - 100, y: 536 + random(`sea-y-${i}`) * 205,
  size: 5 + random(`sea-size-${i}`) * 28, phase: random(`sea-phase-${i}`) * Math.PI * 2,
}));

const CoastalWorldInner = ({style}: WorldProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;
  return (
    <AbsoluteFill style={{backgroundColor: '#c4e6eb', overflow: 'hidden', ...style}}>
      <Interactive.Div name="海岸跟拍镜头" premountFor={fps} style={{position: 'absolute', inset: 0,
        transformOrigin: '960px 680px',
        scale: interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [1, 1.12, 1.12, 1], {
          easing: Easing.bezier(0.4, 0, 0.3, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp', output: 'perceptual-scale',
        }),
        translate: interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], ['0px 0px', '-15px 0px', '-155px 0px', '0px 0px'], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
      }}>
        <CanvasImage name="水彩海岸与公路" src={staticFile('seaside/coast-watercolor.png')} premountFor={fps}
          style={{position: 'absolute', left: -260, top: 0, width: 2700, height: 1080}} />
        <Interactive.Div name="白云慢移" premountFor={fps} style={{position: 'absolute', left: -100, top: 0, width: 2200, height: 1080,
          maskImage: 'linear-gradient(to bottom, black 0%, black 30%, transparent 44%)',
          opacity: 0.7, translate: interpolate(frame, [0, 10 * fps], ['0px 0px', '-32px 0px'], {
            extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          }),
        }}>
          <CanvasImage name="水彩云层" src={staticFile('seaside/coast-watercolor.png')} premountFor={fps}
            style={{position: 'absolute', left: -160, top: 0, width: 2700, height: 1080}} />
        </Interactive.Div>
        <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
          <defs>
            <clipPath id="coast-water-region"><path d="M 0 520 L 850 520 L 1330 610 L 0 855 Z" /></clipPath>
            <filter id="sea-soft"><feGaussianBlur stdDeviation="0.6" /></filter>
          </defs>
          <g clipPath="url(#coast-water-region)" filter="url(#sea-soft)" stroke="#fff9db" strokeLinecap="round">
            {glints.map((glint, i) => (
              <path key={i} d={`M ${glint.x + Math.sin(time * 0.85 + glint.phase) * 12} ${glint.y + Math.sin(time * 1.2 + glint.phase) * 4} l ${glint.size} -1`}
                strokeWidth={1 + (glint.y - 536) / 205} opacity={(0.18 + 0.13 * Math.sin(time * 1.8 + glint.phase)) * 0.8} />
            ))}
            {[552, 590, 643, 701].map((y, i) => (
              <path key={y} d={`M -80 ${y + Math.sin(time * 0.8 + i) * 4} Q 210 ${y - 10} 480 ${y + 2} T 1030 ${y - 5}`}
                fill="none" strokeWidth="1.7" opacity="0.21" strokeDasharray="85 38 150 67" strokeDashoffset={-time * (8 + i * 3)} />
            ))}
          </g>
        </svg>
      </Interactive.Div>
      <Interactive.Div name="海鸥掠过天空" premountFor={fps} style={{position: 'absolute', inset: 0,
        translate: interpolate(frame, [0, 10 * fps], ['-90px 0px', '250px -30px'], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
      }}>
        <svg width="1920" height="1080" viewBox="0 0 1920 1080">
          {[[510, 220, 1], [650, 176, 0.65], [410, 285, 0.55]].map(([x, y, size], i) => (
            <g key={i} style={{translate: `${x}px ${y + Math.sin(time * 0.8 + i) * 12}px`, scale: size}}>
              <path d={`M -34 ${Math.sin(time * 4.1 + i) * 11 - 8} Q -17 -12 0 2 Q 17 -12 34 ${Math.sin(time * 4.1 + i) * 11 - 8}`}
                fill="none" stroke="#7a9298" strokeWidth="3.5" strokeLinecap="round" opacity="0.65" />
              <path d="M -4 1 Q 0 8 5 1" fill="#f9f7e8" />
            </g>
          ))}
        </svg>
      </Interactive.Div>
    </AbsoluteFill>
  );
};

export const CoastalWorld = Interactive.withSchema({
  Component: CoastalWorldInner, componentName: '<CoastalWorld>', schema: {}, wrapInSequence: true,
});
