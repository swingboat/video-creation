import {useId} from 'react';
import {palette} from './settings';

export const cells = [{x: 73, y: 72, rx: 35, ry: 28, angle: -20}, {x: 183, y: 80, rx: 31, ry: 41, angle: 30},
  {x: 100, y: 174, rx: 43, ry: 31, angle: 18}, {x: 202, y: 188, rx: 28, ry: 33, angle: -15}];
export const SegmentationExample = ({mode = 'image', size = 350, error = false}: {mode?: 'image' | 'mask'; size?: number; error?: boolean}) => {
  const id = useId().replace(/:/g, '');
  return <svg width={size} height={size} viewBox="0 0 256 256" style={{borderRadius: 22, overflow: 'hidden', border: '2px solid #E2E8F0'}}>
    <defs><radialGradient id={id}><stop stopColor="#E4BBFA" /><stop offset="0.72" stopColor="#CDA6E8" /><stop offset="1" stopColor="#AF87CB" /></radialGradient></defs>
    <rect width="256" height="256" fill={mode === 'image' ? '#EEE5F6' : '#1E1639'} />
    {mode === 'image' ? Array.from({length: 90}, (_, j) => <circle key={j} cx={(j * 71 + 23) % 256} cy={(j * 43 + 37) % 256} r={1 + j % 3} fill="#AD86C5" opacity="0.13" />) : null}
    {cells.map((c, i) => <g key={i} transform={`translate(${c.x + (error && i === 1 ? 8 : 0)}, ${c.y}) rotate(${c.angle})`}>
      <ellipse rx={c.rx * (error && i === 2 ? 0.75 : 1)} ry={c.ry} fill={mode === 'image' ? `url(#${id})` : '#C4B5FD'} stroke={mode === 'image' ? '#AB80C3' : 'none'} strokeWidth="2" />
      {mode === 'image' ? <><ellipse rx={c.rx * 0.33} ry={c.ry * 0.38} cx="-5" cy="2" fill="#805AA5" opacity="0.85" />
        <path d="M-16 -16 Q-4 -23 11 -19" fill="none" stroke="#F9ECFF" strokeWidth="3" opacity="0.7" /></> : null}
    </g>)}
    {error && mode === 'mask' ? cells.filter((_, i) => i === 1 || i === 2).map((c, i) => <ellipse key={`error-${i}`}
      cx={c.x} cy={c.y} rx={c.rx} ry={c.ry} transform={`rotate(${c.angle} ${c.x} ${c.y})`} fill="none" stroke="#EF4444" strokeWidth="2.5" />) : null}
  </svg>;
};

export const PixelZoom = () => <svg width="300" height="260" viewBox="0 0 300 260">
  {Array.from({length: 64}, (_, i) => {const x = i % 8; const y = Math.floor(i / 8); const inside = (x - 2) ** 2 + (y - 3) ** 2 < 11;
    return <rect key={i} x={x * 28 + 25} y={y * 28 + 12} width="25" height="25" rx="3" fill={inside ? '#A78BFA' : '#DDD6FE'} stroke="#ffffff" />;})}
  <rect x="81" y="96" width="25" height="25" fill="none" stroke={palette.output} strokeWidth="4" />
  <rect x="221" y="180" width="25" height="25" fill="none" stroke={palette.ink} strokeWidth="4" />
</svg>;
