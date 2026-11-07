"""Continuous character choreography and world-space contact targets.

All distances use the existing scene's units. Feet stay at world-space anchors
through stance. The box and pencil each have one continuous transform trajectory.
"""
import math
from mathutils import Vector

FPS=24
DURATION=20
FRAMES=FPS*DURATION
PEN_SCALE=.61
PEN_GRIP=.19
PEN_PALM_Z=.040
PICK_YAW=-2.34
PLACE_YAW=-2.40
DRAW_YAW=-3.68

def sat(x):return min(1.0,max(0.0,x))
def ease(a,b,t):
    u=sat((t-a)/(b-a));return u*u*u*(10+u*(-15+6*u))
def mix(a,b,u):return a*(1-u)+b*u
def vec(x):return Vector(x)
def R(yaw):return Vector((math.cos(yaw),math.sin(yaw),0))
def F(yaw):return Vector((math.sin(yaw),-math.cos(yaw),0))
def blend_pos(a,b,a_t,b_t,t):return vec(a).lerp(vec(b),ease(a_t,b_t,t))

def cruise(a,b,t,ramp=.40):
    """Distance fraction with cosine velocity ramps and a constant-speed middle."""
    d=b-a;u=max(0,min(d,t-a));r=min(ramp,d/3)
    if u<r:return .5*(u-r/math.pi*math.sin(math.pi*u/r))/(d-r)
    if u>d-r:
        v=d-u;return 1-.5*(v-r/math.pi*math.sin(math.pi*v/r))/(d-r)
    return (u-r/2)/(d-r)

def root_at(t):
    if t<.60:return vec((5.27,-.25,0))
    if t<2.10:return blend_pos((5.27,-.25,0),(5.13,-1.30,0),.60,2.10,t)
    if t<4.05:return vec((5.13,-1.30,0))
    if t<5.30:return vec((5.13,-1.30,0)).lerp(vec((4.42,-2.17,0)),cruise(4.05,5.30,t,.20))
    if t<12.70:return vec((4.42,-2.17,0)).lerp(vec((-5.72,-2.17,0)),cruise(5.30,12.70,t))
    if t<14.35:return vec((-5.72,-2.17,0))
    return blend_pos((-5.72,-2.17,0),(-5.26,-2.25,0),14.35,15.25,t)

def yaw_at(t):
    if t<1.60:return mix(0,PICK_YAW,ease(.55,1.60,t))
    if t<3.90:return PICK_YAW
    if t<5.30:return mix(PICK_YAW,-math.pi/2,ease(3.90,5.30,t))
    if t<12.55:return -math.pi/2
    if t<13.20:return mix(-math.pi/2,PLACE_YAW,ease(12.55,13.20,t))
    if t<14.25:return PLACE_YAW
    return mix(PLACE_YAW,DRAW_YAW,ease(14.25,15.35,t))

def moving(t):
    return (ease(.55,.85,t)*(1-ease(2.03,2.30,t))+
            ease(4.00,4.40,t)*(1-ease(12.80,13.25,t))+
            ease(14.30,14.55,t)*(1-ease(15.20,15.50,t)))

def posture(t):
    pick=ease(2.12,2.92,t)*(1-ease(3.20,4.08,t))
    place=ease(13.08,13.80,t)*(1-ease(14.15,14.55,t))
    draw=ease(15.20,15.90,t)
    walk=moving(t)
    phase=(t-4.03)/.62
    z=.43-.23*pick-.23*place-.27*draw-.050*walk
    bob=.010*walk*math.cos(phase*math.tau*2)
    sway=.018*walk*math.sin(phase*math.tau)
    drawing_reach=.075*ease(17.75,18.05,t)*(1-ease(19.65,20.0,t))
    lean=.20*pick+.21*place+.16*draw+.05*walk+drawing_reach
    return {'pelvis_z':z+bob,'lean':lean,'sway':sway,'walk':walk,'phase':phase,'draw':draw}

def foot_default(t,side,lead=0):
    return root_at(t+lead)+R(yaw_at(t))*side*.14+F(yaw_at(t))*.055+vec((0,0,.105))

# Explicit alternating swing intervals; world-space anchors between intervals.
SWINGS={-1:[],1:[]}
for k in range(5):
    start=.65+k*.34;side=1 if k%2==0 else -1
    SWINGS[side].append((start,start+.25,2.30))
k=0
while 4.03+k*.31<13.02:
    start=4.03+k*.31;side=1 if k%2==0 else -1
    SWINGS[side].append((start,start+.24,13.30));k+=1
for k in range(4):
    start=14.35+k*.29;side=1 if k%2==0 else -1
    SWINGS[side].append((start,start+.23,15.50))

FOOT_EVENTS={}
for side in [-1,1]:
    events=[];anchor=foot_default(0,side);anchor_yaw=0
    for idx,(start,end,group_end) in enumerate(SWINGS[side]):
        later=[x for x in SWINGS[side][idx+1:] if x[0]<group_end]
        landing_t=group_end if not later else end
        landing=foot_default(landing_t,side,.105 if later else 0)
        events.append({'start':start,'end':end,'from':anchor.copy(),'to':landing.copy(),'yaw0':anchor_yaw,'yaw1':yaw_at(landing_t)})
        anchor=landing;anchor_yaw=yaw_at(landing_t)
    FOOT_EVENTS[side]=events

