/** Models/textures: David Heckhoff, https://david-hckh.com
 * Source: https://github.com/davidhckh/portfolio-2025
 * Personal/educational use only; license in docs/research/original-license.md.
 * Frame-driven scenes and hologram shader authored for this study. */
import { useMemo, useLayoutEffect, useEffect } from "react";
import { useLoader, useThree } from "@react-three/fiber";
import { ThreeCanvas } from "@remotion/three";
import { staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import * as T from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { clone } from "three/examples/jsm/utils/SkeletonUtils.js";
import { gsap } from "gsap";
type Mode = "office" | "hologram" | "contact";
const texturePaths = [
  "room.webp",
  "contact.webp",
  "head.webp",
  "face-spritesheet.png",
  "matcap-black.webp",
  "matcap-gray.webp",
  "matcap-skin.webp",
  "matcap-white.webp",
  "desktops.webp",
  "room-shadow.webp",
  "contact-shadow.webp",
];
const vertex = `varying vec2 vUv; varying vec3 vNormal; varying vec3 vWorld;
#include <common>
#include <skinning_pars_vertex>
void main(){vUv=uv;
#include <beginnormal_vertex>
#include <skinbase_vertex>
#include <skinnormal_vertex>
#include <defaultnormal_vertex>
vNormal=normalize(transformedNormal);
#include <begin_vertex>
#include <skinning_vertex>
vec4 world=modelMatrix*vec4(transformed,1.);vWorld=world.xyz;gl_Position=projectionMatrix*viewMatrix*world;}`;
const shadowVertex = `varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`;
const shadowFragment = `uniform sampler2D uTexture;varying vec2 vUv;void main(){vec4 s=texture2D(uTexture,vUv);gl_FragColor=vec4(.42,.32,.20,(1.-s.r)*s.a*.28);}`;
const fragment = `uniform float uTime;uniform float uAmount;varying vec2 vUv;varying vec3 vNormal;varying vec3 vWorld;
void main(){float scan=pow(.5+.5*sin(vWorld.y*105.-uTime*8.),5.);float band=exp(-pow((vWorld.y-mod(uTime*.9,4.6))*7.,2.));float rim=pow(1.-abs(normalize(vNormal).z),2.2);float alpha=(.13+rim*.63+scan*.12+band*.3)*uAmount;vec3 cyan=mix(vec3(.015,.38,.7),vec3(.25,.95,1.),rim+band*.45);gl_FragColor=vec4(cyan,alpha);}`;
function Scene({ mode }: { mode: Mode }) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = f / fps;
  const { camera } = useThree();
  const [room, avatar, contact] = useLoader(
    GLTFLoader,
    ["room.glb", "avatar.glb", "contact.glb"].map((x) =>
      staticFile("upstream/models/" + x),
    ),
  );
  const textures = useLoader(
    T.TextureLoader,
    texturePaths.map((x) => staticFile("upstream/textures/" + x)),
  );
  const data = useMemo(() => {
    const tx = textures.map((x, i) => {
      const t = x.clone();
      t.flipY = i === 3;
      t.colorSpace = T.SRGBColorSpace;
      t.needsUpdate = true;
      return t;
    });
    tx[3].repeat.set(0.25, 0.25);
    const roomClone = room.scene.clone(true),
      contactClone = contact.scene.clone(true),
      actor = clone(avatar.scene.children[0]);
    actor.rotation.z = 0;
    const roomMat = new T.MeshBasicMaterial({ map: tx[0] }),
      screenMat = new T.MeshBasicMaterial({ map: tx[8] });
    roomClone.traverse((o) => {
      if (o instanceof T.Mesh) {
        o.material = o.name.startsWith("desktop-plane") ? screenMat : roomMat;
        if (o.name === "shadow-catcher") {
          o.material = new T.ShaderMaterial({
            vertexShader: shadowVertex,
            fragmentShader: shadowFragment,
            uniforms: { uTexture: { value: tx[9] } },
            transparent: true,
            depthWrite: false,
          });
          o.renderOrder = -10;
        }
        o.frustumCulled = false;
      }
    });
    contactClone.traverse((o) => {
      if (o instanceof T.Mesh) {
        o.material = new T.MeshBasicMaterial({ map: tx[1] });
        if (o.name === "shadow-catcher") {
          o.material = new T.ShaderMaterial({
            vertexShader: shadowVertex,
            fragmentShader: shadowFragment,
            uniforms: { uTexture: { value: tx[10] } },
            transparent: true,
            depthWrite: false,
          });
          o.renderOrder = -10;
        }
      }
    });
    const faceMat = new T.MeshBasicMaterial({
      map: tx[3],
      transparent: true,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -2,
    });
    const holo = new T.ShaderMaterial({
      vertexShader: vertex,
      fragmentShader: fragment,
      uniforms: { uTime: { value: 0 }, uAmount: { value: 1 } },
      transparent: true,
      depthWrite: false,
      side: T.DoubleSide,
      blending: T.AdditiveBlending,
    });
    actor.traverse((o) => {
      if (o instanceof T.Mesh) {
        o.frustumCulled = false;
        if (mode === "hologram") {
          o.material = o.name === "face" ? faceMat : holo;
          o.renderOrder = o.name === "face" ? 10 : 0;
        } else if (o.name === "head")
          o.material = new T.MeshBasicMaterial({ map: tx[2] });
        else if (o.name === "face") {
          o.material = faceMat;
          o.renderOrder = 10;
        } else {
          const idx =
            (
              { black: 4, gray: 5, skin: 6, white: 7 } as Record<string, number>
            )[o.name] ?? 4;
          o.material = new T.MeshMatcapMaterial({ matcap: tx[idx] });
        }
      }
    });
    const mixer = new T.AnimationMixer(actor);
    const actions = Object.fromEntries(
      avatar.animations.map((c) => {
        const a = mixer.clipAction(c);
        a.play();
        a.setEffectiveWeight(0);
        return [c.name, a];
      }),
    );
    const motion = { x: 0, y: 0, z: 0, turn: 0 };
    const timeline = gsap.timeline({ paused: true });
    if (mode === "office")
      timeline.fromTo(
        motion,
        { x: 0.25, turn: -0.08 },
        { x: 0, turn: 0.08, duration: 6, ease: "sine.inOut" },
      );
    if (mode === "hologram")
      timeline.fromTo(
        motion,
        { turn: -0.28, y: -0.18 },
        { turn: 0.3, y: 0, duration: 6, ease: "sine.inOut" },
      );
    if (mode === "contact")
      timeline.fromTo(
        motion,
        { x: 0.1, turn: -0.08 },
        { x: 0, turn: 0.04, duration: 6, ease: "sine.inOut" },
      );
    return {
      tx,
      roomClone,
      contactClone,
      actor,
      mixer,
      actions,
      holo,
      motion,
      timeline,
    };
  }, [room, avatar, contact, textures, mode]);
  // Seek before JSX transforms are read, including direct out-of-order frame jumps.
  data.timeline.seek(sec, true);
  useEffect(
    () => () => {
      data.timeline.kill();
    },
    [data],
  );
  useLayoutEffect(() => {
    for (const a of Object.values(data.actions)) {
      a.enabled = true;
      a.setEffectiveWeight(0);
      a.time = 0;
    }
    let pose = "idle",
      time = sec;
    if (mode === "office") {
      pose = sec < 2.7 ? "wave" : "idle";
      time = sec < 2.7 ? Math.min(sec, 2.65) : sec - 2.7;
    }
    if (mode === "hologram") pose = "t-idle";
    if (mode === "contact") {
      pose = sec < 0.75 ? "sleeping" : sec < 1.58 ? "wake-up" : "contact-idle";
      time = sec < 0.75 ? sec : sec < 1.58 ? sec - 0.75 : sec - 1.58;
    }
    const action = data.actions[pose];
    action.setEffectiveWeight(1);
    action.time = time % action.getClip().duration;
    if (mode === "office") {
      const w = 1 - Math.max(0, Math.min(1, (sec - 2.3) / 0.4));
      data.actions.wave.setEffectiveWeight(w);
      data.actions.wave.time = Math.min(sec, 2.7);
      data.actions.idle.setEffectiveWeight(1 - w);
      data.actions.idle.time =
        Math.max(0, sec - 2.3) % data.actions.idle.getClip().duration;
    }
    data.mixer.update(0);
    data.tx[3].offset.set(0, mode === "contact" ? (sec < 0.8 ? 0.5 : 0) : 0.75);
    if (Math.abs(sec - 4.15) < 0.08) data.tx[3].offset.x = 0.75;
    data.holo.uniforms.uTime.value = sec;
    data.holo.uniforms.uAmount.value = Math.min(1, sec * 1.8);
    if (mode === "office") {
      camera.position.set(data.motion.x, 6, 11.3 - sec * 0.1);
      camera.lookAt(0, 2.9, 0);
    } else if (mode === "hologram") {
      camera.position.set(0.3 * Math.sin(sec * 0.25), 3.4, 9.7);
      camera.lookAt(0, 1.9, 0);
    } else {
      camera.position.set(0.1, 4.35, 10.6 - sec * 0.06);
      camera.lookAt(0, 2.1, 0);
    }
    camera.updateProjectionMatrix();
  }, [f, sec, mode, data, camera]);
  return (
    <>
      <ambientLight intensity={1.5} />
      <directionalLight position={[4, 8, 6]} intensity={2} />
      {mode === "office" && (
        <group
          position={[2.4, -0.02, 0]}
          rotation={[0, -2.3 + data.motion.turn, 0]}
        >
          <primitive object={data.roomClone} />
        </group>
      )}
      {mode === "contact" && (
        <group position={[2.8, 0, -0.1]} rotation={[0, -0.8, 0]}>
          <primitive object={data.contactClone} />
        </group>
      )}
      <group
        position={
          mode === "office"
            ? [2.4, 0, 0]
            : mode === "contact"
              ? [2.8, 0, 0]
              : [0, 0.15 + data.motion.y, 0]
        }
        rotation={[
          0,
          mode === "office"
            ? -2.3 + Math.PI / 2 + data.motion.turn
            : -Math.PI + (mode === "hologram" ? data.motion.turn : 0),
          0,
        ]}
      >
        <primitive object={data.actor} />
      </group>
      {mode === "hologram" && (
        <>
          <mesh position={[0, -0.04, 0]}>
            <cylinderGeometry args={[1.18, 1.3, 0.2, 80]} />
            <meshStandardMaterial
              color="#0c496c"
              metalness={0.6}
              roughness={0.3}
            />
          </mesh>
          {[1.08, 1.23, 1.48].map((r, i) => (
            <mesh
              key={r}
              rotation={[-Math.PI / 2, 0, sec * (i % 2 ? -0.18 : 0.18)]}
              position={[0, 0.08 - i * 0.025, 0]}
            >
              <torusGeometry args={[r, 0.012, 8, 100]} />
              <meshBasicMaterial
                color="#51deff"
                transparent
                opacity={i === 2 ? 0.23 : 0.9}
              />
            </mesh>
          ))}
          <gridHelper
            args={[30, 48, "#155579", "#0b365c"]}
            position={[0, -0.16, 0]}
          />
          {Array.from({ length: 52 }, (_, i) => (
            <mesh
              key={i}
              position={[
                Math.sin(i * 2.399) * (0.9 + i * 0.04),
                (i * 0.119 + sec * 0.17) % 3.8,
                Math.cos(i * 2.399) * (1 + i * 0.035),
              ]}
            >
              <sphereGeometry args={[0.014, 5, 5]} />
              <meshBasicMaterial color="#68efff" transparent opacity={0.45} />
            </mesh>
          ))}
        </>
      )}
    </>
  );
}
export const World = ({ mode }: { mode: Mode }) => {
  const { width, height, fps } = useVideoConfig();
  return (
    <ThreeCanvas
      name={`${mode} 3D world`}
      width={width}
      height={height}
      premountFor={fps}
      dpr={1}
      camera={{ fov: 38, near: 0.1, far: 80 }}
      gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
      style={{ position: "absolute", inset: 0 }}
    >
      <Scene mode={mode} />
    </ThreeCanvas>
  );
};
