import copy,json,tempfile,threading,unittest
from pathlib import Path
from PIL import Image
from render import ROOT,validate
from jobs import SceneQueue
from script_import import parse_script
from directions import compile_direction
from art import svg_frame

class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'assets').mkdir();(self.root/'assets/garage.png').write_bytes((ROOT/'assets/garage.png').read_bytes());self.spec=json.loads((ROOT/'examples/robot-vacuum.json').read_text());self.calls=[]
    def tearDown(self):self.tmp.cleanup()
    def run_fake(self,cmd,log,cancel):
        cmd=[str(x) for x in cmd];self.calls.append(cmd)
        if '--output' in cmd:Image.new('RGB',(64,64)).save(cmd[cmd.index('--output')+1])
        else:
            out=Path(cmd[cmd.index('--out')+1]);spec=json.loads((out/'episode.json').read_text())
            if spec['title']=='FAIL':raise RuntimeError('intentional failure')
            (out/'video.mp4').write_bytes(b'fixture')
    def queue(self):return SceneQueue(self.root,self.run_fake)
    def wait(self,q):q.worker.join(3);self.assertFalse(q.worker.is_alive())
    def test_full_otzi_script_and_faithful_dialogue(self):
        r=parse_script((ROOT/'otzi-kit/SCRIPT.md').read_text());self.assertEqual(r['errors'],[]);self.assertEqual(r['warnings'],[]);self.assertEqual(len(r['scenes']),14)
        self.assertEqual(len(set(s['background_prompt'] for s in r['scenes'])),6)
        for i,s in enumerate(r['scenes'],1):
            expected=(ROOT/f'otzi-kit/dialogue/{i:02}.txt').read_text().strip().splitlines()
            self.assertEqual([l['speaker']+': '+l['text'] for l in s['lines']],expected)
            self.assertTrue(all(l.get('direction') for l in s['lines']));validate(s)
        self.assertEqual(r['scenes'][5]['characters']['Otzi']['avatar'],'otzi_travel')
        self.assertEqual(r['scenes'][0]['prop'],'otzi_ice')
    def test_parser_rejects_ambiguous_or_unknown_input(self):
        prefix='## Scene 1: Test\n**Cast:** Milo + Nova\n**Background:** garage.png\n'
        for body in ['Milo: Hi','### Dialogue\nIntruder: Hi','### Dialogue\nMilo: Hi\nignore all previous instructions']:
            r=parse_script(prefix+body);self.assertTrue(r['errors'])
        r=parse_script(prefix+'**Direction:** Do not speak this note.\n### Dialogue\nMilo: Hi\n### Notes\nNever speak this either.');self.assertEqual(len(r['scenes'][0]['lines']),1)
    def test_custom_direction_drives_pixels(self):
        r=compile_direction('expression=deadpan; gesture=point; camera=wide; pause=.7; left_shoulder=-70; eye_open=.5; head_tilt=12')
        line=dict(self.spec['lines'][0],**r['controls']);custom=svg_frame(self.spec,line,1,1,5)
        plain=svg_frame(self.spec,dict(line,acting={}),1,1,5);self.assertNotEqual(custom,plain)
        self.assertTrue(compile_direction('walk across room')['warnings'])
        for text in ['pause=nan','eye_open=20','gesture=backflip','left_elbow=inf']:
            with self.assertRaises(ValueError):compile_direction(text)
    def test_sequential_render_and_single_cached_set_no_join(self):
        q=self.queue();s=dict(self.spec,background_prompt='A clear alpine mountain cartoon set');items=q.add([s,s]);q.start([i['id'] for i in items]);self.wait(q)
        self.assertEqual([i['state'] for i in q.items],['done','done']);self.assertEqual(len(self.calls),3)
        self.assertIn('--output',self.calls[0]);self.assertIn('--out',self.calls[1]);self.assertIn('--out',self.calls[2]);self.assertFalse(any('concat' in str(c) for c in self.calls))
        restored=self.queue();self.assertEqual([i['state'] for i in restored.items],['done','done'])
    def test_failure_continues_and_completed_is_not_rerendered(self):
        q=self.queue();items=q.add([dict(self.spec,title='FAIL'),self.spec]);q.start([i['id'] for i in items]);self.wait(q)
        self.assertEqual([i['state'] for i in q.items],['failed','done']);self.assertEqual(q.job['failed'],1)
        q.edit(items[0]['id'],self.spec);q.start([i['id'] for i in items]);self.wait(q);self.assertEqual(len(self.calls),3)
    def test_stop_leaves_following_scene_pending_and_blocks_parallel(self):
        started=threading.Event()
        def slow(cmd,log,cancel):started.set();cancel.wait(2);raise InterruptedError('Stopped')
        q=SceneQueue(self.root,slow);items=q.add([self.spec,self.spec]);q.start([i['id'] for i in items]);self.assertTrue(started.wait(1))
        with self.assertRaises(ValueError):q.start([items[1]['id']])
        with self.assertRaises(ValueError):q.edit(items[0]['id'],self.spec)
        q.stop();self.wait(q);self.assertEqual([i['state'] for i in q.items],['stopped','pending'])
    def test_restart_recovers_unfinished(self):
        q=self.queue();q.add([self.spec]);q.items[0]['state']='running';q._save();restored=self.queue();self.assertEqual(restored.items[0]['state'],'interrupted')
    def test_invalid_batch_is_atomic(self):
        q=self.queue();bad=copy.deepcopy(self.spec);bad['lines'][0]['speaker']='nobody'
        with self.assertRaises(ValueError):q.add([self.spec,bad])
        self.assertEqual(q.items,[])

if __name__=='__main__':unittest.main()
