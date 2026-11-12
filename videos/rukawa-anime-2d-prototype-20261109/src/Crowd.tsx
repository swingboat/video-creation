import React from 'react';
import {AbsoluteFill,CanvasImage,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
type Props={view:'court'|'hoop'};
export const Crowd=({view}:Props)=>{
 const frame=useCurrentFrame();const {fps}=useVideoConfig();
 const src=view==='court'?'art/court-cheer-v2.png':'art/hoop-cheer-v2.png';
 const polygon=view==='court'?'polygon(0px 25px,1050px 169px,1050px 291px,0px 226px)':'polygon(0px 565px,300px 510px,550px 480px,800px 470px,1045px 475px,1103px 540px,1100px 720px,0px 720px)';
 return <AbsoluteFill style={{clipPath:polygon,pointerEvents:'none'}}>
  {Array.from({length:6},(_,i)=>{
   const span=view==='court'?175:184;
   // Stagger the two drawn gesture states; the architecture stays on the base plate.
   const phase=Math.floor((frame+i*3)/(view==='hoop'&&frame>35?6:9))%2;
   return <AbsoluteFill key={i} data-crowd-group={i} data-gesture={phase} style={{clipPath:`inset(0px ${Math.max(0,1280-(i+1)*span)}px 0px ${i*span}px)`}}>
    <CanvasImage src={staticFile(src)} premountFor={fps} style={{width:1280,height:720,opacity:phase}}/>
   </AbsoluteFill>;
  })}
 </AbsoluteFill>;
};
