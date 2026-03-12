# 方法六：集成投票（Ensemble Voting）

**程式檔案：** `method6_ensemble.py`
**輸出檔案：** `results_ensemble.json`
**外部依賴：** 以上所有（NLTK + spaCy），但缺少時可優雅降級

---

## 一句話說明

> 同時執行方法一到方法五，讓五個方法各自給出答案，再用「加權投票」選出最佳答案。

---

## 這個方法在做什麼？（白話版）

想像五個專家在開會，各自分析同一句測試步驟：

```
步驟："Verify 'Submit' is visible"

專家 1（Regex）   ：動作 = Verify ✓  （信心 0.90）
專家 2（Keyword） ：動作 = Verify ✓  （信心 0.90）
專家 3（NLTK POS）：動作 = Verify ✓  （信心 0.85）
專家 4（Chunk）   ：動作 = Verify ✓  （信心 0.85）
專家 5（spaCy）   ：動作 = is    ✗  （信心 0.50）
```

如何決定最終答案？用「投票」：
- Verify 得到 4 票（0.90 + 0.90 + 0.85 + 0.85 = 3.50）
- is 得到 1 票（0.50）
- Verify 勝出！

但方法六不只是簡單投票，它還加了一個「BDD 先驗規則」來確保結果正確。

---

## 核心技術解說

### 什麼是集成學習（Ensemble Learning）？

集成學習的核心思想是一句老話：**三個臭皮匠，勝過一個諸葛亮**。

```
單一方法：
  ┌─────────┐
  │ 方法 A  │ ─── 準確率 80%
  └─────────┘

集成方法：
  ┌─────────┐
  │ 方法 A  │ ──┐
  └─────────┘   │
  ┌─────────┐   │    ┌──────────┐
  │ 方法 B  │ ──┼──► │ 投票器   │ ─── 準確率 90%+
  └─────────┘   │    └──────────┘
  ┌─────────┐   │
  │ 方法 C  │ ──┘
  └─────────┘
```

**為什麼有效？** 因為不同方法會在**不同的地方犯錯**。方法 A 錯的步驟，方法 B 和 C 可能是對的；反過來也是。只要**多數方法答對**，投票結果就是正確的。

### 信心加權投票 vs 簡單多數決

**簡單多數決：** 每個方法一人一票，票多的贏。

**信心加權投票（本方法使用的）：** 信心高的方法票數更重。

```
例子：3 個方法預測「A」（信心各 0.30），2 個方法預測「B」（信心各 0.90）

簡單多數決：A 勝（3 票 > 2 票）
信心加權：  A = 0.30×3 = 0.90
            B = 0.90×2 = 1.80
            → B 勝！
```

信心加權更合理，因為信心值低代表「我不太確定」，信心值高代表「我很有把握」。

---

## 動作投票算法 — 一步步解說

### 第一步：收集所有方法的預測

```
步驟："Verify that home page is visible successfully"

方法 1（Regex）  ：action = "Verify"   confidence = 0.80
方法 2（Keyword）：action = "Verify"   confidence = 0.90
方法 3（NLTK POS）：action = "Verify"  confidence = 0.70
方法 4（Chunk）  ：action = "Verify"   confidence = 0.75
方法 5（spaCy）  ：action = "is"       confidence = 0.50
```

### 第二步：統計加權票數

```
action_votes = {
    "verify": 0.80 + 0.90 + 0.70 + 0.75 = 3.15,
    "is":     0.50
}
```

### 第三步：加入 BDD 祈使語氣先驗（關鍵步驟！）

**什麼是「先驗」（Prior）？**

先驗就是「在看到資料之前，你已經知道的背景知識」。

在 BDD 測試中，我們知道一個重要事實：**步驟幾乎總是以動作動詞開頭**。

所以如果步驟的第一個詞在 ACTION_VOCAB 中，我們應該**額外加分**，確保它不會被助動詞（is、are、was）搶走。

```
first_tok = "verify"（步驟的第一個詞）
"verify" ∈ ACTION_VOCAB? → Yes!

action_votes["verify"] += 2.0   ← 強先驗（+2.0）

# 其他在 ACTION_VOCAB 中的候選詞也加一點分
# （本例沒有其他候選詞在 ACTION_VOCAB 中，"is" 不在裡面）
```

### 第四步：最終票數

```
action_votes = {
    "verify": 3.15 + 2.0 = 5.15  ← 勝出！
    "is":     0.50
}
→ best_action = "Verify"
```

### 為什麼 +2.0 這個數字？

