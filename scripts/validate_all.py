from pathlib import Path
import subprocess
import sys

VALIDATORS = [
    Path("scripts/validate_knowledge.py"),
    Path("scripts/validate_relationships.py"),
    Path("scripts/validate_canon_rules.py"),
]

failed = False

for validator in VALIDATORS:
    print(f"\nRunning {validator}...")
    result = subprocess.run(
        [sys.executable, str(validator)],
        check=False,
    )

    if result.returncode != 0:
        failed = True

if failed:
    print("\nNumeria validation failed.")
    sys.exit(1)

print("\nAll Numeria validations passed.")
