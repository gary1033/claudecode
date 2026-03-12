# NLP 方法比較報告

記錄所有用於從 `.feature` 測試步驟中提取 **動作（action）** 與 **目標（target）** 的 NLP 方法，
包含完整原理說明、演算法細節、優缺點分析與實際輸出範例。

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

## 共用基礎設施

所有方法共用 `nlp_common.py` 中的基礎元件：

### ACTION_VOCAB — 動詞詞彙表
```
launch, navigate, verify, click, enter, scroll, fill, select, check, submit,
wait, search, type, press, hover, drag, drop, upload, download, open, close,
refresh, filter, register, login, logout, add, delete, edit
```
作為動詞辨識的黃金基準，用於所有方法的候選動詞評估。

### split_compound_step() — 複合步驟分割
針對 `"Enter email and click arrow"` 這類複合步驟，使用 lookahead regex：
```
\s+and\s+(?=(?:ACTION_VOCAB_ALTERNATION)\b)
```
只在 `and` 後方緊接已知動作詞時分割，不影響 `"Enter name and email"`（因 `email` 不在 ACTION_VOCAB）。

### extract_targets() — 多目標分割
以逗號或 `and` 分割目標字串：
- `"name, email, subject"` → `["name", "email", "subject"]`
- `"name and email"` → `["name", "email"]`

---

## 方法一 — 規則式正規表示式

**檔案：** `method1_regex.py`
**輸出：** `results_regex.json`

### 原理與演算法

方法一採用**無語言學知識的字元串匹配**策略，依賴兩個假設：
1. BDD 步驟以祈使動詞開頭（`Click`, `Enter`, `Verify`…）
2. 目標優先出現在引號內，次選為介詞後的名詞短語

**執行流程：**
```
輸入步驟
    │
    ▼
split_compound_step()          ← 偵測複合動作並分割
    │
    ▼ (對每個子步驟)
tokens = step.split()
first  = tokens[0].lower()
    │
    ├─ first ∈ ACTION_VOCAB? → confidence = 0.80
    └─ 否                    → confidence = 0.30
    │
    ▼
quoted = re.findall(r"['\"]([^'\"]+)['\"]", sub)
    │
    ├─ 有引號 → targets = [quoted[0]]; confidence += 0.10
    └─ 無引號 → rest = tokens[1:]
                   │
                   ├─ 移除前置介詞（on/to/in/at/into/with/…）
                   ├─ 在 is/are/was/were 前截斷
                   └─ extract_targets(' '.join(rest))
    │
    ▼
回傳 ActionTarget(action, targets)
```

**信心值計算：**
- 動詞在 ACTION_VOCAB 中：+0.80 基礎
- 有引號目標：+0.10 加成（上限 1.0）
- 動詞不在詞彙表：0.30 基礎

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
**輸出：** `results_keyword.json`

### 原理與演算法

方法二採用**有序正規表示式模式庫**策略：預先為每類 BDD 慣用語設計專屬 regex，依序嘗試匹配。每條模式都明確定義要捕捉的語義角色（`group(1)` = 動作，`group(2)` = 目標）。

**模式庫（優先順序由高至低）：**
```python
navigate to url 'X'      →  action=navigate,  target=X        (conf=0.90)
click [on] 'X'           →  action=click,     target=X        (conf=0.90)
verify [that|text] 'X'   →  action=verify,    target=X        (conf=0.90)
enter X in/into          →  action=enter,     target=X        (conf=0.90)
scroll [down] [to] X     →  action=scroll,    target=X        (conf=0.90)
launch X                 →  action=launch,    target=X        (conf=0.90)
upload X                 →  action=upload,    target=X        (conf=0.90)
verify that X is/are     →  action=verify,    target=X        (conf=0.90)
VERB [prep] X            →  通用退回模式                      (conf=0.65)
```

