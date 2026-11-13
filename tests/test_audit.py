import tempfile
import unittest
from pathlib import Path
from audit import audit


class AuditTests(unittest.TestCase):
    def check(self, content):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.pfp'
            path.write_text(content)
            before = path.read_bytes()
            result = audit(path)
            self.assertEqual(before, path.read_bytes())
            return result

    def test_find_errors_without_changing_source(self):
        result = self.check('''<playlist xmlns="http://xspf.org/ns/0/" xmlns:p="urn:pf"><trackList>
        <track><location>private/a.wav</location><p:entryType>3</p:entryType></track>
        <track><location>private/b.wav</location><p:entryType>3</p:entryType></track>
        <track><location>private/voice.wav</location><p:entryType>48</p:entryType></track>
        <track><location>private/voice.wav</location><p:entryType>48</p:entryType>
        <p:cuePoints><p:cueIn>10</p:cueIn><p:cueOut>5</p:cueOut></p:cuePoints></track>
        </trackList></playlist>''')
        self.assertEqual({x['code'] for x in result['issues']},
                         {'adjacent_jingles', 'repeated_speech_file', 'invalid_cue_order'})
        self.assertNotIn('private/', str(result))

    def test_valid_music_and_jingle(self):
        result = self.check('''<playlist xmlns="http://xspf.org/ns/0/"><trackList>
        <track><location>song.mp3</location><entryType>0</entryType></track>
        <track><location>id.wav</location><entryType>3</entryType></track>
        </trackList></playlist>''')
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['counts'], {'music': 1, 'jingle': 1})


if __name__ == '__main__':
    unittest.main()
