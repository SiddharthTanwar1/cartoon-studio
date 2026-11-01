"""Typed, local explanatory visuals. Charts use explicit data, never model guesses."""
import io, math
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import resvg_py
from art import character, group

FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
KINDS={'bar','line','diagram','picture'}

def asset_path(root,name):
    base=(Path(root)/'assets').resolve();p=(base/name).resolve()
    if not p.is_relative_to(base) or p.suffix.lower() not in {'.png','.jpg','.jpeg','.webp'}:
        raise ValueError('Visual image must be a PNG, JPG or WebP inside assets.')
    return p

def validate_visual(spec,root):
    mode=spec.get('scene_type','dialogue')
    if mode not in ('dialogue','explainer'):raise ValueError('Scene type must be dialogue or explainer.')
    v=spec.get('visual')
    if mode=='dialogue':
        if v is not None or any('visual_step' in l for l in spec.get('lines',[])):raise ValueError('Add Scene type: explainer for a visual or @visual cue.')
        return
    if spec.get('format')!='landscape':raise ValueError('Explainer scenes need landscape format for the central visual and side characters.')
    if spec.get('prop'):raise ValueError('Explainer scenes use Prop: none.')
    if not isinstance(v,dict) or v.get('type') not in KINDS:raise ValueError('Explainer needs a Visual: bar, line, diagram or picture.')
    for k,limit in [('title',75),('caption',130),('source',150),('unit',25),('prompt',2000),('image',240)]:
        if not isinstance(v.get(k,''),str) or len(v.get(k,''))>limit:raise ValueError(f'Visual {k} must be text up to {limit} characters.')
    if not v.get('title','').strip():raise ValueError('Supply a Visual title.')
    if v.get('animation','reveal') not in ('none','reveal'):raise ValueError('Visual animation must be none or reveal.')
    kind=v['type']
    if kind in ('bar','line'):
        labels=v.get('labels');values=v.get('values')
        limit=6 if kind=='bar' else 12
        if not isinstance(labels,list) or not (2 if kind=='line' else 1)<=len(labels)<=limit or any(not isinstance(x,str) or not 1<=len(x)<=28 for x in labels):raise ValueError(f'Visual labels need short names, up to {limit} entries.')
        if not isinstance(values,list) or len(values)!=len(labels) or any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>1e12 for x in values):raise ValueError('Visual values must be finite numbers matching labels.')
        if kind=='bar' and min(values)<0:raise ValueError('Bar values must be nonnegative; use a line for signed values.')
        if not v.get('source','').strip():raise ValueError('Charts require Visual source: cite the source, or explicitly label illustrative data.')
        if not v.get('unit','').strip():raise ValueError('Charts require Visual unit (for example hours or percent).')
    elif kind=='diagram':
        nodes=v.get('nodes')
        if not isinstance(nodes,list) or not 2<=len(nodes)<=6 or any(not isinstance(x,str) or not 1<=len(x)<=60 for x in nodes):raise ValueError('Diagram needs 2–6 node labels, each up to 60 characters.')
    else:
        image=v.get('image','');prompt=v.get('prompt','')
        if not image and not 10<=len(prompt)<=2000:raise ValueError('Picture needs Visual image: an asset filename, or Visual prompt: 10–2000 characters.')
        if image:
            p=asset_path(root,image)
            if not p.is_file():raise ValueError('Visual image does not exist inside assets.')
            with Image.open(p) as im:im.verify()
    n=len(v.get('values',v.get('nodes',[1])))
    for l in spec.get('lines',[]):
        step=l.get('visual_step')
        if step is not None and (type(step)!=int or not 0<=step<=n):raise ValueError(f'@visual must be a whole step from 0 to {n}.')

@lru_cache(maxsize=32)
def font(size):return ImageFont.truetype(FONT,max(8,int(size)))

def label(draw,text,box,size,fill='#26344a',center=False):
    x,y,w,h=box
    for fs in range(max(8,int(size)),7,-1):
        f=font(fs);rows=[];row=''
        for word in text.split():
            candidate=(row+' '+word).strip()
            if row and draw.textlength(candidate,font=f)>w:rows.append(row);row=word
            else:row=candidate
        if row:rows.append(row)
        if len(rows)*(fs+3)<=h and all(draw.textlength(r,font=f)<=w for r in rows):break
    for r in rows:
        draw.text((x+(w-draw.textlength(r,font=f))/2 if center else x,y),r,font=f,fill=fill);y+=fs+3

@lru_cache(maxsize=16)
def picture(path,mtime):
    with Image.open(path) as im:return im.convert('RGBA')

def progress(v,t,line,timeline):
    n=len(v.get('values',v.get('nodes',[1])))
    if v.get('animation')=='none':return float(n)
    cues=[l for l in timeline if 'visual_step' in l and l['start']<=t]
    if cues:
        current=cues[-1];previous=cues[-2]['visual_step'] if len(cues)>1 else 0
        p=max(0,min(1,(t-current['start'])/.8));p=p*p*(3-2*p)
        return previous+(current['visual_step']-previous)*p
    if any('visual_step' in l for l in timeline):return 0.
    return n*max(0,min(1,(t-.35)/2.5))

