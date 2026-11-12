import {writeFileSync} from 'node:fs';
import {deformPoint,basePoint} from '../src/gatherMotion.ts';
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const upper=[{x:395,y:165},{x:470,y:200},{x:300,y:625},{x:390,y:608},{x:425,y:535},{x:330,y:550}];
const feet=[{x:250,y:1430},{x:360,y:1400},{x:650,y:1420},{x:720,y:1490},{x:600,y:1518}];
let rigidError=0,footMotion=0,maxStrain=0,minArea=Infinity,maxDisplacement=0;
const area=(a,b,c)=>(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
for(let i=0;i<=120;i++){
 const t=i/60;
 for(let a=0;a<upper.length;a++)for(let b=a+1;b<upper.length;b++)rigidError=Math.max(rigidError,Math.abs(distance(deformPoint(upper[a],t),deformPoint(upper[b],t))-distance(basePoint(upper[a]),basePoint(upper[b]))));
 for(const p of feet)footMotion=Math.max(footMotion,distance(deformPoint(p,t),basePoint(p)));
 for(let y=900;y<1290;y+=20)for(let x=200;x<760;x+=20){
  const a={x,y},b={x:x+20,y},c={x,y:y+20},da=deformPoint(a,t),db=deformPoint(b,t),dc=deformPoint(c,t);
  minArea=Math.min(minArea,area(da,db,dc));
  for(const [u,v] of [[a,b],[a,c],[b,c]])maxStrain=Math.max(maxStrain,Math.abs(distance(deformPoint(u,t),deformPoint(v,t))/distance(basePoint(u),basePoint(v))-1));
  maxDisplacement=Math.max(maxDisplacement,distance(da,basePoint(a)));
 }
}
const r={composition:'RukawaGatherPreview',durationSeconds:2,sourceImage:'public/art/correctives/rukawa-gather-anatomy-v1.png',method:'One coherent corrected drawing. Rigid upper-body movement, bounded lower-body displacement and fixed feet. No independent wrist, finger or elbow rotations.',upperBodyPairDistanceErrorPx:rigidError,plantedFootMotionPx:footMotion,maxLocalLengthChangeRatio:maxStrain,minimumGridTriangleSignedAreaPx2:minArea,maxSampledLowerBodyDisplacementPx:maxDisplacement,scope:'Small movement preview only. No complete jump shot, supporting-player motion or 20-second film.'};
writeFileSync('outputs/checks/corrected-gather-audit.json',JSON.stringify(r,null,2));console.log(JSON.stringify(r,null,2));
if(rigidError>.001||footMotion>.001||maxStrain>.09||minArea<=0||maxDisplacement>8)throw Error('Corrected-drawing deformation bounds exceeded');
