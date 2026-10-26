# -*- coding: utf-8 -*-
import json, logging

import jieba
jieba.setLogLevel(60)
from qhchina import load_stopwords
from qhchina.analytics.topicmodels import LDAGibbsSampler

with open(r"E:\502\docs.json", encoding="utf-8") as f:
    docs = json.load(f)

stopwords = load_stopwords("zh_sim")
print(f"loaded {len(stopwords)} stopwords")

# tokenize: keep tokens of 2+ chars that are not stopwords
token_docs, kept = [], []
for d in docs:
    toks = [t for t in (tok.strip() for tok in jieba.lcut(d["body"]))
            if len(t) >= 2 and t not in stopwords]
    if len(toks) >= 100:
        token_docs.append(toks)
        kept.append((d["title"], d["year"]))
print(f"docs parsed: {len(docs)}   docs with >=100 tokens: {len(token_docs)}")
print(f"total tokens: {sum(len(t) for t in token_docs)}")

sampler = LDAGibbsSampler(n_topics=10, iterations=200, random_state=42,
                          min_word_count=5, log_interval=20)
sampler.fit(token_docs)

out = []
for t in range(10):
    words = sampler.get_topic_words(t, 10)
    wstr = "  ".join(f"{w}({p:.4f})" for w, p in words)
    out.append(f"Topic {t}: {wstr}")
    for doc_id, p in sampler.get_top_documents(t, 2):
        title, year = kept[doc_id]
        out.append(f"    doc {doc_id}  p={p:.4f}  {year}  {title}")
report = "\n".join(out)
print(report)
with open(r"E:\502\lda_report.txt", "w", encoding="utf-8") as f:
    f.write(f"docs parsed: {len(docs)}, docs with >=100 tokens: {len(token_docs)}, "
            f"total tokens: {sum(len(t) for t in token_docs)}\n\n" + report)
