import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Frame, Reveal, Eyebrow, C, clamp } from "./theme";
import { World } from "./World";
export const Hologram = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Frame dark active="ABOUT" chapter="02 / A DIFFERENT DIMENSION">
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at 50% 65%,#09527980,transparent 65%)",
        }}
      />
      <World mode="hologram" />
      <div style={{ position: "absolute", left: 120, top: 245, width: 520 }}>
        <Reveal>
          <Eyebrow dark>THE HUMAN BEHIND THE PIXELS</Eyebrow>
        </Reveal>
        <Reveal delay={0.2}>
          <h1
            style={{
              fontSize: 100,
              lineHeight: 1.01,
              letterSpacing: -3,
              margin: 0,
              fontWeight: 900,
            }}
          >
            Curiosity,
            <br />
            in every
            <br />
            <span style={{ color: C.cyan }}>dimension.</span>
          </h1>
        </Reveal>
        <Reveal delay={0.7}>
          <p
            style={{
              fontSize: 29,
              lineHeight: 1.5,
              color: "#adc9dc",
              maxWidth: 410,
            }}
          >
            An idea becomes a scene.
            <br />A scene becomes an experience.
          </p>
        </Reveal>
      </div>
      <div style={{ position: "absolute", right: 140, top: 345, width: 405 }}>
        <Reveal delay={0.9}>
          <div
            style={{
              borderBottom: "1px solid #49728c",
              paddingBottom: 20,
              fontSize: 20,
              letterSpacing: 4,
              color: C.cyan,
            }}
          >
            CREATIVE TOOLKIT / 003
          </div>
        </Reveal>
        <Reveal delay={1.15}>
          <div
            style={{
              fontSize: 40,
              fontWeight: 700,
              padding: "26px 0",
              borderBottom: "1px solid #234d6e",
            }}
          >
            Three.js{" "}
            <span
              style={{
                float: "right",
                fontSize: 19,
                color: "#82b5cc",
                paddingTop: 15,
              }}
            >
              3D / WEBGL
            </span>
          </div>
        </Reveal>
        <Reveal delay={1.5}>
          <div
            style={{
              fontSize: 40,
              fontWeight: 700,
              padding: "26px 0",
              borderBottom: "1px solid #234d6e",
            }}
          >
            GSAP{" "}
            <span
              style={{
                float: "right",
                fontSize: 19,
                color: "#82b5cc",
                paddingTop: 15,
              }}
            >
              MOTION
            </span>
          </div>
        </Reveal>
        <Reveal delay={1.85}>
          <div
            style={{
              fontSize: 40,
              fontWeight: 700,
              padding: "26px 0",
              borderBottom: "1px solid #234d6e",
            }}
          >
            Lenis{" "}
            <span
              style={{
                float: "right",
                fontSize: 19,
                color: "#82b5cc",
                paddingTop: 15,
              }}
            >
              SMOOTH SCROLL
            </span>
          </div>
        </Reveal>
        <Reveal delay={2.3}>
          <div
            style={{
              marginTop: 30,
              fontSize: 19,
              color: "#82b5cc",
              letterSpacing: 2,
            }}
          >
            REFERENCE SITE TECHNOLOGY
          </div>
        </Reveal>
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 95,
          left: 850,
          width: 220,
          textAlign: "center",
          color: C.cyan,
          fontSize: 22,
          fontFamily: "monospace",
          letterSpacing: 5,
        }}
      >
        SCAN{" "}
        {String(
          Math.floor(interpolate(f, [0, 3 * fps], [0, 100], clamp)),
        ).padStart(3, "0")}
        <div
          style={{
            fontSize: 13,
            letterSpacing: 3,
            marginTop: 13,
            opacity: 0.5,
          }}
        >
          IDENTITY VERIFIED
        </div>
      </div>
    </Frame>
  );
};
