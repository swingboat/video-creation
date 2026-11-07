import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {SSAOPass} from 'three/addons/postprocessing/SSAOPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {Game,PLATFORMS,SEALS} from './game.ts';

function rng(seed:number){return ()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296;};}
function texture(size:number,draw:(c:CanvasRenderingContext2D)=>void){const canvas=document.createElement('canvas');canvas.width=size;canvas.height=size;draw(canvas.getContext('2d')!);const map=new T.CanvasTexture(canvas);map.colorSpace=T.SRGBColorSpace;return map;}

export class World {
  readonly renderer:T.WebGLRenderer;
  readonly scene=new T.Scene();
  readonly camera=new T.PerspectiveCamera(43,1,.1,250);
  readonly character=new T.Group();
  readonly ready:Promise<void>;
  private environment=new T.Group();
  private mixer:T.AnimationMixer|null=null;
  private actions=new Map<string,T.AnimationAction>();
  private currentMotion='';
  private previousGrounded=true;
  private landTime=0;
  private sealObjects:T.Group[]=[];
  private clouds:T.Sprite[]=[];
  private motes:T.Points;
  private shadow:T.Mesh;
  private sun:T.DirectionalLight;
  private composer:EffectComposer;
  private ao:SSAOPass;
  private target=new T.Vector3(-2,1.3,-1);
  private wanted=new T.Vector3();
  private cameraPosition=new T.Vector3();
  private yaw=.34;
  private pitch=.34;
  private distance=23;
  private pointer={down:false,x:0,y:0};
  private width=1;private height=1;private frames=0;private time=0;
  private loaded=false;private heroFaces=0;private usingAO=true;
  private reduceMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
  private cameraRay=new T.Raycaster();
  private blockers:T.Object3D[]=[];
  private quality='desktop';

