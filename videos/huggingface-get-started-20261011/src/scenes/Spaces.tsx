import {staticFile,useVideoConfig,interpolate} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {C} from '../theme';
import {Frame,Heading,Screen,Spot,Cursor,ListItem,useCue,Fade,Tag,clamp} from '../components';
export const Spaces=()=>{
 const {step,frame,ms,scene}=useCue('spaces');const {fps}=useVideoConfig();
 const showSettings=step===2 && ms>scene.utterances[2].startMs+2800;
 return <Frame id="spaces" chapter="04"><Heading eyebrow="STEP 01 · SPACES">先体验：录音转文字</Heading>
 <div style={{position:'absolute',left:90,top:345,width:515}}><ListItem number="01" label="Spaces → 搜索 whisper" detail="找到语音转文字应用" active={step<=1}/><ListItem number="02" label={showSettings?'中文录音 → Settings':'打开 App → From file'} detail={showSettings?'Multilingual → Chinese → Transcribe':'选择一段短音频，再转录'} active={step===2}/><ListItem number="03" label="等待 → 核对文字" detail="留意下载、排队或应用状态" active={step>=3}/></div>
 {step<=1?<Screen src="screens/spaces-search.png" url="huggingface.co/spaces?search=whisper" top={340} height={480} zoom={.88} x={-55} y={-65}><Spot x={744} y={217} w={166} h={41} label="搜索关键词"/><Cursor x={837} y={239}/></Screen>:<Screen src={showSettings?'screens/whisper-settings.png':step>=3?'screens/whisper-loaded.png':'screens/whisper-app.png'} url="huggingface.co/spaces/Xenova/whisper-web" top={340} height={480} zoom={showSettings?1.25:.86} x={showSettings?-320:-50} y={showSettings?-415:-168}>
 {showSettings?<Spot x={326} y={171} w={500} h={216} label="多语言 + 中文 + 转录"/>:step===2?<><Spot x={520} y={286} w={122} h={60} label="From file：选择音频"/><Cursor x={592} y={317} click/></>:<><Spot x={495} y={365} w={142} h={45} label="Transcribe Audio：开始转录"/><Cursor x={581} y={390} click/></>}
 </Screen>}
 {step>=4?<Fade style={{position:'absolute',left:702,top:864}}><Tag color={C.mint}>先试短录音 · 避免隐私内容</Tag></Fade>:null}
 <div style={{position:'absolute',right:108,top:280,fontSize:23,color:C.muted}}>官网截图 + 操作标注 · 播放器为公开样例</div>
 <div style={{position:'absolute',left:97,top:855,display:'flex',alignItems:'end',gap:6,height:45}}>{Array.from({length:35},(_,i)=><div key={i} style={{width:6,height:step===0?12+Math.abs(Math.sin(frame/10+i*.6))*32:interpolate(frame,[0,30],[10,10],clamp),borderRadius:4,background:C.yellow}}/>)}<span style={{marginLeft:16,fontSize:24,color:C.muted}}>音频 → 文字</span></div>
 <Audio src={staticFile('voiceover/spaces.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "比如，你想把一段录音转成文字。",
    "startMs": 600,
    "endMs": 3792,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "点击 Spaces，搜索 whisper，",
    "startMs": 4142,
    "endMs": 7231,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "找到语音转文字应用。",
    "startMs": 7231,
    "endMs": 8702,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "在 Whisper Web 选择音频。中文录音打开设置，",
    "startMs": 9052,
    "endMs": 13950,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "启用多语言、选择中文，任务选转录。",
    "startMs": 13950,
    "endMs": 16924,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "等待处理后，查看和核对文字结果。",
    "startMs": 17274,
    "endMs": 20826,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "应用可能需要下载模型，或者排队；不是每个演示都一直可用。",
    "startMs": 21176,
    "endMs": 26840,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
