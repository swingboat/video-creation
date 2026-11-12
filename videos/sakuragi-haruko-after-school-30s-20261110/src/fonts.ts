import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';
export const fontFamily='NotoSansSC';
loadFont({family:fontFamily,url:staticFile('fonts/NotoSansSC.ttf'),weight:'400'});
