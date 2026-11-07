import {Composition,Folder,Series,useVideoConfig} from 'remotion';
import {Intro} from './scenes/Intro';
import {MapScene} from './scenes/Map';
import {Home} from './scenes/Home';
import {Spaces} from './scenes/Spaces';
import {Models} from './scenes/Models';
import {Card} from './scenes/Card';
import {Data} from './scenes/Data';
import {Routes} from './scenes/Routes';
import {Community} from './scenes/Community';
import {Outro} from './scenes/Outro';
import './style.css';

export const HuggingFaceGuide=()=>{
 const {fps}=useVideoConfig();
 return <Series>
 <Series.Sequence name="01 · Hugging Face 是什么" durationInFrames={429} premountFor={fps}><Intro/></Series.Sequence>
 <Series.Sequence name="02 · 三个核心入口" durationInFrames={745} premountFor={fps}><MapScene/></Series.Sequence>
 <Series.Sequence name="03 · 首页导航" durationInFrames={530} premountFor={fps}><Home/></Series.Sequence>
 <Series.Sequence name="04 · Spaces 体验" durationInFrames={836} premountFor={fps}><Spaces/></Series.Sequence>
 <Series.Sequence name="05 · Models 筛选" durationInFrames={719} premountFor={fps}><Models/></Series.Sequence>
 <Series.Sequence name="06 · 模型页怎么看" durationInFrames={813} premountFor={fps}><Card/></Series.Sequence>
 <Series.Sequence name="07 · Datasets 预览" durationInFrames={709} premountFor={fps}><Data/></Series.Sequence>
 <Series.Sequence name="08 · 三条使用路径" durationInFrames={854} premountFor={fps}><Routes/></Series.Sequence>
 <Series.Sequence name="09 · 社区与分享" durationInFrames={531} premountFor={fps}><Community/></Series.Sequence>
 <Series.Sequence name="10 · 第一次体验清单" durationInFrames={639} premountFor={fps}><Outro/></Series.Sequence>
 </Series>;
};
export const RemotionRoot=()=> <>
 <Composition id="HuggingFaceGuide" component={HuggingFaceGuide} width={1920} height={1080} fps={30} durationInFrames={6805}/>
 <Folder name="Chapters">
 <Composition id="Intro" component={Intro} width={1920} height={1080} fps={30} durationInFrames={429}/>
 <Composition id="ThreeDoors" component={MapScene} width={1920} height={1080} fps={30} durationInFrames={745}/>
 <Composition id="Home" component={Home} width={1920} height={1080} fps={30} durationInFrames={530}/>
 <Composition id="Spaces" component={Spaces} width={1920} height={1080} fps={30} durationInFrames={836}/>
 <Composition id="Models" component={Models} width={1920} height={1080} fps={30} durationInFrames={719}/>
 <Composition id="ModelPage" component={Card} width={1920} height={1080} fps={30} durationInFrames={813}/>
 <Composition id="Datasets" component={Data} width={1920} height={1080} fps={30} durationInFrames={709}/>
 <Composition id="Paths" component={Routes} width={1920} height={1080} fps={30} durationInFrames={854}/>
 <Composition id="Community" component={Community} width={1920} height={1080} fps={30} durationInFrames={531}/>
 <Composition id="FirstTry" component={Outro} width={1920} height={1080} fps={30} durationInFrames={639}/>
 </Folder>
 </>;
