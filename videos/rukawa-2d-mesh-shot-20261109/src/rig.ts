export type P={x:number;y:number};
export const p=(x:number,y:number):P=>({x,y});
export const add=(a:P,b:P)=>p(a.x+b.x,a.y+b.y);
export const sub=(a:P,b:P)=>p(a.x-b.x,a.y-b.y);
export const mul=(a:P,s:number)=>p(a.x*s,a.y*s);
export const len=(a:P)=>Math.hypot(a.x,a.y);
export const lerp=(a:P,b:P,u:number)=>add(mul(a,1-u),mul(b,u));
export const clamp=(x:number)=>Math.max(0,Math.min(1,x));
export const sm=(a:number,b:number,t:number)=>{const u=clamp((t-a)/(b-a));return u*u*u*(10+u*(-15+6*u));};
export const rot=(v:P,a:number)=>p(v.x*Math.cos(a)-v.y*Math.sin(a),v.x*Math.sin(a)+v.y*Math.cos(a));
export const angle=(v:P)=>Math.atan2(v.y,v.x);
const hermite=(t:number,a:number,b:number,y0:number,y1:number,v0=0,v1=0)=>{const u=clamp((t-a)/(b-a)),d=b-a;return (2*u**3-3*u*u+1)*y0+(u**3-2*u*u+u)*d*v0+(-2*u**3+3*u*u)*y1+(u**3-u*u)*d*v1;};
export const RELEASE=1.43,TAKEOFF=1.16,LAND=1.76;
export const rootY=(t:number)=>t<.3?0:t<.9?42*sm(.3,.9,t):t<TAKEOFF?hermite(t,.9,TAKEOFF,42,0,0,-480):t<LAND?-4*72*((t-TAKEOFF)/.6)*(1-(t-TAKEOFF)/.6):t<LAND+.19?hermite(t,LAND,LAND+.19,0,34,480,0):34*(1-sm(LAND+.19,2.60,t));
const rootAt=(t:number)=>p(950-13*sm(.9,1.76,t),334+rootY(t));
const leanAt=(t:number)=>-.025-.08*sm(.3,.9,t)*(1-sm(1.0,1.42,t));
function heldBallAt(t:number){
 const root=rootAt(t),lift=sm(.65,1.40,t),sh=add(root,rot(mul(sub(p(364,174),p(292,365)),.6),leanAt(t))),fw=rot(p(0,-1),-.15-.15*lift);
 const by=root.y-42-253*lift,wy=by+30-fw.y*24,beta=-.85+1.7*lift,l1=102.03,l2=90.16,reach2=l1*l1+l2*l2+2*l1*l2*Math.cos(beta),wx=sh.x-Math.sqrt(Math.max(1,reach2-(wy-sh.y)**2));
 return p(wx+fw.x*24,by);
}
const air=(t:number)=>t>TAKEOFF&&t<LAND?4*((t-TAKEOFF)/.6)*(1-(t-TAKEOFF)/.6):0;
export const ik=(a:P,b:P,l1:number,l2:number,bend:number):P=>{const v=sub(b,a),d=Math.max(.001,Math.max(Math.abs(l1-l2)+.00001,Math.min(len(v),l1+l2-.00001))),unit=mul(v,1/len(v)),h=(l1*l1-l2*l2+d*d)/(2*d);const n=mul(p(-unit.y,unit.x),bend);return add(add(a,mul(unit,h)),mul(n,Math.sqrt(Math.max(0,l1*l1-h*h))));};
export const SCREEN_SCALE=.83;
export const screen=(v:P)=>p(950+(v.x-950)*SCREEN_SCALE,660+(v.y-660)*SCREEN_SCALE);
export function pose(t:number){
 const root=rootAt(t);
 const lean=leanAt(t);
 const body=(v:P)=>add(root,rot(mul(sub(v,p(292,365)),.6),lean));
 const hipNear=body(p(327,402)),hipFar=body(p(257,402));
 const feetLift=56*air(t),nearAnkle=p(977-13*sm(1.16,1.76,t),616-feetLift),farAnkle=p(917-13*sm(1.16,1.76,t),618-feetLift);
 const kneeNear=ik(hipNear,nearAnkle,131.63,146.22,1),kneeFar=ik(hipFar,farAnkle,132.18,148.51,1);
 const shoulderNear=body(p(364,174)),shoulderFar=body(p(234,178));
 const lift=sm(.65,1.40,t);
 const held=()=>heldBallAt(t);
 const ball=t<=RELEASE?held():add(ballAtRelease(),p(-520*(t-RELEASE),-220*(t-RELEASE)+350*(t-RELEASE)**2));
 function ballAtRelease(){return heldBallAt(RELEASE);}
 const heldAtRelease=ballAtRelease();
 const handFWNear=rot(p(0,-1),-.15-.15*lift),handFWFar=rot(p(0,-1),-.45);
 let palmNear=add(t<=RELEASE?ball:heldAtRelease,p(0,30)),palmFar=add(t<=RELEASE?ball:heldAtRelease,p(26,5));
 let wristNear=sub(palmNear,mul(handFWNear,24)),wristFar=sub(palmFar,mul(handFWFar,24));
 let fwNear=handFWNear,fwFar=handFWFar;
 if(t>RELEASE){
  const rd=rootY(t)-rootY(RELEASE),u=sm(RELEASE,1.68,t),relax=0;
  wristNear=add(wristNear,p(0,rd));wristFar=add(wristFar,p(0,rd));
  const drop=sm(1.52,2.15,t),rpRoot=rootAt(RELEASE),startOffset=sub(wristFar,root);
  wristFar=add(add(root,lerp(startOffset,p(-125,-70),drop)),p(-70*Math.sin(Math.PI*drop),0));
  fwNear=rot(handFWNear,-1.1*u);fwFar=rot(handFWFar,.15*u);
  const aN=add(root,p(28,-10)),aF=add(root,p(-35,-5));
  wristNear=add(lerp(wristNear,aN,relax),p(-45*Math.sin(Math.PI*relax),0));wristFar=add(lerp(wristFar,aF,relax),p(-35*Math.sin(Math.PI*relax),0));
  fwNear=rot(fwNear,2.6*relax);fwFar=rot(fwFar,2.8*relax);
 }
 const elbowNear=ik(shoulderNear,wristNear,102.03,90.16,lift<.5?-1:1),elbowFar=ik(shoulderFar,wristFar,108.30,87.34,-1);
 if(t>RELEASE){
  const rp=pose(RELEASE),u=sm(RELEASE,1.68,t),baseN=angle(sub(rp.wristNear,rp.elbowNear)),baseF=angle(sub(rp.wristFar,rp.elbowFar));
  const wrap=(v:number)=>Math.atan2(Math.sin(v),Math.cos(v));
  const bendN=wrap(angle(rp.fwNear)-baseN)*(1-u)-1.10*u,bendF=wrap(angle(rp.fwFar)-baseF)*(1-sm(1.52,2.15,t));
  fwNear=rot(mul(sub(wristNear,elbowNear),1/len(sub(wristNear,elbowNear))),bendN);
  fwFar=rot(mul(sub(wristFar,elbowFar),1/len(sub(wristFar,elbowFar))),bendF);
 }
 return {root,lean,body,ball,hipNear,hipFar,kneeNear,kneeFar,nearAnkle,farAnkle,shoulderNear,shoulderFar,elbowNear,elbowFar,wristNear,wristFar,fwNear,fwFar};
}
// Rigid dual-quaternion skinning in the 2D plane. Each mesh stays connected.
export type DQ={w:number;z:number;dx:number;dy:number};
export function rigid(a:P,b:P,ta:P,tb:P):DQ{
 const theta=angle(sub(tb,ta))-angle(sub(b,a)),w=Math.cos(theta/2),z=Math.sin(theta/2),tr=sub(ta,rot(a,theta));return {w,z,dx:.5*(tr.x*w+tr.y*z),dy:.5*(-tr.x*z+tr.y*w)};
}
export function skin(v:P,dqs:DQ[],weights:number[]):P{
 const ref=dqs[0];let w=0,z=0,dx=0,dy=0;
 for(let i=0;i<dqs.length;i++){const q=dqs[i],s=(q.w*ref.w+q.z*ref.z<0?-1:1)*weights[i];w+=q.w*s;z+=q.z*s;dx+=q.dx*s;dy+=q.dy*s;}
 const n=Math.hypot(w,z);w/=n;z/=n;dx/=n;dy/=n;
 return add(rot(v,2*Math.atan2(z,w)),p(2*(dx*w-dy*z),2*(dy*w+dx*z)));
}
export const source={nearArm:{shoulder:p(1260,96),elbow:p(1254,266),wrist:p(1240,416),bounds:[1195,40,125,480]},farArm:{shoulder:p(780,96),elbow:p(759,276),wrist:p(739,421),bounds:[703,40,130,480]},nearLeg:{hip:p(272,430),knee:p(267,665),ankle:p(274,926),bounds:[160,550,162,465]},farLeg:{hip:p(768,430),knee:p(790,665),ankle:p(800,930),bounds:[704,550,158,472]}};
export function armMesh(side:'near'|'far',r:ReturnType<typeof pose>){
 const s=side==='near'?source.nearArm:source.farArm;
 const S=(v:P)=>p(v.x*.38,v.y<=s.wrist.y?v.y*.60:s.wrist.y*.6+(v.y-s.wrist.y)*.45);
 const sh=side==='near'?r.shoulderNear:r.shoulderFar,el=side==='near'?r.elbowNear:r.elbowFar,wr=side==='near'?r.wristNear:r.wristFar,fw=side==='near'?r.fwNear:r.fwFar;
 const a=S(s.shoulder),b=S(s.elbow),c=S(s.wrist);
 const qs=[rigid(a,b,sh,el),rigid(b,c,el,wr),rigid(c,add(c,p(0,1)),wr,add(wr,fw))];
 return (v:P)=>{const u=sm(s.elbow.y-25,s.elbow.y+25,v.y),h=sm(s.wrist.y-15,s.wrist.y+15,v.y);return screen(skin(S(v),qs,[(1-u)*(1-h),u*(1-h),h]));};
}
export function legMesh(side:'near'|'far',r:ReturnType<typeof pose>){
 const s=side==='near'?source.nearLeg:source.farLeg,S=(v:P)=>mul(v,.56),a=S(s.hip),b=S(s.knee),c=S(s.ankle),hip=side==='near'?r.hipNear:r.hipFar,knee=side==='near'?r.kneeNear:r.kneeFar,ankle=side==='near'?r.nearAnkle:r.farAnkle;
 const qs=[rigid(a,b,hip,knee),rigid(b,c,knee,ankle),rigid(c,add(c,p(1,0)),ankle,add(ankle,p(1,0)))];
 return (v:P)=>{const u=sm(s.knee.y-24,s.knee.y+24,v.y),f=sm(s.ankle.y-12,s.ankle.y+12,v.y);return screen(skin(S(v),qs,[(1-u)*(1-f),u*(1-f),f]));};
}

export function bodyMesh(r:ReturnType<typeof pose>){return (v:P)=>{
 const b=r.body(v),w=sm(390,524,v.y)*.83,u=sm(265,315,v.x);
 const far=add(r.hipFar,rot(sub(b,r.hipFar),angle(sub(r.kneeFar,r.hipFar))-Math.PI/2-r.lean));
 const near=add(r.hipNear,rot(sub(b,r.hipNear),angle(sub(r.kneeNear,r.hipNear))-Math.PI/2-r.lean));
 const c=lerp(far,near,u);c.y=b.y+(c.y-b.y)*.40+3*w;return screen(lerp(b,c,w));
};}
