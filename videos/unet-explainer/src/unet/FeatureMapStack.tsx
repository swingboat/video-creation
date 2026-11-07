import {useId} from 'react';
import {palette} from './settings';

// Fixed analytic seed: abstract responses, never a resized input image.
export const FeatureMapStack = ({x, y, size, color, layers = 4, seed = 11, opacity = 1, split = false}: {
  x: number; y: number; size: number; color: string; layers?: number; seed?: number; opacity?: number; split?: boolean;
}) => {
  const id = useId().replace(/:/g, '');
  return <g opacity={opacity}>
    {Array.from({length: layers}, (_, i) => {
      const fill = split && i >= layers / 2 ? palette.decoder : color;
      const dx = i * 12; const dy = -i * 8;
      const front = i === layers - 1;
      return <g key={i}>
        <rect x={x + dx} y={y + dy} width={size} height={size} rx={7} fill={fill} fillOpacity={front ? 0.13 : 0.09} stroke={fill} strokeWidth={2.5} />
        {front ? <>
          <defs><clipPath id={id}><rect x={x + dx} y={y + dy} width={size} height={size} rx={7} /></clipPath></defs>
          <g clipPath={`url(#${id})`}>
            {Array.from({length: 36}, (_, j) => {
              const gx = j % 6; const gy = Math.floor(j / 6);
              const v = (Math.sin((j + seed) * 17.31) + 1) / 2;
              return <rect key={j} x={x + dx + gx * size / 6 + 2} y={y + dy + gy * size / 6 + 2}
                width={size / 6 - 4} height={size / 6 - 4} rx={3} fill={fill} opacity={0.12 + v * 0.62} />;
            })}
          </g>
        </> : null}
      </g>;
    })}
  </g>;
};
