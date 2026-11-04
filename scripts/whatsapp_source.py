"""Link every phrase card to the teacher's original WhatsApp text (no harakat, as typed).

    python3 scripts/whatsapp_source.py "path/to/WhatsApp Chat with ....txt"
Writes data/whatsapp.json: { "<day>": { "<block>.<section>.<item>": {"ar": "...", "lines": [...]} } }
"""
import glob, json, os, re, sys
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAMP = re.compile(r'^\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}\s*[ap]m - [^:]+: ')
AR = re.compile(r'[؀-ۿ]')
DIAC = re.compile(r'[ً-ْٰـ]')
JUNK = re.compile(r'^[\s➖_\-–—✳️❇️🔖🎖*]*$')


def norm(s):
    s = DIAC.sub('', s)
    for a, b in (('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ة', 'ه'), ('ى', 'ي'), ('چ', 'ك'), ('ؤ', 'و'), ('ئ', 'ي')):
        s = s.replace(a, b)
    s = re.sub(r'[^ء-ي ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def day_num(line):
    m = re.search(r'\*\s*Day\s*([0-9️⃣🔟]+)\s*\*', line)
    if not m:
        return None
    t = m.group(1).replace('🔟', '10').replace('️', '').replace('⃣', '')
    return int(t) if t.isdigit() else None


def clean(line):
    line = STAMP.sub('', line).strip()
    line = re.sub(r'[*_]', '', line)
    line = re.sub(r'^[👈🔷🔹🔳🔲◾▪️\s]+', '', line)
    return line.strip()


def arabic_part(line):
    """the Arabic words of a line, as typed (keeps / ، ؟)"""
    t = re.sub(r'[^؀-ۿ\s/\\،؟?\-–]', ' ', line)
    t = re.sub(r'\s*[\\/]\s*', ' / ', t)
    t = re.sub(r'(^[\s/\-–]+|[\s/\-–]+$)', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def entries_by_day(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    days, cur = {}, None
    for ln in lines:
        n = day_num(ln)
        if n is not None:
            cur = n
            days[cur] = []
            continue
        if cur is not None:
            days[cur].append(ln)
    out = {}
    for d, ls in days.items():
        ents = []
        for i, ln in enumerate(ls):
            c = clean(ln)
            if not AR.search(c) or 'بالتوفيق' in c or 'مرحبا بكم' in c:
                continue
            ar = arabic_part(c)
            if len(norm(ar)) < 2:
                continue
            # the lines the teacher wrote under it (sound / meaning), until the next Arabic line
            ctx, blank = [], 0
            for nxt in ls[i + 1:i + 10]:
                cn = clean(nxt)
                if STAMP.match(nxt) or AR.search(cn):
                    break
                if not cn or JUNK.match(cn):
                    blank += 1
                    if blank > 1 or (ctx and not cn):
                        if len(ctx) >= 3:
                            break
                    continue
                ctx.append(cn)
                if len(ctx) >= 6:
                    break
            # text on the same line as the Arabic (e.g. "7 - سبعة - Sab'a", "مقابل - mugābil (Opposite)")
            rest = re.sub(r'[\u0600-\u06FF]+', ' ', c).replace('\u200e', '')
            rest = re.sub(r'\(\s*\)', ' ', rest)
            rest = re.sub(r'(\s*[-–/]\s*)+', ' - ', rest)
            rest = re.sub(r'\s+', ' ', rest).strip(' -–/')
            if re.search(r'\w', rest):
                ctx.insert(0, rest)
            ctx = [x.replace('\u200e', '') for x in ctx if re.search(r'[A-Za-z\u0B80-\u0BFF0-9]', x)]
            ents.append({"ar": ar, "n": norm(ar), "lines": ctx, "i": i})
        out[d] = ents
    return out


def variants(ar):
    groups = re.findall(r'\[[rbg]:([^\]]+)\]', ar)
    allopts = norm(re.sub(r'\[[rbg]:([^\]]+)\]', lambda m: ' '.join(m.group(1).split('|')), ar))
    first = norm(re.sub(r'\[[rbg]:([^\]]+)\]', lambda m: m.group(1).split('|')[0], ar))
    return {allopts, first} if groups else {first}


def score(item_ar, ent):
    best = 0
    parts = [p.strip() for p in re.split(r'/', ent["ar"])]
    cands = {ent["n"]} | {norm(p) for p in parts if norm(p)}
    for v in variants(item_ar):
        for c in cands:
            r = SequenceMatcher(None, v.replace(' ', ''), c.replace(' ', '')).ratio()
            best = max(best, r)
    return best


def main(chat):
    ents = entries_by_day(chat)
    res = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', 'days', 'day*.json'))):
        d = json.load(open(p, encoding='utf-8'))
        E = ents.get(d['day'], [])
        got, pos, tot = {}, -1, 0
        for bi, b in enumerate(d['blocks']):
            for si, s in enumerate(b['sections']):
                for ii, it in enumerate(s['items']):
                    tot += 1
                    scored = [(score(it['ar'], e) - (0.04 if k < pos - 3 else 0), k) for k, e in enumerate(E)]
                    if not scored:
                        continue
                    sc, k = max(scored)
                    if sc < 0.55:
                        continue
                    pos = max(pos, k)
                    got[f"{bi}.{si}.{ii}"] = {"ar": E[k]["ar"], "lines": E[k]["lines"]}
        res[str(d['day'])] = got
        print(f"Day {d['day']}: {len(got)}/{tot} phrases linked to the WhatsApp text")
    json.dump(res, open(os.path.join(ROOT, 'data', 'whatsapp.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)


if __name__ == '__main__':
    main(sys.argv[1])
