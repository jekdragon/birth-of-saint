# Hooks Improvement Roadmap

## Phase 1: Critical Fixes (do first)

### 1.1 Fix `--no-verify` in auto-git-commit.py
**Why:** Defeats the entire purpose of combining Hermes + Git hooks.
**Steps:**
1. Open `C:/Users/jekdr/AppData/Local/hermes/agent-hooks/auto-git-commit.py`
2. Find line: `"git", "commit", "-m", msg, "--no-verify"`
3. Remove `"--no-verify"`
4. Test: `hermes hooks test --for-tool write_file`
5. Verify: syntax error in staged file should block commit now

**Time:** 2 min
**Risk:** Low — if pre-commit hook is slow, commits get slower. Our hook takes ~0.1s.
**Dep:** None

---

### 1.2 Fix auto-git-add matcher
**Why:** `patch` edits don't get staged → auto-git-commit has nothing to commit.
**Steps:**
1. Edit config.yaml: change `auto-git-add.py` matcher from `write_file` to `write_file|patch`
2. Can't use `hermes config set` for array items — edit YAML directly via Python
3. Verify: `hermes hooks list` shows `matcher='write_file|patch'`
4. Test: make a `patch` call → file should be staged + committed

**Time:** 3 min
**Risk:** Low
**Dep:** None

---

### 1.3 Re-validate 3 modified hooks
**Why:** Security — scripts changed after approval.
**Steps:**
1. Run `hermes hooks doctor`
2. For each "modified since approval" hook, re-approve via `hermes hooks test --for-tool <tool>`
3. Affected: supermemory-profile-sync, supermemory-inject, graphify-context

**Time:** 2 min
**Risk:** None
**Dep:** None

---

## Phase 2: Anti-Spam (do after Phase 1)

### 2.1 Add debounce to auto-git-commit.py
**Why:** 5 rapid edits = 5 commits. History gets noisy.
**Steps:**
1. Add debounce logic to auto-git-commit.py:
   - Track last commit timestamp
   - If <5s since last commit, accumulate files in a temp file
   - On next call after 5s, commit all accumulated files
2. Use `~/.hermes/cache/auto-commit-queue.json` for persistence
3. Commit message: "auto(batch): config, enemies, weapons" (grouped)
4. Test: rapid writes → single commit with all files

**Time:** 15 min
**Risk:** Medium — edge case: session ends between writes → queued files never committed. Fix: flush queue on `on_session_end`.
**Dep:** 1.1 (need working commit first)

---

### 2.2 Improve commit message quality
**Why:** "auto(add): config" is meaningless.
**Steps:**
1. Parse `tool_input.content` (for `write_file`) or `tool_input.new_string` (for `patch`)
2. Extract first comment/docstring as context hint
3. Fallback to filename-based message if no hint found
4. Format: `auto(type): module — hint` (e.g., `auto(update): enemies — added slow/freeze effects`)

**Time:** 10 min
**Risk:** Low — worst case falls back to current behavior
**Dep:** 1.1

---

## Phase 3: Git Hook Improvements (do after Phase 2)

### 3.1 Move git hooks to `.githooks/`
**Why:** `.git/hooks/` is local-only. Other clones don't get hooks.
**Steps:**
1. `mkdir -p E:/birth-of-saint/.githooks/`
2. `cp E:/birth-of-saint/.git/hooks/pre-commit E:/birth-of-saint/.githooks/pre-commit`
3. `git -C E:/birth-of-saint config core.hooksPath .githooks`
4. Add `.githooks/` to git (not gitignored)
5. Verify: `git -C E:/birth-of-saint config core.hooksPath` → `.githooks`
6. Test: clone fresh → hooks should work

**Time:** 5 min
**Risk:** Low — if someone clones without `core.hooksPath`, they just don't get hooks (graceful degradation)
**Dep:** None

---

### 3.2 Add `commit-msg` hook
**Why:** Enforce conventional commit format.
**Steps:**
1. Create `.githooks/commit-msg`
2. Validate format: `^(auto|feat|fix|chore|docs|test|refactor)(\(.+\))?: .+`
3. Auto-commits from Hermes start with `auto(` — pass through
4. Manual commits must follow conventional format
5. Exit 1 + error message if format wrong
6. Test: bad format blocked, `auto(add): config` passes

