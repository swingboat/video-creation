import React,{useEffect,useState} from 'react';
import {AbsoluteFill,Composition,Folder,Series,continueRender,delayRender,interpolate,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {OpeningScene} from './scenes/OpeningScene';import {GatherScene} from './scenes/GatherScene';import {HandsScene} from './scenes/HandsScene';import {ReleaseScene} from './scenes/ReleaseScene';import {RimScene} from './scenes/RimScene';import {ReactionScene} from './scenes/ReactionScene';import {HeroScene} from './scenes/HeroScene';
import {SCORE_GLOBAL,BUZZER} from './math';
const Scoreboard:React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps,won=t>=SCORE_GLOBAL;
 const remaining=Math.max(0,2.4*(1-t/BUZZER)),clock='00:0'+(Math.ceil(remaining*10)/10).toFixed(1);
 return <div style={{position:'absolute',left:30,top:26,display:'flex',alignItems:'center',gap:18,padding:'12px 18px',backgroundColor:'#071d27e8',color:'#f3eddd',borderBottom:'2px solid #ab252d',boxShadow:'0 3px 12px #071c2830'}}>
  <div><div style={{fontSize:14,letterSpacing:3,color:'#c0cbd0',marginBottom:4}}>SHOHOKU</div><div style={{fontSize:22}}>湘北 <span style={{fontFamily:'Arial,sans-serif',fontSize:35,fontWeight:700,color:won?'#f0c677':'#fff',marginLeft:8}}>{won?80:77}</span></div></div>
  <div style={{height:43,width:1,backgroundColor:'#c0cbd040'}}/>
  <div><div style={{fontSize:14,letterSpacing:3,color:'#c0cbd0',marginBottom:4}}>RYONAN</div><div style={{fontSize:22}}>陵南 <span style={{fontFamily:'Arial,sans-serif',fontSize:35,fontWeight:700,color:'#fff',marginLeft:8}}>78</span></div></div>
  <div style={{paddingLeft:12,borderLeft:'1px solid #c0cbd040',textAlign:'right'}}><div style={{fontSize:13,color:'#bcc6cb',marginBottom:5}}>{t>=BUZZER?'终场':'决胜时刻'}</div><div style={{fontFamily:'Arial,sans-serif',fontVariantNumeric:'tabular-nums',fontSize:23,color:'#f0c677'}}>{clock}</div></div>
 </div>;
};
export const Film:React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps,[fontHandle]=useState(()=>delayRender('Loading local Chinese type'));
 useEffect(()=>{const f=new FontFace('NotoArena',`url(${staticFile('fonts/NotoSansSC.ttf')})`);f.load().then(x=>{document.fonts.add(x);continueRender(fontHandle);}).catch(()=>continueRender(fontHandle));},[fontHandle]);
 return <AbsoluteFill style={{backgroundColor:'#112932',fontFamily:'NotoArena,sans-serif'}}>
  <Series>
   <Series.Sequence name="终场前 · 全场" durationInFrames={90} premountFor={fps}><OpeningScene/></Series.Sequence>
   <Series.Sequence name="持球蓄力" durationInFrames={36} premountFor={fps}><GatherScene/></Series.Sequence>
   <Series.Sequence name="最后一投 · 手部特写" durationInFrames={54} premountFor={fps}><HandsScene/></Series.Sequence>
   <Series.Sequence name="起跳与出手" durationInFrames={120} premountFor={fps}><ReleaseScene/></Series.Sequence>
   <Series.Sequence name="篮球入网" durationInFrames={120} premountFor={fps}><RimScene/></Series.Sequence>
   <Series.Sequence name="看台与队友反应" durationInFrames={90} premountFor={fps}><ReactionScene/></Series.Sequence>
   <Series.Sequence name="终场 · 流川枫" durationInFrames={90} premountFor={fps}><HeroScene/></Series.Sequence>
  </Series>
  <Audio name="Arena sound" src={staticFile('audio/arena.wav')} premountFor={fps} volume={.9}/>
  <AbsoluteFill style={{pointerEvents:'none',background:'radial-gradient(ellipse at 55% 45%, transparent 35%, #061b2738 100%)'}}/>
  {t>=17?<AbsoluteFill style={{background:'linear-gradient(90deg,#071b27ed 0%,#071b2790 38%,transparent 68%)'}}/>:null}
  <Scoreboard/>
  {t<2.7?<div style={{position:'absolute',left:45,bottom:66,color:'#fff6e3',textShadow:'0 2px 8px #071b27',opacity:interpolate(frame,[0,12,65,81],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}><div style={{fontSize:18,letterSpacing:5,marginBottom:10}}>终场前</div><div style={{fontSize:38,letterSpacing:3}}>落后一分。</div></div>:null}
  {t>=4.2&&t<6?<div style={{position:'absolute',right:42,bottom:46,color:'#f9eed8',fontSize:23,letterSpacing:7,textShadow:'0 2px 8px #172b36'}}>最后一投</div>:null}
  {t>=SCORE_GLOBAL&&t<12.55?<div style={{position:'absolute',right:74,top:48,color:'#fff3ca',fontFamily:'Arial,sans-serif',fontWeight:700,fontSize:58,scale:interpolate(frame,[SCORE_GLOBAL*fps,(SCORE_GLOBAL+.18)*fps,(SCORE_GLOBAL+.8)*fps],[1.25,1,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}),textShadow:'0 3px 14px #0a2638'}}>+3</div>:null}
  {t>=17?<div style={{position:'absolute',left:48,top:270,color:'#f6edda',opacity:interpolate(frame,[17*fps,17.4*fps],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>
   <div style={{fontSize:18,letterSpacing:6,color:'#d2b77d',marginBottom:16}}>SHOHOKU  ·  NO.11</div><div style={{fontSize:60,letterSpacing:8,marginBottom:12}}>流川枫</div>
   <div style={{width:62,height:3,backgroundColor:'#b72832',margin:'16px 0 23px'}}/>
   <div style={{fontSize:29,letterSpacing:4,marginBottom:12}}>压哨三分</div><div style={{fontSize:22,color:'#d5dde0',letterSpacing:3}}>80 : 78　湘北获胜</div>
  </div>:null}
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <>
 <Composition id="RukawaFinalThree" component={Film} width={1280} height={720} fps={30} durationInFrames={600}/>
 <Folder name="Scenes">
  <Composition id="Opening" component={OpeningScene} width={1280} height={720} fps={30} durationInFrames={90}/>
  <Composition id="Gather" component={GatherScene} width={1280} height={720} fps={30} durationInFrames={36}/>
  <Composition id="Hands" component={HandsScene} width={1280} height={720} fps={30} durationInFrames={54}/>
  <Composition id="Release" component={ReleaseScene} width={1280} height={720} fps={30} durationInFrames={120}/>
  <Composition id="Rim" component={RimScene} width={1280} height={720} fps={30} durationInFrames={120}/>
  <Composition id="Reaction" component={ReactionScene} width={1280} height={720} fps={30} durationInFrames={90}/>
  <Composition id="Hero" component={HeroScene} width={1280} height={720} fps={30} durationInFrames={90}/>
 </Folder>
</>;
