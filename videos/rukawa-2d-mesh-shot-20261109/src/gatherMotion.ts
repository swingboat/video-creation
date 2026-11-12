export type Point={x:number;y:number};
export const ART_SCALE=.35;
export const ART_ORIGIN={x:735,y:113};
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
export const smooth=(a:number,b:number,t:number)=>{const u=clamp((t-a)/(b-a));return u*u*u*(10+u*(-15+6*u));};
export const loadAt=(t:number)=>smooth(.2,.7,t)*(1-smooth(1.2,1.85,t));
export const basePoint=(p:Point):Point=>({x:ART_ORIGIN.x+p.x*ART_SCALE,y:ART_ORIGIN.y+p.y*ART_SCALE});
export function deformPoint(p:Point,t:number):Point{
 const b=basePoint(p),load=loadAt(t),pivot=basePoint({x:550,y:900}),angle=-.006*load,c=Math.cos(angle),s=Math.sin(angle),dx=b.x-pivot.x,dy=b.y-pivot.y;
 const upper={x:pivot.x+dx*c-dy*s-.5*load,y:pivot.y+dx*s+dy*c+5*load};
 const bodyWeight=1-smooth(900,1290,p.y);
 const kneeWeight=smooth(885,1010,p.y)*(1-smooth(1080,1290,p.y));
 // Every face, finger, palm and basketball pixel shares one rigid transform.
 const out={x:b.x+(upper.x-b.x)*bodyWeight-1.6*load*kneeWeight,y:b.y+(upper.y-b.y)*bodyWeight};
 // A subpixel fold movement is confined to the shorts, below the hands.
 const clothMask=smooth(690,725,p.y)*(1-smooth(840,875,p.y))*smooth(430,475,p.x)*(1-smooth(730,770,p.x));
 out.x+=.25*load*clothMask*Math.sin((p.y-690)/185*Math.PI);
 return out;
}
