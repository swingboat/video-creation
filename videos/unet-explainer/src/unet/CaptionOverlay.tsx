import type {Caption} from '@remotion/captions';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {palette, typography} from './settings';
export const CaptionOverlay = ({captions}: {captions: Caption[]}) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const now = frame / fps * 1000;
  const current = captions.find((caption) => now >= caption.startMs && now < caption.endMs);
  if (!current) return null;
  return <div data-unet-caption style={{position: 'absolute', left: 140, right: 140, bottom: 44, height: 106,
    display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: palette.ink,
    fontSize: typography.caption, lineHeight: 1.27, whiteSpace: 'pre-line', fontWeight: 400}}>{current.text}</div>;
};
