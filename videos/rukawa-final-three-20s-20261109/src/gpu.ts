import {Point,p} from './math';
export type Color=[number,number,number,number];
export const ASSETS={court:'art/court.png',gather:'art/rukawa-gather.png',release:'art/rukawa-release.png',defender:'art/defender-jump.png',support:'art/support-players.png',hoop:'art/hoop-court-reference.png',cheer:'art/arena-cheer.png',ball:'art/ball-atlas.png'};
export type Asset=keyof typeof ASSETS;
export class Painter{
 gl:WebGLRenderingContext;program:WebGLProgram;buffer:WebGLBuffer;pos:number;uv:number;textures={} as Record<Asset,WebGLTexture>;
 constructor(canvas:HTMLCanvasElement,public images:Record<Asset,HTMLImageElement>){
  const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:true,preserveDrawingBuffer:true,antialias:true});if(!gl)throw Error('WebGL unavailable');this.gl=gl;
  const sh=(type:number,s:string)=>{const x=gl.createShader(type)!;gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(x)??'Shader error');return x;};
  this.program=gl.createProgram()!;gl.attachShader(this.program,sh(gl.VERTEX_SHADER,'attribute vec2 aPos;attribute vec2 aUV;varying vec2 uv;void main(){gl_Position=vec4(aPos.x/640.-1.,1.-aPos.y/360.,0.,1.);uv=aUV;}'));
  gl.attachShader(this.program,sh(gl.FRAGMENT_SHADER,'precision mediump float;varying vec2 uv;uniform sampler2D tex;uniform float mode;uniform float opacity;uniform vec4 color;void main(){if(mode>1.5){vec2 q=(uv-.5)*2.;float a=pow(max(0.,1.-dot(q,q)),2.);gl_FragColor=color*a;}else if(mode>.5){gl_FragColor=color;}else{gl_FragColor=texture2D(tex,uv)*opacity;}}'));
  gl.linkProgram(this.program);if(!gl.getProgramParameter(this.program,gl.LINK_STATUS))throw Error('Link error');gl.useProgram(this.program);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,1);
  this.pos=gl.getAttribLocation(this.program,'aPos');this.uv=gl.getAttribLocation(this.program,'aUV');this.buffer=gl.createBuffer()!;
  for(const key of Object.keys(images) as Asset[]){const tx=gl.createTexture()!;gl.bindTexture(gl.TEXTURE_2D,tx);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,images[key]);this.textures[key]=tx;}
 }
 clear(){const g=this.gl;g.viewport(0,0,1280,720);g.clearColor(.06,.12,.14,1);g.clear(g.COLOR_BUFFER_BIT);}
 private render(vertices:number[],mode=0,alpha=1,color:Color=[0,0,0,0]){
  const g=this.gl;g.uniform1f(g.getUniformLocation(this.program,'mode'),mode);g.uniform1f(g.getUniformLocation(this.program,'opacity'),alpha);g.uniform4f(g.getUniformLocation(this.program,'color'),color[0]*color[3],color[1]*color[3],color[2]*color[3],color[3]);g.bindBuffer(g.ARRAY_BUFFER,this.buffer);g.bufferData(g.ARRAY_BUFFER,new Float32Array(vertices),g.DYNAMIC_DRAW);g.enableVertexAttribArray(this.pos);g.vertexAttribPointer(this.pos,2,g.FLOAT,false,16,0);g.enableVertexAttribArray(this.uv);g.vertexAttribPointer(this.uv,2,g.FLOAT,false,16,8);g.drawArrays(g.TRIANGLES,0,vertices.length/4);
 }
 image(key:Asset,rect:number[],map:(v:Point)=>Point,step=30,alpha=1){
  const [x,y,w,h]=rect,nx=Math.ceil(w/step),ny=Math.ceil(h/step),im=this.images[key],out:number[]=[];
  const push=(i:number,j:number)=>{const s=p(x+w*i/nx,y+h*j/ny),d=map(s);out.push(d.x,d.y,s.x/im.width,s.y/im.height);};
  for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){push(i,j);push(i+1,j);push(i,j+1);push(i+1,j);push(i+1,j+1);push(i,j+1);}
  this.gl.bindTexture(this.gl.TEXTURE_2D,this.textures[key]);this.render(out,0,alpha);
 }
 full(key:Asset,map:(v:Point)=>Point,step=30,alpha=1){const im=this.images[key];this.image(key,[0,0,im.width,im.height],map,step,alpha);}
 shadow(cx:number,cy:number,w:number,h:number,alpha:number){const v:number[]=[];for(const [x,y] of [[0,0],[1,0],[0,1],[1,0],[1,1],[0,1]])v.push(cx+(x-.5)*w,cy+(y-.5)*h,x,y);this.render(v,2,1,[.12,.08,.04,alpha]);}
 line(points:Point[],width:number,color:Color){const v:number[]=[];for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],d=Math.hypot(b.x-a.x,b.y-a.y);if(d<.0001)continue;const n=p(-(b.y-a.y)/d*width/2,(b.x-a.x)/d*width/2),q=[p(a.x+n.x,a.y+n.y),p(b.x+n.x,b.y+n.y),p(a.x-n.x,a.y-n.y),p(b.x-n.x,b.y-n.y)];for(const k of [0,1,2,1,3,2])v.push(q[k].x,q[k].y,0,0);}this.render(v,1,1,color);}
 flush(){this.gl.flush();}
}
