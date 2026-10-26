# -*- coding: utf-8 -*-
import json

import jieba
jieba.setLogLevel(60)
from qhchina import load_stopwords
from qhchina.helpers import load_font
from qhchina.analytics.topicmodels import LDAGibbsSampler
import numpy as np
import matplotlib.pyplot as plt

# ---- rebuild corpus + model (same params/seed -> same result as before) ----
with open(r"E:\502\docs.json", encoding="utf-8") as f:
    docs = json.load(f)
stopwords = load_stopwords("zh_sim")

token_docs, kept = [], []
for d in docs:
    toks = [t for t in (tok.strip() for tok in jieba.lcut(d["body"]))
            if len(t) >= 2 and t not in stopwords]
    if len(toks) >= 100:
        token_docs.append(toks)
        kept.append((d["title"], d["year"]))

sampler = LDAGibbsSampler(n_topics=10, iterations=200, random_state=42,
                          min_word_count=5)
sampler.fit(token_docs)

n_docs, n_topics = len(token_docs), 10
theta = np.zeros((n_docs, n_topics))
for i in range(n_docs):
    for tid, p in sampler.get_document_topics(i):
        theta[i, tid] = p

top_words = ["  ".join(w for w, _ in sampler.get_topic_words(t, 3)) for t in range(n_topics)]

# ---- aggregate by decade ----
decades = sorted({(y // 10) * 10 for _, y in kept})
rows = {d: [] for d in decades}
for i, (title, year) in enumerate(kept):
    rows[(year // 10) * 10].append(theta[i])
avg = np.array([np.mean(rows[d], axis=0) for d in decades])   # [n_decades, n_topics]

rep = ["decade  n_docs  " + "  ".join(f"T{t}" for t in range(n_topics))]
for d, vec in zip(decades, avg):
    rep.append(f"{d}s  n={len(rows[d]):<4d}  " + "  ".join(f"{v:.3f}" for v in vec))
rep.append("top-3 words per topic: " + " | ".join(f"T{t}: {top_words[t]}" for t in range(n_topics)))
report = "\n".join(rep)
print(report)
with open(r"E:\502\decade_report.txt", "w", encoding="utf-8") as f:
    f.write(report + "\n")

# ---- plot ----
font_name = load_font()
print("font:", font_name)

fig, ax = plt.subplots(figsize=(11, 6.5))
colors = plt.cm.tab10.colors
bottom = np.zeros(len(decades))
for t in range(n_topics):
    vals = avg[:, t]
    ax.bar([f"{d}s" for d in decades], vals, bottom=bottom,
           color=colors[t], edgecolor="white", linewidth=0.6,
           label=f"Topic {t}: {top_words[t]}")
    bottom += vals

counts = [len(rows[d]) for d in decades]
ax.set_xticks(range(len(decades)))
ax.set_xticklabels([f"{d}s\n(n={c})" for d, c in zip(decades, counts)])
ax.set_xlabel("十年 (decade)")
ax.set_ylabel("平均主题占比 (average topic proportion)")
ax.set_title("《毛泽东选集》各年代平均主题构成（LDA Gibbs, 10 topics）", fontsize=13)
ax.set_ylim(0, 1.0)
ax.legend(title="主题 (top 3 词)", loc="upper left", bbox_to_anchor=(1.01, 1.0),
          fontsize=9, title_fontsize=10, framealpha=0.9)
fig.tight_layout()
fig.savefig(r"E:\502\topics_by_decade.png", dpi=150, bbox_inches="tight")
print("saved topics_by_decade.png")
