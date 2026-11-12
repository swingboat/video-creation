import {Audio} from '@remotion/media';
import {AbsoluteFill,interpolate,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {SceneVideo} from './SceneVideo';import {Caption} from './Caption';import {fontFamily} from './fonts';
export const Opening=()=>{const frame=useCurrentFrame();const {fps}=useVideoConfig();return <AbsoluteFill><SceneVideo scene="opening" art="01-two-shot.png"/><div style={{position:'absolute',top:42,left:56,fontFamily,fontSize:30,color:'#fff9e9',textShadow:'0 2px 5px #34281f',opacity:interpolate(frame,[0,.25*fps,1.7*fps,2*fps],[0,1,1,0],{extrapolateRight:'clamp'})}}>放学后的练习</div><Caption start={.6} end={3.8}>樱木同学，再试一次吧。</Caption><Audio name="晴子：再试一次" from={14} src={staticFile('audio/voices/opening.wav')} premountFor={fps}/></AbsoluteFill>};
