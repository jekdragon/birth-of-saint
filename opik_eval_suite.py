"""
Opik Evaluation Suite for Birth of the Saint
Tests AI-generated claims against actual code to detect hallucinations.

Usage:
    python opik_eval_suite.py          # Run all evaluations
    python opik_eval_suite.py --dry    # Dry run (no API calls)
    python opik_eval_suite.py --facts  # Extract facts from code
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Any, Dict

import opik
from opik import track
from opik.evaluation import evaluate
from opik.evaluation.metrics import Hallucination, AnswerRelevance

# ─── Project root ───
PROJECT_ROOT = Path("E:/birth-of-saint")


# ─── 1. Code Fact Extractor ───

@track(project_name="birth-of-saint-eval")
def extract_facts_from_code() -> dict:
    """Extract verifiable facts from the codebase."""
    facts: Dict[str, Any] = {}

    # Weapon classes
    weapons_path = PROJECT_ROOT / "weapons.py"
    if weapons_path.exists():
        content = weapons_path.read_text(encoding="utf-8")
        weapon_classes = re.findall(r"class (\w+Weapon)\b", content)
        facts["weapon_count"] = len(weapon_classes)
        facts["weapon_classes"] = weapon_classes

    # Enemy types
    enemies_path = PROJECT_ROOT / "enemies.py"
    if enemies_path.exists():
        content = enemies_path.read_text(encoding="utf-8")
        enemy_defs = re.findall(r'^\s+"(\w+)":\s*\{', content, re.MULTILINE)
        facts["enemy_types"] = enemy_defs
        facts["enemy_count"] = len(enemy_defs)

    # Scenes
    scenes_path = PROJECT_ROOT / "scenes.py"
    if scenes_path.exists():
        content = scenes_path.read_text(encoding="utf-8")
        scene_classes = re.findall(r"class (\w+Scene)\b", content)
        facts["scene_count"] = len(scene_classes)
        facts["scenes"] = scene_classes

    # Config constants
    config_path = PROJECT_ROOT / "config.py"
    if config_path.exists():
        content = config_path.read_text(encoding="utf-8")
        width = re.search(r"WIDTH\s*=\s*(\d+)", content)
        height = re.search(r"HEIGHT\s*=\s*(\d+)", content)
        fps = re.search(r"FPS\s*=\s*(\d+)", content)
        if width:
            facts["width"] = int(width.group(1))
        if height:
            facts["height"] = int(height.group(1))
        if fps:
            facts["fps"] = int(fps.group(1))

    # Test files
    test_dir = PROJECT_ROOT / "tests"
    if test_dir.exists():
        test_files = list(test_dir.glob("test_*.py"))
        facts["test_files"] = len(test_files)

    # Save profiles
    save_path = PROJECT_ROOT / "save_system.py"
    if save_path.exists():
        content = save_path.read_text(encoding="utf-8")
        profiles = re.findall(r"profile_(\d+)\.json", content)
        facts["save_profiles"] = len(set(profiles)) if profiles else 1

    return facts


# ─── 2. Load code context for a question ───

def load_context_for_question(question: str) -> str:
    """Load relevant code context based on question keywords."""
    q_lower = question.lower()
    files_to_load = []

    # Map keywords to files
    keyword_map = {
        "weapon": ["weapons.py", "config.py"],
        "enemy": ["enemies.py"],
        "scene": ["scenes.py", "scene_manager.py"],
        "health": ["hud.py"],
        "config": ["config.py"],
        "save": ["save_system.py"],
        "reaper": ["main.py", "wave_manager.py"],
        "deploy": ["main.py"],
        "passive": ["weapons.py", "config.py"],
        "biome": ["config.py"],
        "test": ["tests/test_phase25.py"],
        "ui": ["hud.py", "menu.py", "scenes.py"],
        "lobby": ["lobby.py"],
    }

    for keyword, files in keyword_map.items():
        if keyword in q_lower:
            files_to_load.extend(files)

    if not files_to_load:
        files_to_load = ["config.py", "main.py"]

    # Deduplicate
    files_to_load = list(dict.fromkeys(files_to_load))

    chunks = []
    for f in files_to_load:
        path = PROJECT_ROOT / f
        if path.exists():
            lines = path.read_text(encoding="utf-8").splitlines()[:80]
            chunks.append(f"=== {f} ===\n" + "\n".join(lines))

    return "\n\n".join(chunks)


# ─── 3. Dataset ───

DATASET = [
    {
        "input": "How many weapon types are in the game?",
        "expected_output": "9 weapons",
        "context_files": ["weapons.py", "config.py"],
    },
    {
        "input": "What is the max number of weapon slots?",
        "expected_output": "6 weapon slots",
        "context_files": ["hud.py", "config.py"],
    },
    {
        "input": "How many enemy types exist?",
        "expected_output": "11 enemy types",
        "context_files": ["enemies.py"],
    },
    {
        "input": "What happens at 15 minutes in the game?",
        "expected_output": "The Reaper spawns at 15 minutes",
        "context_files": ["main.py", "wave_manager.py"],
    },
    {
        "input": "How many save profiles are supported?",
        "expected_output": "3 save profiles",
        "context_files": ["save_system.py"],
    },
    {
        "input": "What scene manager pattern is used?",
        "expected_output": "Scene base class with SceneManager, OverlayScene for pause",
        "context_files": ["scene_manager.py", "scenes.py"],
    },
    {
        "input": "How does the health bar work?",
        "expected_output": "Dual-bar with trailing damage bar, red pulse at low HP",
        "context_files": ["hud.py"],
    },
    {
        "input": "How many passive items exist?",
        "expected_output": "10 passive items",
        "context_files": ["weapons.py", "config.py"],
    },
    {
        "input": "What is the game's deployment target?",
        "expected_output": "GitHub Pages via pygbag WASM",
        "context_files": ["main.py"],
    },
    {
        "input": "What screen resolution is used?",
        "expected_output": "1024x768 at 60 FPS",
        "context_files": ["config.py"],
    },
]


# ─── 4. Task function (dict → dict) ───

@track(project_name="birth-of-saint-eval")
def answer_from_code(item: Dict[str, Any]) -> Dict[str, Any]:
    """Answer a question by extracting relevant code lines.

    Returns dict with 'output' key (required by Opik evaluate).
    """
    question = item["input"]
    context = item.get("context", "")
    if not context:
        context = load_context_for_question(question)

    # Extract relevant lines
    q_words = set(question.lower().split()) - {"how", "many", "what", "is", "the", "in", "a", "of", "are", "to", "and"}
    lines = context.splitlines()
    relevant = []
    for line in lines:
        line_lower = line.lower()
        if any(w in line_lower for w in q_words):
            relevant.append(line.strip())

    answer = "\n".join(relevant[:15]) if relevant else "No relevant code found."
    return {"output": answer}


# ─── 5. Evaluation runner ───

def run_evaluation(dry_run: bool = False):
    """Run hallucination detection on the dataset."""

    print("=" * 60)
    print("OPIK EVALUATION: Birth of the Saint")
    print("=" * 60)
    print(f"Dataset: {len(DATASET)} test cases")
    print(f"Project: {PROJECT_ROOT}")
    print()

    # Build items with context
    items = []
    for item in DATASET:
        context = load_context_for_question(item["input"])
        items.append({
            "input": item["input"],
            "expected_output": item["expected_output"],
            "context": context[:8000],
        })

    if dry_run:
        print("[DRY RUN] No API calls will be made.\n")
        for i, item in enumerate(items, 1):
            result = answer_from_code(item)
            print(f"--- Test {i} ---")
            print(f"Q: {item['input']}")
            print(f"Expected: {item['expected_output']}")
            print(f"Got: {result['output'][:200]}")
            print()
        return

    # Initialize Opik client
    client = opik.Opik(project_name="birth-of-saint-eval")

    # Create dataset
    dataset = client.get_or_create_dataset(name="birth-of-saint-facts")
    dataset.clear()
    dataset.insert(items)
    print(f"Dataset created: {len(items)} items")

    # Metrics — using OpenRouter (DeepSeek free)
    hallucination_metric = Hallucination(
        name="hallucination_check",
        model="openrouter/deepseek/deepseek-chat",
    )
    relevance_metric = AnswerRelevance(
        name="relevance_check",
        model="openrouter/deepseek/deepseek-chat",
    )

    # Run evaluation
    print("\nRunning evaluation (may take a few minutes)...")

    result = evaluate(
        dataset=dataset,
        task=answer_from_code,
        scoring_metrics=[hallucination_metric, relevance_metric],
        project_name="birth-of-saint-eval",
        experiment_name="hallucination-scan-v1",
        verbose=1,
    )

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    # Aggregate scores
    agg = result.aggregate_evaluation_scores()
    for metric_name, stats in agg.aggregated_scores.items():
        print(f"  {metric_name}: mean={stats.mean:.2f}, min={stats.min:.2f}, max={stats.max:.2f}")

    # Save report
    report = {
        "experiment": "hallucination-scan-v1",
        "metrics": {
            name: {"mean": stats.mean, "min": stats.min, "max": stats.max}
            for name, stats in agg.aggregated_scores.items()
        },
    }
    report_path = PROJECT_ROOT / "opik-eval-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport: {report_path}")
    print("Dashboard: https://www.comet.com/opik/")


# ─── 6. PyTest integration ───

def test_no_hallucinations():
    """PyTest-compatible test: verify code facts are accurate."""
    facts = extract_facts_from_code()

    # Known correct values
    assert facts.get("weapon_count", 0) >= 6, f"Expected >=6 weapons, got {facts.get('weapon_count')}"
    assert facts.get("enemy_count", 0) >= 6, f"Expected >=6 enemies, got {facts.get('enemy_count')}"
    assert facts.get("scene_count", 0) >= 4, f"Expected >=4 scenes, got {facts.get('scene_count')}"
    assert facts.get("width") == 1024, f"Expected width 1024, got {facts.get('width')}"
    assert facts.get("height") == 768, f"Expected height 768, got {facts.get('height')}"
    assert facts.get("fps") == 60, f"Expected FPS 60, got {facts.get('fps')}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Opik evaluation for Birth of the Saint")
    parser.add_argument("--dry", action="store_true", help="Dry run (no API calls)")
    parser.add_argument("--facts", action="store_true", help="Extract facts only")
    args = parser.parse_args()

    if args.facts:
        facts = extract_facts_from_code()
        print(json.dumps(facts, indent=2, default=str))
    else:
        run_evaluation(dry_run=args.dry)