```
最壞情況：5 個方法全部投給 "is"
  is 的最高可能票數 = 0.90×5 = 4.50

如果第一個詞是 "verify" 且在 ACTION_VOCAB 中：
  verify 至少需要 > 4.50 才能贏
  → 只靠先驗不夠（2.0 < 4.50）
  → 但通常至少有 1~2 個方法也投 "verify"
  → 2.0 + 1~2 個方法的信心 > 4.50 → verify 勝出

設計原則：+2.0 足夠「扶持」一個有少數方法支持的正確答案，
但不會「壓倒」五個方法全部一致的預測。
```

---

## 目標投票算法 — 一步步解說

### 第一步：收集目標候選

```
方法 1：targets = ["home page"]
方法 2：targets = ["home page"]
方法 3：targets = ["that home page"]
方法 4：targets = ["home page"]
方法 5：targets = []（空）
```

### 第二步：統計加權票數

```
target_votes = {
    "home page":      0.80 + 0.90 + 0.75 = 2.45,
    "that home page": 0.70
}
```

### 第三步：決定應該輸出幾個目標

```
各方法的目標數量：[1, 1, 1, 1, 0]

count_votes = {1: 4, 0: 1}
→ 多數決：應該輸出 1 個目標
```

### 第四步：取票數最高的目標

```
sorted by votes:
1. "home page"      → 2.45
2. "that home page" → 0.70

取前 1 個 → targets = ["home page"]
```

---

## 信心值怎麼算？

```
avg_conf = (0.80 + 0.90 + 0.70 + 0.75 + 0.50) / 5 = 0.73
final_conf = 0.73 + 0.05 = 0.78
                    ↑
            共識加成（consensus bonus）
```

**為什麼加 0.05？**

當多個方法一起判斷時，即使平均信心值不變，「多人同意」這件事本身就提供了額外的可信度。+0.05 是一個保守的加成值，反映這種「共識效應」。

最終信心值上限為 1.0：`min(avg + 0.05, 1.0)`

---

## 每個函式在做什麼？

### `analyse(step)` — 唯一的主要函式

這是整個方法六的核心，流程如下：

```
輸入："Enter email address in input and click arrow button"

步驟 1：呼叫所有方法
        all_results = [m1(step), m2(step), m3(step), m4(step), m5(step)]

步驟 2：拆分複合步驟
        sub_steps = ["Enter email address in input", "click arrow button"]

步驟 3：對每個子步驟(idx)投票

    ─── idx=0："Enter email address in input" ───
    收集方法 1~5 對 pairs[0] 的預測
    動作投票 → "enter" 勝出
    目標投票 → "email address" 勝出
    → pair[0] = ("Enter", ["email address"])

    ─── idx=1："click arrow button" ───
    收集方法 1~5 對 pairs[1] 的預測
    動作投票 → "click" 勝出
    目標投票 → "arrow button" 勝出
    → pair[1] = ("click", ["arrow button"])

步驟 4：計算信心值
        avg_conf = mean(所有方法的 confidence)
        final_conf = avg_conf + 0.05

回傳：StepResult('ensemble', [pair0, pair1], final_conf, ...)
```

---

## 優雅降級（Graceful Degradation）

如果 NLTK 或 spaCy 沒有安裝：

```
可用方法：m1（Regex）+ m2（Keyword）= 2 個方法
不可用：m3, m4（返回空結果，信心 0.0）, m5（返回空結果，信心 0.0）

投票時：
  空結果的信心為 0.0 → 不影響投票
  m1 和 m2 的預測仍然有效
  → 結果較不穩健，但不會完全失敗
```

---

## 實際準確率

根據 `ground_truth.json` 的評估結果：

| 方法 | 動作準確率 | 配對準確率 |
|------|-----------|-----------|
| M1 Regex | 100% | — |
| M2 Keyword | 100% | — |
| M3 NLTK POS | 18.9% | — |
| M4 NLTK Chunk | 15.3% | — |
| M5 spaCy | 57.7% | — |
| **M6 Ensemble** | **100%** | — |

M6 結合了 M1/M2 的高準確率和 BDD 先驗規則，成功修正了 M3/M4/M5 的錯誤。

---

## 這個方法的限制

1. **速度最慢**：需要執行全部五個方法，延遲是所有方法的總和。
2. **共同盲點**：如果五個方法都犯了同樣的錯誤，投票也無法修正。
3. **先驗可能過強**：+2.0 的先驗在極端情況下可能壓過正確的非詞彙表動詞。
4. **信心值未校準**：0.78 不代表「78% 的機率是正確的」，只是一個啟發式數值。

---

## 適合的場景

- 追求最高準確率
- 可以接受較慢的速度
- 步驟格式可能不一致（需要多方法互相校正）
- 作為生產系統中的最終輸出方法
