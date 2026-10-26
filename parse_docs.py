# -*- coding: utf-8 -*-
"""Parse 毛泽东选集.txt into one document per text: title + year + footnote-free body."""
import re, json

with open(r"E:\502\maoxuan.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()

Z = "〇○◯ＯOo0０零"                       # zero written various ways
NUM = Z + "一二三四五六七八九十"
date_re = re.compile(rf"^\s*（[{NUM}]+年.*）\s*$")
bare_date_re = re.compile(rf"^[{NUM}]{{4}}年[{NUM}]{{1,2}}月[{NUM}]{{0,2}}日")   # 1999-style closing date, maybe + 于北京
footnote_re = re.compile(r"^\s*〔\d+〕")
inline_re = re.compile(r"〔\d+〕")
star_re = re.compile(r"^[\u3000 ]*[＊*]")
header_re = re.compile(r"^(第.+[卷篇]|毛泽东选集|.*时期（[一二三四五六七八九十]+）)$")

def is_note_header(s):
    return re.sub(r"[\s\u3000]", "", s) == "注释"

def stop_cond(raw, s):
    if footnote_re.match(s): return True
    if star_re.match(raw): return True
    if is_note_header(s): return True
    if header_re.match(s) or s.endswith("时期"): return True
    if bare_date_re.match(s): return True
    if date_re.match(s): return True
    return False

def title_block(d):
    """Collect title lines walking back from date line d."""
    block = []
    j, gap = d - 1, 0
    while j >= 0:
        raw, s = lines[j], lines[j].strip()
        if not s:
            gap += 1
            if block and gap >= 2:
                break
            j -= 1
            continue
        if stop_cond(raw, s) or len(s) > 35 or s.endswith("。"):
            break
        block.append((j, s))
        gap = 0
        j -= 1
    block.reverse()
    return block

idx = [i for i, l in enumerate(lines) if date_re.match(l)]

# ---- build documents ----
docs = []           # (title, year, body_start, body_end_exclusive, date_line)
internal_dates = [] # NOBLOCK date lines (belong to previous doc)
for k, d in enumerate(idx):
    blk = title_block(d)
    if not blk:
        internal_dates.append(d)
        continue
    title = "".join(s for _, s in blk)
    title = inline_re.sub("", title).rstrip("*＊").strip()
    year_str = re.search(rf"（([{NUM}]+)年", lines[d]).group(1)
    digits = []
    for c in year_str:
        if c in "〇○◯ＯOo0０零":
            digits.append("0")
        else:
            digits.append(str("一二三四五六七八九".index(c) + 1))
    year = int("".join(digits))
    body_start = d + 1
    body_end = None               # filled in after the loop: next doc's first title line
    title_start = blk[0][0]
    docs.append({"title": title, "year": year, "body_start": body_start,
                 "title_start": title_start, "date_line": d})

for k in range(len(docs)):
    docs[k]["body_end"] = docs[k + 1]["title_start"] if k + 1 < len(docs) else len(lines)

# ---- diagnostics ----
rep = []
rep.append(f"date lines: {len(idx)}   docs: {len(docs)}   internal(NOBLOCK) dates: {len(internal_dates)}")
rep.append("=== internal dates (kept inside previous doc's body) ===")
for d in internal_dates:
    prev = next((lines[j].strip() for j in range(d - 1, -1, -1) if lines[j].strip()), "?")
    rep.append(f"  L{d}: after {prev[:40]!r} date={lines[d].strip()}")

rep.append("=== all doc titles ===")
for i, doc in enumerate(docs):
    rep.append(f"[{i:3d}] {doc['year']}  {doc['title']}")

rep.append("=== suspicious titles ===")
for i, doc in enumerate(docs):
    t = doc["title"]
    if "。" in t or len(t) > 40 or bare_date_re.match(t):
        rep.append(f"[{i}] {doc['year']} {t!r}")

# ---- body extraction with footnote truncation ----
SENT_END = "。！？；…”"   # characters that may legitimately end a sentence/paragraph
n_salvaged = 0
mid_trig_other = []

def clean_body(bs, be):
    """Collect body lines, cutting at the footnote section. A * note line that
    interrupts a mid-sentence paragraph is stripped of the note and kept."""
    global n_salvaged
    out, cut = [], None
    for j in range(bs, be):
        raw, s = lines[j], lines[j].strip()
        if not s:
            continue
        trig_star = star_re.match(raw) is not None
        trig_other = (footnote_re.match(s) is not None) or is_note_header(s)
        if trig_star or trig_other:
            mid = bool(out) and out[-1][-1] not in SENT_END
            if trig_star and mid:
                t = re.sub(r"^[\u3000 ]*[＊*]\s*", "", s)
                p = t.find("。")
                if p != -1 and len(t) - p > 10:   # note merged with body continuation
                    out.append(t[p + 1:])
                    n_salvaged += 1
                    continue
            cut = j
            break
        out.append(s)
    return out, cut

n_cut_late, leftover_marker, leftover_note, yj = 0, 0, 0, []
for i, doc in enumerate(docs):
    body_lines, cut = clean_body(doc["body_start"], doc["body_end"])
    text = "\n".join(body_lines)
    text = inline_re.sub("", text)
    doc["body"] = text
    if cut is not None:
        rel = (cut - doc["body_start"]) / max(1, doc["body_end"] - doc["body_start"])
        if rel < 0.5:
            yj.append((i, round(rel, 2), lines[cut].strip()[:40]))
        if body_lines and body_lines[-1][-1] not in SENT_END:
            mid_trig_other.append((i, lines[cut].strip()[:30]))
    if "静火有言" in text: leftover_note += 1
    if inline_re.search(text): leftover_marker += 1

rep.append(f"=== salvaged * note lines merged with body: {n_salvaged} ===")
rep.append("=== cut while paragraph mid-sentence (possible lost text) ===")
for i, frag in mid_trig_other:
    rep.append(f"[{i}] cut at {frag!r}")

rep.append(f"=== docs still containing 静火有言: {leftover_note}, leftover 〔n〕: {leftover_marker} ===")
rep.append("=== early footnote cuts (rel<0.5) ===")
for i, rel, frag in yj:
    rep.append(f"[{i}] rel={rel} cut at {frag!r}")

with open(r"E:\502\docs.json", "w", encoding="utf-8") as f:
    json.dump([{"title": d["title"], "year": d["year"], "body": d["body"]} for d in docs], f, ensure_ascii=False)

with open(r"E:\502\parse_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(rep))

print(f"docs={len(docs)} internal={len(internal_dates)} salvaged={n_salvaged} report -> parse_report.txt, docs -> docs.json")
print("body chars: min=%d max=%d" % (min(len(d['body']) for d in docs), max(len(d['body']) for d in docs)))
