import argparse
import shutil
import sys

from utils import RESULTS, run_logged

PROMPTS = {
    "Factual": "What is the difference between a Python list and a tuple? Give a short example of each.",
    "Explain to a 12-year-old": "Explain how public-key encryption works to a 12-year-old using an analogy.",
    "Creative": "Write a short story about a librarian who discovers a door to the moon.",
}


def main() -> None:
    """Ask a local Ollama model the three prompts and save its responses."""
    parser = argparse.ArgumentParser(
        description="Run the three Ollama exercise prompts locally."
    )
    parser.add_argument(
        "--model", default="gemma3:1b", help="Ollama model (default: gemma3:1b)"
    )
    args = parser.parse_args()

    if not shutil.which("ollama"):
        sys.exit(
            "Ollama is not installed or not on PATH. See https://ollama.com/download."
        )

    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "exercise_2.txt").open("w", encoding="utf-8") as log:
        for kind, prompt in PROMPTS.items():
            header = (
                f"\n=== {kind} ===\nModel: {args.model}\nPrompt: {prompt}\nResponse:"
            )
            print(header, flush=True)
            print(header, file=log, flush=True)
            if run_logged(["ollama", "run", args.model, prompt], log) != 0:
                sys.exit(
                    "Ollama failed. Check that its service is running and the model is available."
                )

    print("\nTake a screenshot and review the responses for your written comparison.")


if __name__ == "__main__":
    main()
