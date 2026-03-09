# NLP 方法比較報告

記錄所有用於從 `.feature` 測試步驟中提取 **動作（action）** 與 **目標（target）** 的 NLP 方法，
包含優缺點分析與實際輸出範例。

> 每種方法皆有獨立的 Python 檔案（詳見下表）。

---

## 總覽

| # | 方法 | 檔案 | 依賴套件 | 速度 | 典型信心值 |
|---|------|------|----------|-------|-----------|
| 1 | 規則式正規表示式 | `method1_regex.py` | 僅標準函式庫 | ★★★★★ | 0.80–0.90 |
| 2 | 關鍵字 + 模式啟發法 | `method2_keyword.py` | 僅標準函式庫 | ★★★★★ | 0.65–0.92 |
| 3 | NLTK 詞性標注 | `method3_nltk_pos.py` | NLTK | ★★★★☆ | 0.70–0.85 |
| 4 | NLTK 淺層句法分析 | `method4_nltk_chunk.py` | NLTK | ★★★☆☆ | 0.75–0.85 |
| 5 | spaCy 依存句法分析 | `method5_spacy_dep.py` | spaCy + 模型 | ★★☆☆☆ | 0.80–0.90 |
| 6 | 集成投票 | `method6_ensemble.py` | 以上全部 | ★★☆☆☆ | 0.80–0.95 |

---

## 方法一 — 規則式正規表示式

**檔案：** `method1_regex.py`

**說明：** 以空白字元分割步驟文字，將第一個詞與預定義的 `ACTION_VOCAB` 詞彙表比對。優先以引號內字串作為目標；若無引號，則取去除前置介詞後的名詞短語。

### 優點
- 零外部依賴，任何環境皆可運行。
- 結果確定且完全可解釋。
- 極快（每個步驟僅需微秒）。
- 對嚴格遵循 BDD 慣例的步驟準確率高。

### 缺點
- 不理解語法，將每個第一個詞視為潛在動詞。
- 無引號時目標提取準確率下降。
- 需要手動維護 `ACTION_VOCAB`。
- 無法處理複雜或嵌套子句。

### 輸出範例

| 步驟 | 動作 | 目標 | 信心值 |
|------|------|------|--------|
| Launch browser | `Launch` | browser | 0.8 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.9 |
| Verify that home page is visible successfully | `Verify` | home page | 0.8 |

---

## 方法二 — 關鍵字 + 模式啟發法

**檔案：** `method2_keyword.py`

**說明：** 套用一組有序的已編譯正規表示式，每條針對特定 BDD 慣用語（如 navigate to url、click on 'X'、verify 'X' is visible 等）設計。若無匹配則退回通用的「動詞 + 目標」模式。

### 優點
- 對已涵蓋的模式非常精準。
- 可區分動作類型（NAVIGATE、CLICK、VERIFY 等）。
- 無外部依賴。
- 模式易於稽核與擴充。

### 缺點
- 覆蓋範圍僅限手工撰寫的模式。
- 順序敏感：先匹配的模式會遮蔽後面的模式。
- 通用退回模式信心值較低。
- 不理解表面形式以外的句子結構。

### 輸出範例

| 步驟 | 動作 | 目標 | 信心值 |
|------|------|------|--------|
| Launch browser | `Launch` | browser | 0.9 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.9 |
| Verify that home page is visible successfully | `Verify` | home page | 0.9 |

---

## 方法三 — NLTK 詞性標注

**檔案：** `method3_nltk_pos.py`

**說明：** 使用 `nltk.word_tokenize` 進行斷詞，再以平均感知機標注器對每個詞進行詞性標注。第一個 `VB*` 標記為動作；其後連續的 `NN*`、`JJ`、`DT`、`CD` 詞序列收集為目標名詞短語。

### 優點
- 以語言學為基礎，不單純依賴表面詞序。
- 可處理形態變體（clicks、clicking、clicked）。
- 免費取得，下載容量小。
- 引號字串覆蓋機制提升引號目標的穩健性。

### 缺點
- 領域詞彙（如 "footer"、"arrow"）可能被錯誤標注。
- 簡單名詞短語啟發法對附加介詞短語或並列名詞短語處理不佳。
- 比純正規表示式慢。
- 首次執行需下載 NLTK 資料。

### 輸出範例

