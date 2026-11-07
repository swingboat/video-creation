import './style.css';
import {Game,SEALS} from './game.ts';
import {World} from './world.ts';
import {MountainAudio} from './audio.ts';

const icons:Record<string,string>={
  arrow:'<path d="M4 12h15m-6-6 6 6-6 6"/>',
  sound:'<path d="m11 5-5 4H3v6h3l5 4V5Z"/><path d="M16 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/>',
  muted:'<path d="m11 5-5 4H3v6h3l5 4V5Z"/><path d="m16 9 5 6m0-6-5 6"/>',
  expand:'<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>',
  book:'<path d="M4 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-2H4V4Zm16 0h-4a3 3 0 0 0-3 3v14a4 4 0 0 1 4-2h3V4Z"/>',
  close:'<path d="m6 6 12 12M6 18 18 6"/>',
  refresh:'<path d="M4 10a8 8 0 1 1 1.5 7M4 4v6h6"/>',
  up:'<path d="m6 14 6-6 6 6"/>',
  down:'<path d="m6 10 6 6 6-6"/>',
  left:'<path d="m14 6-6 6 6 6"/>',
  right:'<path d="m10 6 6 6-6 6"/>',
  check:'<path d="m5 12 4 4L19 6"/>',
  mountain:'<path d="m2 19 7-13 5 9 3-5 5 9H2Z"/><path d="m6 12 3 2 3-2"/>',
};
function icon(name:string){return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]??icons.mountain}</svg>`;}
const root=document.querySelector<HTMLDivElement>('#app')!;
root.innerHTML=`
  <main class="experience" id="experience">
    <div id="world" class="world"></div>
    <div class="paper-wash" aria-hidden="true"></div>
    <div class="grain" aria-hidden="true"></div>
    <div class="asset-loading" id="asset-loading" role="status"><span class="loading-stroke"></span><span id="loading-label">正在展开山色…</span></div>
    <header class="header">
      <a class="brand" href="" aria-label="山有归途，返回首页">
        <span class="brand-mark">${icon('mountain')}</span>
        <span class="brand-name">墨山<span>SUMI PASSAGE</span></span>
      </a>
      <span class="header-note">一个可以走进去的山水世界</span>
      <nav class="header-actions" aria-label="旅程工具">
        <button class="journal-button" id="journal">${icon('book')}<span>旅人手记</span></button>
        <span class="nav-divider"></span>
        <button class="icon-button" id="sound" aria-label="开启山间声音" aria-pressed="false" title="开启山间声音">${icon('muted')}</button>
        <button class="icon-button fullscreen" id="fullscreen" aria-label="进入全屏" title="进入全屏">${icon('expand')}</button>
      </nav>
    </header>
    <section class="intro" id="intro" aria-labelledby="title">
      <div class="eyebrow"><span></span> A LITTLE JOURNEY, A LONG WAY HOME</div>
      <div class="title-row"><h1 id="title">山有<span>归途</span></h1><span class="title-seal" aria-hidden="true">山间<br/>来信</span></div>
      <p class="intro-copy">山不言，风自有回音。<br/>循着微光，走回云雾深处。</p>
      <button class="start-button" id="start"><span id="start-label">启程入山</span>${icon('arrow')}</button>
      <p class="start-note"><span class="tiny-circle"></span><span id="save-note">无需下载，即刻出发</span></p>
    </section>
    <div class="vertical-poem" aria-hidden="true"><span>但行山路</span><i></i><span>莫问归期</span></div>
    <aside class="quest" id="quest" aria-label="当前任务" hidden>
      <div class="quest-top"><span class="quest-label">山间寻印</span><span id="seal-count">0 / 3</span></div>
      <p id="objective">越过山隙，拾起三枚山印。</p>
      <div class="seal-progress" aria-label="收集进度">${SEALS.map((s,i)=>`<span class="seal-item" id="seal-${i}" aria-label="${s.name}，未收集"><i>◇</i><span>${s.name}</span></span>`).join('')}</div>
    </aside>
    <div class="location-label" aria-hidden="true"><span class="location-dot"></span><span id="location">雾起之地</span><i>—</i><span>海拔 <span id="altitude">一千二百</span> 米</span></div>
    <footer class="footer">
      <div class="chapter"><span class="chapter-number" id="chapter-number">01<span>/ 03</span></span><div><span id="chapter-name">渡 雾</span><small id="chapter-en">THE CROSSING</small></div></div>
      <div class="lobby-hint" id="lobby-hint"><span class="drag-symbol" aria-hidden="true">↔</span><span>拖动，换个角度看山</span><span class="hint-dot">·</span><span class="zoom-hint">滚轮缩放</span></div>
      <div class="footer-caption" id="footer-caption"><span class="live-dot"></span>此刻，山风正好</div>
      <div class="keyboard-hint" id="keyboard-hint" hidden><span><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> 行走</span><span><kbd class="wide">SPACE</kbd> 跳跃</span><span class="extra-control"><kbd>SHIFT</kbd> 快跑</span><span class="extra-control"><kbd>R</kbd> 返回</span><span><kbd>ESC</kbd> 暂停</span></div>
    </footer>
    <div class="touch-controls" id="touch-controls" hidden aria-label="触屏游戏控制">
      <div class="dpad"><button data-key="KeyW" class="dpad-up" aria-label="向前移动">${icon('up')}</button><button data-key="KeyA" class="dpad-left" aria-label="向左移动">${icon('left')}</button><button data-key="KeyS" class="dpad-down" aria-label="向后移动">${icon('down')}</button><button data-key="KeyD" class="dpad-right" aria-label="向右移动">${icon('right')}</button></div>
      <button class="touch-jump" id="touch-jump" aria-label="跳跃">${icon('up')}<span>跳跃</span></button>
    </div>
    <div class="toast" id="toast" role="status" aria-live="polite"></div>
    <div class="webgl-error" id="webgl-error" hidden><h2>山色暂未展开</h2><p>请使用支持 WebGL 2 的浏览器，并开启硬件加速后重试。</p><button id="retry" class="start-button">重新展开 ${icon('refresh')}</button></div>
  </main>
  <dialog class="journal-dialog" id="guide-dialog" aria-labelledby="guide-title">
    <div class="dialog-top"><span class="eyebrow">NOTES FROM THE MOUNTAIN</span><button class="icon-button close-dialog" aria-label="关闭旅人手记">${icon('close')}</button></div>
    <h2 id="guide-title">旅人手记</h2>
    <div class="tabs" role="tablist" aria-label="手记内容"><button role="tab" aria-selected="true" id="tab-guide" aria-controls="panel-guide" tabindex="0">行走指南</button><button role="tab" aria-selected="false" id="tab-story" aria-controls="panel-story" tabindex="-1">关于归途</button></div>
    <section id="panel-guide" role="tabpanel" aria-labelledby="tab-guide">
      <p class="dialog-lead">不必急着抵达。先走稳脚下的路。</p>
      <div class="journey-map" aria-label="路线：雾起之地、渡雾山印、听松存档点、见山山印、归门终点"><svg viewBox="0 0 480 90" fill="none" aria-hidden="true"><path d="M20 60C80 60 65 20 135 35S215 75 260 35 340 10 375 35 430 50 460 20" stroke="currentColor" stroke-width="1" stroke-dasharray="4 5"/><circle cx="20" cy="60" r="5" fill="currentColor"/><circle cx="135" cy="35" r="7" stroke="currentColor"/><circle cx="260" cy="35" r="7" stroke="currentColor"/><circle cx="375" cy="35" r="7" stroke="currentColor"/><path d="M448 11h24m-21 5h18m-15 0v18m12-18v18" stroke="#9e432f" stroke-width="2"/></svg><div><span>雾起</span><span>渡雾</span><span>听松 · 存档</span><span>见山</span><span>归门</span></div></div>
      <ul class="control-list"><li><span>在山间行走</span><span><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> 或方向键</span></li><li><span>跃过山隙</span><span><kbd>SPACE</kbd> 跳跃 · <kbd>SHIFT</kbd> 快跑</span></li><li><span>看看四周</span><span>拖动视角 · 滚轮缩放 · <kbd>V</kbd> 复位</span></li><li><span>换个角度</span><span><kbd>Q</kbd><kbd>E</kbd> 旋转视角</span></li><li><span>重新站稳</span><span><kbd>R</kbd> 返回存档点</span></li></ul>
      <p class="small-note">拾起「听松」山印会点亮途中存档点。进度自动保存在本机浏览器；掉进云里，也可以再来一次。手机可用屏幕下方的方向与跳跃按钮。</p>
    </section>
    <section id="panel-story" role="tabpanel" aria-labelledby="tab-story" hidden><p class="dialog-lead">群山不问来处，只留一条归途。</p><p class="story-copy">一顶斗笠，一缕赤色衣带。你是行走在云海之上的旅人，越过七座孤崖，循着三枚山印，走向群山深处的朱门。</p><p class="story-copy">这是一个受水墨山景与日式庭园启发的原创网页小品。风化的石壁、曲松与朱门围合成山间小路，旅人的衣袍随脚步舒展。适合慢慢探索。</p><a class="source-link" href="https://x.com/xikhar/status/2117776295534997818" target="_blank" rel="noopener noreferrer">灵感来自 Shikhar 的游戏制作分享 ${icon('arrow')}</a><p class="small-note">参考了原帖的视觉气质与制作思路；原视频与原作者资产没有用于本游戏。</p></section>
    <div class="dialog-actions"><button class="text-button" id="reset">${icon('refresh')}重新开始旅程</button><button class="dark-button" id="resume">回到山间 ${icon('arrow')}</button></div>
  </dialog>
  <dialog class="win-dialog" id="win-dialog" aria-labelledby="win-title"><span class="finish-seal">归</span><p class="eyebrow">EVERY PATH LEADS YOU HOME</p><h2 id="win-title">山高路远，<br/>终有归时。</h2><p class="dialog-lead">三枚山印已归位。山风记得你的脚步。</p><div class="results"><div><span id="result-time">00:00</span><small>行走时光</small></div><div><span>三 / 三</span><small>山间寻印</small></div><div><span id="result-falls">0</span><small>重新出发</small></div></div><button class="dark-button" id="replay">再走一程 ${icon('arrow')}</button><button class="text-button" id="back-home">留在山间，看一会儿风景</button></dialog>
