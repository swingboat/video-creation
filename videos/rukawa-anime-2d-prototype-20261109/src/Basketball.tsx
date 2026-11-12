import React from 'react';
export const Basketball=({x,y,r,angle=0}:{x:number;y:number;r:number;angle?:number})=><svg style={{position:'absolute',left:x-r,top:y-r,width:r*2,height:r*2,rotate:`${angle}deg`,overflow:'visible'}} viewBox="-50 -50 100 100">
 <defs><clipPath id="ball-clip"><circle r="48"/></clipPath></defs>
 <circle r="48" fill="#c87337" stroke="#292223" strokeWidth="3"/>
 <g clipPath="url(#ball-clip)" fill="none" stroke="#382923" strokeWidth="2.6">
 <path d="M-50,-3 Q-3,-16 50,3 M-6,-50 Q9,-4 0,50 M-39,-38 C19,-35 27,32 -34,42 M37,-39 C-21,-20 -24,20 37,40"/>
 </g><path d="M-32 -29 Q-9 -48 17 -41" fill="none" stroke="#f2ad63" strokeWidth="3" opacity=".6"/>
</svg>;
