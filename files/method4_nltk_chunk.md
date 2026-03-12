# 方法四：NLTK 淺層句法分析（Shallow Chunking）

**程式檔案：** `method4_nltk_chunk.py`
**輸出檔案：** `results_nltk_chunk.json`
**外部依賴：** `nltk`（Natural Language Toolkit）

---

## 一句話說明

> 在方法三（詞性標注）的基礎上，進一步用「文法規則」把相鄰的詞組合成「動詞片語」和「名詞片語」，再從片語中提取動作和目標。

---

## 這個方法在做什麼？（白話版）

方法三只是標注每個詞的詞性，就像給每個積木貼標籤。方法四更進一步，把標好的積木**組裝成更大的結構**。

舉例來說：

```
方法三的結果：
  Scroll(VB) down(RB) to(TO) the(DT) footer(NN)
  ↑動詞     ↑副詞   ↑介詞  ↑冠詞   ↑名詞

方法四的結果：
  [Scroll down to] → 動詞片語（VP）= 動作
  [the footer]     → 名詞片語（NP）= 目標
```

方法三只會取 `Scroll` 一個詞當動作；方法四可以取 `Scroll down to` 整個動詞片語。

---

## 核心技術解說

### 什麼是淺層句法分析（Shallow Parsing / Chunking）？

**完整句法分析**像蓋一棟房子的完整藍圖，要分析每個元素之間的所有關係。

**淺層分析**只是找出「哪些詞組成一組」，像把積木分堆：
- 這堆是動詞組（VP）
- 那堆是名詞組（NP）
- 不管它們之間的複雜關係

```
完整分析（很複雜）：
    S
   / \
  VP   NP
  |   / \
  V  DT   N
  |  |    |
Click the button

淺層分析（只分組）：
 [Click]_VP  [the button]_NP
```

### 上下文無關文法（Context-Free Grammar / CFG）

方法四使用手工定義的「文法規則」來決定怎麼分組：

```python
VP: {<VB.*><RP|IN|TO>?<RB>?}
NP: {<DT>?<JJ.*>*<NN.*>+}
```

這兩行規則用白話翻譯就是：

#### VP（動詞片語）規則

```
VP = 動詞 + (可選的)介詞或小品詞 + (可選的)副詞

VB.*   = 任何動詞（VB, VBZ, VBG, VBD 等）
RP     = 小品詞（up, down, out 等）
IN     = 介詞（to, on, in 等）
TO     = to
RB     = 副詞（quickly, down 等）

?  = 可以有也可以沒有
```

**範例：**
| 文字 | 詞性序列 | 匹配 |
|------|---------|------|
| Click | VB | VP ✓ |
| Scroll down | VB + RB | VP ✓ |
| Navigate to | VB + TO | VP ✓ |
| Click on | VB + IN | VP ✓ |
| the button | DT + NN | VP ✗（不是動詞開頭）|

#### NP（名詞片語）規則

```
NP = (可選的)冠詞 + (零或多個)形容詞 + (一或多個)名詞

DT    = 冠詞（the, a, an）
JJ.*  = 任何形容詞（JJ, JJR, JJS）
NN.*  = 任何名詞（NN, NNS, NNP, NNPS）

?  = 0 或 1 個
*  = 0 或多個
+  = 1 或多個
```

**範例：**
| 文字 | 詞性序列 | 匹配 |
|------|---------|------|
| button | NN | NP ✓ |
| the button | DT + NN | NP ✓ |
| the red Submit button | DT + JJ + NNP + NN | NP ✓ |
| Click | VB | NP ✗（是動詞）|

### RegexpParser — 文法規則的執行器

`nltk.RegexpParser` 就像一個工人，拿著你寫的文法規則，從左到右掃描詞性序列，把符合規則的詞「圈起來」成為一個組塊（chunk）。

```
輸入：[("Scroll","VB"), ("down","RB"), ("to","TO"), ("the","DT"), ("footer","NN")]

第一輪（VP 規則）：
  VB + RB 符合 VP 規則 → 圈起來
  [VP: Scroll down] to(TO) [剩餘未處理]

  等等，TO 也符合 VP 的可選部分？
  → 看具體匹配：VB + RB 已匹配，TO 是可選的下一個 → 不包含（RB 後面沒有 TO 的規則）
  → 實際上 VP 規則是 VB + (RP|IN|TO)? + RB?
  → "Scroll"(VB) + ... RegexpParser 是貪婪匹配

第二輪（NP 規則）：
  DT + NN 符合 NP 規則 → 圈起來
  [NP: the footer]

結果：[VP: Scroll down] to(TO) [NP: the footer]
```

