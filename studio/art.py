"""Original, editable 2D character rigs. No generated frames or identity drift."""
import math
from html import escape

INK='#202335'
def path(d, fill='none', stroke=INK, sw=4):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
def ellipse(x,y,rx,ry,fill,stroke='none',sw=3):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def group(content,transform=''):
    return f'<g transform="{transform}">{content}</g>'

POSES={
 'rest': ((-12,-8),(12,8)), 'present': ((-12,-8),(48,100)),
 'question': ((-30,-105),(43,110)), 'point': ((-12,-8),(68,100)),
 'shrug': ((-48,-100),(48,100)), 'hips': ((-52,125),(52,-125)),
 'wave': ((-12,-8),(120,40)), 'fold': ((-40,150),(40,-150))
}

def arm(side, angles, skin, shirt, pose, t):
    sx=side*59; sy=-266
    a,b=angles; a=math.radians(a); b=math.radians(b)
    ex=sx+math.sin(a)*65; ey=sy+math.cos(a)*65
    wx=ex+math.sin(a+b)*62; wy=ey+math.cos(a+b)*62
    limb=f'M{sx} {sy} Q{sx+math.sin(a)*35} {sy+math.cos(a)*35} {ex} {ey} L{wx} {wy}'
    p=path(limb,'none',INK,30)+path(limb,'none',skin,23)
    p+=path(f'M{sx} {sy} L{sx+math.sin(a)*43} {sy+math.cos(a)*43}', 'none',shirt,34)
    p+=path(f'M{sx-16*math.cos(a)+math.sin(a)*43} {sy+16*math.sin(a)+math.cos(a)*43} l{32*math.cos(a)} {-32*math.sin(a)}','none',INK,3)
    hand=path('M-11 -7 Q-19 -16 -22 -8 L-14 5 Q-15 19 -6 24 Q6 29 16 16 L19 2 Q20 -7 15 -8 Q11 -10 9 -5 Q6 -13 2 -10 Q-1 -14 -6 -9 Z',skin)
    hand+=path('M-6 2 L-5 13 M2 1 L2 14 M9 0 L8 11','none','#9f614f',1.5)
    if pose=='point' and side==1:
        hand=path('M-11 6 L-13 -28 Q-11 -38 -6 -30 L-2 -8 Q4 -13 7 -6 Q13 -10 16 -3 L16 14 Q12 25 0 23 L-14 15 L-22 4 Q-22 -3 -17 -1 Z',skin)
    if pose in ('present','question','shrug'):
        hand=path('M-12 2 L-26 -6 Q-31 -13 -24 -13 L-11 -7 L-14 -21 Q-14 -28 -9 -26 L-2 -11 L0 -26 Q3 -32 6 -25 L7 -10 L12 -24 Q16 -28 17 -20 L15 -6 L21 -16 Q26 -18 25 -10 L20 8 Q10 21 -1 18 Z',skin,INK,3)
        hand+=path('M-5 1 Q3 -3 11 2','none','#9f614f',1.5)
    return p+group(hand,f'translate({wx},{wy}) rotate({-math.degrees(a+b)*.55})')

def acting_pose(actor,pose):
    base=POSES.get(pose,POSES['rest']);a=actor.get('_acting',{})
    return ((a.get('left_shoulder',base[0][0]),a.get('left_elbow',base[0][1])),(a.get('right_shoulder',base[1][0]),a.get('right_elbow',base[1][1])))

def eyes(emotion,blink,gaze,customer,acting=None):
    acting=acting or {}
    p=''
    for side in [-1,1]:
        x=side*31
        if blink or emotion=='happy' and customer:
            p+=path(f'M{x-16} -372 Q{x} -384 {x+16} -372','none',INK,4)
        else:
            ry=22 if emotion=='surprised' else (17 if customer else 15)
            ry*=acting.get('eye_open',1)
            p+=ellipse(x,-372,19,ry,'#fff9ef',INK,3)
            p+=ellipse(x+gaze,-370,6.2,min(10.5,ry*.85),'#3b4254')+ellipse(x+gaze-2,-374,2,3,'#ffffff')
            if emotion in ('deadpan','skeptical','proud'):
                p+=path(f'M{x-20} -381 L{x+20} {-376 if (emotion=="skeptical" and side==1) else -381}','none',INK,4)
        by=-404
        if emotion=='worried':d=f'M{x-19} {by+8*side} Q{x} {by-5} {x+17} {by-7*side}'
        elif emotion=='skeptical':d=f'M{x-17} {by+side*4} Q{x} {by-7*side} {x+17} {by+side*3}'
        elif emotion=='surprised':d=f'M{x-18} {by-3} Q{x} {by-16} {x+18} {by-3}'
        else:d=f'M{x-18} {by} Q{x} {by-6} {x+17} {by+1}'
        if 'brow_tilt' in acting:
            tilt=acting['brow_tilt']*side
            d=f'M{x-18} {by+tilt} Q{x} {by-3} {x+17} {by-tilt}'
        p+=path(d,'none',INK,5)
    return p

