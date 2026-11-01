"""Small, deterministic direction compiler; no model calls or executable script input."""
import math,re
EMOTIONS=('neutral','happy','proud','skeptical','worried','surprised','deadpan')
POSES=('rest','present','question','point','shrug','hips','wave','fold')
SHOTS=('speaker','reaction','two','wide')
CUSTOM={'left_shoulder':(-150,150),'left_elbow':(-160,160),'right_shoulder':(-150,150),'right_elbow':(-160,160),'brow_tilt':(-15,15),'eye_open':(.25,1.5),'mouth_curve':(-18,18),'head_tilt':(-20,20)}
ALIASES={'emotion':'emotion','expression':'emotion','gesture':'pose','pose':'pose','camera':'shot','shot':'shot','pause':'pause',**{k:k for k in CUSTOM}}
SYNONYMS={'emotion':{'dry':'deadpan','sarcastic':'deadpan','amused':'happy','smiling':'happy','concerned':'worried','shocked':'surprised','curious':'skeptical','sad':'worried','confused':'skeptical','angry':'skeptical'},'pose':{'arms folded':'fold','hands on hips':'hips','pointing':'point','waving':'wave','shrugging':'shrug','explaining':'present','relaxed':'rest'},'shot':{'close-up':'speaker','closeup':'speaker','two-shot':'two','wide shot':'wide','reaction shot':'reaction'}}

def validate_custom(custom):
    if not isinstance(custom,dict):raise ValueError('Custom acting must be an object.')
    for key,val in custom.items():
        if key not in CUSTOM:raise ValueError(f'Unknown custom acting control: {key}')
        lo,hi=CUSTOM[key]
        if isinstance(val,bool) or not isinstance(val,(int,float)) or not math.isfinite(val) or not lo<=val<=hi:raise ValueError(f'{key} must be between {lo} and {hi}.')
    return custom

def compile_direction(text):
    if not isinstance(text,str) or len(text)>3000:raise ValueError('Directions must be under 3000 characters.')
    result={};custom={};warnings=[];rest=text.lower().strip()
    # Explicit key=value controls take priority over prose aliases.
    for m in re.finditer(r'([a-z_]+)\s*=\s*([^;,\n]+)',rest):
        raw,value=m.groups();key=ALIASES.get(raw)
        if not key:raise ValueError(f'Unknown direction control: {raw}')
        value=value.strip()
        if key in CUSTOM or key=='pause':
            try:v=float(value)
            except ValueError:raise ValueError(f'{key} needs a number.')
            if key=='pause':
                if not math.isfinite(v) or not 0<=v<=5:raise ValueError('Pause must be 0–5 seconds.')
                result[key]=v
            else:custom[key]=v
        else:
            allowed={'emotion':EMOTIONS,'pose':POSES,'shot':SHOTS}[key]
            mapped=SYNONYMS.get(key,{}).get(value,value)
            if mapped not in allowed:raise ValueError(f'Unsupported {raw}: {value}. Choose {", ".join(allowed)} or use custom acting controls.')
            result[key]=mapped
            if mapped!=value:warnings.append(f'{value} uses the {mapped} rig preset; adjust custom acting for a different look.')
    rest=re.sub(r'([a-z_]+)\s*=\s*([^;,\n]+)',' ',rest)
    for key,allowed in [('emotion',EMOTIONS),('pose',POSES),('shot',SHOTS)]:
        if key in result:continue
        matches=[]
        for phrase,mapped in {**{v:v for v in allowed},**SYNONYMS.get(key,{})}.items():
            if re.search(r'\b'+re.escape(phrase)+r'\b',rest):matches.append((phrase,mapped))
        unique=list(dict.fromkeys(v for _,v in matches))
        if len(unique)==1:
            result[key]=unique[0]
            for phrase,mapped in matches:
                rest=re.sub(r'\b'+re.escape(phrase)+r'\b',' ',rest)
                if phrase in ('angry','sad','confused','curious'):warnings.append(f'{phrase} approximated with {mapped}; use custom face controls for precision.')
        elif len(unique)>1:warnings.append(f'Multiple {key} cues; choose one or use per-line directions.')
    if custom:result['acting']=validate_custom(custom)
    residual=re.sub(r'\b(and|with|a|an|the|look|delivery|expression|gesture|camera|please|be|then)\b|[\s,;./-]','',rest)
    if residual:warnings.append('Some prose remains an editorial note. Only the shown controls will animate; walking, props interaction and new body actions need artwork.')
    return {'controls':result,'warnings':list(dict.fromkeys(warnings))}
