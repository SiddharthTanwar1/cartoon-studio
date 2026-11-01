import copy,json,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageChops
from script_import import parse_script
from render import ROOT,validate
from visuals import compose,progress
from jobs import SceneQueue

PREFIX='''## Scene 1: Visual test
**Cast:** Milo + Nova
**Background:** garage.png
**Scene type:** explainer
**Format:** landscape
**Visual:** bar
**Visual title:** Demonstration
**Visual unit:** units
**Visual source:** Illustrative data, not study findings
**Visual data:** {"labels":["A","B"],"values":[2,5]}
### Dialogue
Milo: Let us explain this.
@visual: 1
Nova: Now the second part.
@visual: 2
'''
class VisualTests(unittest.TestCase):
    def spec(self):
        r=parse_script(PREFIX);self.assertEqual(r['errors'],[]);self.assertEqual(r['warnings'],[]);return r['scenes'][0]
    def timeline(self,s):return [dict(l,start=i*3,speech_duration=2,duration=3,words=[],energy=[]) for i,l in enumerate(s['lines'])]
    def test_parser_preserves_cues_and_queue_export(self):
        s=self.spec();self.assertEqual([l['visual_step'] for l in s['lines']],[1,2])
        r=parse_script(json.dumps({'scenes':[s]}));self.assertEqual(r['scenes'],[s])
    def test_validation_rejects_bad_chart_and_path(self):
        original=self.spec()
        for mutate in [lambda s:s['visual'].update(source=''),lambda s:s['visual'].update(values=[float('nan'),3]),lambda s:s['visual'].update(values=[-1,3]),lambda s:s['visual'].update(values=[3]),lambda s:s.update(format='portrait'),lambda s:s['lines'][0].update(visual_step=9),lambda s:s['visual'].update(type='picture',image='../current.json')]:
            s=copy.deepcopy(original);mutate(s)
            with self.assertRaises(ValueError):validate(s)
        self.assertTrue(parse_script(PREFIX.replace('{"labels":["A","B"],"values":[2,5]}','[]'))['errors'])
    def test_reveal_persists_across_uncued_lines(self):
        s=self.spec();tl=self.timeline(s);tl.insert(1,dict(tl[0],start=1));del tl[1]['visual_step']
        self.assertEqual(progress(s['visual'],2,tl[1],tl),1)
        self.assertEqual(progress(s['visual'],4,tl[-1],tl),2)
        self.assertGreater(progress(s['visual'],3.4,tl[-1],tl),1)
    def test_all_visual_types_draw_and_change(self):
        s=self.spec();tl=self.timeline(s)
        a=compose(s,tl[0],0,0,tl,854,480,ROOT);b=compose(s,tl[1],4,1,tl,854,480,ROOT)
        self.assertIsNotNone(ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox())
        for v in [dict(s['visual'],type='line',values=[-2,4]),{'type':'diagram','title':'Process','nodes':['First','Then','Finally']},{'type':'picture','title':'Existing picture','image':'garage.png'}]:
            s['visual']=v
            for l in s['lines']:l.pop('visual_step',None)
            validate(s);tl=self.timeline(s);im=compose(s,tl[0],3,3,tl,854,480,ROOT);self.assertEqual(im.size,(854,480))
    def test_generated_picture_cache_and_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'assets').mkdir();Image.new('RGB',(8,8)).save(root/'assets/garage.png');calls=[]
            def runner(cmd,log,cancel):
                calls.append(cmd)
                if '--output' in cmd:Image.new('RGB',(12,12)).save(cmd[cmd.index('--output')+1])
                else:(Path(cmd[cmd.index('--out')+1])/'video.mp4').write_bytes(b'fixture')
            q=SceneQueue(root,runner);s=self.spec();s['visual']={'type':'picture','title':'Illustration','prompt':'A clean cartoon tooth illustration'}
            for l in s['lines']:l.pop('visual_step',None)
            items=q.add([s,s]);q.start([i['id'] for i in items]);q.worker.join(3)
            self.assertFalse(q.worker.is_alive());self.assertEqual([i['state'] for i in q.items],['done','done']);self.assertEqual(len(calls),3)
            self.assertNotIn('empty foreground',calls[0][calls[0].index('--prompt')+1])
            self.assertEqual(SceneQueue(root,runner).items[0]['spec']['visual'],s['visual'])
            episode=json.loads(next((root/'renders').glob('*/episode.json')).read_text());self.assertTrue(episode['visual']['image'].startswith('visuals/'))
if __name__=='__main__':unittest.main()