def board(spec,W,H,t,line,timeline,root):
    v=spec['visual'];im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
    x,y,w,h=round(W*.2),round(H*.07),round(W*.6),round(H*.7)
    d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill='#fffdf5',outline='#26344a',width=3)
    pad=W*.015
    label(d,v['title'],(x+pad,y+12,w-2*pad,H*.075),H*.035,center=True)
    label(d,v.get('caption',''),(x+pad,y+h-H*.13,w-2*pad,H*.055),H*.021,center=True)
    label(d,v.get('source',''),(x+pad,y+h-H*.065,w-2*pad,H*.05),H*.018,fill='#526074',center=True)
    bx,by,bw,bh=x+pad,y+H*.115,w-2*pad,h-H*.27
    p=progress(v,t,line,timeline);kind=v['type']
    if kind in ('bar','line'):
        vals=v['values'];names=v['labels'];n=len(vals)
        left=bx+W*.04;right=bx+bw-W*.012;top=by+H*.04;bottom=by+bh-H*.045
        lo=min(0,min(vals));hi=max(0,max(vals));hi=hi if hi>lo else lo+1
        def yy(value):return bottom-(value-lo)/(hi-lo)*(bottom-top)
        for k in range(5):
            value=lo+(hi-lo)*k/4;cy=yy(value)
            d.line((left,cy,right,cy),fill='#d9dee5',width=1)
            label(d,f'{value:g}',(bx,cy-7,W*.037,H*.025),H*.017)
        label(d,v['unit'],(left,by,right-left,H*.033),H*.02)
        if kind=='bar':
            slot=(right-left)/n
            for i,(name,val) in enumerate(zip(names,vals)):
                f=max(0,min(1,p-i));cx=left+(i+.5)*slot;cy=yy(val*f)
                if f>0:d.rounded_rectangle((cx-slot*.3,cy,cx+slot*.3,bottom),radius=3,fill='#268c97')
                if f>=1:label(d,f'{val:g}',(cx-slot*.4,cy-H*.035,slot*.8,H*.03),H*.023,center=True)
                label(d,name,(cx-slot*.48,bottom+7,slot*.96,H*.045),H*.019,center=True)
        else:
            coords=[(left+i*(right-left)/(n-1),yy(val)) for i,val in enumerate(vals)]
            for i,(cx,cy) in enumerate(coords):
                f=max(0,min(1,p-i))
                if i and f>0:
                    a,b=coords[i-1];d.line((a,b,a+(cx-a)*f,b+(cy-b)*f),fill='#268c97',width=max(2,round(H*.005)))
                if f>=1:d.ellipse((cx-4,cy-4,cx+4,cy+4),fill='#d78339')
                label(d,names[i],(cx-(right-left)/n*.45,bottom+7,(right-left)/n*.9,H*.045),H*.016,center=True)
    elif kind=='diagram':
        nodes=v['nodes'];n=len(nodes);cols=2 if n<=4 else 3;rows=math.ceil(n/cols);cw=bw/cols;ch=bh/rows
        for i,node in enumerate(nodes):
            cx=bx+(i%cols)*cw;cy=by+(i//cols)*ch;active=p>=i+1
            box=(cx+cw*.06,cy+ch*.12,cx+cw*.94,cy+ch*.85)
            d.rounded_rectangle(box,radius=12,fill='#d6f0e9' if active else '#edf0f3',outline='#268c97' if active else '#c4cbd3',width=2)
            label(d,f'{i+1}. {node}',(box[0]+10,box[1]+10,box[2]-box[0]-20,box[3]-box[1]-20),H*.03,fill='#203444' if active else '#82909f',center=True)
            if i%cols<cols-1 and i<n-1:
                ax=cx+cw;ay=cy+ch*.49;d.line((ax-cw*.045,ay,ax+cw*.045,ay),fill='#268c97',width=3);d.polygon([(ax+cw*.045,ay),(ax,ay-5),(ax,ay+5)],fill='#268c97')
        # Numbering makes the continuation to the next row explicit.
    else:
        if v.get('image'):
            path=asset_path(root,v['image']);pic=picture(str(path),path.stat().st_mtime_ns)
            pic=ImageOps.contain(pic,(round(bw),round(bh)),Image.Resampling.LANCZOS)
            if p<1:pic=pic.copy();pic.putalpha(pic.getchannel('A').point(lambda a:round(a*p)))
            im.alpha_composite(pic,(round(bx+(bw-pic.width)/2),round(by+(bh-pic.height)/2)))
        else:label(d,'Illustration will generate when this scene renders.',(bx,by,bw,bh),H*.03,center=True)
    return im

@lru_cache(maxsize=4)
def background(path,mtime,W,H):
    with Image.open(path) as raw:return ImageOps.fit(raw.convert('RGBA'),(W,H),method=Image.Resampling.LANCZOS)

def compose(spec,line,t,local,timeline,W,H,root):
    bgpath=Path(root)/'assets'/spec.get('background','garage.png')
    bg=background(str(bgpath),bgpath.stat().st_mtime_ns,W,H).copy()
    bg.alpha_composite(board(spec,W,H,t,line,timeline,root))
    parts=[];scale=min(H*.0011,W*.00055)
    for i,(name,a) in enumerate(spec['characters'].items()):
        active=name==line['speaker'];actor=dict(a,_acting=line.get('acting',{}) if active else {})
        from render import mouth_shape
        char=character(actor,t,line.get('emotion','neutral') if active else 'neutral',line.get('pose','present') if active else 'rest',mouth_shape(line,local) if active else 'closed',active,1 if i==0 else -1,local)
        parts.append(group(char,f'translate({W*(.095 if i==0 else .905)},{H*.8}) scale({scale})'))
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'+''.join(parts)+'</svg>'
    bg.alpha_composite(Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg,width=W,height=H))).convert('RGBA'))
    return bg