def mouth(shape,emotion,acting=None):
    acting=acting or {}
    y=-328
    if shape=='closed':
        if 'mouth_curve' in acting:return path(f'M-20 {y} Q0 {y+acting["mouth_curve"]} 20 {y}','none',INK,3.5)
        if emotion in ('happy','proud'): return path(f'M-21 {y-4} Q0 {y+12} 22 {y-4}','none',INK,3.5)
        if emotion=='worried':return path(f'M-16 {y+3} Q0 {y-8} 16 {y+3}','none',INK,3.5)
        return path(f'M-15 {y} Q0 {y+2} 15 {y}','none',INK,3.5)
    if shape=='o':return ellipse(0,y+1,10,16,'#4d293b',INK,3)+ellipse(1,y+8,5,4,'#dc7a88')
    if shape=='wide':
        return path(f'M-24 {y-9} Q0 {y-3} 24 {y-9} Q19 {y+21} 0 {y+22} Q-18 {y+18} -24 {y-9} Z','#442839',INK,3)+path(f'M-21 {y-7} Q0 {y-2} 21 {y-7} L17 {y+1} Q0 {y+6} -18 {y+1} Z','#fff9ec','none')+path(f'M-10 {y+18} Q0 {y+7} 12 {y+17} Q0 {y+24} -10 {y+18}','#df7989','none')
    if shape=='teeth':return path(f'M-20 {y-3} Q0 {y-9} 20 {y-3} L18 {y+7} Q0 {y+12} -18 {y+7} Z','#fff8e9',INK,3)
    return path(f'M-20 {y-5} Q0 {y} 20 {y-5} Q15 {y+13} 0 {y+13} Q-15 {y+12} -20 {y-5} Z','#4b2938',INK,3)+path(f'M-10 {y+11} Q0 {y+4} 10 {y+11}','none','#df7989',4)

