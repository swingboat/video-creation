"""Create deterministic, project-local surf, wind and skateboard sound design."""
from pathlib import Path
from array import array
import math
import random
import wave

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'public' / 'seaside'
RATE = 44100
SECONDS = 10

def write_track(name, kind):
    rng = random.Random(819 + kind)
    samples = array('h')
    low = soft = rumble = 0.0
    for i in range(RATE * SECONDS):
        t = i / RATE
        noise = rng.uniform(-1, 1)
        low += 0.018 * (noise - low)
        soft += 0.12 * (noise - soft)
        rumble += 0.004 * (noise - rumble)
        if kind == 0:
            # A swell rises, breaks, and washes back every few seconds.
            phase = (t + 0.7) % 3.9 / 3.9
            swell = math.sin(math.pi * phase) ** 2
            sample = (low * 2.9 + soft * 0.65 + noise * 0.09) * (0.22 + 0.55 * swell)
        elif kind == 1:
            gust = 0.52 + 0.2 * math.sin(t * 0.87) + 0.12 * math.sin(t * 2.13)
            sample = (rumble * 4.0 + low * 0.4) * gust
        else:
            # Low wheel rumble, granular road texture, and quiet pavement joints.
            sample = low * 1.45 + soft * 0.28 + noise * 0.04
            sample *= 0.7 + 0.13 * math.sin(t * 46) + 0.06 * math.sin(t * 101)
            for at in (0.9, 1.65, 2.3, 2.95, 4.3, 6.1, 7.1):
                age = t - at
                if 0 <= age < 0.09:
                    sample += 0.15 * math.exp(-age * 65) * math.sin(age * 1600)
        fade = min(1, t / 0.5, (SECONDS - t) / 0.55)
        sample = max(-0.95, min(0.95, sample * fade))
        # Slight stereo variation, kept quiet and spacious.
        samples.append(int(sample * 26000))
        samples.append(int(sample * (0.97 + 0.02 * math.sin(t * 0.5)) * 26000))
    with wave.open(str(DEST / name), 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(samples.tobytes())
    print(name, SECONDS, 'seconds, stereo')

DEST.mkdir(parents=True, exist_ok=True)
write_track('surf.wav', 0)
write_track('wind.wav', 1)
write_track('skateboard.wav', 2)
