# GOLD FM Playlist Audit

A small, dependency-free, read-only checker for exported XSPF/ProppFrexx playlists.

This is a new standalone open-source project, extracted as a general idea from operational radio diagnostics. It is not the GOLD FM commercial Studio app and has no established external adoption yet. It does not connect to or control an on-air system.

Requires Python 3.10 or later.

```sh
python3 audit.py /path/to/export.pfp
python3 -m unittest discover -s tests -v
```

The JSON report detects adjacent jingles, repeated speech files, missing locations and invalid cue order. Entry types 0, 3 and 48 are interpreted as music, jingle and speech; other types are reported as unknown. It does not open audio files, change tags, save a playlist, access the network or prove airplay. Report output omits all paths, titles and artists. The input remains private and unchanged.

Contributions: open an issue with a synthetic minimal playlist, expected result and Python version. Do not submit real station logs, credentials, listener details, copyrighted media or voice references. Please discuss broader integration changes before implementing them.

MIT licensed. Not affiliated with ProppFrexx or OpenAI.
