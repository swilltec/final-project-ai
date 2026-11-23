import subprocess
import sys
from pathlib import Path

EXERCISES = Path(__file__).resolve().parent / "excecises"


def main() -> int:
    """Run each exercise in order and report any that did not complete."""
    failed = []
    for number in range(1, 5):
        print(f"\n=== Exercise {number} ===", flush=True)
        script = EXERCISES / f"excercise_{number}.py"
        # A missing model or a failed exercise should not prevent the others from running.
        result = subprocess.run([sys.executable, str(script)], check=False)
        if result.returncode != 0:
            failed.append(number)
            print(
                f"Exercise {number} exited with status {result.returncode}.", flush=True
            )

    if failed:
        print(f"\nExercises that did not complete: {', '.join(map(str, failed))}.")
        return 1
    print("\nAll exercises completed. Review the saved results and write-ups.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
