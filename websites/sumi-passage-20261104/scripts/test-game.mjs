import assert from 'node:assert/strict';
import {Game,PLATFORMS} from '../src/game.ts';
const idle={x:0,z:0,sprint:false};
let passed=0;
function test(name,fn){fn();passed++;console.log(`PASS ${name}`);}
function advance(game,seconds,input=idle){for(let i=0;i<Math.round(seconds*120);i++)game.update(1/120,input);}
test('jump rises, then lands on the same island',()=>{
  const g=new Game();g.start();g.jump();advance(g,.25);assert(g.y>1.2&&!g.grounded);
  advance(g,1);assert(g.grounded);assert.equal(g.y,0);
});
test('pause freezes movement, gravity, and timer',()=>{
  const g=new Game();g.start();g.paused=true;const before=g.save();advance(g,3,{x:1,z:1,sprint:true});assert.deepEqual(g.save(),before);assert.equal(g.x,-.9);
});
test('diagonal movement has the same speed as straight movement',()=>{
  const a=new Game(),b=new Game();a.start();b.start();advance(a,.3,{x:1,z:0,sprint:false});advance(b,.3,{x:1,z:1,sprint:false});
  assert(Math.abs(Math.hypot(b.x+.9,b.z-1.4)-(a.x+.9))<1e-8);
});
test('fall restores the checkpoint without losing collected seals',()=>{
  const g=new Game();g.start();g.seals.add(0);advance(g,4,{x:0,z:1,sprint:false});assert(g.falls>=1);assert(g.seals.has(0));
});
test('invalid and inconsistent browser saves are rejected',()=>{
  const g=new Game();assert(!g.restore(null));assert(!g.restore({version:1,checkpoint:99,seals:[],seconds:1,falls:0}));
  assert(!g.restore({version:1,checkpoint:3,seals:[0],seconds:1,falls:0}));assert(!g.restore({version:1,checkpoint:0,seals:[9],seconds:1,falls:0}));
  assert(!g.restore({version:1,checkpoint:0,seals:[],seconds:Infinity,falls:0}));
});
test('valid save restores at the middle island',()=>{
  const g=new Game();assert(g.restore({version:1,checkpoint:3,seals:[0,1],seconds:42,falls:2}));assert.equal(g.x,17.5);assert.equal(g.y,1.6);assert.equal(g.seals.size,2);
});
test('the gate requires all three seals',()=>{
  const g=new Game();g.start();g.x=35;g.z=-7.2;g.y=3.3;advance(g,.1);assert(!g.won);
  g.seals=new Set([0,1,2]);advance(g,.1);assert(g.won);
});
test('all seven islands are traversable using normal movement and jumping',()=>{
  const g=new Game();g.start();const events=[];g.onEvent=e=>events.push(e.type);
  const moveTo=(x,z,limit=700)=>{
    for(let i=0;i<limit;i++){
      const dx=x-g.x,dz=z-g.z;if(g.won||Math.hypot(dx,dz)<.06)return;
      const length=Math.hypot(dx,dz);g.update(1/120,{x:dx/length,z:dz/length,sprint:false});
      assert.equal(g.falls,0,`fell while walking to ${x},${z}`);
    }
    assert.fail(`could not walk to ${x},${z}`);
  };
  moveTo(0,0);
  for(let i=1;i<PLATFORMS.length;i++){
    const from=PLATFORMS[i-1],to=PLATFORMS[i];moveTo(from.x+from.w/2-.52,from.z);
    g.jump();let landed=false;
    for(let step=0;step<240;step++){
      const dx=to.x-g.x,dz=to.z-g.z,len=Math.hypot(dx,dz);
      g.update(1/120,{x:dx/len,z:dz/len,sprint:false});
      assert.equal(g.falls,0,`jump to island ${i} failed`);
      if(step>15&&g.grounded&&g.x>from.x+from.w/2){landed=true;break;}
    }
    assert(landed,`could not land on island ${i}`);moveTo(to.x,to.z);
  }
  // The gate may finish the run as soon as the final island center is reached.
  if(!g.won)moveTo(35,-7.2);
  assert.equal(g.seals.size,3);assert.equal(g.checkpoint,3);assert(g.won);assert.equal(g.falls,0);
  assert.equal(events.filter(e=>e==='seal').length,3);assert.equal(events.filter(e=>e==='win').length,1);
});
console.log(`${passed} gameplay checks passed.`);
