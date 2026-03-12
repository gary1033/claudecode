# 方法五：spaCy 依存句法分析（Dependency Parsing）

**程式檔案：** `method5_spacy_dep.py`
**輸出檔案：** `results_spacy_dep.json`
**外部依賴：** `spacy` + `en_core_web_sm` 模型（約 12 MB）

---

## 一句話說明

> 用神經網路分析句子中每個詞與其他詞的「依存關係」（誰修飾誰、誰是誰的受詞），從而找出動作和目標。

---

## 這個方法在做什麼？（白話版）

前面的方法都是用「規則」或「分組」來理解句子。方法五則是用**真正的 AI 模型**來分析句子結構。

想像一個句子是一棵家族樹：

```
          Click（根節點/族長）
          /        \
        on          button（直接受詞）
                   /
                 the
```

- `Click` 是整棵樹的根（ROOT）→ 主要動作
- `button` 是 `Click` 的直接受詞（dobj）→ 目標
- `the` 和 `on` 是修飾語

方法五就是讓 AI 模型畫出這棵樹，然後從樹上找到「根 = 動作」和「受詞 = 目標」。

---

## 核心技術解說

### 什麼是依存句法分析（Dependency Parsing）？

每個句子可以用一棵「依存樹」來表示詞與詞之間的語法關係。

```
句子：Enter email address in the input field

依存樹：
  Enter ──── ROOT（根節點：整句的主要動詞）
    │
    ├── address ──── dobj（直接受詞：動作的對象）
    │     │
    │     └── email ──── compound（複合名詞修飾語）
    │
    └── in ──── prep（介詞）
          │
          └── field ──── pobj（介詞受詞）
                │
                ├── the ──── det（冠詞）
                └── input ──── compound（複合名詞修飾語）
```

#### 依存關係標籤解釋

| 標籤 | 全名 | 白話解釋 | 範例 |
|------|------|---------|------|
| **ROOT** | Root | 句子的「核心」，通常是主要動詞 | Click, Enter, Verify |
| **dobj** | Direct object | 動作的直接對象（「做什麼」的「什麼」） | click **button** |
| **pobj** | Prepositional object | 介詞後面的對象 | navigate to **page** |
| **prep** | Preposition | 介詞（連接動詞和受詞） | scroll **to** footer |
| **det** | Determiner | 冠詞 | **the** button |
| **compound** | Compound | 複合名詞的前半部 | **email** address |
| **nsubj** | Nominal subject | 名義主語 | **page** is visible |
| **attr** | Attribute | 繫動詞的補語 | is **visible** |
| **advmod** | Adverbial modifier | 副詞修飾語 | scroll **down** |
| **conj** | Conjunct | 連接詞連接的並列成分 | name **and** email |

### spaCy 的 en_core_web_sm 模型

spaCy 使用一個預訓練的**神經網路模型**來分析句子。

```
文字輸入："Click the submit button"
    │
    ▼
┌──────────────────────────────────────┐
│ Tokenizer（斷詞器）                    │
│ 規則式，不是 AI                        │
│ → ["Click", "the", "submit", "button"]│
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Tagger（詞性標注器）                    │
│ CNN 神經網路 + 詞向量嵌入              │
│ → [VB, DT, JJ, NN]                   │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Parser（依存分析器）                    │
│ Transition-based 神經網路              │
│ 使用「弧轉移」演算法                    │
│ → ROOT(Click) → det(the)             │
│                → dobj(button)         │
│                    → amod(submit)     │
└──────────────────────────────────────┘
```

#### 什麼是「弧轉移」（Transition-based）演算法？

白話解釋：想像你有一疊撲克牌（句子中的詞），一張一張翻開。每翻一張，你要做一個決定：

1. **SHIFT**：把這個詞放到「等待區」
2. **LEFT-ARC**：等待區頂端的詞是當前詞的「下屬」→ 畫箭頭
3. **RIGHT-ARC**：當前詞是等待區頂端的詞的「下屬」→ 畫箭頭

神經網路的工作就是**學會在每一步做出正確的決定**。它在大量已標注的句子上訓練（OntoNotes 5.0 語料庫，約 200 萬詞），學會了英文的語法結構。

### 名詞短語展開（left_edge / right_edge）

找到目標詞後，我們想要完整的名詞短語，而不只是單一個詞。

spaCy 提供了 `left_edge` 和 `right_edge` 屬性：

```python
# token = "button"（dobj）
# button 的修飾語有 "the" 和 "submit"

span = doc[token.left_edge.i : token.right_edge.i + 1]
# left_edge = "the"（最左邊的下屬）
# right_edge = "button"（最右邊的下屬就是自己）
# → span = "the submit button"
```

