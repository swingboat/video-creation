import React,{useEffect,useState} from 'react';
import {AbsoluteFill,Composition,continueRender,delayRender,staticFile} from 'remotion';
import {CorrectedGather} from './CorrectedGather';
const GatherShot:React.FC=()=>{
 const [handle]=useState(()=>delayRender('Chinese font'));
 useEffect(()=>{const f=new FontFace('NotoShot',`url(${staticFile('fonts/NotoSansSC.ttf')})`);f.load().then(font=>{document.fonts.add(font);continueRender(handle);}).catch(()=>continueRender(handle));},[handle]);
 return <AbsoluteFill style={{backgroundColor:'#e3dfd4'}}>
  <CorrectedGather/>
  <div style={{position:'absolute',left:42,top:35,fontFamily:'NotoShot,sans-serif',fontSize:21,color:'#202b32',letterSpacing:2}}>流川枫 · 蓄力微动作预览</div>
  <div style={{position:'absolute',left:43,top:73,width:38,height:2,backgroundColor:'#b5242c'}}/>
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="RukawaGatherPreview" component={GatherShot} width={1280} height={720} fps={30} durationInFrames={60}/>;
