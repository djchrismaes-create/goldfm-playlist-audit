"""Read-only XSPF/ProppFrexx playlist audit. Python 3.10+, no dependencies."""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


def audit(path):
    root = ET.parse(path).getroot()
    rows = []
    issues = []
    for index, track in enumerate(root.findall('.//{*}track'), 1):
        location = track.findtext('{*}location', '')
        kind = track.findtext('.//{*}entryType', '')
        category = {'0': 'music', '3': 'jingle', '48': 'speech'}.get(kind, 'unknown')
        row = {'position': index, 'kind': category}
        # Paths stay internal; reports contain no source filenames or personal metadata.
        rows.append((row, re.sub(r'/+', '/', location.replace('\\', '/')).casefold()))
        if not location:
            issues.append({'position': index, 'code': 'missing_location'})
        cues = track.find('.//{*}cuePoints')
        if cues is not None:
            try:
                start = float(cues.findtext('{*}cueIn', '0'))
                end = cues.findtext('{*}cueOut')
                next_point = cues.findtext('{*}next')
                if start < 0 or (end is not None and float(end) <= start):
                    raise ValueError()
                if next_point is not None and (float(next_point) < start or
                   (end is not None and float(next_point) > float(end))):
                    raise ValueError()
            except (ValueError, TypeError):
                issues.append({'position': index, 'code': 'invalid_cue_order'})
    seen_speech = set()
    previous = None
    for row, location in rows:
        if row['kind'] == previous == 'jingle':
            issues.append({'position': row['position'], 'code': 'adjacent_jingles'})
        if row['kind'] == 'speech' and location:
            if location in seen_speech:
                issues.append({'position': row['position'], 'code': 'repeated_speech_file'})
            seen_speech.add(location)
        previous = row['kind']
    return {'schema_version': 1, 'read_only': True, 'tracks': len(rows),
            'counts': dict(Counter(row['kind'] for row, _ in rows)),
            'issues': issues, 'limitations': 'Offline structure only; does not prove audio quality or airplay.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('playlist', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.playlist), indent=2))


if __name__ == '__main__':
    main()
