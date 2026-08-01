"""Deep code review: API contracts, stale refs, common bugs."""
import re
import os

PROJECT = "E:/birth-of-saint"

# 1. Check for stale/dangling references in function calls
stale_patterns = [
    (r'damage_numbers\.append\(', "Old damage_numbers API (should be floating_numbers.spawn_damage)"),
    (r'display_name\(\)', "Old display_name() method call (should be w.name property)"),
    (r'DamageNumber\(', "Direct DamageNumber instantiation (should use floating_numbers.spawn_damage)"),
]

# 2. Check for missing 'from __future__' or type hints issues
# 3. Check for hardcoded values that should be in config
hardcoded_patterns = [
    (r'(?<!\w)(800|600)(?!\w)', "Hardcoded screen dimensions (check if should be WIDTH/HEIGHT)"),
    (r'4000', "Hardcoded MAP dimensions"),
]

# 4. Check for undefined variable patterns
# 5. Check weapon API consistency
# 6. Check scene flow consistency

issues = []

py_files = [f for f in os.listdir(PROJECT) if f.endswith('.py') and not f.startswith('_') and f != 'ref_vs_clone.py']

for fname in sorted(py_files):
    path = os.path.join(PROJECT, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check stale patterns
    for pattern, desc in stale_patterns:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line) and not line.strip().startswith('#'):
                issues.append(f"  {fname}:{i} — {desc}: {line.strip()[:80]}")
    
    # Check for 'self.damage_numbers' in main.py
    if fname == 'main.py':
        for i, line in enumerate(lines, 1):
            if 'self.damage_numbers' in line and not line.strip().startswith('#'):
                issues.append(f"  {fname}:{i} — Stale self.damage_numbers: {line.strip()[:80]}")

# 6. Check for missing animator=None guard in scene draw methods
for fname in ['scenes.py', 'game_over_screen.py']:
    path = os.path.join(PROJECT, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if draw methods have animator guard
    if 'animator' in content:
        if 'if self.animator' not in content and 'if animator' not in content:
            issues.append(f"  {fname} — Uses animator but no None guard in draw()")
        elif 'if self.animator' in content:
            pass  # has guard
        elif 'animator is not None' in content:
            pass  # has guard

# 7. Check for w.display_name() in all files
for fname in py_files:
    path = os.path.join(PROJECT, fname)
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if 'display_name()' in line and not line.strip().startswith('#'):
                issues.append(f"  {fname}:{i} — display_name() call: {line.strip()[:80]}")

# 8. Check that all classes referenced in scenes.py are imported
path = os.path.join(PROJECT, 'scenes.py')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

scene_classes = ['SplashScene', 'TitleScene', 'GameScene', 'PauseOverlay', 'GameOverScene', 
                 'LobbyScene', 'SettingsScene', 'BestiaryScene', 'CodexScene', 'RunPrepScene']
for cls in scene_classes:
    if cls not in content:
        issues.append(f"  scenes.py — Missing scene class: {cls}")

# 9. Check for missing pygame.time.get_ticks() workaround in tests
# 10. Check for round() calls that might cause issues
# 11. Check for missing await in async functions
for fname in py_files:
    path = os.path.join(PROJECT, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check async def functions have await
    async_funcs = re.findall(r'async def (\w+)', content)
    for func in async_funcs:
        # Find the function body
        func_match = re.search(rf'async def {func}\b.*?(?=\n(?:    def |class |\S)|\Z)', content, re.DOTALL)
        if func_match:
            body = func_match.group()
            if 'await' not in body and 'asyncio.sleep' not in body:
                # Check if it's a short function that might legitimately not need await
                if len(body.split('\n')) > 5:
                    issues.append(f"  {fname} — async def {func}() has no await")

# 12. Check for import sound_manager inside try/except (good pattern)
# 13. Check for missing self. initialization
for fname in ['main.py', 'lobby.py', 'menu.py', 'scenes.py']:
    path = os.path.join(PROJECT, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for common typos
    if 'self.sounds_manager' in content:
        issues.append(f"  {fname} — Typo: self.sounds_manager (should be sound_manager)")
    if 'self.screen = None' in content and 'self.screen = pygame' not in content:
        issues.append(f"  {fname} — self.screen initialized to None but never set")

# 14. Check for unclosed file handles
for fname in py_files:
    path = os.path.join(PROJECT, fname)
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if 'open(' in line and 'with ' not in line and not line.strip().startswith('#'):
                issues.append(f"  {fname}:{i} — Possible unclosed file handle: {line.strip()[:80]}")

print(f"Files scanned: {len(py_files)}")
if issues:
    print(f"\n⚠️ {len(issues)} potential issues found:")
    for issue in sorted(set(issues)):
        print(issue)
else:
    print("\n✅ No issues detected.")
