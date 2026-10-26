import qhchina, jieba
print("qhchina", qhchina.__version__ if hasattr(qhchina, "__version__") else "n/a")
print("jieba", jieba.__version__)
print("--- qhchina top-level ---")
print([n for n in dir(qhchina) if not n.startswith("_")])
try:
    from qhchina.analytics import topicmodels
    print("--- topicmodels ---")
    print([n for n in dir(topicmodels) if not n.startswith("_")])
    import inspect
    print(inspect.signature(topicmodels.LDAGibbsSampler.__init__))
except Exception as e:
    print("topicmodels err:", e)
for mod in ["helpers", "preprocessing", "analytics", "stopwords"]:
    try:
        m = __import__(f"qhchina.{mod}", fromlist=["*"])
        print(f"--- {mod} ---")
        print([n for n in dir(m) if not n.startswith("_")])
    except Exception as e:
        print(mod, "err:", e)
