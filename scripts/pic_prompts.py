#!/usr/bin/env python3
"""Write data/pic_prompts.json: one Gemini image prompt per dialogue phrase (single-word
vocabulary grids are skipped), with the same cast and style in every prompt so the pictures match.

Each entry: {key: "<day>.<block>.<sec>.<item>", file: "dNN-b-s-i.webp", day, ar, ten, en, prompt, done}.
`done` is true when docs/pics/<file> already exists. Also writes 2x2 "sheet" prompts (4 phrases in
one image, cropped apart by add_pics.py --grid) for when Gemini's daily image limit is tight.

Usage: python3 scripts/pic_prompts.py            (then generate the ones with done=false, newest day first)
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STYLE = ("Flat vector cartoon illustration, square 1:1. Soft rounded shapes, clean dark outlines, warm palette of "
         "sand, teal, coral and cream, simple background with a light hint of a modern UAE setting (villa, office, "
         "café, car or street as the scene needs). Friendly faces, big clear gestures, like a children's language book.")
CAST = ("Recurring characters, always drawn the same way: SAEED, young Emirati man, white kandura and white ghutra, "
        "short black beard; MARIAM, Emirati woman, black abaya and dark-blue shayla, kind smile; RAVI, South Indian "
        "man learning Arabic, glasses, light-blue shirt, dark trousers. Use one or two of them, as the line needs "
        "(MARIAM when the line is said to or by a woman).")
RULE = ("Show the meaning only through the action, gestures and faces. One character is clearly the speaker, with an "
        "EMPTY speech bubble. Absolutely no text, letters, numbers or words anywhere in the picture.")

def plain(t):  # strip colour-group markup [r:A|B] -> A
    return re.sub(r"\[[rbg]:([^|\]]+)(?:\|[^\]]*)?\]", r"\1", t or "")

def prompt_for(it, day_title):
    return (f"Create an image. {STYLE} {CAST} SCENE (lesson: {day_title}): the speaker says "
            f"\"{plain(it['en'])}\" (Gulf Arabic: {plain(it['ten'])}). Act this line out in an everyday Gulf "
            f"situation. {RULE}")

def main():
    out, sheets = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "days", "day*.json")), reverse=True):  # newest day first
        d = json.load(open(f, encoding="utf-8"))
        group = []
        for bi, b in enumerate(d["blocks"]):
            for si, s in enumerate(b["sections"]):
                if s.get("grid"):
                    continue  # single-word vocabulary, not a dialogue line
                for ii, it in enumerate(s["items"]):
                    k = f"{bi}.{si}.{ii}"
                    fn = f"d{d['day']:02d}-{bi}-{si}-{ii}.webp"
                    e = {"key": f"{d['day']}.{k}", "file": fn, "day": d["day"], "ar": plain(it["ar"]),
                         "ten": plain(it["ten"]), "en": plain(it["en"]), "prompt": prompt_for(it, d["title"]),
                         "done": os.path.exists(os.path.join(ROOT, "docs", "pics", fn))}
                    out.append(e)
                    if not e["done"]:
                        group.append(e)
                    if len(group) == 4:
                        sheets.append(group); group = []
        if group:
            sheets.append(group)
    sheet_prompts = [{"keys": [e["key"] for e in g],
                      "prompt": (f"Create one square image split into a 2x2 grid of {len(g)} separate equal panels "
                                 f"with thin white gutters (top-left, top-right, bottom-left, bottom-right). {STYLE} "
                                 f"{CAST} " + " ".join(f"PANEL {n+1}: the speaker says \"{e['en']}\" "
                                 f"(Gulf Arabic: {e['ten']})." for n, e in enumerate(g)) + f" {RULE}")}
                     for g in sheets]
    json.dump({"style": STYLE, "cast": CAST, "rule": RULE, "phrases": out, "sheets": sheet_prompts},
              open(os.path.join(ROOT, "data", "pic_prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(out)} phrases, {sum(e['done'] for e in out)} with a picture, {len(sheet_prompts)} 2x2 sheet prompts left")

if __name__ == "__main__":
    main()
