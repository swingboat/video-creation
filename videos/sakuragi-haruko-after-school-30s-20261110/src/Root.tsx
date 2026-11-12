import {Audio} from '@remotion/media';
import {AbsoluteFill,Composition,Folder,Series,interpolate,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Opening} from './Opening';import {Haruko} from './Haruko';import {Shy} from './Shy';import {Practice} from './Practice';import {Gather} from './Gather';import {Cheer} from './Cheer';import {Resolve} from './Resolve';import {Ending} from './Ending';
import {Smile} from './Smile';
import {Epilogue} from './Epilogue';
export const SakuragiHaruko=()=>{
 const {fps,durationInFrames}=useVideoConfig();const frame=useCurrentFrame();
 return <AbsoluteFill style={{background:'#171916'}}>
  <Series>
   <Series.Sequence name="同框鼓励" durationInFrames={4*fps} premountFor={fps}><Opening/></Series.Sequence>
   <Series.Sequence name="晴子的建议" durationInFrames={4*fps} premountFor={fps}><Haruko/></Series.Sequence>
   <Series.Sequence name="樱木害羞" durationInFrames={86} premountFor={fps}><Shy/></Series.Sequence>
   <Series.Sequence name="认真练习" durationInFrames={4*fps} premountFor={fps}><Practice/></Series.Sequence>
   <Series.Sequence name="收球准备" durationInFrames={2.5*fps} premountFor={fps}><Gather/></Series.Sequence>
   <Series.Sequence name="晴子拍手" durationInFrames={94} premountFor={fps}><Cheer/></Series.Sequence>
   <Series.Sequence name="恢复自信" durationInFrames={4*fps} premountFor={fps}><Resolve/></Series.Sequence>
   <Series.Sequence name="再来一遍" durationInFrames={4*fps} premountFor={fps}><Ending/></Series.Sequence>
  </Series>
  <Audio name="对白下的配乐与球馆声" src={staticFile('audio/background-ducked.wav')} premountFor={fps}/>
  <AbsoluteFill style={{background:'#171916',pointerEvents:'none',opacity:interpolate(frame,[0,.25*fps,durationInFrames-.35*fps,durationInFrames-1],[.6,0,0,.9],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
 </AbsoluteFill>;
};
export const RemotionRoot=()=> <>
 <Composition id="SakuragiHaruko" component={SakuragiHaruko} width={1280} height={720} fps={24} durationInFrames={720}/>
 <Folder name="Scenes">
  <Composition id="Opening" component={Opening} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Haruko" component={Haruko} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Shy" component={Shy} width={1280} height={720} fps={24} durationInFrames={86}/>
  <Composition id="Smile" component={Smile} width={1280} height={720} fps={24} durationInFrames={34}/>
  <Composition id="Practice" component={Practice} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Gather" component={Gather} width={1280} height={720} fps={24} durationInFrames={60}/>
  <Composition id="Cheer" component={Cheer} width={1280} height={720} fps={24} durationInFrames={94}/>
  <Composition id="Resolve" component={Resolve} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Ending" component={Ending} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Epilogue" component={Epilogue} width={1280} height={720} fps={24} durationInFrames={36}/>
 </Folder>
</>;
