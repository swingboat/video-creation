import {CanvasImage,interpolate,staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Fade,Tag,Icon,useCue,ease} from '../components';
export const Intro=()=>{
 const {frame,step}=useCue('intro');const {fps}=useVideoConfig();
 return <Frame id="intro" chapter="01">
 <Fade style={{position:'absolute',left:90,top:255}}><div style={{fontSize:30,color:C.yellow,letterSpacing:6,marginBottom:30}}>从看懂，到用起来</div><div style={{fontSize:146,fontWeight:800,letterSpacing:-6,lineHeight:1.1}}>Hugging Face</div><div style={{fontSize:76,fontWeight:650,marginTop:26}}>你的 AI 资源入口</div><div style={{fontSize:38,color:C.muted,marginTop:40,lineHeight:1.6}}>找到模型 · 理解数据 · 直接体验应用</div><div style={{marginTop:42,display:'flex',gap:18}}><Tag>零基础</Tag><Tag color={C.blue}>中文操作指南</Tag><Tag color={C.mint}>3 分钟 +</Tag></div></Fade>
 <div style={{position:'absolute',left:1210,top:230,width:560,height:560,scale:interpolate(frame,[0,35],[.9,1],ease)}}><svg width="560" height="560" viewBox="0 0 560 560"><circle cx="280" cy="280" r="235" stroke={C.line} fill="none"/><circle cx="280" cy="280" r="185" stroke="#FFD24B30" fill="#FFD24B07"/><circle cx="280" cy="280" r="235" stroke={C.yellow} strokeWidth="3" strokeDasharray="150 1330" fill="none" transform={`rotate(${frame*.28} 280 280)`}/></svg><CanvasImage src={staticFile('huggingface.svg')} premountFor={fps} style={{position:'absolute',left:120,top:123,width:320,height:320,translate:`0px ${Math.sin(frame/35)*8}px`}}/>{[['model',70,70],['data',438,125],['app',400,440]].map(([kind,x,y],i)=><div key={kind} style={{position:'absolute',left:Number(x),top:Number(y),background:C.panel,border:`1px solid ${C.line}`,borderRadius:20,padding:17,opacity:interpolate(frame,[20+i*8,40+i*8],[0,1],ease)}}><Icon kind={String(kind)} size={50} color={i===1?C.blue:i===2?C.mint:C.yellow}/></div>)}</div>
 {step>=2?<Fade style={{position:'absolute',left:90,top:815,fontFamily:'monospace',fontSize:36,color:C.yellow}}>huggingface.co</Fade>:null}
 <Audio src={staticFile('voiceover/intro.mp3')} name="中文旁白" premountFor={fps}/>
 <div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "想试试人工智能，却不知道从哪里开始？",
    "startMs": 600,
    "endMs": 4320,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "Hugging Face，把模型、数据和应用汇集在一个网站。",
    "startMs": 4670,
    "endMs": 9350,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "今天，带你从认识它，到真正用起来。",
    "startMs": 9700,
    "endMs": 13300,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div>
 </Frame>;
};
