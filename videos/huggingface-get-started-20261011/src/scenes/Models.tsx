import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Heading,Screen,ListItem,useCue,Tag,Fade} from '../components';
export const Models=()=>{
 const {step}=useCue('models');const {fps}=useVideoConfig();
 return <Frame id="models" chapter="05"><Heading eyebrow="STEP 02 · MODELS">从任务出发，找到模型</Heading>
 <div style={{position:'absolute',left:90,top:350,width:515}}><ListItem number="01" label="任务：语音识别" detail="Automatic Speech Recognition" active={step<=1}/><ListItem number="02" label="语言 + 许可 + 说明" detail="用你的实际需求筛选" active={step===2}/><ListItem number="03" label="阅读示例模型" detail="openai / whisper-small" active={step>=3}/></div>
 <Screen src={step>=3?'screens/model-card.png':'screens/models-asr.png'} url={step>=3?'huggingface.co/openai/whisper-small':'huggingface.co/models'} top={340} height={480} zoom={.88} x={-55} y={-65}/>
 <Fade style={{position:'absolute',left:705,top:869}}><Tag color={step>=3?C.yellow:C.blue}>{step>=3?'下载量是线索，效果要测试':'任务 → 语言 → 许可 → 模型说明'}</Tag></Fade>
 <Audio src={staticFile('voiceover/models.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "想知道背后用的是什么？进入 Models。",
    "startMs": 600,
    "endMs": 4728,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "按任务筛选 Automatic Speech Recognition，",
    "startMs": 5078,
    "endMs": 9185,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "也就是自动语音识别。",
    "startMs": 9185,
    "endMs": 10358,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "再结合语言、使用许可和模型说明，缩小范围。",
    "startMs": 10708,
    "endMs": 15316,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "这里以 openai 的 whisper-small 为例。",
    "startMs": 15666,
    "endMs": 19944,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "下载量能帮你发现模型，但不能代替效果测试。",
    "startMs": 19944,
    "endMs": 22938,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
