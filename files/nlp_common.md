# 共用基礎模組：nlp_common.py

**程式檔案：** `nlp_common.py`
**輸出檔案：** 無（被其他方法 import，不獨立執行）
**外部依賴：** `nltk`（選用）、`spacy` + `en_core_web_sm`（選用）；缺少時自動降級

---

## 一句話說明

> 所有六種 NLP 方法共用的「基礎工具箱」：定義資料型別、動詞詞彙表、複合步驟拆分器、`.feature` 檔解析器與結果存檔工具。

---

## 這個模組在做什麼？（白話版）

六種方法（method1 ～ method6）各自負責不同的 NLP 分析邏輯，但有很多事情是大家都要做的：

- 讀取 `.feature` 檔
- 把「Enter email and click button」這類複合步驟拆開
- 用同一種格式儲存結果到 JSON
- 共用同一份動詞詞彙表

如果每個方法都自己寫一份，六份程式碼幾乎一模一樣，往後修改要改六次。
`nlp_common.py` 就是把這些重複的部分統一抽出來，讓各方法只需 `from nlp_common import ...` 即可使用。

---

## 模組結構總覽

```
nlp_common.py
│
├── NLP 函式庫偵測
│   ├── NLTK_AVAILABLE   （bool）
│   └── SPACY_AVAILABLE  （bool）、NLP_MODEL
│
├── 共用詞彙表
│   ├── ACTION_VOCAB     （34 個動作動詞）
│   └── SKIP_WORDS       （介詞、冠詞等略過詞）
│
├── 資料型別
│   ├── ActionTarget     （NamedTuple）
│   └── StepResult       （NamedTuple）
│
├── 拆分工具
│   ├── split_compound_step()
│   └── extract_targets()
│
└── 執行工具
    ├── parse_feature_file()
    ├── save_method_results()
    └── run_method_standalone()
```

---

## 共用詞彙表

### ACTION_VOCAB — 動作動詞表

34 個已知動作詞，各方法都以此作為「是否為動作」的判斷依據：

```
launch, navigate, verify, click, enter, scroll, fill, select, check,
submit, wait, search, type, press, hover, drag, drop, upload, download,
open, close, refresh, filter, register, login, logout, add, delete, edit
```

### SKIP_WORDS — 略過詞

提取目標時濾掉的介詞與冠詞：

```
on, to, in, at, into, with, that, down, the, a, an
```

---

## 資料型別

### `ActionTarget`

儲存從單一（子）步驟提取出的一組動作與目標：

```python
class ActionTarget(NamedTuple):
    action:  str        # 動作動詞，例如 "Click"
    targets: List[str]  # 目標列表，例如 ["Signup / Login"]
```

一個步驟可能含多個 `ActionTarget`，例如：

```
Enter email address in input and click arrow button
→ [ActionTarget("Enter", ["email address"]),
   ActionTarget("click",  ["arrow button"])]
```

### `StepResult`

儲存一個完整步驟的分析結果（包含信心值與備註）：

```python
class StepResult(NamedTuple):
    method:     str              # 使用的方法名稱
    pairs:      List[ActionTarget]
    confidence: float            # 0.0 ~ 1.0
    notes:      str              # 除錯或說明訊息
```

---

## 拆分工具

### `split_compound_step(step)` — 複合步驟拆分器

**問題：** 測試步驟可能把兩個動作用 `and` 連接在一起：

```
Enter email address in input and click arrow button
```

這是兩個獨立操作，必須分開處理。

**運作方式：** 只在 `and` 後面緊跟著 `ACTION_VOCAB` 中的動詞時才切割，避免把「Enter name and email」（兩個目標）誤切。

```python
split_compound_step("Enter email and click button")
# → ["Enter email", "click button"]   ← 切割（click 是動作詞）

split_compound_step("Enter name and email address")
# → ["Enter name and email address"]  ← 不切割（email 不是動作詞）
```

### `extract_targets(raw)` — 多目標拆分器

**問題：** 有些步驟的目標本身就是多個，用逗號或 `and` 分隔：

```
Fill details: Title, Name, Email, Password, Date of birth
```

**運作方式：** 以 `, ` 或 ` and ` 分割字串：

```python
extract_targets("Title, Name, Email, Password")
# → ["Title", "Name", "Email", "Password"]

extract_targets("name and email address")
# → ["name", "email address"]

extract_targets("SUBSCRIPTION")
# → ["SUBSCRIPTION"]   ← 單一目標直接回傳
```

---

## 執行工具

### `parse_feature_file(path)` — `.feature` 檔解析器

讀取一個 `.feature` 檔，回傳結構化字典：

```python
{
  'file':  'App1-TestCase1.feature',
  'urls':  ['http://automationexercise.com'],
  'title': 'Test Case 1: Verify Subscription in home page',
  'steps': ['Launch browser', 'Navigate to url ...', ...]
}
```

**特殊處理：**

| 問題 | 處理方式 |
|------|----------|
| 部分檔案含 JSON 區塊 | 截取 `{` 前的文字，忽略後半 |
| TestCase3 步驟重複兩次 | 偵測「後半 = 前半」，自動去重保留前半 |
| 連續相同步驟 | 逐行去除相鄰重複 |

### `save_method_results(method_id, all_cases)` — 結果存檔

將所有測試案例的分析結果寫入 `results_<method_id>.json`：

```python
save_method_results("regex", all_cases)
# → 寫出 results_regex.json
```

### `run_method_standalone(method_id, analyse_fn)` — 統一執行入口

各方法在 `if __name__ == '__main__':` 時呼叫此函式，標準化執行流程：

```
1. 掃描目錄下所有 *.feature 檔
2. 對每個步驟呼叫 analyse_fn(step) → StepResult
3. 印出結果到 stdout
4. 呼叫 save_method_results() 存檔
5. 將存檔內容再印一次到 stdout
```

各方法只需傳入自己的分析函式，執行流程完全統一。

---

## NLP 函式庫偵測

模組載入時自動偵測 NLTK 與 spaCy 是否可用：

```python
NLTK_AVAILABLE  # True / False
SPACY_AVAILABLE # True / False
NLP_MODEL       # spacy 模型物件，或 None
```

若 NLTK 可用，同時自動下載所需的語料庫（`punkt_tab`、`averaged_perceptron_tagger_eng` 等）。
各方法根據這兩個旗標決定是否啟用對應功能，確保在未安裝 NLP 套件的環境下也能執行。

---

## 與各方法的關係

```
nlp_common.py
    │
    ├── method1_regex.py      import: ACTION_VOCAB, SKIP_WORDS,
    ├── method2_keyword.py             split_compound_step, extract_targets,
    ├── method3_nltk_pos.py            ActionTarget, StepResult,
    ├── method4_nltk_chunk.py          parse_feature_file,
    ├── method5_spacy_dep.py           save_method_results,
    └── method6_ensemble.py            run_method_standalone
```

所有方法都 import 完整的共用介面，自身只實作各自的 `analyse(step) → StepResult` 函式。
