# 方法一：規則式正規表示式（Rule-based Regex）

**程式檔案：** `method1_regex.py`
**輸出檔案：** `results_regex.json`
**外部依賴：** 無（僅使用 Python 標準函式庫）

---

## 一句話說明

> 把每句測試步驟當成一串文字，用「第一個詞 = 動作、引號內文字或後面的名詞 = 目標」的簡單規則來拆解。

---

## 這個方法在做什麼？（白話版）

想像你拿到一張紙條，上面寫著：

```
Navigate to url 'http://example.com'
```

你會怎麼理解？

1. 看第一個詞 → **Navigate**（導航）→ 這就是「動作」
2. 看到引號裡有東西 → **http://example.com** → 這就是「目標」

方法一就是教電腦用這種「看第一個詞 + 找引號」的方式來理解每一句。

---

## 核心技術解說

### 什麼是正規表示式（Regular Expression / Regex）？

正規表示式是一種「文字搜尋模式」。例如：

| Regex 寫法 | 意思 | 能找到的文字 |
|-----------|------|-------------|
| `['\"]([^'\"]+)['\"]` | 引號中間的任何文字 | `'hello'` 裡的 `hello` |
| `\s+` | 一個以上的空白 | 空格、Tab |
| `\b` | 單詞邊界 | 分隔 `click` 和 `clicking` |

方法一不使用任何 AI 或機器學習模型，純粹靠這種「文字比對規則」來工作。

### ACTION_VOCAB — 動詞詞彙表

程式內建了一份「已知動作詞清單」：

```
launch, navigate, verify, click, enter, scroll, fill, select, check,
submit, wait, search, type, press, hover, drag, drop, upload, download,
open, close, refresh, filter, register, login, logout, add, delete, edit
```

如果步驟的第一個詞在這份清單裡，程式就會更有信心這確實是一個動作。

---

## 每個函式（function）在做什麼？

### `_analyse_single(sub)` — 分析單一子步驟

這是最核心的函式，處理一個「不含 and 連接的簡單步驟」。

**輸入範例：** `"Navigate to url 'http://example.com'"`

**處理流程：**

```
步驟 1：把句子用空白切成詞列表
        ["Navigate", "to", "url", "'http://example.com'"]

步驟 2：取第一個詞 → "navigate"（轉小寫）
        查 ACTION_VOCAB → 有找到 ✓
        → action = "Navigate"
        → confidence = 0.80（在詞彙表中）

步驟 3：找引號中的文字
        regex 搜尋 → 找到 "http://example.com"
        → targets = ["http://example.com"]
        → confidence += 0.10 → 0.90

步驟 4：回傳 action="Navigate", targets=["http://example.com"], confidence=0.90
```

**如果沒有引號怎麼辦？**

```
輸入："Scroll down to footer"

步驟 1：切成 ["Scroll", "down", "to", "footer"]
步驟 2：action = "Scroll"（在 ACTION_VOCAB → confidence = 0.80）
步驟 3：沒有引號
步驟 4：去掉介詞（to, down 等 SKIP_WORDS）
        剩下 ["footer"]
步驟 5：在 is/are/was/were 前截斷（本例沒有）
步驟 6：targets = ["footer"]
```

### `analyse(step)` — 分析完整步驟（含複合步驟）

這個函式是外部呼叫的入口。

**為什麼需要它？** 因為有些步驟包含兩個動作，例如：

```
Enter email address in input and click arrow button
```

這其實是兩個動作合在一起：
1. Enter email address
2. click arrow button

**處理流程：**

```
步驟 1：呼叫 split_compound_step()
        → ["Enter email address in input", "click arrow button"]

步驟 2：對每個子步驟呼叫 _analyse_single()
        子步驟1 → action="Enter", targets=["email address"]
        子步驟2 → action="click", targets=["arrow button"]

步驟 3：合併結果，計算平均信心值
        → pairs = [("Enter", ["email address"]), ("click", ["arrow button"])]
        → confidence = (0.80 + 0.80) / 2 = 0.80
```

---

## 信心值（Confidence）怎麼算？

信心值代表「程式對自己答案的把握程度」，範圍 0.0 ~ 1.0。

| 情況 | 信心值 |
|------|--------|
| 第一個詞在 ACTION_VOCAB 中 | 0.80 |
| 第一個詞不在 ACTION_VOCAB 中 | 0.30 |
| 有找到引號中的目標 | 額外 +0.10 |

例如 `Click on 'Submit'`：
- `click` 在詞彙表 → 0.80
- 有引號 `Submit` → +0.10
- 最終信心值 = **0.90**

---

## 實際執行範例

以 `App1-TestCase1.feature` 為例：

| 步驟 | 提取的動作 | 提取的目標 | 信心值 |
|------|-----------|-----------|--------|
| Launch browser | Launch | browser | 0.80 |
| Navigate to url 'http://automationexercise.com' | Navigate | http://automationexercise.com | 0.90 |
| Verify that home page is visible successfully | Verify | home page | 0.80 |
| Scroll down to footer | Scroll | footer | 0.80 |
| Verify text 'SUBSCRIPTION' | Verify | SUBSCRIPTION | 0.90 |
| Enter email address in input and click arrow button | Enter / click | email address / arrow button | 0.80 |

---

## 這個方法的限制

### 會出錯的情況

1. **非標準動詞開頭**：如果步驟不以動詞開頭（`The page should display X`），第一個詞 `The` 會被誤認為動作。

2. **無引號的複雜目標**：`Verify that the user registration form is displayed correctly` — 沒有引號，程式只能猜測 `user registration form` 是目標，但可能會多抓或少抓。

3. **不在詞彙表的新動詞**：如果測試步驟用了 `Swipe`、`Pinch` 等未收錄的動詞，信心值會降到 0.30，但動作仍可正確提取（只是信心低）。

### 適合的場景

- 步驟格式規範、以已知動詞開頭
- 目標放在引號中
- 不需要安裝任何外部套件

---

## 用其他自然語言腳本會怎樣？

詳見本文件最後的「泛化能力分析」章節（於 `generalizability_analysis.md`）。

簡短回答：**如果新腳本也遵循「動詞開頭 + 引號目標」的格式，準確率不會下降太多**。但如果步驟格式差異很大（如用完整英文句子、被動語態），準確率會顯著降低。