def foot_at(t,side):
    pos=foot_default(0,side);yaw=0
    for e in FOOT_EVENTS[side]:
        if t<e['start']:break
        if t<=e['end']:
            u=sat((t-e['start'])/(e['end']-e['start']))
            p=e['from'].lerp(e['to'],ease(0,1,u))
            p.z+=.135*math.sin(math.pi*u)**1.4+.008*abs(math.sin(math.tau*u))
            yy=mix(e['yaw0'],e['yaw1'],ease(0,1,u))
            return p,yy,.18*math.sin(math.tau*u),False
        pos=e['to'];yaw=e['yaw1']
    return pos.copy(),yaw,0,True

def box_at(t):
    initial=vec((4.75,-.92,.16))
    target=vec((-6.07,-1.73,.16))
    carry=root_at(t)+F(yaw_at(t))*.39+vec((0,0,.69+.012*moving(t)*math.cos((t-4.3)/.70*math.tau*2)))
    if t<3.0:return initial,PICK_YAW
    if t<3.85:return initial.lerp(carry,ease(3.0,3.85,t)),mix(PICK_YAW,yaw_at(t),ease(3,3.85,t))
    if t<13.20:return carry,yaw_at(t)
    if t<14.15:return carry.lerp(target,ease(13.20,14.15,t)),mix(yaw_at(t),PLACE_YAW,ease(13.20,14.15,t))
    return target,PLACE_YAW

def resample(points,count):
    lengths=[0]
    for a,b in zip(points,points[1:]):lengths.append(lengths[-1]+(b-a).length)
    result=[];j=0
    for i in range(count):
        d=lengths[-1]*i/(count-1)
        while j<len(lengths)-2 and lengths[j+1]<d:j+=1
        u=(d-lengths[j])/max(1e-9,lengths[j+1]-lengths[j]);result.append(points[j].lerp(points[j+1],u))
    return result

STEM=[vec((-5.08,-1.98,.043)),vec((-5.08,-1.84,.043))]
FLOWER=resample([vec((-5.08+(.09+.025*math.sin(5*(a+math.pi/2)))*math.cos(a),-1.75+(.09+.025*math.sin(5*(a+math.pi/2)))*math.sin(a),.043)) for a in [-math.pi/2+math.tau*j/800 for j in range(801)]],241)

def on_path(points,u):
    x=sat(u)*(len(points)-1);i=min(len(points)-2,int(x));return points[i].lerp(points[i+1],x-i)

def pen_at(t):
    initial=vec((-4.97,-1.92,.052));axis0=vec((-1,0,0));axis1=vec((-.18,.24,.40)).normalized()
    if t<15.80:return initial,axis0
    if t<16.85:
        u=ease(15.80,16.85,t);tip=initial.lerp(STEM[0],u);tip.y+=.22*math.sin(math.pi*u);tip.z+=.12*math.sin(math.pi*u)
        axis=axis0.lerp(axis1,u).normalized();return tip,axis
    if t<17.75:return on_path(STEM,ease(16.85,17.75,t)),axis1
    if t<19.75:return on_path(FLOWER,ease(17.75,19.75,t)),axis1
    tip=FLOWER[-1].copy();tip.z+=.035*ease(19.75,20,t);return tip,axis1

def hand_targets(t):
    root=root_at(t);yaw=yaw_at(t);post=posture(t)
    free_swing=post['walk']*(1-ease(2.0,2.3,t) if t<3 else ease(14.45,14.70,t)*(1-ease(15.1,15.35,t)))
    rest={s:root+R(yaw)*s*.29+F(yaw)*(.03+s*.075*free_swing*math.sin(post['phase']*math.tau))+vec((0,0,post['pelvis_z']+.12)) for s in [-1,1]}
    box,byaw=box_at(t)
    acquire=ease(2.30,3.0,t)*(1-ease(14.15,14.45,t))
    hands={s:rest[s].lerp(box+R(byaw)*s*.225+vec((0,0,.015)),acquire) for s in [-1,1]}
    tip,axis=pen_at(t);grip=tip+axis*PEN_GRIP+vec((0,0,PEN_PALM_Z))
    hands[1]=hands[1].lerp(grip,ease(15.25,15.80,t))
    hands[-1]=hands[-1].lerp(vec((-5.16,-2.16,.105)),ease(15.30,16.40,t))
    return hands

def blink(t):
    amount=0
    for center in [.35,2.85,4.03,7.35,10.6,13.1,15.8,18.7]:
        u=abs(t-center)/.095
        if u<1:amount=max(amount,(1-u*u)**2)
    return max(.055,1-.96*amount)

def two_bone(shoulder,wrist,pole,a,b):
    delta=wrist-shoulder;actual=delta.length;d=max(.001,min(a+b-.001,actual));n=delta.normalized()
    toward=pole-shoulder;perp=toward-n*toward.dot(n)
    if perp.length<1e-6:perp=n.cross(Vector((0,0,1)))
    perp.normalize();along=(a*a-b*b+d*d)/(2*d);height=math.sqrt(max(.000001,a*a-along*along))
    return shoulder+n*along+perp*height,max(0,actual-(a+b))
