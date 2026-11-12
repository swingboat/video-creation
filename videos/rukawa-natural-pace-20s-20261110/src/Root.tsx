import React from 'react';
import {Audio} from '@remotion/media';
import {AbsoluteFill,Composition,Folder,Series,interpolate,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {DribbleScene} from './DribbleScene';
import {DefenderScene} from './DefenderScene';
import {OpeningScene} from './OpeningScene';
import {ShotScene,PilotScene} from './ShotScene';
import {RimScene} from './RimScene';
import {CelebrationScene} from './CelebrationScene';
import {CrowdScene} from './CrowdScene';
import {HeroScene} from './HeroScene';
import {useLocalFont} from './font';
import {BUZZER_SECONDS,SCORE_SECONDS} from './timing';
import {clipsReady} from './media-status';
const Film=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps;useLocalFont();
 const complete=clipsReady.dribble&&clipsReady.defender&&clipsReady.close&&clipsReady.shot&&clipsReady.rim&&clipsReady.celebrate&&clipsReady.crowd&&clipsReady.hero;
 const score=t>=SCORE_SECONDS?80:77,remaining=Math.max(0,BUZZER_SECONDS-t);
 return <AbsoluteFill style={{backgroundColor:'#193b3d',fontFamily:'Arena,sans-serif'}}>
  <Series>
   <Series.Sequence name="最后七秒 · 控球" durationInFrames={1.5*fps} premountFor={fps}><DribbleScene/></Series.Sequence>
   <Series.Sequence name="仙道 · 防守判断" durationInFrames={2.5*fps} premountFor={fps}><DefenderScene/></Series.Sequence>
   <Series.Sequence name="抬眼 · 锁定篮筐" durationInFrames={2*fps} premountFor={fps}><OpeningScene/></Series.Sequence>
   <Series.Sequence name="起跳 · 封盖 · 出手" durationInFrames={2*fps} premountFor={fps}><ShotScene/></Series.Sequence>
   <Series.Sequence name="压哨 · 入网" durationInFrames={2*fps} premountFor={fps}><RimScene/></Series.Sequence>
   <Series.Sequence name="湘北 · 庆祝" durationInFrames={2*fps} premountFor={fps}><CelebrationScene/></Series.Sequence>
   <Series.Sequence name="看台 · 欢呼" durationInFrames={4*fps} premountFor={fps}><CrowdScene/></Series.Sequence>
   <Series.Sequence name="流川枫 · 终场" durationInFrames={4*fps} premountFor={fps}><HeroScene/></Series.Sequence>
  </Series>
  {complete?<Audio src={staticFile('audio/buzzer.wav')} from={Math.round(BUZZER_SECONDS*fps)} premountFor={fps} volume={.85}/>:null}
  {complete?<div style={{position:'absolute',left:28,top:24,padding:'8px 13px',backgroundColor:'#132c30db',color:'#fff2da',fontSize:19,display:'flex',gap:18,borderBottom:'2px solid #a92b30'}}><span>湘北 <b style={{color:t>=SCORE_SECONDS?'#f5cf8e':'#fff2da'}}>{score}</b> : 78 陵南</span><span style={{fontFamily:'Arial,sans-serif',color:'#f5cf8e',fontVariantNumeric:'tabular-nums'}}>{t>=BUZZER_SECONDS?'00.0':(Math.ceil(remaining*10)/10).toFixed(1).padStart(4,'0')}</span></div>:null}
  {complete&&t>=16?<AbsoluteFill style={{background:'linear-gradient(90deg,#122e33bc,transparent 65%)',pointerEvents:'none'}}/>:null}
  {complete&&t>=16?<div style={{position:'absolute',left:42,top:330,color:'#fff0d7',opacity:interpolate(frame,[16*fps,16.4*fps],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}><div style={{fontSize:43,letterSpacing:5}}>流川枫</div><div style={{height:3,width:50,background:'#bd3437',margin:'18px 0'}}/><div style={{fontSize:24,letterSpacing:3}}>压哨三分</div><div style={{fontSize:20,marginTop:11}}>80 : 78　湘北获胜</div></div>:null}
 </AbsoluteFill>;
};
export const Root=()=> <>
 <Composition id="RukawaNaturalPace" component={Film} width={1280} height={720} fps={24} durationInFrames={480}/>
 <Folder name="Scenes">
  <Composition id="Dribble" component={DribbleScene} width={1280} height={720} fps={24} durationInFrames={36}/>
  <Composition id="Defender" component={DefenderScene} width={1280} height={720} fps={24} durationInFrames={60}/>
  <Composition id="Opening" component={OpeningScene} width={1280} height={720} fps={24} durationInFrames={48}/>
  <Composition id="Shot" component={ShotScene} width={1280} height={720} fps={24} durationInFrames={48}/>
  <Composition id="Rim" component={RimScene} width={1280} height={720} fps={24} durationInFrames={48}/>
  <Composition id="Celebration" component={CelebrationScene} width={1280} height={720} fps={24} durationInFrames={48}/>
  <Composition id="Crowd" component={CrowdScene} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="Hero" component={HeroScene} width={1280} height={720} fps={24} durationInFrames={96}/>
  <Composition id="MotionPilot" component={PilotScene} width={1280} height={720} fps={24} durationInFrames={49}/>
 </Folder>
</>;
