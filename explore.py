import re, io, sys

with open(r"E:\502\maoxuan.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()

print("total lines:", len(lines))
print("=== first 30 lines ===")
for i, l in enumerate(lines[:30]):
    print(i, repr(l))

# date lines like （一九二五年十二月一日）
date_re = re.compile(r"^\s*（[〇○○零一二三四五六七八九]+年.*）\s*$")
idx = [i for i, l in enumerate(lines) if date_re.match(l)]
print("=== date-line count:", len(idx))
print("first 5 date lines:", [lines[i] for i in idx[:5]])
print("last 3 date lines:", [lines[i] for i in idx[-3:]])

# any line containing 年 inside （） but not matching (to catch date variants)
weird = [lines[i] for i, l in enumerate(lines) if not date_re.match(l) and re.search(r"（[^（）]*年[^（）]*）", l)]
print("=== non-matching lines containing （...年...）:", len(weird))
for w in weird[:15]:
    print(repr(w))

# footnote-style lines
fl = [l for l in lines if l.lstrip().startswith("〔")]
print("=== lines starting with 〔:", len(fl))
for l in fl[:5]:
    print(repr(l[:60]))

# asterisk-footnote lines
al = [l for l in lines if l.lstrip().startswith("*") or l.lstrip().startswith("＊")]
print("=== lines starting with * :", len(al))
for l in al[:5]:
    print(repr(l[:60]))

# inline markers
import itertools
cnt = sum(len(re.findall(r"〔\d+〕", l)) for l in lines)
print("=== inline 〔n〕 occurrences:", cnt)

# look at context around the first two date lines
for d in idx[:2]:
    print(f"=== context around line {d} ===")
    for i in range(max(0, d-6), min(len(lines), d+6)):
        print(i, repr(lines[i][:60]))
