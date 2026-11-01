"""Import marked Markdown scenes into editable render specs, without GPU work."""
import copy,json,re,unicodedata
from pathlib import Path
from directions import compile_direction
from render import ROOT,validate

def canonical(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c)).strip()
def parse_script(text):
    if not isinstance(text,str) or not text.strip() or len(text)>2_000_000:raise ValueError('Upload a nonempty Markdown script under 2 MB.')
    if text.lstrip().startswith('{'):
        data=json.loads(text);scenes=data.get('scenes',[])
        if not isinstance(scenes,list) or not scenes:raise ValueError('Queue JSON must contain a nonempty scenes list.')
        for scene in scenes:validate(scene)
        return {'scenes':scenes,'errors':[],'warnings':[],'title':'Imported queue'}
    catalog=json.loads((ROOT/'assets/avatars/catalog.json').read_text())
    byid={e['id']:e for e in catalog};byname={}
    for e in catalog:byname.setdefault(canonical(e['name']),e)
    heading=re.compile(r'^##\s+(?:(?:scene|take)\s+)?(\d+)[.:)\s-]+(.+)$',re.I|re.M)
    chunks=list(heading.finditer(text));scenes=[];errors=[];warnings=[]
    if not chunks:raise ValueError('No scenes found. Use “## Scene 1: Title”, then Cast, Set prompt, Direction and “### Dialogue”.')
    for i,m in enumerate(chunks):
        label=m.group(1);title=re.split(r'\s+—\s+\d+:',m.group(2))[0].strip()
        block=text[m.end():chunks[i+1].start() if i+1<len(chunks) else len(text)]
        try:
            marker=re.search(r'^(?:###\s+Dialogue|\*\*Dialogue:?\*\*:?)\s*$',block,re.I|re.M)
            if not marker:raise ValueError('Missing “### Dialogue” marker. Dialogue must be clearly separated from notes.')
            meta=block[:marker.start()];body=block[marker.end():]
            fields={canonical(k):v.strip().strip('·').strip() for k,v in re.findall(r'\*\*([^*]+?):\*\*\s*(.*?)(?=\s*·\s*\*\*|\n|$)',meta)}
            names=[n.strip() for n in fields.get('cast','').split('+') if n.strip()]
            if not 1<=len(names)<=2:raise ValueError('Declare one or two cast names separated by +. Split scenes with more speakers into takes.')
            variants={}
            for pair in fields.get('avatars','').split(';'):
                if pair.strip():
                    if '=' not in pair:raise ValueError('Avatars format: Otzi=otzi_travel; Mira=mira')
                    a,b=pair.split('=',1);variants[canonical(a)]=b.strip()
            actors={};rename={}
            for n in names:
                key=canonical(n);entry=byid.get(variants[key]) if key in variants else byname.get(key)
                if not entry:raise ValueError(f'Unknown cast or avatar: {n}. Select an installed preset in the Cast field.')
                name=entry['name'];actors[name]=copy.deepcopy(entry['actor']);rename[key]=name
            if len(actors)!=len(names):raise ValueError('Duplicate cast identity; use one slot per character.')
            prompt=fields.get('set prompt','');setname=fields.get('set','')
            background=fields.get('background','')
            if not background and not prompt:
                if not setname:raise ValueError('Supply a Set prompt or an existing Background filename.')
                prompt=f'{setname}. Original flat 2D cartoon set, clear empty foreground for two actors, no people, no text.'
                warnings.append(f'Scene {label}: built a basic set prompt from “{setname}”; review it before rendering.')
            direction=fields.get('direction','');defaults={'emotion':'neutral','pose':'present','shot':'speaker','pause':.25}
            if fields.get('acting'):
                compiled=compile_direction(fields['acting']);defaults.update(compiled['controls']);warnings.extend(f'Scene {label}: {w}' for w in compiled['warnings'])
            elif direction:
                compiled=compile_direction(direction);defaults.update(compiled['controls']);warnings.extend(f'Scene {label}: {w}' for w in compiled['warnings'])
            lines=[]
            for raw in body.splitlines():
                raw=raw.strip()
                if not raw:continue
                if re.match(r'^(?:#{1,3}\s|Paste file:|\*\*Planning total|<!--\s*end)',raw,re.I):break
                if raw.lower().startswith('@visual:'):
                    if not lines:raise ValueError('@visual must follow a dialogue line.')
                    try:lines[-1]['visual_step']=int(raw.split(':',1)[1].strip())
                    except ValueError:raise ValueError('@visual must be a whole-number reveal step.')
                    continue
                if raw.lower().startswith('@direction:'):
                    if not lines:raise ValueError('@direction must follow a dialogue line.')
                    cue=raw.split(':',1)[1].strip();compiled=compile_direction(cue)
                    lines[-1].update(compiled['controls']);lines[-1]['direction']=cue
                    warnings.extend(f'Scene {label}, line {len(lines)}: {w}' for w in compiled['warnings']);continue
                match=re.match(r'^([^:]+):\s*(.+)$',raw)
                if not match:raise ValueError(f'Unexpected text in Dialogue: {raw[:80]}')
                speaker,spoken=match.groups();name=rename.get(canonical(speaker))
                if not name:raise ValueError(f'Unknown speaker “{speaker}”. Put only cast dialogue below the marker.')
                lines.append(dict(copy.deepcopy(defaults),speaker=name,text=spoken))
            spec=dict(title=f'{label.zfill(2)} · {title}',characters=actors,lines=lines,background=background or 'garage.png',background_prompt=prompt,set_name=setname,direction=direction,prop=None if fields.get('prop','none').lower()=='none' else fields.get('prop'),format=fields.get('format','landscape'),resolution=int(fields.get('resolution','720')),fps=30,seed=712,captions=True)
            if fields.get('scene type','dialogue').lower()!='dialogue' or 'visual' in fields:
                spec['scene_type']=fields.get('scene type','dialogue').lower()
                try:v=json.loads(fields.get('visual data','{}'))
                except json.JSONDecodeError:raise ValueError('Visual data must be a single-line JSON object.')
                if not isinstance(v,dict):raise ValueError('Visual data must be a JSON object.')
                v.update(type=fields.get('visual','').lower(),title=fields.get('visual title',''),caption=fields.get('visual caption',''),source=fields.get('visual source',''),unit=fields.get('visual unit',''),animation=fields.get('visual animation','reveal').lower())
                if fields.get('visual image'):v['image']=fields['visual image']
                if fields.get('visual prompt'):v['prompt']=fields['visual prompt']
                spec['visual']=v
            validate(spec);scenes.append(spec)
        except (ValueError,TypeError,KeyError) as e:errors.append(f'Scene {label}: {e}')
    return {'scenes':scenes,'errors':errors,'warnings':warnings,'title':text.splitlines()[0].lstrip('# ').strip()}
