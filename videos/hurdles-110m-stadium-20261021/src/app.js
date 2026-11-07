import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { BokehPass } from 'three/examples/jsm/postprocessing/BokehPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { Sky } from 'three/examples/jsm/objects/Sky.js';
import assets from '../.cache/packed-assets.json';

const $=s=>document.querySelector(s),V=(x=0,y=0,z=0)=>new THREE.Vector3(x,y,z),Q=()=>new THREE.Quaternion(),clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp;
const smooth=(a,b,x)=>{let t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
const LANE=4.27, DURATION=22, FIRST=13.72, GAP=9.14, ACCEL=2*FIRST/9, SPEED=ACCEL*3, FINISH=5+(110-FIRST)/SPEED;
const hurdleTimes=Array.from({length:10},(_,i)=>5+i*GAP/SPEED);
const params=new URLSearchParams(location.search);let simTime=params.has('t')?Number(params.get('t')):3.6;
let playing=!params.has('paused')&&!matchMedia('(prefers-reduced-motion: reduce)').matches,speed=1,cameraMode=params.get('camera')||'cinematic',lastNow=0;
const errors=[];window.addEventListener('error',e=>errors.push(e.message));
let composer,bokeh;let renderer,scene,camera,controls,rig,bones={},rest={},restWorld={},axis={},sun,bodyRoot,headRoot,bodyMesh,headMesh,ready=false;
let lastFootContact=-1,audio=null,sound=false;
const state={time:0,distance:0,velocity:0,phase:'',hurdle:0,cleared:0,fps:0};
let seed=48;function rnd(){seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;}
function canvasTex(w,h,fn){const c=document.createElement('canvas');c.width=w;c.height=h;fn(c.getContext('2d'),w,h);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;}
function material(color,roughness=.75,extra={}){return new THREE.MeshStandardMaterial({color,roughness,...extra});}
function box(w,h,d,mat,x=0,y=0,z=0,parent=scene){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);parent.add(m);return m;}
function cylinder(a,b,r,mat,parent=scene,sides=10){const d=b.clone().sub(a);const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,d.length(),sides),mat);m.position.copy(a).add(b).multiplyScalar(.5);m.quaternion.setFromUnitVectors(V(0,1,0),d.normalize());parent.add(m);return m;}
function clipBelowY(geometry,y){
 const g=geometry.index?geometry.toNonIndexed():geometry.clone(),p=g.attributes.position,n=g.attributes.normal,uv=g.attributes.uv,out=[],ns=[],us=[];
 for(let i=0;i<p.count;i+=3){let poly=[];for(let k=0;k<3;k++)poly.push({p:V().fromBufferAttribute(p,i+k),n:V().fromBufferAttribute(n,i+k),uv:new THREE.Vector2().fromBufferAttribute(uv,i+k)});
  const result=[];for(let j=0;j<poly.length;j++){const a=poly[j],b=poly[(j+1)%poly.length],inside=a.p.y>=y,next=b.p.y>=y;if(inside)result.push(a);if(inside!==next){const u=(y-a.p.y)/(b.p.y-a.p.y);result.push({p:a.p.clone().lerp(b.p,u),n:a.n.clone().lerp(b.n,u).normalize(),uv:a.uv.clone().lerp(b.uv,u)});}}
  for(let j=1;j+1<result.length;j++)for(const v of [result[0],result[j],result[j+1]]){out.push(...v.p.toArray());ns.push(...v.n.toArray());us.push(v.uv.x,v.uv.y);}
 }
 const cut=new THREE.BufferGeometry();cut.setAttribute('position',new THREE.Float32BufferAttribute(out,3));cut.setAttribute('normal',new THREE.Float32BufferAttribute(ns,3));cut.setAttribute('uv',new THREE.Float32BufferAttribute(us,2));g.dispose();return cut;
}
function label(text,w=512,h=128,color='#eff2e5',bg=null,font='500 80px Arial'){return canvasTex(w,h,(c,W,H)=>{if(bg){c.fillStyle=bg;c.fillRect(0,0,W,H);}c.fillStyle=color;c.font=font;c.textAlign='center';c.textBaseline='middle';c.fillText(text,W/2,H/2);});}
function planeText(text,x,z,w,h,rotation=-Math.PI/2){let map=label(text);const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map,transparent:true,depthWrite:false}));m.rotation.x=rotation;m.position.set(x,.012,z);scene.add(m);return m;}
function capsulePath(radius){const pts=[];const n1=100,n2=70;for(let i=0;i<n1;i++)pts.push(V(110*i/n1,0,-36+radius));for(let i=0;i<n2;i++){let a=Math.PI/2-i/n2*Math.PI;pts.push(V(110+Math.cos(a)*radius,0,-36+Math.sin(a)*radius));}for(let i=0;i<n1;i++)pts.push(V(110*(1-i/n1),0,-36-radius));for(let i=0;i<n2;i++){let a=-Math.PI/2-i/n2*Math.PI;pts.push(V(Math.cos(a)*radius,0,-36+Math.sin(a)*radius));}return pts;}
function ribbon(r1,r2,y1,y2,mat,uvScale=1){const a=capsulePath(r1),b=capsulePath(r2),p=[],uv=[],idx=[];let length=0;for(let i=0;i<=a.length;i++){let j=i%a.length;if(i)length+=a[j].distanceTo(a[(i-1)%a.length]);p.push(a[j].x,y1,a[j].z,b[j].x,y2,b[j].z);uv.push(length/uvScale,0,length/uvScale,(r2-r1)/uvScale);if(i<a.length){let k=i*2;idx.push(k,k+1,k+2,k+1,k+3,k+2);}}const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();const m=new THREE.Mesh(g,mat);m.receiveShadow=true;scene.add(m);return m;}
function stadium(){
 const trackTexture=canvasTex(1024,1024,(c,w,h)=>{c.fillStyle='#ac5141';c.fillRect(0,0,w,h);for(let i=0;i<155000;i++){const v=Math.floor(90+rnd()*95);c.fillStyle=`rgba(${v+55},${v*.58},${v*.44},${.12+rnd()*.3})`;const k=.5+rnd()*1.5;c.fillRect(rnd()*w,rnd()*h,k,k);}});trackTexture.wrapS=trackTexture.wrapT=THREE.RepeatWrapping;
 const track=material('#ffffff',.94,{map:trackTexture,side:THREE.DoubleSide});ribbon(36,45.76,0,0,track,5);
 const white=material('#e7e2ce',.88,{side:THREE.DoubleSide});for(let i=0;i<=8;i++)ribbon(36+i*1.22-.021,36+i*1.22+.021,.006,.006,white,10);
 const grassTexture=canvasTex(1024,1024,(c,w,h)=>{c.fillStyle='#658354';c.fillRect(0,0,w,h);for(let i=0;i<14;i++){c.fillStyle=i%2?'rgba(175,196,132,.12)':'rgba(19,67,40,.08)';c.fillRect(i*w/14,0,w/14,h);}for(let i=0;i<110000;i++){c.fillStyle=rnd()>.5?'rgba(208,215,149,.14)':'rgba(36,74,35,.17)';c.fillRect(rnd()*w,rnd()*h,.8,2+rnd()*3);}});
 const ground=box(600,.08,600,material('#9da88b'),55,-.085,-36);ground.receiveShadow=true;
 const shape=new THREE.Shape();shape.moveTo(0,0);shape.lineTo(110,0);shape.absarc(110,-36,36,Math.PI/2,-Math.PI/2,true);shape.lineTo(0,-72);shape.absarc(0,-36,36,-Math.PI/2,-3*Math.PI/2,true);
 const grass=new THREE.Mesh(new THREE.ShapeGeometry(shape,70),material('#ffffff',.95,{map:grassTexture,side:THREE.DoubleSide}));grass.rotation.x=Math.PI/2; // Shape XY maps to XZ with positive original Y.
 grass.rotation.x=-Math.PI/2;grass.scale.y=-1;grass.position.y=-.008; // preserve negative-Z infield
 // Explicit grass capsule mesh avoids reflected UV and winding ambiguities.
 const fp=capsulePath(35.9),gp=[55,-.01,-36],gi=[],gu=[.5,.5];for(const p of fp){gp.push(p.x,-.01,p.z);gu.push((p.x+36)/182,(p.z+72)/72);}for(let i=0;i<fp.length;i++)gi.push(0,1+i,1+(i+1)%fp.length);const gg=new THREE.BufferGeometry();gg.setAttribute('position',new THREE.Float32BufferAttribute(gp,3));gg.setAttribute('uv',new THREE.Float32BufferAttribute(gu,2));gg.setIndex(gi);gg.computeVertexNormals();const gm=new THREE.Mesh(gg,material('#ffffff',.98,{map:grassTexture,side:THREE.DoubleSide}));scene.add(gm);gm.receiveShadow=true;
 const fieldLine=material('#d0d9ad',.9);for(const x of [5,105])box(.04,.007,62,fieldLine,x,.008,-36);for(const z of [-5,-67])box(100,.007,.04,fieldLine,55,.008,z);
 const circlePts=[];for(let i=0;i<=96;i++)circlePts.push(V(55+9.15*Math.cos(i/96*Math.PI*2),.015,-36+9.15*Math.sin(i/96*Math.PI*2)));scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(circlePts),new THREE.LineBasicMaterial({color:'#c2ccaa'})));
 box(.05,.012,62,fieldLine,55,.01,-36);
 // Finish, stagger marks, lane numbers, and start line.
 for(let lane=0;lane<8;lane++){planeText(String(lane+1),-2,.61+lane*1.22,1.0,.6);box(.055,.01,1.18,white,0,.01,.61+lane*1.22);for(let row=0;row<2;row++)for(let c=0;c<8;c++){const m=(row+c)%2?white:material('#242f2a');box(.16,.012,.147,m,110+row*.16,.012,lane*1.22+c*.147+.036);}}
 for(let i=0;i<10;i++)for(let lane=0;lane<8;lane++){box(.045,.012,.18,white,FIRST+i*GAP,.013,lane*1.22+.12);}
 planeText('110',106,LANE,1.8,.9);planeText('START',-3,LANE,1.8,.36);
 // Warm-up / start blocks.
 const metal=material('#73817e',.35,{metalness:.65}),block=material('#263d38',.8);box(.65,.055,.11,metal,-.6,.04,LANE);for(const off of [-.12,.13]){const m=box(.2,.11,.14,block,-.6+off,.085,LANE+off);m.rotation.z=-.25;}
 // Hurdles in the athlete lane, plus two neighbouring training lanes.
 const rail=material('#d9ded9',.3,{metalness:.75}),red=material('#ad4d34',.55),stripe=material('#252f2b',.65);
 const hurdleMap=canvasTex(1024,64,(c,w,h)=>{c.fillStyle='#f1efdf';c.fillRect(0,0,w,h);c.fillStyle='#26372e';for(let i=0;i<8;i+=2)c.fillRect(i*w/8,0,w/8,h);c.fillStyle='#f0f1df';c.font='bold 23px Arial';c.textAlign='center';c.fillText('TRACK / FIELD',w/2,45);});
 const barMat=material('#ffffff',.64,{map:hurdleMap});
 for(let lane of [3])for(let i=0;i<10;i++){
  const x=FIRST+i*GAP,z=lane*1.22+.61,g=new THREE.Group();g.position.set(x,0,z);scene.add(g);
  for(let dz of [-.53,.53]){box(.8,.04,.065,rail,.29,.027,dz,g);box(.055,1.0,.055,rail,0,.52,dz,g);box(.067,.34,.07,red,0,.2,dz,g);}
  const bar=box(.065,.075,1.18,barMat,0,1.067-.0375,0,g);bar.castShadow=true;
  if(lane===3){const tag=new THREE.Mesh(new THREE.PlaneGeometry(.18,.16),new THREE.MeshBasicMaterial({map:label(String(i+1),128,128,'#22342e','#e6e9dc','600 80px Arial')}));tag.position.set(.036,.78,.54);tag.rotation.y=Math.PI/2;g.add(tag);}
 }
 // A capsule stadium bowl, tiered seating, continuous canopy.
 const concrete=material('#a9b1a6',.9,{side:THREE.DoubleSide}),riser=material('#8e9c92',.9,{side:THREE.DoubleSide});
 const seatMatrices=[],colors=[],dummy=new THREE.Object3D();const palettes=['#536e64','#708b74','#bfc9b0','#d2d5bb','#a8b99e','#6d8270'];
 for(let row=0;row<22;row++){
  const r=49+row*.8,y=.7+row*.51;ribbon(r,r+.79,y,y,concrete,10);ribbon(r+.8,r+.81,y,y+.5,riser,10);
  const p=capsulePath(r+.35);let acc=0;
  for(let i=1;i<p.length;i++){const a=p[i-1],b=p[i],len=a.distanceTo(b);acc+=len;const count=Math.floor(len/.64);for(let k=0;k<count;k++){const pos=a.clone().lerp(b,(k+.5)/count);if(Math.abs(pos.x%24)<1.5)continue;dummy.position.set(pos.x,y+.13,pos.z);dummy.rotation.set(0,Math.atan2(b.z-a.z,b.x-a.x),0);dummy.scale.set(.48,.22,.4);dummy.updateMatrix();seatMatrices.push(dummy.matrix.clone());colors.push(new THREE.Color(palettes[Math.floor(rnd()*palettes.length)]));}}
 }
 const seats=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),material('#ffffff',.78),seatMatrices.length);seatMatrices.forEach((m,i)=>{seats.setMatrixAt(i,m);seats.setColorAt(i,colors[i]);});scene.add(seats);
 const roofmat=material('#dae0d8',.5,{metalness:.17,side:THREE.DoubleSide});ribbon(48,69,16.6,19.0,roofmat,10);ribbon(48,48.12,16.25,16.6,material('#f0f2e6',.6,{side:THREE.DoubleSide}),10);
 const roofp=capsulePath(67),edge=capsulePath(49);for(let i=0;i<roofp.length;i+=15){let a=roofp[i],b=edge[i];cylinder(V(a.x,0,a.z),V(a.x,18.7,a.z),.2,metal);cylinder(V(a.x,18.7,a.z),V(b.x,16.5,b.z),.1,metal);}
 for(const [x,z] of [[-28,-5],[-28,-68],[138,-5],[138,-68]]){cylinder(V(x,0,z),V(x,28,z),.2,metal);const lamps=new THREE.Group();lamps.position.set(x,28,z);scene.add(lamps);for(let k=0;k<8;k++)box(.62,.43,.22,material('#e8eacc',.4,{emissive:'#cbd9b1',emissiveIntensity:.5}),k%4*.75-1.15,Math.floor(k/4)*.55,0,lamps);}
 const boardTex=canvasTex(1536,512,(c,w,h)=>{c.fillStyle='#21362f';c.fillRect(0,0,w,h);c.fillStyle='#d9ed81';c.font='500 184px Arial';c.fillText('110 / HURDLES',65,245);c.fillStyle='#bdcdb6';c.font='31px Arial';c.fillText('TRAINING SESSION     •     LANE 04     •     TRACK / FIELD',73,370);c.strokeStyle='#536c55';c.strokeRect(28,28,w-56,h-56);});
 for(let x of [40,70])cylinder(V(x,10,-105),V(x,24,-105),.3,metal);box(35,12,.65,material('#ffffff',.6,{map:boardTex,emissiveMap:boardTex,emissive:'#ffffff',emissiveIntensity:.15}),55,22,-104);
 // Far skyline and flags add depth without competing with the athlete.
 const skyline=material('#92a3a0',.9);for(let i=0;i<32;i++){const x=-90+i*9;box(5+rnd()*5,8+rnd()*12,6,skyline,x,7,-145-rnd()*10);}
 const flagMat=material('#c95f47',.8,{side:THREE.DoubleSide});const flags=[];for(let i=0;i<9;i++){let x=-4+i*15;cylinder(V(x,17.5,-95),V(x,24,-95),.035,metal);const geo=new THREE.PlaneGeometry(1.8,.9,14,5);const flag=new THREE.Mesh(geo,flagMat);flag.position.set(x+.9,23.4,-95);scene.add(flag);flags.push(flag);}
 return {flags};
}
function trajectory(t){if(t<=2)return {d:0,v:0};if(t<=5){const u=t-2;return {d:.5*ACCEL*u*u,v:ACCEL*u};}if(t<=FINISH)return {d:FIRST+(t-5)*SPEED,v:SPEED};const u=Math.min(t-FINISH,4);return {d:110+SPEED*u-.5*(SPEED/4)*u*u,v:Math.max(0,SPEED*(1-u/4))};}
function nearestHurdle(t){let i=0;for(let j=1;j<10;j++)if(Math.abs(t-hurdleTimes[j])<Math.abs(t-hurdleTimes[i]))i=j;return {i,tau:t-hurdleTimes[i]};}
function curve(keys,t){if(t<=keys[0][0])return keys[0].slice(1);for(let i=1;i<keys.length;i++)if(t<=keys[i][0]){const a=keys[i-1],b=keys[i],u=smooth(a[0],b[0],t);return a.slice(1).map((v,k)=>lerp(v,b[k+1],u));}return keys.at(-1).slice(1);}
function aim(name,target){const bone=bones[name];if(!bone)return;rig.updateMatrixWorld(true);const from=bone.getWorldPosition(V());const dir=target.clone().sub(from).normalize();const parentQ=bone.parent.getWorldQuaternion(Q()).invert();dir.applyQuaternion(parentQ);const base=axis[name].clone().applyQuaternion(rest[name].q);bone.quaternion.copy(Q().setFromUnitVectors(base.normalize(),dir).multiply(rest[name].q));bone.updateWorldMatrix(false,true);}
function solveLimb(upper,lower,end,localTarget,pole){rig.updateMatrixWorld(true);const hip=bones[upper].getWorldPosition(V()),k0=bones[lower].getWorldPosition(V()),e0=bones[end].getWorldPosition(V());const l1=restWorld[upper].distanceTo(restWorld[lower]),l2=restWorld[lower].distanceTo(restWorld[end]);const goal=rig.localToWorld(localTarget.clone());let delta=goal.clone().sub(hip),d=clamp(delta.length(),.02,l1+l2-.0003),dir=delta.normalize();goal.copy(hip).addScaledVector(dir,d);const poleDir=pole.clone().transformDirection(rig.matrixWorld);const bend=poleDir.addScaledVector(dir,-poleDir.dot(dir)).normalize();const a=(l1*l1-l2*l2+d*d)/(2*d),h=Math.sqrt(Math.max(0,l1*l1-a*a));const knee=hip.clone().addScaledVector(dir,a).addScaledVector(bend,h);aim(upper,knee);aim(lower,goal);return {knee,goal};}
function orientFoot(name,angle){rig.updateMatrixWorld(true);const bone=bones[name],parentQ=bone.parent.getWorldQuaternion(Q()).invert(),rq=rig.getWorldQuaternion(Q());const desired=rq.multiply(Q().setFromAxisAngle(V(1,0,0),angle)).multiply(rest[name].worldQ);bone.quaternion.copy(parentQ.multiply(desired));bone.updateWorldMatrix(false,true);}
const contactEvents={L:[],R:[]};
for(let h=4;h<=hurdleTimes[9]+1;h+=GAP/SPEED){contactEvents.L.push(h+.18,h+.62);contactEvents.R.push(h+.40,h+.81);}
function runFoot(t,side,d){
 if(t>4.6&&t<hurdleTimes[9]+.7){
  const events=contactEvents[side];let prev=events[0],next=events[1];for(let i=0;i<events.length-1;i++)if(t>=events[i]){prev=events[i];next=events[i+1];}
  const contactX=trajectory(prev).d+.28,leave=prev+.105;let y=.085,z=contactX-d;
  if(t>leave){const u=clamp((t-leave)/(next-leave),0,1);z=lerp(contactX,trajectory(next).d+.28,u*u*(3-2*u))-d;y+=.48*Math.sin(Math.PI*u);}
  return {p:V(side==='L'?.105:-.105,y,z),phase:(t-prev)/(next-prev),contact:t<=leave};
 }

 const active=clamp((t-2)/.65,0,1),period=.64,offset=side==='L'?0:.5;
 const rate= t<5?lerp(.7,1.1,smooth(2,5,t)):1.05;
 const cycles=(t-2)*rate/period+offset;let phase=((cycles%1)+1)%1;
 const stance=.28;const legx=side==='L'?.105:-.105;
 // A planted foot stays at the world-space contact coordinate for the entire
 // support interval, rather than being translated with the character root.
 const cycleStart=t-phase*period/rate,contactTime=cycleStart;const contact=trajectory(contactTime).d+.36;
 let z,y;
 if(phase<stance){z=contact-d;y=.085;}
 else{const u=(phase-stance)/(1-stance),leave=trajectory(contactTime).d+.36,arrive=trajectory(contactTime+period/rate).d+.36;const eased=u*u*(3-2*u);z=lerp(leave,arrive,eased)-d;y=.085+Math.sin(Math.PI*u)*((t>FINISH?.52*Math.pow(clamp(trajectory(t).v/SPEED,0,1),1.3):.52*active)+.045);}
 z=lerp(side==='L'?.20:-.22,z,active);return {p:V(legx,y,z),phase,contact:phase<stance};
}
function pose(t){
 const {d,v}=trajectory(t),near=nearestHurdle(t),tau=near.tau;
 const cross =t>4.55&&t<hurdleTimes[9]+.34?Math.min(smooth(-.34,-.20,tau),1-smooth(.20,.34,tau)):0;
 const activity=smooth(1.7,2.7,t)*(1-smooth(FINISH+2.2,FINISH+4,t))*(t>FINISH?Math.pow(clamp(v/SPEED,0,1),.9):1);
 const stride=Math.sin((t-2)/.61*Math.PI*2);
 const jumpLift=cross*(.19+.055*Math.sin((tau+.2)/.4*Math.PI));
 const bob=activity*(.025+.025*Math.cos((t-2)/.305*Math.PI*2))*(1-cross);
 for(const n in bones){bones[n].quaternion.copy(rest[n].q);bones[n].position.copy(rest[n].p);}
 rig.position.set(d,jumpLift+bob,LANE);rig.rotation.y=Math.PI/2;
 // Lean around the pelvis, keeping root travel separate from articulation.
 const lean=lerp(.06,.18,activity)+cross*.39;
 const root=bones.root;root.quaternion.premultiply(Q().setFromAxisAngle(V(1,0,0),lean));
 for(const n in bones){const m=n.match(/^finger([2-5])-([123])\./);if(m)bones[n].rotateX([0,.65,.95,.5][Number(m[2])]);}
 rig.updateMatrixWorld(true);
 let lf=runFoot(t,'L',d),rf=runFoot(t,'R',d),footL=lf.p,footR=rf.p;
 if(cross>0){
  const lead=curve([[-.34,.105,.085,-.4],[-.21,.105,.78,.2],[-.07,.105,1.18,.88],[.02,.105,1.24,.86],[.10,.105,.87,.69],[.21,.105,.085,.32],[.34,.105,.085,-.6]],tau);
  const trail=curve([[-.34,-.105,.085,.15],[-.21,-.12,.085,-.63],[-.08,-.25,1.12,-.30],[.01,-.25,1.18,-.18],[.13,-.22,1.00,.25],[.25,-.13,.42,.58],[.34,-.105,.085,.35]],tau);
  if(tau>=.18&&tau<.29){lead[1]=.085;lead[2]=trajectory(hurdleTimes[near.i]+.18).d+.28-d;}
  footL.lerp(V(...lead),cross);footR.lerp(V(...trail),cross);
 }
 if(t<2){footL=V(.105,.085,.25);footR=V(-.105,.085,-.25);}
 if(t>FINISH+4){footL=V(.105,.085,.08);footR=V(-.105,.085,-.08);}
 // Targets are in the moving root coordinate system. Remove pelvis lift from
 // planted-foot targets; flight paths remain absolute over the track surface.
 footL.y-=rig.position.y;footR.y-=rig.position.y;
 solveLimb('upperleg01.L','lowerleg01.L','foot.L',footL,V(0,0,1));
 solveLimb('upperleg01.R','lowerleg01.R','foot.R',footR,cross>.2?V(-1,.08,.08):V(0,0,1));
 orientFoot('foot.L',cross>.25?-.04:lf.contact?0:.18*Math.sin(lf.phase*Math.PI*2));
 orientFoot('foot.R',cross>.25?.45:rf.contact?0:.18*Math.sin(rf.phase*Math.PI*2));
 const armSwing=Math.sin((t-2)/.61*Math.PI*2),handL=V(.285,1.22+.07*armSwing,.13+.35*armSwing*activity),handR=V(-.285,1.22-.07*armSwing,.13-.35*armSwing*activity);
 if(t>FINISH){const relax=smooth(FINISH,FINISH+3,t);handL.y-=.22*relax;handR.y-=.22*relax;}
 handL.lerp(V(.29,1.22,-.28),cross);handR.lerp(V(-.24,1.39,.54),cross);
 solveLimb('upperarm01.L','lowerarm01.L','wrist.L',handL,V(.25,0,-1));solveLimb('upperarm01.R','lowerarm01.R','wrist.R',handR,V(-.25,0,-1));
 for(const side of ['L','R']){rig.updateMatrixWorld(true);const hand=bones['wrist.'+side].getWorldPosition(V());const fore=bones['lowerarm01.'+side].getWorldPosition(V());const dir=hand.clone().sub(fore).normalize();aim('wrist.'+side,hand.clone().addScaledVector(dir,.1));}
 // Neck counter-rotation keeps gaze down the lane as the torso inclines.
 if(bones.head){rig.updateMatrixWorld(true);const head=bones.head;const correction=Q().setFromAxisAngle(V(1,0,0),-lean*.47);const parentInv=head.parent.getWorldQuaternion(Q()).invert();const own=head.getWorldQuaternion(Q());const axisWorld=V(1,0,0).transformDirection(rig.matrixWorld);const corrected=Q().setFromAxisAngle(axisWorld,-lean*.47).multiply(own);head.quaternion.copy(parentInv.multiply(corrected));}
 rig.updateMatrixWorld(true);
 state.time=t;state.distance=d;state.velocity=v;state.hurdle=clamp(near.i+1,1,10);state.cleared=hurdleTimes.filter(ht=>t>ht+.20).length;
 state.phase=t<2?'准备起跑':t<4.6?'起跑加速':t>FINISH+3.9?'训练完成':t>FINISH?'冲线减速':cross>.15?tau<-.13?'提膝起跨':tau<.10?'腾空越栏':'下压落地':'栏间三步';
 // Audio contact is event-driven and does not alter simulation state.
 const contactIndex=Math.floor((t-2)/.305);if(sound&&playing&&contactIndex!==lastFootContact&&v>.8&&cross<.2){footstep(v/SPEED);lastFootContact=contactIndex;}
}
function updateCamera(){const d=state.distance;let target=V(d+.3,1.10,LANE),pos;
 camera.fov=40;
 if(cameraMode==='cinematic'){const drift=Math.sin(simTime*.16)*.8;pos=V(d+3.6+drift,2.05,LANE+6.5);target=V(d+.24,1.05,LANE-.1);camera.fov=37;}
 else if(cameraMode==='side'){pos=V(d+.08,1.72,LANE+9);target=V(d+.2,1.12,LANE);camera.fov=32;}
 else if(cameraMode==='portrait'){pos=V(d+1.9,1.8,LANE+2.7);target=V(d+.1,1.47,LANE);camera.fov=34;}
 else if(cameraMode==='chase'){pos=V(d-5.8,2.3,LANE+2.9);target=V(d+2.8,1.1,LANE);camera.fov=43;}
 else if(cameraMode==='wide'){pos=V(66,62,91);target=V(55,0,-27);camera.fov=49;}
 else if(cameraMode==='orbit'){controls.update();return;}
 if(innerWidth<600&&cameraMode==='cinematic'){pos=V(d+5.1,2.6,LANE+10);target=V(d,1.15,LANE);camera.fov=38;}
 camera.position.copy(pos);camera.lookAt(target);camera.updateProjectionMatrix();controls.target.copy(target);
}
function updateUI(){
 $('#clock').innerHTML=`${state.time.toFixed(2).padStart(5,'0')}<small>s</small>`;$('#distance').textContent=Math.min(110,state.distance).toFixed(1);$('#velocity').textContent=state.velocity.toFixed(1);$('#phase').textContent=state.phase;$('#hurdle-label').textContent=`${String(state.hurdle).padStart(2,'0')} / 10`;
 $('#seek').value=simTime;$('#seek').style.setProperty('--progress',`${simTime/DURATION*100}%`);
 $('#timeline-status').textContent=state.time<FINISH?`${state.phase} · ${state.cleared} / 10 栏`:`${state.phase} · 110 m 完成`;
 [...$('#hurdle-dots').children].forEach((e,i)=>{e.className=i<state.cleared?'passed':i===state.hurdle-1?'current':'';});
 $('#play').setAttribute('aria-label',playing?'暂停训练':'播放训练');$('#play-path').setAttribute('d',playing?'M8 5v14M16 5v14':'M8 4v16l12-8Z');
 document.querySelectorAll('[data-speed]').forEach(b=>b.classList.toggle('active',Number(b.dataset.speed)===speed));document.querySelectorAll('[data-camera]').forEach(b=>b.classList.toggle('active',b.dataset.camera===cameraMode));
 $('.session').firstChild.classList.toggle('paused',!playing);
}
function frameAt(t){if(!ready)return;simTime=clamp(t,0,DURATION);pose(simTime);sun.position.set(state.distance-11,22,LANE+15);sun.target.position.set(state.distance,0,LANE);sun.target.updateMatrixWorld();
 scene.userData.flags.forEach((flag,i)=>{const p=flag.geometry.attributes.position;for(let j=0;j<p.count;j++){let x=p.getX(j);p.setZ(j,.10*Math.sin(x*4+simTime*2.4+i)+.03*Math.cos(x*10+simTime*4));}p.needsUpdate=true;flag.geometry.computeVertexNormals();});updateCamera();updateUI();if(composer){bokeh.enabled=cameraMode!=='wide'&&innerWidth>600;bokeh.uniforms.focus.value=camera.position.distanceTo(controls.target);bokeh.uniforms.aperture.value=cameraMode==='portrait'?.00018:.00011;bokeh.uniforms.maxblur.value=cameraMode==='portrait'?.008:.006;composer.render();}else renderer.render(scene,camera);}
