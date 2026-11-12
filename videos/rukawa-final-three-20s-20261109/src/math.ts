export type Point={x:number;y:number};
export const p=(x:number,y:number):Point=>({x,y});
export const add=(a:Point,b:Point)=>p(a.x+b.x,a.y+b.y);
export const sub=(a:Point,b:Point)=>p(a.x-b.x,a.y-b.y);
export const mul=(a:Point,s:number)=>p(a.x*s,a.y*s);
export const rot=(a:Point,t:number)=>p(a.x*Math.cos(t)-a.y*Math.sin(t),a.x*Math.sin(t)+a.y*Math.cos(t));
export const mix=(a:Point,b:Point,u:number)=>add(mul(a,1-u),mul(b,u));
export const clamp=(u:number)=>Math.min(1,Math.max(0,u));
export const sm=(a:number,b:number,t:number)=>{const u=clamp((t-a)/(b-a));return u*u*u*(10+u*(-15+6*u));};
export const RELEASE_LOCAL=1.55,RELEASE_GLOBAL=7.55,BUZZER=7.9,SWISH_LOCAL=1.55,SWISH_GLOBAL=11.55,SCORE_GLOBAL=11.75;
export const jump=(t:number)=>140*Math.sin(Math.PI*clamp(t/4.4));
export function releaseLocalPoint(src:Point,t:number){
 const angle=.35*(1-sm(1.20,1.85,t)),w=(1-sm(100,160,src.y))*(1-sm(410,455,src.x));
 const a=add(p(366,99),rot(sub(src,p(366,99)),angle));
 return mix(src,a,w);
}
export const shotOrigin=(t:number)=>p(700-13*sm(.1,2.2,t),70-.05*jump(t));
export const releaseWorld=(src:Point,t:number)=>add(shotOrigin(t),mul(releaseLocalPoint(src,t),.37));
export function shotBall(t:number){
 if(t<=RELEASE_LOCAL)return releaseWorld(p(263,-40),t);
 const b=releaseWorld(p(263,-40),RELEASE_LOCAL),u=t-RELEASE_LOCAL;
 return add(b,p(-320*u,-125*u+110*u*u));
}
export function rimBall(t:number){
 const u=t/SWISH_LOCAL,a=p(1250,-170),b=p(1010,20),c=p(734,304);
 if(u<=1){return add(add(mul(a,(1-u)**2),mul(b,2*u*(1-u))),mul(c,u*u));}
 const d=t-SWISH_LOCAL;return p(734-35*(1-Math.exp(-5*d)),304+370*d+310*d*d);
}
export const netPulse=(t:number)=>{const age=t-SWISH_LOCAL;return age<0?0:Math.exp(-3.8*age)*Math.sin(12*age);};
export function gatherLocal(src:Point,t:number){
 const load=sm(.12,.65,t)*(1-.12*sm(.9,1.5,t)),v=rot(sub(src,p(550,900)),-.006*load),rigid=add(add(v,p(550,900)),p(-1.4*load,14.2*load));
 return mix(src,rigid,1-sm(900,1290,src.y));
}
