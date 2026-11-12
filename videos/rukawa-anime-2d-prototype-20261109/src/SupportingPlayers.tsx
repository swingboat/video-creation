import React from 'react';
import {AbsoluteFill,CanvasImage,interpolate,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import bounds from './support-bounds.json';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
type PlayerProps={row:number;x:number;ground:number;height:number;pose:number;dx:number;jump:number};
const Player=({row,x,ground,height,pose,dx,jump}:PlayerProps)=>{
 const {fps}=useVideoConfig();const box=bounds[row][pose];const scale=height/bounds[row][0].h;
 const width=box.w*scale,hh=box.h*scale;
 return <>
  <svg width="1280" height="720" style={{position:'absolute',inset:0}}><ellipse cx={x+dx} cy={ground+2} rx={height*.17} ry={5+height*.006} fill="#46342a" opacity={.18+jump*.002}/></svg>
  <div data-player-row={row} data-pose={pose} style={{position:'absolute',left:x+dx-(box.footX-box.x)*scale,top:ground-hh+jump,width,height:hh,overflow:'hidden'}}>
   <CanvasImage src={staticFile('art/support-players-v2.png')} premountFor={fps} style={{position:'absolute',width:1024*scale,height:1536*scale,left:-box.x*scale,top:-box.y*scale}}/>
  </div>
 </>;
};
export const SupportingPlayers=()=>{
 const f=useCurrentFrame();
 return <AbsoluteFill style={{pointerEvents:'none'}}>
  <Player row={1} x={743} ground={495} height={206} pose={f<11?0:f<40?(Math.floor((f-11)/6)%2):2} dx={interpolate(f,[0,11,40,65],[0,0,30,38],clamp)} jump={f>11&&f<40?-Math.abs(Math.sin((f-11)*Math.PI/12))*3:0}/>
  <Player row={0} x={582} ground={552} height={300} pose={f<13?0:f<37?1:2} dx={interpolate(f,[0,13,37,65],[0,0,26,35],clamp)} jump={0}/>
  <Player row={2} x={1046} ground={569} height={348} pose={f<21?0:f<42?1:2} dx={interpolate(f,[0,21,42,65],[0,0,-18,-12],clamp)} jump={0}/>
  <Player row={3} x={858} ground={558} height={307} pose={f<23?0:f<38?1:2} dx={interpolate(f,[0,15,28,45,65],[0,-10,-55,-64,-62],clamp)} jump={interpolate(f,[0,23,30,35,43,65],[0,0,-36,-32,0,0],clamp)}/>
  <Player row={4} x={1192} ground={596} height={326} pose={f<17?0:f<43?1:2} dx={interpolate(f,[0,17,30,43,65],[0,0,18,10,8],clamp)} jump={f>17&&f<43?-Math.abs(Math.sin((f-17)*Math.PI/13))*3:0}/>
 </AbsoluteFill>;
};
