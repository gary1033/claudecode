# 方法三：NLTK 詞性標注（POS Tagging）

**程式檔案：** `method3_nltk_pos.py`
**輸出檔案：** `results_nltk_pos.json`
**外部依賴：** `nltk`（Natural Language Toolkit）

---

## 一句話說明

> 讓電腦先判斷每個詞是「動詞」「名詞」還是「介詞」，然後用「第一個動詞 = 動作、後面的名詞 = 目標」的邏輯來提取。

---

## 這個方法在做什麼？（白話版）

你在學校學英文時，老師教過：句子裡有**動詞**（做什麼）、**名詞**（對象是誰）、**形容詞**（什麼樣的）。

方法三就是先讓電腦「標注」每個詞的詞性，再根據詞性來找動作和目標。

例如：

```
Click    on     the     Submit    button
動詞(VB) 介詞(IN) 冠詞(DT) 名詞(NNP) 名詞(NN)
```

電腦看到：第一個動詞是 `Click` → 動作。後面的名詞是 `Submit button` → 目標。

---

## 核心技術解說

### 什麼是詞性標注（POS Tagging）？

POS = Part of Speech（詞性）

就像每個詞都戴了一頂「帽子」，告訴你它在句子裡扮演什麼角色：

| 詞性標記 | 全名 | 白話解釋 | 範例 |
|---------|------|---------|------|
| **VB** | Verb, base form | 動詞原型（做什麼） | click, enter, verify |
| **VBZ** | Verb, 3rd person singular | 動詞第三人稱 | clicks, enters |
| **VBG** | Verb, gerund | 動詞進行式 | clicking, entering |
| **VBD** | Verb, past tense | 動詞過去式 | clicked, entered |
| **NN** | Noun, singular | 名詞單數（東西） | button, field, page |
| **NNP** | Proper noun | 專有名詞（名字） | Google, Submit |
| **NNS** | Noun, plural | 名詞複數 | buttons, fields |
| **JJ** | Adjective | 形容詞（形容東西） | visible, active, red |
| **DT** | Determiner | 冠詞（the/a/an） | the, a, an |
| **IN** | Preposition | 介詞（位置關係） | to, in, on, at |
| **CC** | Coordinating conjunction | 連接詞 | and, or, but |
| **CD** | Cardinal number | 數字 | 1, 2, 100 |

這套標記系統叫做 **Penn Treebank Tagset**，由美國賓州大學（UPenn）在 1993 年定義，是英文 NLP 的業界標準。

### NLTK 怎麼判斷詞性？— 平均感知機（Averaged Perceptron）

NLTK 的詞性標注器使用一種叫「平均感知機」的機器學習演算法。

**白話解釋：**

想像你要教一個小朋友分辨「動詞」和「名詞」。你給他看很多例子：

```
老師：「run」在「I run fast」裡是動詞
老師：「run」在「a morning run」裡是名詞
老師：「click」在「Click the button」裡是動詞
```

小朋友會慢慢學會一些規則：
- 句子開頭的詞常常是動詞（在命令句中）
- 「the」後面的詞通常是名詞
- 以 `-ing` 結尾的可能是動詞進行式
- 以 `-tion` 結尾的通常是名詞

平均感知機就是這樣「從大量例子中學規則」的演算法。它看過的訓練資料來自 **Wall Street Journal（華爾街日報）** 的文章，約 100 萬個詞。

**但這裡有個問題：** 華爾街日報寫的是新聞文章，不是測試步驟。所以有些測試用語可能被標錯。

### 為什麼 BDD 步驟容易標錯？

BDD 測試步驟有個特色：**以大寫動詞開頭的祈使句**。

```
Verify that home page is visible
```

- `Verify` 大寫開頭 → 標注器可能以為是專有名詞（NNP）而非動詞（VB）
- 因為在新聞文章中，句子開頭大寫的通常是人名或地名

這是方法三在 BDD 領域準確率偏低的主要原因。

---

## 每個函式在做什麼？

### `_analyse_single(sub)` — 用詞性標注分析單一子步驟

**完整流程範例：**

