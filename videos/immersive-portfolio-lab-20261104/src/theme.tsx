import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
export const C = {
  cream: "#f4efe5",
  ink: "#27312f",
  orange: "#f58b32",
  blue: "#061e49",
  cyan: "#5ce8ff",
};
export const ease = Easing.bezier(0.16, 1, 0.3, 1);
export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
export const FontStyle = () => (
  <style>{`@font-face{font-family:Urbanist;src:url('${staticFile("fonts/urbanist-400.woff2")}');font-weight:400}@font-face{font-family:Urbanist;src:url('${staticFile("fonts/urbanist-700.woff2")}');font-weight:700}@font-face{font-family:Urbanist;src:url('${staticFile("fonts/urbanist-900.woff2")}');font-weight:900}*{box-sizing:border-box}`}</style>
);
export const Cube = () => (
  <svg
    width="44"
    height="44"
    viewBox="0 0 40 40"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
  >
    <path d="m20 3 16 9v17l-16 9-16-9V12L20 3ZM4 12l16 9 16-9M20 21v17M12 8l16 9v17" />
  </svg>
);
export const Frame = ({
  children,
  dark = false,
  active = "STUDIO",
  chapter = "01 / ENTER THE STUDIO",
}: {
  children: React.ReactNode;
  dark?: boolean;
  active?: string;
  chapter?: string;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background: dark ? C.blue : C.cream,
        fontFamily: "Urbanist, sans-serif",
        color: dark ? "#ecfbff" : C.ink,
        overflow: "hidden",
      }}
    >
      <FontStyle />
      {children}
      <div
        style={{
          position: "absolute",
          left: 92,
          right: 92,
          top: 62,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 17 }}>
          <Cube />
          <div style={{ fontSize: 23, fontWeight: 900, letterSpacing: 3 }}>
            FIELDNOTES
            <span
              style={{
                fontWeight: 400,
                letterSpacing: 1,
                marginLeft: 15,
                opacity: 0.55,
              }}
            >
              STUDIO
            </span>
          </div>
        </div>
        <div
          style={{
            display: "flex",
            gap: 12,
            fontSize: 20,
            fontWeight: 700,
            letterSpacing: 2,
          }}
        >
          {["STUDIO", "ABOUT", "WORK", "CONTACT"].map((x) => (
            <div
              key={x}
              style={{
                padding: "13px 25px",
                background:
                  active === x ? (dark ? "#135d7b" : C.ink) : "transparent",
                color: active === x ? "#fff" : undefined,
                borderRadius: 40,
                opacity: active === x ? 1 : 0.55,
              }}
            >
              {x}
            </div>
          ))}
        </div>
        <div
          style={{
            fontSize: 19,
            fontWeight: 900,
            padding: "17px 25px",
            background: dark ? C.cyan : C.orange,
            color: dark ? C.blue : C.ink,
            borderRadius: 40,
            letterSpacing: 1,
          }}
        >
          LET’S TALK <span style={{ marginLeft: 20 }}>↗</span>
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 96,
          right: 96,
          bottom: 45,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "end",
          fontSize: 17,
          fontWeight: 700,
          letterSpacing: 1.4,
          opacity: dark ? 0.7 : 0.65,
        }}
      >
        <span>{chapter}</span>
        <span style={{ fontWeight: 400, letterSpacing: 0.4 }}>
          Study remix · 3D assets & original projects by David Heckhoff ·
          david-hckh.com
        </span>
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          width: interpolate(frame, [0, 6 * fps], [0, 1920], clamp),
          height: 5,
          background: dark ? C.cyan : C.orange,
        }}
      />
    </AbsoluteFill>
  );
};
export const Reveal = ({
  children,
  delay = 0,
  style = {},
}: {
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        ...style,
        opacity: interpolate(
          f,
          [delay * fps, (delay + 0.65) * fps],
          [0, 1],
          clamp,
        ),
        translate: interpolate(
          f,
          [delay * fps, (delay + 0.9) * fps],
          ["0px 44px", "0px 0px"],
          { ...clamp, easing: ease },
        ),
      }}
    >
      {children}
    </div>
  );
};
export const Eyebrow = ({
  children,
  dark = false,
}: {
  children: React.ReactNode;
  dark?: boolean;
}) => (
  <div
    style={{
      fontSize: 21,
      fontWeight: 700,
      letterSpacing: 4,
      color: dark ? C.cyan : "#8d6d4d",
      marginBottom: 30,
      display: "flex",
      alignItems: "center",
      gap: 16,
    }}
  >
    <span style={{ width: 32, height: 2, background: "currentColor" }} />
    {children}
  </div>
);
