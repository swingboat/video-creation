"""Shared deterministic choreography. Metres; +Y is the attacking direction."""
import math
FPS=24
RELEASE=9.0
SWISH=13.6
RIM=(0.,12.,3.05)
def clamp(x):return min(1.,max(0.,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def mix(a,b,u):return tuple(x+(y-x)*u for x,y in zip(a,b))
def hero_root(t):
    u=ease(t/5.1)
    x=-2.4+1.2*u;y=1.8+3.0*u
    if t>5.1:y-=.38*ease((t-5.1)/1.0)
    bounce=.025*math.sin(t*9) if t<5.1 else 0
    crouch=-.24*ease((t-6.3)/1.3)*(1-ease((t-7.6)/.7))
    jump=.46*math.sin(math.pi*clamp((t-7.75)/2.65)) if 7.75<t<10.4 else 0
    return x,y,bounce+crouch+jump
RELEASE_POINT=(*hero_root(RELEASE)[:2],hero_root(RELEASE)[2]+2.34)
def ball_at(t):
    x,y,z=hero_root(t)
    if t<4.8:
        phase=t*1.25
        h=.125+1.04*abs(math.cos(math.pi*phase))
        return x+.47,y+.28,h
    if t<7:
        return mix((x+.47,y+.28,1.14+z),(x+.12,y+.35,1.37+z),ease((t-4.8)/2.2))
    if t<RELEASE:
        return mix((x+.12,y+.35,1.37+z),RELEASE_POINT,ease((t-7)/(RELEASE-7)))
    if t<=SWISH:
        u=(t-RELEASE)/(SWISH-RELEASE);d=1.55;px,py,pz=RELEASE_POINT
        return px*(1-u),py+(12-py)*u,pz+(3.05-pz)*u+4.905*d*d*u*(1-u)
    dt=(t-SWISH)*.55
    impact=(-2.3+math.sqrt(2.3**2+4*4.905*(3.05-.125)))/(2*4.905)
    if dt<impact:return (dt*.12,12+dt*.4,3.05-2.3*dt-4.905*dt*dt)
    age=dt-impact
    # Continuous damped bounces, with exact shared floor-contact endpoints.
    period=.78;height=.62;elapsed=0.
    while age>period and period>.08:
        age-=period;elapsed+=period;period*=.66;height*=.4356
    u=min(1,age/period)
    return (.12*impact+(dt-impact)*.4,12+.4*impact-(dt-impact)*.3,.125+4*height*u*(1-u))

def game_clock(t):
    # Actual play is slowed during gather, release and ball flight.
    if t<5.2:return 5.2-t*.67
    if t<9.15:return 1.716*(1-(t-5.2)/3.95)
    return 0.
