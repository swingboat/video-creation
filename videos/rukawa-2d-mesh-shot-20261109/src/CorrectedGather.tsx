import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {deformPoint,Point,loadAt} from './gatherMotion';
const W=1280,H=720;
type GPU={gl:WebGLRenderingContext;program:WebGLProgram;buffer:WebGLBuffer;art:WebGLTexture;court:WebGLTexture;position:number;uv:number};
const shader=(gl:WebGLRenderingContext,type:number,source:string)=>{const s=gl.createShader(type)!;gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s)??'Shader compile error');return s;};
function init(canvas:HTMLCanvasElement,images:HTMLImageElement[]):GPU{
 const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:true,preserveDrawingBuffer:true,antialias:true});if(!gl)throw Error('WebGL is required');
 const program=gl.createProgram()!;
 gl.attachShader(program,shader(gl,gl.VERTEX_SHADER,'attribute vec2 aPosition;attribute vec2 aUV;varying vec2 uv;void main(){gl_Position=vec4(aPosition.x/640.-1.,1.-aPosition.y/360.,0.,1.);uv=aUV;}'));
 gl.attachShader(program,shader(gl,gl.FRAGMENT_SHADER,'precision mediump float;varying vec2 uv;uniform sampler2D tex;uniform float shadowAlpha;void main(){if(shadowAlpha>0.){vec2 q=(uv-.5)*2.;float a=shadowAlpha*pow(max(0.,1.-dot(q,q)),2.);gl_FragColor=vec4(vec3(.10,.08,.06)*a,a);}else{gl_FragColor=texture2D(tex,uv);}}'));
 gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('Shader link error');gl.useProgram(program);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,1);
 const textures=images.map(im=>{const tex=gl.createTexture()!;gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);return tex;});
 return {gl,program,buffer:gl.createBuffer()!,art:textures[0],court:textures[1],position:gl.getAttribLocation(program,'aPosition'),uv:gl.getAttribLocation(program,'aUV')};
}
function mesh(g:GPU,rect:number[],step:number,map:(v:Point)=>Point,texture:WebGLTexture,tw:number,th:number,shadowAlpha=0){
 const [x,y,w,h]=rect,nx=Math.ceil(w/step),ny=Math.ceil(h/step),data:number[]=[];
 const vertex=(i:number,j:number)=>{const p={x:x+w*i/nx,y:y+h*j/ny},q=map(p);data.push(q.x,q.y,p.x/tw,p.y/th);};
 for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){vertex(i,j);vertex(i+1,j);vertex(i,j+1);vertex(i+1,j);vertex(i+1,j+1);vertex(i,j+1);}
 const {gl}=g;gl.uniform1f(gl.getUniformLocation(g.program,'shadowAlpha'),shadowAlpha);gl.bindTexture(gl.TEXTURE_2D,texture);gl.bindBuffer(gl.ARRAY_BUFFER,g.buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data),gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(g.position);gl.vertexAttribPointer(g.position,2,gl.FLOAT,false,16,0);gl.enableVertexAttribArray(g.uv);gl.vertexAttribPointer(g.uv,2,gl.FLOAT,false,16,8);gl.drawArrays(gl.TRIANGLES,0,data.length/4);
}
export const CorrectedGather:React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),canvas=useRef<HTMLCanvasElement>(null),gpu=useRef<GPU|null>(null),handle=useRef<number|null>(null),[images,setImages]=useState<HTMLImageElement[]|null>(null);
 if(handle.current===null&&!images)handle.current=delayRender('Loading corrected character art');
 useEffect(()=>{let active=true;Promise.all(['art/correctives/rukawa-gather-anatomy-v1.png','art/court-background.png'].map(file=>new Promise<HTMLImageElement>((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=staticFile(file);}))).then(im=>{if(active)setImages(im);});return()=>{active=false;};},[]);
 useLayoutEffect(()=>{
  if(!images||!canvas.current)return;if(!gpu.current)gpu.current=init(canvas.current,images);const g=gpu.current,{gl}=g,t=frame/fps;gl.viewport(0,0,W,H);gl.clearColor(.91,.88,.83,1);gl.clear(gl.COLOR_BUFFER_BIT);
  const bg=images[1],crop=350;mesh(g,[0,crop,bg.width,bg.height-crop],128,p=>({x:W-p.x/bg.width*W,y:(p.y-crop)/(bg.height-crop)*H}),g.court,bg.width,bg.height);
  // Separate static contact shadows for the staggered feet.
  for(const sh of [{x:842,y:631,w:91,h:13},{x:974,y:648,w:87,h:14}])mesh(g,[0,0,1,1],1,p=>({x:sh.x+(p.x-.5)*sh.w,y:sh.y+(p.y-.5)*sh.h}),g.art,1,1,.20+.025*loadAt(t));
  mesh(g,[0,0,images[0].width,images[0].height],22,p=>deformPoint(p,t),g.art,images[0].width,images[0].height);
  gl.flush();if(handle.current!==null){continueRender(handle.current);handle.current=null;}
 },[frame,fps,images]);
 return <canvas ref={canvas} width={W} height={H} style={{position:'absolute',width:'100%',height:'100%'}}/>;
};
