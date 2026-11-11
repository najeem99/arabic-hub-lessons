# CLAUDE.md: standing instructions for this repo

This repo is **Najeem's Gulf Arabic study site** for the Riyas *Arabic Language Hub* WhatsApp course (Oct 08 module). Najeem is a learner whose first language is Tamil. Read this whole file before you change anything. It records what Najeem has asked for so far, so they never have to repeat it.

> **Keep this file current.** If you add or change a feature, a workflow, a data format or a rule Najeem gives you, update CLAUDE.md (and README.md where it covers the same thing) **in the same commit**. A future session only knows what is written here.

---

## 1. Golden rules

1. **Push straight to `main`.** Every change Najeem asks for gets committed and pushed directly to `main` of `najeem99/arabic-hub-lessons`. No pull requests, no waiting for review. (Standing rule since 2026-11-10.) If your session was given a feature branch, still land the work on `main`: commit, then `git push origin HEAD:main` (rebase on `origin/main` first).
2. **GitHub Pages is the real site.** Najeem uses https://najeem99.github.io/arabic-hub-lessons/ (served from `docs/` on `main`). The claude.ai artifact study page (https://claude.ai/artifact/RRVLCZktK9fatoRHQBgX67) is optional; update it only if asked.
3. **Always rebuild before committing.** `python3 scripts/build.py` regenerates `docs/index.html`. Never hand-edit `docs/index.html`: edit `src/app.html` or `data/*` and rebuild. Commit the source change and the rebuilt `docs/index.html` together.
4. **Check the deploy.** After pushing, check the GitHub Actions run *pages build and deployment* for your commit. `najeem99.github.io` is blocked from the cloud container, so the Actions run is the only check. If the run ends "abandoned" or never starts (happened 2026-11-09), push again (any small real change) to trigger a fresh deploy.
5. **Gulf / UAE Arabic only.** Gulf form first; the course's formal word stays visible next to it. See section 3.
6. **Never invent lesson content.** Phrases, words and activities come from the teacher's messages and PDFs only.
7. **Pull first.** Other sessions push to `main` too. `git fetch origin main && git rebase origin/main` before you start and before you push. On a conflict in `docs/index.html`, take either side and just rebuild.
8. **Keep the course material private.** The voice notes and lesson text belong to the Arabic Language Hub. Do not post them anywhere outside this repo and Najeem's own pages.

---

## 2. What the site is

One page (`docs/index.html`) built from `src/app.html` + the JSON in `data/`. Phone layout at every screen width (desktop uses the same compact layout, narrow column). Features, all of which Najeem asked for:

| Area | What it does | Notes |
|---|---|---|
| **Day tabs / side menu** | One tab per lesson day, **newest day first** (tabs, menu, quiz picker, materials). Hash `#day-N`. | Najeem mostly studies the latest day. |
| **Phrase cards** | Arabic with full harakat, English + Tamil transliteration, English + Tamil meaning, expandable **word-by-word**, colour groups for interchangeable words. | |
| **Voice notes** | Teacher's notes placed **before** the phrases they explain ("Explains the N phrases below"). | Najeem plays audio first, then scrolls through the words. |
| **Teacher says it** | Per-phrase button that plays just that moment of the voice note (from `data/clips.json`). Dashed "≈" = approximate clip. | |
| **WhatsApp text** | Shows the phrase exactly as the teacher typed it (no harakat) with his transliteration lines (`data/whatsapp.json`). | |
| **Collapsible sections** | Each day's numbered sections fold; side-menu sections fold (`alh-drfold`). | Everything collapsible, collapsed by default where it's a list of sheets. |
| **Audio only** | Toggle (like the theme toggle) hiding lesson text, keeping voice notes; plays notes back to back with a chime. | `alh-audio-only` |
| **Mini player** | Bottom bar shown **whenever a note is playing or paused part-way**. Its round button **only toggles play/pause**; tapping the title area (with ^ chevron) opens the full-screen player. | Don't change this split again. |
| **Full-screen player** | Built for **driving**: big controls, play/pause, ±5 s skip, previous/next note, previous/next day, speed, Repeat (➡️ off, 🔂 audio, 📅 day; `alh-repeat`), shows and speaks "Day N · Audio x of y" and the day + topic when a new day starts. | Keep controls large and simple. |
| **Screen stays on** | Wake Lock while audio plays (muted looping video fallback for iPhone), released 12 s after stopping. | |
| **Headphone / car buttons** | Media Session: next/prev track changes note (crosses days), play/pause, ±5 s seek, lock-screen title. | |
| **Scroll progress bar** | Thin bar under the sticky header, reaches the end at page bottom. | |
| **Search** | Across all days in Arabic (harakat optional), sound, English or Tamil; results jump to the card. | |
| **Quiz** | Across one or more days; score, streak, review of misses. Hash `#quiz`. | |
| **Materials** | Course PDFs (in-page reader with prev/next, sortable by day: `alh-msort2`) + training videos on YouTube. Hash `#materials`. Days link to their "Lesson PDF" / "Training video". | Najeem wants them openable in any order. |
| **📋 Cheat sheets** (`#sheets`) | **Essentials only**: pronouns, possessive endings, and the tense charts from the live-class PPTs (past, present, future, past continuous, the practice answer keys, a past · present · future table), laid out **like the PPT slides** (verb شَرَبْ, order he/they/she · you · I/we). | Every sheet starts **collapsed**; Open all / Close all; filter by topic; 🙈 Hide Arabic to self-test; link to the source PDF page. |
| **🚶 On the go** (`#onthego`) | Practical sheets: everyday phrases from the lessons (I'm at work, I'm coming now…), numbers, ordinals, days, time, directions, greetings, plurals. | Numbers belong here, **not** in Cheat sheets. |
| Other | ☆ "I know this" stars, ✓ listened progress, light/dark theme (`alh-theme`), last day opened (`alh-last`). | localStorage keys all start `alh-`. |

