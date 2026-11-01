"""Original Ötzi supporting cast; shares the studio's pose/mouth contract."""
import math
from art import path,ellipse,group,arm,eyes,mouth,POSES,INK,acting_pose

from ensemble import IDS as ENSEMBLE_IDS
AVATAR_IDS={'otzi','otzi_travel','mira','officer','unknown'} | ENSEMBLE_IDS

def copper_axe():
    return path('M0 12 Q-3 -45 5 -115 L32 -130','none','#765031',10)+path('M25 -141 L61 -139 L61 -119 L28 -121 Z','#c98050',INK,3)+path('M25 -136 L39 -136 M24 -131 L39 -131 M23 -126 L38 -126','none','#ead3a1',3)

def ice_mummy():
    """Non-graphic discovery illustration, not an anatomical reconstruction."""
    p=ellipse(0,12,205,31,'#182b3a44')
    p+=path('M-207 3 L-172 -35 L-91 -47 L-31 -31 L57 -42 L137 -29 L199 -3 L176 29 L63 38 L-79 26 L-175 27 Z','#a9d8e1','#538fa6',3)
    p+=path('M-124 -24 Q-79 -44 -18 -23 L44 -15 L90 -6 L142 -8 L146 4 L82 12 L27 7 Q-20 22 -78 0 Z','#80543f',INK,3)
    p+=path('M-112 -22 Q-102 -69 -155 -62 Q-184 -56 -172 -34 Q-157 -12 -131 -13 Z','#865b43',INK,3)
    p+=path('M-156 -48 L-143 -46 M-141 -35 Q-134 -31 -127 -36','none','#3c3030',2.5)
    p+=path('M-93 -13 Q-72 -38 -46 -46 L-10 -54 L-5 -44 L-42 -32 L-57 -7','none',INK,16)+path('M-93 -13 Q-72 -38 -46 -46 L-10 -54 L-5 -44 L-42 -32 L-57 -7','none','#92664b',10)
    p+=path('M-201 2 L-155 -5 L-119 2 L-71 -8 L-26 8 L16 -8 L74 8 L113 -2 L187 6 L168 30 L63 37 L-79 25 L-175 27 Z','#d9f0ed','#86bbc9',2)
    p+=path('M-183 10 L-142 11 M25 21 L86 24 M129 16 L160 14','none','#f7ffff',3)
    return p

