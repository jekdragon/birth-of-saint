import subprocess, sys, os, time

os.chdir("E:/birth-of-saint")
sys.path.insert(0, "E:/birth-of-saint")

result = subprocess.run(
    [sys.executable, "main.py"],
    capture_output=True,
    text=True,
    timeout=8,
    cwd="E:/birth-of-saint"
)

with open("E:/birth-of-saint/_test_output.txt", "w") as f:
    f.write(f"RETURN CODE: {result.returncode}\n")
    f.write(f"STDOUT ({len(result.stdout)} chars):\n{result.stdout[:2000]}\n")
    f.write(f"STDERR ({len(result.stderr)} chars):\n{result.stderr[:2000]}\n")
print("DONE")
