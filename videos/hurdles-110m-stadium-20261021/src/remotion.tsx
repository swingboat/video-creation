import React,{useEffect,useMemo,useRef,useState} from 'react';
import {AbsoluteFill,Composition,continueRender,delayRender,registerRoot,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
type HurdleWindow=Window & {hurdleApp?:{ready:boolean;setPlaying:(p:boolean)=>void;setTime:(t:number)=>void;setCamera:(m:string)=>void;getState:()=>unknown}};
const HurdleScene:React.FC=()=>{
 const frame=useCurrentFrame();const {fps}=useVideoConfig();const ref=useRef<HTMLIFrameElement>(null);const [loaded,setLoaded]=useState(false);
 const handle=useMemo(()=>delayRender('Rendering stadium frame '+frame),[frame]);
 useEffect(()=>{if(!loaded)return;const w=ref.current?.contentWindow as HurdleWindow|null;if(!w)return;
  const draw=()=>{if(!w.hurdleApp?.ready)return false;w.hurdleApp.setPlaying(false);w.hurdleApp.setCamera('cinematic');w.hurdleApp.setTime(frame/fps);w.document.body.classList.add('clean');w.document.querySelector('#loading')?.remove();continueRender(handle);return true;};
  if(draw())return;const id=setInterval(()=>{if(draw())clearInterval(id);},30);return()=>clearInterval(id);
 },[frame,fps,loaded,handle]);
 return <AbsoluteFill style={{backgroundColor:'#c7d8d7'}}><iframe ref={ref} title="110m hurdles" src={staticFile('hurdle-110-3d.html')+'?paused=1&t=0&clean=1&render=1'} onLoad={()=>setLoaded(true)} style={{width:'100%',height:'100%',border:0}}/></AbsoluteFill>;
};
const CGScene:React.FC=()=> <AbsoluteFill style={{backgroundColor:'#202b22'}}>
 <Video src={staticFile('assets/offline/hurdles-cycles.mp4')} playbackRate={1} muted style={{width:'100%',height:'100%',objectFit:'contain'}}/>
 </AbsoluteFill>;
const Root:React.FC=()=> <>
 <Composition id="HurdleCG" component={CGScene} durationInFrames={66} fps={24} width={1280} height={720}/>\n <Composition id="Hurdle110" component={HurdleScene} durationInFrames={660} fps={30} width={1920} height={1080}/>
 </>;
registerRoot(Root);