---

## 每個函式在做什麼？

### `_analyse_single(sub)` — 用文法規則分析單一子步驟

**完整流程範例：**

```
輸入："Click on the Submit button"

步驟 1：斷詞
        → ["Click", "on", "the", "Submit", "button"]

步驟 2：詞性標注
        → [("Click","VB"), ("on","IN"), ("the","DT"), ("Submit","NNP"), ("button","NN")]

步驟 3：使用 RegexpParser 建立 chunk 樹
        VP 規則匹配：VB + IN → [VP: Click on]
        NP 規則匹配：DT + NNP + NN → [NP: the Submit button]

        chunk 樹結構：
        (S
          (VP Click/VB on/IN)        ← 動詞片語
          (NP the/DT Submit/NNP button/NN))  ← 名詞片語

步驟 4：遍歷 chunk 樹
        遇到第一個 VP → action = "Click on"
        遇到第一個 NP（在 VP 之後）→ targets = ["the Submit button"]

步驟 5：檢查引號（本例沒有）
        → confidence = 0.75（有動作 + 有目標）

回傳：action="Click on", targets=["the Submit button"], confidence=0.75
```

**如果沒有形成 chunk 怎麼辦？**

```
輸入："Launch browser"

標注：[("Launch","VB"), ("browser","NN")]

VP 規則：VB 單獨也可以匹配 → [VP: Launch]
NP 規則：NN 單獨也可以匹配 → [NP: browser]

action = "Launch", targets = ["browser"]
```

**如果動詞沒被標對呢？**

```
輸入："Scroll down to footer"

可能的標注：[("Scroll","NNP"), ("down","RB"), ("to","TO"), ("footer","NN")]
                        ↑
                  被標為專有名詞！

VP 規則需要 VB 開頭 → 找不到 VP chunk
但程式有 fallback：掃描裸詞，找第一個 VB* → 也找不到

→ 檢查是否有非 chunk 的 VB* 標記 → 沒有
→ action = ""（空），targets 可能有 "footer"
→ confidence = 0.40（低）
```

### `analyse(step)` — 處理完整步驟

同樣的框架：拆分 → 逐一分析 → 合併。

---

## 與方法三的關鍵差異

| 比較項目 | 方法三（POS） | 方法四（Chunking） |
|---------|-------------|-------------------|
| 動作提取 | 只取一個動詞詞 | 取整個動詞片語 |
| 動作範例 | `Scroll` | `Scroll down to` |
| 目標提取 | 連續名詞序列 | 文法定義的 NP chunk |
| 分組依據 | 相鄰詞性相同 → 合併 | CFG 文法規則 → 組塊 |
| 除錯難度 | 容易 | 中等（需理解文法）|

---

## 信心值怎麼算？

| 情況 | 信心值 |
|------|--------|
| 有動作 + 有引號目標 | 0.85 |
| 有動作 + 有 NP chunk 目標 | 0.75 |
| 其他（缺動作或缺目標） | 0.40 |

---

## 常見錯誤案例

### 錯誤 1：與方法三相同的大寫問題

因為 Chunking 建立在 POS 標注之上，如果詞性標錯，chunk 結果也會錯。

```
"Verify that home page is visible"
如果 Verify → NNP → VP 規則不匹配
→ action 可能是空的或是 "is"
```

### 錯誤 2：多餘的介詞被包含在動作中

```
"Navigate to url 'http://example.com'"

VP 規則匹配：VB + TO → [VP: Navigate to]
→ action = "Navigate to"（多了 "to"）

有些場景這是對的（如 "scroll down to"），有些場景則是多餘的。
```

### 正確案例：多詞動作短語

```
"Scroll down to footer"

如果標注正確：VB + RB → [VP: Scroll down]
→ action = "Scroll down"（比方法三的 "Scroll" 更完整！）
```

---

## 這個方法適合什麼場景？

- 需要捕捉多詞動作（`scroll down`、`fill in`、`click on`）
- 想要透明、可調整的分組規則
- 不需要安裝大型模型（NLTK 很輕量）
- 願意為特定領域手動調整 CFG 文法
