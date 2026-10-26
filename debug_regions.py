# -*- coding: utf-8 -*-
import json, re

with open(r"E:\502\maoxuan.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()

Z = "〇○◯ＯOo0０零"
NUM = Z + "一二三四五六七八九"
date_re = re.compile(rf"^\s*（[{NUM}]+年.*）\s*$")
idx = [i for i, l in enumerate(lines) if date_re.match(l)]

out = []
# telegram region: dump raw lines 31390-31470
out.append("=== raw lines 31390-31470 ===")
for i in range(31390, 31470):
    out.append(f"{i:5d} {lines[i]!r}")

# for suspicious docs, dump their region with cut marker
with open(r"E:\502\docs.json", encoding="utf-8") as f:
    docs = json.load(f)

# rebuild doc boundaries quickly: recompute from parse logic minimally
# simpler: locate by title in lines? Instead re-run boundary calc:
def is_note_header(s):
    return re.sub(r"[\s\u3000]", "", s) == "注释"
star_re = re.compile(r"^[\u3000 ]*[＊*]")
footnote_re = re.compile(r"^\s*〔\d+〕")

# map doc index -> (body_start, body_end) using same algorithm
bare_date_re = re.compile(rf"^[{NUM}]{{4}}年[{NUM}]{{1,2}}月[{NUM}]{{0,2}}日")
header_re = re.compile(r"^(第.+[卷篇]|毛泽东选集|.*时期（[一二三四五六七八九十]+）)$")
def stop_cond(raw, s):
    if footnote_re.match(s): return True
    if star_re.match(raw): return True
    if is_note_header(s): return True
    if header_re.match(s) or s.endswith("时期"): return True
    if bare_date_re.match(s): return True
    if date_re.match(s): return True
    return False
def title_block(d):
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

bounds = []
for d in idx:
    blk = title_block(d)
    if blk:
        bounds.append((d, blk[0][0]))

sus = [79, 87, 92, 147, 153, 238, 318, 326, 333, 336, 347, 353, 379, 387, 397, 408, 370, 372]
for si in sus:
    if si >= len(bounds): continue
    d, ts = bounds[si]
    be = bounds[si+1][1] if si+1 < len(bounds) else len(lines)
    out.append(f"=== doc [{si}] {docs[si]['title'][:30]} region L{d+1}-L{be-1} ===")
    cut = None
    for j in range(d+1, be):
        raw, s = lines[j], lines[j].strip()
        if not s: continue
        trig = footnote_re.match(s) or star_re.match(raw) or is_note_header(s)
        if trig and cut is None:
            cut = j
        marker = ">>CUT>>" if j == cut else ("  trig " if trig else "      ")
        out.append(f"{marker} {j:5d} {s[:60]!r}")
        if j == cut:
            break

with open(r"E:\502\debug_regions.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("ok", len(out))
