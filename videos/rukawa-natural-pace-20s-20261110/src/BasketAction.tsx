import React,{useEffect,useState} from 'react';
import {Audio,Video} from '@remotion/media';
import {AbsoluteFill,CanvasImage,cancelRender,continueRender,delayRender,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const sm=(a:number,b:number,t:number)=>{const u=clamp((t-a)/(b-a));return u*u*(3-2*u);};
type P={x:number;y:number};
function ballPosition(t:number):P{
 if(t<=2){const u=t/2;return{x:683*(1-u)**2+2*760*u*(1-u)+849*u*u,y:239*(1-u)**2+2*50*u*(1-u)+386*u*u};}
 const d=t-2;return{x:849+89*d,y:386+336*d+131.25*d*d};
}
function contact(t:number){const d=t-2;return sm(-.03,.22,d)*(1-sm(.85,1.12,d));}
function pulse(t:number){const d=t-3;return .9*contact(t)-(d<0?0:.28*Math.exp(-3*d)*Math.sin(9*d));}
function node(i:number,row:number,t:number):P{
 const u=row/8,a=(i+(row%2)*.5)*Math.PI/8,k=pulse(t),r=181-101*u+25*k*u;
 const age=Math.max(0,t-2),lean=89*Math.min(age,1)*contact(t)+12*k;
 return{x:849+r*Math.cos(a)+lean*u,y:394+300*u+(46-27*u)*Math.sin(a)+72*k*u*u};
}
const Net:React.FC<{t:number;front:boolean}>=({t,front})=>{
 const paths:React.ReactNode[]=[];
 for(let i=0;i<16;i++)for(let row=0;row<8;row++){
  if((Math.sin((i+.5)*Math.PI/8)>=0)!==front)continue;
  const a=node(i,row,t),b=node(i,row+1,t),c=node(i+(row%2?1:-1),row+1,t);
  paths.push(<path key={`s${i}-${row}`} d={`M${a.x} ${a.y}L${b.x} ${b.y}M${a.x} ${a.y}L${c.x} ${c.y}`} fill="none" stroke="#655c50" strokeWidth={6} opacity={front?.58:.3} strokeLinejoin="round"/>);
  paths.push(<path key={`r${i}-${row}`} d={`M${a.x} ${a.y}L${b.x} ${b.y}M${a.x} ${a.y}L${c.x} ${c.y}`} fill="none" stroke={front?'#eee3ce':'#c8c0ad'} strokeWidth={4.1} opacity={front?1:.72} strokeLinejoin="round"/>);
  paths.push(<circle key={`k${i}-${row}`} cx={b.x} cy={b.y} r={3.4} fill={front?'#eee3ce':'#c8c0ad'} stroke="#928673" strokeWidth={.8} opacity={front?1:.7}/>);
 }
 return <g strokeLinecap="round">{paths}</g>;
};
function nativeBall(t:number):P{
 const keys=[[0,420,150],[1.25,529,95],[1.875,560,312],[2.5,571,450],[3.125,583,570],[3.5,592,680],[5,592,900]];
 let j=1;while(j<keys.length-1&&t>keys[j][0])j++;
 const a=keys[j-1],b=keys[j],u=clamp((t-a[0])/(b[0]-a[0]));return{x:(a[1]+(b[1]-a[1])*u)*1.25,y:(a[2]+(b[2]-a[2])*u)*1.25};
}
export const BasketAction=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps*5,ball=ballPosition(t),hole=nativeBall(frame/fps*2.5);
 const [handle]=useState(()=>delayRender('Loading matching basketball texture'));
 useEffect(()=>{const im=new Image();im.onload=()=>continueRender(handle);im.onerror=()=>cancelRender(new Error('Ball texture failed to load'));im.src=staticFile('art/rim-scene.png');},[handle]);
 return <AbsoluteFill>
  <CanvasImage src={staticFile('art/rim-clean-plate.png')} style={{width:'100%',height:'100%',objectFit:'cover'}}/>
  <AbsoluteFill style={{maskImage:'linear-gradient(to bottom,transparent 61%,black 68%)',WebkitMaskImage:'linear-gradient(to bottom,transparent 61%,black 68%)'}}>
   <AbsoluteFill style={{maskImage:`radial-gradient(circle 114px at ${hole.x}px ${hole.y}px,transparent 92%,black 100%)`,WebkitMaskImage:`radial-gradient(circle 114px at ${hole.x}px ${hole.y}px,transparent 92%,black 100%)`}}>
    <AbsoluteFill style={{maskImage:'radial-gradient(ellipse 185px 160px at 650px 435px,transparent 95%,black 100%)',WebkitMaskImage:'radial-gradient(ellipse 185px 160px at 650px 435px,transparent 95%,black 100%)'}}>
     <Video src={staticFile('video/rim.mp4')} premountFor={fps} volume={.65} style={{width:'100%',height:'100%',objectFit:'cover'}}/>
    </AbsoluteFill>
   </AbsoluteFill>
  </AbsoluteFill>
  <svg viewBox="0 0 1672 941" preserveAspectRatio="none" style={{position:'absolute',width:'100%',height:'100%'}}>
   <defs><clipPath id="basketball-original-texture"><circle cx={0} cy={0} r={79.5}/></clipPath></defs>
   <Net t={t} front={false}/>
   <g transform={`translate(${ball.x} ${ball.y}) rotate(${-t*140})`}>
    <image href={staticFile('art/rim-scene.png')} x={-683} y={-239} width={1672} height={941} clipPath="url(#basketball-original-texture)"/>
    <circle r={80.3} fill="none" stroke="#342623" strokeWidth={2.9}/>
   </g>
   <Net t={t} front/>
   {t<2.3?<g fill="none" strokeLinecap="round"><path d="M1039 386A190 53 0 0 1 659 386" stroke="#392722" strokeWidth={14}/><path d="M1039 386A190 53 0 0 1 659 386" stroke="#db702c" strokeWidth={10}/><path d="M1039 383A190 53 0 0 1 659 383" stroke="#f59942" strokeWidth={2}/></g>:null}
  </svg>
  <Audio src={staticFile('audio/net.wav')} from={Math.round(.4*fps)} premountFor={fps} volume={.85}/>
 </AbsoluteFill>;
};
