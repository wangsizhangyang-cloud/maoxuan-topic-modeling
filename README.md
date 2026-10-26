# 毛澤東選集主題建模（Topic Modeling on the Selected Works of Mao Zedong）

以主題模型（LDA Gibbs）分析《毛澤東選集》語料，並附一個自包含的互動視覺化網站。

- 語料：[`mcjkurz/qhchina-data`](https://github.com/mcjkurz/qhchina-data) · `corpora/選集/毛澤東選集.txt`（`maoxuan.txt`）
- 工具：Python 3.14 · `qhchina` 0.2.7 · `jieba` 0.42.1

## 管線

1. **解析**（`parse_docs.py`）：切分出 409 篇文檔（標題＋年份，支援多行標題、多部分文檔、各種「〇」寫法）；去除腳注（`注　　釋` 區塊、`〔n〕` 行內標記）。
2. **分詞**：jieba（≥2 字）→ `qhchina.load_stopwords("zh_sim")` ＋口語功能詞擴充（見 `build_site.py` 的 `EXTRA_STOP`，用於避免「口語 vs 書面」語域聚成一個主題）→ 保留 ≥100 詞的文檔（356 篇）。
3. **主題模型**：`qhchina.analytics.topicmodels.LDAGibbsSampler`（10 主題，iterations=200，random_state=42，min_word_count=5），主題已人工命名（見 `build_site.py` 的 `TOPIC_NAMES`）。
4. **視覺化**：`build_site.py` 重新訓練並生成 `index.html`（自包含、離線可用）。

## 網站 `index.html`

- 各年代平均主題構成（堆疊柱狀圖，圖例可開關主題）
- 文檔年代分佈、整體主題分佈
- 主題關鍵詞卡片（點標題看主題詳情：年代分佈＋全部文檔按 θ 排序）
- 文檔主題散點圖（θ 經 PCA 降至二維；點擊圓點可閱讀原文全文）
- 全部 409 篇文檔可搜尋表格（點任一行讀原文）

## 檔案

| 檔案 | 說明 |
|---|---|
| `maoxuan.txt` | 原始語料（5.6 MB） |
| `docs.json` | 解析後的 409 篇文檔（標題、年份、去腳注正文） |
| `index.html` | 互動網站（自包含） |
| `site_template.html` | 網站模板（資料由 `build_site.py` 注入） |
| `parse_docs.py` / `build_site.py` / `run_lda.py` / `plot_decades.py` | 各階段腳本 |
| `lda_report.txt` / `decade_report.txt` / `parse_report.txt` | 分析報告 |
| `topics_by_decade.png` | 年代×主題堆疊圖（matplotlib 版） |
| `lda_model.npy` | 已訓練的模型快照 |

## 復現

```bash
pip install qhchina jieba
python build_site.py   # 重新訓練並重建 index.html（random_state=42，結果可復現）
```