**執行流程：**
```
輸入步驟
    │
    ▼
split_compound_step()
    │
    ▼ (對每個子步驟)
for pattern in _PATTERNS:          ← 依優先順序嘗試
    m = pattern.match(sub)
    if m:
        action  = m.group(1)
        raw_tgt = m.group(2)
        targets = extract_targets(raw_tgt) if multi_target else [raw_tgt]
        return action, targets, 0.90

→ 所有模式失敗 → fallback: tokens[0], tokens[1:], 0.30
```

**順序敏感性問題：**
例如 `verify 'X' is visible` 會先匹配 `verify ... 'X'` 模式，即使後面的 `verify that X is` 模式也能匹配；先匹配的模式「遮蔽」後者。因此模式順序即為優先權設計。

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

## 方法三 — NLTK 詞性標注（POS Tagging）

**檔案：** `method3_nltk_pos.py`
**輸出：** `results_nltk_pos.json`

### 原理與演算法

#### Penn Treebank 詞性標記集（POS Tagset）
NLTK 使用 Penn Treebank 標記集，關鍵標記如下：

| 標記 | 含義 | 範例 |
|------|------|------|
| `VB`  | 動詞原型 | click, enter, verify |
| `VBZ` | 動詞第三人稱單數 | clicks, enters |
| `VBG` | 動詞現在分詞 | clicking, entering |
| `VBD` | 動詞過去式 | clicked, entered |
| `NN`  | 普通名詞單數 | button, field |
| `NNP` | 專有名詞單數 | Google, Facebook |
| `NNS` | 普通名詞複數 | buttons, fields |
| `JJ`  | 形容詞 | visible, active |
| `DT`  | 冠詞 | the, a, an |
| `IN`  | 介詞 | to, in, on |

#### 平均感知機標注器（Averaged Perceptron Tagger）
NLTK 使用**平均感知機（Averaged Perceptron）**作為 POS 標注模型：
- 使用上下文特徵（前後詞、詞綴、大小寫）預測詞性
- 在 Wall Street Journal 語料庫上訓練，準確率約 97%（通用英文）
- 對 BDD 領域詞彙（`footer`、`arrow`、`carousel`）準確率較低

**執行流程：**
```
輸入步驟
    │
    ▼
split_compound_step()
    │
    ▼ (對每個子步驟)
tokens = nltk.word_tokenize(sub)           ← 斷詞（處理縮寫、標點）
tagged = nltk.pos_tag(tokens)              ← 詞性標注
    │
    ▼
找第一個 VB/VBZ/VBG/VBD/VBP/VBN 標記
    │
    ├─ 有引號 → target = quoted_string     ← 引號覆蓋機制
    └─ 無引號 → 收集動詞之後的 NN*/JJ/DT/CD 序列
               遇到 VB*/IN/CC 時停止
    │
    ▼
回傳 ActionTarget(action_token, targets)
```

**BDD 特有問題：**
`Verify 'X' is visible` 中，`Verify` 以大寫開頭，標注器可能誤標為 `NNP`（專有名詞），導致第一個 `VB*` 缺失，最終以 `is` 作為動詞。引號覆蓋機制可部分緩解此問題。

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

## 方法四 — NLTK 淺層句法分析（Shallow Chunking）

**檔案：** `method4_nltk_chunk.py`
**輸出：** `results_nltk_chunk.json`

### 原理與演算法

#### 淺層句法分析 vs 完整句法分析
- **完整句法分析（Full Parsing）**：建立完整的巢狀句法樹（需大量計算）
- **淺層分析（Shallow Parsing / Chunking）**：只識別「組塊（chunk）」的邊界，不建立完整樹結構
- 目標：識別 **VP（動詞短語）** 與 **NP（名詞短語）**，成本低、速度快

#### 上下文無關文法（CFG）規則
方法四使用手工設計的 CFG 文法，由 `nltk.RegexpParser` 解析：

```
VP: {<VB.*><RP|RB|IN>*}      # 動詞 + 可選副詞/介詞（如 scroll down to）
NP: {<DT>?<JJ>*<NN.*>+}      # 可選冠詞 + 可選形容詞 + 一或多個名詞
```

