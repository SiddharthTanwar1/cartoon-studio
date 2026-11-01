"""Regression checks for framing, malformed episodes, timing and caches."""
import copy, io, json, unittest
from pathlib import Path
import resvg_py
from PIL import Image
from render import ROOT,validate,camera,svg_frame,wer,mouth_shape

class StudioTests(unittest.TestCase):
    def setUp(self):self.spec=json.loads((ROOT/'examples/robot-vacuum.json').read_text())
    def test_script_validation(self):
        validate(self.spec)
        for mutation in [lambda s:s.update(lines=[]),lambda s:s.update(background='../studio/index.html'),lambda s:s['lines'][0].update(speaker='Nobody'),lambda s:s['lines'][0].update(pause=-1),lambda s:s['characters']['Milo'].update(shirt='url(http://example.com)')]:
            s=copy.deepcopy(self.spec);mutation(s)
            with self.assertRaises(ValueError):validate(s)
    def test_all_framings_stay_inside_set(self):
        for fmt in ['square','landscape','portrait']:
            self.spec['format']=fmt
            for speaker in ['Milo','Nova']:
                for shot in ['speaker','reaction','two','wide']:
                    l={**self.spec['lines'][0],'speaker':speaker,'shot':shot}
                    for local in [0,.2,3]:
                        x,y,w,h=camera(self.spec,l,local,local,3)
                        self.assertGreaterEqual(x,-160.001);self.assertGreaterEqual(y,-.001)
                        self.assertLessEqual(x+w,1120.001);self.assertLessEqual(y+h,960.001)
    def test_all_expressions_and_gestures_render(self):
        from render import EMOTIONS,POSES
        for expression in EMOTIONS:
            for pose in POSES:
                l={**self.spec['lines'][0],'emotion':expression,'pose':pose}
                image=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg_frame(self.spec,l,1,.5,3,'open',120))))
                self.assertEqual(image.size,(120,120));self.assertIsNotNone(image.getbbox())
    def test_number_aware_dialogue_check(self):
        self.assertEqual(wer('It costs $700.','It costs seven hundred dollars.'),0)
        self.assertGreater(wer('The robot is asleep.','The robot is awake.'),0)
    def test_silence_closes_mouth(self):
        l={'energy':[.01]*100,'words':[]}
        self.assertEqual(mouth_shape(l,.5),'closed');self.assertEqual(mouth_shape(l,50),'closed')
    def test_demo_has_real_audio_and_matching_timeline(self):
        import soundfile as sf
        p=ROOT/'renders/demo';timeline=json.loads((p/'timeline.json').read_text())
        self.assertEqual(len(timeline),7)
        for i,l in enumerate(timeline):
            self.assertGreater(l['speech_duration'],.2)
            if i:self.assertAlmostEqual(l['start'],timeline[i-1]['start']+timeline[i-1]['duration'],places=4)
            self.assertTrue(all(0<=w['start']<=l['speech_duration'] for w in l['words']))
        self.assertGreater(sf.info(p/'soundtrack.wav').duration,10)
    def test_voice_manifest_matches_script(self):
        p=ROOT/'renders/demo';voices=json.loads((p/'voices.json').read_text())
        for l,v in zip(self.spec['lines'],voices):
            self.assertEqual(l['text'],v['text']);self.assertTrue(Path(v['path']).is_file())

if __name__=='__main__':unittest.main()
