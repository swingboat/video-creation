import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Heading,Fade,Icon,useCue} from '../components';
export const Community=()=>{
 const {step}=useCue('community');const {fps}=useVideoConfig();
 return <Frame id="community" chapter="09"><Heading eyebrow="BUILD & SHARE">不止使用，也能分享</Heading>
 <div style={{position:'absolute',left:90,top:350,width:1010}}>{[{icon:'users',title:'Community',desc:'提问、讨论与协作'},{icon:'folder',title:'Collections',desc:'把模型、数据与应用整理成清单'},{icon:'app',title:'Create a Space',desc:'用 Gradio / Docker 发布自己的应用'}].map((x,i)=><Fade key={x.title} delay={i*12} style={{display:'flex',alignItems:'center',gap:28,padding:'26px 34px',height:158,marginBottom:16,background:C.panel,border:`1px solid ${i===2&&step>=2?C.yellow:C.line}`,borderRadius:22}}><Icon kind={x.icon} size={62} color={i===0?C.blue:i===1?C.mint:C.yellow}/><div><div style={{fontSize:43,fontWeight:700}}>{x.title}</div><div style={{fontSize:30,color:C.muted,marginTop:10}}>{x.desc}</div></div></Fade>)}</div>
 <Fade delay={18} style={{position:'absolute',left:1240,top:410,width:540,height:400,borderRadius:28,padding:45,background:'#FFD24B',color:C.bg}}><Icon kind="model" size={80} color={C.bg}/><div style={{fontSize:59,fontWeight:800,lineHeight:1.3,marginTop:24}}>把你的作品<br/>带给更多人</div><div style={{fontSize:30,marginTop:28}}>模型 · 数据 · 应用</div></Fade>
 <Audio src={staticFile('voiceover/community.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "Hugging Face 也是一个协作社区。",
    "startMs": 600,
    "endMs": 3480,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "你可以在 Community 提问，",
    "startMs": 3830,
    "endMs": 6290,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "用 Collections 整理资源，",
    "startMs": 6290,
    "endMs": 8886,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "或上传自己的模型和数据。",
    "startMs": 8886,
    "endMs": 10526,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "会开发之后，还能用 Gradio 或 Docker，",
    "startMs": 10876,
    "endMs": 14471,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "把应用发布成自己的 Space。",
    "startMs": 14471,
    "endMs": 16684,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
