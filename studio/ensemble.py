"""Five original everyday-character rigs, using the shared acting controls."""
import math
from art import path,ellipse,group,arm,eyes,mouth,POSES,INK,acting_pose
IDS={'ellie','jun','anaya','malik','rowan'}

def draw_ensemble(actor,t,emotion,pose,talk,active,side,local):
    kind=actor['avatar'];skin=actor['skin'];cloth=actor['shirt'];hair=actor['hair'];custom=actor.get('_acting',{})
    beat=math.floor(t*12)/12;bob=math.sin(beat*2)*1.2+(math.sin(beat*10) if active else 0)
    settle=1-math.exp(-max(0,local)*12)*math.cos(max(0,local)*14)
    target=acting_pose(actor,pose);accent=2*math.sin(beat*7) if active and talk!='closed' else 0
    angles=tuple(tuple(r+(v-r)*settle+accent for r,v in zip(rest,p)) for rest,p in zip(POSES['rest'],target))
    p=ellipse(0,0,86,13,'#172a3d44')
    pants={'ellie':'#486581','jun':'#39424f','anaya':'#293e50','malik':'#33475a','rowan':'#70564c'}[kind]
    p+=path('M-45 -155 L-47 -81 L-43 -23 L-12 -23 L0 -109 L14 -23 L46 -23 L47 -83 L44 -155 Z',pants)
    p+=path('M-34 -134 L-29 -34 M30 -132 L33 -34','none','#ffffff22',5)
    p+=path('M-45 -29 L-12 -29 L-10 -3 L-65 -3 L-67 -12 Q-53 -14 -45 -29 Z M14 -29 L45 -29 Q54 -15 68 -13 L68 -3 L11 -3 Z','#ebe7d9')
    p+=path('M-63 -8 L-14 -8 M16 -8 L65 -8 M-42 -22 l15 4 M28 -20 l15 -3','none','#6b7780',2)
    arms=arm(-1,angles[0],skin,cloth,pose,t)+arm(1,angles[1],skin,cloth,pose,t)
    torso=path('M-23 -289 Q-52 -288 -66 -266 L-57 -225 L-51 -129 Q0 -115 52 -129 L57 -225 L67 -266 Q54 -287 22 -289 Z',cloth)
    torso+=path('M-22 -302 L-20 -278 Q0 -260 22 -278 L21 -302 Z',skin)
    if kind in ('ellie','jun','anaya','malik'):
        under={'ellie':'#f5efe1','jun':'#dde7de','anaya':'#efd1ad','malik':'#f0e7c9'}[kind]
        torso+=path('M-21 -282 Q0 -264 23 -282 L31 -129 Q0 -120 -31 -128 Z',under,INK,2)
        torso+=path('M-21 -283 L-38 -254 L-24 -232 L-31 -128 M23 -283 L39 -254 L25 -232 L31 -129','none',INK,3)
        if kind=='jun':
            torso+=path('M-49 -228 L-31 -228 L-31 -210 L-48 -212 M32 -228 L49 -228 L48 -211 L32 -210','none',INK,2)
        elif kind=='anaya':torso+=path('M-49 -163 L-34 -169 M35 -169 L48 -163','none','#efcd9c',3)
        elif kind=='malik':
            torso+=path('M-25 -282 L-13 -247 M26 -282 L15 -247','none','#f2cdb5',3)
            torso+=path('M-48 -154 L-31 -154 M32 -154 L48 -154','none',INK,2)
    else:
        torso+=path('M-24 -283 Q0 -254 26 -283 M-52 -140 Q0 -128 52 -140','none','#bdcbb0',6)
        torso+=path('M-31 -210 L30 -210','none','#c4bd88',9)
    p+=group(arms+torso,f'translate(0,{bob})')
    back=''
    if kind=='ellie':back=path('M-77 -406 Q-91 -465 -7 -470 Q80 -478 85 -404 L84 -288 Q62 -276 45 -294 L-53 -291 L-89 -303 Z',hair)
    if kind=='anaya':
        for x,y,rx,ry in [(53,-457,33,34),(76,-432,23,28),(85,-402,19,24),(82,-373,17,22)]:back+=ellipse(x,y,rx,ry,hair,INK,3)
    head=back+ellipse(-73,-364,13,20,skin,INK,3)+ellipse(73,-364,13,20,skin,INK,3)
    jaw='M-72 -405 Q-78 -453 -10 -460 Q66 -464 74 -411 L69 -351 Q53 -313 5 -303 Q-43 -309 -68 -343 Z'
    head+=path(jaw,skin)
    head+=path('M63 -410 L66 -352 Q51 -322 7 -309','none','#00000016',7)
    if kind=='ellie':
        head+=path('M-73 -380 Q-92 -426 -63 -454 Q-17 -479 32 -458 Q80 -452 78 -410 L65 -382 L57 -423 Q29 -437 4 -442 Q-17 -413 -58 -410 L-61 -378 Z',hair)
        head+=path('M-56 -443 Q-24 -454 -5 -450 M22 -450 Q52 -444 65 -427','none','#f7df92',5)
    elif kind=='jun':
        head+=path('M-74 -380 L-80 -418 Q-74 -456 -36 -458 Q0 -478 38 -456 Q78 -449 77 -411 L68 -382 L57 -411 L50 -431 Q3 -409 -46 -424 L-60 -415 L-62 -380 Z',hair)
        head+=path('M-50 -444 Q-6 -456 38 -442 M-37 -436 Q-2 -443 17 -437','none','#4b5661',4)
    elif kind=='anaya':
        head+=path('M-73 -378 Q-87 -415 -72 -439 Q-64 -469 -37 -458 Q-16 -481 7 -462 Q32 -475 49 -453 Q76 -453 78 -415 L66 -379 L56 -412 Q24 -410 -1 -438 Q-22 -412 -59 -409 L-61 -377 Z',hair)
        head+=path('M-63 -438 Q-49 -450 -35 -440 M-23 -451 Q-9 -460 4 -447 M17 -453 Q30 -457 42 -442','none','#654c43',4)
    elif kind=='malik':
        head+=path('M-74 -383 L-81 -419 Q-78 -452 -46 -455 Q-20 -474 11 -461 Q44 -469 68 -443 Q82 -432 76 -395 L65 -379 L57 -415 Q0 -407 -57 -420 L-62 -381 Z',hair)
        for x,y in [(-62,-435),(-40,-448),(-17,-453),(7,-454),(31,-451),(54,-438)]:head+=ellipse(x,y,13,12,hair,INK,2)
        head+=path('M-45 -337 Q-32 -315 0 -311 Q33 -315 48 -337','none',hair,5)
    else:
        head+=path('M-74 -379 Q-95 -426 -63 -449 L-75 -468 L-39 -459 L-27 -483 L-5 -464 L22 -480 L33 -459 L65 -463 L58 -445 Q86 -433 77 -405 L67 -380 L55 -412 Q16 -402 -19 -428 Q-37 -412 -61 -414 L-63 -379 Z',hair)
        head+=path('M-50 -446 Q-16 -436 12 -456 M15 -447 L39 -446','none','#d49b69',5)
    blink=((t+(.4 if kind in ('ellie','anaya') else 1.7))%3.9)<.13
    head+=eyes(emotion,blink,side*3,kind in ('ellie','anaya'),custom)
    head+=path('M2 -361 L-3 -349 L5 -347','none','#744d40',2.5)
    if kind in ('anaya','rowan'):
        for x in [-31,31]:head+=f'<rect x="{x-23}" y="-393" width="46" height="36" rx="{16 if kind=="rowan" else 7}" fill="none" stroke="{("#bd854b" if kind=="rowan" else "#333955")}" stroke-width="4"/>'
        head+=path('M-8 -381 Q0 -387 8 -381 M-54 -380 L-71 -384 M54 -380 L71 -384','none','#333955',3)
    if kind in ('ellie','rowan'):
        for x,y in [(-48,-350),(-39,-346),(-51,-341),(39,-348),(48,-351),(50,-341)]:head+=ellipse(x,y,1.6,1.6,'#a56646')
    if kind=='anaya':head+=ellipse(-74,-342,5,7,'#d6b260',INK,1.5)+ellipse(74,-342,5,7,'#d6b260',INK,1.5)
    head+=mouth(talk,emotion,custom)
    tilt=(-3 if emotion=='skeptical' else 2 if emotion=='proud' else -1)+math.sin(beat*1.7)+custom.get('head_tilt',0)
    p+=group(head,f'translate(0,{bob}) rotate({tilt} 0 -292)')
    return p
