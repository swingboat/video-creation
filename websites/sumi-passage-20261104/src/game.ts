export type Platform = {x:number; z:number; y:number; w:number; d:number; depth:number};
export const PLATFORMS: Platform[] = [
  {x:0,z:0,y:0,w:8.8,d:7,depth:15},
  {x:7.1,z:-1.3,y:.65,w:3.2,d:3.4,depth:13},
  {x:11.7,z:-2.5,y:1.15,w:3.4,d:3.7,depth:16},
  {x:17.5,z:-3.3,y:1.6,w:6.9,d:6.5,depth:19},
  {x:23.8,z:-4.3,y:2.2,w:3.2,d:3.5,depth:18},
  {x:28.5,z:-5.5,y:2.8,w:3.8,d:3.9,depth:20},
  {x:35,z:-6.5,y:3.3,w:7.3,d:7,depth:22},
];
export const SEALS = [
  {x:7.1,z:-1.3,y:.65,name:'渡雾'},
  {x:17.5,z:-3.3,y:1.6,name:'听松'},
  {x:28.5,z:-5.5,y:2.8,name:'见山'},
];
export type Input = {x:number; z:number; sprint:boolean};
export type Save = {version:1; checkpoint:number; seals:number[]; seconds:number; falls:number};
export type GameEvent = {type:'seal'|'fall'|'win'|'missing'; index?:number};
export class Game {
  x=-.9; z=1.4; y=0; vy=0; grounded=true;
  moving=0; facing=Math.PI; seconds=0; falls=0; checkpoint=0;
  seals=new Set<number>(); started=false; paused=false; won=false;
  private coyote=.12;
  private jumpBuffer=0;
  private missingCooldown=0;
  onEvent:(event:GameEvent)=>void=()=>{};
  jump(){if(this.started&&!this.paused&&!this.won)this.jumpBuffer=.16;}
  start(){this.started=true;this.paused=false;}
  reset(){
    this.x=-.9;this.z=1.4;this.y=0;this.vy=0;this.grounded=true;
    this.moving=0;this.facing=Math.PI;this.seconds=0;this.falls=0;this.checkpoint=0;
    this.seals.clear();this.won=false;this.paused=false;this.coyote=.12;
    this.jumpBuffer=0;this.missingCooldown=0;
  }
  respawn(countFall=false){
    if(countFall){this.falls++;this.onEvent({type:'fall'});}
    const p=PLATFORMS[this.checkpoint];
    this.x=p.x-(this.checkpoint===0?.9:0);this.z=p.z+(this.checkpoint===0?1.4:.6);
    this.y=p.y;this.vy=0;this.grounded=true;this.coyote=.12;this.jumpBuffer=0;
  }
  save():Save{return {version:1,checkpoint:this.checkpoint,seals:[...this.seals],seconds:this.seconds,falls:this.falls};}
  restore(value:unknown):boolean{
    if(!value||typeof value!=='object')return false;
    const v=value as Save;
    if(v.version!==1||![0,3].includes(v.checkpoint)||!Array.isArray(v.seals)||v.seals.length>3||
      !v.seals.every(i=>Number.isInteger(i)&&i>=0&&i<3)||!Number.isFinite(v.seconds)||v.seconds<0||
      !Number.isInteger(v.falls)||v.falls<0||
      (v.checkpoint===3&&!v.seals.includes(1)))return false;
    this.checkpoint=v.checkpoint;this.seals=new Set(v.seals);this.seconds=v.seconds;this.falls=v.falls;
    this.respawn();return true;
  }
  update(dt:number,input:Input){
    if(!this.started||this.paused||this.won){this.moving=0;return;}
    this.seconds+=dt;
    this.missingCooldown=Math.max(0,this.missingCooldown-dt);
    this.jumpBuffer=Math.max(0,this.jumpBuffer-dt);
    this.coyote=this.grounded?.12:Math.max(0,this.coyote-dt);
    if(this.jumpBuffer>0&&this.coyote>0){this.vy=9.4;this.grounded=false;this.coyote=0;this.jumpBuffer=0;}
    const length=Math.hypot(input.x,input.z);
    const speed=input.sprint?5.3:3.2;
    const dx=length>0?input.x/Math.max(1,length):0;
    const dz=length>0?input.z/Math.max(1,length):0;
    this.moving=Math.min(1,length)*(input.sprint?1.4:1);
    if(length>.01)this.facing=Math.atan2(dx,dz);
    this.x+=dx*speed*dt;this.z+=dz*speed*dt;
    const prevY=this.y;
    this.vy-=23*dt;this.y+=this.vy*dt;
    this.grounded=false;
    for(const p of PLATFORMS){
      if(Math.abs(this.x-p.x)<p.w/2-.1&&Math.abs(this.z-p.z)<p.d/2-.1&&
        this.vy<=0&&prevY>=p.y-.025&&this.y<=p.y){
        this.y=p.y;this.vy=0;this.grounded=true;break;
      }
    }
    if(this.y<-9){this.respawn(true);return;}
    SEALS.forEach((seal,i)=>{
      if(!this.seals.has(i)&&Math.hypot(this.x-seal.x,this.z-seal.z)<1.05&&Math.abs(this.y-seal.y)<1.5){
        this.seals.add(i);if(i===1)this.checkpoint=3;
        this.onEvent({type:'seal',index:i});
      }
    });
    if(Math.hypot(this.x-35,this.z+7.2)<1.8&&this.grounded){
      if(this.seals.size===3){this.won=true;this.moving=0;this.onEvent({type:'win'});}
      else if(this.missingCooldown===0){this.missingCooldown=4;this.onEvent({type:'missing'});}
    }
  }
}
