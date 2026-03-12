# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working in this repository.

本文件為在此儲存庫中工作的 AI 助理（Claude 及其他）提供指引。

---

## Repository Overview

**Project:** claudecode
**Status:** Early-stage / starter repository
**Repository:** gary1033/claudecode

This is a minimal repository currently in its initial state. As the project grows, this file should be updated to reflect the actual codebase structure, conventions, and workflows.

## 儲存庫概覽

**專案：** claudecode
**狀態：** 早期階段 / 起始儲存庫
**儲存庫：** gary1033/claudecode

這是一個目前處於初始狀態的最小化儲存庫。隨著專案成長，本文件應持續更新以反映實際的程式碼結構、慣例與工作流程。

---

## Current Structure

```
/
├── README.md       # Project title placeholder
└── CLAUDE.md       # This file
```

## 目前結構

```
/
├── README.md       # 專案標題佔位文件
└── CLAUDE.md       # 本文件
```

---

## Development Branch Conventions

When working on this repository as part of an AI-assisted workflow:

- Feature branches follow the pattern `claude/<task-slug>-<session-id>`
- Always develop on the designated branch and push when work is complete
- Never push directly to `master` without explicit permission
- Use `git push -u origin <branch-name>` for pushing branches

## 開發分支慣例

在 AI 輔助工作流程中操作此儲存庫時：

- 功能分支遵循 `claude/<task-slug>-<session-id>` 的命名格式
- 始終在指定分支上開發，完成後再推送
- 未經明確許可，絕不直接推送至 `master`
- 推送分支時使用 `git push -u origin <branch-name>`

---

## Git Workflow

```bash
# Check current branch before making changes
git status
git branch

# Stage and commit changes
git add <specific-files>   # Prefer specific files over `git add .`
git commit -m "descriptive message"

# Push to remote
git push -u origin <branch-name>
```

### Commit Message Style

- Use imperative mood: "Add feature" not "Added feature"
- Keep subject line under 72 characters
- Be descriptive about the *why*, not just the *what*

## Git 工作流程

```bash
# 修改前確認目前分支
git status
git branch

# 暫存並提交變更
git add <specific-files>   # 優先指定檔案，避免使用 `git add .`
git commit -m "描述性訊息"

# 推送至遠端
git push -u origin <branch-name>
```

### Commit 訊息風格

- 使用祈使語氣：寫「Add feature」而非「Added feature」
- 主旨行保持在 72 個字元以內
- 著重描述「為什麼」，而非只說「做了什麼」

---

## Adding New Code

When this project gains a language/framework, update the relevant sections below:

### If JavaScript/TypeScript (Node.js)
- Run `npm install` to install dependencies
- Run `npm test` to execute tests
- Run `npm run build` for production builds
- Run `npm run lint` for linting

