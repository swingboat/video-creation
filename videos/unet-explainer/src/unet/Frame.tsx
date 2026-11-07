import {type CSSProperties, type ReactNode} from 'react';
import {AbsoluteFill, staticFile, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {useMiSans} from '../fonts';
import {palette, sceneTitles, typography} from './settings';
import {timeline} from './timeline.generated';
import {CaptionOverlay} from './CaptionOverlay';
export type SceneProps = {still?: boolean; sceneFrames?: number; style?: CSSProperties};
export const Frame = ({scene, children, style}: {scene: number; children: ReactNode; style?: CSSProperties}) => {
  const ready = useMiSans(); const {fps, id} = useVideoConfig(); if (!ready) return null;
  const withNarration = timeline.audioAvailable && id !== 'UnetStoryboard' && id !== 'UnetSkipSample';
  return <AbsoluteFill style={{backgroundColor: palette.background, color: palette.ink, fontFamily: 'MiSans, sans-serif', overflow: 'hidden', ...style}}>
    <div style={{position: 'absolute', left: 100, top: 60, fontSize: 26, letterSpacing: 3, color: palette.muted}}>U-NET / 图像分割</div>
    <div style={{position: 'absolute', right: 100, top: 60, fontSize: 26, color: palette.muted}}>0{scene + 1} / 07</div>
    <div style={{position: 'absolute', left: 100, top: 111, fontSize: typography.title, fontWeight: 700, letterSpacing: -1}}>{sceneTitles[scene]}</div>
    {children}
    <div style={{position: 'absolute', left: 100, bottom: 183, fontSize: typography.note, color: palette.muted}}>教学简化示意：采用同尺寸填充</div>
    <div style={{position: 'absolute', right: 100, bottom: 183, fontSize: typography.note, color: palette.muted}}>图形与纹理均为合成教学素材</div>
    <div style={{position: 'absolute', left: 100, right: 100, bottom: 165, height: 2, background: '#E2E8F0'}} />
    {withNarration ? <>
      <Audio name="本镜头普通话旁白" src={staticFile(timeline.scenes[scene].audioSrc)} premountFor={fps} />
      <CaptionOverlay captions={timeline.scenes[scene].captions} />
    </> : null}
  </AbsoluteFill>;
};
