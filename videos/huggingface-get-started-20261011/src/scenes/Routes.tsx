import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Heading,Fade,Icon,useCue} from '../components';
export const Routes=()=>{
 const {step}=useCue('routes');const {fps}=useVideoConfig();
 return <Frame id="routes" chapter="08"><Heading eyebrow="CHOOSE YOUR PATH">选一条适合你的使用路径</Heading>
 <div style={{position:'absolute',left:90,top:350,display:'flex',gap:30}}>{[{num:'01',title:'网页体验',en:'Spaces',icon:'app',color:C.mint,main:'打开应用，直接操作',detail:'通常不需要写代码',cost:'留意排队与使用额度'},{num:'02',title:'本地运行',en:'Download + Tools',icon:'screen',color:C.yellow,main:'下载模型，安装工具',detail:'按模型说明检查硬件',cost:'需要内存、显存与存储'},{num:'03',title:'接入应用',en:'Inference API',icon:'cloud',color:C.blue,main:'用推理服务调用模型',detail:'选择支持该模型的服务',cost:'查看额度、权限与计费'}].map((x,i)=><Fade key={x.num} delay={i*10} style={{width:560,height:493,padding:'32px 38px',background:step===i+1?`${x.color}13`:C.panel,border:`2px solid ${step===i+1?x.color:C.line}`,borderRadius:24}}><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><Icon kind={x.icon} color={x.color} size={64}/><span style={{fontSize:46,color:'#536075',fontFamily:'monospace'}}>{x.num}</span></div><div style={{fontSize:52,fontWeight:700,marginTop:22}}>{x.title}</div><div style={{fontSize:28,color:x.color,marginTop:8}}>{x.en}</div><div style={{fontSize:33,marginTop:34}}>{x.main}</div><div style={{fontSize:29,color:C.muted,marginTop:14}}>{x.detail}</div><div style={{fontSize:27,color:x.color,marginTop:30,paddingTop:24,borderTop:`1px solid ${C.line}`}}>{x.cost}</div></Fade>)}</div>
 {step>=4?<Fade style={{position:'absolute',left:90,top:877,fontSize:32,color:C.yellow}}>公开可下载 ≠ 运行不消耗算力</Fade>:null}
 <Audio src={staticFile('voiceover/routes.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "接下来，按需求选一条路。",
    "startMs": 600,
    "endMs": 3336,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "只想体验：继续使用 Spaces，通常不需要写代码。",
    "startMs": 3686,
    "endMs": 8462,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "想在自己电脑运行：下载模型，按说明安装工具，",
    "startMs": 8812,
    "endMs": 13598,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "并检查内存或显存。",
    "startMs": 13598,
    "endMs": 15556,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "想接入自己的应用：使用支持该模型的推理服务，调用 API，",
    "startMs": 15906,
    "endMs": 21613,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "并查看计费。",
    "startMs": 21613,
    "endMs": 22794,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "公开可下载，不等于运行模型不花算力成本。",
    "startMs": 23144,
    "endMs": 27440,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