**執行流程：**
```
輸入步驟
    │
    ▼
POS 標注（同方法三）
    │
    ▼
RegexpParser(grammar).parse(tagged)    ← 建立 chunk 樹
    │
    ▼
遍歷樹節點：
    ├─ 第一個 VP chunk → 提取所有詞 → action 短語
    │    例：[scroll, down, to] → action="scroll down to"
    └─ 第一個 NP chunk（VP 之後）→ 提取所有名詞詞 → target
         例：[the, footer] → target="footer"
    │
    ├─ 有引號 → 引號字串覆蓋 target
    └─ 無引號 → 使用 NP chunk 結果
    │
    ▼
回傳 ActionTarget(action_phrase, targets)
```

**與方法三的差異：**
- 方法三只取第一個動詞 token 作為 action（單一詞）
- 方法四可捕捉**多詞動作短語**（`scroll down to`、`click on`）
- 方法四使用文法規則定義邊界，比啟發式序列收集更結構化

**CFG 的局限性：**
CFG 是上下文無關的，無法處理長距離依存（如主語-動詞一致性），也無法處理歧義消解（同一字串可有多種合法 parse 結果）。`RegexpParser` 使用貪婪匹配，由左至右取第一個符合的 chunk。

### 優點
- 可捕捉多詞動作短語（如 "scroll down to"）。
- 文法規則透明且可調整。
- 比單一動詞提取產生更豐富的動作標籤。
- 無需 GPU 或大型模型。

### 缺點
- CFG 文法需針對各領域手動調整。
- 淺層分析無法處理長距離依存關係。
- 詞性標注不正確時效果下降（與方法三相同弱點）。
- 比平面正規表示式更難除錯。

### 輸出範例

| 步驟 | 動作 | 目標 | 信心值 |
|------|------|------|--------|
| Navigate to url 'http://automationexercise.com' | `url` | http://automationexercise.com | 0.85 |
| Verify that home page is visible successfully | `Verify` | that home page | 0.75 |
| Scroll down to footer | `footer` | *(無)* | 0.4 |

---

## 方法五 — spaCy 依存句法分析（Dependency Parsing）

**檔案：** `method5_spacy_dep.py`
**輸出：** `results_spacy_dep.json`

### 原理與演算法

#### spaCy 神經網路管線（en_core_web_sm）
`en_core_web_sm` 是一個輕量型英文模型（約 12 MB），包含三個串聯元件：

```
文字輸入
    │
    ▼
Tokenizer（規則式）        ← 智慧斷詞（縮寫、連字符等）
    │
    ▼
Tagger（CNN + Embedding）  ← 詞性標注（準確率 ~97%）
    │
    ▼
Parser（Transition-based Dependency Parser）
    ← 採用弧轉移（arc-eager / arc-standard）演算法
    ← 訓練自 OntoNotes 5.0 語料庫
```

#### 依存句法關係（Dependency Relations）
| 關係標籤 | 含義 | 範例 |
|----------|------|------|
| `ROOT` | 句子的根節點（通常為主要動詞） | click, verify, enter |
| `dobj` | 直接受詞 | click **button**, enter **text** |
| `pobj` | 介詞受詞 | navigate to **page** |
| `nsubj` | 名義主語 | **page** is visible |
| `attr` | 屬性補語（繫動詞補語） | is **visible** |
| `prep` | 介詞短語修飾語 | scroll **down** |
| `advmod` | 副詞修飾語 | scroll **down** |

#### 名詞短語展開（left_edge / right_edge）
spaCy 的 token 物件具備 `.left_edge` 和 `.right_edge` 屬性，可快速取得以該 token 為頭部（head）的完整子樹邊界：
```python
# 若 target_token 是 "page"，且修飾語有 "home"
span = doc[target_token.left_edge.i : target_token.right_edge.i + 1]
# → "home page"  而非單獨的 "page"
```

