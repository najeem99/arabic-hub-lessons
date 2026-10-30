"""Find where the teacher says each phrase inside his voice notes.

Reads data/days/day*.json + data/transcripts/<note>.json (word timestamps), writes data/clips.json:
    python3 scripts/match.py
 { "<day>": { "items": { "<sec>.<item>": {"f": note, "s": start, "e": end, "r": score} },
              "splits": { "<block>": [phrases covered by each note, in chat order] } } }
"""
import glob, json, os, re, itertools
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAC = re.compile(r'[ً-ْٰـ]')


def norm(s):
    s = DIAC.sub('', s)
    for a, b in (('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ٱ', 'ا'), ('ة', 'ه'), ('ى', 'ي'), ('ؤ', 'و'), ('ئ', 'ي'),
                 ('چ', 'ك'), ('گ', 'ق'), ('ڤ', 'ف')):
        s = s.replace(a, b)
    s = re.sub(r'[^ء-ي ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


ALIAS = {'احنا': 'نحن', 'هني': 'هنا', 'الحين': 'الان', 'وياك': 'معك', 'وياي': 'معي', 'شو': 'ماذا', 'باكر': 'بكره', 'باجر': 'بكره',
         'ديay': 'دجاج', 'دياي': 'دجاج', 'سمك': 'سمك', 'يوعان': 'جوعان', 'ايلس': 'اجلس', 'ايي': 'اجي', 'يي': 'يجي', 'ياي': 'جاي'}
LESSON = re.compile(r'(?:lesson:?|formal)\s*([\u0600-\u06FF\u064B-\u0652 ]+)')


def lesson_variants(it, base):
    """also try the lesson's own wording where the card shows a Gulf swap"""
    swaps = {}
    for a_, e_ in it.get('w', []):
        m = LESSON.search(e_)
        src = norm(re.sub(r'\[[rbg]:([^\]]+)\]', lambda x: x.group(1), a_))
        if m and src:
            swaps[src] = norm(m.group(1))
    out = set()
    for v in base:
        words = v.split()
        alt = [swaps.get(w, ALIAS.get(w, w)) for w in words]
        if alt != words:
            out.add(' '.join(alt))
    return list(out)


def variants(ar):
    groups = re.findall(r'\[[rbg]:([^\]]+)\]', ar)
    opts = [g.split('|') for g in groups]
    out = set()
    n = max([len(o) for o in opts] or [1])
    for k in range(n):  # option k of every group (falls back to the last option)
        it = iter([o[min(k, len(o) - 1)] for o in opts])
        out.add(norm(re.sub(r'\[[rbg]:[^\]]+\]', lambda m: next(it), ar)))
    return [v for v in out if v]


def ratio(a, b):
    return SequenceMatcher(None, a.replace(' ', ''), b.replace(' ', '')).ratio()


def candidates(vs, words, fi, toff):
    """best windows of the transcript matching any variant of one phrase"""
    found = []
    for v in vs:
        k = len(v.split())
        vlen = len(v.replace(' ', ''))
        thr = 0.86 if vlen <= 4 else 0.8
        for L in {max(1, k - 1), k, k + 1}:
            for i in range(0, len(words) - L + 1):
                win = words[i:i + L]
                txt = ' '.join(w[2] for w in win)
                if not txt:
                    continue
                r = ratio(v, txt)
                if r >= thr:
                    found.append((r, fi, win[0][0], win[-1][1], toff + win[0][0]))
    found.sort(reverse=True)
    keep, seen = [], []
    for c in found:  # drop overlapping duplicates, keep up to 6 places
        if any(c[1] == s[1] and abs(c[2] - s[2]) < 1.0 for s in seen):
            continue
        seen.append(c)
        keep.append(c)
        if len(keep) >= 6:
            break
    return keep


def main():
    res = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', 'days', 'day*.json'))):
        d = json.load(open(p, encoding='utf-8'))
        day = {"items": {}, "splits": {}}
        for bi, b in enumerate(d['blocks']):
            notes = b.get('audio', [])
            allnotes = b.get('intro', []) + notes
            trs = []
            toff = 0.0
            for fi, f in enumerate(allnotes):
                tp = os.path.join(ROOT, 'data', 'transcripts', f + '.json')
                if not os.path.exists(tp):
                    trs = None
                    break
                segs = json.load(open(tp, encoding='utf-8'))
                words = [(w[0], w[1], norm(w[2])) for s in segs for w in s['w']]
                words = [w for w in words if w[2]]
                trs.append((f, words, toff))
                toff += (segs[-1]['e'] if segs else 0) + 1
            if not trs:
                continue
            phrases = [(si, ii, it) for si, s in enumerate(b['sections']) for ii, it in enumerate(s['items'])]
            cands = []  # (globaltime, phrase_idx, score, file, start, end)
            for pi, (si, ii, it) in enumerate(phrases):
                vs = variants(it['ar'])
                vs += lesson_variants(it, vs)
                for fi, (f, words, off) in enumerate(trs):
                    for r, _, s0, e0, g in candidates(vs, words, fi, off):
                        cands.append((g, pi, r, f, s0, e0))
            # monotonic alignment: phrases taught in order → maximise total score
            cands.sort()
            best, prev = [0.0] * len(cands), [-1] * len(cands)
            for c in range(len(cands)):
                best[c] = cands[c][2]
                for q in range(c):
                    if cands[q][1] < cands[c][1] and cands[q][0] < cands[c][0] and best[q] + cands[c][2] > best[c]:
                        best[c], prev[c] = best[q] + cands[c][2], q
            chosen = []
            if cands:
                c = max(range(len(cands)), key=lambda x: best[x])
                while c != -1:
                    chosen.append(cands[c])
                    c = prev[c]
            chosen.reverse()
            last_by_note = {}
            for g, pi, r, f, s0, e0 in chosen:
                si, ii, _ = phrases[pi]
                # stretch over the other spoken alternatives that follow closely (X / Y / Z)
                for (g2, pj, r2, f2, s2, e2) in cands:
                    if pj == pi and f2 == f and s0 < s2 <= e0 + 4 and e2 - s0 <= 10:
                        e0 = max(e0, e2)
                day["items"][f"{bi}.{si}.{ii}"] = {"f": f, "s": round(max(0, s0 - 0.15), 2), "e": round(e0 + 0.35, 2), "r": round(r, 2)}
                last_by_note[f] = max(last_by_note.get(f, -1), pi)
            # where each full note goes: after the last phrase it explains
            if notes and any(f in last_by_note for f in notes):
                cuts, prevc = [], 0
                for k, f in enumerate(notes):
                    cut = max(prevc + 1, last_by_note.get(f, prevc) + 1)
                    cut = min(cut, len(phrases) - (len(notes) - k - 1))
                    cuts.append(cut)
                    prevc = cut
                cuts[-1] = len(phrases)
                day["splits"][str(bi)] = [cuts[0]] + [cuts[k] - cuts[k - 1] for k in range(1, len(cuts))]
            print(f"Day {d['day']} block {bi}: {sum(1 for (g,pi,r,f,s0,e0) in chosen)}/{len(phrases)} phrases found in {len(allnotes)} notes",
                  day["splits"].get(str(bi), ""))
        res[str(d['day'])] = day
    json.dump(res, open(os.path.join(ROOT, 'data', 'clips.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)


if __name__ == '__main__':
    main()
