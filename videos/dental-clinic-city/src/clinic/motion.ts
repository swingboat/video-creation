import {Easing, interpolate} from 'remotion';

export const tween = (time: number, start: number, end: number, a = 0, b = 1) => interpolate(time, [start, end], [a, b], {
  easing: Easing.bezier(0.32, 0, 0.18, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
});
export const fade = (time: number, duration: number) => tween(time, 0, 0.55) * tween(time, duration - 0.45, duration, 1, 0);
