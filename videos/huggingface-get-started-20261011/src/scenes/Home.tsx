import {staticFile,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {BasicCaptions} from '../basic-captions';
import {Frame,Heading,Screen,Spot,Cursor,ListItem,useCue,Fade,Tag} from '../components';
export const Home=()=>{
 const {step}=useCue('home');const {fps}=useVideoConfig();
 return <Frame id="home" chapter="03"><Heading eyebrow="GET ORIENTED">从首页开始</Heading>
 <div style={{position:'absolute',left:90,top:355,width:525}}><ListItem number="01" label="找到三个核心入口" detail="Models / Datasets / Spaces" active={step===0}/><ListItem number="02" label="浏览 → 按需注册" detail="收藏、申请访问、发布作品" active={step===1}/><ListItem number="03" label="先明确自己的任务" detail="录音转文字？生成图片？" active={step>=2}/></div>
 <Screen src="screens/home.png" url="huggingface.co" top={340} height={490} zoom={.82} y={0}>
 {step===0?<><Spot x={493} y={8} w={238} h={39}/><Cursor x={700} y={30} click/></>:step===1?<><Spot x={975} y={8} w={133} h={39}/><Cursor x={1065} y={31} click/></>:null}
 </Screen>
 {step>=2?<Fade style={{position:'absolute',left:705,top:870}}><Tag>先问：我想完成什么？</Tag></Fade>:null}
 <Audio src={staticFile('voiceover/home.mp3')} name="中文旁白" premountFor={fps}/><div className="subtitles"><BasicCaptions name="中文字幕" premountFor={fps} width={1540} style={{position:'absolute',left:190,bottom:52}} captions={[
  {
    "text": "打开 huggingface 点 co，顶部就有这三个入口。",
    "startMs": 600,
    "endMs": 4464,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "先浏览公开资源；需要收藏、申请访问或发布作品时，再注册登录。",
    "startMs": 4814,
    "endMs": 11390,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  },
  {
    "text": "不要先追热门。先想清楚：你要让人工智能做什么？",
    "startMs": 11740,
    "endMs": 16636,
    "timestampMs": null,
    "confidence": null,
    "pageBreakAfter": true
  }
]}/></div></Frame>;
};
