import {Audio} from '@remotion/media';
import {AbsoluteFill, CanvasImage, Easing, Interactive, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CoastalWorld} from './seaside/CoastalWorld';
import {Skater} from './seaside/Skater';

export const SeasideSkate = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;
  const x = interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [-230, 825, 1040, 1570], {
    easing: Easing.bezier(0.22, 0.6, 0.35, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const y = interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [993, 982, 967, 657], {
    easing: Easing.bezier(0.42, 0, 0.4, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const scale = interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [0.58, 0.78, 0.78, 0.13], {
    easing: Easing.bezier(0.4, 0, 0.3, 1), output: 'perceptual-scale', extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{backgroundColor: '#e6efde', overflow: 'hidden'}}>
      <CoastalWorld name="海岸水彩世界" durationInFrames={10 * fps} premountFor={fps} />
      <Interactive.Div name="贴地投影" premountFor={fps} style={{position: 'absolute', left: x - 173 * scale,
        top: y + 26 * scale, width: 390 * scale, height: 25 * scale, borderRadius: '50%',
        backgroundColor: '#636963', opacity: 0.22, filter: 'blur(8px)',
      }} />
      <Interactive.Div name="女孩滑入・侧面跟拍・滑向远方" premountFor={fps} style={{position: 'absolute',
        width: 800, height: 1000,
        left: interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [-630, 425, 640, 1170], {
          easing: Easing.bezier(0.22, 0.6, 0.35, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
        top: interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [136, 125, 110, -200], {
          easing: Easing.bezier(0.42, 0, 0.4, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
        transformOrigin: '400px 857px',
        scale: interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [0.58, 0.78, 0.78, 0.13], {
          easing: Easing.bezier(0.4, 0, 0.3, 1), output: 'perceptual-scale', extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
        rotate: `${Math.sin(time * 3.3) * 0.27}deg`,
      }}>
        <Skater name="女孩蹬地与平衡动作" durationInFrames={10 * fps} premountFor={fps}
          spriteSrc={staticFile('seaside/girl-poses.png')} motionStrength={1} />
      </Interactive.Div>
      <Interactive.Div name="近景野花视差" premountFor={fps} style={{position: 'absolute', width: 2800, height: 900,
        left: 0, top: 760, opacity: interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], [0.65, 0.9, 0.85, 0.65], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
        translate: interpolate(frame, [0, 2 * fps, 7 * fps, 10 * fps], ['-10px 0px', '-140px 0px', '-700px 0px', '-840px 18px'], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
        scale: `${1 + Math.sin(time * 1.7) * 0.004} 1`, filter: 'blur(1px)',
      }}>
        <CanvasImage name="手绘野花前景" src={staticFile('seaside/foreground-flowers.png')} premountFor={fps}
          style={{position: 'absolute', top: 0, left: 0, width: 2800, height: 933}} />
      </Interactive.Div>
      <AbsoluteFill style={{pointerEvents: 'none', background: 'linear-gradient(135deg, rgba(255,246,211,0.10), transparent 55%, rgba(109,148,118,0.045))'}} />
      <AbsoluteFill style={{pointerEvents: 'none', backgroundColor: '#fff8e9',
        opacity: interpolate(frame, [0, 0.55 * fps], [0.65, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
      }} />
      <Audio name="海浪" src={staticFile('seaside/surf.wav')} durationInFrames={10 * fps} premountFor={fps} volume={0.62} />
      <Audio name="轻柔海风" src={staticFile('seaside/wind.wav')} durationInFrames={10 * fps} premountFor={fps} volume={0.3} />
      <Audio name="滑板滚动与路面接缝" src={staticFile('seaside/skateboard.wav')} durationInFrames={10 * fps} premountFor={fps}
        volume={interpolate(frame, [0, 1.5 * fps, 7 * fps, 10 * fps], [0, 0.58, 0.58, 0.07], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        })} />
    </AbsoluteFill>
  );
};