```
輸入："Verify that home page is visible successfully"

步驟 1：斷詞（Tokenization）
        nltk.word_tokenize() 把句子切成詞列表
        → ["Verify", "that", "home", "page", "is", "visible", "successfully"]

步驟 2：詞性標注（POS Tagging）
        nltk.pos_tag() 給每個詞標上詞性
        → [("Verify", "VB"),       ← 動詞 ✓（但有時被標為 NNP）
           ("that",   "IN"),       ← 介詞
           ("home",   "NN"),       ← 名詞
           ("page",   "NN"),       ← 名詞
           ("is",     "VBZ"),      ← 動詞
           ("visible","JJ"),       ← 形容詞
           ("successfully","RB")]  ← 副詞

步驟 3：掃描 — 找第一個動詞
        found_verb = False
        掃到 ("Verify", "VB") → 是 VB* → action = "Verify"
        found_verb = True

步驟 4：繼續掃描 — 收集名詞短語
        ("that", "IN") → 介詞，在 NP 中 → 加入 np_words（保持連續性）
        ("home", "NN") → 名詞 → 加入 np_words
        ("page", "NN") → 名詞 → 加入 np_words
        ("is", "VBZ")  → 遇到新的動詞 → 不在 _NP_TAGS 中
                          in_np 為 True → break，停止收集

        np_words = ["that", "home", "page"]

步驟 5：檢查引號
        沒有引號 → targets = extract_targets("that home page")
        → targets = ["that home page"]
        → confidence = 0.70（有動詞但無引號）

回傳：action="Verify", targets=["that home page"], confidence=0.70
```

**注意：** 目標中多了 `that`，這是因為 `IN`（介詞）被包含在收集邏輯中。這是方法三不夠精準的一個例子。

### `_NP_TAGS` — 定義哪些詞性算「名詞短語的一部分」

```python
_NP_TAGS = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'DT', 'CD'}
```

白話翻譯：名詞（單/複數/專有）、形容詞、冠詞、數字 — 這些都可以組成一個「名詞短語」。

例如 `the red Submit button` → DT + JJ + NNP + NN → 都在 `_NP_TAGS` 中 → 整體作為一個目標。

### `analyse(step)` — 處理完整步驟

與方法一相同的框架：
1. `split_compound_step()` 拆分複合步驟
2. 對每個子步驟呼叫 `_analyse_single()`
3. 合併結果並計算平均信心值

---

## 信心值怎麼算？

| 情況 | 信心值 |
|------|--------|
| 找到動詞 + 有引號目標 | 0.85 |
| 找到動詞 + 無引號（用名詞短語） | 0.70 |
| 沒找到任何動詞 | 0.20 |

---

## 常見錯誤案例

### 錯誤 1：大寫動詞被標為名詞

```
步驟："Scroll down to footer"

實際標注：[("Scroll", "NNP"), ("down", "RB"), ("to", "TO"), ("footer", "NN")]
                         ↑
                    被標為專有名詞！

結果：找不到 VB* → action = ""（空）
      程式退回到低信心結果
```

### 錯誤 2：助動詞搶走動詞位置

```
步驟："Verify 'X' is visible"
如果 Verify 被標為 NNP，則第一個 VB* 是 "is"

結果：action = "is"（錯誤！應該是 Verify）
```

### 正確案例：引號覆蓋機制

```
步驟："Click on 'Submit'"

標注：[("Click", "VB"), ("on", "IN"), ("'", "''"), ("Submit", "NNP"), ("'", "''")]

結果：action = "Click"（第一個 VB）
      有引號 → target = "Submit"（覆蓋名詞短語結果）
      confidence = 0.85
```

---

## 與方法一、二的差異

| 比較項目 | 方法一 | 方法二 | 方法三 |
|---------|--------|--------|--------|
| 判斷依據 | 詞的位置 | 句型模板 | 詞性標注 |
| 理解語言 | 否 | 部分 | 是 |
| 處理 clicks/clicking | 只認 click | 只認 click | 認出 VBZ/VBG |
| 外部依賴 | 無 | 無 | NLTK |
| BDD 準確率 | 高 | 高 | 低（大寫問題） |
