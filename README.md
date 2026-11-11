# Arabic Hub Lessons

A one-page study site for the **Arabic Language Hub** (Oct 08 module) WhatsApp course, in Gulf / UAE Arabic.

Every lesson day becomes a tab with:

- Arabic with full harakat, English + Tamil transliteration and meaning
- an expandable **word-by-word** breakdown on every phrase
- the teacher's **voice notes**, placed right after the phrases they explain
- **"Teacher says it"** buttons that play just the moment where the teacher says that phrase
- a **WhatsApp text** button showing the phrase exactly as the teacher typed it (no harakat, with his transliteration lines)
- colour groups for interchangeable words (same colour = same meaning)
- a **quiz** across one or more days, with score, streak and review of misses
- **search** across all days in Arabic (harakat optional), sound, English or Tamil — results show day and topic and jump to the card
- a **Materials** view: the course PDFs (read in the page, sorted by day) and the training videos on YouTube, plus a "Lesson PDF" / "Training video" link on matching days
- **Cheat sheets** (collapsed by default — tap a sheet to open it, or "Open all"): the chart pages of the course PDFs (pronouns, possessive endings, verb forms, numbers, ordinals, days, time, prepositions, directions, broken plurals…) as tables with Arabic + harakat, transliteration, English and Tamil, Gulf word first. Filter by topic, jump to the source PDF page, or hide the Arabic to test yourself. Matching days link to their sheet.
- star ☆ "I know this", listened ✓ progress, light / dark theme, phone side menu

Days 3–19 are included (Day 2 had no text; Day 11 was a revision class). Days 16–17 have voice notes but no "Teacher says it" clips yet.

## Project layout

```
src/app.html            page template (styles + script); __DATA__ is replaced at build time
data/days/dayNN.json    lesson content, one file per day
data/clips.json         where the teacher says each phrase (made by scripts/match.py)
data/whatsapp.json      each phrase's original WhatsApp text (made by scripts/whatsapp_source.py)
data/transcripts/       speech-recognition output per voice note (made by scripts/transcribe.py)
docs/index.html         the built site (served by GitHub Pages)
docs/audio/             compressed voice notes (mono 48 kbps MP3)
docs/materials/         course PDFs + first-page covers (listed in data/materials.json)
data/videos.json        training videos (YouTube ids, matched to days)
data/cheatsheets.json   cheat-sheet tables (cols: ar / txt / ta; "t" = transliteration key, "under" = folds under another column on phones)
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
4. Link each phrase to its original WhatsApp text:
   `python3 scripts/whatsapp_source.py "path/to/WhatsApp Chat with ….txt"`
5. `python3 scripts/build.py`, check `docs/index.html`, commit.

## Publish with GitHub Pages

Settings → Pages → Build and deployment → *Deploy from a branch* → `main` / `/docs`.

> The voice notes and lesson text belong to the Arabic Language Hub course. Keep the repository **private** unless you have the course's permission to share them.
