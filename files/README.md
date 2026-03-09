# 測試案例 POS 分析器

## 功能說明

這個程式會讀取所有的 `.feature` 測試案例檔案，對每一個測試步驟進行詞性（POS - Part of Speech）分析，並為每個步驟生成一個 SVG 視覺化圖表。

## 主要功能

### 1. 讀取檔案
- 自動讀取當前目錄下所有的 `.feature` 檔案
- 解析測試案例的標題、URL 和步驟

### 2. POS 詞性分析
程式會分析每個測試步驟中的詞彙，並標註其詞性：

- **VERB (動詞)** - 紅色 (#ff6b6b)
  - 例如: launch, navigate, verify, click, enter, scroll
  
- **NOUN (名詞)** - 青色 (#4ecdc4)
  - 例如: browser, page, button, input, email, text
  
- **PREP (介係詞)** - 淺青色 (#95e1d3)
  - 例如: to, in, on, at, with, by
  
- **DET (限定詞)** - 黃色 (#f9ca24)
  - 例如: a, an, the, that, this
  
- **AUX (助動詞)** - 粉色 (#fd79a8)
  - 例如: is, are, am, was, were, be
  
- **ADV (副詞)** - 橙色 (#fdcb6e)
  - 例如: successfully, correctly, visible
  
- **CONJ (連接詞)** - 紫色 (#a29bfe)
  - 例如: and, or, but
  
- **QUOTE (引用文字)** - 藍色 (#74b9ff)
  - 所有在引號中的文字

### 3. SVG 生成
為每個測試步驟生成一個 SVG 圖表，顯示：
- 原始測試步驟文字
- 每個詞彙及其詞性標籤
- 用顏色區分不同的詞性
- 虛線連接相鄰的詞彙

## 輸出結構

```
svg_output/
├── App1-TestCase1/
│   ├── step_01.svg
│   ├── step_02.svg
│   ├── ...
│   └── step_07.svg
├── App1-TestCase2/
│   ├── step_01.svg
│   ├── ...
├── App2-TestCase1/
│   ├── step_01.svg
│   ├── ...
└── index.html (索引頁面)
```

## 統計資訊

- **測試案例檔案**: 12 個
- **總測試步驟**: 107 個
- **生成的 SVG**: 107 個

## 使用方法

1. 將所有 `.feature` 檔案放在程式所在目錄
2. 執行程式: `python test_case_reader.py`
3. 查看 `svg_output` 目錄中生成的 SVG 檔案
4. 開啟 `svg_output/index.html` 可在瀏覽器中查看所有圖表

## 範例

### 輸入
```
6. Enter email address in input and click arrow button
```

### 輸出 (POS 分析)
```
Enter(VERB) email(NOUN) address(NOUN) in(PREP) input(NOUN) and(CONJ) click(VERB) arrow(NOUN) button(NOUN)
```

### 視覺化
生成的 SVG 會顯示每個詞彙，並用不同顏色的標籤標示其詞性。

## 技術細節

- 使用簡化的規則式 POS 標註器
- SVG 格式輸出，可在任何瀏覽器中查看
- 支援中文輸出和說明
- 自動創建目錄結構

## 檔案清單

1. `test_case_reader.py` - 主程式
2. `svg_output/` - SVG 輸出目錄
3. `svg_output/index.html` - 索引頁面
4. `README.md` - 本說明文檔
