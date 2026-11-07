import {
  AbsoluteFill,
  Composition,
  Folder,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import { Audio } from "@remotion/media";
import { Office } from "./Office";
import { Hologram } from "./Hologram";
import { Projects } from "./Projects";
import { Contact } from "./Contact";
import { clamp } from "./theme";
const Wipe = ({ at, color }: { at: number; color: string }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background: color,
        translate: interpolate(
          f / fps - at,
          [-0.3, 0, 0.3],
          ["0px 1080px", "0px 0px", "0px -1080px"],
          clamp,
        ),
        pointerEvents: "none",
      }}
    />
  );
};
export const PortfolioFilm = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Sequence
        name="01 · Office / welcome"
        from={0}
        durationInFrames={6 * fps}
        premountFor={fps}
      >
        <Office />
      </Sequence>
      <Sequence
        name="02 · Hologram / toolkit"
        from={6 * fps}
        durationInFrames={6 * fps}
        premountFor={fps}
      >
        <Hologram />
      </Sequence>
      <Sequence
        name="03 · Selected projects"
        from={12 * fps}
        durationInFrames={6 * fps}
        premountFor={fps}
      >
        <Projects />
      </Sequence>
      <Sequence
        name="04 · Contact / finale"
        from={18 * fps}
        durationInFrames={6 * fps}
        premountFor={fps}
      >
        <Contact />
      </Sequence>
      <Wipe at={6} color="#0c3457" />
      <Wipe at={12} color="#e8dfce" />
      <Wipe at={18} color="#e9dfcf" />
      <Audio
        name="Original electronic score"
        src={staticFile("audio/studio-score.wav")}
        premountFor={fps}
        volume={0.8}
      />
    </AbsoluteFill>
  );
};
export const Root = () => (
  <>
    <Composition
      id="PortfolioFilm"
      component={PortfolioFilm}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={720}
    />
    <Folder name="Scenes">
      <Composition
        id="Office"
        component={Office}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={180}
      />
      <Composition
        id="Hologram"
        component={Hologram}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={180}
      />
      <Composition
        id="Projects"
        component={Projects}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={180}
      />
      <Composition
        id="Contact"
        component={Contact}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={180}
      />
    </Folder>
  </>
);
