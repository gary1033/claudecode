# 泛化能力分析：這些演算法用在其他自然語言腳本時會準確嗎？

本文分析六種 NLP 方法在面對**不同格式、不同領域的自然語言測試腳本**時，
準確率是否會大幅下降，以及每種方法最脆弱的環節在哪裡。

---

## 目前的測試腳本特徵

我們的 `.feature` 檔案具有以下特徵：

| 特徵 | 說明 |
|------|------|
| 語言 | 英文 |
| 句式 | 祈使句（動詞開頭：Click、Enter、Verify…） |
| 格式 | `序號. 步驟文字`，一行一步 |
| 目標標記 | 引號標注（`'Submit'`、`'http://...'`） |
| 動詞範圍 | 約 10 種常見動詞 |
| 步驟複雜度 | 簡單（1~2 個動作，目標明確） |

**關鍵假設：所有演算法都隱含地假設了這些特徵。** 當新腳本偏離這些特徵時，準確率就會下降。

---

## 會影響準確率的 5 大變化

### 變化 1：句式不同（非祈使句）

**我們的格式：**
```
Click the submit button
Verify that home page is visible
```

**可能遇到的其他格式：**
```
The user clicks the submit button        ← 第三人稱陳述句
Home page should be visible              ← 情態動詞句型
When the submit button is clicked        ← 被動語態
Given that the user is on the home page  ← Gherkin Given/When/Then
```

| 方法 | 影響程度 | 原因 |
|------|---------|------|
| M1 Regex | 🔴 嚴重 | 第一個詞不是動詞（`The`、`Home`、`When`、`Given`） |
| M2 Keyword | 🔴 嚴重 | 所有模板假設動詞開頭，無法匹配 |
| M3 NLTK POS | 🟡 中等 | 能找到句中的動詞（`clicks`→VBZ），但不一定是第一個 |
| M4 NLTK Chunk | 🟡 中等 | VP chunk 可以在句中出現，但需要調整取用邏輯 |
| M5 spaCy | 🟢 輕微 | ROOT 依然是主要動詞，不論位置 |
| M6 Ensemble | 🟡 中等 | BDD 先驗失效（第一個詞不在 ACTION_VOCAB），但投票仍可能正確 |

**預估準確率變化：**
- M1/M2：從 ~100% 降至 ~30%
- M5：可能維持 ~60-70%
- M6：從 ~100% 降至 ~60%

---

### 變化 2：沒有引號標記目標

**我們的格式：**
```
Click on 'Submit Button'
Navigate to url 'http://example.com'
```

**沒有引號的格式：**
```
Click on the Submit Button
Navigate to http://example.com
Verify that the error message is displayed
```

| 方法 | 影響程度 | 原因 |
|------|---------|------|
| M1 Regex | 🟡 中等 | 失去引號加成（-0.10），退回名詞短語提取（不太準） |
| M2 Keyword | 🟡 中等 | 多個模板依賴引號匹配，會落入通用退回模式 |
| M3 NLTK POS | 🟢 輕微 | 本身就不太依賴引號，用名詞短語序列提取 |
| M4 NLTK Chunk | 🟢 輕微 | NP chunk 不需要引號 |
| M5 spaCy | 🟢 輕微 | dobj/pobj 不需要引號 |
| M6 Ensemble | 🟢 輕微 | M3/M4/M5 在無引號時反而更穩定 |

**預估準確率變化：**
- 動作準確率：幾乎不變
- 目標準確率：M1/M2 下降約 15-20%，M5/M6 下降約 5%

---

### 變化 3：使用 Gherkin 語法（Given/When/Then）

**標準 Gherkin 格式：**
```gherkin
Feature: User Registration
  Scenario: Successful registration
    Given the user is on the registration page
    When the user enters "John" in the name field
    And clicks the "Submit" button
    Then the success message "Registration complete" should be displayed
```

| 方法 | 影響程度 | 原因 |
|------|---------|------|
| M1 Regex | 🔴 嚴重 | `Given`、`When`、`Then`、`And` 不在 ACTION_VOCAB |
| M2 Keyword | 🔴 嚴重 | 沒有匹配 Gherkin 的模板 |
| M3 NLTK POS | 🟡 中等 | 需要跳過 Given/When/Then 找真正的動詞 |
| M4 NLTK Chunk | 🟡 中等 | 同上 |
| M5 spaCy | 🟡 中等 | ROOT 可能是 Given/When 後面的動詞 |
| M6 Ensemble | 🟡 中等 | 需要在 ACTION_VOCAB 加入 Gherkin 關鍵字或修改先驗 |

**修正方式：** 在解析前先去除 `Given`/`When`/`Then`/`And`/`But` 前綴：
```python
step = re.sub(r'^(Given|When|Then|And|But)\s+', '', step)
```
加上這一行預處理，大部分方法的準確率可以恢復到接近原始水準。

---

### 變化 4：動詞詞彙不同

**我們的動詞：** click, enter, verify, navigate, scroll, fill, select…

**其他可能的動詞：**
```
Tap the menu icon              ← 行動裝置測試
Swipe left on the card         ← 手勢操作
Assert that the count equals 5 ← 斷言式
Invoke the API endpoint        ← API 測試
Await the loading spinner      ← 非同步操作
```

