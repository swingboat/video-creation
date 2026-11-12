import {writeFileSync} from 'node:fs';
import {pose,source,armMesh,legMesh,bodyMesh,p,sub,len,screen,RELEASE,TAKEOFF,LAND} from '../src/rig.ts';
const samples=[];let maxStep=0,maxContact=0,maxHeadError=0,maxHandError=0,heldGap=0;let previous=null;const baseHead=len(sub(pose(0).body(p(250,50)),pose(0).body(p(315,120))));
const keys=['shoulderNear','elbowNear','wristNear','shoulderFar','elbowFar','wristFar','kneeNear','kneeFar','nearAnkle','farAnkle'];
for(let f=0;f<180;f++){
 const t=f/60,r=pose(t),row={time:t,joints:{},meshPoints:{}};
 for(const k of keys){row.joints[k]=screen(r[k]);if(previous)maxStep=Math.max(maxStep,len(sub(row.joints[k],previous.joints[k])));}
 for(const side of ['near','far']){
  const s=side==='near'?source.nearLeg:source.farLeg,a=side==='near'?r.nearAnkle:r.farAnkle,fn=legMesh(side,r);
  maxContact=Math.max(maxContact,len(sub(fn(s.ankle),screen(a))));
  for(let i=0;i<12;i++){const v=p(s.bounds[0]+s.bounds[2]*.5,s.bounds[1]+s.bounds[3]*i/11);row.meshPoints[side+'leg'+i]=fn(v);}
  const ar=side==='near'?source.nearArm:source.farArm,afn=armMesh(side,r),wr=side==='near'?r.wristNear:r.wristFar;
  maxHandError=Math.max(maxHandError,len(sub(afn(ar.wrist),screen(wr))));
  for(let i=0;i<12;i++){const v=p(ar.bounds[0]+ar.bounds[2]*.5,ar.bounds[1]+ar.bounds[3]*i/11);row.meshPoints[side+'arm'+i]=afn(v);}
 }
 maxHeadError=Math.max(maxHeadError,Math.abs(len(sub(r.body(p(250,50)),r.body(p(315,120))))-baseHead));
 if(t<=RELEASE){const actual=armMesh('near',r)(p(source.nearArm.wrist.x,source.nearArm.wrist.y+24/.45));const target=screen(p(r.ball.x,r.ball.y+30));heldGap=Math.max(heldGap,len(sub(actual,target)));}
 if(previous)for(const k in row.meshPoints)maxStep=Math.max(maxStep,len(sub(row.meshPoints[k],previous.meshPoints[k])));
 samples.push(row);previous=row;
}
const report={samplingFps:60,durationSeconds:3,poseImageSwitches:0,sourceAtlas:'public/art/rukawa-layer-atlas-v1.png',method:'Connected 2D textured meshes; planar rigid dual-quaternion skinning; continuous ball/IK trajectories; fixed elbow chirality with a fully extended crossing for the shooting arm.',maxPointStepAt60fpsPx:maxStep,ankleMeshAnchorErrorPx:maxContact,wristMeshAnchorErrorPx:maxHandError,faceRigidityErrorPx:maxHeadError,heldPalmTargetErrorPx:heldGap,release:RELEASE,takeoff:TAKEOFF,land:LAND,scope:'This verifies local continuity and anchors, not natural acting or completion of the 20-second film.'};
writeFileSync('outputs/checks/rig-audit.json',JSON.stringify(report,null,2));writeFileSync('outputs/checks/pose-samples.json',JSON.stringify(samples));
console.log(JSON.stringify(report,null,2));if(maxContact>.8||maxHandError>.8||maxHeadError>.01||heldGap>.8||maxStep>35)throw Error('Rig continuity check failed');
