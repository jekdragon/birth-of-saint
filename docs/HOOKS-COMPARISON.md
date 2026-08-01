# Git Hooks vs Hermes Hooks — Comparison

Based on official documentation:
- Git: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
- Hermes: https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks

---

## Architecture Overview

| Dimension | Git Hooks | Hermes Shell Hooks |
|-----------|-----------|-------------------|
| **Trigger** | Git operations (commit, push, merge, etc.) | Agent tool calls, LLM calls, sessions |
| **Location** | `.git/hooks/` | `~/.hermes/agent-hooks/` |
| **Registration** | Filename = event name (auto-detected) | `hooks:` block in `config.yaml` |
| **Language** | Any executable (shell, Python, Ruby, Go) | Any executable (shell, Python, Go) |
| **Isolation** | Subprocess (same user) | Subprocess (same user) |
| **Crash safety** | Hook crash = operation fails | Hook crash = logged & skipped, agent continues |

---

## Event Types

| Git Hook Event | Fires When | Blocks? | Hermes Equivalent |
|---------------|-----------|---------|-------------------|
| `pre-commit` | Before commit message | ✅ exit 1 | `pre_tool_call` (before any tool) |
| `prepare-commit-msg` | After default msg, before editor | ✅ exit 1 | — |
| `commit-msg` | After user writes msg | ✅ exit 1 | — |
| `post-commit` | After commit completes | ❌ | `post_tool_call` |
| `pre-push` | Before push to remote | ✅ exit 1 | — |
| `pre-receive` | Server: before accepting push | ✅ exit 1 | — |
| `post-receive` | Server: after push accepted | ❌ | — |
| `post-checkout` | After `git checkout` | ❌ | — |
| `post-merge` | After `git merge` | ❌ | — |
| `pre-rebase` | Before rebase | ✅ exit 1 | — |
| — | — | — | `pre_llm_call` (before LLM turn) |
| — | — | — | `post_llm_call` (after LLM turn) |
| — | — | — | `on_session_start` |
| — | — | — | `on_session_end` |
| — | — | — | `pre_verify` (before code verify) |
| — | — | — | `subagent_stop` (delegate_task done) |

---

## Blocking Mechanism

| Aspect | Git | Hermes |
|--------|-----|--------|
| **Block signal** | Exit code ≠ 0 | JSON `{"action": "block", "message": "..."}` or exit ≠ 0 |
| **Bypass flag** | `git commit --no-verify` | No per-call bypass (but `hooks_auto_accept: true` globally) |
| **Block scope** | Aborts the git operation | Blocks the specific tool call |
| **Error message** | stderr → shown to user | `message` field → injected into agent context |

---

## Input/Output Protocol

| Aspect | Git | Hermes |
|--------|-----|--------|
| **Input** | stdin (for some hooks: commit-msg file, ref list) | stdin: JSON `{"hook_event_name", "tool_name", "tool_input", ...}` |
| **Output** | exit code only (stdout/stderr for messages) | stdout: JSON `{}` (passthrough) or `{"action":"block",...}` |
| **Structured data** | No (raw text) | Yes (JSON wire protocol) |

---

## Configuration

### Git
```bash
# No config file needed — just drop executable in .git/hooks/
chmod +x .git/hooks/pre-commit
```

### Hermes
```yaml
# config.yaml
hooks:
  post_tool_call:
    - matcher: "write_file|patch"    # regex filter
      command: "python ~/.hermes/agent-hooks/auto-format.py"
      timeout: 10                    # seconds, default 60, max 300

hooks_auto_accept: false             # consent model
```

---

## Matcher/Filtering

| Capability | Git | Hermes |
|-----------|-----|--------|
| **Event filter** | Filename-based (pre-commit, post-push, etc.) | `event_name:` key in config |
| **Tool filter** | N/A (only git operations) | `matcher: "write_file\|patch"` regex |
| **Path filter** | Manual in hook script (`git diff --cached`) | Manual in hook script (inspect `tool_input.path`) |
| **Multiple hooks per event** | One file per event | Array of hooks per event |

---

## Consent / Security Model

| Aspect | Git | Hermes |
|--------|-----|--------|
| **Trust** | `.git/hooks/` is local-only, not cloned | `shell-hooks-allowlist.json` per (event, command) pair |
| **First-run prompt** | None | Interactive prompt per new (event, command) |
| **Auto-accept** | N/A | `hooks_auto_accept: true` or `--accept-hooks` or env var |
| **Audit** | `ls .git/hooks/` | `hermes hooks list`, `hermes hooks doctor` |
| **Revocation** | `rm .git/hooks/pre-commit` | `hermes hooks revoke <event>` |

---

## CLI / Debugging

| Command | Git | Hermes |
|---------|-----|--------|
| **List hooks** | `ls .git/hooks/` | `hermes hooks list` |
| **Test hooks** | Manual run | `hermes hooks test --for-tool X` |
| **Health check** | N/A | `hermes hooks doctor` |
| **Revoke** | Delete file | `hermes hooks revoke <event>` |

---

## Portability

| Aspect | Git | Hermes |
|--------|-----|--------|
| **Cloned with repo** | ❌ (local only) | ❌ (config.yaml is per-user) |
| **Shared via** | `.githooks/` dir + `core.hooksPath` | Version-controlled config.yaml |
| **Cross-platform** | Works (with shebang/PATH) | Works (Python .cmd shims on Windows) |

---

## Key Differences Summary

1. **Git hooks = version control lifecycle** (commit, push, merge). Hermes hooks = **AI agent lifecycle** (tool calls, LLM turns, sessions).
2. **Git** blocks via exit code. **Hermes** blocks via structured JSON response.
3. **Git** has no built-in filtering — you script it. **Hermes** has `matcher:` regex for tool names.
4. **Git** hooks are per-repo. **Hermes** hooks are per-user (global config).
5. **Hermes** has a consent model (allowlist). **Git** trusts anything in `.git/hooks/`.
6. **Hermes** hooks are non-blocking by design — errors are caught, logged, skipped. **Git** hooks crashing = operation fails.
7. **Hermes** has `hermes hooks doctor` for health checks. **Git** has no equivalent.

---

## Our Setup (birth-of-saint)

| Layer | Hook | What it does |
|-------|------|-------------|
| **Hermes** | `auto-git-add.py` (post_tool_call, matcher: write_file) | Stages files after `write_file` |
| **Hermes** | `auto-git-commit.py` (post_tool_call, matcher: write_file\|patch) | Auto-commits staged changes with descriptive message |
| **Git** | `pre-commit` (.git/hooks/) | Blocks syntax errors, warns about debug prints & large files |

Flow: `write_file` → auto-git-add (stage) → auto-git-commit (commit) → pre-commit (validate) → commit succeeds or blocked
