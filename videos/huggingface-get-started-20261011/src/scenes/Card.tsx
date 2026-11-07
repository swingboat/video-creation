import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {Frame,Heading,Screen,Spot,Cursor,ListItem,useCue,Fade,Tag} from '../components';
export const Card=()=>{
 const {step}=useCue('card');const {fps}=useVideoConfig();
 const source=step===2?'screens/model-files.png':step===3?'screens/model-use.png':'screens/model-card.png';
 return <Frame id="card" chapter="06"><Heading eyebrow="READ BEFORE YOU USE">模型页，重点看这三处</Heading>
 <div style={{position:'absolute',left:90,top:355,width:525}}><ListItem number="01" icon="book" label="Model card · 说明书" detail="用途 / 语言 / 示例 / 局限" active={step<=1}/><ListItem number="02" icon="file" label="Files · 文件区" detail="权重 / 配置 / 分词器" active={step===2}/><ListItem number="03" icon="code" label="Use this model" detail="按工具查看接入代码" active={step===3}/></div>
 <Screen src={source} url="huggingface.co/openai/whisper-small" top={340} height={480} zoom={.88} x={-55} y={-66}>
 {step<=1?<><Spot x={28} y={133} w={115} h={45}/><Cursor x={91} y={158}/></>:step===2?<><Spot x={146} y={133} w={175} h={45}/><Cursor x={224} y={158}/></>:step===3?<><Spot x={989} y={133} w={154} h={45}/><Cursor x={1084} y={158}/></>:<Spot x={296} y={80} w={150} h={39} label="先检查许可"/>}
 </Screen>
 {step>=4?<Fade style={{position:'absolute',left:705,top:869}}><Tag>许可 + 硬件要求 + 访问权限</Tag></Fade>:null}
 <Audio src={staticFile('voiceover/card.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "打开模型页，重点看三处。",
    "startMs": 600,
    "endMs": 3552,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Model card 是说明书：",
    "startMs": 3902,
    "endMs": 6701,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "看用途、支持语言、示例和局限。",
    "startMs": 6701,
    "endMs": 9326,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Files 是文件区：模型权重、配置和分词器等文件都在这里。",
    "startMs": 9676,
    "endMs": 15268,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Use this model 是接入入口：",
    "startMs": 15618,
    "endMs": 18611,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "查看相应工具的使用代码。",
    "startMs": 18611,
    "endMs": 20322,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "先确认许可和硬件要求；部分模型还需要申请访问权限。",
    "startMs": 20672,
    "endMs": 26072,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
