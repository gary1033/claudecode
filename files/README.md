# files/ 目錄說明

本目錄存放所有與「從測試步驟自動萃取 action/target」相關的分析文件與程式。

---

## 文件索引

### NLP 方法說明（六種演算法）

| 檔案 | 對應程式 | 說明 |
|------|----------|------|
| [method1_regex.md](method1_regex.md) | `method1_regex.py` | 規則式正規表示式：用預設動詞列表搭配 regex pattern 拆解步驟，無外部依賴 |
| [method2_keyword.md](method2_keyword.md) | `method2_keyword.py` | 關鍵字 + 模式啟發法：以關鍵字表驅動，針對引號、介系詞等結構做啟發式切割 |
| [method3_nltk_pos.md](method3_nltk_pos.md) | `method3_nltk_pos.py` | NLTK 詞性標注（POS Tagging）：標記每個詞的詞性，取第一個動詞為 action、其後名詞片語為 target |
| [method4_nltk_chunk.md](method4_nltk_chunk.md) | `method4_nltk_chunk.py` | NLTK 淺層句法分析（Chunking）：在 POS 之上定義名詞片語 chunk 規則，進一步分組 target |
| [method5_spacy_dep.md](method5_spacy_dep.md) | `method5_spacy_dep.py` | spaCy 依存句法分析（Dependency Parsing）：分析詞與詞的句法依存關係，精準找出動詞的受詞 |
| [method6_ensemble.md](method6_ensemble.md) | `method6_ensemble.py` | 集成投票（Ensemble Voting）：彙整以上各方法的結果，以多數決或加權投票取最終輸出 |

---

### 比較與評估報告

| 檔案 | 說明 |
|------|------|
| [nlp_methods_comparison.md](nlp_methods_comparison.md) | 六種方法的完整橫向比較：原理、演算法細節、優缺點、實際輸出範例 |
| [nlp_accuracy_report.md](nlp_accuracy_report.md) | 對照 `ground_truth.json` 的準確率報告，包含 action 準確率與 pair 準確率數字 |
| [nlp_results_table.md](nlp_results_table.md) | 逐步驟輸出對照表：每個測試步驟在六種方法下的 action/target 輸出與正確性標記 |

---

### 延伸分析

| 檔案 | 說明 |
|------|------|
| [generalizability_analysis.md](generalizability_analysis.md) | 泛化能力分析：評估六種方法在面對不同格式或不同領域的自然語言腳本時，準確率預期下降的原因與風險點 |
| [element_matching_strategies.md](element_matching_strategies.md) | 元素比對策略：說明如何將萃取出的 action/target 對應到真實網頁的 DOM 元素，涵蓋精確比對、屬性比對、模糊比對、語意嵌入等四段 fallback 流程，並提供 Selenium 與 Playwright 實作範例 |

---

## 目錄其他檔案

| 檔案 | 說明 |
|------|------|
| `method1_regex.py` ~ `method6_ensemble.py` | 各方法的 Python 實作 |
| `nlp_common.py` | 各方法共用的工具函式（載入 feature 檔、格式化輸出等） |
| `test_case_reader.py` | 讀取 `.feature` 檔並解析測試步驟的基礎模組 |
| `results_*.json` | 各方法對所有測試案例的原始輸出結果 |
| `nlp_analysis_results.json` | 彙整六種方法結果的統整 JSON |
| `ground_truth.json` | 人工標注的正確 action/target 對照表，作為準確率評估基準 |
| `index.html` | 結果的網頁視覺化呈現 |
| `step_01.svg` | 演算法流程示意圖 |
