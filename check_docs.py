# -*- coding: utf-8 -*-
import json
with open(r"E:\502\docs.json", encoding="utf-8") as f:
    docs = json.load(f)

for i in [33, 65, 87, 139, 153, 154, 172, 404, 405]:
    d = docs[i]
    body = d["body"]
    last = [l for l in body.split("\n") if l.strip()][-1] if body.strip() else "(EMPTY)"
    print(f"[{i}] {d['year']} {d['title']}")
    print(f"     chars={len(body)}  last body line: ...{last[-60:]}")
print()
print("=== 愚公移山 body check (parable present?) ===")
print("has 愚公移山寓言:", "中国古代有个寓言" in docs[87]["body"])
print("has ending:", "就是全中国的人民大众" in docs[87]["body"])
print("no note text:", "这是毛泽东在中国共产党第七次全国代表大会上的闭幕词" not in docs[87]["body"])
