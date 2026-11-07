import {useId} from 'react';
import {FeatureMapStack} from './FeatureMapStack';
import {channels, palette, spatialSizes} from './settings';
import {move} from './motion';

const nodes = [[190, 130], [330, 250], [470, 370], [610, 490], [780, 585], [950, 490], [1090, 370], [1230, 250], [1370, 130]];
const sizes = [130, 106, 84, 64, 48, 64, 84, 106, 130];
export const UNetDiagram = ({focus = 'all', reveal = 1, flow = 0, selected = -1, style}: {
  focus?: 'all' | 'encoder' | 'decoder' | 'skip'; reveal?: number; flow?: number; selected?: number; style?: React.CSSProperties;
}) => {
  const id = useId().replace(/:/g, '');
  const opacity = (i: number) => focus === 'all' || (focus === 'encoder' && i <= 4) || (focus === 'decoder' && i >= 4) ||
    (focus === 'skip' && (i === 2 || i === 6)) ? 1 : 0.16;
  return <svg width="100%" height="100%" viewBox="0 0 1580 715" style={{overflow: 'visible', ...style}}>
    <defs>{[palette.encoder, palette.decoder, palette.skip].map((color, i) => <marker key={color} id={`${id}-a${i}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill={color} /></marker>)}</defs>
    <text x="120" y="36" fontSize="37" fontWeight="700" fill={palette.encoder} opacity={focus === 'decoder' ? 0.3 : 1}>编码器</text>
    <text x="1300" y="36" fontSize="37" fontWeight="700" fill={palette.decoder} opacity={focus === 'encoder' ? 0.3 : 1}>解码器</text>
    {[0, 1, 2, 3].map((i) => {
      const left = nodes[i]; const right = nodes[8 - i]; const half = sizes[i] / 2;
      const y = left[1] - 28;
      const d = `M ${left[0] + half + 30} ${y} L ${right[0] - half - 25} ${y}`;
      const alpha = move(reveal, 0.78, 1) * (focus === 'skip' ? i === 2 ? 1 : 0.13 : focus === 'all' ? 0.65 : 0.13);
      return <g key={i} opacity={alpha}>
        <path d={d} stroke={palette.skip} strokeWidth={i === 2 && focus === 'skip' ? 7 : 4} fill="none" markerEnd={`url(#${id}-a2)`} />
        {i === 0 ? <g><rect x="610" y="72" width="338" height="46" rx="16" fill={palette.background} /><text x="779" y="104" textAnchor="middle" fontSize="31" fontWeight="700" fill={palette.skip}>跳跃连接 · 拼接</text></g> : null}
      </g>;
    })}
    {nodes.slice(0, 8).map((p, i) => {
      const q = nodes[i + 1]; const dx = q[0] - p[0]; const dy = q[1] - p[1]; const norm = Math.hypot(dx, dy);
      const sx = p[0] + dx / norm * (sizes[i] * 0.62 + 18); const sy = p[1] + dy / norm * (sizes[i] * 0.62 + 18);
      const ex = q[0] - dx / norm * (sizes[i + 1] * 0.6 + 9); const ey = q[1] - dy / norm * (sizes[i + 1] * 0.6 + 9);
      const color = i < 4 ? palette.encoder : palette.decoder;
      const t = Math.max(0, Math.min(1, flow * 8 - i));
      return <g key={i} opacity={move(reveal, i * 0.075, i * 0.075 + 0.16) * Math.min(opacity(i), opacity(i + 1))}>
        <path d={`M${sx} ${sy}L${ex} ${ey}`} stroke={color} strokeWidth="4" markerEnd={`url(#${id}-a${i < 4 ? 0 : 1})`} />
        {t > 0 && t < 1 ? <circle cx={sx + (ex - sx) * t} cy={sy + (ey - sy) * t} r="9" fill={color} /> : null}
      </g>;
    })}
    {nodes.map(([x, y], i) => {
      const s = sizes[i]; const color = i <= 4 ? palette.encoder : palette.decoder;
      const active = selected === i;
      return <g key={i} opacity={opacity(i) * move(reveal, i * 0.073, i * 0.073 + 0.14)}>
        {active ? <rect x={x - s / 2 - 18} y={y - s / 2 - 45} width={s + 72} height={s + 115} rx="20" fill={color} fillOpacity="0.07" stroke={color} strokeWidth="3" /> : null}
        <FeatureMapStack x={x - s / 2} y={y - s / 2} size={s} color={color} layers={i <= 4 ? i + 2 : 10 - i} seed={i * 13 + 11} />
        <text x={x + 9} y={y + s / 2 + 42} fontSize="30" textAnchor="middle" fontWeight="700" fill={palette.ink}>{spatialSizes[i]}²</text>
        <text x={x + 9} y={y + s / 2 + 76} fontSize="25" textAnchor="middle" fill={color}>{channels[i]} 通道</text>
      </g>;
    })}
    <text x="780" y="60" textAnchor="middle" fontSize="24" fill={palette.muted}>特征示意 · 空间尺度 / 通道数</text>
  </svg>;
};
