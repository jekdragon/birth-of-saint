# Hooks: Current State vs Optimal

## Current Setup

### Hermes (41 hooks across 8 events)

| Event | Count | What's There |
|-------|-------|-------------|
| pre_tool_call | 3 | skill_forge_gate, duplicate-check, secrets-guard |
| post_tool_call | 9 | auto-format, auto-lint, auto-git-add, **auto-git-commit** (NEW), credential-scanner, gbrain-auto-signal, auto-timeline, code-index-sync, web-fact-extract |
| pre_llm_call | 11 | inject-git-context, inject-backlinks, auto-skill-load, context-size-monitor, keyword-router, anti-sycophancy-gate, loop-detector, memory-inject, gbrain-context, supermemory-inject, graphify-context, stale-warning |
| post_llm_call | 5 | quota-tracker, auto-save, signal-detector, decision-detector, correction-detector |
| on_session_start | 5 | gbrain-health-check, orphan-alert, dream-status-check, cold-tier-update, supermemory-profile-sync |
| on_session_end | 2 | session-to-gbrain, session-tracker |
| pre_verify | 1 | verify-gate |
| subagent_stop | 1 | notify-subagent |
| transform_llm_output | 3 | confidence-tagger, citation-checker, sycophancy-check |

### Git (birth-of-saint)

| Hook | What's There |
|------|-------------|
| pre-commit | Syntax check, conflict markers, large file detection, debug print warnings |

---

## Issues Found

### 1. auto-git-commit uses `--no-verify` ⚠️

**Current:** `git commit --no-verify` — SKIPS the pre-commit hook entirely.
**Problem:** The whole point of combining Hermes + Git hooks is defeated. Syntax errors slip through.
**Fix:** Remove `--no-verify` from auto-git-commit.py. Let pre-commit validate every auto-commit.

### 2. auto-git-add only matches `write_file`, not `patch` ⚠️

**Current:** `auto-git-add.py` has `matcher: write_file` only.
**Problem:** When I use `patch` (surgical edits), files aren't staged → auto-git-commit finds nothing to commit.
**Fix:** Change matcher to `write_file|patch`.

### 3. No debounce on auto-commit ⚠️

**Current:** Every `write_file` triggers a commit. If I edit 5 files in rapid succession = 5 commits.
**Problem:** Noisy git history, "auto(add): config" spam.
**Fix:** Add 5-second debounce window (like graphify-sync.py does). Accumulate files, commit once.

### 4. No commit message intelligence ⚠️

**Current:** `auto(add): config` — just the filename.
**Problem:** Doesn't tell WHY the change was made. No context from the agent's task.
**Fix:** Read `tool_input.content` for a comment/docstring hint, or inject the agent's current task context via stdin payload.

### 5. Git pre-commit doesn't run tests ⚠️

**Current:** Only syntax check + conflict markers.
**Problem:** Syntactically valid code can still break (logic errors, import failures).
**Fix:** Add `python -c "import main"` smoke test (fast, catches import errors). Full test suite is too slow for pre-commit.

### 6. No `commit-msg` hook ❌

**Current:** No commit message validation.
**Problem:** Auto-generated messages like `auto(add): config` don't follow conventional commits.
**Fix:** Add `commit-msg` hook to enforce format: `type(scope): description`. Auto-prefix with `auto:` for Hermes commits.

### 7. 3 hooks modified since approval ⚠️

**Current:** supermemory-profile-sync, supermemory-inject, graphify-context — all show "script modified since approval".
**Problem:** Security risk — modified scripts bypass consent.
**Fix:** Run `hermes hooks doctor` to re-validate.

### 8. No `on_session_start` health check for git state ❌

**Current:** Session start checks GBrain health, but not git.
**Problem:** Could be on a detached HEAD, dirty tree, or behind origin without knowing.
**Fix:** Add a session-start hook that reports git status summary.

### 9. pre-commit hook is NOT in the repo ⚠️

**Current:** Lives in `.git/hooks/` — local only, not cloned.
**Problem:** Other clones of birth-of-saint don't get the hook.
**Fix:** Move to `.githooks/pre-commit`, add `git config core.hooksPath .githooks`.

---

## Optimal Setup

### Hermes Hooks (what should change)

| Change | Action |
|--------|--------|
| auto-git-commit.py | Remove `--no-verify` |
| auto-git-add.py | Matcher: `write_file` → `write_file\|patch` |
| auto-git-commit.py | Add 5s debounce |
| New: git-status-inject.py | `on_session_start` — report git status |
| Re-validate 3 modified hooks | `hermes hooks doctor` |

### Git Hooks (what should change)

| Change | Action |
|--------|--------|
| Move to `.githooks/` | `git config core.hooksPath .githooks` |
| Add `commit-msg` hook | Enforce conventional commits |
| Add smoke test | `python -c "import main"` in pre-commit |
| Add `.githooks/README.md` | Document what each hook does |

---

## Priority Order

1. **Fix `--no-verify`** — critical, defeats the purpose
2. **Fix auto-git-add matcher** — patch edits don't get committed
3. **Add debounce** — stop commit spam
4. **Move git hooks to .githooks/** — make them portable
5. **Re-validate 3 modified hooks** — security
6. **Add commit-msg hook** — enforce format
7. **Add smoke test** — catch import errors
8. **Add git-status session hook** — awareness
