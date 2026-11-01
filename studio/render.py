"""Script -> cached local speech -> timing -> animated MP4. No remote services."""
from __future__ import annotations
import argparse, bisect, hashlib, io, json, math, os, re, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
import resvg_py
from art import svg_frame, camera, POSES

ROOT=Path(__file__).resolve().parents[1]
os.environ['PATH']='/opt/homebrew/bin:/usr/local/bin:'+os.environ.get('PATH','/usr/bin:/bin')
MODEL_ROOT=Path(os.environ.get('CARTOON_MODEL_ROOT',str(Path.home()/'AI_EXPLAINER_FACTORY')))
FONT=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
EMOTIONS={'neutral','happy','proud','skeptical','worried','surprised','deadpan'}
SHOTS={'speaker','reaction','two','wide'}

def run(args,**kwargs):return subprocess.run([str(x) for x in args],check=True,**kwargs)
def log(s):print(s,flush=True)
def validate(s,root=ROOT):
    root=Path(root).resolve()
    if not isinstance(s,dict):raise ValueError('The episode must be a JSON object.')
    chars=s.get('characters',{})
    if not isinstance(chars,dict) or not 1<=len(chars)<=2:raise ValueError('Choose one or two cast members.')
    for name,c in chars.items():
        if not isinstance(name,str) or not name.strip() or len(name)>40:raise ValueError('Character names must be 1–40 characters.')
        if c.get('rig') not in ('mechanic','customer'):raise ValueError('Choose the mechanic or customer rig.')
        if c.get('avatar'):
            from avatars import AVATAR_IDS
            if c['avatar'] not in AVATAR_IDS:raise ValueError('Choose an installed avatar from the cast library.')
        for field in ('shirt','hair','skin'):
            if not re.fullmatch(r'#[a-fA-F0-9]{6}',c.get(field,'')):raise ValueError(f'{name}: use a hex color for {field}.')
        if not isinstance(c.get('voice',''),str) or len(c.get('voice',''))>600:raise ValueError('Voice descriptions must be under 600 characters.')
    from directions import validate_custom
    if s.get('prop') not in (None,'','robot','otzi_ice'):raise ValueError('Unknown prop.')
    prompt=s.get('background_prompt','')
    if not isinstance(prompt,str) or prompt and not 10<=len(prompt)<=2000:raise ValueError('Set prompts must be 10–2000 characters.')
    if not isinstance(s.get('direction',''),str) or len(s.get('direction',''))>3000:raise ValueError('Scene directions must be under 3000 characters.')
    lines=s.get('lines',[])
    if not isinstance(lines,list) or not 1<=len(lines)<=80:raise ValueError('Use 1–80 dialogue lines.')
    for i,l in enumerate(lines):
        if l.get('speaker') not in chars:raise ValueError(f'Line {i+1}: unknown speaker.')
        if not isinstance(l.get('text'),str) or not 1<=len(l['text'].strip())<=400:raise ValueError(f'Line {i+1}: use 1–400 characters.')
        if l.get('emotion','neutral') not in EMOTIONS:raise ValueError(f'Line {i+1}: unknown expression.')
        if l.get('pose','rest') not in POSES:raise ValueError(f'Line {i+1}: unknown gesture.')
        if l.get('shot','speaker') not in SHOTS:raise ValueError(f'Line {i+1}: unknown camera shot.')
        validate_custom(l.get('acting',{}))
        if not isinstance(l.get('direction',''),str) or len(l.get('direction',''))>3000:raise ValueError('Line directions must be under 3000 characters.')
        pause=float(l.get('pause',.25))
        if not math.isfinite(pause) or not 0<=pause<=5:raise ValueError('Pauses must be 0–5 seconds.')
    if s.get('format','square') not in ('square','landscape','portrait'):raise ValueError('Unknown format.')
    if s.get('resolution',720) not in (480,720,1080):raise ValueError('Resolution must be 480, 720, or 1080.')
    if s.get('fps',30) not in (24,30):raise ValueError('Frame rate must be 24 or 30.')
    bg=(root/'assets'/s.get('background','garage.png')).resolve()
    if not bg.is_relative_to(root/'assets') or not bg.is_file():raise ValueError('Choose an existing background from assets.')
    from visuals import validate_visual
    validate_visual(s,root)
    return s

def norm(s):
    from num2words import num2words
    s=re.sub(r'\$([\d,]+(?:\.\d+)?)',lambda m:m.group(1)+' dollars',s)
    s=re.sub(r'\b\d[\d,]*(?:\.\d+)?\b',lambda m:num2words(m.group().replace(',','')),s)
    s=s.replace('%',' percent').replace('&',' and')
    return re.findall(r"[a-z]+(?:'[a-z]+)?",s.lower())
