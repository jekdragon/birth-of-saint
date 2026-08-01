#!/usr/bin/env python3
"""
Birth of the Saint — Log Analyzer CLI

Usage:
    python log_analyzer.py list                          # List all sessions
    python log_analyzer.py summary [session.jsonl]       # Session summary
    python log_analyzer.py analyze [session.jsonl]       # Full analysis with patterns
    python log_analyzer.py replay [session.jsonl]        # Step-by-step replay
    python log_analyzer.py grep --type ERROR [--last N]  # Search across sessions
    python log_analyzer.py patterns [session.jsonl]      # Pattern detection
    python log_analyzer.py perf [session.jsonl]          # Performance analysis

Zero dependencies — stdlib only.
"""
from __future__ import annotations
import json
import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Optional


# ── Colors ──────────────────────────────────────────────────────────
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_log_dir() -> Path:
    return Path(__file__).parent / "logs"


def list_sessions() -> list[Path]:
    log_dir = get_log_dir()
    if not log_dir.exists():
        return []
    return sorted(log_dir.glob("session_*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)


def read_entries(path: Path) -> list[dict]:
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def resolve_session(arg: Optional[str]) -> Path:
    """Resolve session file from arg or pick latest."""
    if arg:
        p = Path(arg)
        if p.exists():
            return p
        # Try in logs dir
        p = get_log_dir() / arg
        if p.exists():
            return p
        print(f"{RED}File not found: {arg}{RESET}")
        sys.exit(1)
    sessions = list_sessions()
    if not sessions:
        print(f"{RED}No sessions found in {get_log_dir()}{RESET}")
        sys.exit(1)
    return sessions[0]


def fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins}m {secs:.0f}s"


def fmt_time(entry: dict) -> str:
    t = entry.get("_t", 0)
    return f"{t:7.1f}s"


# ── LIST ────────────────────────────────────────────────────────────
def cmd_list(args):
    sessions = list_sessions()
    if not sessions:
        print(f"{DIM}No sessions found{RESET}")
        return

    print(f"{BOLD}Sessions ({len(sessions)}):{RESET}\n")
    for s in sessions:
        entries = read_entries(s)
        size = s.stat().st_size
        start = entries[0] if entries else {}
        end = entries[-1] if entries else {}
        duration = end.get("duration", end.get("_t", 0))
        errors = sum(1 for e in entries if e.get("type") == "ERROR")
        anomalies = sum(1 for e in entries if e.get("type") == "ANOMALY")

        ts = start.get("timestamp", s.stem.replace("session_", ""))
        status = f"{RED}✗ {errors} err{RESET}" if errors else f"{GREEN}✓{RESET}"
        anom = f" {YELLOW}⚠ {anomalies} anom{RESET}" if anomalies else ""

        print(f"  {DIM}{s.name}{RESET}")
        print(f"    {ts}  {fmt_duration(duration)}  {size//1024}KB  {status}{anom}  {len(entries)} entries")


# ── SUMMARY ─────────────────────────────────────────────────────────
def cmd_summary(args):
    path = resolve_session(args.session)
    entries = read_entries(path)
    if not entries:
        print(f"{RED}Empty session{RESET}")
        return

    # Collect stats
    types = Counter(e.get("type") for e in entries)
    errors = [e for e in entries if e.get("type") == "ERROR"]
    anomalies = [e for e in entries if e.get("type") == "ANOMALY"]
    transitions = [e for e in entries if e.get("type") == "TRANSITION"]
    levelups = [e for e in entries if e.get("type") == "LEVELUP"]
    fps_drops = [e for e in entries if e.get("type") == "FPS_DROP"]
    inputs = [e for e in entries if e.get("type") == "INPUT"]
    perf = [e for e in entries if e.get("type") == "PERF_SAMPLE"]

    start = entries[0]
    end = entries[-1]
    duration = end.get("duration", end.get("_t", 0))

    # FPS stats
    fps_vals = [e.get("fps", 0) for e in perf if e.get("fps")]
    avg_fps = sum(fps_vals) / len(fps_vals) if fps_vals else 0
    min_fps = min(fps_vals) if fps_vals else 0

    # Entity peaks
    max_enemies = max((e.get("enemies", 0) for e in perf), default=0)
    max_projectiles = max((e.get("projectiles", 0) for e in perf), default=0)

    print(f"{BOLD}═══ {path.name} ═══{RESET}\n")
    print(f"  Duration:     {CYAN}{fmt_duration(duration)}{RESET}")
    print(f"  Entries:      {len(entries)}")
    print(f"  Frames:       {end.get('total_frames', '?')}")
    print(f"  Timestamp:    {start.get('timestamp', '?')}")

    print(f"\n{BOLD}Event Breakdown:{RESET}")
    for t, count in types.most_common():
        color = ""
        if t == "ERROR": color = RED
        elif t == "ANOMALY": color = YELLOW
        elif t == "ENTITY_LEAK": color = YELLOW
        elif t == "FPS_DROP": color = CYAN
        print(f"  {color}{t:15s}{RESET} {count}")

    if errors:
        print(f"\n{RED}{BOLD}Errors ({len(errors)}):{RESET}")
        for e in errors[:5]:
            print(f"  {fmt_time(e)} {e.get('error_type')}: {e.get('message', '')[:80]}")

    if anomalies:
        print(f"\n{YELLOW}{BOLD}Anomalies ({len(anomalies)}):{RESET}")
        anom_types = Counter(e.get("description") for e in anomalies)
        for desc, count in anom_types.most_common():
            print(f"  {desc}: {count}")

    if transitions:
        print(f"\n{BOLD}Scene Flow:{RESET}")
        for t in transitions:
            fade = t.get("fade_type", "")
            fade_str = f" ({fade})" if fade else ""
            print(f"  {fmt_time(t)} {t.get('from')} → {t.get('to')}{fade_str} [{t.get('trigger')}]")

    if fps_vals:
        print(f"\n{BOLD}Performance:{RESET}")
        print(f"  Avg FPS:  {avg_fps:.1f}")
        print(f"  Min FPS:  {min_fps:.1f}")
        print(f"  FPS drops: {len(fps_drops)}")
        print(f"  Peak enemies: {max_enemies}")
        print(f"  Peak projectiles: {max_projectiles}")

    if levelups:
        print(f"\n{BOLD}Level-ups ({len(levelups)}):{RESET}")
        for lu in levelups[:10]:
            ttc = lu.get("time_to_choose", 0)
            print(f"  Lv{lu.get('level', '?')} → {lu.get('chosen_item', '?')} ({ttc:.1f}s)")

    # Health verdict
    print(f"\n{BOLD}Verdict:{RESET}")
    issues = []
    if errors:
        issues.append(f"{RED}{len(errors)} errors{RESET}")
    if anomalies:
        issues.append(f"{YELLOW}{len(anomalies)} anomalies{RESET}")
    if avg_fps < 30:
        issues.append(f"{CYAN}low avg FPS ({avg_fps:.0f}){RESET}")
    if max_enemies > 200:
        issues.append(f"{YELLOW}high enemy count ({max_enemies}){RESET}")
    if issues:
        print(f"  ⚠ Issues: {', '.join(issues)}")
    else:
        print(f"  {GREEN}✓ Clean session{RESET}")


# ── ANALYZE ─────────────────────────────────────────────────────────
def cmd_analyze(args):
    path = resolve_session(args.session)
    entries = read_entries(path)
    if not entries:
        print(f"{RED}Empty session{RESET}")
        return

    # First show summary
    cmd_summary(args)

    # Then pattern analysis
    print(f"\n{BOLD}═══ Pattern Analysis ═══{RESET}\n")
    detect_patterns(entries)


# ── PATTERNS ────────────────────────────────────────────────────────
def detect_patterns(entries: list[dict]):
    patterns = []

    # Pattern 1: Rapid scene transitions (thrashing)
    transitions = [e for e in entries if e.get("type") == "TRANSITION"]
    for i in range(len(transitions) - 2):
        t1, t2, t3 = transitions[i], transitions[i+1], transitions[i+2]
        if (t1.get("from") == t3.get("from") and
            t1.get("to") != t2.get("to") and
            t3.get("_t", 0) - t1.get("_t", 0) < 5):
            patterns.append(("scene_thrashing",
                f"Rapid scene cycling: {t1.get('from')}→{t1.get('to')}→{t2.get('to')}→{t3.get('to')} in {t3.get('_t', 0) - t1.get('_t', 0):.1f}s"))

    # Pattern 2: Error cascade (multiple errors in short window)
    errors = [e for e in entries if e.get("type") == "ERROR"]
    for i in range(len(errors) - 1):
        dt = errors[i+1].get("_t", 0) - errors[i].get("_t", 0)
        if dt < 2:
            patterns.append(("error_cascade",
                f"Errors within {dt:.1f}s: {errors[i].get('error_type')} → {errors[i+1].get('error_type')}"))

    # Pattern 3: Entity leak spiral
    leaks = [e for e in entries if e.get("type") == "ENTITY_LEAK"]
    leak_types = Counter(e.get("leak_type") for e in leaks)
    for lt, count in leak_types.items():
        if count > 3:
            patterns.append(("entity_leak_spiral",
                f"{lt} reported {count} times — persistent leak"))

    # Pattern 4: Performance degradation
    perf = [e for e in entries if e.get("type") == "PERF_SAMPLE"]
    if len(perf) >= 3:
        fps_early = [e.get("fps", 60) for e in perf[:3]]
        fps_late = [e.get("fps", 60) for e in perf[-3:]]
        avg_early = sum(fps_early) / len(fps_early)
        avg_late = sum(fps_late) / len(fps_late)
        if avg_late < avg_early * 0.7:
            patterns.append(("perf_degradation",
                f"FPS degraded: {avg_early:.0f} → {avg_late:.0f} ({(1-avg_late/avg_early)*100:.0f}% drop)"))

    # Pattern 5: Input ignored (clicks with no result)
    inputs = [e for e in entries if e.get("type") == "INPUT"]
    ignored = [e for e in inputs if e.get("result") == "ignored"]
    if len(ignored) > len(inputs) * 0.3 and len(inputs) > 5:
        patterns.append(("input_ignored",
            f"{len(ignored)}/{len(inputs)} inputs ignored ({len(ignored)/len(inputs)*100:.0f}%)"))

    # Pattern 6: Long level-up decision
    levelups = [e for e in entries if e.get("type") == "LEVELUP"]
    for lu in levelups:
        if lu.get("time_to_choose", 0) > 5:
            patterns.append(("slow_decision",
                f"Lv{lu.get('level')} took {lu.get('time_to_choose'):.1f}s to choose"))

    # Pattern 7: Gold anomaly
    anomalies = [e for e in entries if e.get("type") == "ANOMALY"]
    gold_anomalies = [e for e in anomalies if "gold" in e.get("description", "").lower()]
    if gold_anomalies:
        patterns.append(("gold_anomaly",
            f"Gold anomalies detected: {len(gold_anomalies)}"))

    # Pattern 8: FPS cluster (many drops in short window)
    drops = [e for e in entries if e.get("type") == "FPS_DROP"]
    if len(drops) > 10:
        patterns.append(("fps_cluster",
            f"{len(drops)} FPS drops — likely sustained performance issue"))

    # Pattern 9: Boss fight anomalies
    boss_anomalies = [e for e in anomalies if "boss" in e.get("description", "").lower()]
    if boss_anomalies:
        patterns.append(("boss_issue",
            f"Boss-related anomalies: {[e.get('description') for e in boss_anomalies]}"))

    # Pattern 10: Short session (likely crash)
    end = entries[-1] if entries else {}
    duration = end.get("duration", end.get("_t", 0))
    if duration < 10:
        patterns.append(("short_session",
            f"Session lasted only {duration:.1f}s — likely crash or quick exit"))

    # Print patterns
    if not patterns:
        print(f"  {GREEN}✓ No concerning patterns detected{RESET}")
        return

    for ptype, desc in patterns:
        icon = "🔴" if "cascade" in ptype or "crash" in ptype else "🟡"
        print(f"  {icon} {BOLD}{ptype}{RESET}: {desc}")


# ── REPLAY ──────────────────────────────────────────────────────────
def cmd_replay(args):
    path = resolve_session(args.session)
    entries = read_entries(path)
    if not entries:
        print(f"{RED}Empty session{RESET}")
        return

    limit = args.limit or 50
    event_types = args.type.split(",") if args.type else None

    print(f"{BOLD}Replay: {path.name} (showing {limit} entries){RESET}\n")

    shown = 0
    for e in entries:
        t = e.get("type", "")
        if event_types and t not in event_types:
            continue
        if shown >= limit:
            break

        time_str = fmt_time(e)
        color = ""
        if t == "ERROR": color = RED
        elif t == "ANOMALY": color = YELLOW
        elif t == "TRANSITION": color = GREEN
        elif t == "LEVELUP": color = CYAN
        elif t == "FPS_DROP": color = DIM
        elif t == "PERF_SAMPLE": color = DIM

        # Format based on type
        if t == "TRANSITION":
            print(f"  {DIM}{time_str}{RESET} {color}TRANSITION{RESET} {e.get('from')} → {e.get('to')} [{e.get('trigger')}]")
        elif t == "INPUT":
            result = e.get("result", "")
            element = e.get("element", "")
            print(f"  {DIM}{time_str}{RESET} INPUT {e.get('key')} @ {e.get('scene')} → {result} {element}")
        elif t == "ERROR":
            print(f"  {DIM}{time_str}{RESET} {color}ERROR{RESET} {e.get('error_type')}: {e.get('message', '')[:60]}")
        elif t == "LEVELUP":
            print(f"  {DIM}{time_str}{RESET} {color}LEVELUP{RESET} Lv{e.get('level')} → {e.get('chosen_item')} ({e.get('time_to_choose', 0):.1f}s)")
        elif t == "ANOMALY":
            print(f"  {DIM}{time_str}{RESET} {color}ANOMALY{RESET} {e.get('description')}")
        elif t == "FPS_DROP":
            print(f"  {DIM}{time_str}{RESET} {color}FPS{RESET} {e.get('fps')} fps (dt={e.get('dt')})")
        elif t == "STATE_SNAP":
            print(f"  {DIM}{time_str}{RESET} SNAP HP={e.get('hp')}/{e.get('max_hp')} kills={e.get('kills')} wave={e.get('wave')} gold={e.get('gold')}")
        elif t == "PERF_SAMPLE":
            if not args.quiet:
                print(f"  {DIM}{time_str}{RESET} PERF fps={e.get('fps')} enemies={e.get('enemies')} proj={e.get('projectiles')} part={e.get('particles')}")
        elif t == "ENTITY_LEAK":
            print(f"  {DIM}{time_str}{RESET} {color}LEAK{RESET} {e.get('leak_type')} x{e.get('count')}")
        elif t == "PAUSE":
            print(f"  {DIM}{time_str}{RESET} PAUSE {e.get('action')} (dt={e.get('pause_duration', 0):.1f}s)")
        elif t == "SESSION_START":
            print(f"  {DIM}{time_str}{RESET} {GREEN}▶ SESSION START{RESET}")
        elif t == "SESSION_END":
            print(f"  {DIM}{time_str}{RESET} {RED}■ SESSION END{RESET} reason={e.get('reason')} frames={e.get('total_frames')}")
        else:
            if not args.quiet:
                print(f"  {DIM}{time_str}{RESET} {color}{t}{RESET}")

        shown += 1

    print(f"\n  {DIM}Showing {shown}/{len(entries)} entries{RESET}")


# ── GREP ────────────────────────────────────────────────────────────
def cmd_grep(args):
    sessions = list_sessions()
    if args.last:
        sessions = sessions[:args.last]

    target_type = args.type.upper() if args.type else None
    query = args.query.lower() if args.query else None

    print(f"{BOLD}Searching {len(sessions)} sessions...{RESET}\n")
    total_hits = 0

    for s in sessions:
        entries = read_entries(s)
        hits = []
        for e in entries:
            if target_type and e.get("type") != target_type:
                continue
            if query:
                text = json.dumps(e, ensure_ascii=False).lower()
                if query not in text:
                    continue
            hits.append(e)

        if hits:
            print(f"  {BOLD}{s.name}{RESET} ({len(hits)} hits)")
            for h in hits[:10]:
                t = h.get("type", "?")
                time_str = fmt_time(h)
                desc = h.get("description") or h.get("message") or h.get("error_type") or ""
                print(f"    {DIM}{time_str}{RESET} {t}: {desc[:80]}")
            if len(hits) > 10:
                print(f"    {DIM}... and {len(hits)-10} more{RESET}")
            total_hits += len(hits)

    print(f"\n  {BOLD}Total: {total_hits} hits across {len(sessions)} sessions{RESET}")


# ── PERF ────────────────────────────────────────────────────────────
def cmd_perf(args):
    path = resolve_session(args.session)
    entries = read_entries(path)
    if not entries:
        print(f"{RED}Empty session{RESET}")
        return

    perf = [e for e in entries if e.get("type") == "PERF_SAMPLE"]
    drops = [e for e in entries if e.get("type") == "FPS_DROP"]

    if not perf:
        print(f"{DIM}No performance samples found{RESET}")
        return

    fps_vals = [e.get("fps", 0) for e in perf]
    enemy_vals = [e.get("enemies", 0) for e in perf]
    proj_vals = [e.get("projectiles", 0) for e in perf]
    part_vals = [e.get("particles", 0) for e in perf]

    print(f"{BOLD}═══ Performance Report ═══{RESET}\n")
    print(f"  Samples:    {len(perf)}")
    print(f"  FPS drops:  {len(drops)}")
    print(f"")
    print(f"  FPS:     avg={sum(fps_vals)/len(fps_vals):.1f}  min={min(fps_vals):.1f}  max={max(fps_vals):.1f}")
    print(f"  Enemies: avg={sum(enemy_vals)/len(enemy_vals):.0f}  max={max(enemy_vals)}")
    print(f"  Proj:    avg={sum(proj_vals)/len(proj_vals):.0f}  max={max(proj_vals)}")
    print(f"  Particles: avg={sum(part_vals)/len(part_vals):.0f}  max={max(part_vals)}")

    # Timeline (FPS over time)
    print(f"\n{BOLD}FPS Timeline:{RESET}")
    for e in perf:
        fps = e.get("fps", 0)
        t = e.get("_t", 0)
        bar_len = int(fps / 2)
        color = GREEN if fps >= 50 else YELLOW if fps >= 30 else RED
        bar = f"{color}{'█' * bar_len}{RESET}"
        print(f"  {t:6.1f}s {bar} {fps:.0f}")

    # Correlation: FPS vs entity count
    if len(perf) >= 3:
        print(f"\n{BOLD}FPS vs Entity Count:{RESET}")
        for e in perf:
            fps = e.get("fps", 0)
            total = e.get("enemies", 0) + e.get("projectiles", 0) + e.get("particles", 0)
            t = e.get("_t", 0)
            color = GREEN if fps >= 50 else YELLOW if fps >= 30 else RED
            print(f"  {t:6.1f}s  FPS={color}{fps:5.1f}{RESET}  entities={total}")


# ── MAIN ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Birth of the Saint — Log Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python log_analyzer.py list
  python log_analyzer.py summary
  python log_analyzer.py analyze logs/session_20260802_010635.jsonl
  python log_analyzer.py replay --type ERROR,ANOMALY --limit 20
  python log_analyzer.py grep --type ERROR --last 5
  python log_analyzer.py perf
        """)

    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="List all sessions")

    # summary
    p_sum = sub.add_parser("summary", help="Session summary")
    p_sum.add_argument("session", nargs="?", help="Session file (default: latest)")

    # analyze
    p_ana = sub.add_parser("analyze", help="Full analysis with patterns")
    p_ana.add_argument("session", nargs="?", help="Session file")

    # replay
    p_rep = sub.add_parser("replay", help="Step-by-step replay")
    p_rep.add_argument("session", nargs="?", help="Session file")
    p_rep.add_argument("--limit", "-n", type=int, default=50, help="Max entries to show")
    p_rep.add_argument("--type", "-t", help="Filter by type (comma-separated)")
    p_rep.add_argument("--quiet", "-q", action="store_true", help="Hide PERF_SAMPLE")

    # grep
    p_grep = sub.add_parser("grep", help="Search across sessions")
    p_grep.add_argument("--type", "-t", help="Filter by event type")
    p_grep.add_argument("--query", "-q", help="Text search in entries")
    p_grep.add_argument("--last", "-n", type=int, help="Only last N sessions")

    # perf
    p_perf = sub.add_parser("perf", help="Performance analysis")
    p_perf.add_argument("session", nargs="?", help="Session file")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "summary": cmd_summary,
        "analyze": cmd_analyze,
        "replay": cmd_replay,
        "grep": cmd_grep,
        "perf": cmd_perf,
    }

    if not args.command:
        parser.print_help()
        return

    commands[args.command](args)


if __name__ == "__main__":
    main()