### If Python
- Create and activate a virtual environment: `python -m venv .venv && source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Run tests: `pytest`
- Format code: `black .` and `isort .`
- Lint: `flake8` or `ruff`

### If Go
- Run `go mod tidy` to sync dependencies
- Run `go test ./...` to execute tests
- Run `go build ./...` to build
- Run `go vet ./...` and `golint ./...` for linting

### If Rust
- Run `cargo build` to build
- Run `cargo test` to execute tests
- Run `cargo clippy` for linting
- Run `cargo fmt` for formatting

## 新增程式碼

當專案加入語言或框架時，請更新以下對應區塊：

### 若使用 JavaScript/TypeScript (Node.js)
- 執行 `npm install` 安裝依賴
- 執行 `npm test` 跑測試
- 執行 `npm run build` 建置正式版本
- 執行 `npm run lint` 進行程式碼檢查

### 若使用 Python
- 建立並啟用虛擬環境：`python -m venv .venv && source .venv/bin/activate`
- 安裝依賴：`pip install -r requirements.txt`
- 跑測試：`pytest`
- 格式化程式碼：`black .` 與 `isort .`
- 程式碼檢查：`flake8` 或 `ruff`

### 若使用 Go
- 執行 `go mod tidy` 同步依賴
- 執行 `go test ./...` 跑測試
- 執行 `go build ./...` 建置
- 執行 `go vet ./...` 與 `golint ./...` 進行檢查

### 若使用 Rust
- 執行 `cargo build` 建置
- 執行 `cargo test` 跑測試
- 執行 `cargo clippy` 進行程式碼檢查
- 執行 `cargo fmt` 格式化程式碼

---

## Key Conventions for AI Assistants

### General Principles

1. **Read before editing** — Always read a file before modifying it
2. **Minimal changes** — Only change what is necessary; avoid over-engineering
3. **No unnecessary files** — Do not create files unless strictly required
4. **Security first** — Never introduce SQL injection, XSS, command injection, or other OWASP vulnerabilities
5. **No secrets in code** — Never commit credentials, API keys, or tokens

### Code Quality

- Prefer editing existing files over creating new ones
- Do not add docstrings, comments, or type annotations to code you didn't change
- Do not add error handling for scenarios that cannot happen
- Do not create abstractions or helpers for one-time-use operations
- Keep complexity at the minimum required for the current task

### Before Making Changes

1. Understand the existing code and structure
2. Confirm which branch to work on
3. Make focused, targeted edits
4. Verify changes do not break existing functionality

### File Index Maintenance

- Whenever a file is **added or removed** from the `files/` directory, **always update `files/README.md`** in the same commit to reflect the change.

### Risky Actions — Always Confirm First

The following actions require explicit user confirmation before proceeding:

- Deleting files or directories
- Force-pushing any branch
- Resetting commit history (`git reset --hard`)
- Modifying CI/CD pipelines
- Pushing to `master`/`main`
- Any action affecting shared state or external services

## AI 助理的核心慣例

### 一般原則

1. **先讀後改** — 修改檔案前必須先讀取內容
2. **最小變動** — 只修改必要的部分，避免過度設計
3. **不建立多餘檔案** — 除非絕對必要，否則不新增檔案
4. **安全優先** — 絕不引入 SQL 注入、XSS、命令注入或其他 OWASP 漏洞
5. **程式碼不含密鑰** — 絕不提交憑證、API 金鑰或 Token

### 程式碼品質

- 優先修改現有檔案，而非建立新檔案
- 不要對未修改的程式碼新增 docstring、注解或型別標注
- 不要為不可能發生的情境添加錯誤處理
- 不要為一次性操作建立抽象層或輔助函式
- 將複雜度控制在完成當前任務的最低限度

### 修改前確認事項

1. 理解現有程式碼與結構
2. 確認要在哪個分支上工作
3. 進行有針對性的精確修改
4. 確認變更不會破壞現有功能

### 檔案索引維護

- 每當 `files/` 目錄有檔案**新增或刪除**，**必須在同一次 commit 中同步更新 `files/README.md`**。

### 高風險操作 — 必須先確認

以下操作在執行前需取得使用者明確確認：

- 刪除檔案或目錄
- 強制推送任何分支
- 重置提交歷史（`git reset --hard`）
- 修改 CI/CD 流水線
- 推送至 `master`/`main`
- 任何影響共享狀態或外部服務的操作

---

## Environment Setup

As this project grows, document environment variables and setup steps here.

```bash
# Example: copy and configure environment
cp .env.example .env
# Edit .env with your values
```

## 環境設定

隨著專案成長，請在此記錄環境變數與設定步驟。

```bash
# 範例：複製並設定環境變數
cp .env.example .env
# 編輯 .env 填入實際值
```

---

## Testing

Document test commands here as they are established. Ensure all tests pass before pushing.

## 測試

請在此記錄測試指令。推送前確保所有測試通過。

---

## Updating This File

This CLAUDE.md should be kept current. When the project gains:
- A language or framework → update the relevant setup/test commands
- Linting or formatting tools → document the commands
- CI/CD pipelines → describe the workflow
- Architectural decisions → capture the reasoning
- New conventions → add them to the conventions section

## 維護本文件

本 CLAUDE.md 應保持最新狀態。當專案新增以下內容時，請同步更新：
- 語言或框架 → 更新對應的設定/測試指令
- Lint 或格式化工具 → 記錄相關指令
- CI/CD 流水線 → 描述工作流程
- 架構決策 → 記錄決策理由
- 新慣例 → 加入慣例區塊
