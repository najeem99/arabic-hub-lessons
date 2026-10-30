"""Stitch every day in data/days/*.json into ONE page: docs/index.html (audio in docs/audio/)

Add a new day: drop data/days/dayNN.json in (same format), put its voice notes in docs/audio/, run
    python3 scripts/build.py

Day JSON:
{ "day": 4, "icon": "people", "title": "...", "arTitle": "...", "ta": "...", "keys": [...],
  "guide": {"title":..,"rows":[{ar,head,en,ta}]}?, "activity": {"items":[{"ta":..,"en":..}], "hint": ..}?,
  "blocks": [            # one block = one WhatsApp text message (or several sent in a row)
    { "intro": ["AUD-x.mp3"],        # voice notes sent BEFORE the text (optional)
      "audio": ["AUD-y.mp3", ...],   # voice notes sent AFTER the text, in chat order
      "split": [12, 11, ...],        # optional: phrases each voice note covers (else shared by length)
      "sections": [ {title, ar, ta, note?, grid?, items:[{ar,ten,tta,en,tm,w,tag?,key?}]} ] } ] }
Colour groups in ar/ten/tta/w: [r:A|B] red, [b:A|B] blue, [g:A|B] green  (same colour = same meaning).
"""
import glob, json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
AUDIO = os.path.join(DOCS, "audio")
ICONS = {"wave", "people", "pray", "calendar", "numbers", "clock", "hand", "food", "no", "compass", "question", "book"}


def dur(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", os.path.join(AUDIO, f)], capture_output=True, text=True).stdout
    return round(float(out.strip()), 1)


CLIPS = json.load(open(os.path.join(DATA, "clips.json"), encoding="utf-8")) if os.path.exists(os.path.join(DATA, "clips.json")) else {}


def prepare(path):
    d = json.load(open(path, encoding="utf-8"))
    C = CLIPS.get(str(d["day"]), {"items": {}, "splits": {}})
    total_audio = sum(len(b.get("intro", [])) + len(b.get("audio", [])) for b in d["blocks"])
    n, sections, used = 0, [], []
    for bi, b in enumerate(d["blocks"]):
        secs = [dict(s, items=[dict(it) for it in s["items"]]) for s in b["sections"]]
        for si, s in enumerate(secs):  # teacher's own pronunciation, cut from his voice note
            for ii, it in enumerate(s["items"]):
                c = C["items"].get(f"{bi}.{si}.{ii}")
                if c:
                    it["clip"] = {"f": c["f"], "s": c["s"], "e": c["e"]}
                    if c.get("approx"):
                        it["clip"]["a"] = 1
        for s in secs:
            for it in s["items"]:
                assert it.get("w"), f"Day {d['day']}: missing word-by-word for {it.get('ar')}"
        for f in b.get("intro", []):
            n += 1
            used.append(f)
            secs[0]["items"].insert(0, {"audio": {"file": f, "n": n, "of": total_audio, "dur": dur(f),
                                                  "label": "Introduction · listen first"}})
        auds = b.get("audio", [])
        if auds:
            flat = [(si, ii) for si, s in enumerate(secs) for ii, it in enumerate(s["items"]) if "audio" not in it]
            N = len(flat)
            durs = [dur(f) for f in auds]
            split = b.get("split") or C["splits"].get(str(bi))
            if split:
                cuts, c = [], 0
                for k in split:
                    c += k
                    cuts.append(min(c, N))
            else:
                tot, c, cuts = sum(durs), 0, []
                for k, x in enumerate(durs):
                    c += x
                    lo = (cuts[-1] if cuts else 0) + 1
                    hi = N - (len(durs) - k - 1)
                    cuts.append(max(lo, min(hi, round(N * c / tot))))
            cuts[-1] = N
            inserts, prev = [], 0
            for f, x, cut in zip(auds, durs, cuts):
                n += 1
                used.append(f)
                si, ii = flat[cut - 1]
                cnt = cut - prev
                label = f"Explains the {cnt} phrases above" if cnt > 1 else "Explains the phrase above"
                inserts.append((si, ii, {"audio": {"file": f, "n": n, "of": total_audio, "dur": x, "label": label}}))
                prev = cut
            for si, ii, a in sorted(inserts, key=lambda t: (t[0], t[1]), reverse=True):
                secs[si]["items"].insert(ii + 1, a)
        sections += secs
    page = {k: d[k] for k in ("day", "icon", "title", "arTitle", "ta", "keys", "guide", "activity") if k in d}
    if page.get("icon") not in ICONS:
        page["icon"] = "book"
    page["sections"] = sections
    return page, used


def main():
    days, used = [], []
    for p in sorted(glob.glob(os.path.join(DATA, "days", "day*.json"))):
        page, u = prepare(p)
        days.append(page)
        used += u
        cards = sum(1 for s in page["sections"] for i in s["items"] if "audio" not in i)
        print(f"Day {page['day']:>2}: {cards:>3} phrases, {len(u)} voice notes")
    days.sort(key=lambda d: d["day"])
    tpl = open(os.path.join(ROOT, "src", "app.html"), encoding="utf-8").read()
    body = tpl.replace("__DATA__", json.dumps(days, ensure_ascii=False, separators=(",", ":")))
    missing = [f for f in used if not os.path.exists(os.path.join(AUDIO, f))]
    if missing:
        print("WARNING missing audio in docs/audio:", ", ".join(missing))
    # docs/index.html: full standalone page (GitHub Pages / open locally)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<style>:root{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
            'body{margin:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>\n'
            '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(page)
    # dist/artifact.html: same page without the document wrapper (for a claude.ai Artifact)
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    open(os.path.join(ROOT, "dist", "artifact.html"), "w", encoding="utf-8").write(body)
    print(f"{len(days)} days, {len(used)} voice notes -> docs/index.html")


if __name__ == "__main__":
    main()
