"""Bias analysis + dot plot from trained models."""
import os
import numpy as np
import matplotlib.pyplot as plt
from qhchina.analytics.vectors import calculate_bias
from qhchina import helpers

HERE = os.path.dirname(os.path.abspath(__file__))

ANCHORS = [("女人", "男人"), ("母亲", "父亲"), ("妻子", "丈夫"), ("女儿", "儿子"),
           ("姐姐", "哥哥"), ("妹妹", "弟弟"), ("太太", "老爷"), ("小姐", "少爷"),
           ("妇人", "汉子"), ("女子", "男子"), ("娘", "爹")]
TARGETS = ["读书", "做官", "赚钱", "生意", "打仗", "针线", "做饭", "哭", "美丽", "聪明",
           "勇敢", "温柔", "学校", "自由", "恋爱", "革命", "工作", "社会", "国家", "眼泪", "力气"]
PERIODS = ["late_qing", "republican"]

# Chinese font support
import matplotlib.font_manager as fm
cached = helpers.list_cached_fonts()
if cached:
    fm.fontManager.addfont(cached[0]["path"])
    cjk_name = cached[0]["font_name"]
    print("using cached font:", cjk_name)
    plt.rcParams["font.sans-serif"] = [cjk_name, "Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]
else:
    try:
        fonts = helpers.list_remote_fonts()
        zh = [f for f in fonts if any(k in f for k in ("CJK", "NotoSansSC", "SimHei", "WenQuanYi"))]
        if zh:
            helpers.load_font(zh[0])
        print("font in use:", helpers.get_current_font_name())
    except Exception as e:
        print("font setup fallback:", e)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

scores = {p: {} for p in PERIODS}
for period in PERIODS:
    for seed in (1, 2):
        from qhchina.analytics import Word2Vec
        model = Word2Vec.load(os.path.join(HERE, "models", f"{period}_seed{seed}.model"))
        needed = [w for f, m in ANCHORS for w in (f, m)] + TARGETS
        wv = {w: np.asarray(model.get_vector(w)) for w in needed if w in model.vocab}
        present_targets = [t for t in TARGETS if t in wv]
        missing_targets = [t for t in TARGETS if t not in wv]
        if missing_targets:
            print(f"[{period} seed{seed}] targets missing from vocab: {missing_targets}")
        usable = [(f, m) for f, m in ANCHORS if f in wv and m in wv]
        skipped = [(f, m) for f, m in ANCHORS if not (f in wv and m in wv)]
        if skipped:
            print(f"[{period} seed{seed}] skipped pairs (word missing): {skipped}")
        vecs = calculate_bias(usable, present_targets, wv)
        scores[period][seed] = {t: float(s) for t, s in zip(present_targets, vecs)}

# ---- Table ----
def fmt(x):
    return f"{x:+.3f}" if x is not None else "  n/a "

hdr = f"{'word':<6} {'LQ-s1':>8} {'LQ-s2':>8} {'RP-s1':>8} {'RP-s2':>8}  unstable"
print(hdr)
print("-" * len(hdr))
for t in TARGETS:
    vals = [scores[p].get(s, {}).get(t) for p in PERIODS for s in (1, 2)]
    unstable = ""
    for i, p in enumerate(PERIODS):
        a, b = vals[2 * i], vals[2 * i + 1]
        if a is not None and b is not None and (a > 0) != (b > 0):
            unstable += f" {p}"
    print(f"{t:<6} " + " ".join(fmt(v) for v in vals) + f"  {unstable}")

# ---- Dot plot (seed averages, sorted by republican score) ----
def avg(t, p):
    xs = [scores[p][s][t] for s in (1, 2) if t in scores[p][s]]
    return sum(xs) / len(xs) if xs else None

rows = sorted(TARGETS, key=lambda t: (avg(t, "republican") is None,
                                      avg(t, "republican") if avg(t, "republican") is not None else 0))
y = np.arange(len(rows))
fig, ax = plt.subplots(figsize=(7, 0.38 * len(rows) + 2))
styles = {"late_qing": ("tab:red", "o"), "republican": ("tab:blue", "s")}
for p, (color, marker) in styles.items():
    xs = [avg(t, p) for t in rows]
    xpos = [x if x is not None else np.nan for x in xs]
    ax.scatter(xpos, y, marker=marker, color=color, label=p, s=55, zorder=3, alpha=0.85)
ax.axvline(0, color="gray", lw=0.8, ls="--", zorder=1)
ax.set_yticks(y)
ax.set_yticklabels(rows)
ax.invert_yaxis()
ax.set_xlabel("gender bias score  (positive = toward the male pole)")
ax.legend(loc="best")
ax.set_title("Gender bias of target words, by period (mean over 2 seeds)")
plt.tight_layout()
plt.savefig(os.path.join(HERE, "gender_bias.png"), dpi=150)
print("saved gender_bias.png")
