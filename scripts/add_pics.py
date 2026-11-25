#!/usr/bin/env python3
"""Add Gemini scene pictures to the site: compress to 480x480 WebP in docs/pics/ and record them in data/pics.json.

  python3 scripts/add_pics.py IMAGE KEY [IMAGE KEY ...]        one picture per phrase
  python3 scripts/add_pics.py --grid IMAGE K1 K2 [K3 K4]       a 2x2 sheet, cut into 4 pictures (reading order)

KEY is "<day>.<block>.<sec>.<item>", as in data/pic_prompts.json. Then run pic_prompts.py and build.py.
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICS = os.path.join(ROOT, "data", "pics.json")
SIZE = 480

def square(im):
    w, h = im.size; m = min(w, h)
    return im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))

def save(im, key, db):
    day, b, s, i = key.split(".")
    fn = f"d{int(day):02d}-{b}-{s}-{i}.webp"
    im = square(im.convert("RGB")).resize((SIZE, SIZE), Image.LANCZOS)
    im.save(os.path.join(ROOT, "docs", "pics", fn), "WEBP", quality=72, method=6)
    db.setdefault(str(int(day)), {})[f"{b}.{s}.{i}"] = fn
    print(key, "->", fn, os.path.getsize(os.path.join(ROOT, "docs", "pics", fn)) // 1024, "KB")

def main(a):
    os.makedirs(os.path.join(ROOT, "docs", "pics"), exist_ok=True)
    db = json.load(open(PICS, encoding="utf-8")) if os.path.exists(PICS) else {}
    if a and a[0] == "--grid":
        im = Image.open(a[1]); w, h = im.size; g = 6  # trim the white gutter between panels
        boxes = [(0, 0, w // 2 - g, h // 2 - g), (w // 2 + g, 0, w, h // 2 - g),
                 (0, h // 2 + g, w // 2 - g, h), (w // 2 + g, h // 2 + g, w, h)]
        for key, box in zip(a[2:6], boxes):
            save(im.crop(box), key, db)
    else:
        for path, key in zip(a[0::2], a[1::2]):
            save(Image.open(path), key, db)
    db = {d: dict(sorted(v.items())) for d, v in sorted(db.items(), key=lambda x: int(x[0]))}
    json.dump(db, open(PICS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1:])
