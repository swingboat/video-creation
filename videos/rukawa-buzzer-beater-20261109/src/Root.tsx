import React, {useEffect, useState} from 'react';
import {AbsoluteFill, CanvasImage, Composition, continueRender, delayRender, cancelRender, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio, Video} from '@remotion/media';

type FilmProps = {source: string; preview: boolean};
const Film: React.FC<FilmProps> = ({source, preview}) => {
 const [fontHandle]=useState(()=>delayRender('Loading project font'));
 useEffect(()=>{
  const face=new FontFace('FilmHan', `url(${staticFile('fonts/Arial-Unicode.ttf')})`);
  face.load().then(font=>{document.fonts.add(font);continueRender(fontHandle);}).catch(cancelRender);
 },[fontHandle]);
 const frame=useCurrentFrame();const {fps}=useVideoConfig();const t=frame/fps;
 const clock=t<5.2?5.2-t*.67:t<9.15?1.716*(1-(t-5.2)/3.95):0;
 const won=t>=13.85;
 return <AbsoluteFill style={{backgroundColor:'#090d12',color:'#f4f0e6',fontFamily:'Arial, FilmHan, "PingFang SC", "Microsoft YaHei", sans-serif'}}>
  {preview?<CanvasImage src={staticFile(source)} style={{width:'100%',height:'100%'}} premountFor={fps}/>:<Video src={staticFile(source)} muted premountFor={fps} style={{width:'100%',height:'100%'}}/>}
  <Audio src={staticFile('court-soundscape.wav')} premountFor={fps} volume={0.9}/>
  <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(3,7,13,.25),transparent 25%,transparent 75%,rgba(3,7,13,.38))'}}/>
  <div style={{position:'absolute',left:0,right:0,top:0,height:30,background:'#080c11'}}/>
  <div style={{position:'absolute',left:0,right:0,bottom:0,height:30,background:'#080c11'}}/>
  <div style={{position:'absolute',left:46,top:49,display:'flex',height:58,boxShadow:'0 6px 30px #0005',fontWeight:700}}>
   <div style={{background:'#9b1626',padding:'9px 18px',borderLeft:'3px solid #e5cda4'}}>
    <div style={{fontSize:11,letterSpacing:2,opacity:.8}}>SHOHOKU</div><div style={{fontSize:20,letterSpacing:3}}>湘北</div>
   </div>
   <div style={{background:'#121b25ed',display:'flex',alignItems:'center',padding:'0 20px',gap:17,fontSize:29,fontVariantNumeric:'tabular-nums'}}><span style={{color:won?'#f4ce84':'#fff'}}>{won?'77':'74'}</span><span style={{fontSize:16,color:'#73818e'}}>:</span><span>76</span></div>
   <div style={{background:'#24303be8',padding:'8px 14px',minWidth:78,textAlign:'center'}}><div style={{fontSize:10,letterSpacing:2,color:'#c2b7a3'}}>{won?'FINAL':'4TH'}</div><div style={{fontSize:23,color:clock===0?'#ff6a61':'#f4f0e6',fontVariantNumeric:'tabular-nums'}}>{clock.toFixed(1).padStart(4,'0')}</div></div>
  </div>
  <div style={{position:'absolute',right:47,top:53,fontSize:11,letterSpacing:3,color:'#e4d4b5',textShadow:'0 1px 5px #000'}}>THE LAST SHOT <span style={{marginLeft:12,color:'#b33d45'}}>●</span></div>
  <div style={{position:'absolute',left:48,bottom:51,opacity:interpolate(frame,[0,.5*fps,2.7*fps,3.1*fps],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>
   <div style={{fontSize:11,letterSpacing:4,color:'#dfc08b',marginBottom:8}}>SLAM DUNK / FAN ANIMATION</div><div style={{fontSize:29,fontWeight:700,letterSpacing:4}}>最后一投</div>
  </div>
  {t>=6.1&&t<9.15?<div style={{position:'absolute',right:49,bottom:53,fontSize:13,letterSpacing:3,color:'#e3cfad'}}>11 / RUKAWA</div>:null}
  {t>=15.4?<div style={{position:'absolute',left:50,bottom:56,opacity:interpolate(frame,[15.4*fps,16.2*fps],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}),translate:`0 ${interpolate(frame,[15.4*fps,16.2*fps],[15,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}px`}}>
   <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:10}}><div style={{height:2,width:34,background:'#d6b67e'}}/><span style={{fontSize:12,letterSpacing:4,color:'#ecd3a8'}}>THREE POINTS. ONE WIN.</span></div>
   <div style={{fontSize:44,fontWeight:700,letterSpacing:8,textShadow:'0 2px 15px #0006'}}>流川枫</div>
   <div style={{fontSize:15,letterSpacing:5,marginTop:10,color:'#ecdfca'}}>三分绝杀 · 湘北获胜</div>
  </div>:null}
 </AbsoluteFill>;
};
export const Root = () => <Composition id="RukawaFinalShot" component={Film} durationInFrames={480} fps={24} width={1280} height={720} defaultProps={{source:'picture.mp4',preview:false}}/>;