def character(actor,t,emotion='neutral',pose='rest',talk='closed',active=False,side=1,local=1):
    if actor.get('avatar'):
        from avatars import draw_avatar
        return draw_avatar(actor,t,emotion,pose,talk,active,side,local)
    customer=actor.get('rig')=='customer';skin=actor.get('skin','#e9aa83');shirt=actor.get('shirt','#ee794e');hair=actor.get('hair','#383045')
    beat=math.floor(t*12)/12
    bob=(math.sin(beat*2.4)*1.3 + (math.sin(beat*13)*1.2 if active else 0))
    tilt=(-3 if emotion=='skeptical' else 2 if emotion=='proud' else -1)+math.sin(beat*1.7)*1.1
    blink=((t+(1.3 if customer else 0))%3.7)<.13
    p=ellipse(0,0,92,15,'#172a3d55')
    # Sturdy silhouette: fitted trousers, folded cuffs, oversized sneakers.
    p+=path('M-48 -145 L-52 -78 L-46 -22 L-13 -22 L-4 -103 L11 -23 L46 -23 L48 -86 L41 -146 Z','#30364b')
    p+=path('M-40 -135 L-31 -35 M22 -133 L30 -36','none','#414b61',7)
    p+=path('M-48 -31 L-11 -31 L-11 -15 L-48 -15 Z M10 -31 L47 -31 L48 -15 L10 -15 Z','#616d7e',INK,3)
    p+=path('M-47 -18 Q-60 -8 -70 -8 L-70 0 L-10 0 L-10 -18 Z','#f2e4cd')+path('M10 -18 L10 0 L71 0 L71 -9 Q61 -9 47 -18 Z','#f2e4cd')
    p+=path('M-68 -3 L-12 -3 M13 -3 L68 -3','none','#aaaca7',3)
    p+=path('M-47 -12 L-31 -9 M-44 -16 L-28 -13 M31 -10 L47 -13 M29 -14 L43 -17','none',INK,2)
    target=acting_pose(actor,pose);settle=1-math.exp(-max(0,local)*12)*math.cos(max(0,local)*14)
    accent=math.sin(beat*7)*2.8 if active and talk!='closed' else 0
    angles=tuple(tuple(r+(v-r)*settle+accent for r,v in zip(rest,p)) for rest,p in zip(POSES['rest'],target))
    arms=arm(-1,angles[0],skin,shirt,pose,t)+arm(1,angles[1],skin,shirt,pose,t)
    torso=path('M-22 -287 Q-54 -286 -69 -263 L-58 -220 L-51 -142 Q0 -123 50 -142 L57 -220 L70 -264 Q48 -285 23 -287 Z',shirt)
    torso+=path('M-55 -240 L-42 -158 Q-4 -145 49 -153 L50 -142 Q0 -123 -51 -142 Z','#20304b','none') if customer else path('M-49 -242 L-42 -156 Q-2 -146 50 -155 L50 -142 Q0 -123 -51 -142 Z','#b54f46','none')
    torso+=path('M-23 -300 L-22 -274 Q0 -252 23 -274 L22 -301 Z',skin)
    if customer:
        torso+=path('M-22 -280 Q-51 -282 -42 -260 Q-31 -241 0 -257 Q29 -239 42 -260 Q48 -281 23 -281 Q7 -264 -22 -280 Z','#3a5b78')
        torso+=path('M-12 -257 L-16 -214 M14 -257 L17 -214','none','#d5e8db',3)
        torso+=path('M-29 -184 L29 -184 L35 -160 L-35 -160 Z','#416879',INK,2)
        torso+=path('M-14 -229 L2 -242 L18 -230 L0 -212 Z','#eec17f',INK,2)
    else:
        torso+=path('M-22 -282 L-3 -266 L-22 -247 L-35 -272 Z M23 -282 L-3 -266 L14 -247 L36 -272 Z','#f5af75')
        torso+=path('M-3 -265 L-3 -146','none','#a84c42',3)
        torso+=path('M14 -238 L42 -238 L40 -214 L16 -214 Z','#c85e49',INK,2)
        torso+=path('M18 -231 L34 -231','none','#f7ddac',4)
        torso+=path('M-39 -238 L-13 -238','none','#ffc78c',3)
        for yy in [-234,-203,-170]:torso+=ellipse(-5,yy,2,2,INK)
    p+=group(arms+torso,f'translate(0,{bob})')
    # Face and hair have their own pivot, so acting is not whole-image wobble.
    head=ellipse(-73,-360,14,22,skin,INK,3)+ellipse(73,-360,14,22,skin,INK,3)
    head+=path('M-72 -404 Q-75 -436 -45 -449 Q0 -465 46 -444 Q75 -429 74 -400 L69 -346 Q55 -311 8 -299 Q-42 -305 -66 -337 Z',skin)
    head+=path('M53 -417 Q76 -418 71 -381 L65 -342 Q45 -314 8 -305 L9 -299 Q55 -311 69 -346 L74 -400 Z','#b46b5c','none')
    head+=path('M-72 -365 Q-79 -372 -78 -357 M73 -365 Q80 -372 77 -357','none','#a96658',2)
    head+=ellipse(-44,-345,15,5,'#d6817755')+ellipse(45,-345,15,5,'#d6817755')
    if customer:
        head+=path('M-74 -363 L-87 -399 Q-95 -443 -64 -451 L-76 -474 L-42 -462 L-46 -490 L-16 -469 L1 -499 L15 -470 L44 -488 L43 -464 L74 -473 L68 -449 Q99 -425 76 -362 L61 -396 L55 -415 Q14 -402 -20 -426 Q-31 -411 -59 -411 L-61 -379 Z',hair)
        head+=path('M-62 -450 Q-22 -438 4 -468 L-1 -449 Q35 -441 63 -455 Q44 -426 13 -429 Q-11 -443 -33 -433 Z','#4c5063','none')
        head+=path('M-83 -407 Q-88 -386 -71 -366','none','#86c5cb',3)
        head+=ellipse(-74,-340,4,6,'#e7c680',INK,1.5)
    else:
        head+=path('M-73 -368 L-86 -399 L-79 -432 L-93 -445 L-58 -447 L-67 -473 L-37 -459 L-31 -490 L-7 -466 L16 -497 L24 -466 L57 -483 L53 -455 L81 -457 L73 -437 Q90 -415 71 -371 L56 -406 L52 -426 Q-7 -398 -58 -425 L-61 -389 Z',hair)
        head+=path('M-68 -442 L-45 -440 L-47 -458 L-28 -442 L-24 -470 L-5 -448 L15 -477 L14 -448 L46 -467 L39 -441 Q-8 -425 -51 -439 Z','#67556a','none')
        head+=path('M-83 -401 L-72 -379 M69 -429 L75 -414','none','#83c7c9',3)
    head+=eyes(emotion,blink,side*4,customer,actor.get('_acting'))
    head+=path('M3 -361 L-2 -349 L6 -347','none','#a96d57',2.5)
    head+=mouth(talk,emotion,actor.get('_acting'))
    tilt+=actor.get('_acting',{}).get('head_tilt',0)
    p+=group(head,f'translate(0,{bob}) rotate({tilt} 0 -290)')
    return p

