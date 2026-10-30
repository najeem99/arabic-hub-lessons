# Arabic Hub Lessons

A one-page study site for the **Arabic Language Hub** (Oct 08 module) WhatsApp course, in Gulf / UAE Arabic.

Every lesson day becomes a tab with:

- Arabic with full harakat, English + Tamil transliteration and meaning
- an expandable **word-by-word** breakdown on every phrase
- the teacher's **voice notes**, placed right after the phrases they explain
- **"Teacher says it"** buttons that play just the moment where the teacher says that phrase
- colour groups for interchangeable words (same colour = same meaning)
- a **quiz** across one or more days, with score, streak and review of misses
- star ☆ "I know this", listened ✓ progress, light / dark theme, phone side menu

Days 3–14 are included (Day 2 had no text; Day 11 was a revision class).

## Project layout

```
src/app.html            page template (styles + script); __DATA__ is replaced at build time
data/days/dayNN.json    lesson content, one file per day
data/clips.json         where the teacher says each phrase (made by scripts/match.py)
data/transcripts/       speech-recognition output per voice note (made by scripts/transcribe.py)
docs/index.html         the built site (served by GitHub Pages)
docs/audio/             compressed voice notes (mono 48 kbps MP3)
scripts/                build, compress, transcribe, match
```

## Build

Needs Python 3.10+ and `ffmpeg`.

```bash
python3 scripts/build.py          # writes docs/index.html and dist/artifact.html
```

Open `docs/index.html` in a browser, or serve the folder: `python3 -m http.server -d docs`.

## Add a new day

1. Compress the new voice notes:
   `scripts/compress_audio.sh ~/Downloads/AUD-2026xxxx-WA00xx.mp3 …`
2. Create `data/days/dayNN.json` (copy an existing day). One **block** = the text message(s) the teacher sent before a run of voice notes; list those notes in `audio` in chat order (`intro` for a note sent before the text).
   Phrase item: `{ar, ten, tta, en, tm, w: [[arabic, english], …], tag?, key?}` — colour groups as `[r:A|B]`, `[b:A|B]`, `[g:A|B]`.
3. Optional, for the "Teacher says it" buttons:
   ```bash
   pip install -r requirements.txt
   python3 scripts/transcribe.py   # ~real time on 2 CPU cores; skips notes already done
   python3 scripts/match.py        # updates data/clips.json and where each note sits
   ```
4. `python3 scripts/build.py`, check `docs/index.html`, commit.

## Publish with GitHub Pages

Settings → Pages → Build and deployment → *Deploy from a branch* → `main` / `/docs`.

> The voice notes and lesson text belong to the Arabic Language Hub course. Keep the repository **private** unless you have the course's permission to share them.
