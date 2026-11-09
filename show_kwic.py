import os, pickle, random
import pandas as pd
from qhchina.analytics import kwic

HERE = os.path.dirname(os.path.abspath(__file__))
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 60)

with open(os.path.join(HERE, "data", "tokens.pkl"), "rb") as fh:
    tokens = pickle.load(fh)

for period in ("late_qing", "republican"):
    sents = tokens[period]
    for target in ("恋爱", "国家"):
        df = kwic(sents, target=target, horizon=15, separator="")
        n = len(df)
        sample = df.sample(n=min(10, n), random_state=0)
        print(f"\n===== {period} · {target}  ({n:,} total hits, 10 random shown) =====")
        disp = sample[["left", "node", "right"]].copy()
        disp.index = range(1, len(disp) + 1)
        print(disp.to_string())
