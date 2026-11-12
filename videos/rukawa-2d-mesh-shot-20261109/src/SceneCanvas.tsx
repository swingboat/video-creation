import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {P,p,pose,screen,armMesh,legMesh,bodyMesh,source,rot,sub,add,mul} from './rig';
const W=1280,H=720;
type GPU={gl:WebGLRenderingContext;program:WebGLProgram;buf:WebGLBuffer;atlas:WebGLTexture;bg:WebGLTexture;pos:number;uv:number};
const shader=(gl:WebGLRenderingContext,type:number,s:string)=>{const o=gl.createShader(type)!;gl.shaderSource(o,s);gl.compileShader(o);if(!gl.getShaderParameter(o,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(o)??'Shader failed');return o;};
function init(canvas:HTMLCanvasElement,images:HTMLImageElement[]):GPU{
 const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:true,preserveDrawingBuffer:true,antialias:true})!;if(!gl)throw Error('WebGL unavailable');
 const program=gl.createProgram()!;gl.attachShader(program,shader(gl,gl.VERTEX_SHADER,'attribute vec2 aPos;attribute vec2 aUV;varying vec2 uv;void main(){gl_Position=vec4(aPos.x/640.0-1.0,1.0-aPos.y/360.0,0.0,1.0);uv=aUV;}'));gl.attachShader(program,shader(gl,gl.FRAGMENT_SHADER,'precision mediump float;varying vec2 uv;uniform sampler2D tex;uniform float isShadow;void main(){if(isShadow>.5){vec2 q=(uv-.5)*2.;float a=.24*pow(max(0.,1.-dot(q,q)),2.);gl_FragColor=vec4(vec3(.12,.09,.07)*a,a);}else{gl_FragColor=texture2D(tex,uv);}}'));gl.linkProgram(program);gl.useProgram(program);
 gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,1);
 const textures=images.map(im=>{const tx=gl.createTexture()!;gl.bindTexture(gl.TEXTURE_2D,tx);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);return tx;});
 return {gl,program,buf:gl.createBuffer()!,atlas:textures[0],bg:textures[1],pos:gl.getAttribLocation(program,'aPos'),uv:gl.getAttribLocation(program,'aUV')};
}
function grid(g:GPU,bounds:number[],step:number,map:(v:P)=>P,tex=g.atlas,tw=1536,th=1024,shadow=false){
 const [x,y,w,h]=bounds,nx=Math.ceil(w/step),ny=Math.ceil(h/step),v:number[]=[];
 function vertex(ix:number,iy:number){const src=p(x+w*ix/nx,y+h*iy/ny),dst=map(src);v.push(dst.x,dst.y,src.x/tw,src.y/th);}
 for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){vertex(i,j);vertex(i+1,j);vertex(i,j+1);vertex(i+1,j);vertex(i+1,j+1);vertex(i,j+1);}
 const {gl}=g;gl.uniform1f(gl.getUniformLocation(g.program,'isShadow'),shadow?1:0);gl.bindTexture(gl.TEXTURE_2D,tex);gl.bindBuffer(gl.ARRAY_BUFFER,g.buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(v),gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(g.pos);gl.vertexAttribPointer(g.pos,2,gl.FLOAT,false,16,0);gl.enableVertexAttribArray(g.uv);gl.vertexAttribPointer(g.uv,2,gl.FLOAT,false,16,8);gl.drawArrays(gl.TRIANGLES,0,v.length/4);
}
export const SceneCanvas:React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),canvas=useRef<HTMLCanvasElement>(null),gpu=useRef<GPU|null>(null),[images,setImages]=useState<HTMLImageElement[]|null>(null),handle=useRef<number|null>(null);
 if(handle.current===null&&!images)handle.current=delayRender('Loading local 2D art');
 useEffect(()=>{let active=true;Promise.all(['art/rukawa-layer-atlas-v1.png','art/court-background.png'].map(n=>new Promise<HTMLImageElement>((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=staticFile(n);}))).then(x=>{if(active)setImages(x);});return()=>{active=false;};},[]);
 useLayoutEffect(()=>{
  if(!canvas.current||!images)return;if(!gpu.current)gpu.current=init(canvas.current,images);const g=gpu.current,gl=g.gl;gl.viewport(0,0,W,H);gl.clearColor(.91,.89,.83,1);gl.clear(gl.COLOR_BUFFER_BIT);
  // Crop below the stands: this short test isolates the player's movement.
  grid(g,[0,350,images[1].width,images[1].height-350],128,v=>p(W-v.x/images[1].width*W,(v.y-350)/(images[1].height-350)*H),g.bg,images[1].width,images[1].height);
  const t=frame/fps,r=pose(t);
  const sh=screen(p(922-(950-r.root.x),664));grid(g,[0,0,1,1],1,v=>p(sh.x+(v.x-.5)*130,sh.y+(v.y-.5)*17),g.atlas,1,1,true);
  grid(g,source.farLeg.bounds,7,legMesh('far',r));grid(g,source.nearLeg.bounds,7,legMesh('near',r));
  gl.enable(gl.SCISSOR_TEST);gl.scissor(0,0,Math.ceil(screen(p(r.root.x+5,0)).x),H);
  grid(g,[703,92,130,428],6,armMesh('far',r));gl.disable(gl.SCISSOR_TEST);
  
  grid(g,[176,5,232,532],7,bodyMesh(r));
  const bp=screen(r.ball),a=t*1.8;
  grid(g,[1165,682,196,202],24,v=>add(bp,rot(mul(sub(v,p(1263,783)),.315*.83),a)));
  grid(g,[1195,92,125,428],6,armMesh('near',r));
  gl.flush();if(handle.current!==null){continueRender(handle.current);handle.current=null;}
 },[frame,fps,images]);
 return <canvas ref={canvas} width={W} height={H} style={{position:'absolute',width:'100%',height:'100%'}}/>;
};
