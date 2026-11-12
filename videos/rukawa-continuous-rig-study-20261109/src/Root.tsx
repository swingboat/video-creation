import React, {useEffect,useState} from 'react';
import {AbsoluteFill,Composition,continueRender,delayRender,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';

const Film: React.FC = () => {
  const frame=useCurrentFrame();
  const {fps}=useVideoConfig();
  const [fontHandle]=useState(()=>delayRender('Loading local Chinese font'));
  useEffect(()=>{
    const font=new FontFace('StudyChinese',`url(${staticFile('fonts/NotoSansSC.ttf')})`);
    font.load().then(f=>{document.fonts.add(f);continueRender(fontHandle);}).catch(()=>continueRender(fontHandle));
  },[fontHandle]);
  const t=frame/fps;
  const phase=t<.55?'持球准备':t<1.62?'屈膝蓄力':t<1.94?'起跳举球':t<2.76?'出手与落地':t<3.16?'保持随球动作':'入网与多人反应';
  return <AbsoluteFill style={{backgroundColor:'#273536',fontFamily:'StudyChinese, sans-serif'}}>
    <Video name="Continuous mesh animation" src={staticFile('rig-study-picture.mp4')+'?v=continuous-rig-4'} muted premountFor={fps} style={{position:'absolute',width:'100%',height:'100%'}}/>
    <div style={{position:'absolute',top:24,left:28,color:'#fff',backgroundColor:'#18282be6',padding:'12px 18px',borderLeft:'4px solid #e5bd6a'}}>
      <div style={{fontSize:26}}>连续蒙皮 · 动作测试</div>
      <div style={{fontSize:17,color:'#c4d1d1',marginTop:5}}>6 名球员 / 6 名观众 / 固定机位观察</div>
    </div>
    <div style={{position:'absolute',top:30,right:28,color:'#edf0e8',fontSize:20,backgroundColor:'#18282bdb',padding:'10px 16px'}}>外观未定稿</div>
    <div style={{position:'absolute',bottom:26,left:28,color:'#fff',fontSize:23,backgroundColor:'#18282be8',padding:'11px 17px'}}>{phase}</div>
    <div style={{position:'absolute',bottom:26,right:28,color:'#fff',fontSize:19,fontVariantNumeric:'tabular-nums',backgroundColor:'#18282be8',padding:'11px 17px'}}>{t.toFixed(2)} s / 5.00 s</div>
  </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="ContinuousRigStudy" component={Film} durationInFrames={150} fps={30} width={1280} height={720}/>;
