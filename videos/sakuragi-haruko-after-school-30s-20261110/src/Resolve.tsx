import {Audio} from '@remotion/media';
import {AbsoluteFill,staticFile,useVideoConfig} from 'remotion';import {SceneVideo} from './SceneVideo';import {Caption} from './Caption';
export const Resolve=()=>{const {fps}=useVideoConfig();return <AbsoluteFill><SceneVideo scene="resolve" art="07-resolve.png"/><Caption start={.65} end={3.7}>我可是天才嘛。</Caption><Audio name="樱木：天才" from={16} src={staticFile('audio/voices/resolve.wav')} premountFor={fps}/></AbsoluteFill>};