| 方法 | 影響程度 | 原因 |
|------|---------|------|
| M1 Regex | 🟡 中等 | 不在 ACTION_VOCAB → 信心值降至 0.30，但動作仍可提取 |
| M2 Keyword | 🟡 中等 | 退回通用模式（信心 0.65） |
| M3 NLTK POS | 🟢 輕微 | 只要詞性標注正確，不受詞彙限制 |
| M4 NLTK Chunk | 🟢 輕微 | VP chunk 只需 VB* 標記，不管具體詞彙 |
| M5 spaCy | 🟢 輕微 | ROOT 不受詞彙限制 |
| M6 Ensemble | 🟡 中等 | BDD 先驗不加分（+0.0 而非 +2.0），但投票仍可能正確 |

**修正方式：** 在 `nlp_common.py` 的 `ACTION_VOCAB` 中加入新動詞即可。

---

### 變化 5：步驟非常複雜或使用自然語言敘述

**簡單步驟：**
```
Click the submit button
```

**複雜步驟：**
```
After the page loads, the user should be able to see the dashboard
  and the welcome message should contain the user's first name
If the login fails, an error message saying "Invalid credentials"
  should appear near the password field within 3 seconds
Drag the item from the shopping cart to the wish list,
  then verify that the cart total decreases accordingly
```

| 方法 | 影響程度 | 原因 |
|------|---------|------|
| M1 Regex | 🔴 嚴重 | 完全無法處理條件句、多子句 |
| M2 Keyword | 🔴 嚴重 | 模板匹配簡單句型，無法處理 |
| M3 NLTK POS | 🔴 嚴重 | 名詞短語收集邏輯會取到過多/過少的詞 |
| M4 NLTK Chunk | 🔴 嚴重 | CFG 文法設計用於簡單句 |
| M5 spaCy | 🟡 中等 | 依存分析可處理複雜句型，但多動詞時 ROOT 選擇可能不正確 |
| M6 Ensemble | 🔴 嚴重 | 所有子方法都失敗 → 投票也失敗 |

**結論：** 所有方法都假設步驟是「一個動作 + 一個目標」的簡單結構。面對複雜自然語言敘述，需要完全不同的方法（如 LLM 語義分析）。

---

## 泛化能力總評

### 按方法排名（1 = 最容易泛化，6 = 最難泛化）

| 排名 | 方法 | 泛化能力 | 原因 |
|------|------|---------|------|
| 1 | M5 spaCy | 🟢 最佳 | 基於句法結構而非格式假設，對句式變化最穩健 |
| 2 | M3 NLTK POS | 🟡 中等 | 基於詞性，不依賴特定詞彙，但 BDD 大寫問題在其他格式可能更嚴重 |
| 3 | M4 NLTK Chunk | 🟡 中等 | 文法規則需要針對新格式調整 |
| 4 | M6 Ensemble | 🟡 中等 | 泛化能力取決於子方法，BDD 先驗在非 BDD 格式中可能有害 |
| 5 | M1 Regex | 🔴 差 | 高度依賴「動詞開頭 + 引號」的格式假設 |
| 6 | M2 Keyword | 🔴 差 | 模板是為特定 BDD 用語手寫的，換一種說法就失效 |

### 按場景建議

| 新腳本類型 | 建議方法 | 需要的修改 |
|-----------|---------|-----------|
| 同樣格式的其他 BDD 步驟 | M6 Ensemble | 幾乎不需修改 |
| Gherkin (Given/When/Then) | M6 + 預處理 | 加一行去除 Gherkin 關鍵字的前綴 |
| 陳述句 / 第三人稱 | M5 spaCy | 修改 action 提取邏輯（不限第一個 VB） |
| 行動裝置測試（新動詞） | M6 Ensemble | 擴充 ACTION_VOCAB |
| 複雜自然語言敘述 | 需要新方法 | 考慮使用 LLM（如 GPT/Claude）進行語義分析 |

---

## 具體建議：如何提升泛化能力

### 低成本改善（修改幾行程式碼）

1. **擴充 ACTION_VOCAB**：加入更多動詞（tap, swipe, assert, invoke, await…）
2. **加入 Gherkin 預處理**：去除 Given/When/Then/And 前綴
3. **M1/M2 降低對引號的依賴**：改善無引號時的目標提取邏輯

### 中成本改善（需要調整架構）

4. **M3/M4 加入 BDD 先驗**：在詞性標注後，將句首大寫詞強制標為 VB
5. **M5 改善 ROOT 選擇**：如果 ROOT 是助動詞（is/are/was），向上尋找真正的動詞
6. **M6 調整先驗權重**：針對不同格式使用不同的先驗策略

### 高成本改善（需要新方法）

7. **使用 LLM**：對於複雜的自然語言敘述，直接用 GPT/Claude 提取 action-target
8. **Fine-tune 模型**：在大量 BDD 步驟語料上微調 NLTK 或 spaCy 模型
9. **機器學習分類器**：訓練一個專用的序列標注模型（如 BiLSTM-CRF）

---

## 總結

**短答：會下降，但下降幅度取決於新腳本與現有格式的差異程度。**

- 如果新腳本也是「動詞開頭的祈使句 + 引號目標」→ 準確率幾乎不變
- 如果是 Gherkin 格式 → 加一行預處理就能恢復
- 如果是陳述句或被動語態 → M5 (spaCy) 相對穩健，其他方法需大幅修改
- 如果是複雜自然語言 → 需要換用完全不同的方法（如 LLM）

**最穩健的方法是 M5（spaCy），因為它分析句法結構而非表面格式。**
**但在當前 BDD 格式下，M1/M2/M6 的準確率反而更高，因為它們的假設完美匹配。**

這是 NLP 中經典的「專用 vs 通用」取捨：
- 專用方法（M1/M2）在特定格式上極準，但換格式就失效
- 通用方法（M5）在所有格式上都還行，但不如專用方法準
- 集成方法（M6）嘗試兼顧兩者，但泛化能力受限於子方法