這樣我們就能自動取得完整的名詞短語，而不需要手寫規則。

---

## 每個函式在做什麼？

### `_analyse_single(sub)` — 用依存分析處理單一子步驟

**完整流程範例：**

```
輸入："Navigate to url 'http://example.com'"

步驟 1：執行 spaCy 管線
        doc = NLP_MODEL("Navigate to url 'http://example.com'")

步驟 2：找引號中的文字
        quoted = ["http://example.com"]  → 有引號！

步驟 3：找 ROOT
        掃描所有 token，找 dep_ == "ROOT"
        → root = "Navigate"（ROOT）

步驟 4：因為有引號，直接用引號內容作為目標
        → targets = ["http://example.com"]
        → confidence = 0.90

回傳：action="Navigate", targets=["http://example.com"], confidence=0.90
```

**沒有引號時的流程：**

```
輸入："Click the submit button"

步驟 1：doc = NLP_MODEL("Click the submit button")

步驟 2：沒有引號

步驟 3：找 ROOT → "Click"

步驟 4：找 ROOT 的 dobj（直接受詞）
        root.children 中找 dep_ == "dobj"
        → 找到 "button"

步驟 5：展開為完整名詞短語
        left_edge = "the"，right_edge = "button"
        → span = "the submit button"
        → targets = ["the submit button"]

步驟 6：找 conjuncts（並列受詞）
        button.conjuncts → 沒有
        → 最終 targets = ["the submit button"]
        → confidence = 0.80

回傳：action="Click", targets=["the submit button"], confidence=0.80
```

**找 pobj（介詞受詞）的流程：**

```
輸入："Scroll down to footer"

步驟 3：ROOT = "Scroll"
步驟 4：找 dobj → 沒有
步驟 5：找 prep → "to"
        → to 的 children 中找 pobj → "footer"
        → targets = ["footer"]
        → confidence = 0.80
```

### `analyse(step)` — 處理完整步驟

同樣的框架：先拆複合步驟，再逐一分析。

---

## 為什麼 spaCy 在 BDD 步驟上有時會出錯？

### 問題：ROOT 不一定是你想要的動詞

```
步驟："Verify 'X' is visible"

spaCy 的分析：
  is ──── ROOT          ← spaCy 認為 "is" 是句子核心！
  │
  ├── Verify ──── csubj（子句主語）
  │     │
  │     └── X ──── dobj
  │
  └── visible ──── attr（屬性補語）
```

**為什麼？** 在英文語法中，`Verify that X is visible` 的主要動詞確實可以被解讀為 `is`（「X 是可見的」這個事實），而 `Verify` 是對這個事實的操作。spaCy 的神經網路從新聞語料中學到的就是這種分析方式。

但在 BDD 測試中，我們真正想要的動作是 `Verify`。這個問題由方法六（Ensemble）的 BDD 先驗來修正。

### 問題：沒有受詞的情況

```
步驟："Launch browser"

spaCy 的分析：
  browser ──── ROOT     ← "browser" 是 ROOT？！
  │
  └── Launch ──── compound

或：
  Launch ──── ROOT
  │
  └── browser ──── dobj   ← 正確分析

（取決於模型版本和上下文）
```

spaCy 有時會把 `browser` 當作 ROOT（名詞為核心），導致 action = "browser"（錯誤）。

---

## 信心值怎麼算？

| 情況 | 信心值 |
|------|--------|
| 有 ROOT + 有引號目標 | 0.90 |
| 有 ROOT + 有 dobj/pobj 目標 | 0.80 |
| 有 ROOT 但沒找到目標 | 0.50 |
| 沒有 ROOT 或 spaCy 不可用 | 0.00 |

---

## 與其他方法的比較

| 比較項目 | 方法一~二 | 方法三~四 | 方法五 |
|---------|----------|----------|--------|
| 分析深度 | 表面文字 | 詞性 + 分組 | 完整句法結構 |
| 理解「誰修飾誰」 | 不能 | 部分（相鄰性） | 完整（依存關係）|
| 處理複雜句 | 差 | 中 | 好 |
| 速度 | 微秒 | 毫秒 | 5~20 毫秒 |
| 安裝成本 | 無 | NLTK（小） | spaCy + 模型（12 MB） |
| BDD 準確率 | 高 | 低 | 中（ROOT 問題） |

---

## 這個方法適合什麼場景？

- 步驟格式多樣、不遵循固定模板
- 需要處理複雜句型（從屬子句、並列結構）
- 可以接受安裝 spaCy 和下載模型的成本
- 與 Ensemble 結合使用效果最佳
