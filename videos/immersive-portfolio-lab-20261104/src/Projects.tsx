import {
  CanvasImage,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Frame, Reveal, Eyebrow, clamp, ease } from "./theme";
const Card = ({
  name,
  tag,
  image,
  index,
  x,
  y,
}: {
  name: string;
  tag: string;
  image: string;
  index: number;
  x: number;
  y: number;
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: 550,
        opacity: interpolate(
          f,
          [index * 0.17 * fps, (index * 0.17 + 0.7) * fps],
          [0, 1],
          clamp,
        ),
        translate: interpolate(
          f,
          [index * 0.17 * fps, (index * 0.17 + 1) * fps],
          ["0px 100px", "0px 0px"],
          { ...clamp, easing: ease },
        ),
        rotate: interpolate(
          f,
          [0, 6 * fps],
          [index % 2 ? "1.8deg" : "-1.8deg", index % 2 ? "-0.5deg" : "0.5deg"],
          clamp,
        ),
      }}
    >
      <div
        style={{
          height: 275,
          borderRadius: 21,
          overflow: "hidden",
          boxShadow: "0 20px 30px #55442b13",
        }}
      >
        <CanvasImage
          src={staticFile("upstream/thumbnails/" + image)}
          premountFor={fps}
          style={{ width: 550, height: 275, objectFit: "cover" }}
        />
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: 17,
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: 32, fontWeight: 900 }}>{name}</span>
        <span style={{ fontSize: 18, letterSpacing: 2, color: "#7d8175" }}>
          {tag} ↗
        </span>
      </div>
    </div>
  );
};
export const Projects = () => (
  <Frame active="WORK" chapter="03 / IDEAS OUT IN THE WORLD">
    <div style={{ position: "absolute", left: 120, top: 320, width: 460 }}>
      <Reveal>
        <Eyebrow>SELECTED PLAYGROUNDS</Eyebrow>
      </Reveal>
      <Reveal delay={0.15}>
        <h1
          style={{
            fontSize: 105,
            letterSpacing: -4,
            lineHeight: 1,
            margin: 0,
            fontWeight: 900,
          }}
        >
          Serious
          <br />
          about
          <br />
          <span style={{ color: "#cb652d" }}>play.</span>
        </h1>
      </Reveal>
      <Reveal delay={0.6}>
        <p
          style={{
            fontSize: 28,
            color: "#6f756c",
            lineHeight: 1.5,
            marginTop: 35,
          }}
        >
          Small details.
          <br />
          Memorable worlds.
        </p>
      </Reveal>
      <Reveal delay={1}>
        <div
          style={{
            marginTop: 45,
            fontSize: 18,
            lineHeight: 1.6,
            color: "#8d8c80",
          }}
        >
          FEATURED PROJECTS BY
          <br />
          <strong style={{ color: "#465149" }}>DAVID HECKHOFF</strong>
        </div>
      </Reveal>
    </div>
    <Card
      name="CubeWar"
      tag="MULTIPLAYER"
      image="cubewar.webp"
      index={0}
      x={650}
      y={215}
    />
    <Card
      name="Quibbo"
      tag="SOCIAL PLAY"
      image="quibbo.webp"
      index={1}
      x={1240}
      y={215}
    />
    <Card
      name="Sharkie"
      tag="BROWSER GAME"
      image="sharkie.webp"
      index={2}
      x={650}
      y={600}
    />
    <Card
      name="Particles"
      tag="WEBGL STUDY"
      image="particles.webp"
      index={3}
      x={1240}
      y={600}
    />
  </Frame>
);
