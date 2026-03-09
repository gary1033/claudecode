# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working in this repository.

## Repository Overview

**Project:** claudecode
**Status:** Early-stage / starter repository
**Repository:** gary1033/claudecode

This is a minimal repository currently in its initial state. As the project grows, this file should be updated to reflect the actual codebase structure, conventions, and workflows.

## Current Structure

```
/
├── README.md       # Project title placeholder
└── CLAUDE.md       # This file
```

## Development Branch Conventions

When working on this repository as part of an AI-assisted workflow:

- Feature branches follow the pattern `claude/<task-slug>-<session-id>`
- Always develop on the designated branch and push when work is complete
- Never push directly to `master` without explicit permission
- Use `git push -u origin <branch-name>` for pushing branches

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

### Risky Actions — Always Confirm First

The following actions require explicit user confirmation before proceeding:

- Deleting files or directories
- Force-pushing any branch
- Resetting commit history (`git reset --hard`)
- Modifying CI/CD pipelines
- Pushing to `master`/`main`
- Any action affecting shared state or external services

## Environment Setup

As this project grows, document environment variables and setup steps here.

```bash
# Example: copy and configure environment
cp .env.example .env
# Edit .env with your values
```

## Testing

Document test commands here as they are established. Ensure all tests pass before pushing.

## Updating This File

This CLAUDE.md should be kept current. When the project gains:
- A language or framework → update the relevant setup/test commands
- Linting or formatting tools → document the commands
- CI/CD pipelines → describe the workflow
- Architectural decisions → capture the reasoning
- New conventions → add them to the conventions section