def draw_avatar(actor,t,emotion='neutral',pose='rest',talk='closed',active=False,side=1,local=1):
    if actor['avatar'] in ENSEMBLE_IDS:
        from ensemble import draw_ensemble
        return draw_ensemble(actor,t,emotion,pose,talk,active,side,local)
    kind=actor['avatar'];skin=actor['skin'];cloth=actor['shirt'];hair=actor['hair'];ancient=kind.startswith('otzi')
    if kind=='unknown':
        return ellipse(0,0,85,13,'#172a3d44')+path('M-48 -14 L-43 -173 L-65 -243 L-60 -282 Q-50 -310 -22 -313 L-22 -335 Q-69 -351 -64 -410 Q-63 -457 0 -459 Q63 -457 64 -410 Q69 -351 22 -335 L22 -313 Q50 -310 60 -282 L65 -243 L43 -173 L48 -14 L14 -14 L0 -123 L-14 -14 Z','#48546a',INK,4)+f'<text x="0" y="-369" text-anchor="middle" font-family="Arial" font-size="64" font-weight="bold" fill="#f3e2b7">?</text>'
    beat=math.floor(t*12)/12;bob=math.sin(beat*2)*1.2+(math.sin(beat*11) if active else 0)
    settle=1-math.exp(-max(0,local)*12)*math.cos(max(0,local)*14)
    target=acting_pose(actor,pose);accent=2*math.sin(beat*7) if active and talk!='closed' else 0
    angles=tuple(tuple(r+(v-r)*settle+accent for r,v in zip(rest,p)) for rest,p in zip(POSES['rest'],target))
    p=ellipse(0,0,86,13,'#172a3d44')
    if kind=='otzi_travel':angles=(POSES['rest'][0],angles[1])
    pants='#806046' if ancient else '#344656'
    p+=path('M-43 -159 L-46 -83 L-43 -19 L-12 -19 L-2 -115 L13 -19 L45 -19 L44 -88 L40 -159 Z',pants)
    p+=path('M-39 -139 L-32 -33 M22 -142 L31 -34','none','#ab8960' if ancient else '#4c6172',5)
    shoe='#96734d' if ancient else '#283643'
    p+=path('M-43 -30 Q-53 -17 -67 -10 L-66 0 L-10 0 L-12 -31 Z M13 -31 L10 0 L67 0 L67 -10 Q55 -12 44 -30 Z',shoe)
    if ancient:
        p+=path('M-43 -24 L-22 -18 L-43 -12 L-23 -7 M23 -22 L44 -16 L24 -11 L44 -6','none','#dbc79a',2)
        p+=path('M-45 -37 L-13 -37 M13 -37 L45 -37','none','#bfab7c',4)
    arms=arm(-1,angles[0],skin,cloth,'rest' if kind=='otzi_travel' else pose,t)+arm(1,angles[1],skin,cloth,pose,t)
    torso=path('M-23 -289 Q-54 -290 -67 -265 L-56 -224 L-53 -115 Q0 -101 52 -115 L56 -224 L68 -265 Q52 -287 23 -289 Z',cloth)
    torso+=path('M-22 -302 L-21 -278 Q0 -257 23 -278 L21 -302 Z',skin)
    if ancient:
        torso+=path('M-22 -282 L-4 -262 L-17 -113 L-49 -119 L-43 -241 Z','#b49265',INK,2)
        torso+=path('M23 -281 L-4 -262 L11 -111 L34 -113 L39 -256 Z','#76583e',INK,2)
        torso+=path('M-50 -130 L-46 -167 L-19 -160 L-19 -116 M13 -178 L40 -184 L43 -124','none','#d1b686',2)
        for y in [-242,-219,-196,-139]:torso+=path(f'M-21 {y} l8 3 M33 {y} l8 -3','none','#e1cca1',2)
        torso+=path('M-52 -181 Q0 -170 54 -184 L53 -173 Q0 -160 -53 -170 Z','#473d30',INK,2)
        torso+=path('M27 -177 L48 -181 L51 -151 Q38 -142 26 -150 Z','#95704b',INK,2)
        torso+=path('M-60 -259 l12 4 M-61 -253 l12 4','none','#d4b381',2)
    elif kind=='mira':
        torso+=path('M-23 -282 L-7 -265 L-16 -112 L-52 -117 L-52 -239 Z','#e5e7d6',INK,2)
        torso+=path('M22 -282 L-7 -265 L11 -111 L52 -117 L52 -239 Z','#f1efe1',INK,2)
        torso+=path('M-23 -279 L-34 -249 L-19 -231 L-6 -264 M23 -279 L36 -249 L19 -229 L-6 -264','none','#798d96',2)
        torso+=path('M20 -211 L42 -211 L40 -185 L21 -185 Z','#c6d9d7',INK,2)
        torso+=path('M25 -218 L25 -202 M33 -220 L33 -202','none','#d3875d',3)
        torso+=path('M-20 -174 L-39 -174 L-39 -150 L-19 -150 Z','#c6d9d7',INK,2)
    else:
        torso+=path('M-23 -282 L-3 -268 L-20 -247 L-34 -273 Z M23 -282 L-3 -268 L16 -247 L36 -273 Z','#536c84',INK,2)
        torso+=path('M-3 -265 L-3 -123','none','#78879a',2)
        torso+=path('M-53 -164 L53 -164 L53 -150 L-53 -150 Z','#182a38')
        torso+=path('M-8 -164 L7 -164 L7 -150 L-8 -150 Z','#d5b575',INK,2)
        torso+=path('M16 -235 L41 -235 L40 -216 L28 -210 L16 -217 Z','#d2ba7e',INK,2)
        torso+=path('M-44 -233 L-17 -233 L-17 -219 L-44 -219 Z','#324858',INK,2)
        for y in [-243,-213,-184]:torso+=ellipse(-4,y,2.5,2.5,'#d3ba84')
    p+=group(arms+torso,f'translate(0,{bob})')
    head=ellipse(-72,-363,14,21,skin,INK,3)+ellipse(72,-363,14,21,skin,INK,3)
    head+=path('M-72 -403 Q-77 -451 -12 -457 Q60 -466 74 -417 L69 -350 Q57 -315 8 -301 Q-40 -307 -66 -340 Z',skin)
    head+=path('M55 -423 Q70 -412 65 -351 Q45 -324 9 -309 L8 -301 Q57 -315 69 -350 L74 -417 Z','#553c3344','none')
    if ancient:
        # Balding is an evidence-informed choice; exact hairline/beard is not known.
        head+=path('M-73 -390 Q-82 -419 -65 -440 L-51 -445 Q-65 -418 -60 -384 Z M63 -445 Q82 -426 73 -386 L60 -382 Q67 -417 51 -446 Z',hair,INK,2)
        head+=path('M-41 -418 Q-3 -430 36 -419 M-24 -431 Q-1 -439 20 -432','none','#5c3b2c',2)
        head+=path('M-51 -341 Q-43 -316 -7 -308 Q27 -304 54 -331','none','#583c30',6)
        for x in [-35,-23,-10,3,16,29,40]:head+=path(f'M{x} {-317+abs(x)*.2} l2 4','none',hair,2)
    elif kind=='mira':
        head=ellipse(53,-442,33,32,hair,INK,4)+head
        head+=path('M-73 -378 Q-91 -420 -62 -443 Q-25 -478 32 -452 Q76 -455 77 -408 L66 -378 L54 -417 Q10 -398 -23 -427 Q-34 -411 -59 -409 L-61 -380 Z',hair)
        head+=path('M-55 -440 Q-20 -448 15 -432 M-40 -446 Q-15 -450 6 -443','none','#c8d4cd',4)
    else:
        head+=path('M-73 -380 L-78 -417 Q-72 -449 -21 -451 Q64 -458 77 -416 L70 -379 L56 -411 L51 -427 Q-4 -410 -56 -427 L-58 -381 Z',hair)
        head+=path('M-80 -429 L-70 -458 Q0 -485 73 -458 L81 -429 Z','#32485e')
        head+=path('M-80 -431 Q0 -414 81 -431 L81 -420 Q0 -400 -80 -420 Z','#718297',INK,3)
        head+=path('M-59 -418 Q0 -401 68 -419 Q52 -394 -8 -399 Q-43 -403 -59 -418 Z','#1e2f40',INK,3)
        head+=path('M-9 -451 L3 -455 L15 -451 L12 -437 L3 -431 L-6 -437 Z','#ddc086',INK,2)
    blink=((t+.7)%3.8)<.13
    head+=eyes(emotion,blink,side*3,kind=='mira',actor.get('_acting'))
    if ancient:
        # Dark-brown iris overlays retain the shared blink/eye acting.
        if not blink:
            for x in [-31,31]:head+=ellipse(x+side*3,-370,5.7,min(9.7,15*actor.get('_acting',{}).get('eye_open',1)*.85),'#432d24')+ellipse(x+side*3-2,-374,1.7,2.4,'#f8ecdc')
    if kind=='mira':
        for x in [-31,31]:head+=f'<rect x="{x-23}" y="-392" width="46" height="35" rx="10" fill="none" stroke="#2d4f61" stroke-width="4"/>'
        head+=path('M-8 -379 Q0 -385 8 -379 M-55 -379 L-70 -382 M55 -379 L69 -382','none','#2d4f61',3)
    head+=path('M3 -361 L-2 -349 L6 -347','none','#6b4436',2.5)
    if kind=='officer':head+=path('M0 -338 Q-14 -346 -26 -333 Q-13 -327 0 -333 Q15 -327 27 -333 Q15 -346 0 -338 Z',hair,INK,1)
    head+=mouth(talk,emotion,actor.get('_acting'))
    if kind=='otzi_travel':
        head+=path('M-78 -420 Q-84 -466 -44 -477 Q7 -500 51 -475 Q80 -459 78 -420 L61 -425 L43 -417 L23 -425 L4 -418 L-16 -425 L-38 -418 L-56 -426 Z','#624a35',INK,4)
        head+=path('M-56 -455 l10 -6 M-30 -468 l10 3 M-4 -474 l10 3 M24 -466 l10 4 M49 -454 l10 6','none','#a2865e',4)
        head+=path('M-75 -421 Q-78 -327 0 -294 Q80 -324 76 -421','none','#b69a6c',2)
    tilt=(-3 if emotion=='skeptical' else 2 if emotion=='proud' else -1)+math.sin(beat*1.7)
    tilt+=actor.get('_acting',{}).get('head_tilt',0)
    p+=group(head,f'translate(0,{bob}) rotate({tilt} 0 -292)')
    if kind=='otzi_travel':
        a,b=map(math.radians,angles[0]);wx=-59+math.sin(a)*65+math.sin(a+b)*62;wy=-266+math.cos(a)*65+math.cos(a+b)*62
        p+=group(copper_axe(),f'translate({wx-12},{wy+6+bob}) rotate(-14)')
    return p
