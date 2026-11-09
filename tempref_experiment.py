# -*- coding: utf-8 -*-
import pickle
import random
import numpy as np
from qhchina.analytics import TempRefWord2Vec

TARGETS = ["革命", "自由", "社会", "经济", "文明", "国家", "同志", "小姐",
           "先生", "学生", "政治", "科学", "银行", "火车", "朋友", "母亲",
           "皇帝", "百姓", "眼睛", "吃饭", "山", "马"]
P1, P2 = "late_qing", "republican"

with open(r"E:\502\data\tokens.pkl", "rb") as f:
    tokens = pickle.load(f)
print({k: len(v) for k, v in tokens.items()})

def train(sentences, seed):
    model = TempRefWord2Vec(
        sentences=sentences,
        targets=TARGETS,
        vector_size=100, window=5, min_word_count=10,
        sg=1, negative=5, epochs=3, workers=4, seed=seed,
    )
    model.train()
    return model

def changes(model, labels):
    out = {}
    for w in TARGETS:
        v1, v2 = f"{w}_{labels[0]}", f"{w}_{labels[1]}"
        try:
            a, b = model.get_vector(v1), model.get_vector(v2)
        except KeyError:
            continue
        out[w] = 1 - float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return out

def fmt(w):
    return w.encode("unicode_escape").decode()[:10]

# (a) and (b): real periods
print("Training run (a)...")
model_a = train({P1: tokens[P1], P2: tokens[P2]}, seed=1)
print("Training run (b)...")
model_b = train({P1: tokens[P1], P2: tokens[P2]}, seed=2)

# (c): shuffled control
print("Training run (c)...")
pool = tokens[P1] + tokens[P2]
random.seed(0)
random.shuffle(pool)
half = len(pool) // 2
model_c = train({"A": pool[:half], "B": pool[half:]}, seed=1)

ch_a = changes(model_a, (P1, P2))
ch_b = changes(model_b, (P1, P2))
ch_c = changes(model_c, ("A", "B"))

print("\n=== Semantic change by run (sorted by change in run a) ===")
header = f"{'word':<8}{'change_a':>10}{'change_b':>10}{'change_c':>10}"
print(header)
for w in sorted(ch_a, key=ch_a.get, reverse=True):
    b = ch_b.get(w, float("nan"))
    c = ch_c.get(w, float("nan"))
    print(f"{w:<8}{ch_a[w]:>10.4f}{b:>10.4f}{c:>10.4f}")

noise_ceiling = max(ch_c.values())
print(f"\nNoise ceiling (largest change in shuffled control c): {noise_ceiling:.4f}")

# Deep dive on top 5 from (a)
top5 = sorted(ch_a, key=ch_a.get, reverse=True)[:5]
for w in top5:
    print("\n" + "=" * 70)
    print(f"WORD: {w}   change(a)={ch_a[w]:.4f}  change(b)={ch_b.get(w, float('nan')):.4f}  change(c)={ch_c.get(w, float('nan')):.4f}")
    for label in (P1, P2):
        print(f"  most_similar('{w}_{label}', topn=10):")
        for t, s in model_a.most_similar(f"{w}_{label}", topn=10):
            print(f"    {t:<10}{s:.4f}")
    res = model_a.calculate_semantic_change(w)
    for transition, lst in res.items():
        towards = lst[:8]
        away = sorted(lst, key=lambda x: x[1])[:8]
        print(f"  {transition} — moved TOWARDS (top 8):")
        for t, s in towards:
            print(f"    {t:<10}{s:+.4f}")
        print(f"  {transition} — moved AWAY (bottom 8):")
        for t, s in away:
            print(f"    {t:<10}{s:+.4f}")
