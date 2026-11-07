import {memo, useLayoutEffect, useMemo, useRef} from 'react';
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill, Interactive, useCurrentFrame, useVideoConfig} from 'remotion';
import {CanvasTexture, PCFShadowMap, SRGBColorSpace, type Group, type PerspectiveCamera} from 'three';
import {useMiSans} from '../fonts';
import {configSchema, useMerchant, type BuildingConfig, type ClinicProps, type MerchantConfig} from './config';
import {tween} from './motion';

const Box = ({position, size, color, glow = 0}: {position: [number, number, number]; size: [number, number, number]; color: string; glow?: number}) => (
  <mesh position={position} castShadow receiveShadow>
    <boxGeometry args={size} />
    <meshStandardMaterial color={color} roughness={0.78} emissive={color} emissiveIntensity={glow} />
  </mesh>
);

const Building = ({item}: {item: BuildingConfig}) => {
  const floors = Math.max(1, Math.floor(item.height / 0.85));
  return <group position={[item.position[0], 0, item.position[1]]}>
    <Box position={[0, item.height / 2, 0]} size={[item.width, item.height, item.depth]} color={item.color} />
    <Box position={[0, item.height + 0.08, 0]} size={[item.width + 0.08, 0.16, item.depth + 0.08]} color="#eef1eb" />
    {Array.from({length: floors}, (_, floor) => [0, 1].map((column) => <Box key={`${floor}-${column}`}
      position={[(column - 0.5) * item.width * 0.46, 0.5 + floor * 0.85, item.depth / 2 + 0.015]}
      size={[item.width * 0.23, 0.36, 0.045]} color="#91b2af" />))}
  </group>;
};

const StaticCity = memo(({config, rise}: {config: MerchantConfig; rise: number}) => <>
  <Box position={[0, -0.38, 0]} size={[19, 0.7, 17.8]} color="#dce6de" />
  <Box position={[0, -0.035, 0]} size={[18.7, 0.07, 17.5]} color="#edf2e9" />
  {Array.from({length: 19}, (_, i) => <group key={i}>
    <Box position={[i - 9, 0.015, 0]} size={[0.018, 0.016, 17.4]} color="#d5e1d8" />
    {i < 18 ? <Box position={[0, 0.015, i - 8.5]} size={[18.6, 0.016, 0.018]} color="#d5e1d8" /> : null}
  </group>)}
  <Box position={[0, 0.07, 3.7]} size={[18.6, 0.12, 2.3]} color="#b1c3bd" />
  <Box position={[0, 0.1, 2.42]} size={[18.6, 0.14, 0.24]} color="#fffdf4" />
  <Box position={[0, 0.1, 4.98]} size={[18.6, 0.14, 0.24]} color="#fffdf4" />
  {Array.from({length: 14}, (_, i) => <Box key={i} position={[-8.7 + i * 1.35, 0.139, 3.7]} size={[0.65, 0.018, 0.07]} color="#faf9ee" />)}
  <Box position={[-0.75, 0.08, -3.6]} size={[1.1, 0.12, 10.2]} color="#c6d4cd" />
  <group scale={[1, rise, 1]}>{config.buildings.map((item) => <Building key={item.id} item={item} />)}</group>
  {[-8, -4.9, -1.4, 5, 8].map((x, i) => <group key={x} position={[x, 0, i % 2 ? 1.4 : -3.2]}>
    <Box position={[0, 0.35, 0]} size={[0.13, 0.7, 0.13]} color="#a89577" />
    <mesh position={[0, 1.02, 0]} castShadow><sphereGeometry args={[0.61, 8, 6]} /><meshStandardMaterial color="#86b79a" roughness={1} /></mesh>
  </group>)}
</>);

const CameraRig = ({config, time}: {config: MerchantConfig; time: number}) => {
  const {camera} = useThree();
  const sx = config.store.position[0];
  const sz = config.store.position[1];
  useLayoutEffect(() => {
    const aerial = tween(time, 0, 5);
    const approach = tween(time, 14, 21.5);
    const final = tween(time, 22, 24);
    const drift = tween(time, 5, 14);
    const wide = [tween(aerial, 0, 1, 0, 18) - drift, tween(aerial, 0, 1, 36, 20) - drift * 2,
      tween(aerial, 0, 1, 5, 23) - drift * 1.5];
    camera.position.set(wide[0] * (1 - approach) + (sx + 7.8 - final) * approach,
      wide[1] * (1 - approach) + (10.3 - final * 0.7) * approach,
      wide[2] * (1 - approach) + (sz + 12 - final * 0.5) * approach);
    camera.lookAt(sx * approach, 0.8 + approach * 1.6 + final * 0.5, sz * approach);
    (camera as PerspectiveCamera).fov = 43;
    camera.updateProjectionMatrix();
  }, [camera, sx, sz, time]);
  return null;
};

