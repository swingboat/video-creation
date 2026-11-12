import {Painter,Asset,Color} from '../gpu';
import {p,Point,add,sub,mul,rot,mix,sm,clamp,jump,releaseWorld,shotBall,rimBall,netPulse,gatherLocal,SWISH_LOCAL,RELEASE_LOCAL,releaseLocalPoint,shotOrigin} from '../math';
import {supportBounds} from '../supportBounds';
export type Shot='opening'|'gather'|'hands'|'release'|'rim'|'reaction'|'hero';
const camera=(v:Point,s=1,dx=0,dy=0,c=p(640,360))=>add(add(c,mul(sub(v,c),s)),p(dx,dy));
function crowd(v:Point,t:number,top=65,bottom=355,amp=1){
 const w=sm(top,top+45,v.y)*(1-sm(bottom-28,bottom,v.y)),phase=v.x*.019+t*3.1;
 return p(v.x+w*amp*.45*Math.cos(phase*.7),v.y+w*amp*Math.sin(phase));
}
function court(g:Painter,t:number,map:(p:Point)=>Point=(v=>v),key:Asset='court',energy=1){
 const im=g.images[key];g.full(key,s=>{let v=crowd(s,t,65,355,1.35*energy);const flag=sm(80,115,s.y)*(1-sm(210,250,s.y));v.x+=2.3*energy*flag*Math.sin(s.x*.014+t*2.5);return map(p(1280-v.x/im.width*1280,v.y/im.height*720));},30);
}
function ball(g:Painter,where:Point,radius:number,t:number,map:(v:Point)=>Point=(v=>v)){
 g.image('ball',[1165,682,196,202],v=>map(add(where,rot(mul(sub(v,p(1263,783)),radius/95),t*1.7))),12);
}
function player(g:Painter,row:number,col:number,x:number,floor:number,scale:number,t:number,phase:number,cam:(v:Point)=>Point=(v=>v)){
 const b=supportBounds[row][col],ox=x-b.footX*scale,oy=floor-(b.y+b.h)*scale;
 const f=cam(p(x,floor));g.shadow(f.x,f.y+3,58*scale,9*scale,.16);
 g.image('support',[b.x,b.y,b.w,b.h],v=>{const u=(v.y-b.y)/b.h,w=1-sm(.62,.94,u);return cam(p(ox+v.x*scale+.45*w*Math.sin(t*2.3+phase),oy+v.y*scale+1.55*w*Math.sin(t*2.7+phase)));},8);
}
function gatherFigure(g:Painter,origin:Point,scale:number,t:number,cam:(v:Point)=>Point=(v=>v)){
 g.full('gather',v=>cam(add(origin,mul(gatherLocal(v,t),scale))),22);
}
function opening(g:Painter,t:number){
 const cam=(v:Point)=>camera(v,1+.014*sm(0,3,t),-2*sm(0,3,t),0,p(800,430));
 court(g,t,cam);
 player(g,2,0,225,563,.72,t,.7,cam);player(g,4,0,460,573,.66,t,2.2,cam);
 player(g,0,0,355,592,.74,t,1.8,cam);player(g,1,0,565,602,.73,t,3.6,cam);player(g,3,0,940,623,.84,t,4.8,cam);
 const s=cam(p(1180,636));g.shadow(s.x,s.y,130,13,.19);
 gatherFigure(g,p(1052,237),.26,t*.38,cam);
}
function gather(g:Painter,t:number){
 const im=g.images.court;g.image('court',[0,350,im.width,im.height-350],v=>p(1280-v.x/im.width*1280,(v.y-350)/(im.height-350)*720),36);
 gatherFigure(g,p(610,70),.5,t+.15);
}
function hands(g:Painter,t:number){
 court(g,t+4.2,v=>camera(v,1.34,0,-45));
 const s=1.33+.07*sm(0,1.8,t),origin=p(535-330*s,320-550*s-35*sm(0,1.8,t));
 g.full('gather',v=>add(origin,mul(v,s)),25);
}
function release(g:Painter,t:number){
 const j=jump(t),pan=j*.95;court(g,t+6,v=>camera(v,1.35,-60,-190+pan));
 const dphase=clamp((t-.4)/3.8),dj=105*Math.sin(Math.PI*dphase),defOrigin=p(350+17*sm(.4,2.1,t),180+pan-dj);
 g.full('defender',v=>add(defOrigin,mul(v,.30)),26);
 const b=shotBall(t);ball(g,b,.37*100,t+6);
 g.full('release',v=>{const a=releaseLocalPoint(v,t);return add(shotOrigin(t),mul(a,.37));},20);
}
function netNode(i:number,u:number,t:number,shift=0){
 const a=i*Math.PI*2/12+shift,pulse=netPulse(t),radius=190-95*u+18*pulse*u,y=304+222*u;
 return p(734+radius*Math.cos(a)-18*pulse*u,y+(54-35*u)*Math.sin(a)+32*pulse*u);
}
function drawNet(g:Painter,t:number,front:boolean){
 const color:Color=front?[.90,.88,.78,.94]:[.73,.73,.65,.45],rows=[0,.33,.66,1];
 for(let i=0;i<12;i++){
  const theta=(i+.5)*Math.PI*2/12,isFront=Math.sin(theta)>=0;if(front!==isFront)continue;
  for(let r=0;r<rows.length-1;r++){
   const sh=r%2?Math.PI/12:0,nh=(r+1)%2?Math.PI/12:0;
   g.line([netNode(i,rows[r],t,sh),netNode(i,rows[r+1],t,nh)],1.7,color);
   g.line([netNode(i+1,rows[r],t,sh),netNode(i,rows[r+1],t,nh)],1.3,color);
  }
 }
 for(const u of [.33,.66,1]){
  const pts:Point[]=[];const start=front?0:Math.PI;for(let i=0;i<=28;i++)pts.push(netNode((start+i*Math.PI/28)/(Math.PI*2/12),u,t));g.line(pts,1.5,color);
 }
}
function rim(g:Painter,t:number){
 const im=g.images.hoop;g.full('hoop',v=>{const w=sm(680,745,v.y)*(1-sm(905,940,v.y))*(1-sm(1380,1430,v.x));return p((v.x+.45*w*Math.sin(t*3+v.x*.02))/im.width*1280,(v.y+1.25*w*Math.sin(t*2.9+v.x*.018))/im.height*720);},28);
 drawNet(g,t,false);ball(g,rimBall(t),85,t+10);drawNet(g,t,true);
 const front:Point[]=[];for(let i=0;i<=64;i++){const a=i*Math.PI/64;front.push(p(734+190*Math.cos(a),304+54*Math.sin(a)));}
 g.line(front,10,[.33,.13,.055,1]);g.line(front,6,[.83,.32,.07,1]);
}
function victory(g:Painter,row:number,cx:number,top:number,scale:number,t:number,phase:number){
 const b=supportBounds[row][2],pivot=p(cx,top+b.h*scale*.62),angle=.012*Math.sin(t*3.8+phase),bob=-10*sm(0,.6,t)+3.5*Math.sin(t*4+phase);
 g.image('support',[b.x,b.y,b.w,b.h],v=>{const base=p(cx+(v.x-b.x-b.w/2)*scale,top+(v.y-b.y)*scale);return add(add(pivot,rot(sub(base,pivot),angle)),p(0,bob));},8);
}
function reaction(g:Painter,t:number){
 court(g,t+14,v=>camera(v,1.07,0,-20),'cheer',1.7);
 g.shadow(320,671,115,13,.17);g.shadow(650,658,105,12,.17);g.shadow(1000,675,120,13,.17);
 victory(g,0,320,170,1.6,t,.2);victory(g,1,650,210,1.6,t,2.1);victory(g,2,1000,140,1.6,t,3.7);
}
function hero(g:Painter,t:number){
 court(g,t+17,v=>camera(v,1.08,0,0), 'cheer',1.6);
 const s=1.8+.015*sm(0,3,t),ox=880-450*s,oy=0;
 g.full('gather',v=>p(ox+v.x*s,oy+v.y*s+Math.sin(t*2.1)*.7),24);
}
export function drawScene(g:Painter,shot:Shot,t:number){g.clear();({opening,gather,hands,release,rim,reaction,hero}[shot])(g,t);g.flush();}
