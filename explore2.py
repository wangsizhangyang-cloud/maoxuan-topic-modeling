import re, sys

with open(r"E:\502\maoxuan.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()

date_re = re.compile(r"^\s*（[〇○○零一二三四五六七八九]+年.*）\s*$")
idx = [i for i, l in enumerate(lines) if date_re.match(l)]

print("=== date lines with preceding non-empty line (first 30) ===")
for k, d in enumerate(idx[:30]):
    prev = next((lines[j].strip() for j in range(d-1, -1, -1) if lines[j].strip()), "?")
    print(f"[{k}] line {d}: title={prev!r} date={lines[d].strip()!r}")

print("=== gaps between consecutive date lines < 30 lines (possible double dates) ===")
for a, b in zip(idx, idx[1:]):
    if b - a < 30:
        print(f"lines {a} -> {b} (gap {b-a}):")
        for i in range(a, b+1):
            print("   ", i, repr(lines[i][:70]))

print("=== lines containing 原注 ===")
on = [(i, lines[i]) for i, l in enumerate(lines) if "原注" in l]
print("count:", len(on))
for i, l in on[:10]:
    print(i, repr(l[:50]))

print("=== zero variants in date lines ===")
for ch in "〇○○零":
    n = sum(1 for d in idx if ch in lines[d])
    print(ch, n)

print("=== transitions: lines between end of one doc and next title (scan for headers) ===")
# print everything between the footnote block of doc k and title of doc k+1 for first 2 transitions
# find footnote end: last 〔 line before next date line
for k in range(0, 2):
    d_next = idx[k+1]
    # scan backwards from d_next to find title, then scan back further to find structure
    t = d_next - 1
    while t >= 0 and not lines[t].strip():
        t -= 1
    # walk back until blank gap of >=2 after footnote lines
    print(f"--- doc {k+1}: title line {t}: {lines[t]!r}")
    j = t - 1
    shown = 0
    while j >= 0 and shown < 14:
        if lines[j].strip():
            print("   ", j, repr(lines[j][:70]))
            shown += 1
        j -= 1

print("=== check: titles that are very long or start with 〔 ===")
bad = 0
for k, d in enumerate(idx):
    prev = next((lines[j].strip() for j in range(d-1, -1, -1) if lines[j].strip()), "?")
    if len(prev) > 30 or prev.startswith("〔"):
        bad += 1
        print(f"[{k}] line {d}: title={prev[:60]!r} date={lines[d].strip()[:30]!r}")
print("bad titles:", bad)
