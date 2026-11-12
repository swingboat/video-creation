import {Audio} from '@remotion/media';
import {AbsoluteFill,staticFile,useVideoConfig} from 'remotion';import {SceneVideo} from './SceneVideo';import {Caption} from './Caption';
export const Cheer=()=>{const {fps}=useVideoConfig();return <AbsoluteFill><SceneVideo scene="cheer" art="06-cheer.png"/><Caption start={.4} end={3.25}>对，就是这样！</Caption><Audio name="晴子：就是这样" from={10} src={staticFile('audio/voices/cheer.wav')} premountFor={fps}/></AbsoluteFill>};
