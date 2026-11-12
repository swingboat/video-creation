"""Summarize actual candidate timing and generation parameters."""
import project_env
from pathlib import Path
import json,re,datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for file in sorted((ROOT/'outputs/checks').glob('generation-*.json')):
 record=json.loads(file.read_text())
 if 'exit_code' not in record:continue
 log=ROOT/'outputs/checks'/(file.stem.replace('generation-','')+'.log')
 text=log.read_text() if log.exists() else ''
 matches=re.findall(r'"mlx_peak_gib":\s*([\d.]+)',text)
 rows.append({'candidate':file.stem.replace('generation-',''),'frames':record['frames'],'width':record['width'],'height':record['height'],'fps':record['fps'],'seed':record['seed'],'seconds':record['wall_seconds'],'exit_code':record['exit_code'],'mlx_peak_gib':float(matches[-1]) if matches else None})
now=datetime.datetime.now(ZoneInfo('Asia/Shanghai'))
summary={'updated_at':now.isoformat(),'candidates':rows,'total_inference_seconds':sum(row['seconds'] for row in rows),'note':'Includes prompt encoding, denoising, decoding and muxing. Excludes image generation, setup, visual QA and editing. MLX peak is not total process or system memory.'}
(ROOT/'outputs/checks/generation-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
lines=['# 本片连续动画实际生成记录','','| 候选 | 帧数 | 尺寸 | 实际分钟 | 结果 |','|---|---:|---|---:|---|']
for r in rows:lines.append(f"| {r['candidate']} | {r['frames']} | {r['width']}×{r['height']} | {r['seconds']/60:.2f} | {'完成生成，是否采用另见选片记录' if r['exit_code']==0 else '失败'} |")
lines.extend(['',f"累计推理时间：{summary['total_inference_seconds']/60:.2f}分钟。",'',summary['note']])
(ROOT/'docs/generation-timings.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
