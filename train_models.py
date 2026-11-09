"""Train Word2Vec models (seed 1 & 2) for each period and save to models/."""
import os, pickle
from qhchina.analytics import Word2Vec

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "data", "tokens.pkl"), "rb") as fh:
    tokens = pickle.load(fh)

os.makedirs(os.path.join(HERE, "models"), exist_ok=True)

for period, sents in tokens.items():
    for seed in (1, 2):
        out = os.path.join(HERE, "models", f"{period}_seed{seed}.model")
        if os.path.exists(out):
            print("skip existing", out); continue
        print(f"training {period} seed={seed}, {len(sents)} sentences...", flush=True)
        model = Word2Vec(sentences=sents, vector_size=100, window=5, min_word_count=10,
                         sg=1, negative=5, epochs=3, workers=4, seed=seed)
        model.build_vocab(sents)
        model.train(epochs=3)
        model.save(out)
        print("saved", out, flush=True)
print("done")
