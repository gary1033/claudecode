# 演算法輸出 (Action/Target) 對比真實網頁元素的方法整理

本文針對前述 NLP 演算法所萃取的 `action` / `target` 結構，
說明如何在真實網頁中定位對應的 DOM 元素，並依可靠度排序各策略。

---

## 一、問題背景

演算法輸出的典型結構如下：

```json
{ "action": "Click",  "targets": ["Signup / Login"] }
{ "action": "Enter",  "targets": ["email address"] }
{ "action": "Verify", "targets": ["ACCOUNT CREATED!"] }
{ "action": "Scroll", "targets": ["footer"] }
```

`target` 是**自然語言描述**，不是 CSS selector 或 XPath，
因此需要一套「語意 → DOM 元素」的對比流程。

---

## 二、依 Action 類型分類的對比策略

### 2.1 `Click` — 點擊類

目標通常是按鈕、連結、圖示。

| 優先順序 | 比對方式 | 範例 XPath / CSS |
|----------|----------|-----------------|
| 1 | **完整文字比對**（大小寫不敏感） | `//button[normalize-space()='Signup / Login']` |
| 2 | **部分文字包含** | `//a[contains(text(),'Signup')]` |
| 3 | **aria-label / title 屬性** | `[aria-label='Signup / Login']` |
| 4 | **value 屬性**（`<input type="submit">`） | `input[value='Login']` |
| 5 | **placeholder / name 屬性**（備用） | `[name='login']` |

**注意**：文字比對前先做 `normalize-space()` 去除首尾空白與多餘換行。

---

### 2.2 `Enter` / `Fill` — 輸入類

目標通常是 `<input>`、`<textarea>`。

| 優先順序 | 比對方式 | 範例 |
|----------|----------|------|
| 1 | **placeholder 屬性**（最常見） | `input[placeholder*='email' i]` |
| 2 | **關聯 `<label>` 文字**（for/id 連結） | `//label[contains(.,'Email')]/..//input` |
| 3 | **name / id 屬性**（語意關鍵字模糊比對） | `input[name*='email']` |
| 4 | **aria-label** | `[aria-label*='email' i]` |
| 5 | **input type 推斷**（target='password' → `type="password"`） | `input[type='password']` |

**關鍵技巧**：target 字串如為 `email address`，先拆詞取主幹 `email`，
再用 `contains` 或 `*=`（CSS substring）比對各屬性。

---

### 2.3 `Verify` — 驗證類

目標通常是**可見文字**，不需要互動，只需確認存在。

| 優先順序 | 比對方式 | 範例 |
|----------|----------|------|
| 1 | **精確全文比對**（引號內字串） | `//body[contains(.,'ACCOUNT CREATED!')]` |
| 2 | **heading/paragraph 標籤縮小範圍** | `//h2[contains(.,'SUBSCRIPTION')]` |
| 3 | **忽略大小寫的 CSS** | `:has-text('account created')` (Playwright) |
| 4 | **正規表達式比對**（動態訊息） | `page.get_by_text(re.compile(r'subscribed', re.I))` |

**Playwright 特有**：`page.get_by_text()` 內建模糊比對，最適合 Verify 步驟。

---

### 2.4 `Scroll` — 捲動類

目標通常是區塊容器或方向描述。

| target 範例 | 對比策略 |
|-------------|----------|
| `footer` | CSS tag selector: `footer`, 或 `[id*='footer']` |
| `page to bottom` | `window.scrollTo(0, document.body.scrollHeight)` |
| `bottom right side` | 視覺定位，找 `position:fixed` 的元素 |
| `RECOMMENDED ITEMS` | 先找含此文字的 `section/div`，再 scroll into view |

---

### 2.5 `Hover` — 懸停類

與 Click 策略相同，但執行 `element.hover()` 而非 `element.click()`。

---

## 三、通用比對優先級流程

以下流程適用於所有 action 類型，依序嘗試直到找到唯一元素：

```
target 字串
    │
    ▼
Step 1: 精確文字比對（完整 normalize 後的可見文字）
    │  找到唯一元素 → 使用
    ▼  找不到或多個
Step 2: 屬性比對（id / name / placeholder / aria-label / title / value）
    │  以 target 關鍵字做 substring 比對（大小寫不敏感）
    ▼  找不到
Step 3: 關聯 label 比對
    │  找 <label> 含 target 關鍵字，取其 for 指向的元素
    ▼  找不到
Step 4: 模糊文字比對（Fuzzy / NLP 語意相似度）
    │  計算 target 與所有可互動元素文字的相似度，取最高分
    ▼  找不到
Step 5: 根據 action 類型 + DOM 結構推斷
        例：action=Enter → 優先取當前 <form> 內的第 N 個 input
```

