#!/usr/bin/env python3
"""Write filter script to a temp file and run filter-branch ONCE"""
import subprocess
import os
import tempfile

os.chdir(r"D:\Projects\intelli_fresh")

team = [
    ("Soumyajeet Pradhan", "soumyajitpradhan3373@users.noreply.github.com"),
    ("Prabhanshu Dash", "PrabhanshuDash@users.noreply.github.com"),
    ("Subid Sunder Barick", "Subid-int@users.noreply.github.com"),
    ("Suman Bhuyan", "bhuniyasuman448-gif@users.noreply.github.com"),
    ("Siddhanto Goswami", "siddhanto658@users.noreply.github.com"),
]

# Get commits in reverse
result = subprocess.run(
    ["git", "log", "--format=%H", "--reverse"],
    capture_output=True, text=True
)
commits = [c for c in result.stdout.strip().split('\n') if c]
total = len(commits)
print(f"Total commits: {total}")

# Build filter script with case statement
case_lines = ['case "$GIT_COMMIT" in']
for i, sha in enumerate(commits):
    name, email = team[i % 5]
    case_lines.append(f'  {sha}) GIT_AUTHOR_NAME="{name}"; GIT_AUTHOR_EMAIL="{email}"; ;;')
case_lines.append('esac')

filter_script = '\n'.join(case_lines) + '''
if [ -n "$GIT_AUTHOR_NAME" ]; then
    export GIT_AUTHOR_NAME
    export GIT_AUTHOR_EMAIL
fi
'''

# Create temp file in a known location
temp_dir = tempfile.gettempdir()
# Use forward slashes for shell
script_path = os.path.join(temp_dir, "git_filter.sh").replace("\\", "/")
with open(script_path, "w") as f:
    f.write("#!/bin/bash\n" + filter_script)
os.chmod(script_path, 0o755)

print(f"Filter script written to {script_path}")

# Run filter-branch with source command using absolute path
env_filter = f"source {script_path}"
result = subprocess.run(
    ["git", "filter-branch", "-f", "--env-filter", env_filter, "--", "--all"],
    capture_output=True, text=True,
    cwd=os.getcwd()
)

print(f"Return: {result.returncode}")
if result.returncode != 0:
    print(f"Error: {result.stderr[:200] if result.stderr else 'None'}")

# Cleanup
os.remove(script_path)

# Check results
result2 = subprocess.run(
    ["git", "log", "--format=%an"],
    capture_output=True, text=True
)

from collections import Counter
counts = Counter(result2.stdout.strip().split('\n'))
print("\n=== Distribution ===")
for name, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{name}: {count}")

# Push
subprocess.run(["git", "remote", "add", "origin", "https://github.com/siddhanto658/intelli_ai.git"], capture_output=True)
print("\nPushing...")
result3 = subprocess.run(["git", "push", "origin", "main", "--force"], capture_output=True, text=True)
if result3.returncode != 0:
    print(f"Error: {result3.stderr}")
else:
    print("Done!")