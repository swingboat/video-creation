import React from 'react';
import {Audio} from '@remotion/media';
import {staticFile} from 'remotion';
import {AbsoluteFill,Composition,Folder,Series,interpolate,useCurrentFrame,useVideoConfig} from 'remotion';
import {OpeningScene} from './OpeningScene';import {ShotScene,PilotScene} from './ShotScene';import {RimScene} from './RimScene';import {CelebrationScene} from './CelebrationScene';import {HeroScene} from './HeroScene';import {useLocalFont} from './font';import {BUZZER_SECONDS,SCORE_SECONDS} from './timing';import {clipsReady} from './media-status';
const Film=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps;useLocalFont();
 const complete=clipsReady.close&&clipsReady.shot&&clipsReady.rim&&clipsReady.celebrate&&clipsReady.hero;
 const score=t>=SCORE_SECONDS?80:77,remaining=Math.max(0,2.4*(1-t/BUZZER_SECONDS));
 return <AbsoluteFill style={{backgroundColor:'#193b3d',fontFamily:'Arena,sans-serif'}}>
  <Series>
   <Series.Sequence name="屏息 · 最后一投" durationInFrames={72} premountFor={fps}><OpeningScene/></Series.Sequence>
   <Series.Sequence name="蓄力 · 起跳 · 封盖 · 出手" durationInFrames={96} premountFor={fps}><ShotScene/></Series.Sequence>
   <Series.Sequence name="压哨 · 篮球入网" durationInFrames={120} premountFor={fps}><RimScene/></Series.Sequence>
   <Series.Sequence name="湘北 · 获胜庆祝" durationInFrames={96} premountFor={fps}><CelebrationScene/></Series.Sequence>
   <Series.Sequence name="流川枫 · 终场" durationInFrames={96} premountFor={fps}><HeroScene/></Series.Sequence>
  </Series>
  {complete?<Audio src={staticFile('audio/buzzer.wav')} from={Math.round(BUZZER_SECONDS*fps)} premountFor={fps} volume={.85}/>:null}
  {complete?<div style={{position:'absolute',left:28,top:24,padding:'8px 13px',backgroundColor:'#132c30db',color:'#fff2da',fontSize:19,display:'flex',gap:18,borderBottom:'2px solid #a92b30'}}><span>湘北 <b style={{color:t>=SCORE_SECONDS?'#f5cf8e':'#fff2da'}}>{score}</b> : 78 陵南</span><span style={{fontFamily:'Arial,sans-serif',color:'#f5cf8e',fontVariantNumeric:'tabular-nums'}}>{t>=BUZZER_SECONDS?'00.0':(Math.ceil(remaining*10)/10).toFixed(1).padStart(4,'0')}</span></div>:null}
  {complete&&t>=16?<AbsoluteFill style={{background:'linear-gradient(90deg,#122e33bc,transparent 65%)',pointerEvents:'none'}}/>:null}
  {complete&&t>=16?<div style={{position:'absolute',left:42,top:330,color:'#fff0d7',opacity:interpolate(frame,[16*fps,16.4*fps],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}><div style={{fontSize:43,letterSpacing:5}}>流川枫</div><div style={{height:3,width:50,background:'#bd3437',margin:'18px 0'}}/><div style={{fontSize:24,letterSpacing:3}}>压哨三分</div><div style={{fontSize:20,marginTop:11}}>80 : 78　湘北获胜</div></div>:null}
 </AbsoluteFill>;
};
export const Root=()=> <>
 <Composition id="RukawaRemake" component={Film} width={1280} height={720} fps={24} durationInFrames={480}/>
 <Folder name="Scenes">
  <Composition id="Opening" component={OpeningScene} width={1280} height={720} fps={24} durationInFrames={72}/>
  <Composition id="Shot" component={ShotScene} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Rim" component={RimScene} width={1280} height={720} fps={24} durationInFrames={120}/>
  <Composition id="Celebration" component={CelebrationScene} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Hero" component={HeroScene} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="MotionPilot" component={PilotScene} width={1280} height={720} fps={24} durationInFrames={49}/>
 </Folder>
</>;
