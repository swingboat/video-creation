"""Deterministic smooth schooling paths. No Blender callbacks are needed at playback."""
import math
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline

ROOT=Path(__file__).resolve().parents[1]
FPS=24
FRAMES=480

def make_route(radius, half, height, phase):
    # A rounded racetrack: long swimming passes and broad, continuous turns.
    pts=[]
    for a in np.linspace(-math.pi/2,math.pi/2,7):
        pts.append([-.45+half+radius*math.cos(a),radius*math.sin(a)])
    for x in np.linspace(half,-half,5)[1:-1]:pts.append([-.45+x,radius])
    for a in np.linspace(math.pi/2,3*math.pi/2,7):
        pts.append([-.45-half+radius*math.cos(a),radius*math.sin(a)])
    for x in np.linspace(-half,half,5)[1:-1]:pts.append([-.45+x,-radius])
    pts.append(pts[0])
    u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(np.array(pts),axis=0),axis=1))]
    spline=CubicSpline(u,np.array(pts),bc_type='periodic')
    dense=np.linspace(0,u[-1],24001)
    xy=spline(dense)
    ds=np.linalg.norm(np.diff(xy,axis=0),axis=1)
    arc=np.r_[0,np.cumsum(ds)]
    def at(distance):
        q=np.interp(distance%arc[-1],arc,dense)
        xy=spline(q)
        # Small vertical exploration, with a separate phase for each fish.
        a=q/u[-1]*math.tau
        z=height+.023*math.sin(a+phase)+.009*math.sin(2*a-phase)
        return np.r_[xy,z]
    return at,float(arc[-1])

out={'fps':FPS,'frames':FRAMES,'model':'arc-length rounded schooling routes; two depths; opposite directions','fish':[]}
for i in range(9):
    upper=i>=6
    group=i-6 if upper else i
    direction=-1 if upper else 1
    radius=(.64,.69,.60,.71,.66,.62,.57,.67,.72)[i]
    height=(.805,.825,.795,.815,.805,.83,1.09,1.10,1.08)[i]
    scale=(1.0,.83,.94,.86,1.04,.89,.86,.93,.79)[i]
    at,length=make_route(radius,1.67-(i%3)*.055,height,i*1.19)
    offset=(group/(3 if upper else 6)+(.055 if upper else .012))*length
    speed0=.98 if upper else .83
    def dist(t):
        # Integrating speed makes acceleration smooth and prevents framewise jitter.
        return offset+direction*length/11.3*(speed0*t+.18/.62*(math.cos(.3)-math.cos(.62*t+.3))+.025/.91*(math.cos(i*1.3)-math.cos(.91*t+i*1.3)))
    samples=[];phase=i*2.399
    for fr in range(FRAMES):
        t=fr/FPS;p=at(dist(t));p0=at(dist(t-.01));p1=at(dist(t+.01))
        velocity=(p1-p0)/.02;speed=float(np.linalg.norm(velocity));v=velocity/speed
        acc=(p1-2*p+p0)/.0001
        yaw=math.atan2(v[1],v[0]);pitch=-math.asin(v[2])
        curvature=float((velocity[0]*acc[1]-velocity[1]*acc[0])/(np.linalg.norm(velocity[:2])**3))
        bank=max(-.20,min(.20,curvature*speed*speed*.10))
        # Faster swimming increases tailbeat frequency; phase is integrated, never reset.
        frequency=1.35+.78*speed/(scale*.68)
        phase+=math.tau*frequency/FPS
        samples.append({'p':[round(float(x),7) for x in p],'yaw':yaw,'pitch':pitch,'bank':bank,'speed':speed,'phase':phase,'turn':max(-1.6,min(1.6,curvature))})
    out['fish'].append({'id':i,'scale':scale,'radius':radius,'height':height,'direction':direction,'route_length':length,'samples':samples})
# Body-volume proximity is checked independently from screen-space overlap.
minimum=10.;closest=None
for fr in range(FRAMES):
    for i in range(9):
        a=out['fish'][i];sa=a['samples'][fr];pa=np.array(sa['p'])
        for j in range(i):
            b=out['fish'][j];sb=b['samples'][fr];pb=np.array(sb['p'])
            delta=pa-pb
            # Ellipsoid broad phase; vertical radii exclude transparent fin membranes.
            normalized=float(np.linalg.norm(delta/np.array([.50,.20,.105*(a['scale']+b['scale'])])))
            if normalized<minimum:minimum=normalized;closest=[fr+1,j,i]
out['spacing']={'min_normalized_center_distance':minimum,'closest':closest}
(ROOT/'docs/fish-paths.json').write_text(json.dumps(out,separators=(',',':')))
print(json.dumps({'fish':9,'frames':FRAMES,'spacing':out['spacing']}))
