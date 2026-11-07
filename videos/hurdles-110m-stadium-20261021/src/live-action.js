import assets from '../.cache/live-action-assets.json';
const $=id=>document.getElementById(id),video=$('film'),seek=$('seek');
const errors=[];let ready=false,hasStarted=false,objectUrl;
const q=new URLSearchParams(location.search);
const timeString=t=>Math.max(0,t).toFixed(2).padStart(5,'0');
function sync(){const t=video.currentTime||0,d=Number.isFinite(video.duration)?video.duration:6.2;seek.max=String(d);seek.value=String(t);seek.style.setProperty('--progress',`${100*t/d}%`);$('time').textContent=timeString(t);$('duration').textContent=`${timeString(d)} s`;$('frame-count').textContent=`FRAME ${String(Math.round(t*30)).padStart(3,'0')}`;
 const playing=!video.paused&&!video.ended;$('play').setAttribute('aria-label',playing?'暂停训练':'播放训练');$('play').classList.toggle('is-playing',playing);$('play-icon').setAttribute('d',playing?'M8 5v14M16 5v14':'m9 5 10 7-10 7Z');$('hero-play').hidden=hasStarted&&!video.ended;
 $('hero-play').querySelector('span').textContent=video.ended?'再看一次':'播放训练影像';$('caption').textContent=t<4.8?'真实动作，真实节奏。':t<5.32?'向前，把握起跨的一刻。':t<5.68?'越过，再继续向前。':'每次落地，都是新的起点。';
 document.querySelectorAll('.moment').forEach(b=>b.classList.toggle('selected',Math.abs(t-Number(b.dataset.time))<.13));
}
async function setPlaying(p){if(!ready)return;if(p){if(video.ended)video.currentTime=0;hasStarted=true;await video.play();}else video.pause();sync();}
async function setTime(t){if(!ready)return;const target=Math.min(Math.max(0,Number(t)||0),video.duration-.001);hasStarted=true;if(Math.abs(video.currentTime-target)<.001){sync();return;}
 await new Promise((resolve,reject)=>{let timer;const done=()=>{clearTimeout(timer);video.removeEventListener('error',fail);sync();resolve();};const fail=()=>{clearTimeout(timer);video.removeEventListener('seeked',done);reject(Error('Video seek failed'));};video.addEventListener('seeked',done,{once:true});video.addEventListener('error',fail,{once:true});timer=setTimeout(()=>{video.removeEventListener('seeked',done);video.removeEventListener('error',fail);reject(Error('Video seek timed out'));},12000);video.currentTime=target;});
}
function setSpeed(rate){video.defaultPlaybackRate=rate;video.playbackRate=rate;document.querySelectorAll('[data-speed]').forEach(b=>{const active=Number(b.dataset.speed)===rate;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});}
function immersive(){const active=document.body.classList.toggle('immersive');$('immersive').setAttribute('aria-pressed',String(active));$('immersive').setAttribute('aria-label',active?'退出沉浸':'沉浸观看');}
function fail(error){const message=error?.message||String(error);errors.push(message);$('error').hidden=false;$('error').textContent='影像无法加载：'+message;$('load-status').hidden=true;}
window.liveHurdle={get ready(){return ready;},setPlaying,setTime,setSpeed,getState:()=>({ready,time:video.currentTime,duration:video.duration,playing:!video.paused,speed:video.playbackRate,errors:[...errors],media:video.currentSrc,immersive:document.body.classList.contains('immersive')})};
$('play').onclick=$('hero-play').onclick=()=>setPlaying(video.paused).catch(fail);
$('restart').onclick=async()=>{await setTime(0);await setPlaying(true);};
seek.addEventListener('input',()=>{video.pause();hasStarted=true;video.currentTime=Number(seek.value);sync();});
$('prev-frame').onclick=async()=>{video.pause();await setTime(video.currentTime-1/30);};$('next-frame').onclick=async()=>{video.pause();await setTime(video.currentTime+1/30);};
document.querySelectorAll('[data-speed]').forEach(b=>b.onclick=()=>setSpeed(Number(b.dataset.speed)));
document.querySelectorAll('.moment').forEach(b=>b.onclick=async()=>{video.pause();await setTime(Number(b.dataset.time));});
$('immersive').onclick=$('exit-immersive').onclick=immersive;
video.onclick=()=>{if(document.body.classList.contains('immersive'))setPlaying(video.paused).catch(fail);};
const dialog=$('credits');$('credits-open').onclick=$('credits-footer').onclick=()=>dialog.showModal();$('credits-close').onclick=()=>dialog.close();
dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
document.addEventListener('keydown',e=>{if(dialog.open||/INPUT|TEXTAREA/.test(document.activeElement?.tagName))return;if(e.code==='Space'){if(/BUTTON|A/.test(document.activeElement?.tagName))return;e.preventDefault();setPlaying(video.paused).catch(fail);}else if(e.code==='ArrowRight'||e.code==='ArrowLeft'){e.preventDefault();video.pause();setTime(video.currentTime+(e.code==='ArrowRight'?1:-1)/30).catch(fail);}else if(e.key.toLowerCase()==='h')immersive();else if(e.key.toLowerCase()==='r')$('restart').click();else if(e.key==='Escape'&&document.body.classList.contains('immersive'))immersive();});
video.addEventListener('error',()=>fail(Error(video.error?.message||'浏览器无法解码 MP4')));['timeupdate','play','pause','ended','seeked'].forEach(event=>video.addEventListener(event,sync));
video.addEventListener('waiting',()=>{if(hasStarted)$('load-status').hidden=false;});video.addEventListener('canplay',()=>{$('load-status').hidden=true;});
if('requestVideoFrameCallback'in video){const frame=()=>{sync();video.requestVideoFrameCallback(frame);};video.requestVideoFrameCallback(frame);}
document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();});
window.addEventListener('pagehide',()=>{if(objectUrl)URL.revokeObjectURL(objectUrl);});
async function init(){video.poster=assets.poster;for(const [id,key]of[['moment-approach','approach'],['moment-flight','flight'],['moment-landing','landing']])$(id).src=assets[key];
 const bytes=Uint8Array.from(atob(assets.video.split(',')[1]),c=>c.charCodeAt(0));objectUrl=URL.createObjectURL(new Blob([bytes],{type:'video/mp4'}));video.src=objectUrl;setSpeed(1);
 await new Promise((resolve,reject)=>{video.addEventListener('loadeddata',resolve,{once:true});video.addEventListener('error',reject,{once:true});video.load();});ready=true;setSpeed(1);$('load-status').hidden=true;sync();if(q.has('t'))await setTime(Number(q.get('t')));if(q.get('clean')==='1')document.body.classList.add('immersive');if(q.get('autoplay')==='1'&&!matchMedia('(prefers-reduced-motion: reduce)').matches)await setPlaying(true);
}
init().catch(fail);
