import {useEffect, useLayoutEffect, useRef, useState, type CSSProperties} from 'react';
import {AbsoluteFill, Interactive, cancelRender, continueRender, delayRender, useCurrentFrame, useVideoConfig} from 'remotion';

type SkaterProps = {readonly spriteSrc: string; readonly motionStrength: number; readonly style?: CSSProperties};

const SkaterInner = ({spriteSrc, motionStrength, style}: SkaterProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [handle] = useState(() => delayRender('Loading watercolor girl sprite'));
  useEffect(() => {
    const img = new Image();
    let mounted = true;
    img.onload = () => { if (mounted) setImage(img); };
    img.onerror = () => cancelRender(new Error(`Unable to load character asset: ${spriteSrc}`));
    img.src = spriteSrc;
    return () => { mounted = false; continueRender(handle); };
  }, [spriteSrc, handle]);
  useEffect(() => { if (image) continueRender(handle); }, [image, handle]);

  useLayoutEffect(() => {
    const context = canvasRef.current?.getContext('2d');
    if (!context || !image) return;
    context.clearRect(0, 0, 800, 1000);
    const pose = time < 3.3 ? 0 : time < 4.8 ? 1 : 2;
    const source = [{left: 0, width: 557, anchor: 435}, {left: 567, width: 456, anchor: 819}, {left: 1024, width: 512, anchor: 1324}][pose];
    const offset = 400 - source.anchor;
    // Small scanline deformations give the painted hair and dress a breeze.
    for (let y = 0; y < 1024; y += 8) {
      const dress = y >= 440 && y <= 640;
      const hair = y >= 130 && y <= 300;
      const sway = dress ? Math.sin(time * 6.8 + y * 0.025) * ((y - 430) / 210) * 4.5
        : hair ? Math.sin(time * 4.3 + y * 0.035) * 1.7 : 0;
      const rowHeight = Math.min(8, 1024 - y);
      if (pose === 0 && y >= 632) {
        // Deform the trailing leg as one continuous image, without cutting it
        // into overlapping pieces. The planted front shoe stays fixed.
        const amount = Math.min(1, (y - 632) / 224);
        const kick = Math.sin(time * 6.1);
        context.drawImage(image, 0, y, 360, rowHeight,
          offset + amount * kick * 9 * motionStrength, y + amount * (30 + kick * 5), 360, rowHeight * 1.18);
        context.drawImage(image, 360, y, source.width - 360, rowHeight,
          360 + offset, y, source.width - 360, rowHeight);
      } else {
        context.drawImage(image, source.left, y, source.width, rowHeight,
          source.left + offset + sway * motionStrength, y, source.width, rowHeight);
      }
    }
  }, [frame, fps, time, image, motionStrength]);

  return (
    <AbsoluteFill style={{width: 800, height: 1000, ...style}}>
      <canvas ref={canvasRef} width={800} height={1000} style={{position: 'absolute', width: 800, height: 1000}} />
      <svg width="800" height="1000" viewBox="0 0 800 1000" style={{position: 'absolute'}}>
        <defs>
          <linearGradient id="skate-deck" x1="0" y1="0" x2="0" y2="1">
            <stop stopColor="#b78657" /><stop offset="1" stopColor="#795542" />
          </linearGradient>
          <filter id="skate-painted"><feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="2" />
            <feComposite in="SourceGraphic" operator="in" /><feBlend in="SourceGraphic" mode="multiply" /></filter>
        </defs>
        <path d="M 257 858 Q 263 865 285 866 L 555 866 Q 572 863 582 854 L 576 866 Q 566 874 548 875 L 282 875 Q 265 874 256 866 Z"
          fill="url(#skate-deck)" stroke="#6b5546" strokeWidth="2.6" />
        <path d="M 263 858 Q 288 862 555 861 L 579 853" stroke="#d5af7c" strokeWidth="3" fill="none" />
        <path d="M 306 875 L 306 884 L 337 884 M 503 875 L 503 884 L 531 884" stroke="#778382" strokeWidth="7" fill="none" />
        {[320, 518].map((x) => (
          <g key={x} style={{transformOrigin: `${x}px 893px`, rotate: `${time * 1500}deg`}}>
            <circle cx={x} cy="893" r="15" fill="#bf7d51" stroke="#6e5846" strokeWidth="2.5" />
            <circle cx={x} cy="893" r="6" fill="#e4c79b" />
            <path d={`M ${x - 9} 893 L ${x + 9} 893 M ${x} 884 L ${x} 902`} stroke="#92643e" strokeWidth="2" />
          </g>
        ))}
      </svg>
    </AbsoluteFill>
  );
};

export const Skater = Interactive.withSchema({
  Component: SkaterInner, componentName: '<Skater>', wrapInSequence: true,
  schema: {
    spriteSrc: {type: 'asset', assetType: 'image', default: '', description: '女孩手绘姿态素材'},
    motionStrength: {type: 'number', default: 1, min: 0, max: 2, step: 0.1, hiddenFromList: false, description: '海风摆动幅度'},
  },
});
