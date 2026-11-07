import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Heading,Fade,Icon,useCue} from '../components';
export const MapScene=()=>{
 const {step}=useCue('map');const {fps}=useVideoConfig();
 return <Frame id="map" chapter="02"><Heading eyebrow="THE THREE DOORS">记住三个入口</Heading>
 <div style={{position:'absolute',top:335,left:90,display:'flex',gap:30}}>{[{en:'Models',cn:'模型库',desc:'找到能完成任务的模型',analogy:'引擎',kind:'model',color:C.yellow},{en:'Datasets',cn:'数据集',desc:'获取训练与评测的材料',analogy:'教材',kind:'data',color:C.blue},{en:'Spaces',cn:'应用体验区',desc:'在浏览器里直接试用',analogy:'可以直接开的车',kind:'app',color:C.mint}].map((x,i)=><Fade key={x.en} delay={i*10} style={{width:560,height:510,padding:'38px 40px',borderRadius:24,border:`2px solid ${step===i+1||step>=4?x.color:C.line}`,background:step===i+1?`${x.color}0D`:C.panel}}><Icon kind={x.kind} color={x.color} size={75}/><div style={{fontSize:68,fontWeight:750,marginTop:30,color:x.color}}>{x.en}</div><div style={{fontSize:44,fontWeight:600,marginTop:5}}>{x.cn}</div><div style={{fontSize:31,color:C.muted,marginTop:28,lineHeight:1.5}}>{x.desc}</div>{step>=4?<div style={{marginTop:32,fontSize:34,borderTop:`1px solid ${C.line}`,paddingTop:26,color:x.color}}>就像：{x.analogy}</div>:null}</Fade>)}</div>
 <Audio src={staticFile('voiceover/map.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "先记住三个入口。",
    "startMs": 600,
    "endMs": 2616,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Models，是模型库：找能完成任务的人工智能模型。",
    "startMs": 2966,
    "endMs": 7478,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Datasets，是数据集：找训练和评测用的材料。",
    "startMs": 7828,
    "endMs": 12364,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Spaces，是应用体验区：打开网页，",
    "startMs": 12714,
    "endMs": 16112,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "就能试用别人做好的应用。",
    "startMs": 16112,
    "endMs": 18258,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "模型像引擎，数据像教材，应用像一辆可以直接开的车。",
    "startMs": 18608,
    "endMs": 23816,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
