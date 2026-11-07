import {FeatureMapStack} from './FeatureMapStack';
import {palette} from './settings';
import {move} from './motion';

export const ConcatDemo = ({progress}: {progress: number}) => {
  const merge = move(progress, 0.35, 0.62); const fuse = move(progress, 0.73, 0.88);
  const xA = 140 + merge * 180; const xB = 760 - merge * 380;
  return <svg width="100%" height="100%" viewBox="0 0 1100 610">
    <text x="550" y="45" textAnchor="middle" fontSize="39" fontWeight="700" fill={palette.ink}>同样的宽和高，沿通道维度连接</text>
    <g opacity={1 - fuse}>
      <FeatureMapStack x={xA} y={165} size={180} color={palette.encoder} layers={4} seed={27} />
      <FeatureMapStack x={xB} y={165 - merge * 40} size={180} color={palette.decoder} layers={4} seed={89} />
      <text x="140" y="415" fontSize="31" fill={palette.encoder} opacity={1 - merge}>编码器：64 通道</text>
      <text x="750" y="415" fontSize="31" fill={palette.decoder} opacity={1 - merge}>解码器：64 通道</text>
      <path d="M470 280L650 175" fill="none" stroke={palette.skip} strokeWidth="3" opacity={merge} />
      <text x="670" y="171" fontSize="28" fill={palette.skip} opacity={merge}>通道轴 C</text>
    </g>
    <g opacity={fuse}>
      <FeatureMapStack x={420} y={160} size={180} color={palette.skip} layers={4} seed={143} />
    </g>
    <text x="550" y="415" textAnchor="middle" fontSize="36" fontWeight="700" fill={palette.skip} opacity={merge}>{fuse > 0.5 ? '卷积融合 → 64 通道' : '拼接后：128 通道'}</text>
    <text x="550" y="480" textAnchor="middle" fontSize="38" fontWeight="700" fill={palette.ink}>64 + 64 → 128 通道</text>
    <text x="550" y="535" textAnchor="middle" fontSize="28" fill={palette.muted}>64×64×64  →  64×64×128  →  64×64×64</text>
    <text x="550" y="585" textAnchor="middle" fontSize="27" fill={palette.ink}>“+”只表示通道数计数；特征值没有逐元素相加</text>
  </svg>;
};
