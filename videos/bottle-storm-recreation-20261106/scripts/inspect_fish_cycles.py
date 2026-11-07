import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;records=[]
for i in range(9):
    o=bpy.data.objects['Fish v3 %02d • flexible body and fins'%i]
    key=o.data.shape_keys;action=key.animation_data.action
    curves=[f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
    errors=[]
    for frame in range(1,480,4):
        for fraction in (.15,.5,.85):
            scene.frame_set(frame,subframe=fraction)
            values=[k.value for k in key.key_blocks if k.name.startswith('Swim phase')]
            errors.append(abs(sum(values)-1))
    records.append({'fish':i,'action':action.name,'interpolation':sorted({p.interpolation for f in curves for p in f.keyframe_points}),'max_subframe_weight_sum_error':max(errors)})
report={'cycles':records,'note':'Subframe checks describe the saved native animation, including samples used by motion blur.'}
(ROOT/'outputs/checks/fish/subframe-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
