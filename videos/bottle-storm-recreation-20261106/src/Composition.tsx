import { Audio, Video } from "@remotion/media";
import { AbsoluteFill, Composition, staticFile, useVideoConfig } from "remotion";
type Props = { source: string };

export const MyComposition = () => {
  return (
    <Composition
      id="BottleStorm"
      component={MyComponent}
      durationInFrames={480}
      fps={24}
      width={1280}
      height={720}
      defaultProps={{ source: "bunny-fish-picture.mp4" }}
    />
  );
};

export const MyComponent: React.FC<Props> = ({ source }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#181b20" }}>
      <Video
        name="Rabbit carries a block and draws"
        src={staticFile(source)}
        durationInFrames={20 * fps}
        premountFor={fps}
        muted
        objectFit="contain"
        style={{ width: "100%", height: "100%" }}
      />
      <Audio
        name="Procedural ocean, wind, rain and thunder"
        src={staticFile("storm-soundscape.wav")}
        durationInFrames={20 * fps}
        premountFor={fps}
        volume={0.8}
      />
    </AbsoluteFill>
  );
};
