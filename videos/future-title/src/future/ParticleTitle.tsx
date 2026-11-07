import {useLayoutEffect, useMemo, useRef, type CSSProperties} from 'react';
import {AbsoluteFill, Easing, Interactive, interpolate, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {useMiSans} from './fonts';

type TitleProps = {readonly title: string; readonly subtitle: string; readonly style?: CSSProperties};
type Particle = {x: number; y: number; startX: number; startY: number; delay: number; size: number; phase: number; alpha: number; tint: string};

const createParticles = (title: string): {particles: Particle[]; fontSize: number; spacing: number} => {
  const canvas = document.createElement('canvas');
  canvas.width = 1920;
  canvas.height = 1080;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Canvas 2D is required for particle typography');
  const characters = Array.from(title);
  const fontSize = Math.min(174, 1500 / Math.max(characters.length, 1));
  const spacing = 12;
  context.font = `700 ${fontSize}px MiSans`;
  context.textBaseline = 'middle';
  context.fillStyle = '#fff';
  const textWidth = characters.reduce((width, character) => width + context.measureText(character).width, 0)
    + Math.max(0, characters.length - 1) * spacing;
  let x = (1920 - textWidth) / 2;
  for (const character of characters) {
    context.fillText(character, x, 480);
    x += context.measureText(character).width + spacing;
  }
  const pixels = context.getImageData(0, 0, 1920, 1080).data;
  const particles: Particle[] = [];
  for (let y = 360; y < 600; y += 5) {
    for (let targetX = 120; targetX < 1800; targetX += 5) {
      if (pixels[(y * 1920 + targetX) * 4 + 3] < 150) continue;
      const i = particles.length;
      const angle = random(`angle-${i}`) * Math.PI * 2;
      const radius = 530 + random(`radius-${i}`) * 850;
      particles.push({
        x: targetX,
        y,
        startX: 960 + Math.cos(angle) * radius,
        startY: 480 + Math.sin(angle) * radius * 0.6,
        delay: random(`delay-${i}`) * 0.62,
        size: 1.25 + random(`size-${i}`) * 1.3,
        phase: random(`phase-${i}`) * Math.PI * 2,
        alpha: 0.45 + random(`particle-alpha-${i}`) * 0.55,
        tint: i % 5 === 0 ? '#e8edff' : targetX < 960 ? '#68caff' : '#ae8bff',
      });
    }
  }
  return {particles, fontSize, spacing};
};

const ParticleTitleInner = ({title, subtitle, style}: TitleProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fontsReady = useMiSans();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const {particles, fontSize, spacing} = useMemo(() => fontsReady ? createParticles(title)
    : {particles: [], fontSize: 174, spacing: 12}, [title, fontsReady]);
  const dissolve = interpolate(frame, [6.3 * fps, 7.35 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const particleOpacity = interpolate(frame, [0, 0.35 * fps, 2.85 * fps, 3.4 * fps, 6.15 * fps, 6.5 * fps, 7.35 * fps],
    [0, 1, 1, 0, 0, 0.85, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  // A single canvas avoids updating thousands of DOM nodes during Studio playback.
  useLayoutEffect(() => {
    const context = canvasRef.current?.getContext('2d');
    if (!context) return;
    context.clearRect(0, 0, 1920, 1080);
    if (particleOpacity === 0) return;
    for (const particle of particles) {
      const progress = interpolate(frame, [(0.35 + particle.delay) * fps, (2.65 + particle.delay * 0.3) * fps], [0, 1], {
        easing: Easing.bezier(0.18, 0.75, 0.18, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      });
      const swirl = Math.sin(progress * Math.PI) * 85;
      const x = particle.startX + (particle.x - particle.startX) * progress + Math.sin(particle.phase + progress * 4) * swirl
        + dissolve * (particle.startX - particle.x) * 0.32;
      const y = particle.startY + (particle.y - particle.startY) * progress + Math.cos(particle.phase + progress * 4) * swirl
        + dissolve * (particle.startY - particle.y) * 0.32;
      context.globalAlpha = particleOpacity * particle.alpha;
      context.fillStyle = particle.tint;
      context.beginPath();
      context.arc(x, y, particle.size, 0, Math.PI * 2);
      context.fill();
    }
  }, [frame, fps, particles, particleOpacity, dissolve]);

  return (
    <AbsoluteFill style={{fontFamily: 'MiSans', ...style}}>
      <canvas ref={canvasRef} width={1920} height={1080} style={{position: 'absolute', width: '100%', height: '100%'}} />
      <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <defs>
          <linearGradient id="future-title-gradient" x1="0" x2="1">
            <stop stopColor="#b7e8ff" />
            <stop offset="0.4" stopColor="#d7e4ff" />
            <stop offset="1" stopColor="#c7a5ff" />
          </linearGradient>
          <linearGradient id="future-rule-gradient">
            <stop stopColor="#44bfff" stopOpacity="0" />
            <stop offset="0.5" stopColor="#8e94ff" />
            <stop offset="1" stopColor="#a475ff" stopOpacity="0" />
          </linearGradient>
          <filter id="future-title-glow" x="-20%" y="-40%" width="140%" height="180%">
            <feGaussianBlur stdDeviation="9" />
          </filter>
        </defs>
        <g opacity={interpolate(frame, [2.7 * fps, 3.3 * fps, 6.15 * fps, 6.6 * fps], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        })}>
          <text x="960" y="480" textAnchor="middle" dominantBaseline="central"
            fontFamily="MiSans" fontWeight="700" fontSize={fontSize} letterSpacing={spacing}
            fill="#7798ff" opacity="0.25" filter="url(#future-title-glow)">{title}</text>
          <text x="960" y="480" textAnchor="middle" dominantBaseline="central"
            fontFamily="MiSans" fontWeight="700" fontSize={fontSize} letterSpacing={spacing}
            fill="url(#future-title-gradient)">{title}</text>
        </g>
        <path d="M 710 594 L 1210 594" stroke="url(#future-rule-gradient)" strokeWidth="1.3"
          opacity={interpolate(frame, [2.7 * fps, 3.8 * fps, 6 * fps, 6.6 * fps], [0, 1, 1, 0], {
            extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          })} />
      </svg>
      <Interactive.Div name="中文副标题" premountFor={fps} style={{
        position: 'absolute', top: 625, width: '100%', textAlign: 'center', color: '#a6b6d9',
        fontSize: 40, letterSpacing: 12, fontWeight: 400,
        opacity: interpolate(frame, [3.1 * fps, 4.1 * fps, 6.1 * fps, 6.6 * fps], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
        translate: interpolate(frame, [3.1 * fps, 4.1 * fps], ['0px 18px', '0px 0px'], {
          easing: Easing.bezier(0.16, 1, 0.3, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        }),
      }}>{subtitle}</Interactive.Div>
    </AbsoluteFill>
  );
};

export const ParticleTitle = Interactive.withSchema({
  Component: ParticleTitleInner,
  componentName: '<ParticleTitle>',
  schema: {
    title: {type: 'text-content', default: '未来，正在发生', description: '中文主标题'},
    subtitle: {type: 'text-content', default: '向下一刻，出发', description: '中文副标题'},
  },
  wrapInSequence: true,
});
