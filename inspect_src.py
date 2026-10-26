import inspect
from qhchina.analytics import topicmodels as tm
src = inspect.getsource(tm.LDAGibbsSampler)
# print only the signatures + docstrings of key methods and the preprocess/fit logic
import re
for name in ["fit", "preprocess", "get_top_documents", "get_topic_words", "__init__"]:
    m = re.search(rf"def {name}\(.*?(?=\n    def |\nclass )", src, re.S)
    if m:
        text = m.group(0)
        print("="*30, name)
        print(text[:2200])
        print()
