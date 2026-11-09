"""Build data/tokens.pkl: jieba-tokenized sentences from late_qing and republican corpora."""
import faulthandler, os, pickle, random, re
faulthandler.enable()
import jieba

BASE = os.path.join(os.environ["TEMP"], "qhc")
SRC = {"late_qing": "corpora/epochs_normalized/late_qing",
       "republican": "corpora/epochs_normalized/republican"}
SPLIT_RE = re.compile(r"[。！？\n\r]+")
TOKEN_LIMIT = 12_000_000


def is_punct(tok: str) -> bool:
    stripped = tok.strip()
    if not stripped:
        return True
    for ch in stripped:
        cat_start = ord(ch)
        # treat as non-punct if CJK or alnum
        if '\u4e00' <= ch <= '\u9fff':
            return False
        if ch.isalnum():
            return False
    return True


def main():
    random.seed(0)
    result = {}
    for period, rel in SRC.items():
        src_dir = os.path.join(BASE, rel)
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", period)
        files = sorted(os.listdir(src_dir))
        files = [f for f in files if f.endswith(".txt")]
        order = list(range(len(files)))
        random.shuffle(order)

        sentences = []
        total_chars = 0
        print(f"== {period}: {len(files)} files", flush=True)
        for idx in order:
            if total_chars >= TOKEN_LIMIT:
                break
            path = os.path.join(src_dir, files[idx])
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            total_chars += len(text)
            # copy raw file to data/<period>/ as requested
            os.makedirs(out_dir, exist_ok=True)
            dest = os.path.join(out_dir, files[idx])
            if not os.path.exists(dest):
                import shutil
                shutil.copyfile(path, dest)
            for sent in SPLIT_RE.split(text):
                sent = sent.strip()
                if not sent:
                    continue
                toks = [t for t in jieba.lcut(sent) if not is_punct(t)]
                if toks:
                    sentences.append(toks)
        n_tokens = sum(len(s) for s in sentences)
        print(f"== {period} done", flush=True)
        result[period] = sentences
        print(f"{period}: files used={len([i for i in order])}/{len(files)} chars~{total_chars:,} "
              f"sentences={len(sentences):,} tokens={n_tokens:,}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tokens.pkl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as fh:
        pickle.dump(result, fh, protocol=pickle.HIGHEST_PROTOCOL)
    print("saved:", out_path)


if __name__ == "__main__":
    main()
