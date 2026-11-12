import {Audio} from '@remotion/media';
import {AbsoluteFill,staticFile,useVideoConfig} from 'remotion';import {SceneVideo} from './SceneVideo';import {Caption} from './Caption';
export const Haruko=()=>{const {fps}=useVideoConfig();return <AbsoluteFill><SceneVideo scene="haruko" art="02-haruko.png"/><Caption>先站稳，别着急。</Caption><Audio name="晴子：别着急" from={13} src={staticFile('audio/voices/haruko.wav')} premountFor={fps}/></AbsoluteFill>};
