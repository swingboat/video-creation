import {Audio,Video} from '@remotion/media';
import {loadFont} from '@remotion/fonts';
import {AbsoluteFill,Composition,Folder,Img,Sequence,Series,staticFile,useCurrentFrame} from 'remotion';
import raw from '../production.json';

type Dialogue={file:string|null;text:string;fromFrame:number;sync:'on-screen'|'voiceover'};
type ShotSpec={id:string;frames:number;art:string|null;clip:string|null;caption:{text:string;startFrame:number;endFrame:number}|null;dialogue:Dialogue|null};
type Production={title:string;format:{width:number;height:number;fps:number;durationFrames:number};fontFile:string|null;background:{file:string;volume:number}|null;sfx:{file:string;frame:number;volume:number}[];shots:ShotSpec[]};
const data=raw as unknown as Production;
if(data.fontFile)loadFont({family:'ProductionFont',url:staticFile(data.fontFile)});
const fontFamily=data.fontFile?'ProductionFont':'sans-serif';

const Shot=({shot}:{shot:ShotSpec})=>{
  const frame=useCurrentFrame();
  const caption=shot.caption&&frame>=shot.caption.startFrame&&frame<shot.caption.endFrame?shot.caption.text:null;
  return <AbsoluteFill style={{background:'#171b22',fontFamily}}>
    {shot.clip?<Video src={staticFile(shot.clip)} volume={0} style={{width:'100%',height:'100%'}} objectFit="cover"/>:
      shot.art?<Img src={staticFile(shot.art)} style={{width:'100%',height:'100%',objectFit:'contain'}}/>:null}
    {!shot.clip?<div style={{position:'absolute',left:28,top:24,color:'white',background:'#111c',padding:12,fontSize:24}}>Source footage pending · {shot.id}</div>:null}
    {caption?<div style={{position:'absolute',bottom:38,left:36,right:36,textAlign:'center',fontSize:Math.round(data.format.width/42),fontWeight:600,color:'white',textShadow:'0 2px 5px #000, 0 0 2px #000',lineHeight:1.4,whiteSpace:'pre-wrap'}}>{caption}</div>:null}
    {shot.dialogue?.file?<Sequence from={shot.dialogue.fromFrame} layout="none"><Audio src={staticFile(shot.dialogue.file)}/></Sequence>:null}
  </AbsoluteFill>;
};
const Episode=()=> <AbsoluteFill style={{background:'#171b22'}}>
  <Series>{data.shots.map(shot=><Series.Sequence key={shot.id} durationInFrames={shot.frames} premountFor={data.format.fps}><Shot shot={shot}/></Series.Sequence>)}</Series>
  {data.background?<Audio src={staticFile(data.background.file)} volume={data.background.volume}/>:null}
  {data.sfx.map((s,i)=><Sequence key={i} from={s.frame} layout="none"><Audio src={staticFile(s.file)} volume={s.volume}/></Sequence>)}
</AbsoluteFill>;
export const RemotionRoot=()=> <>
  <Composition id="Episode" component={Episode} width={data.format.width} height={data.format.height} fps={data.format.fps} durationInFrames={data.format.durationFrames}/>
  <Folder name="Scenes">{data.shots.map(shot=><Composition key={shot.id} id={shot.id} component={Shot} defaultProps={{shot}} width={data.format.width} height={data.format.height} fps={data.format.fps} durationInFrames={shot.frames}/>)}</Folder>
</>;
