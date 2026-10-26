import inspect
from qhchina.analytics.topicmodels import LDAGibbsSampler
print("=== LDAGibbsSampler public methods ===")
for name, fn in inspect.getmembers(LDAGibbsSampler, predicate=inspect.isfunction):
    if not name.startswith("_"):
        try:
            print(f"{name}{inspect.signature(fn)}")
        except Exception:
            print(name)
from qhchina import load_stopwords
sw = load_stopwords("zh_sim")
print("=== stopwords zh_sim ===")
print(type(sw), len(sw))
print(list(sorted(sw))[:10])