| 步驟 | 動作 | 目標 | 信心值 |
|------|------|------|--------|
| Navigate to url 'http://automationexercise.com' | `url` | http://automationexercise.com | 0.85 |
| Verify that home page is visible successfully | `Verify` | that home page | 0.7 |
| Scroll down to footer | `footer` | *(無)* | 0.7 |

---

## 方法四 — NLTK 淺層句法分析

**檔案：** `method4_nltk_chunk.py`

**說明：** 使用 `nltk.RegexpParser` 搭配手工設計的 CFG 文法，定義 VP（動詞短語）與 NP（名詞短語）。第一個 VP 區塊取得完整動作短語；其後第一個 NP 區塊取得目標。

### 優點
- 可捕捉多詞動作短語（如 "scroll down to"）。
- 文法規則透明且可調整。
- 比單一動詞提取產生更豐富的動作標籤。
- 無需 GPU 或大型模型。

### 缺點
- CFG 文法需針對各領域手動調整。
- 淺層分析無法處理長距離依存關係。
- 詞性標注不正確時效果下降。
- 比平面正規表示式更難除錯。

### 輸出範例

| 步驟 | 動作 | 目標 | 信心值 |
|------|------|------|--------|
| Navigate to url 'http://automationexercise.com' | `url` | http://automationexercise.com | 0.85 |
| Verify that home page is visible successfully | `Verify` | that home page | 0.75 |
| Scroll down to footer | `footer` | *(無)* | 0.4 |

---

## 方法五 — spaCy 依存句法分析

**檔案：** `method5_spacy_dep.py`

**說明：** 對每個步驟執行 spaCy 的 `en_core_web_sm` 神經網路管線。ROOT 詞（通常為主要動詞）為動作；直接受詞（`dobj`）或介詞受詞（`pobj`）為目標，透過 `left_edge`/`right_edge` 展開為完整名詞短語。

### 優點
- 語言學準確度最高，理解句法角色。
- 可處理含從屬子句的複雜句子。
- 完整名詞短語涵蓋限定詞與形容詞。
- 引號字串覆蓋機制維持 BDD 步驟的高精準度。

### 缺點
- 需要 spaCy 及 `en_core_web_sm` 模型（約 12 MB）。
- 最慢的方法（比正規表示式慢約 5–20 倍）。
- 神經模型對不尋常句型可能產生意外分析結果。
- 對 BDD 中常見的簡單祈使句而言過於複雜。

### 輸出範例

| 步驟 | 動作 | 目標 | 信心值 |
|------|------|------|--------|
| Launch browser | `browser` | *(無)* | 0.5 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.9 |
| Verify that home page is visible successfully | `is` | *(無)* | 0.5 |

---

## 方法六 — 集成投票

**檔案：** `method6_ensemble.py`

**說明：** 彙總方法一至五的預測結果，以信心加權投票決定最終答案。套用 BDD 祈使語氣先驗（ACTION_VOCAB 中第一個詞加 +2.0 權重），防止助動詞（is/are）獲勝。最終信心值 = 加權平均 + 0.05 共識加成（上限 1.0）。

### 優點
- 降低個別方法錯誤的影響。
- BDD 先驗規則防止助動詞被誤標為動作。
- 當部分選用套件不可用時仍可優雅降級。
- 整體精準度通常高於任何單一方法。

### 缺點
- 繼承所有子方法的共同盲點。
- 信心分數為啟發式，未經實驗校準。
- 延遲等於所有子方法的總和。
- 可能將正確的少數派預測「平均化」掉。

### 輸出範例

| 步驟 | 動作 | 目標 | 信心值 |
|------|------|------|--------|
| Launch browser | `Launch` | browser | 0.783 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.93 |
| Verify that home page is visible successfully | `Verify` | home page | 0.78 |

---

## 建議

- **無安裝環境**：以方法二（關鍵字啟發法）為主，方法一為備援，兩者皆無需外部依賴。
- **單一方法最佳精準度**：在 `en_core_web_sm` 模型可用時，使用方法五（spaCy）。
- **最高整體精準度**：使用方法六（集成投票），結合所有方法優勢。
- **擴充覆蓋範圍**：在 `method2_keyword.py` 新增模式、在 `nlp_common.py` 的 `ACTION_VOCAB` 新增動詞。

---

_本報告由 `test_case_reader.py` 自動生成_
