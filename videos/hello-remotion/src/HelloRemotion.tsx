import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

export const HelloRemotion = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const progress = frame / (durationInFrames - 1);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#111827',
        color: '#f9fafb',
        fontFamily: 'Arial, sans-serif',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div style={{opacity, fontSize: 76, fontWeight: 700}}>Hello, Remotion!</div>
      <div style={{opacity, marginTop: 24, fontSize: 30, color: '#93c5fd'}}>
        Project-local video rendering is ready.
      </div>
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          height: 12,
          width: `${progress * 100}%`,
          backgroundColor: '#60a5fa',
        }}
      />
    </AbsoluteFill>
  );
};