function animate(now){requestAnimationFrame(animate);const dt=lastNow?Math.min((now-lastNow)/1000,.055):0;lastNow=now;if(ready){if(playing&&document.visibilityState!=='hidden'){simTime+=dt*speed;if(simTime>DURATION)simTime=0;}frameAt(simTime);}}
function setCamera(mode){cameraMode=mode;controls.enabled=mode==='orbit';if(controls.enabled){playing=false;controls.target.set(state.distance,1.1,LANE);camera.position.set(state.distance+3,2.2,LANE+5.5);controls.update();}frameAt(simTime);}
function setPlaying(value){playing=Boolean(value);updateUI();}
function footstep(intensity=1){if(!audio)return;const ctx=audio.ctx,osc=ctx.createOscillator(),g=ctx.createGain();osc.type='sine';osc.frequency.setValueAtTime(135,ctx.currentTime);osc.frequency.exponentialRampToValueAtTime(48,ctx.currentTime+.07);g.gain.setValueAtTime(.08*intensity,ctx.currentTime);g.gain.exponentialRampToValueAtTime(.0001,ctx.currentTime+.085);osc.connect(g);g.connect(audio.master);osc.start();osc.stop(ctx.currentTime+.09);}
function toggleSound(){if(!audio){const ctx=new AudioContext(),master=ctx.createGain();master.gain.value=.35;master.connect(ctx.destination);const buffer=ctx.createBuffer(1,ctx.sampleRate*4,ctx.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=(rnd()-.5)*.13;const source=ctx.createBufferSource();source.buffer=buffer;source.loop=true;const filt=ctx.createBiquadFilter();filt.type='lowpass';filt.frequency.value=550;source.connect(filt);filt.connect(master);source.start();audio={ctx,master};}sound=!sound;audio.ctx.resume();audio.master.gain.setTargetAtTime(sound?.28:0,audio.ctx.currentTime,.15);$('#sound').setAttribute('aria-label',sound?'关闭环境声音':'开启环境声音');$('#sound').setAttribute('aria-pressed',String(sound));$('#sound-path').setAttribute('d',sound?'M11 4 5 9H2v6h3l6 5ZM16 8q6 4 0 8M19 4q12 8 0 16':'M11 4 5 9H2v6h3l6 5ZM16 9l6 6m0-6-6 6');}
function controlsSetup(){for(let i=0;i<10;i++)$('#hurdle-dots').appendChild(document.createElement('i'));$('#play').onclick=()=>setPlaying(!playing);$('#restart').onclick=()=>{simTime=0;playing=true;frameAt(0);};$('#seek').oninput=e=>{playing=false;frameAt(Number(e.target.value));};document.querySelectorAll('[data-speed]').forEach(b=>b.onclick=()=>{speed=Number(b.dataset.speed);updateUI();});document.querySelectorAll('[data-camera]').forEach(b=>b.onclick=()=>setCamera(b.dataset.camera));$('#credits-open').onclick=()=>$('#credits').showModal();$('#credits-close').onclick=()=>$('#credits').close();$('#sound').onclick=toggleSound;$('#hide').onclick=()=>document.body.classList.add('clean');$('#show').onclick=()=>document.body.classList.remove('clean');$('.brand').onclick=e=>{e.preventDefault();simTime=0;playing=true;};window.addEventListener('keydown',e=>{if(e.target instanceof HTMLInputElement)return;if(e.code==='Space'){e.preventDefault();setPlaying(!playing);}if(e.key.toLowerCase()==='r'){simTime=0;playing=true;}if(e.key.toLowerCase()==='h')document.body.classList.toggle('clean');if(e.key.toLowerCase()==='m')toggleSound();if(['1','2','3','4','5'].includes(e.key))setCamera(['cinematic','side','chase','wide','orbit'][Number(e.key)-1]);});}
async function init(){
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.91;$('#scene').appendChild(renderer.domElement);
 scene=new THREE.Scene();scene.background=new THREE.Color('#c7d8d7');scene.fog=new THREE.FogExp2('#c8d6d2',.0033);camera=new THREE.PerspectiveCamera(37,innerWidth/innerHeight,.035,650);
 const sky=new Sky();sky.scale.setScalar(1000);const uniforms=sky.material.uniforms;uniforms.turbidity.value=4.5;uniforms.rayleigh.value=1.1;uniforms.mieCoefficient.value=.006;uniforms.mieDirectionalG.value=.82;uniforms.sunPosition.value.set(-.45,.52,.68);scene.add(sky);const envScene=new THREE.Scene();envScene.add(sky.clone());const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(envScene,.04).texture;scene.environmentIntensity=.5;pmrem.dispose();
 scene.add(new THREE.HemisphereLight('#edf5e9','#9c8c70',1.15));sun=new THREE.DirectionalLight('#fff0ce',2.7);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-9,right:9,top:10,bottom:-10,near:1,far:65});sun.shadow.bias=-.00018;sun.shadow.normalBias=.006;sun.shadow.radius=3;scene.add(sun,sun.target);
 const fill=new THREE.DirectionalLight('#d6e5f3',.55);fill.position.set(40,15,-30);scene.add(fill);
 $('#load-progress').style.width='25%';scene.userData=stadium();controls=new OrbitControls(camera,renderer.domElement);controls.enabled=false;controls.enableDamping=true;controls.dampingFactor=.08;controls.minDistance=1.3;controls.maxDistance=180;controls.maxPolarAngle=Math.PI*.495;controls.minPolarAngle=.15;
 $('#load-progress').style.width='45%';$('#load-text').textContent='正在准备连续人体网格与扫描面部…';
 const loader=new GLTFLoader();const body=await loader.loadAsync(assets.body);
 rig=new THREE.Group();scene.add(rig);bodyRoot=body.scene;rig.add(bodyRoot);rig.updateMatrixWorld(true);
 const skinNoise=canvasTex(512,512,(c,w,h)=>{const im=c.createImageData(w,h);for(let i=0;i<im.data.length;i+=4){const v=130+rnd()*65;im.data[i]=im.data[i+1]=im.data[i+2]=v;im.data[i+3]=255;}c.putImageData(im,0,0);});skinNoise.colorSpace=THREE.NoColorSpace;skinNoise.wrapS=skinNoise.wrapT=THREE.RepeatWrapping;skinNoise.repeat.set(4,4);
 const weave=canvasTex(128,128,(c,w,h)=>{c.fillStyle='#aaa';c.fillRect(0,0,w,h);for(let i=0;i<w;i+=4){c.fillStyle='#777';c.fillRect(i,0,1,h);c.fillStyle='#ccc';c.fillRect(0,i,w,1);}});weave.colorSpace=THREE.NoColorSpace;weave.wrapS=weave.wrapT=THREE.RepeatWrapping;weave.repeat.set(12,12);
 bodyRoot.traverse(o=>{if(o.isBone)bones[o.name.replace(/([LR])$/,'.$1')]=o;if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;const mats=Array.isArray(o.material)?o.material:[o.material];for(const m of mats){if(m.name==='AthleteSkin'){m.color.set('#ffffff');m.roughness=.55;m.metalness=0;m.bumpMap=skinNoise;m.bumpScale=.00065;m.onBeforeCompile=shader=>{
 shader.uniforms.singletColor={value:new THREE.Color('#bd412a')};shader.uniforms.shortsColor={value:new THREE.Color('#202e2b')};
 shader.vertexShader='varying vec3 vAnatomy;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvAnatomy = position;');
 shader.fragmentShader='varying vec3 vAnatomy; uniform vec3 singletColor; uniform vec3 shortsColor;\n'+shader.fragmentShader;
 shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
 float ax=abs(vAnatomy.x);float yy=vAnatomy.y;
 float collar=1.495+0.091*smoothstep(0.055,0.115,ax);
 float armhole=0.235-0.073*smoothstep(1.34,1.54,yy);
 float singlet=step(1.094,yy)*(1.0-step(collar,yy))*(1.0-step(armhole,ax));
 float shorts=step(0.795,yy)*(1.0-step(1.096,yy))*(1.0-step(0.34,ax));
 diffuseColor.rgb=mix(diffuseColor.rgb,singletColor,singlet);diffuseColor.rgb=mix(diffuseColor.rgb,shortsColor,shorts);
 float trim=singlet*(1.0-smoothstep(0.001,0.005,min(collar-yy,armhole-ax)));
 diffuseColor.rgb=mix(diffuseColor.rgb,vec3(0.12,0.15,0.12),trim*0.6);
 `);
};m.customProgramCacheKey=()=> 'athlete-fabric-v1';}if(m.name==='RacingSinglet'){m.color.set('#c7462c');m.roughness=.86;m.bumpMap=weave;m.bumpScale=.00065;}if(m.name==='CompressionShorts'){m.color.set('#25322f');m.roughness=.83;m.bumpMap=weave;m.bumpScale=.0005;}if(m.name==='AthleteHair'){m.color.set('#b9aca0');m.roughness=.82;m.side=THREE.DoubleSide;m.alphaTest=.3;m.transparent=false;m.depthWrite=true;m.alphaToCoverage=true;}if(m.name==='AthleteEyes'){m.color.set('#ffffff');m.roughness=.18;m.envMapIntensity=.7;m.alphaTest=.12;m.transparent=false;m.depthWrite=true;}if(m.name==='TrackShoes'){m.color.set('#ffffff');m.roughness=.72;}}}});
 rig.updateMatrixWorld(true);
 for(const [n,b]of Object.entries(bones)){restWorld[n]=b.getWorldPosition(V());rest[n]={q:b.quaternion.clone(),p:b.position.clone(),worldQ:b.getWorldQuaternion(Q())};}
 const ends={};for(const side of ['L','R']){ends['upperleg01.'+side]='lowerleg01.'+side;ends['lowerleg01.'+side]='foot.'+side;ends['upperarm01.'+side]='lowerarm01.'+side;ends['lowerarm01.'+side]='wrist.'+side;ends['wrist.'+side]='finger3-1.'+side;}
 for(const [n,end]of Object.entries(ends)){axis[n]=restWorld[end].clone().sub(restWorld[n]).normalize().applyQuaternion(rest[n].worldQ.clone().invert());}
 // A race bib and singlet piping are attached to the chest, following its rig.
 const bibMap=canvasTex(512,512,(c,w,h)=>{c.fillStyle='#ebe9d8';c.fillRect(0,0,w,h);c.fillStyle='#d35a38';c.fillRect(0,0,w,62);c.fillStyle='#ffffff';c.font='23px Arial';c.textAlign='center';c.fillText('TRACK / FIELD',w/2,41);c.fillStyle='#25362e';c.font='600 260px Arial';c.fillText('04',w/2,340);c.font='23px Arial';c.fillText('HURDLES • 110 M',w/2,450);});
 const bib=new THREE.Mesh(new THREE.PlaneGeometry(.188,.185),material('#ffffff',.85,{map:bibMap,side:THREE.DoubleSide}));bib.position.set(0,1.36,.153);rig.add(bib);rig.updateMatrixWorld(true);(bones.spine02||bones.spine01).attach(bib);
 composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));bokeh=new BokehPass(scene,camera,{focus:7,aperture:.00011,maxblur:.006});composer.addPass(bokeh);composer.addPass(new OutputPass());
 controlsSetup();$('#load-progress').style.width='90%';
 window.addEventListener('resize',()=>{renderer.setSize(innerWidth,innerHeight);composer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();frameAt(simTime);});
 ready=true;if(params.has('clean'))document.body.classList.add('clean');setCamera(cameraMode);frameAt(simTime);await renderer.compileAsync(scene,camera);$('#load-progress').style.width='100%';document.body.classList.add('loaded');
 window.hurdleApp={ready:true,duration:DURATION,finishTime:FINISH,renderAt:frameAt,setTime:frameAt,setPlaying,setCamera,getState:()=>({...state,playing,speed,camera:cameraMode,errors:[...errors],bones:Object.keys(bones).length}),getRenderer:()=>renderer,getScene:()=>scene,getRig:()=>rig,getCamera:()=>camera,getControls:()=>controls,getBones:()=>bones};
 window.dispatchEvent(new Event('hurdle-ready'));if(params.has('render'))$('#show').remove();else requestAnimationFrame(animate);
}
init().catch(e=>{console.error(e);$('#error').hidden=false;$('#error').textContent='场景加载失败：'+e.message+'\n请确认浏览器支持 WebGL 2。';$('#load-text').textContent=e.message;});
