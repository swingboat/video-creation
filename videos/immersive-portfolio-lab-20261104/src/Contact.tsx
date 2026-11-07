import { Frame, Reveal, Eyebrow, C } from "./theme";
import { World } from "./World";
export const Contact = () => (
  <Frame active="CONTACT" chapter="04 / THE NEXT CHAPTER IS YOURS">
    <World mode="contact" />
    <div style={{ position: "absolute", left: 120, top: 275, width: 800 }}>
      <Reveal>
        <Eyebrow>GOOD THINGS START WITH A HELLO</Eyebrow>
      </Reveal>
      <Reveal delay={0.15}>
        <h1
          style={{
            fontSize: 119,
            lineHeight: 0.98,
            letterSpacing: -5,
            margin: 0,
            fontWeight: 900,
          }}
        >
          Let’s make
          <br />
          something
          <br />
          <span style={{ color: "#cb652d" }}>move.</span>
        </h1>
      </Reveal>
      <Reveal delay={0.7}>
        <div
          style={{
            marginTop: 44,
            display: "inline-flex",
            gap: 40,
            padding: "22px 32px",
            background: C.orange,
            borderRadius: 50,
            fontSize: 27,
            fontWeight: 900,
          }}
        >
          START A CONVERSATION <span>↗</span>
        </div>
      </Reveal>
      <Reveal delay={1.2}>
        <div
          style={{
            marginTop: 40,
            fontSize: 22,
            color: "#7f8376",
            letterSpacing: 2,
          }}
        >
          DESIGN WITH CHARACTER. BUILD WITH CARE.
        </div>
      </Reveal>
    </div>
    <Reveal
      delay={2.25}
      style={{ position: "absolute", right: 110, top: 210, rotate: "7deg" }}
    >
      <div
        style={{
          background: "#fffaf0",
          border: "1px solid #ded7c8",
          padding: "18px 27px",
          fontSize: 22,
          fontWeight: 700,
          borderRadius: 16,
        }}
      >
        Ready when you are.
      </div>
    </Reveal>
  </Frame>
);
