import React from 'react';
import {AbsoluteFill,CanvasImage,Easing,interpolate,useCurrentFrame,useVideoConfig,staticFile} from 'remotion';
import {C,font} from './theme';
import timeline from './timeline.json';

export const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
export const ease={...clamp,easing:Easing.bezier(.16,1,.3,1)};
export function useCue(id:string){
 const frame=useCurrentFrame();const {fps}=useVideoConfig();
 const scene=timeline.scenes.find(s=>s.id===id)!;
 const ms=frame/fps*1000;
 return {frame,fps,scene,step:Math.max(0,scene.utterances.findLastIndex(u=>ms>=u.startMs)),ms};
}
export const Fade:React.FC<{children:React.ReactNode;delay?:number;style?:React.CSSProperties}>=({children,delay=0,style})=>{
 const frame=useCurrentFrame();return <div style={{opacity:interpolate(frame,[delay,delay+22],[0,1],ease),translate:interpolate(frame,[delay,delay+28],['0px 24px','0px 0px'],ease),...style}}>{children}</div>;
};
export const Frame:React.FC<{id:string;chapter:string;children:React.ReactNode;accent?:string}>=({id,chapter,children,accent=C.yellow})=>{
 const frame=useCurrentFrame();const {durationInFrames,fps}=useVideoConfig();const scene=timeline.scenes.find(s=>s.id===id)!;
 return <AbsoluteFill style={{fontFamily:font,color:C.ink,background:C.bg,overflow:'hidden'}}>
 <AbsoluteFill style={{backgroundImage:'radial-gradient(circle at 82% 25%,rgba(66,88,118,.18),transparent 46%),linear-gradient(rgba(160,180,215,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(160,180,215,.035) 1px,transparent 1px)',backgroundSize:'auto,80px 80px,80px 80px'}}/>
 <div style={{position:'absolute',left:90,top:50,display:'flex',gap:18,alignItems:'center'}}><CanvasImage src={staticFile('huggingface.svg')} premountFor={fps} style={{width:42,height:42}}/><span style={{fontSize:25,fontWeight:650,letterSpacing:1}}>HUGGING FACE</span><span style={{width:1,height:25,background:C.line,margin:'0 12px'}}/><span style={{color:C.muted,fontSize:25}}>零基础使用指南</span></div>
 <div style={{position:'absolute',right:90,top:56,fontSize:25,color:C.muted,letterSpacing:2}}><span style={{color:accent,fontWeight:750}}>{chapter}</span> / 10</div>
 <div style={{position:'absolute',inset:'0',opacity:interpolate(frame,[0,12,durationInFrames-12,durationInFrames-1],[0,1,1,0],clamp)}}>{children}</div>
 <div style={{position:'absolute',bottom:0,left:0,width:1920,height:5,background:C.panel}}><div style={{height:'100%',background:accent,width:interpolate(scene.startFrame+frame,[0,timeline.durationInFrames],[0,1920],clamp)}}/></div>
 </AbsoluteFill>;
};
export const Heading:React.FC<{eyebrow:string;children:React.ReactNode;sub?:string;size?:number}>=({eyebrow,children,sub,size=84})=><Fade style={{position:'absolute',left:90,top:140}}><div style={{fontSize:25,color:C.yellow,fontWeight:600,letterSpacing:3,marginBottom:18}}>{eyebrow}</div><div style={{fontSize:size,fontWeight:750,letterSpacing:-3,lineHeight:1.2}}>{children}</div>{sub?<div style={{fontSize:35,color:C.muted,marginTop:22,lineHeight:1.5}}>{sub}</div>:null}</Fade>;
export const Icon:React.FC<{kind:string;size?:number;color?:string}>=({kind,size=64,color=C.yellow})=>{
 const paths:Record<string,React.ReactNode>={
 model:<><path d="M12 3 3 8v9l9 5 9-5V8Z M3 8l9 5 9-5 M12 13v9"/><path d="m7 5 10 6"/></>,
 data:<><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v7c0 4 18 4 18 0V5M3 12v7c0 4 18 4 18 0v-7"/></>,
 app:<><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 8h18M8 8v13"/><path d="m13 12 5 3-5 3Z"/></>,
 audio:<><rect x="9" y="2" width="6" height="13" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/></>,
 book:<><path d="M12 5c-3-3-6-3-10-2v16c4-1 7-1 10 2 3-3 6-3 10-2V3c-4-1-7-1-10 2ZM12 5v16"/></>,
 file:<><path d="M5 2h9l5 5v15H5Z M14 2v5h5M8 12h8M8 16h8"/></>,
 code:<><path d="m8 5-6 7 6 7m8-14 6 7-6 7m-3-17-2 20"/></>,
 check:<path d="m4 12 5 5L20 6"/>,
 arrow:<path d="M3 12h18m-7-7 7 7-7 7"/>,
 cloud:<><path d="M6 18a5 5 0 0 1-1-10 7 7 0 0 1 13-2 6 6 0 0 1 0 12Z"/></>,
 screen:<><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M12 17v5M6 22h12"/></>,
 users:<><circle cx="9" cy="7" r="4"/><path d="M1 21v-3a8 8 0 0 1 16 0v3M17 3a4 4 0 0 1 0 8M20 15a7 7 0 0 1 3 6"/></>,
 search:<><circle cx="10" cy="10" r="7"/><path d="m15 15 7 7"/></>,
 folder:<><path d="M2 5h8l2 3h10v13H2Z"/></>,
 };
 return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{paths[kind]??paths.model}</svg>;
};
export const Tag:React.FC<{children:React.ReactNode;color?:string}>=({children,color=C.yellow})=><span style={{display:'inline-flex',padding:'10px 20px',border:`1px solid ${color}55`,borderRadius:10,fontSize:29,color,background:`${color}12`,alignItems:'center'}}>{children}</span>;
export const Screen:React.FC<{src:string;url:string;left?:number;top?:number;width?:number;height?:number;zoom?:number;x?:number;y?:number;children?:React.ReactNode}>=({src,url,left=690,top=335,width=1140,height=545,zoom=1,x=0,y=0,children})=>{
 const {fps}=useVideoConfig();
 return <Fade delay={10} style={{position:'absolute',left,top,width,height:height+58,borderRadius:20,overflow:'hidden',border:`1px solid ${C.line}`,boxShadow:'0 24px 80px #0006',background:'#fff'}}>
 <div style={{height:58,background:'#1B2331',display:'flex',alignItems:'center',padding:'0 24px',gap:10}}>{['#FF736D','#E8BD57','#69BD89'].map(c=><span key={c} style={{background:c,width:12,height:12,borderRadius:'50%'}}/>)}<span style={{fontFamily:'monospace',fontSize:22,color:'#CDD5E1',marginLeft:18}}>{url}</span></div>
 <div style={{position:'relative',height,overflow:'hidden'}}><CanvasImage src={staticFile(src)} premountFor={fps} style={{position:'absolute',width:1440*zoom,height:1000*zoom,left:x,top:y,maxWidth:'none'}}/>{children}</div>
 </Fade>;
};
export const Spot:React.FC<{x:number;y:number;w:number;h:number;label?:string;color?:string}>=({x,y,w,h,label,color=C.yellow})=>{
 const frame=useCurrentFrame();return <div style={{position:'absolute',left:x,top:y,width:w,height:h,border:`4px solid ${color}`,borderRadius:12,boxShadow:`0 0 0 9999px #0c111a18,0 0 28px ${color}33`,opacity:interpolate(frame,[0,15],[0,1],clamp)}}>{label?<span style={{position:'absolute',left:0,top:-46,color:C.bg,background:color,padding:'3px 15px',borderRadius:'7px 7px 0 0',fontSize:26,fontWeight:700,whiteSpace:'nowrap'}}>{label}</span>:null}</div>;
};
export const Cursor:React.FC<{x:number;y:number;click?:boolean}>=({x,y,click=false})=>{
 const frame=useCurrentFrame();return <div style={{position:'absolute',left:x,top:y,translate:interpolate(frame,[0,35],['35px 50px','0px 0px'],ease)}}>{click?<div style={{position:'absolute',width:65,height:65,left:-25,top:-25,border:'3px solid #FFD24B',borderRadius:'50%',opacity:(1-Math.sin(frame/12))/3}}/>:null}<svg width="36" height="46" viewBox="0 0 30 40"><path d="M2 2v30l8-8 7 14 6-3-7-14h12Z" fill="#fff" stroke="#0c111a" strokeWidth="2"/></svg></div>;
};
export const ListItem:React.FC<{number:string;label:string;detail:string;active?:boolean;icon?:string}>=({number,label,detail,active=false,icon})=><div style={{padding:'20px 24px',borderLeft:`4px solid ${active?C.yellow:C.line}`,background:active?'#FFD24B0D':'transparent',marginBottom:14,borderRadius:'0 12px 12px 0'}}><div style={{display:'flex',alignItems:'center',gap:16,fontSize:34,fontWeight:650,color:active?C.yellow:C.ink}}>{icon?<Icon kind={icon} size={34} color={active?C.yellow:C.muted}/>:<span style={{fontSize:25,fontFamily:'monospace',color:C.muted}}>{number}</span>}{label}</div><div style={{fontSize:29,color:C.muted,marginTop:12,lineHeight:1.5}}>{detail}</div></div>;
