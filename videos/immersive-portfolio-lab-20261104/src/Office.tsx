import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { Frame, Reveal, Eyebrow, C, clamp } from "./theme";
import { World } from "./World";
export const Office = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Frame chapter="01 / ENTER THE STUDIO">
      <World mode="office" />
      <div style={{ position: "absolute", left: 120, top: 290, width: 710 }}>
        <Reveal>
          <Eyebrow>A CREATIVE LITTLE UNIVERSE</Eyebrow>
        </Reveal>
        <Reveal delay={0.12}>
          <h1
            style={{
              fontSize: 122,
              lineHeight: 0.96,
              letterSpacing: -5,
              margin: 0,
              fontWeight: 900,
            }}
          >
            A little world.
            <br />A lot of <span style={{ color: "#cc642a" }}>ideas.</span>
          </h1>
        </Reveal>
        <Reveal delay={0.5}>
          <p
            style={{
              fontSize: 32,
              lineHeight: 1.5,
              maxWidth: 490,
              marginTop: 35,
              color: "#6f756c",
            }}
          >
            Crafting playful experiences
            <br />
            where design meets code.
          </p>
        </Reveal>
        <Reveal delay={0.8}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 28,
              padding: "19px 26px",
              border: "1px solid #c9c3b5",
              borderRadius: 50,
              fontSize: 23,
              fontWeight: 700,
              marginTop: 12,
            }}
          >
            STEP INSIDE <span style={{ fontSize: 30 }}>↘</span>
          </div>
        </Reveal>
      </div>
      <div
        style={{
          position: "absolute",
          right: 170,
          top: 210,
          rotate: "6deg",
          opacity: interpolate(f, [1.3 * fps, 1.9 * fps], [0, 1], clamp),
          padding: "16px 24px",
          background: C.orange,
          borderRadius: 18,
          fontSize: 23,
          fontWeight: 900,
          boxShadow: "0 14px 30px #98693720",
        }}
      >
        Oh, hey there! <span style={{ marginLeft: 12 }}>✦</span>
      </div>
      <div
        style={{
          position: "absolute",
          left: 125,
          bottom: 150,
          fontSize: 20,
          letterSpacing: 4,
          color: "#96978c",
        }}
      >
        DESIGN · CODE · PLAY
      </div>
    </Frame>
  );
};
