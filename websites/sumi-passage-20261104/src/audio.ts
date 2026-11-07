export class MountainAudio {
  enabled=false;
  private context:AudioContext|null=null;
  private volume:GainNode|null=null;
  private wind:AudioBufferSourceNode|null=null;
  async toggle(){
    if(!this.context){
      this.context=new AudioContext();
      this.volume=this.context.createGain();this.volume.gain.value=0;this.volume.connect(this.context.destination);
      const buffer=this.context.createBuffer(1,this.context.sampleRate*4,this.context.sampleRate);
      const channel=buffer.getChannelData(0);let last=0;
      for(let i=0;i<channel.length;i++){last=(last+(Math.random()*2-1)*.025)/1.025;channel[i]=last;}
      this.wind=this.context.createBufferSource();this.wind.buffer=buffer;this.wind.loop=true;
      const filter=this.context.createBiquadFilter();filter.type='lowpass';filter.frequency.value=540;
      this.wind.connect(filter);filter.connect(this.volume);this.wind.start();
    }
    await this.context.resume();this.enabled=!this.enabled;
    this.volume!.gain.setTargetAtTime(this.enabled?.44:0,this.context.currentTime,.35);
    if(this.enabled)this.chime();
    return this.enabled;
  }
  chime(index=0){
    if(!this.enabled||!this.context||!this.volume)return;
    [293.66,440,587.33].forEach((f,i)=>{
      const oscillator=this.context!.createOscillator();const gain=this.context!.createGain();
      const at=this.context!.currentTime+i*.12;
      oscillator.type='sine';oscillator.frequency.value=f*Math.pow(2,index/12);
      gain.gain.setValueAtTime(0,at);gain.gain.linearRampToValueAtTime(.16,at+.015);
      gain.gain.exponentialRampToValueAtTime(.0001,at+2.8);
      oscillator.connect(gain);gain.connect(this.volume!);oscillator.start(at);oscillator.stop(at+3);
    });
  }
}
