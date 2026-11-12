import {useEffect,useState} from 'react';import {cancelRender,continueRender,delayRender,staticFile} from 'remotion';
let load:Promise<void>|undefined;
export function useLocalFont(){const [handle]=useState(()=>delayRender('Loading local font'));useEffect(()=>{if(!load){load=new FontFace('Arena',`url(${staticFile('fonts/NotoSansSC.ttf')})`).load().then(f=>{document.fonts.add(f);});}load.then(()=>continueRender(handle)).catch(e=>cancelRender(e));},[handle]);}