  constructor(private host:HTMLElement){
    this.renderer=new T.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
    this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));
    this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=T.PCFShadowMap;
    this.renderer.outputColorSpace=T.SRGBColorSpace;this.renderer.toneMapping=T.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.02;
    this.renderer.info.autoReset=false;
    const canvas=this.renderer.domElement;canvas.tabIndex=0;
    canvas.setAttribute('role','img');canvas.setAttribute('aria-label','可行走的水墨山崖。W A S D 移动，空格跳跃，拖动旋转视角。');host.append(canvas);
    this.scene.background=texture(256,c=>{const g=c.createLinearGradient(0,0,0,256);g.addColorStop(0,'#b79b80');g.addColorStop(.48,'#c2b8a2');g.addColorStop(1,'#d3cdbb');c.fillStyle=g;c.fillRect(0,0,256,256);});
    this.scene.fog=new T.FogExp2(0xc6c0ad,.0125);
    this.scene.add(new T.HemisphereLight(0xe8e0c9,0x36463b,1.25));
    this.sun=new T.DirectionalLight(0xffe4bb,3.1);this.sun.position.set(-12,25,18);this.sun.target.position.set(10,0,-5);
    this.sun.castShadow=true;this.sun.shadow.mapSize.set(2048,2048);
    Object.assign(this.sun.shadow.camera,{left:-27,right:33,top:24,bottom:-22,near:1,far:100});
    this.sun.shadow.normalBias=.022;this.sun.shadow.bias=-.00009;this.sun.shadow.radius=1.4;
    this.scene.add(this.sun,this.sun.target);
    const bounce=new T.DirectionalLight(0xaab9b5,.34);bounce.position.set(15,8,-15);this.scene.add(bounce);
    this.composer=new EffectComposer(this.renderer);this.composer.addPass(new RenderPass(this.scene,this.camera));
    this.ao=new SSAOPass(this.scene,this.camera,512,512,16);this.ao.kernelRadius=5;this.ao.minDistance=.0009;this.ao.maxDistance=.022;
    this.composer.addPass(this.ao);this.composer.addPass(new OutputPass());
    this.scene.add(this.environment,this.character);
    this.background();this.seals();
    const map=texture(128,c=>{const g=c.createRadialGradient(64,64,3,64,64,62);g.addColorStop(0,'rgba(12,20,15,.5)');g.addColorStop(.45,'rgba(12,20,15,.18)');g.addColorStop(1,'rgba(12,20,15,0)');c.fillStyle=g;c.fillRect(0,0,128,128);});
    this.shadow=new T.Mesh(new T.PlaneGeometry(1.05,.8),new T.MeshBasicMaterial({map,transparent:true,depthWrite:false}));this.shadow.rotation.x=-Math.PI/2;this.scene.add(this.shadow);
    const random=rng(515);const positions=[];for(let i=0;i<100;i++)positions.push(-5+random()*48,.4+random()*7,-8+random()*14);
    const particleGeo=new T.BufferGeometry();particleGeo.setAttribute('position',new T.Float32BufferAttribute(positions,3));
    const particleMap=texture(32,c=>{const gr=c.createRadialGradient(16,16,0,16,16,16);gr.addColorStop(0,'rgba(235,221,179,.8)');gr.addColorStop(1,'rgba(235,221,179,0)');c.fillStyle=gr;c.fillRect(0,0,32,32);});
    this.motes=new T.Points(particleGeo,new T.PointsMaterial({color:0xe0d4b1,size:.055,map:particleMap,transparent:true,opacity:.42,depthWrite:false}));this.scene.add(this.motes);
    this.listen();this.resize();
    const manager=new T.LoadingManager();manager.onProgress=(_,loaded,total)=>window.dispatchEvent(new CustomEvent('sumi:loading',{detail:{loaded,total}}));
    const loader=new GLTFLoader(manager);
    this.ready=Promise.all([
      loader.loadAsync('/models/mountain-environment-v2.glb'),
      loader.loadAsync('/models/traveler-v2.glb'),
    ]).then(([env,hero])=>{
      const anisotropy=Math.min(8,this.renderer.capabilities.getMaxAnisotropy());
      env.scene.traverse(object=>{
        if(!(object instanceof T.Mesh))return;
        const mats=Array.isArray(object.material)?object.material:[object.material];
        object.castShadow=!mats.some(m=>/Lichen|InkCrevices|HempRope/.test(m.name));object.receiveShadow=true;
        mats.forEach(m=>{
          if(!(m instanceof T.MeshStandardMaterial))return;
          m.roughness=1;
          if(m.map){m.map.anisotropy=anisotropy;m.map.wrapS=m.map.wrapT=T.RepeatWrapping;}
          if(/MountainLimestone|StoneEdge/.test(m.name)&&m.map){
            m.bumpMap=m.map.clone();m.bumpMap.colorSpace=T.NoColorSpace;m.bumpScale=.055;
            m.color.setHex(0xe4dfce);this.blockers.push(object);
          }
          if(/PineNeedle/.test(m.name))m.side=T.DoubleSide;
          if(/PineFoliageCards/.test(m.name)){m.alphaTest=.62;m.transparent=false;m.depthWrite=true;m.side=T.DoubleSide;m.alphaToCoverage=false;m.needsUpdate=true;}
        });
      });
      this.environment.add(env.scene);
      hero.scene.traverse(object=>{
        if(!(object instanceof T.Mesh))return;
        object.castShadow=true;object.receiveShadow=true;
        this.heroFaces+=(object.geometry.index?.count??object.geometry.getAttribute('position').count)/3;
        const mats=Array.isArray(object.material)?object.material:[object.material];
        mats.forEach(m=>{if(m instanceof T.MeshStandardMaterial){m.roughness=Math.max(.75,m.roughness);if(m.map)m.map.anisotropy=anisotropy;}});
        object.frustumCulled=false;
      });
      this.character.add(hero.scene);this.mixer=new T.AnimationMixer(hero.scene);
      hero.animations.forEach(clip=>this.actions.set(clip.name,this.mixer!.clipAction(clip)));
      this.motion('Idle');this.loaded=true;
      window.dispatchEvent(new CustomEvent('sumi:ready',{detail:{animations:[...this.actions.keys()],heroFaces:this.heroFaces}}));
    });
  }
  private motion(name:string){
    if(name===this.currentMotion)return;
    const next=this.actions.get(name)??this.actions.get('Idle');if(!next)return;
    const previous=this.actions.get(this.currentMotion);previous?.fadeOut(.13);
    next.reset();next.enabled=true;next.setEffectiveWeight(1);next.setEffectiveTimeScale(1);
    if(['Jump','Land'].includes(name)){next.setLoop(T.LoopOnce,1);next.clampWhenFinished=true;}else next.setLoop(T.LoopRepeat,Infinity);
    next.fadeIn(.13).play();this.currentMotion=name;
  }
  private seals(){
    const gold=new T.MeshStandardMaterial({color:0xb69757,roughness:.6,metalness:.25});
    SEALS.forEach((seal,index)=>{
      const group=new T.Group();group.position.set(seal.x,seal.y+1,seal.z);this.scene.add(group);
      const ring=new T.Mesh(new T.TorusGeometry(.25,.016,8,48),gold);group.add(ring);
      const center=new T.Mesh(new T.BoxGeometry(.12,.23,.045),new T.MeshStandardMaterial({color:0xa74227,emissive:0x581d08,emissiveIntensity:.3,roughness:1}));center.rotation.z=.1;group.add(center);
      const glowMap=texture(64,c=>{const gr=c.createRadialGradient(32,32,0,32,32,32);gr.addColorStop(0,'rgba(235,187,99,.75)');gr.addColorStop(.3,'rgba(221,166,71,.14)');gr.addColorStop(1,'rgba(221,166,71,0)');c.fillStyle=gr;c.fillRect(0,0,64,64);});
      const glow=new T.Sprite(new T.SpriteMaterial({map:glowMap,transparent:true,depthWrite:false}));glow.scale.setScalar(1.7);group.add(glow);this.sealObjects[index]=group;
    });
  }
  private background(){
    const random=rng(665);
    const material=new T.MeshStandardMaterial({color:0x89917f,roughness:1,flatShading:true});
    for(let i=0;i<25;i++){
      const height=18+random()*24;const geo=new T.ConeGeometry(5+random()*8,height,9,6);
      const pos=geo.getAttribute('position');for(let j=0;j<pos.count;j++){const x=pos.getX(j),y=pos.getY(j);pos.setX(j,x+Math.sin(y*.27+i)*1.3);pos.setZ(j,pos.getZ(j)+Math.sin(y*.33+i)*.8);}geo.computeVertexNormals();
      const mountain=new T.Mesh(geo,material);mountain.position.set(-75+i*6,-14+height*.12,-68-random()*35);mountain.scale.z=.7;this.scene.add(mountain);
    }
    const sun=new T.Mesh(new T.CircleGeometry(5,64),new T.MeshBasicMaterial({color:0xad6a49,transparent:true,opacity:.35,fog:false,toneMapped:false}));sun.position.set(-28,20,-100);this.scene.add(sun);
    const cloudMap=texture(128,c=>{const g=c.createRadialGradient(64,64,0,64,64,64);g.addColorStop(0,'rgba(218,213,194,.7)');g.addColorStop(.5,'rgba(218,213,194,.34)');g.addColorStop(1,'rgba(218,213,194,0)');c.fillStyle=g;c.fillRect(0,0,128,128);});
    for(let i=0;i<22;i++){
      const cloud=new T.Sprite(new T.SpriteMaterial({map:cloudMap,transparent:true,depthWrite:false,opacity:.5}));cloud.position.set(-25+random()*95,-6-random()*10,-25+random()*30);cloud.scale.set(18+random()*25,5+random()*4,1);this.scene.add(cloud);this.clouds.push(cloud);
    }
    for(let i=0;i<6;i++){
      const line=new T.Line(new T.BufferGeometry().setFromPoints([new T.Vector3(-.25,.08,0),new T.Vector3(0,0,0),new T.Vector3(.25,.08,0)]),new T.LineBasicMaterial({color:0x4c5748,transparent:true,opacity:.5}));line.position.set(-17+i*3,8+Math.sin(i),-48);this.scene.add(line);
    }
  }
  resetView(){this.yaw=.38;this.pitch=.34;this.distance=16;}
  private listen(){
    new ResizeObserver(()=>this.resize()).observe(this.host);
    const canvas=this.renderer.domElement;
    canvas.addEventListener('pointerdown',event=>{this.pointer={down:true,x:event.clientX,y:event.clientY};canvas.setPointerCapture(event.pointerId);});
    canvas.addEventListener('pointermove',event=>{if(!this.pointer.down)return;this.yaw-=(event.clientX-this.pointer.x)*.005;this.pitch=T.MathUtils.clamp(this.pitch+(event.clientY-this.pointer.y)*.003,.13,.87);this.pointer.x=event.clientX;this.pointer.y=event.clientY;});
    const release=()=>{this.pointer.down=false;};canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
    canvas.addEventListener('wheel',event=>{event.preventDefault();this.distance=T.MathUtils.clamp(this.distance+event.deltaY*.012,9,35);},{passive:false});
    window.addEventListener('keydown',event=>{if((event.target as HTMLElement).closest?.('button,a')||document.querySelector('dialog[open]'))return;if(event.code==='KeyQ')this.yaw+=.15;if(event.code==='KeyE')this.yaw-=.15;if(event.code==='KeyV')this.resetView();});
    matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',event=>{this.reduceMotion=event.matches;});
  }
  private resize(){
    this.width=this.host.clientWidth;this.height=Math.max(1,this.host.clientHeight);this.camera.aspect=this.width/this.height;this.camera.updateProjectionMatrix();
    const mobile=this.width<760;this.quality=mobile?'mobile':'desktop';
    this.renderer.setPixelRatio(Math.min(devicePixelRatio,mobile?1.35:1.5));this.renderer.setSize(this.width,this.height);
    this.composer.setSize(this.width,this.height);this.ao.setSize(Math.round(this.width*.6),Math.round(this.height*.6));
    this.usingAO=!mobile;this.ao.enabled=this.usingAO;
  }
  update(game:Game,dt:number){
    if(!this.reduceMotion)this.time+=dt;
    this.character.position.set(game.x,game.y,game.z);
    let angle=game.facing-this.character.rotation.y;angle=Math.atan2(Math.sin(angle),Math.cos(angle));this.character.rotation.y+=angle*Math.min(1,dt*13);
    if(this.loaded){
      if(!this.previousGrounded&&game.grounded)this.landTime=.18;
      this.landTime=Math.max(0,this.landTime-dt);
      const motion=!game.started||game.won?'Idle':!game.grounded?(game.vy>1?'Jump':'Fall'):this.landTime>0?'Land':game.moving>.1?(game.moving>1.1?'Run':'Walk'):'Idle';
      this.motion(motion);this.mixer?.update(dt);
      this.previousGrounded=game.grounded;
    }
    let support:number|null=null;for(const p of PLATFORMS)if(Math.abs(game.x-p.x)<p.w/2&&Math.abs(game.z-p.z)<p.d/2)support=p.y;
    this.shadow.visible=support!==null&&game.y>=support;
    if(support!==null){this.shadow.position.set(game.x,support+.07,game.z);(this.shadow.material as T.MeshBasicMaterial).opacity=Math.max(.1,.8-(game.y-support)*.3);}
    this.sealObjects.forEach((object,i)=>{object.visible=!game.seals.has(i);object.position.y=SEALS[i].y+1+Math.sin(this.time*1.8+i)*.08;object.rotation.y=this.time*.55;});
    if(!this.reduceMotion){this.clouds.forEach((cloud,i)=>cloud.position.x+=Math.sin(i*3)*dt*.055);this.motes.rotation.y=Math.sin(this.time*.06)*.015;}
    if(game.started){this.wanted.set(game.x+1.9,game.y+1.0,game.z-.85);}
    else this.wanted.set(this.width<700?1.0:-2.4,1.7,-1.0);
    if(this.target.distanceTo(this.wanted)>14)this.target.copy(this.wanted);
    else this.target.lerp(this.wanted,1-Math.exp(-dt*4.0));
    const distance=game.started?this.distance*.82:(this.distance<20?23:this.distance);
    const mobile=this.width<700?1.34:1;
    this.cameraPosition.set(this.target.x+Math.sin(this.yaw)*Math.cos(this.pitch)*distance*mobile,this.target.y+Math.sin(this.pitch)*distance*mobile,this.target.z+Math.cos(this.yaw)*Math.cos(this.pitch)*distance*mobile);
    if(game.started&&this.blockers.length){
      const direction=this.cameraPosition.clone().sub(this.target);const length=direction.length();this.cameraRay.set(this.target,direction.normalize());this.cameraRay.far=length;
      const hit=this.cameraRay.intersectObjects(this.blockers,false)[0];if(hit&&hit.distance>2.8)this.cameraPosition.copy(this.target).addScaledVector(direction,Math.max(2.7,hit.distance-.3));
    }
    this.camera.position.copy(this.cameraPosition);this.camera.lookAt(this.target);
    this.frames++;
    this.renderer.info.reset();
    if(this.usingAO)this.composer.render(dt);else this.renderer.render(this.scene,this.camera);
  }
  diagnostics(){return {loaded:this.loaded,quality:this.quality,ao:this.usingAO,animations:[...this.actions.keys()],motion:this.currentMotion,heroFaces:this.heroFaces,frames:this.frames,calls:this.renderer.info.render.calls,triangles:this.renderer.info.render.triangles,geometries:this.renderer.info.memory.geometries,textures:this.renderer.info.memory.textures};}
}
