import {loadFont} from '@remotion/fonts';
import {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

// Original MiSans files from Xiaomi, stored only in this project.
const fontsLoaded = Promise.all([
  loadFont({family: 'MiSans', url: staticFile('fonts/MiSans-Regular.woff2'), weight: '400'}),
  loadFont({family: 'MiSans', url: staticFile('fonts/MiSans-Bold.woff2'), weight: '700'}),
]);

// Particle positions must be sampled after the real font has loaded.
export const useMiSans = () => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender('Preparing MiSans particle typography'));
  useEffect(() => {
    let mounted = true;
    fontsLoaded.then(() => { if (mounted) setReady(true); });
    return () => { mounted = false; continueRender(handle); };
  }, [handle]);
  useEffect(() => { if (ready) continueRender(handle); }, [ready, handle]);
  return ready;
};
