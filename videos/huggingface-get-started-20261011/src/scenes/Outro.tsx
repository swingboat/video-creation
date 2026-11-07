import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Heading,Fade,Icon,Tag,useCue} from '../components';
export const Outro=()=>{
 const {step}=useCue('outro');const {fps}=useVideoConfig();
 return <Frame id="outro" chapter="10"><Heading eyebrow="YOUR FIRST TRY">现在，完成你的第一次体验</Heading>
 <div style={{position:'absolute',left:90,top:365,width:1060}}>{[{title:'Spaces 搜索 whisper',detail:'转录一段不含隐私的短录音'},{title:'打开对应模型页',detail:'找到 Model card / Files / Use this model'}].map((x,i)=><Fade key={x.title} delay={i*12} style={{display:'flex',gap:27,alignItems:'center',padding:'30px 35px',borderRadius:22,border:`2px solid ${step>=i+1?C.yellow:C.line}`,marginBottom:28,background:C.panel}}><div style={{width:64,height:64,borderRadius:'50%',display:'flex',alignItems:'center',justifyContent:'center',background:C.yellow,color:C.bg,fontSize:35,fontWeight:800}}>{i+1}</div><div><div style={{fontSize:45,fontWeight:700}}>{x.title}</div><div style={{fontSize:32,color:C.muted,marginTop:15}}>{x.detail}</div></div></Fade>)}</div>
 <Fade delay={18} style={{position:'absolute',left:1280,top:360,width:500,padding:'38px 32px',borderRadius:24,border:`1px solid ${C.line}`,background:C.panel}}>{[{en:'Spaces',cn:'先体验',kind:'app',color:C.mint},{en:'Models',cn:'找能力',kind:'model',color:C.yellow},{en:'Datasets',cn:'看数据',kind:'data',color:C.blue}].map(x=><div key={x.en} style={{display:'flex',alignItems:'center',gap:22,marginBottom:30}}><Icon kind={x.kind} size={53} color={x.color}/><div style={{fontSize:34}}><span style={{color:x.color,fontWeight:700}}>{x.en}</span><span style={{color:C.muted,marginLeft:20}}>{x.cn}</span></div></div>)}</Fade>
 <Fade style={{position:'absolute',left:90,top:810,display:'flex',gap:25,alignItems:'center'}}><Tag>huggingface.co</Tag><span style={{fontSize:26,color:C.muted}}>内容依据官网 · 2026.10.11 · 非官方介绍</span></Fade>
 <Audio src={staticFile('voiceover/outro.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "现在，试着完成你的第一次体验。",
    "startMs": 600,
    "endMs": 3792,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "打开 Spaces，搜索 whisper，",
    "startMs": 4142,
    "endMs": 7270,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "转录一段不含隐私的短录音。",
    "startMs": 7270,
    "endMs": 9206,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "再打开对应模型页，找到说明书、文件区和使用入口。",
    "startMs": 9556,
    "endMs": 14740,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "记住：Spaces 先体验，Models 找能力，",
    "startMs": 15090,
    "endMs": 18501,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Datasets 看数据。",
    "startMs": 18501,
    "endMs": 20274,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
