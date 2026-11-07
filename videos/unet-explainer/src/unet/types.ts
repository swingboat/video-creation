import type {Caption} from '@remotion/captions';
export type SceneTiming = {startFrame: number; durationFrames: number; audioSrc: string; captions: Caption[]};
export type UnetTimeline = {fps: number; audioAvailable: boolean; voice: string; speechRate: number; durationFrames: number; scenes: SceneTiming[]};
