import React from 'react';import {clipsReady} from './media-status';import {PendingFrame} from './PendingFrame';import {BasketAction} from './BasketAction';
export const RimScene=()=>clipsReady.rim?<BasketAction/>:<PendingFrame image="art/rim-scene.png"/>;
