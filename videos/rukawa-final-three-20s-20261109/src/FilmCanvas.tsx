import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {ASSETS,Asset,Painter} from './gpu';
import {drawScene,Shot} from './scenes/drawScenes';
export const FilmCanvas:React.FC<{shot:Shot}>=({shot})=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),ref=useRef<HTMLCanvasElement>(null),painter=useRef<Painter|null>(null),handle=useRef<number|null>(null),[images,setImages]=useState<Record<Asset,HTMLImageElement>|null>(null);
 if(handle.current===null&&!images)handle.current=delayRender('Loading local anime artwork');
 useEffect(()=>{let active=true;Promise.all((Object.keys(ASSETS) as Asset[]).map(key=>new Promise<[Asset,HTMLImageElement]>((resolve,reject)=>{const im=new Image();im.onload=()=>resolve([key,im]);im.onerror=()=>reject(Error('Missing artwork '+key));im.src=staticFile(ASSETS[key]);}))).then(entries=>{if(active)setImages(Object.fromEntries(entries) as Record<Asset,HTMLImageElement>);});return()=>{active=false;};},[]);
 useLayoutEffect(()=>{if(!ref.current||!images)return;if(!painter.current)painter.current=new Painter(ref.current,images);drawScene(painter.current,shot,frame/fps);if(handle.current!==null){continueRender(handle.current);handle.current=null;}},[frame,fps,images,shot]);
 return <canvas ref={ref} width={1280} height={720} style={{position:'absolute',width:'100%',height:'100%'}}/>;
};
