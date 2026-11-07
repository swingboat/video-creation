import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Heading,Screen,ListItem,useCue,Fade,Tag} from '../components';
export const Data=()=>{
 const {step}=useCue('data');const {fps}=useVideoConfig();
 return <Frame id="data" chapter="07" accent={C.blue}><Heading eyebrow="DATASETS">数据集：先看说明，再看样本</Heading>
 <div style={{position:'absolute',left:90,top:355,width:525}}><ListItem number="01" label="数据卡 · Dataset card" detail="来源 / 字段 / 使用许可" active={step<=1}/><ListItem number="02" label="Data Studio · 数据预览" detail="查看具体样本和数据划分" active={step===2}/><ListItem number="03" label="访问是否受限？" detail="部分数据集需要申请权限" active={step>=3}/></div>
 <Screen src="screens/dataset.png" url="huggingface.co/datasets/stanfordnlp/imdb" top={340} height={480} zoom={.9} x={-60} y={-65}/>
 <Fade style={{position:'absolute',left:705,top:869}}><Tag color={C.blue}>示例：IMDB 影评与情感标签</Tag></Fade>
 <Audio src={staticFile('voiceover/data.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "Datasets 用来找数据，",
    "startMs": 600,
    "endMs": 3143,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "不是直接使用人工智能的聊天窗口。",
    "startMs": 3143,
    "endMs": 5856,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "打开一个数据集，先看数据卡，了解来源、字段和使用许可。",
    "startMs": 6206,
    "endMs": 11990,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "再用 Data Studio 预览样本和训练、测试等划分。",
    "startMs": 12340,
    "endMs": 16972,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "有些数据集支持直接预览；受限数据需要申请权限。",
    "startMs": 17322,
    "endMs": 22602,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
