"""Loopback-only editor and job runner. Everything stays on this Mac."""
import argparse, base64, io, json, os, secrets, signal, subprocess, sys, threading, time, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote
from PIL import Image
from render import ROOT, MODEL_ROOT, validate

from jobs import SceneQueue
from script_import import parse_script
from directions import compile_direction
from art import svg_frame

TOKEN=secrets.token_urlsafe(24);PORT=8768;QUEUE=None

def snapshot():return QUEUE.snapshot()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send(self,data,kind='application/json',code=200):
        if isinstance(data,(dict,list)):data=json.dumps(data).encode()
        elif isinstance(data,str):data=data.encode()
        self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        if path=='/':
            return self.send((ROOT/'studio/index.html').read_text().replace('__TOKEN__',TOKEN),'text/html; charset=utf-8')
        if path=='/api/status':return self.send(snapshot())
        if path=='/api/queue':return self.send(QUEUE.queue())
        if path=='/api/episode':
            saved=ROOT/'current.json'
            return self.send(json.loads((saved if saved.exists() else ROOT/'examples/robot-vacuum.json').read_text()))
        if path=='/api/library':
            latest=json.loads((ROOT/'latest.json').read_text()) if (ROOT/'latest.json').exists() else {'video':'/renders/demo/video.mp4'}
            return self.send({'backgrounds':[x.name for x in (ROOT/'assets').glob('*.png') if not x.name.startswith('preview')],'latest':latest})
        if path.startswith(('/assets/','/renders/')):
            target=(ROOT/path.lstrip('/')).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():return self.send({'error':'Not found'},code=404)
            import mimetypes
            kind=mimetypes.guess_type(str(target))[0] or 'application/octet-stream';size=target.stat().st_size
            start=0;end=size-1;partial=False
            requested=self.headers.get('Range','')
            if requested.startswith('bytes='):
                try:
                    a,b=requested[6:].split('-',1);start=int(a or 0);end=min(end,int(b)) if b else end;partial=True
                    if not 0<=start<=end<size:raise ValueError()
                except ValueError:return self.send('Invalid range','text/plain',416)
            self.send_response(206 if partial else 200);self.send_header('Content-Type',kind);self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
            if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers()
            try:
                with target.open('rb') as f:
                    f.seek(start);left=end-start+1
                    while left:
                        data=f.read(min(left,1024*1024))
                        if not data:break
                        self.wfile.write(data);left-=len(data)
            except (BrokenPipeError,ConnectionResetError):pass
            return
        return self.send({'error':'Not found'},code=404)
    def do_POST(self):
        origin=self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}'):return self.send({'error':'Origin rejected'},code=403)
        if self.headers.get('X-Studio-Token')!=TOKEN:return self.send({'error':'Open the editor again to refresh its session.'},code=403)
        try:
            length=int(self.headers.get('Content-Length',0))
            if not 0<length<18*1024*1024:raise ValueError('Request is too large.')
            data=json.loads(self.rfile.read(length));path=urlparse(self.path).path
            if path=='/api/save':
                validate(data);(ROOT/'current.json').write_text(json.dumps(data,indent=2));return self.send({'saved':True})
            if path=='/api/upload-background':
                raw=base64.b64decode(data['data']);im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert('RGB');im.thumbnail((2048,2048))
                name='set-'+secrets.token_hex(4)+'.png';im.save(ROOT/'assets'/name);return self.send({'name':name})
            if path=='/api/import-script':return self.send(parse_script(data.get('text','')))
            if path=='/api/direction':return self.send(compile_direction(data.get('text','')))
            if path=='/api/preview':
                spec=data['spec'];validate(spec);index=int(data.get('line',0))
                if not 0<=index<len(spec['lines']):raise ValueError('Choose a dialogue line.')
                import resvg_py
                if spec.get('scene_type')=='explainer':
                    from visuals import compose
                    timeline=[dict(l,start=n*5,speech_duration=4,duration=5) for n,l in enumerate(spec['lines'])]
                    line=timeline[index];frame=compose(spec,line,index*5+3,3,timeline,640,360,ROOT)
                    buf=io.BytesIO();frame.save(buf,format='PNG');png=buf.getvalue()
                else:
                    svg=svg_frame(spec,spec['lines'][index],1,1,5,size=360)
                    png=resvg_py.svg_to_bytes(svg_string=svg)
                return self.send({'image':'data:image/png;base64,'+base64.b64encode(png).decode()})
            if path=='/api/queue/add':return self.send({'items':QUEUE.add(data.get('scenes'))})
            if path=='/api/queue/update':
                QUEUE.edit(data['id'],data['spec']);return self.send({'saved':True})
            if path=='/api/queue/remove':
                QUEUE.edit(data['id'],remove=True);return self.send({'removed':True})
            if path=='/api/queue/start':
                QUEUE.start(data.get('ids'));return self.send({'started':True})
            if path=='/api/render':
                validate(data)
                with QUEUE.lock:
                    if QUEUE.job.get('state')=='running':raise ValueError('A job is already running.')
                    items=QUEUE.add([data]);QUEUE.start([items[0]['id']])
                (ROOT/'current.json').write_text(json.dumps(data,indent=2));return self.send({'started':True})
            if path=='/api/background':
                QUEUE.start_background(data.get('prompt',''));return self.send({'started':True})
            if path=='/api/stop':
                QUEUE.stop();return self.send({'stopped':True})
            return self.send({'error':'Not found'},code=404)
        except Exception as e:return self.send({'error':str(e)},code=400)

def main():
    global PORT,QUEUE
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8768);p.add_argument('--open',action='store_true');a=p.parse_args();PORT=a.port
    QUEUE=SceneQueue()
    server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
    print(f'Cartoon Studio is ready: http://127.0.0.1:{PORT}\nKeep this window open while rendering. Ctrl+C stops the editor.',flush=True)
    if a.open:webbrowser.open(f'http://127.0.0.1:{PORT}')
    def interrupt(*args):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,interrupt)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:
        QUEUE.stop()
        if QUEUE.worker:QUEUE.worker.join(timeout=7)
        server.server_close()
if __name__=='__main__':main()