const Store = ({config, time}: {config: MerchantConfig; time: number}) => {
  const {width: w, height: h, depth: d, position} = config.store;
  const glow = tween(time, 14, 16) * (0.22 + Math.sin(time * 2.4) * 0.06);
  const texture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 1024; canvas.height = 192;
    const ctx = canvas.getContext('2d')!;
    ctx.fillStyle = config.theme.brand; ctx.fillRect(0, 0, 1024, 192);
    ctx.fillStyle = '#ffffff'; ctx.font = '700 108px MiSans'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(config.name, 512, 96, 950);
    const result = new CanvasTexture(canvas); result.colorSpace = SRGBColorSpace;
    return result;
  }, [config.name, config.theme.brand]);
  useLayoutEffect(() => () => texture.dispose(), [texture]);
  return <group position={[position[0], 0, position[1]]}>
    <Box position={[0, h / 2, 0]} size={[w, h, d]} color="#fffdf6" glow={glow} />
    <Box position={[0, h + 0.1, 0]} size={[w + 0.25, 0.2, d + 0.25]} color={config.theme.brand} glow={glow * 3} />
    <Box position={[0, 0.15, d / 2 + 0.35]} size={[w + 0.5, 0.25, 0.85]} color="#ffffff" />
    <Box position={[0, h - 0.46, d / 2 + 0.06]} size={[w + 0.04, 0.61, 0.15]} color={config.theme.brand} glow={glow} />
    <mesh position={[0, h - 0.46, d / 2 + 0.142]}>
      <planeGeometry args={[w - 0.2, 0.54]} /><meshBasicMaterial map={texture} />
    </mesh>
    <Box position={[-w * 0.28, 1.05, d / 2 + 0.025]} size={[w * 0.28, 1.4, 0.07]} color="#a3d4d2" />
    <Box position={[w * 0.28, 1.05, d / 2 + 0.025]} size={[w * 0.28, 1.4, 0.07]} color="#a3d4d2" />
    <Box position={[0, 0.94, d / 2 + 0.05]} size={[w * 0.24, 1.64, 0.09]} color="#6dafb0" />
    <Box position={[0, 0.94, d / 2 + 0.11]} size={[0.045, 1.64, 0.035]} color="#ffffff" />
    <Box position={[0.17, 0.92, d / 2 + 0.13]} size={[0.04, 0.24, 0.03]} color="#ffffff" />
    <Box position={[w / 2 + 0.02, 1.3, 0]} size={[0.035, 1.4, d * 0.55]} color="#acd3d0" />
    <mesh position={[0, 0.17, 0]} scale={[w * 0.78, 0.04, d * 0.85]}>
      <sphereGeometry args={[1, 32, 16]} /><meshBasicMaterial color={config.theme.brand} transparent opacity={tween(time, 14, 16, 0, 0.22)} depthWrite={false} />
    </mesh>
  </group>;
};

const LocationPin = ({config, time}: {config: MerchantConfig; time: number}) => {
  const {camera} = useThree();
  const pin = useRef<Group>(null);
  const appear = tween(time, 5, 5.8);
  const bob = Math.sin(time * 2) * 0.08;
  const pulse = (time * 0.6) % 1;
  useLayoutEffect(() => {pin.current?.quaternion.copy(camera.quaternion);}, [camera, time]);
  return <group position={[config.store.position[0], config.store.height + 1.9 + bob, config.store.position[1]]} scale={appear}>
    <mesh castShadow><sphereGeometry args={[0.62, 24, 16]} /><meshStandardMaterial color={config.theme.marker} roughness={0.4} /></mesh>
    <group ref={pin}>
      <group position={[0, 0, 0.625]}><mesh><sphereGeometry args={[0.22, 16, 12]} /><meshBasicMaterial color="#fff8f3" /></mesh></group>
    </group>
    <Box position={[0, -0.72, 0]} size={[0.11, 0.75, 0.11]} color={config.theme.marker} />
    <mesh position={[0, -config.store.height - 1.72 - bob, 0]} scale={[1.25 + pulse * 0.7, 0.025, 1.25 + pulse * 0.7]}>
      <sphereGeometry args={[1, 32, 16]} /><meshBasicMaterial color={config.theme.marker} transparent opacity={(1 - pulse) * 0.15} depthWrite={false} />
    </mesh>
  </group>;
};

const CitySceneInner = ({configSrc, style}: ClinicProps) => {
  const config = useMerchant(configSrc);
  const fontsReady = useMiSans();
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  const time = frame / fps;
  if (!config || !fontsReady) return null;
  return <AbsoluteFill style={{top: 325, height: 1190, maskImage: 'linear-gradient(to bottom, #000 0%, #000 84%, transparent 100%)', ...style}}>
    <ThreeCanvas width={width} height={1190} camera={{position: [18, 20, 23], fov: 43}} shadows={{type: PCFShadowMap}}
      gl={{antialias: true, alpha: true, preserveDrawingBuffer: true}} dpr={1}>
      <ambientLight intensity={1.6} />
      <hemisphereLight args={['#ffffff', '#adc9bc', 1.4]} />
      <directionalLight position={[-12, 24, 14]} intensity={2.6} castShadow shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-18} shadow-camera-right={18} shadow-camera-top={18} shadow-camera-bottom={-18}
        shadow-camera-far={80} shadow-bias={-0.0005} />
      <CameraRig config={config} time={time} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.77, 0]} receiveShadow>
        <planeGeometry args={[150, 150]} /><shadowMaterial transparent opacity={0.13} />
      </mesh>
      <StaticCity config={config} rise={tween(time, 0.6, 3, 0.05, 1)} />
      <Store config={config} time={time} />
      <LocationPin config={config} time={time} />
    </ThreeCanvas>
  </AbsoluteFill>;
};

export const CityScene = Interactive.withSchema({Component: CitySceneInner, componentName: '<CityScene>', wrapInSequence: true, schema: configSchema});