def wer(a,b):
    a=norm(a);b=norm(b);r=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        z=[i]
        for j,y in enumerate(b,1):z.append(min(z[-1]+1,r[j]+1,r[j-1]+(x!=y)))
        r=z
    return r[-1]/max(1,len(a))

def align(wav,text,out):
    binary=MODEL_ROOT/'runtime/whisper.cpp/build/bin/whisper-cli';model=MODEL_ROOT/'models/whisper/ggml-small.en.bin'
    base=out.with_suffix('');jp=base.with_suffix('.json')
    if not jp.exists():
        run([binary,'-m',model,'-f',wav,'-ng','-np','-l','en','-ml','1','-sow','-oj','-of',base],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    d=json.loads(jp.read_text());segments=d.get('transcription',[])
    hyp=' '.join(x.get('text','').strip() for x in segments)
    score=wer(text,hyp)
    # Keep the authored wording; align equal word runs to the recognized timestamps.
    words=text.split();dur=sf.info(wav).duration
    timed=[]
    for seg in segments:
        tx=seg.get('text','').strip();off=seg.get('offsets',{})
        if tx:timed.append({'word':tx,'start':float(off.get('from',0))/1000,'end':float(off.get('to',0))/1000})
    import difflib
    starts=[None]*len(words); ends=[None]*len(words)
    def key(x):return ''.join(norm(x))
    sm=difflib.SequenceMatcher(a=[key(x) for x in words],b=[key(x['word']) for x in timed],autojunk=False)
    for a,b,n in sm.get_matching_blocks():
        for k in range(n):starts[a+k]=timed[b+k]['start'];ends[a+k]=timed[b+k]['end']
    for i,w in enumerate(words):
        if starts[i] is None:
            left=next((j for j in range(i-1,-1,-1) if ends[j] is not None),-1)
            right=next((j for j in range(i+1,len(words)) if starts[j] is not None),len(words))
            lo=ends[left] if left>=0 else .05; hi=starts[right] if right<len(words) else dur
            step=max(.02,(hi-lo)/(right-left-1));starts[i]=lo+step*(i-left-1);ends[i]=starts[i]+step
    result=[{'word':w,'start':max(0,min(dur,float(starts[i]))),'end':max(0,min(dur,float(ends[i])))} for i,w in enumerate(words)]
    return result,score,hyp

def prepare(spec,out,skip_voice=False):
    out.mkdir(parents=True,exist_ok=True);sp=out/'episode.json';sp.write_text(json.dumps(spec,indent=2))
    if not skip_voice or not (out/'voices.json').exists():
        run([MODEL_ROOT/'envs/audio/bin/python',ROOT/'studio/voices.py',sp,out])
    voices=json.loads((out/'voices.json').read_text());timeline=[];audio=[];offset=.35;rate=48000;qa=[]
    if len(voices)!=len(spec['lines']) or any(v['text']!=l['text'] or v['speaker']!=l['speaker'] for v,l in zip(voices,spec['lines'])):
        raise ValueError('Cached voices do not match this script. Render again without --reuse-voices.')
    audio.append(np.zeros(round(offset*rate),np.float32))
    for i,(line,v) in enumerate(zip(spec['lines'],voices)):
        log(f'Checking dialogue and timing · {i+1}/{len(voices)}')
        wav=out/f'line-{i:03}.wav';ref=out/f'line-{i:03}-16k.wav'
        candidates=[];original_key=v.get('cache_key')
        for attempt in range(3):
            if attempt:
                log(f'Automatically improving line {i+1} · take {attempt+1}')
                retry=out/f'retake-{i}-{attempt}';retry.mkdir(exist_ok=True)
                retry_spec={**spec,'lines':[{**line,'take':int(line.get('take',0))+attempt}]}
                retry_file=retry/'episode.json';retry_file.write_text(json.dumps(retry_spec))
                run([MODEL_ROOT/'envs/audio/bin/python',ROOT/'studio/voices.py',retry_file,retry])
                v=json.loads((retry/'voices.json').read_text())[0]
            run(['ffmpeg','-v','error','-y','-i',v['path'],'-ac','1','-ar',rate,wav])
            run(['ffmpeg','-v','error','-y','-i',wav,'-ac','1','-ar','16000',ref])
            data,sr=sf.read(wav,dtype='float32');dur=len(data)/rate
            alignment_key=hashlib.sha256(ref.read_bytes()+line['text'].encode()).hexdigest()[:12]
            words,score,hyp=align(ref,line['text'],out/f'align-{alignment_key}.json')
            candidates.append((score,v,words,hyp,data.copy(),dur))
            if score<=.12 or line.get('audio'):break
        score,v,words,hyp,data,dur=min(candidates,key=lambda x:x[0]);sf.write(wav,data,rate,subtype='PCM_16')
        voices[i]=v
        if original_key and score<=.35 and not line.get('audio'):
            (ROOT/'assets/voice_cache'/f'{original_key}.chosen.json').write_text(json.dumps({'path':v['path'],'word_error_rate':score}))
        qa.append({'line':i+1,'expected':line['text'],'heard':hyp,'word_error_rate':round(score,3)})
        if score>.35:
            (out/'dialogue-check.json').write_text(json.dumps(qa,indent=2))
            raise ValueError(f'Line {i+1} did not pass after three takes (heard: {hyp}). Use the line’s New take button, shorten its wording, or supply a recorded WAV in the episode JSON. Other takes are cached.')
        hop=rate//30;energy=np.array([np.sqrt(np.mean(data[j:j+hop]**2)) for j in range(0,len(data),hop)])
        energy=(energy/max(.001,float(np.percentile(energy,90)))).clip(0,1)
        pause=float(line.get('pause',.25));timeline.append({**line,'start':offset,'speech_duration':dur,'duration':dur+pause,'words':words,'energy':energy.tolist()})
        audio.extend([data,np.zeros(round(pause*rate),np.float32)]);offset+=(len(data)+round(pause*rate))/rate
    audio.append(np.zeros(int(rate*.35),np.float32));total=np.concatenate(audio)
    # Very quiet original procedural room tone; small electronic payoff at the reveal.
    rng=np.random.default_rng(18);total+=rng.normal(0,.00018,len(total)).astype(np.float32)
    if spec.get('prop')=='robot':
        begin=int((timeline[-1]['start']+timeline[-1]['speech_duration']+.12)*rate)
        for shift,freq in [(0,620),(.12,830)]:
            j=begin+int(shift*rate);n=min(int(.09*rate),len(total)-j)
            if n>0:
                tt=np.arange(n)/rate;total[j:j+n]+=(np.sin(tt*freq*2*np.pi)*np.sin(np.linspace(0,np.pi,n))*.07).astype(np.float32)
    sf.write(out/'mix-raw.wav',total,rate,subtype='PCM_16')
    run(['ffmpeg','-v','error','-y','-i',out/'mix-raw.wav','-af','highpass=f=65,loudnorm=I=-16:TP=-1.5:LRA=8','-ar',rate,out/'soundtrack.wav'])
    (out/'voices.json').write_text(json.dumps(voices,indent=2));(out/'timeline.json').write_text(json.dumps(timeline,indent=2));(out/'dialogue-check.json').write_text(json.dumps(qa,indent=2))
    return timeline,len(total)/rate

def mouth_shape(line,local):
    energy=line.get('energy',[]);i=int(local*30)
    if i<0 or i>=len(energy) or energy[i]<.13:return 'closed'
    words=line.get('words',[]);w=next((w['word'].lower() for w in words if w['start']<=local<w['end']),'')
    phase=int(local*12)%4
    if phase==0 and energy[i]<.45:return 'closed'
    if any(x in w for x in ['oo','ou','or','you','who']):return 'o' if phase!=2 else 'open'
    if phase==2:return 'teeth'
    return 'wide' if energy[i]>.65 else 'open'

def caption(draw,line,local,W,H,font):
    words=line.get('words',[])
    if not words or local<0 or local>line['speech_duration']+.13:return
    idx=max(0,bisect.bisect_right([w['start'] for w in words],local)-1)
    # Short phrases, wrapping to at most two lines, in screen space.
    chunks=[];chunk=[]
    for i,w in enumerate(words):
        chunk.append(i)
        if len(chunk)>=4 or re.search(r'[.!?]$',w['word']):chunks.append(chunk);chunk=[]
    if chunk:chunks.append(chunk)
    chosen=next((c for c in chunks if idx in c),chunks[-1]);texts=[words[j]['word'] for j in chosen]
    rows=[[]]
    for j,tx in zip(chosen,texts):
        if rows[-1] and draw.textlength(' '.join(x[1] for x in rows[-1])+' '+tx,font=font)>W*.83:rows.append([])
        rows[-1].append((j,tx))
    y=H*.84-(len(rows)-1)*font.size*1.25
    for row in rows:
        text=' '.join(tx for j,tx in row);width=draw.textlength(text,font=font);x=(W-width)/2
        draw.rounded_rectangle((x-14,y-6,x+width+14,y+font.size+12),radius=12,fill=(16,25,37,205))
        for j,tx in row:
            fill='#ffd38b' if j==idx else '#fff9ef'
            draw.text((x,y),tx,font=font,fill=fill,stroke_width=max(1,font.size//22),stroke_fill='#172333')
            x+=draw.textlength(tx+' ',font=font)
        y+=font.size*1.25

def render(spec,out,timeline,duration):
    H=int(spec.get('resolution',720));ratio={'square':1,'landscape':16/9,'portrait':9/16}[spec.get('format','square')];W=math.ceil(H*ratio/2)*2;fps=spec.get('fps',30)
    bg=Image.open(ROOT/'assets'/spec.get('background','garage.png')).convert('RGB').resize((1280,960),Image.Resampling.LANCZOS)
    font=ImageFont.truetype(str(FONT),round(H*.043));starts=[x['start'] for x in timeline]
    count=math.ceil(duration*fps);temp=out/'video.partial.mp4';dest=out/'video.mp4'
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-i',str(out/'soundtrack.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(temp)]
    log(f'Animating {count} frames · {W} × {H} · {fps} fps')
    err=(out/'encoder.log').open('w');proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
    frames_to_save={min(count-1,int((line['start']+.5)*fps)):n for n,line in enumerate(timeline)}
    try:
        for f in range(count):
            t=f/fps;i=max(0,bisect.bisect_right(starts,t)-1);line=timeline[i];local=t-line['start']
            shape=mouth_shape(line,local)
            if spec.get('scene_type')=='explainer':
                from visuals import compose
                frame=compose(spec,line,t,local,timeline,W,H,ROOT)
            else:
                x,y,w,h=camera(spec,line,t,local,line['duration'])
                frame=bg.transform((W,H),Image.Transform.AFFINE,(w/W,0,x+160,0,h/H,y),Image.Resampling.BICUBIC)
                svg=svg_frame(spec,line,t,local,line['duration'],shape,H)
                overlay=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg,width=W,height=H,skip_system_fonts=True))).convert('RGBA')
                frame=frame.convert('RGBA');frame.alpha_composite(overlay)
            draw=ImageDraw.Draw(frame)
            if spec.get('captions',True):caption(draw,line,local,W,H,font)
            if t<.15:frame=Image.blend(Image.new('RGBA',frame.size,'#101b28'),frame,max(0,t/.15))
            if t>duration-.3:frame=Image.blend(frame,Image.new('RGBA',frame.size,'#101b28'),min(1,(t-duration+.3)/.3))
            if f in frames_to_save:frame.convert('RGB').save(out/f'shot-{frames_to_save[f]+1:02}.jpg',quality=93)
            proc.stdin.write(frame.convert('RGB').tobytes())
            if f%max(1,fps*2)==0:log(f'Render {round(f/count*100)}%')
        proc.stdin.close();code=proc.wait(timeout=120)
        if code:raise RuntimeError((out/'encoder.log').read_text())
    except BaseException:
        proc.kill();proc.wait();raise
    finally:err.close()
    temp.replace(dest)
    # Independent media checks, not a success message based solely on file existence.
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]))
    streams=probe['streams'];assert any(x['codec_type']=='audio' for x in streams)
    video=next(x for x in streams if x['codec_type']=='video');assert video['width']==W and video['height']==H
    assert abs(float(probe['format']['duration'])-duration)<.2
    report={'status':'passed','duration_seconds':float(probe['format']['duration']),'width':W,'height':H,'fps':fps,'frames':int(video['nb_frames']),'video_codec':video['codec_name'],'audio_codec':next(x['codec_name'] for x in streams if x['codec_type']=='audio'),'paid_api_calls':0,'dialogue':json.loads((out/'dialogue-check.json').read_text())}
    (out/'quality-report.json').write_text(json.dumps(report,indent=2))
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (out/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(l["start"])} --> {stamp(l["start"]+l["speech_duration"])}\n{l["text"]}' for i,l in enumerate(timeline)))
    log(f'Finished: {dest}')
    return dest

def main():
    p=argparse.ArgumentParser(description='Render a cartoon locally without paid APIs.');p.add_argument('episode',type=Path);p.add_argument('--out',type=Path,default=ROOT/'renders/latest');p.add_argument('--reuse-voices',action='store_true');p.add_argument('--render-only',action='store_true');a=p.parse_args()
    spec=validate(json.loads(a.episode.read_text()));out=a.out.resolve();started=time.time()
    if a.render_only:
        timeline=json.loads((out/'timeline.json').read_text());duration=sf.info(out/'soundtrack.wav').duration
        if len(timeline)!=len(spec['lines']) or any(l['text']!=t['text'] or l['speaker']!=t['speaker'] or float(l.get('pause',.25))!=float(t.get('pause',.25)) for l,t in zip(spec['lines'],timeline)):
            raise ValueError('Dialogue or timing changed. Use a normal render so the audio can be updated.')
        timeline=[{**t,**l} for l,t in zip(spec['lines'],timeline)]
    else:timeline,duration=prepare(spec,out,a.reuse_voices)
    render(spec,out,timeline,duration);log(f'Total elapsed: {time.time()-started:.1f} seconds')

if __name__=='__main__':main()