---

## 四、模糊比對（Fuzzy Matching）方法比較

當精確比對失敗時，以下方法可提升召回率：

### 4.1 字串相似度（輕量）

```python
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# target = "Signup / Login"
# element text = "SIGNUP/LOGIN"  → ratio ≈ 0.85 → 通過
```

**閾值建議**：ratio ≥ 0.75 視為匹配。

---

### 4.2 Token 集合比對（對詞序不敏感）

```python
from rapidfuzz import fuzz

score = fuzz.token_set_ratio("arrow button", "submit arrow")
# 比 SequenceMatcher 更能處理詞序不同的情況
```

---

### 4.3 語意嵌入（最準確，成本較高）

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

target_emb = model.encode("email address input")
elements = ["Enter your email", "Email", "Your email address"]

scores = util.cos_sim(target_emb, model.encode(elements))
best_match = elements[scores.argmax()]  # → "Enter your email"
```

**適用場景**：target 描述與元素屬性措辭差異大時（如 `arrow button` vs `scroll-to-top`）。

---

### 4.4 關鍵字抽取後比對（配合前述演算法）

由於演算法已做 NLP 分析，可進一步：

1. 從 target 抽出**名詞主幹**（已有 spaCy dep parsing）
2. 只用主幹比對 DOM，降低雜訊

```python
# target = "incorrect email address and password"
# 主幹名詞 = ["email", "password"]
# → 分別找 input[name*='email'] 和 input[type='password']
```

---

## 五、依框架的實作建議

### Selenium

```python
from selenium.webdriver.common.by import By

# 文字比對（XPath）
driver.find_element(By.XPATH, f"//*[normalize-space()='{target}']")

# 屬性模糊比對
driver.find_element(By.CSS_SELECTOR, f"[placeholder*='{keyword}' i]")

# 關聯 label
driver.find_element(By.XPATH,
    f"//label[contains(.,'{keyword}')]/..//input")
```

### Playwright（推薦，內建語意定位）

```python
# 最接近 target 語意的定位方式
page.get_by_role("button", name=target)       # Click
page.get_by_label(target)                      # Enter
page.get_by_text(target)                       # Verify
page.get_by_placeholder(target)               # Enter（placeholder）

# 模糊文字（regex）
page.get_by_text(re.compile(keyword, re.I))
```

Playwright 的 `get_by_role` + `name` 結合了角色語意與文字比對，
**最接近人類閱讀測試步驟的方式**，推薦作為主要策略。

---

## 六、特殊 Target 類型處理

| Target 特徵 | 識別方式 | 對比策略 |
|-------------|----------|----------|
| 全大寫字串（`SUBSCRIPTION`） | `isupper()` | 用 `normalize-space()` 忽略大小寫比對 |
| 引號包裹（`'Create Account'`） | 含 `'...'` | 去除引號後精確比對 |
| URL（`http://...`） | `startswith('http')` | 比對 `href` 屬性或 `window.location` |
| 方向描述（`bottom right`） | 含方向詞 | 使用 `position:fixed` 或座標比對 |
| 序數（`first product`） | 含 first/second/1st | XPath `[1]` 或 CSS `:nth-child(1)` |
| 錯誤/成功訊息 | 含 `!` 結尾長句 | Verify 流程：全文比對 `body` 文字 |

---

## 七、整體建議架構

```
┌─────────────────────────────────────────────────────┐
│  輸入：action="Click", target="Signup / Login"      │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  依 action 決定       │
         │  候選元素類型         │
         │  Click → button, a    │
         │  Enter → input, textarea│
         │  Verify → 任意可見元素│
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  Step1: 精確文字比對  │──→ 找到 → 回傳
         └───────────┬───────────┘
                     │ 找不到
         ┌───────────▼───────────┐
         │  Step2: 屬性 substring│──→ 找到 → 回傳
         └───────────┬───────────┘
                     │ 找不到
         ┌───────────▼───────────┐
         │  Step3: label 關聯    │──→ 找到 → 回傳
         └───────────┬───────────┘
                     │ 找不到
         ┌───────────▼───────────┐
         │  Step4: Fuzzy/語意    │──→ score≥0.75 → 回傳
         └───────────┬───────────┘
                     │ 仍找不到
                 回報無法定位，
                 標記該步驟需人工確認
```

---

## 八、參考資源

- [Playwright Locators 文件](https://playwright.dev/python/docs/locators)
- [RapidFuzz — Python 模糊比對](https://github.com/maxbachmann/RapidFuzz)
- [sentence-transformers — 語意相似度](https://www.sbert.net/)
- [XPath axes cheatsheet](https://devhints.io/xpath)
