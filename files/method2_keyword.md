# 方法二：關鍵字 + 模式啟發法（Keyword + Pattern Heuristics）

**程式檔案：** `method2_keyword.py`
**輸出檔案：** `results_keyword.json`
**外部依賴：** 無（僅使用 Python 標準函式庫）

---

## 一句話說明

> 預先寫好一組「句型模板」，依序去比對每句步驟，第一個吻合的模板就決定動作和目標。

---

## 這個方法在做什麼？（白話版）

想像你在教一個實習生讀測試步驟。你給他一張小抄：

```
如果看到 "navigate to url '某某'"  → 動作=Navigate，目標=某某
如果看到 "click on '某某'"        → 動作=Click，目標=某某
如果看到 "verify ... '某某'"      → 動作=Verify，目標=某某
如果看到 "enter 某某 in ..."      → 動作=Enter，目標=某某
…（更多模板）
如果以上都不符合               → 取第一個詞當動作，其餘當目標
```

方法二就是把這張小抄寫成程式碼。每個模板就是一條正規表示式，程式從上到下依序嘗試，第一個匹配的就是答案。

---

## 核心技術解說

### 模式比對（Pattern Matching）

方法一只看「第一個詞」和「引號」，方法二則進一步分析**整句的結構**。

每個模板由三個部分組成：
1. **正規表示式（regex）**：描述句子的格式
2. **群組編號（group）**：指定哪一部分是目標
3. **是否多目標（multi_target）**：目標是否需要再分割

### 模板庫詳解

以下是程式中的 8 個模板（按優先順序排列）：

```
優先順序 1：navigate to url 'X'
─────────────────────────────────
正規表示式：^(navigate)\s+to\s+url\s+['"]([^'"]+)['"]
說明：     抓 navigate 和 URL 引號中的網址
範例：     Navigate to url 'http://example.com'
           → action=Navigate, target=http://example.com
```

```
優先順序 2：click [on] 'X'
─────────────────────────────────
正規表示式：^(click)\s+(?:on\s+)?['"]([^'"]+)['"]
說明：     click 後面可以有 on 也可以沒有，抓引號中的目標
範例：     Click on 'Submit Button'
           → action=Click, target=Submit Button
```

```
優先順序 3：verify [that|text|error...] 'X'
─────────────────────────────────
正規表示式：^(verify)\s+(?:that\s+|text\s+|error...)?['"]([^'"]+)['"]
說明：     verify 後可接多種修飾詞，抓引號中的文字
範例：     Verify text 'SUBSCRIPTION'
           → action=Verify, target=SUBSCRIPTION
```

```
優先順序 4：enter X in/into
─────────────────────────────────
正規表示式：^(enter)\s+(.+?)\s+(?:in|into)\s+
說明：     enter 和 in/into 之間的文字就是目標
範例：     Enter email address in input field
           → action=Enter, target=email address
```

```
優先順序 5-7：scroll / launch / upload
─────────────────────────────────
各自處理特定動詞，取動詞後面的所有文字為目標
```

```
優先順序 8：verify that X is/are
─────────────────────────────────
正規表示式：^(verify)\s+that\s+(.+?)\s+(?:is|are)\b
說明：     抓 that 和 is/are 之間的內容作為目標
範例：     Verify that home page is visible
           → action=Verify, target=home page
```

```
優先順序 9（退回模式）：VERB [prep] X
─────────────────────────────────
如果以上都不匹配，使用通用模式：
第一個詞 = 動作，剩下的 = 目標
信心值降為 0.65（命名模板是 0.90）
```

---

## 每個函式在做什麼？

### `_analyse_single(sub)` — 用模板庫比對單一子步驟

**輸入：** 一個不含 `and` 連接動作的簡單步驟

**處理流程：**

```
輸入："Click on 'Login'"

步驟 1：嘗試模板 1（navigate to url...）→ 不匹配 ✗
步驟 2：嘗試模板 2（click [on] 'X'）→ 匹配 ✓
        group(1) = "Click"    → action
        group(2) = "Login"    → raw target
        is_named = True       → confidence = 0.90

回傳：action="Click", targets=["Login"], confidence=0.90
```

**如果所有模板都不匹配：**

```
輸入："Swipe left on screen"

步驟 1~9：所有模板都不匹配
步驟 10：fallback
         tokens = ["Swipe", "left", "on", "screen"]
         action = "Swipe"（第一個詞）
         targets = extract_targets("left on screen")
         confidence = 0.30

回傳：action="Swipe", targets=["left on screen"], confidence=0.30
```

### `analyse(step)` — 處理完整步驟（含複合步驟）

與方法一相同的流程：
1. 先用 `split_compound_step()` 拆分複合步驟
2. 對每個子步驟呼叫 `_analyse_single()`
3. 合併所有結果

---

## 「順序敏感」是什麼意思？

模板的順序非常重要。例如：

```
步驟："Verify text 'SUBSCRIPTION'"

模板 3（verify ... 'X'） 會先匹配 → target = "SUBSCRIPTION" ✓
模板 8（verify that X is/are）   不會有機會嘗試
```

如果把模板 8 放到模板 3 前面：

```
模板 8（verify that X is/are） → 不匹配（沒有 "that"）
模板 3（verify ... 'X'）      → 匹配 ✓ → 結果正確
```

但在某些情況下，順序錯誤可能導致錯誤的匹配「遮蔽」正確的匹配。

---

## 與方法一的差異

| 比較項目 | 方法一（Regex） | 方法二（Keyword） |
|---------|----------------|------------------|
| 辨識策略 | 只看第一個詞 + 引號 | 看整句的結構模式 |
| 模板數量 | 0（無模板） | 9 個模板 |
| 新動詞處理 | 信心低但仍可提取 | 若無匹配模板則退回通用模式 |
| 信心值範圍 | 0.30–0.90 | 0.30–0.90 |
| 準確率 | 動作高，目標中等 | 動作高，目標中高 |

---

## 實際執行範例

| 步驟 | 匹配的模板 | 動作 | 目標 | 信心值 |
|------|-----------|------|------|--------|
| Launch browser | 模板 6（launch X） | Launch | browser | 0.90 |
| Navigate to url '...' | 模板 1（navigate to url） | Navigate | URL | 0.90 |
| Verify that home page is visible | 模板 8（verify that X is） | Verify | home page | 0.90 |
| Scroll down to footer | 模板 5（scroll X） | Scroll | down to footer | 0.90 |
| Enter email and click arrow | 拆分後各自匹配 | Enter / click | email / arrow | 0.90 |

---

## 這個方法的限制

### 會出錯的情況

1. **新句型**：遇到模板沒覆蓋的句型（如 `Drag element A to position B`），只能靠通用退回模式，信心值降低。

2. **相似但微妙不同的措辭**：`Click the button labeled 'Submit'` — 模板 2 需要 `click [on] 'X'`，但這裡是 `click the button labeled 'X'`，可能不會匹配。

3. **非英文步驟**：模板完全基於英文設計，中文或其他語言的步驟無法使用。

### 適合的場景

- 步驟遵循常見的 BDD 慣用語
- 動作詞有限且可預測
- 不需要安裝外部套件
