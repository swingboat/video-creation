import {Video} from '@remotion/media';
import {AbsoluteFill,CanvasImage,staticFile,useVideoConfig} from 'remotion';
import {ready} from './media-status';
import {fontFamily} from './fonts';
type Props={scene:keyof typeof ready;art:string};
export const SceneVideo=({scene,art}:Props)=>{
 const {fps}=useVideoConfig();
 return <AbsoluteFill style={{background:'#181b18',fontFamily}}>
  {ready[scene]?<Video src={staticFile(`video/${scene}.mp4`)} volume={0} premountFor={fps} style={{width:'100%',height:'100%'}} objectFit="cover"/>:<><CanvasImage src={staticFile(`art/${art}`)} style={{width:'100%',height:'100%',objectFit:'cover'}}/><div style={{position:'absolute',left:36,top:24,color:'white',background:'#111a',padding:'6px 12px',fontSize:22}}>原画预览 · 连续动作生成中</div></>}
 </AbsoluteFill>;
};
