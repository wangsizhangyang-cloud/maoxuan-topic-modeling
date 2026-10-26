# -*- coding: utf-8 -*-
"""Compute all analysis data and build the self-contained index.html site."""
import json
import jieba
jieba.setLogLevel(60)
from qhchina import load_stopwords
from qhchina.analytics.topicmodels import LDAGibbsSampler

with open(r"E:\502\docs.json", encoding="utf-8") as f:
    docs = json.load(f)
# 口語功能詞擴充停用詞：zh_sim 較精簡，未收錄這些高頻口語標記詞；
# 不剔除的話 LDA 無論幾個主題都會把「口語 vs 書面」的語域差異聚成一個主題。
EXTRA_STOP = set(("现在 同志 不要 一点 不能 不行 会议 事情 办法 不好 东西 过去 几个 "
                  "地方 可能 一样 时候 起来 出来 什么 怎么 这样 那么 问题").split())
stopwords = load_stopwords("zh_sim") | EXTRA_STOP

token_docs, kept_flags, kept_tokens = [], [], []
for d in docs:
    toks = [t for t in (tok.strip() for tok in jieba.lcut(d["body"]))
            if len(t) >= 2 and t not in stopwords]
    kept_flags.append(len(toks) >= 100)
    kept_tokens.append(len(toks))
    if len(toks) >= 100:
        token_docs.append(toks)

N_TOPICS = 10
sampler = LDAGibbsSampler(n_topics=N_TOPICS, iterations=200, random_state=42, min_word_count=5)
sampler.fit(token_docs)

kept_idx = [i for i, k in enumerate(kept_flags) if k]
theta_by_kept = {}
for n in range(len(token_docs)):
    pairs = sorted(sampler.get_document_topics(n), key=lambda x: x[0])
    theta_by_kept[kept_idx[n]] = [round(p, 4) for _, p in pairs]

topics = []
# 手動命名：對應目前這個 10 主題模型（random_state=42）。若改變主題數或語料，需重新核對。
TOPIC_NAMES = {
    0: ("群眾工作", "群眾工作與農村生產"),
    1: ("階級鬥爭", "階級鬥爭與思想批判"),
    2: ("哲學辯證", "哲學認識論與辯證法"),
    3: ("外交國際", "外交與國際關係"),
    4: ("軍事作戰", "軍事作戰方針"),
    5: ("戰略理論", "戰爭戰略理論"),
    6: ("國共抗戰", "國共關係與抗戰時局"),
    7: ("農業集體化", "農業合作化與社會主義改造"),
    8: ("文革運動", "文革運動與中央指示"),
    9: ("反帝革命", "反帝革命與新民主主義"),
}
for t in range(N_TOPICS):
    words = [[w, round(p, 4)] for w, p in sampler.get_topic_words(t, 10)]
    top_docs = []
    for doc_id, p in sampler.get_top_documents(t, 2):
        gi = kept_idx[doc_id]
        top_docs.append({"title": docs[gi]["title"], "year": docs[gi]["year"], "p": round(p, 4)})
    topics.append({"id": t, "name": TOPIC_NAMES[t][0], "name_long": TOPIC_NAMES[t][1],
                   "words": words, "top_docs": top_docs})

out_docs = []
for i, d in enumerate(docs):
    out_docs.append({"i": i, "title": d["title"], "year": d["year"], "tokens": kept_tokens[i],
                     "kept": kept_flags[i], "theta": theta_by_kept.get(i), "text": d["body"]})

# PCA projection of the document-topic matrix (2D) for the scatter plot
import numpy as np
T = np.array([theta_by_kept[i] for i in kept_idx], dtype=float)
Tc = T - T.mean(axis=0)
U, S, Vt = np.linalg.svd(Tc, full_matrices=False)
pc = U[:, :2] * S[:2]
pc_var = (S ** 2 / (S ** 2).sum())[:2] * 100
for n, gi in enumerate(kept_idx):
    out_docs[gi]["x"] = round(float(pc[n, 0]), 2)
    out_docs[gi]["y"] = round(float(pc[n, 1]), 2)

years = [d["year"] for d in docs]
year_counts = {}
for i, d in enumerate(docs):
    yc = year_counts.setdefault(d["year"], {"parsed": 0, "kept": 0})
    yc["parsed"] += 1
    if kept_flags[i]:
        yc["kept"] += 1

decades = sorted({y - y % 10 for y in years})
data = {
    "meta": {"parsed": len(docs), "kept": len(token_docs),
             "tokens": sum(kept_tokens[i] for i in kept_idx),
             "vocab": len(sampler.vocabulary), "n_topics": N_TOPICS,
             "pcVar": [round(float(pc_var[0]), 1), round(float(pc_var[1]), 1)]},
    "topics": topics,
    "docs": out_docs,
    "decades": decades,
    "yearRange": [min(years), max(years)],
    "yearCounts": {str(y): year_counts[y] for y in sorted(year_counts)},
}

# --- topic overview + decade averages for the console report ---
theta_mat = np.array([theta_by_kept[i] for i in kept_idx])
lines = [f"=== {N_TOPICS}-topic model overview ==="]
for t in range(N_TOPICS):
    ws = " ".join(w for w, _ in sampler.get_topic_words(t, 8))
    dom = int(np.sum(np.argmax(theta_mat, axis=1) == t))
    lines.append(f"T{t} (dominant in {dom} docs): {ws}")
lines.append("=== average topic proportion by decade ===")
lines.append("decade  n  " + "  ".join(f"T{t}" for t in range(N_TOPICS)))
years_kept = [docs[i]["year"] for i in kept_idx]
for dc in sorted({y - y % 10 for y in years_kept}):
    rows = theta_mat[np.array([y - y % 10 == dc for y in years_kept])]
    m = rows.mean(axis=0)
    lines.append(f"{dc}s  n={len(rows):<4d}" + "  " + "  ".join(f"{v:.3f}" for v in m))
rep = "\n".join(lines)
print(rep)
with open(r"E:\502\decade_report.txt", "w", encoding="utf-8") as f:
    f.write(rep + "\n")

with open(r"E:\502\site_template.html", encoding="utf-8") as f:
    html = f.read()
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = html.replace("__DATA__", payload)
with open(r"E:\502\index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"index.html written: {len(html)/1024:.0f} KB  "
      f"(parsed={data['meta']['parsed']}, kept={data['meta']['kept']}, "
      f"tokens={data['meta']['tokens']}, vocab={data['meta']['vocab']})")
