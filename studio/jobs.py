"""Durable sequential scene queue. One GPU subprocess at a time; never joins videos."""
import copy,hashlib,json,os,secrets,signal,subprocess,sys,threading,time
from pathlib import Path
from PIL import Image
from render import ROOT,MODEL_ROOT,validate

def atomic_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(data,indent=2));temp.replace(path)

def background_command(prompt,output,seed=46321):
    return [str(MODEL_ROOT/'envs/vision/bin/mflux-generate-flux2'),'--model',str(MODEL_ROOT/'models/flux2-klein-4b-4bit'),'--base-model','flux2-klein-4b','--prompt',prompt+'. Professional 2D cartoon background, clean ink outlines, cel shading, wide eye level view, empty foreground floor for characters, no people, no lettering, no watermark.','--width','1024','--height','768','--steps','4','--seed',str(seed),'--low-ram','--mlx-cache-limit-gb','3','--output',str(output)]

class SceneQueue:
    def __init__(self,root=ROOT,runner=None):
        self.root=Path(root);self.path=self.root/'scene-queue.json';self.lock=threading.RLock();self.items=[];self.revision=0;self.process=None;self.cancel=threading.Event();self.worker=None;self.runner=runner;self.job={}
        if self.path.exists():
            data=json.loads(self.path.read_text());self.items=data.get('items',[]);self.revision=data.get('revision',0)
            for item in self.items:
                if item['state'] in ('queued','running'):
                    item.update(state='interrupted',stage='Stopped when the editor closed; ready to retry.')
            self._save()
    def _save(self):
        self.revision+=1;atomic_json(self.path,{'revision':self.revision,'items':self.items})
    def snapshot(self):
        with self.lock:
            job=copy.deepcopy(self.job);job['queue_revision']=self.revision
            if job.get('log') and Path(job['log']).exists():job['messages']=Path(job['log']).read_text(errors='replace')[-7000:]
            return job
    def queue(self):
        with self.lock:return copy.deepcopy({'revision':self.revision,'items':self.items,'running':self.job.get('state')=='running'})
    def add(self,specs):
        if not isinstance(specs,list) or not specs:raise ValueError('Add at least one scene.')
        for spec in specs:validate(spec,self.root)
        with self.lock:
            added=[dict(id=secrets.token_hex(8),spec=copy.deepcopy(s),state='pending',stage='Ready') for s in specs]
            self.items.extend(added);self._save();return copy.deepcopy(added)
    def edit(self,id,spec=None,remove=False):
        if spec is not None:validate(spec,self.root)
        with self.lock:
            item=self._find(id)
            if item['state'] in ('queued','running'):raise ValueError('Stop the batch before editing or removing a queued scene.')
            if remove:self.items.remove(item)
            else:
                item.update(spec=copy.deepcopy(spec),state='pending',stage='Edited; ready to render');item.pop('video',None);item.pop('error',None);item.pop('out',None)
            self._save()
    def _find(self,id):
        item=next((i for i in self.items if i['id']==id),None)
        if item is None:raise ValueError('Scene no longer exists in the queue.')
        return item
    def _reserve(self,kind):
        if self.job.get('state')=='running':raise ValueError('A job is already running. Scenes render one at a time.')
        self.cancel.clear();self.job=dict(state='running',kind=kind,stage='Starting',run=secrets.token_hex(6))
    def start(self,ids):
        if not isinstance(ids,list) or not ids:raise ValueError('Select at least one unfinished scene.')
        with self.lock:
            if len(ids)!=len(set(ids)):raise ValueError('Duplicate scene selection.')
            chosen=[self._find(id) for id in ids]
            chosen=[i for i in chosen if i['state']!='done']
            if not chosen:raise ValueError('Selected scenes are already complete. Edit a scene to render it again.')
            for item in chosen:validate(item['spec'],self.root)
            self._reserve('batch');ids=[i['id'] for i in chosen];self.job.update(total=len(ids),completed=0,failed=0)
            for item in chosen:item.update(state='queued',stage='Waiting');item.pop('error',None)
            self._save();self.worker=threading.Thread(target=self._batch,args=(ids,),daemon=True);self.worker.start()
    def _stage(self,item,stage):
        with self.lock:
            item.update(stage=stage,state='running');self.job.update(stage=stage,scene=item['spec']['title'],scene_id=item['id']);self._save()
    def _run(self,cmd,log):
        if self.runner:return self.runner(cmd,log,self.cancel)
        with self.lock:
            if self.cancel.is_set():raise InterruptedError('Stopped by you.')
            with open(log,'a') as handle:
                self.process=subprocess.Popen([str(c) for c in cmd],stdout=handle,stderr=subprocess.STDOUT,start_new_session=True,cwd=self.root)
            process=self.process
        code=process.wait()
        with self.lock:self.process=None
        if self.cancel.is_set():raise InterruptedError('Stopped by you.')
        if code:raise RuntimeError(f'Local job exited with code {code}. Open the scene log for details; retry retains cached audio and sets.')
    def _set(self,spec,log,item=None):
        prompt=spec.get('background_prompt','').strip()
        if not prompt:return spec['background']
        key=hashlib.sha256((prompt+'|flux2-klein-4b|1024x768|4|46321|v1').encode()).hexdigest()[:20]
        name='auto-'+key+'.png';dest=self.root/'assets'/name
        if dest.exists():
            try:
                with Image.open(dest) as im:im.verify()
                return name
            except Exception:pass
        if item:self._stage(item,'Generating background')
        tmp=dest.with_name(dest.stem+'.partial.png')
        self._run(background_command(prompt,tmp),log)
        with Image.open(tmp) as im:im.verify()
        tmp.replace(dest);return name
    def _visual(self,spec,log,item=None):
        v=spec.get('visual',{})
        if v.get('type')!='picture' or v.get('image'):return
        prompt=v.get('prompt','').strip()
        key=hashlib.sha256((prompt+'|visual-picture-v1').encode()).hexdigest()[:20]
        name='visuals/generated-'+key+'.png';dest=self.root/'assets'/name;dest.parent.mkdir(exist_ok=True)
        if dest.exists():
            try:
                with Image.open(dest) as im:im.verify()
                v['image']=name;return
            except Exception:pass
        if item:self._stage(item,'Generating explanatory illustration')
        tmp=dest.with_name(dest.stem+'.partial.png')
        cmd=background_command(prompt,tmp)
        cmd[cmd.index('--prompt')+1]=prompt+'. Clear explanatory illustration, clean composition, no lettering, no chart axes, no numerical data, no watermark.'
        self._run(cmd,log)
        with Image.open(tmp) as im:im.verify()
        tmp.replace(dest);v['image']=name

    def _batch(self,ids):
        try:
            for index,id in enumerate(ids):
                if self.cancel.is_set():break
                with self.lock:
                    item=self._find(id);spec=copy.deepcopy(item['spec']);self.job['index']=index+1
                    out=self.root/'renders'/('scene-'+time.strftime('%Y%m%d-%H%M%S')+'-'+id[:8]+'-'+secrets.token_hex(2));out.mkdir(parents=True)
                    log=out/'render.log';item['out']='/renders/'+out.name;self.job['log']=str(log)
                try:
                    self._stage(item,'Preparing scene');spec['background']=self._set(spec,log,item)
                    self._visual(spec,log,item)
                    if self.cancel.is_set():raise InterruptedError('Stopped by you.')
                    spec['background_prompt']='';validate(spec,self.root)
                    atomic_json(out/'episode.json',spec);self._stage(item,'Rendering dialogue and animation')
                    self._run([sys.executable,str(ROOT/'studio/render.py'),str(out/'episode.json'),'--out',str(out)],log)
                    if not (out/'video.mp4').is_file():raise RuntimeError('Renderer finished without a video file. See scene log.')
                    with self.lock:
                        item.update(state='done',stage='Complete',video=item['out']+'/video.mp4',background=spec['background']);self.job['completed']+=1
                        atomic_json(self.root/'latest.json',{'video':item['video'],'episode':item['out']+'/episode.json'});self._save()
                except InterruptedError as e:
                    with self.lock:item.update(state='stopped',stage=str(e));self._save()
                    break
                except Exception as e:
                    with self.lock:item.update(state='failed',stage='Failed; ready to retry',error=str(e));self.job['failed']+=1;self._save()
            with self.lock:
                for id in ids:
                    item=self._find(id)
                    if item['state']=='queued':item.update(state='pending',stage='Not started')
                self.job.update(state='stopped' if self.cancel.is_set() else ('failed' if self.job['failed'] else 'done'),stage='Batch stopped' if self.cancel.is_set() else 'Batch finished');self._save()
        except Exception as e:
            with self.lock:
                for id in ids:
                    item=self._find(id)
                    if item['state'] in ('queued','running'):item.update(state='interrupted',stage='Interrupted; ready to retry')
                self.job.update(state='failed',stage=str(e));self._save()
    def start_background(self,prompt):
        if not isinstance(prompt,str) or not 10<=len(prompt.strip())<=2000:raise ValueError('Describe your set in 10–2000 characters.')
        with self.lock:
            self._reserve('background');log=self.root/'logs'/('set-'+secrets.token_hex(5)+'.log');log.parent.mkdir(exist_ok=True);self.job['log']=str(log)
            self.worker=threading.Thread(target=self._background,args=(prompt,log),daemon=True);self.worker.start()
    def _background(self,prompt,log):
        try:
            name=self._set({'background_prompt':prompt},log)
            with self.lock:self.job.update(state='done',stage='Background ready',background=name)
        except Exception as e:
            with self.lock:self.job.update(state='stopped' if self.cancel.is_set() else 'failed',stage=str(e))
    def stop(self):
        with self.lock:
            self.cancel.set()
            if self.process and self.process.poll() is None:
                proc=self.process
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                def kill_later():
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        try:os.killpg(proc.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                threading.Thread(target=kill_later,daemon=True).start()
