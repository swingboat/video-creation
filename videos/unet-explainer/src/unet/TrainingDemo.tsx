import {UNetDiagram} from './UNetDiagram';
import {SegmentationExample} from './SegmentationExample';
import {palette} from './settings';
import {move} from './motion';

export const TrainingDemo = ({progress}: {progress: number}) => <div style={{position: 'absolute', left: 100, top: 250, width: 1720, height: 585}}>
  <div style={{position: 'absolute', left: 0, top: 75}}><SegmentationExample size={230} /><div style={{fontSize: 32, marginTop: 17}}>输入图像</div><div style={{fontSize: 23, color: palette.muted}}>分割示意</div></div>
  <svg width="1720" height="585" style={{position: 'absolute', left: 0, top: 0}}>
    <defs><marker id="training-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill={palette.muted} /></marker></defs>
    <path d="M255 190H375 M780 190H895" stroke={palette.muted} strokeWidth="4" markerEnd="url(#training-arrow)" fill="none" />
    <path d="M1155 190H1210V300H1270 M1155 460H1210V330H1270" opacity={move(progress, 0.25, 0.4)} stroke={palette.output} strokeWidth="4" markerEnd="url(#training-arrow)" fill="none" />
    <path d="M1470 398V555H580V355" opacity={move(progress, 0.45, 0.63) * (1 - move(progress, 0.72, 0.78))} stroke={palette.skip} strokeWidth="5" markerEnd="url(#training-arrow)" fill="none" />
    <text x="775" y="590" fontSize="30" fill={palette.skip} opacity={move(progress, 0.45, 0.63) * (1 - move(progress, 0.72, 0.78))}>更新参数 · 让预测更符合标注</text>
  </svg>
  <div style={{position: 'absolute', left: 365, top: 58, width: 430, height: 285, borderRadius: 22, background: '#ffffff', border: '2px solid #E2E8F0', padding: '20px 8px'}}>
    <div style={{fontSize: 32, textAlign: 'center', fontWeight: 700}}>U-Net</div><div style={{height: 207}}><UNetDiagram /></div>
  </div>
  <div style={{position: 'absolute', left: 915, top: 15, opacity: move(progress, 0.08, 0.2)}}><SegmentationExample mode="mask" size={210} error /><div style={{fontSize: 28, marginTop: 6}}>预测掩码</div><div style={{fontSize: 22, color: palette.muted}}>预测示意</div></div>
  <div style={{position: 'absolute', left: 935, top: 302, opacity: move(progress, 0.2, 0.33)}}><SegmentationExample mode="mask" size={170} /><div style={{fontSize: 26, marginTop: 6}}>人工标注掩码</div><div style={{fontSize: 22, color: palette.muted}}>分割示意</div></div>
  <div style={{position: 'absolute', left: 1270, top: 155, width: 420, borderRadius: 26, background: '#F5F3FF', padding: '30px 28px', opacity: move(progress, 0.3, 0.46)}}>
    <div style={{fontSize: 40, fontWeight: 700, color: palette.output}}>计算损失</div>
    <svg width="360" height="130" viewBox="0 0 360 130" style={{marginTop: 16}}>
      <ellipse cx="74" cy="65" rx="43" ry="35" fill="#DDD6FE" />
      <ellipse cx="81" cy="65" rx="34" ry="35" fill="none" stroke="#EF4444" strokeWidth="5" />
      <text x="155" y="61" fill={palette.ink} fontSize="24">比较预测与标注</text><text x="155" y="99" fill="#DC2626" fontSize="24">红线：边界误差</text>
    </svg>
  </div>
  <div style={{position: 'absolute', left: 340, top: 408, background: palette.background, padding: '13px 20px', fontSize: 30,
    opacity: move(progress, 0.78, 0.9), borderLeft: `6px solid ${palette.encoder}`}}>推理：新图像 → 已训练模型 → 预测<br /><span style={{fontSize: 26, color: palette.muted}}>不需要同时提供标注掩码</span></div>
</div>;
