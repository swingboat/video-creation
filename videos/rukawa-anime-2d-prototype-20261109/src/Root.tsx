import React,{useEffect,useState} from 'react';
import {AbsoluteFill,Composition,continueRender,delayRender,cancelRender,interpolate,Sequence,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {CourtShot} from './CourtShot';
import {HoopShot} from './HoopShot';
const Film=()=>{
 const frame=useCurrentFrame();const {fps}=useVideoConfig();
 const [handle]=useState(()=>delayRender('Load local title font'));
 useEffect(()=>{const font=new FontFace('FilmHan',`url(${staticFile('fonts/Arial-Unicode.ttf')})`);font.load().then(f=>{document.fonts.add(f);continueRender(handle);}).catch(cancelRender);},[handle]);
 const won=frame>=3.55*fps;
 return <AbsoluteFill style={{fontFamily:'FilmHan,Arial,sans-serif',background:'#171c20',overflow:'hidden'}}>
  <Sequence name="起跳 / 球场与球员" durationInFrames={2.2*fps} premountFor={fps}><CourtShot/></Sequence>
  <Sequence name="篮筐 / 入网与观众" from={2.2*fps} durationInFrames={2.8*fps} premountFor={fps}><HoopShot/></Sequence>
  <Audio src={staticFile('soundscape.wav')} premountFor={fps} volume={.9}/>
  <div style={{position:'absolute',left:0,right:0,top:0,height:23,background:'#10171b'}}/>
  <div style={{position:'absolute',left:0,right:0,bottom:0,height:23,background:'#10171b'}}/>
  <div style={{position:'absolute',left:35,top:38,display:'flex',color:'#f4ecda',boxShadow:'2px 3px 0 #1c18197d',fontWeight:700}}>
   <div style={{background:'#a02c30',padding:'7px 14px',fontSize:18}}>湘北</div>
   <div style={{background:'#252d32',padding:'5px 14px',fontSize:23,letterSpacing:4}}>{won?'77':'74'} : 76</div>
   <div style={{background:'#ded2b9',color:'#302c28',padding:'9px 12px',fontSize:13}}>{won?'终场':'第四节'}</div>
  </div>
  <div style={{position:'absolute',left:39,bottom:41,color:'#fff7e4',textShadow:'1px 2px 2px #1d2928',opacity:interpolate(frame,[3.9*fps,4.25*fps],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>
   <span style={{fontSize:29,letterSpacing:5,fontWeight:700}}>三分，逆转。</span>
  </div>
 </AbsoluteFill>;
};
export const Root=()=> <>
 <Composition id="RukawaAnimeSample" component={Film} durationInFrames={150} fps={30} width={1280} height={720}/>
 <Composition id="CourtShot" component={CourtShot} durationInFrames={66} fps={30} width={1280} height={720}/>
 <Composition id="HoopShot" component={HoopShot} durationInFrames={84} fps={30} width={1280} height={720}/>
</>;