**執行流程：**
```
輸入步驟
    │
    ▼
split_compound_step()
    │
    ▼ (對每個子步驟)
doc = nlp(sub)                   ← 執行完整 spaCy 管線
    │
    ▼
有引號？→ target = quoted_string  ← 引號覆蓋機制
    │
    ▼
找 ROOT token：
    ├─ ROOT.pos_ in VERB → action = ROOT.text
    └─ ROOT.pos_ 非 VERB → 搜尋依存子節點中的動詞
    │
    ▼
找目標 token（依優先順序）：
    1. ROOT 的 dobj（直接受詞）
    2. ROOT 的 prep → pobj（介詞受詞）
    3. ROOT 的任何名詞子節點
    │
    ▼
用 left_edge/right_edge 展開為完整名詞短語
    │
    ▼
回傳 ActionTarget(action, targets)
```

**BDD 特有問題：**
`Verify 'X' is visible` — spaCy 的 ROOT 是 `is`（繫動詞），因為它在句法上是連接 `Verify` 子句與 `visible` 的核心。此問題由引號覆蓋機制（target）和 Ensemble 的 BDD 先驗（action）共同解決。

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

## 方法六 — 集成投票（Ensemble Voting）

**檔案：** `method6_ensemble.py`
**輸出：** `results_ensemble.json`

### 原理與演算法

#### 集成學習（Ensemble Learning）概念
集成方法的核心思想：**多個弱/中等分類器的加權組合，通常優於任一單一分類器**。

本實作採用**信心加權投票（Confidence-Weighted Voting）**，而非簡單多數決：
- 信心值高的方法對最終答案貢獻更大
- 允許在部分方法不可用時優雅降級

#### 動作投票算法

```
對每個子步驟（pair index = idx）：

1. 收集所有方法的預測：
   action_votes = Counter()
   for r in [m1, m2, m3, m4, m5]:
       if r.pairs[idx].action:
           action_votes[action.lower()] += r.confidence

2. BDD 祈使語氣先驗（Imperative Prior）：
   first_tok = sub_steps[idx].split()[0].lower()
   if first_tok in ACTION_VOCAB:
       action_votes[first_tok] += 2.0   ← 強先驗：第一詞是已知動詞
   for key in action_votes:
       if key ≠ first_tok and key in ACTION_VOCAB:
           action_votes[key] += 0.30    ← 弱先驗：其他已知動詞

3. 選出得票最高者 → best_action
```

**為什麼需要 BDD 先驗？**
若無先驗，`is` 在多個方法中都可能獲得票數（spaCy 選 ROOT=`is`，NLTK 標注 `is` 為 VBZ），導致 `is` 票數超過真正的動詞。+2.0 先驗確保句首的已知動詞詞彙在票數上佔優。

數學示例：
```
步驟: "Verify 'X' is visible"
方法預測: m1=Verify(0.9), m2=Verify(0.9), m3=Verify(0.7), m4=Verify(0.75), m5=is(0.5)

無先驗投票:
  verify: 0.9+0.9+0.7+0.75 = 3.25
  is:     0.5

BDD 先驗後（first_tok="verify" ∈ ACTION_VOCAB）:
  verify: 3.25 + 2.0 = 5.25  ← 勝出
  is:     0.5
```

#### 目標投票算法

```
target_votes = Counter()
for r in all_results:
    for t in r.pairs[idx].targets:
        target_votes[t.lower()] += r.confidence

# 多數決：決定應輸出幾個目標
count_votes = Counter(len(r.pairs[idx].targets) for r in all_results)
expected_n = count_votes.most_common(1)[0][0]

# 取票數最高的 expected_n 個目標
top_targets = sorted(target_votes.items(), key=score, reverse=True)[:expected_n]
```

#### 信心值計算

```
avg_conf = mean(r.confidence for r in all_results)   ← 所有方法的平均
final_conf = min(avg_conf + 0.05, 1.0)               ← +0.05 共識加成
```

共識加成（0.05）反映：多方法一致時，整體可信度高於單一方法平均。

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

## 方法比較與準確率總結