**Time:** 10 min
**Risk:** Low — can always bypass with `--no-verify` for emergencies
**Dep:** 3.1

---

### 3.3 Add smoke test to pre-commit
**Why:** Syntax-valid code can still break on import.
**Steps:**
1. Add to `.githooks/pre-commit` after syntax check:
   ```python
   # Smoke test: try importing main modules
   result = subprocess.run(
       [sys.executable, "-c", "import config, enemies, weapons"],
       capture_output=True, text=True, timeout=10
   )
   if result.returncode != 0:
       errors.append(f"  IMPORT: {result.stderr[:200]}")
   ```
2. Only run if any `.py` file changed
3. Timeout 10s max (don't block commits forever)
4. Test: break an import → commit blocked

**Time:** 10 min
**Risk:** Medium — import might fail due to missing SDL/display. Need `SDL_VIDEODRIVER=dummy` fallback.
**Dep:** 3.1

---

## Phase 4: Awareness (do after Phase 3)

### 4.1 Add git-status session hook
**Why:** Start sessions knowing if tree is dirty, detached HEAD, behind origin.
**Steps:**
1. Create `agent-hooks/git-status-inject.py`
2. Fire on `on_session_start`
3. Run `git status --short -b` for watched projects
4. If dirty or behind origin, inject context: "⚠️ birth-of-saint: 47 uncommitted changes, 3 commits behind origin"
5. Register in config.yaml under `on_session_start`
6. Add to allowlist

**Time:** 10 min
**Risk:** Low — adds ~0.5s to session start
**Dep:** None

---

### 4.2 Add post-commit hook for notifications
**Why:** Know when auto-commits happen.
**Steps:**
1. Create `.githooks/post-commit`
2. Log commit hash + message + changed files count to `~/.hermes/logs/auto-commits.log`
3. Optional: if commit was auto-generated, don't notify (too noisy)
4. Test: commit → log entry appears

**Time:** 5 min
**Risk:** None — post-commit can't block anything
**Dep:** 3.1

---

## Summary

| Phase | Items | Total Time | Dependencies |
|-------|-------|-----------|-------------|
| **1: Critical** | 1.1, 1.2, 1.3 | 7 min | None |
| **2: Anti-Spam** | 2.1, 2.2 | 25 min | 1.1 |
| **3: Git Hooks** | 3.1, 3.2, 3.3 | 25 min | 3.1 |
| **4: Awareness** | 4.1, 4.2 | 15 min | 3.1 |
| **Total** | 9 items | ~72 min | |

---

## Execution Order

```
1.1 (no-verify fix)  ─┐
1.2 (matcher fix)    ─┤── Phase 1 (parallel, 7 min)
1.3 (re-validate)    ─┘
                      ↓
2.1 (debounce)       ─┐── Phase 2 (sequential, 25 min)
2.2 (msg quality)    ─┘
                      ↓
3.1 (.githooks/)     ─┐
3.2 (commit-msg)     ─┤── Phase 3 (sequential, 25 min)
3.3 (smoke test)     ─┘
                      ↓
4.1 (git-status)     ─┐── Phase 4 (parallel, 15 min)
4.2 (post-commit)    ─┘
```

## Files Modified

| File | Phase | Change |
|------|-------|--------|
| `agent-hooks/auto-git-commit.py` | 1.1, 2.1, 2.2 | Remove --no-verify, add debounce, improve msgs |
| `config.yaml` | 1.2 | auto-git-add matcher → `write_file\|patch` |
| `.githooks/pre-commit` | 3.1 | Move from .git/hooks/ |
| `.githooks/commit-msg` | 3.2 | New hook |
| `.githooks/post-commit` | 4.2 | New hook |
| `agent-hooks/git-status-inject.py` | 4.1 | New hook |
| `.hermes/cache/auto-commit-queue.json` | 2.1 | Debounce state file |
