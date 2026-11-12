import {interpolate,useCurrentFrame,useVideoConfig} from 'remotion';
import {fontFamily} from './fonts';
type Props={children:string;start?:number;end?:number};
export const Caption=({children,start=.55,end=3.65}:Props)=>{
 const frame=useCurrentFrame();const {fps}=useVideoConfig();
 return <div style={{position:'absolute',left:70,right:70,bottom:34,textAlign:'center',fontFamily,fontSize:34,fontWeight:600,lineHeight:1.45,color:'#fffdf6',WebkitTextStroke:'1.2px #25251e',paintOrder:'stroke fill',textShadow:'0 2px 5px #000c',opacity:interpolate(frame,[start*fps,(start+.15)*fps,(end-.15)*fps,end*fps],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>{children}</div>;
};
