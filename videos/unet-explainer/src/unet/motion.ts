import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
export const move = (p: number, a: number, b: number, x = 0, y = 1) => interpolate(p, [a, b], [x, y], {easing: Easing.bezier(0.3, 0, 0.2, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
export const useSceneProgress = (still = false, sceneFrames?: number) => {
  const frame = useCurrentFrame(); const {durationInFrames} = useVideoConfig();
  return still ? 0.83 : Math.max(0, Math.min(1, frame / Math.max(1, (sceneFrames ?? durationInFrames) - 1)));
};