`;

const $=<T extends HTMLElement=HTMLElement>(id:string)=>document.getElementById(id) as T;
const game=new Game();const audio=new MountainAudio();
const SAVE_KEY='sumi-passage-progress-v1';
let saved=false;
try{const raw=localStorage.getItem(SAVE_KEY);if(raw)saved=game.restore(JSON.parse(raw));}catch{/* Storage can be unavailable in private contexts. */}
if(saved){$('start-label').textContent='续上山间路';$('save-note').textContent='已记下你上次的脚步';}
let world:World|undefined;
$<HTMLButtonElement>('start').disabled=true;
window.addEventListener('sumi:loading',((event:CustomEvent<{loaded:number;total:number}>)=>{$('loading-label').textContent=`正在展开山色 · ${Math.round(event.detail.loaded/event.detail.total*100)}%`;} ) as EventListener);
try{world=new World($('world'));}catch(error){
  console.error('Unable to create the mountain scene',error);$('webgl-error').hidden=false;$('intro').hidden=true;
  $('start').setAttribute('disabled','');
}
world?.ready.then(()=>{$('asset-loading').hidden=true;$<HTMLButtonElement>('start').disabled=false;}).catch(error=>{
  console.error('Unable to load mountain assets',error);$('asset-loading').hidden=true;$('webgl-error').hidden=false;
  $('webgl-error').querySelector('h2')!.textContent='山路还未展开';
  $('webgl-error').querySelector('p')!.textContent='场景暂未加载完成，请检查连接后重新展开。';
});
$('retry').addEventListener('click',()=>location.reload());
const keys=new Set<string>();
const guide=$<HTMLDialogElement>('guide-dialog');const win=$<HTMLDialogElement>('win-dialog');
let toastTimer=0;let saveTimer=0;let hudTimer=0;let accumulator=0;let last=performance.now();let resumeAfterDialog=false;
function notify(message:string){window.clearTimeout(toastTimer);$('toast').textContent=message;$('toast').classList.add('visible');toastTimer=window.setTimeout(()=>$('toast').classList.remove('visible'),3800);}
function persist(){try{localStorage.setItem(SAVE_KEY,JSON.stringify(game.save()));}catch{/* The game remains playable without persistence. */}}
function clearSave(){try{localStorage.removeItem(SAVE_KEY);}catch{}}
function updateHUD(){
  $('seal-count').textContent=`${game.seals.size} / 3`;
  SEALS.forEach((seal,i)=>{const node=$(`seal-${i}`);node.classList.toggle('collected',game.seals.has(i));node.setAttribute('aria-label',`${seal.name}，${game.seals.has(i)?'已收集':'未收集'}`);node.querySelector('i')!.innerHTML=game.seals.has(i)?icon('check'):'◇';});
  const chapter=game.x<13?0:game.x<26?1:2;
  $('chapter-number').innerHTML=`0${chapter+1}<span>/ 03</span>`;
  $('chapter-name').textContent=['渡 雾','听 松','归 门'][chapter];
  $('chapter-en').textContent=['THE CROSSING','PINES & WHISPERS','HOMEWARD'][chapter];
  $('location').textContent=['雾起之地','松风歇处','朱门在望'][chapter];
  $('altitude').textContent=String(Math.round(1200+Math.max(0,game.y)*28));
  $('objective').textContent=game.seals.size===3?'山印已齐，走向最高处的朱色鸟居。':game.checkpoint===3?'脚步已存于听松处，继续循光而行。':'越过山隙，拾起三枚山印。';
}
function start(reset=false){
  if(!world)return;
  if(reset){game.reset();clearSave();saved=false;}
  game.start();root.classList.add('playing');$('intro').inert=true;$('intro').setAttribute('aria-hidden','true');
  $('quest').hidden=false;$('keyboard-hint').hidden=false;$('touch-controls').hidden=false;
  $('lobby-hint').hidden=true;$('footer-caption').hidden=true;
  world.resetView();world.renderer.domElement.focus({preventScroll:true});keys.clear();updateHUD();persist();
  if(!saved||reset)notify('往右前方走，循微光跃过山隙。空格跳跃。');
}
$('start').addEventListener('click',()=>start());
function openGuide(){
  if(guide.open||win.open)return;
  resumeAfterDialog=game.started&&!game.paused&&!game.won;
  game.paused=true;keys.clear();guide.showModal();
}
function closeGuide(){guide.close();}
$('journal').addEventListener('click',openGuide);
guide.querySelector('.close-dialog')!.addEventListener('click',closeGuide);
$('resume').addEventListener('click',closeGuide);
guide.addEventListener('close',()=>{if(resumeAfterDialog)game.paused=false;resumeAfterDialog=false;keys.clear();if(game.started)world?.renderer.domElement.focus();else $('journal').focus();});
guide.addEventListener('click',event=>{if(event.target===guide){const r=guide.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)closeGuide();}});
$('reset').addEventListener('click',()=>{resumeAfterDialog=false;guide.close();start(true);});
const tabs=[$('tab-guide'),$('tab-story')];
function selectTab(index:number,focus=false){tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));tab.tabIndex=i===index?0:-1;$(i===0?'panel-guide':'panel-story').hidden=i!==index;});if(focus)tabs[index].focus();}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectTab(i));tab.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();selectTab(1-i,true);}});});
function formatTime(seconds:number){return `${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(Math.floor(seconds%60)).padStart(2,'0')}`;}
game.onEvent=event=>{
  if(event.type==='seal'){
    audio.chime(event.index!*2);notify(`已拾起「${SEALS[event.index!].name}」山印${event.index===1?' · 已点亮途中存档点':''}`);persist();updateHUD();
  }
  if(event.type==='fall'){notify('云雾托住了你。回到上一次站稳的地方。');persist();}
  if(event.type==='missing')notify(`朱门在等你。还有 ${3-game.seals.size} 枚山印留在山间。`);
  if(event.type==='win'){
    keys.clear();audio.chime(5);clearSave();$('result-time').textContent=formatTime(game.seconds);$('result-falls').textContent=String(game.falls);win.showModal();
  }
};
$('replay').addEventListener('click',()=>{win.close();start(true);});
$('back-home').addEventListener('click',()=>{
  win.close();game.started=false;game.paused=false;root.classList.remove('playing');$('intro').inert=false;$('intro').removeAttribute('aria-hidden');
  $('quest').hidden=true;$('keyboard-hint').hidden=true;$('touch-controls').hidden=true;$('lobby-hint').hidden=false;$('footer-caption').hidden=false;
  game.reset();saved=false;clearSave();$('start-label').textContent='再走一程';$('save-note').textContent='山风一直在这里';$('start').focus();
});
win.addEventListener('cancel',e=>{e.preventDefault();$('back-home').click();});
$('sound').addEventListener('click',async()=>{
  try{const enabled=await audio.toggle();$('sound').innerHTML=icon(enabled?'sound':'muted');$('sound').setAttribute('aria-pressed',String(enabled));$('sound').setAttribute('aria-label',enabled?'关闭山间声音':'开启山间声音');$('sound').title=enabled?'关闭山间声音':'开启山间声音';notify(enabled?'山间风声已开启':'山间声音已关闭');}catch{notify('声音暂未唤醒，请再次点击尝试。');}
});
$('fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{notify('当前浏览器不支持全屏，可用窗口继续游玩。');}});
document.addEventListener('fullscreenchange',()=>{$('fullscreen').setAttribute('aria-label',document.fullscreenElement?'退出全屏':'进入全屏');});
const movementCodes=['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowLeft','ArrowDown','ArrowRight','ShiftLeft','ShiftRight'];
window.addEventListener('keydown',event=>{
  if(event.code==='Escape'&&!guide.open&&!win.open&&game.started){event.preventDefault();openGuide();return;}
  if(guide.open||win.open||!game.started||game.paused||game.won)return;
  if((event.target as HTMLElement).closest('button,a'))return;
  if(movementCodes.includes(event.code)){event.preventDefault();keys.add(event.code);}
  if(event.code==='Space'){event.preventDefault();if(!event.repeat)game.jump();}
  if(event.code==='KeyR'&&!event.repeat){game.respawn();notify('回到存档点，重新出发。');}
});
window.addEventListener('keyup',event=>keys.delete(event.code));
window.addEventListener('blur',()=>{keys.clear();if(game.started&&!game.paused&&!game.won)openGuide();});
document.addEventListener('visibilitychange',()=>{if(document.hidden){keys.clear();if(game.started&&!game.paused&&!game.won)openGuide();if(!game.won&&game.started)persist();}});
document.querySelectorAll<HTMLButtonElement>('[data-key]').forEach(button=>{
  const code=button.dataset.key!;
  button.addEventListener('pointerdown',event=>{event.preventDefault();button.setPointerCapture(event.pointerId);keys.add(code);button.classList.add('pressed');});
  const release=()=>{keys.delete(code);button.classList.remove('pressed');};
  button.addEventListener('pointerup',release);button.addEventListener('pointercancel',release);button.addEventListener('lostpointercapture',release);
  // Keyboard activation remains available for assistive technology.
  button.addEventListener('keydown',event=>{if(event.code==='Space'||event.code==='Enter'){event.preventDefault();keys.add(code);}});
  button.addEventListener('keyup',release);
});
$('touch-jump').addEventListener('pointerdown',event=>{event.preventDefault();game.jump();});
$('touch-jump').addEventListener('keydown',event=>{if(event.key==='Enter'||event.code==='Space'){event.preventDefault();game.jump();}});
const input=()=>({x:Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft')),z:Number(keys.has('KeyS')||keys.has('ArrowDown'))-Number(keys.has('KeyW')||keys.has('ArrowUp')),sprint:keys.has('ShiftLeft')||keys.has('ShiftRight')});
function animate(now:number){
  requestAnimationFrame(animate);if(!world)return;
  const dt=Math.min((now-last)/1000,.1);last=now;accumulator+=dt;
  const direction=input();while(accumulator>=1/120){game.update(1/120,direction);accumulator-=1/120;}
  world.update(game,game.paused?0:dt);
  hudTimer+=dt;saveTimer+=dt;
  if(hudTimer>.2){hudTimer=0;if(game.started)updateHUD();}
  if(saveTimer>2){saveTimer=0;if(game.started&&!game.won)persist();}
}
updateHUD();requestAnimationFrame(animate);
// Read-only diagnostics for development QA. Production builds do not expose it.
if(import.meta.env.DEV)Object.defineProperty(window,'__SUMI__',{value:()=>({x:game.x,y:game.y,z:game.z,grounded:game.grounded,seconds:game.seconds,falls:game.falls,started:game.started,paused:game.paused,won:game.won,seals:[...game.seals],checkpoint:game.checkpoint,renderer:world?.diagnostics()})});
