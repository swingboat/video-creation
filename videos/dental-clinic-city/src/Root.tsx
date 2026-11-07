import {Composition, Folder} from 'remotion';
import {DentalClinicCity} from './DentalClinicCity';
import {CityScene} from './clinic/CityScene';
import {CityIntro} from './clinic/CityIntro';
import {CityLocation} from './clinic/CityLocation';
import {ClinicBenefits} from './clinic/ClinicBenefits';
import {ClinicContact} from './clinic/ClinicContact';

export const RemotionRoot = () => (
  <>
  <Composition id="DentalClinicCity" component={DentalClinicCity} durationInFrames={900} fps={30} width={1080} height={1920}
    defaultProps={{configSrc: 'business/clinic.json'}} />
  <Folder name="DentalClinic-Layers">
    <Composition id="CityScene" component={CityScene} durationInFrames={900} fps={30} width={1080} height={1920} defaultProps={{configSrc: 'business/clinic.json'}} />
    <Composition id="CityIntro" component={CityIntro} durationInFrames={150} fps={30} width={1080} height={1920} defaultProps={{configSrc: 'business/clinic.json'}} />
    <Composition id="CityLocation" component={CityLocation} durationInFrames={270} fps={30} width={1080} height={1920} defaultProps={{configSrc: 'business/clinic.json'}} />
    <Composition id="ClinicBenefits" component={ClinicBenefits} durationInFrames={240} fps={30} width={1080} height={1920} defaultProps={{configSrc: 'business/clinic.json'}} />
    <Composition id="ClinicContact" component={ClinicContact} durationInFrames={240} fps={30} width={1080} height={1920} defaultProps={{configSrc: 'business/clinic.json'}} />
  </Folder>
  </>
);