| 方法 | 動作準確率 | 配對準確率 | 優勢場景 |
|------|-----------|-----------|----------|
| M1 規則式正規表示式 | 高 | 中 | 有引號的簡單 BDD 步驟 |
| M2 關鍵字啟發法 | 高 | 中高 | 有標準 BDD 動詞的步驟 |
| M3 NLTK POS 標注 | 低 | 低 | 形態豐富語言（英文通用文本）|
| M4 NLTK 淺層分析 | 低 | 低 | 多詞動作短語（`scroll down to`）|
| M5 spaCy 依存分析 | 中 | 中 | 複雜句型、從屬子句 |
| M6 集成投票 | 高 | 中高 | 最佳整體精準度 |

> M3/M4 在 BDD 領域準確率偏低，主因是 NLTK 模型訓練於通用英文語料（WSJ），而非 BDD 測試步驟的祈使句式。

---

## 建議

- **無安裝環境**：以方法二（關鍵字啟發法）為主，方法一為備援，兩者皆無需外部依賴。
- **單一方法最佳精準度**：在 `en_core_web_sm` 模型可用時，使用方法五（spaCy）。
- **最高整體精準度**：使用方法六（集成投票），結合所有方法優勢。
- **擴充覆蓋範圍**：在 `method2_keyword.py` 新增模式、在 `nlp_common.py` 的 `ACTION_VOCAB` 新增動詞。
- **改善 M3/M4**：可考慮在 BDD 步驟語料上 fine-tune NLTK 模型，或加入 BDD 先驗詞性覆蓋機制。

---

## 參考文獻

### 工具與函式庫

| 編號 | 引用 |
|------|------|
| [1] | Loper, E., & Bird, S. (2002). **NLTK: The Natural Language Toolkit**. *Proceedings of the ACL-02 Workshop on Effective Tools and Methodologies for Teaching Natural Language Processing and Computational Linguistics*, 63–70. https://doi.org/10.3115/1118108.1118117 |
| [2] | Bird, S., Klein, E., & Loper, E. (2009). **Natural Language Processing with Python**. O'Reilly Media. ISBN 978-0-596-51649-9. https://www.nltk.org/book/ |
| [3] | Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). **spaCy: Industrial-strength Natural Language Processing in Python**. Zenodo. https://doi.org/10.5281/zenodo.1212303 |

---

### 詞性標注（POS Tagging）

| 編號 | 引用 |
|------|------|
| [4] | Marcus, M. P., Santorini, B., & Marcinkiewicz, M. A. (1993). **Building a Large Annotated Corpus of English: The Penn Treebank**. *Computational Linguistics*, 19(2), 313–330. https://aclanthology.org/J93-2004 |
| [5] | Ratnaparkhi, A. (1996). **A Maximum Entropy Model for Part-of-Speech Tagging**. *Proceedings of EMNLP 1996*, 133–142. https://aclanthology.org/W96-0213 |
| [6] | Toutanova, K., Klein, D., Manning, C. D., & Singer, Y. (2003). **Feature-Rich Part-of-Speech Tagging with a Cyclic Dependency Network**. *Proceedings of NAACL-HLT 2003*, 173–180. https://doi.org/10.3115/1073445.1073478 |
| [7] | Collins, M. (2002). **Discriminative Training Methods for Hidden Markov Models: Theory and Experiments with Perceptron Algorithms**. *Proceedings of EMNLP 2002*, 1–8. https://aclanthology.org/W02-1001 *(NLTK Averaged Perceptron Tagger 的理論基礎)* |

---

### 淺層句法分析（Shallow Parsing / Chunking）

| 編號 | 引用 |
|------|------|
| [8] | Abney, S. P. (1991). **Parsing by Chunks**. In Berwick, R., Abney, S., & Tenny, C. (Eds.), *Principle-Based Parsing: Computation and Psycholinguistics* (pp. 257–278). Kluwer Academic Publishers. https://doi.org/10.1007/978-94-011-3474-3_10 *(Chunking 概念的奠基論文)* |
| [9] | Ramshaw, L. A., & Marcus, M. P. (1995). **Text Chunking Using Transformation-Based Learning**. *Proceedings of the Third ACL Workshop on Very Large Corpora*, 82–94. https://aclanthology.org/W95-0107 |
| [10] | Tjong Kim Sang, E. F., & Buchholz, S. (2000). **Introduction to the CoNLL-2000 Shared Task: Chunking**. *Proceedings of CoNLL-2000 and LLL-2000*, 127–132. https://aclanthology.org/W00-0726 |