def robot(t,reveal=False):
    x=500+math.sin(t*.8)*8; y=842
    p=ellipse(0,4,87,18,'#14263866')
    p+=path('M-72 -32 Q-68 -57 0 -57 Q68 -57 72 -32 L73 -8 Q56 13 -2 13 Q-61 13 -73 -8 Z','#29354b')
    p+=ellipse(0,-31,72,27,'#e8e3d0',INK,4)
    p+=path('M-65 -27 Q0 -3 65 -27','none','#b8c2b4',4)
    p+=path('M-32 -10 Q0 -4 32 -10 L30 5 Q0 12 -30 5 Z','#172735',INK,2)
    p+=ellipse(-15,-1,4,5,'#73efc8')+ellipse(15,-1,4,5,'#73efc8')
    p+=ellipse(0,-34,20,7,'#596b7d',INK,2)+ellipse(0,-35,9,3,'#7bf6c9')
    p+=path('M-57 -35 Q-67 -109 0 -111 Q67 -109 57 -35','none',INK,15)+path('M-57 -35 Q-63 -100 0 -103 Q63 -100 57 -35','none','#ec9956',7)
    p+=path('M-66 -50 L-49 -50 L-46 -25 L-65 -23 Z M49 -50 L66 -50 L65 -23 L46 -25 Z','#ed9f5d',INK,4)
    if reveal:
        p+=path('M63 -13 L97 -49','none',INK,5)+path('M83 -60 L119 -54 L114 -10 L78 -16 Z','#f3edcf',INK,3)
        p+=path('M90 -46 L108 -43 M88 -38 L105 -35 M86 -30 L99 -28','none','#7c8790',2)
    return group(p,f'translate({x},{y})')

def camera(spec,line,t,local,duration):
    fmt=spec.get('format','square');ratio={'square':1,'landscape':16/9,'portrait':9/16}[fmt]
    names=list(spec['characters']);idx=names.index(line['speaker']);shot=line.get('shot','speaker')
    if shot=='wide':h=940;cx=480;cy=480
    elif shot=='two':h=800;cx=480;cy=470
    elif shot=='reaction':h=520;cx=300 if idx==1 else 690;cy=520
    else:h=520;cx=300 if idx==0 else 690;cy=520
    if fmt=='portrait':
        if shot in ('wide','two'):h=940;cx=480;cy=480
        else:cx=330 if (idx==0) != (shot=='reaction') else 630;h=510;cy=570
    if len(names)==1:cx=480
    if fmt=='landscape' and shot in ('wide','two'):h=720;cy=540
    # Intentional slow 2% push, reset on each cut.
    h*=1-.02*min(1,local/max(.1,duration));w=h*ratio
    return (max(-160,min(1120-w,cx-w/2)),max(0,min(960-h,cy-h/2)),w,h)

def foreground(spec,line,t,local,duration,shape='closed'):
    names=list(spec['characters']);speaker=line['speaker']; p=''
    reveal=line.get('shot')=='wide'
    for i,name in enumerate(names[:2]):
        active=name==speaker;actor=dict(spec['characters'][name],_acting=line.get('acting',{}) if name==speaker else {})
        emotion=line.get('emotion','neutral') if active else ('skeptical' if i==1 else 'neutral')
        pose=line.get('pose','rest') if active else 'rest'
        char=character(actor,t,emotion,pose,shape if active else 'closed',active,1 if i==0 else -1,local)
        # Characters stay planted at the same world coordinates through cuts.
        x=300 if i==0 else 690;scale=1.0 if i==0 else .96
        if spec.get('format')=='portrait':x=330 if i==0 else 630;scale*=.78
        if len(names)==1:x=480
        p+=group(char,f'translate({x},820) scale({scale})')
    if spec.get('prop')=='robot':p+=robot(t,reveal)
    if spec.get('prop')=='otzi_ice':
        from avatars import ice_mummy
        p+=group(ice_mummy(),'translate(480,853)')
    return p

def svg_frame(spec,line,t,local,duration,shape='closed',size=720,background=None):
    x,y,w,h=camera(spec,line,t,local,duration)
    ratio=w/h;W=int(size*ratio);H=size
    bg=f'<image href="{escape(str(background),quote=True)}" x="-160" y="0" width="1280" height="960" preserveAspectRatio="xMidYMid slice"/>' if background else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="{x} {y} {w} {h}">{bg}{foreground(spec,line,t,local,duration,shape)}</svg>'
