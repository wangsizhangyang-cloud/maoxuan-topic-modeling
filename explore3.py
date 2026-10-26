import re

with open(r"E:\502\maoxuan.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()

date_re = re.compile(r"^\s*（[〇○○零一二三四五六七八九]+年.*）\s*$")
idx = [i for i, l in enumerate(lines) if date_re.match(l)]

def title_block(d):
    """Walk back from date line d, collecting title lines."""
    block = []
    j = d - 1
    gap = 0
    while j >= 0:
        s = lines[j].strip()
        if not s:
            gap += 1
            if block and gap >= 2:
                break
            if not block and gap >= 2:
                # leading blanks before any title line; keep scanning a bit
                pass
            j -= 1
            continue
        # stop conditions
        if s.startswith("〔") or s.lstrip("　").startswith("*") or s.lstrip("　").startswith("＊"):
            break
        if re.match(r"^　*注　+释\s*$", lines[j]) or s == "注释":
            break
        if len(s) > 35:
            break
        if re.match(r"^第.+[卷篇]$", s) or s.endswith("时期") or s == "毛泽东选集":
            break
        if re.match(r"^（[〇○○零一二三四五六七八九]+年.*）$", s):
            break
        block.append((j, s))
        gap = 0
        j -= 1
    block.reverse()
    return block

out = []
out.append("=== ALL date lines with title-block candidates ===")
for k, d in enumerate(idx):
    b = title_block(d)
    titles = " / ".join(s for _, s in b)
    # classify
    if not b:
        cls = "NOBLOCK"
    else:
        # nearest non-blank above block
        j = b[0][0] - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        p = lines[j].strip() if j >= 0 else "BOF"
        if date_re.match(lines[j]) if j >= 0 else False:
            cls = "AFTER-DATE(internal?)"
        else:
            cls = f"prev={p[:25]!r}"
    out.append(f"[{k:3d}] L{d:5d} {cls:35s} | {titles[:60]} | {lines[d].strip()[:26]}")

out.append("=== region dumps ===")
def dump(a, b, label):
    out.append(f"--- {label} lines {a}-{b} ---")
    for i in range(a, min(b, len(lines))):
        s = lines[i]
        if s.strip():
            out.append(f"{i:5d} {s[:78]}")
        else:
            out.append(f"{i:5d} ·")

for a, b, lab in [(13735, 13940, "long-title cluster"), (22440, 22560, "nine-commentaries group"),
                  (22690, 22740, "two-section doc"), (25715, 25800, "1967-01 group"),
                  (31340, 31420, "1975 group")]:
    dump(a, b, lab)

out.append("=== counts ===")
out.append(f"date lines: {len(idx)}")
out.append(f"'注　　释' headers: {sum(1 for l in lines if re.match(r'^　*注　+释\\s*$', l))}")
nd = [l for l in lines if l.lstrip().startswith('〔') and not re.match(r'^〔\d+〕', l.lstrip())]
out.append(f"lines starting with 〔 but not 〔digit: {len(nd)}")
for l in nd[:10]:
    out.append("   " + repr(l[:50]))
star = [l for l in lines if re.match(r'^[\u3000 ]*[＊*]', l)]
out.append(f"*-note lines: {len(star)}")

with open(r"E:\502\ctx.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("written", len(out), "lines")