---

### 依存句法分析（Dependency Parsing）

| 編號 | 引用 |
|------|------|
| [11] | Nivre, J. (2003). **An Efficient Algorithm for Projective Dependency Parsing**. *Proceedings of IWPT 2003*, 149–160. https://aclanthology.org/W03-3017 *(Arc-standard 轉移演算法)* |
| [12] | Nivre, J. (2008). **Algorithms for Deterministic Incremental Dependency Parsing**. *Computational Linguistics*, 34(4), 513–553. https://doi.org/10.1162/coli.07-056-R2-07-027 |
| [13] | Nivre, J., et al. (2016). **Universal Dependencies v1: A Multilingual Treebank Collection**. *Proceedings of LREC 2016*, 1659–1666. https://aclanthology.org/L16-1262 *(spaCy 使用的依存關係標籤體系)* |
| [14] | Honnibal, M., & Johnson, M. (2015). **An Improved Non-monotonic Transition System for Dependency Parsing**. *Proceedings of EMNLP 2015*, 1373–1378. https://doi.org/10.18653/v1/D15-1162 *(spaCy 依存解析器的核心演算法)* |

---

### 集成學習（Ensemble Learning）

| 編號 | 引用 |
|------|------|
| [15] | Dietterich, T. G. (2000). **Ensemble Methods in Machine Learning**. *Proceedings of the 1st International Workshop on Multiple Classifier Systems (MCS 2000)*, Lecture Notes in Computer Science, Vol. 1857, 1–15. https://doi.org/10.1007/3-540-45014-9_1 |
| [16] | Breiman, L. (1996). **Bagging Predictors**. *Machine Learning*, 24(2), 123–140. https://doi.org/10.1007/BF00058655 |
| [17] | Polikar, R. (2006). **Ensemble Based Systems in Decision Making**. *IEEE Circuits and Systems Magazine*, 6(3), 21–45. https://doi.org/10.1109/MCAS.2006.1688199 |

---

### BDD 與自動化測試 NLP

| 編號 | 引用 |
|------|------|
| [18] | Solis, C., & Wang, X. (2011). **A Study of the Characteristics of Behaviour Driven Development**. *Proceedings of SEAA 2011*, 383–387. https://doi.org/10.1109/SEAA.2011.76 |
| [19] | Soeken, M., Wille, R., & Drechsler, R. (2012). **Assisted Behavior Driven Development Using Natural Language Processing**. *Proceedings of TOOLS 2012*, Lecture Notes in Computer Science, Vol. 7304, 269–287. https://doi.org/10.1007/978-3-642-30561-0_19 |
| [20] | Srikaew, A., Tangworakitthaworn, P., Seekhao, N., & Namahoot, C. S. (2019). **Automated Acceptance Test Cases Generation from Behavior-Driven Development (BDD) Using NLP**. *Proceedings of ICCAS 2019*, 1278–1282. https://doi.org/10.23919/ICCAS47443.2019.8971573 |

---

### 資訊抽取（Information Extraction）通論

| 編號 | 引用 |
|------|------|
| [21] | Jurafsky, D., & Martin, J. H. (2024). **Speech and Language Processing** (3rd ed. draft). Stanford University. https://web.stanford.edu/~jurafsky/slp3/ *(第 8 章：Sequence Labeling for Parts of Speech and NER；第 15 章：Dependency Parsing)* |
| [22] | Manning, C. D., & Schütze, H. (1999). **Foundations of Statistical Natural Language Processing**. MIT Press. ISBN 978-0-262-13360-9. *(第 10 章：Markov Models；第 11 章：POS Tagging)* |

---

_本報告由 `test_case_reader.py` 自動生成，方法細節與參考文獻由人工補充_