---

## 3. Language rules (apply to site content AND to tutoring)

- **Gulf / UAE forms**, e.g. وِيَّاكْ wiyyāk (not مَعَكْ ma'ak), مُبْ mub, هْنِي hni, الْحِينْ al-heen, أَبَا abā / أَبْغَى, إِحْنَا ihna, إِنْتَ Inta, negate verbs with مَا (مَا أَحِبّْ, not لَا أَحِبّْ), يُومْ, -طَعَشْ numbers (إِحْدَعَشْ), ج pronounced y (يِيتْ) and ق as g where the Gulf does.
- If the lesson used a formal word, show the **Gulf word first and keep the lesson word visible**: as a colour-group alternative `[r:Gulf|lesson]`, or in the word row note, e.g. `["هْنِي", "here (Gulf; lesson هِنَا)"]`. The Gulf cleanup of Days 3–14 (PR #2, 2026-11-02) is the reference; its change list is in the project files `gulf-fixes/proposed-gulf-changes.md`.
- Before rewriting existing Arabic words in bulk, **send Najeem the list of proposed changes and wait for confirmation** (that's how the Gulf cleanup was done).
- **Every card**: full harakat on Arabic, `ten` (English-letter transliteration), `tta` (Tamil-script transliteration), `en`, `tm` (Tamil meaning), and a **required** `w` word-by-word list covering every word (small words too), with notes like "(Gulf)", "(to a woman)", "(ق = g)". `build.py` fails if `w` is missing.
- Interchangeable words: `[r:A|B]` red, `[b:A|B]` blue, `[g:A|B]` green. Same colour = same meaning, in `ar`, `ten`, `tta` and `w`.
- Follow the teacher's own Tamil transliteration style (e.g. மதா, ஹ்னி) and his English spellings where sensible.

### When acting as Najeem's tutor
- Use **only words and phrases from the lessons** in practice and quizzes, so the teacher doesn't think Najeem looked things up.
- Always show Arabic with harakat + transliteration + English (and Tamil where helpful).
- One phrase at a time with its word-by-word meaning, a quick quiz after each, a full revision at the end.
- A memory trick for each new word, preferably a Tamil or Hindi sound-alike.
- Activities: give the **Tamil** sentence, Najeem answers in Arabic, correct gently and show the right Gulf form.
- Voice practice: short replies, pause after each item, say "one, two, three" before a short Arabic word.
- When Najeem writes an Arabic word in chat they are learning, not switching language: reply in English with meaning, word-by-word, transliteration, Gulf usage, and say which day it comes from (search `data/days/`) or that it's new.
- When Najeem shares a new day's lesson: help them learn it, and add it to the site (section 4).

### Chat replies to Najeem
- Lead with the result, short and plain. Give the GitHub Pages link (with the hash, e.g. `#sheets`) when something changed on the site, and say deploys take a few minutes.
- Tech answers end with a `---` line, a bold "💡 Why this approach" heading, and 2–4 short `>` blockquote bullets.

---

## 4. Workflow: adding a new day (WhatsApp export)

Najeem uploads a **WhatsApp chat export `.zip`** (a `WhatsApp Chat with ….txt` plus the teacher's `AUD-YYYYMMDD-WA00NN.mp3` / `.opus` voice notes), or pastes the lesson text and attaches audio. Uploads in a Claude project land in `/mnt/project-files/uploads/hearth/<id>` with **no extension**; check with `file` and unzip into a fresh scratch folder (never into the repo; `raw/` and `*.zip` are git-ignored).

1. **Find the lesson.** Lessons start with a `*Day N*` header (emoji digits like `Day1️⃣7️⃣` too) from Riyas ALH. Ignore class reminders, Meet links, stickers, other members' messages and their voice notes. Only add days not already in `data/days/` (unless asked to redo one). Day 2 had no text; Day 11 was a revision class (no file).
2. **Compress ("trim") the voice notes** to small mono MP3s:
   `scripts/compress_audio.sh path/to/AUD-*.mp3` → `docs/audio/<same name>.mp3` (mono, 22.05 kHz, 48 kbps). Keep the original WhatsApp file name; it's how notes are referenced everywhere.
3. **Write `data/days/dayNN.json`** (copy a recent day such as `day19.json`):
   ```
   { "day": 19, "icon": "question", "title": "Questions 2 · When? / Is…?", "arTitle": "…", "ta": "<Tamil title>",
     "keys": ["key phrases…"], "guide": {…}?, "activity": {"items": [{"ta": "<Tamil sentence>", "en": "…"}], "hint": "…"},
     "blocks": [ { "intro": ["AUD-…mp3"]?, "audio": ["AUD-…mp3", …], "split": [12, 11]?,
                   "sections": [ {"title": "1. When?", "ar": "مَتَى", "ta": "எப்போது?", "note"?, "grid"?,
                                  "items": [ {"ar","ten","tta","en","tm","w":[[ar,en],…],"tag"?,"key"?} ] } ] } ] }
   ```
   - One **block** = the text message(s) the teacher sent before a run of voice notes; `audio` lists those notes in chat order. `intro` = a note sent before any text of the day. A text message with no notes of its own joins the next block.
   - `icon` ∈ wave, people, pray, calendar, numbers, clock, hand, food, no, compass, question, book.
   - `grid: true` only for single-word vocabulary sections. `key: true` marks key phrases.
   - `activity` comes from the day's `ACTIVITY DAY-N` list (Tamil sentences); add English and a `hint` with the lesson words to use.
4. **Teacher clips** ("Teacher says it"):
   ```bash
   pip install -r requirements.txt     # faster-whisper, numpy
   python3 scripts/transcribe.py       # data/transcripts/<note>.json, ~real time on 2 cores; run in background
   python3 scripts/match.py            # updates data/clips.json and data splits
   ```
   `match.py` fuzzy-matches each phrase (and its Gulf/lesson variants) against the transcript, keeps teaching order, and fills gaps with approximate clips. Whisper downloads its model from huggingface.co, which was blocked from the cloud container on 2026-11-05 (Days 16–17 have no clips) but worked for Days 18–19 on 2026-11-11. If it's blocked, skip clips and say so; no clip is better than a wrong one.
5. **WhatsApp text**: `python3 scripts/whatsapp_source.py "path/to/WhatsApp Chat with ….txt"` → `data/whatsapp.json`.
6. **Build, check, push**: `python3 scripts/build.py` (prints phrases / voice notes per day and warns on missing audio, materials or transliteration), commit `data/ docs/` (and README/CLAUDE.md if counts or features changed: README says "Days 3–N are included"), push to `main`, check the Pages run.
7. **Reply** in 2–3 lines: days added, phrase and voice-note counts, how many phrases got a teacher clip, and anything skipped. Then offer to teach the new day (section 3).

---

## 5. Workflow: materials, videos, cheat sheets

- **Course PDFs** come from Najeem's Notion page "Arabic Class" (Najeem Home / Arabic Class) or uploads in the project. Put the PDF in `docs/materials/<kebab-name>.pdf` plus a first-page cover `<same-name>.jpg`, and add an entry to `data/materials.json`: `{file, thumb, day (number or null), kind?, title, ar, ta, by, pages}`. Sorted by day in the UI.
- **Training videos** (YouTube): `data/videos.json` entries `{id, day (or null), kind?, title, yt}`; `id` is the YouTube video id.
- **Cheat sheets / On the go**: `data/cheatsheets.json`, a list of sheets `{id, set: "cheat"|"go", group, title, ar, ta, day?, src: {file, pages, p}?, note?, cols: [{k, label, type: "ar"|"txt"|"ta", t?: <translit key>, under?: <col it folds under on phones>}], rows: [{…}]}`. Gulf form first with the slide's formal word alongside (e.g. إِحْنَا with نَحْنُ). Cheat sheets = grammar essentials copied from the trainers' slides only; everyday/practical tables go in On the go. When a new grammar PPT/PDF arrives, add it to materials **and** a sheet here.

---

## 6. File layout

```
CLAUDE.md                this file (keep it current)
README.md                human-facing overview, build and add-a-day steps
src/app.html             the whole app: CSS + JS; placeholders __DATA__, __MATERIALS__, __SHEETS__, __VIDEOS__
data/days/dayNN.json     lesson content, one file per day (Days 3–19 now; no 11)
data/clips.json          per-phrase teacher clips {day: {items: {"block.sec.item": {f,s,e,r,approx?}}, splits}} (match.py)
data/transcripts/        whisper word timestamps per note (transcribe.py)
data/whatsapp.json       original WhatsApp text per card (whatsapp_source.py)
data/materials.json      course PDFs list
data/videos.json         training videos list
data/cheatsheets.json    Cheat sheets + On the go tables
docs/index.html          BUILT site served by GitHub Pages (don't hand-edit)
docs/audio/              compressed voice notes (AUD-*.mp3)
docs/materials/          PDFs + .jpg covers
docs/.nojekyll           keep (Pages serves files as-is)
dist/artifact.html       BUILT page body for the claude.ai artifact (git-ignored)
scripts/build.py         stitches everything into docs/index.html + dist/artifact.html
scripts/compress_audio.sh  WhatsApp notes -> mono 48 kbps MP3s in docs/audio/
scripts/transcribe.py    faster-whisper transcription with word timestamps
scripts/match.py         finds each phrase inside the notes -> data/clips.json
scripts/whatsapp_source.py  links cards to the WhatsApp export -> data/whatsapp.json
```

Needs Python 3.10+ and `ffmpeg`/`ffprobe` (build.py reads note durations). Preview locally: `python3 -m http.server -d docs`, and check phone width (~390 px) as well as desktop, light and dark.

---

## 7. UI conventions

- Phone-first; the same layout on desktop. No horizontal scrolling; on phones secondary table columns fold under the main one (`under`).
- Lists of things (cheat sheets, menu sections) start **collapsed**; offer Open all / Close all.
- Audio comes before the text it explains.
- Keep player controls big and simple (Najeem listens while driving).
- Arabic always with harakat and its transliteration next to it.
- Newest content first (days, materials sort default desc).
- New views get a hash route (`#quiz`, `#materials`, `#sheets`, `#onthego`, `#day-N`) and a side-menu entry.
- Store per-viewer settings in `localStorage` with an `alh-` prefix, wrapped so the page works without it.

---

## 8. Optional: the claude.ai artifact study page

Only when Najeem asks. `python3 scripts/build.py` writes `dist/artifact.html`; publish that file to https://claude.ai/artifact/RRVLCZktK9fatoRHQBgX67, sending only **new** audio as files `audio/<name>.mp3` and new PDFs/covers as `materials/<name>` (files already on the artifact stay). The page declares the `downloads` capability (plain `<a download>` does nothing in artifacts). Before publishing, compare the live page's days with your build so you don't drop a day another session added.

---

## 9. History of Najeem's requests (newest first)

- 2026-11-11: this CLAUDE.md; keep it updated with every workflow/feature change.
- 2026-11-11: Cheat sheets = essentials laid out like the PPT; new On the go menu; numbers moved there; everything collapsible, collapsed by default.
- 2026-11-11: Cheat sheets from the PDF chart pages as tables; Days 18 (Adjectives) and 19 (Questions 2) added with 4 live-class PDFs (past, present & future, past continuous, meet a new person).
- 2026-11-10: mini player shows whenever audio plays; button = play/pause, title = open full player.
- 2026-11-10: days listed newest first. Rule: push everything directly to main; GitHub Pages is the page used.
- 2026-11-09: Materials (Notion PDFs + YouTube training videos, sortable, any order); audio before text; collapsible sections; driving-friendly player with repeat modes and distinct emoji.
- 2026-11-06: keep screen on while playing; headphone/car next/prev buttons.
- 2026-11-05: Day 17; ±5 s skip; full-screen player; prev/next note and day; spoken day and topic.
- 2026-11-04: WhatsApp-text button; Days 15–16.
- 2026-11-03: Audio only toggle; scroll progress bar.
- 2026-11-02: Gulf Arabic word fixes (confirmed list first); phone layout on desktop.
