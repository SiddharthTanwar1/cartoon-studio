"""Local voice worker. Invoked separately so only one model occupies memory."""
import hashlib, json, os, sys
from pathlib import Path
import numpy as np
import soundfile as sf

def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    target = Path(sys.argv[2]); target.mkdir(parents=True, exist_ok=True)
    root = Path(os.environ.get('CARTOON_MODEL_ROOT', str(Path.home()/'AI_EXPLAINER_FACTORY')))
    cache = Path(__file__).resolve().parents[1]/'assets'/'voice_cache'; cache.mkdir(exist_ok=True)
    import mlx.core as mx
    from mlx_audio.tts.utils import load_model
    mx.set_cache_limit(1024**3)
    model = None
    actors = spec['characters']; refs = {}; manifest = []
    for n, line in enumerate(spec['lines']):
        name = line['speaker']; actor = actors[name]
        description = actor.get('voice', 'A natural conversational adult American voice, clear studio speech.')
        identity = hashlib.sha256((name+description+str(spec.get('seed', 712))).encode()).hexdigest()[:18]
        ref = cache / (identity+'.wav')
        ref_meta = cache / (identity+'.json')
        take=int(line.get('take',0))
        key = hashlib.sha256((identity+line['text']+'vox-v1'+str(take)+('-ref' if take>=2 else '') if take else identity+line['text']+'vox-v1').encode()).hexdigest()[:24]
        wav = cache/(key+'.wav')
        chosen=cache/(key+'.chosen.json')
        if chosen.exists():
            selected=Path(json.loads(chosen.read_text())['path'])
            if selected.is_file():wav=selected
        if line.get('audio'):
            wav = Path(line['audio']).expanduser().resolve()
            if not wav.is_file(): raise ValueError(f'Audio file missing: {wav}')
        elif not wav.exists():
            if model is None:
                print('Loading your local VoxCPM2 voice model…', flush=True)
                model = load_model(str(root/'models'/'voxcpm2-4bit'))
            mx.random.seed((int(identity[:8],16)+take*137)%2**32)
            kwargs = dict(text=line['text'], inference_timesteps=10, cfg_value=2.0, max_tokens=600)
            if ref.exists() and ref_meta.exists():
                kwargs.update(ref_audio=str(ref), ref_text=json.loads(ref_meta.read_text())['text'])
            else:
                kwargs['instruct'] = description
            print(f'Voice {n+1}/{len(spec["lines"])} · {name}: {line["text"]}', flush=True)
            chunks=[]; rate=48000
            for result in model.generate(**kwargs):
                chunks.append(np.asarray(result.audio,dtype=np.float32).reshape(-1)); rate=result.sample_rate
            if not chunks: raise RuntimeError(f'No audio generated for line {n+1}')
            data=np.concatenate(chunks)
            if not np.isfinite(data).all() or len(data)<rate*.15: raise RuntimeError('Voice output is invalid')
            # Trim only long leading/trailing silence, retaining natural breaths.
            hop=max(1,rate//100); energy=np.array([np.sqrt(np.mean(data[i:i+hop]**2)) for i in range(0,len(data),hop)])
            active=np.where(energy>max(.003,float(energy.max())*.035))[0]
            if len(active):data=data[max(0,(active[0]-8)*hop):min(len(data),(active[-1]+12)*hop)]
            peak=max(.01,float(np.max(np.abs(data)))); data=data/peak*.84
            tmp=wav.with_suffix('.tmp.wav');sf.write(tmp,data,rate,subtype='PCM_16');tmp.replace(wav)
            if not ref.exists():
                import shutil
                shutil.copy2(wav,ref);ref_meta.write_text(json.dumps({'text':line['text'],'description':description}))
            mx.clear_cache()
        print(f'Voice {n+1}/{len(spec["lines"])} ready',flush=True)
        manifest.append({'path':str(wav),'speaker':name,'text':line['text'],'cache_key':key})
    (target/'voices.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
