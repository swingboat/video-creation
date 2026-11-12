import React from 'react';
import {AbsoluteFill,CanvasImage,staticFile} from 'remotion';
export const PendingFrame:React.FC<{image:string}>=({image})=><AbsoluteFill><CanvasImage src={staticFile(image)} style={{width:'100%',height:'100%',objectFit:'cover'}}/><div style={{position:'absolute',left:28,bottom:24,padding:'9px 15px',background:'#122b30e6',color:'#fff2d8',fontSize:20,fontFamily:'sans-serif'}}>原画预览 · 连续片段制作中</div></AbsoluteFill>;
