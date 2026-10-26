# -*- coding: utf-8 -*-
import json
import jieba
jieba.setLogLevel(60)
from qhchina import load_stopwords
from qhchina.analytics.topicmodels import LDAGibbsSampler

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

sampler = LDAGibbsSampler(n_topics=10, iterations=200, random_state=42, min_word_count=5)
sampler.fit(token_docs)
sampler.save(r"E:\502\lda_model")   # keep for reuse

print("=== Topic 7: top 20 words ===")
for w, p in sampler.get_topic_words(7, 20):
    print(f"  {w}  {p:.4f}")

print("=== Topic 7: top 12 documents ===")
for doc_id, p in sampler.get_top_documents(7, 12):
    title, year = kept[doc_id]
    print(f"  p={p:.3f}  {year}  {title}")
