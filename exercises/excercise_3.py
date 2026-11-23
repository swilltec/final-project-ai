import sys
from typing import TextIO

from utils import REPO, RESULTS, prepare_nanogpt, record, run_logged


def run_sample(title: str, options: list[str], log: TextIO) -> None:
    """Generate a nanoGPT sample and save the output."""
    record(f"\n=== {title} ===\n", log)
    command = [
        sys.executable,
        "-u",
        "sample.py",
        "--init_from=gpt2",
        "--device=cpu",
        "--dtype=float32",
        *options,
    ]
    if run_logged(command, log, cwd=REPO) != 0:
        sys.exit("nanoGPT sampling failed; see results/exercise_3.txt.")


def main() -> None:
    """Generate the course samples and compare two temperatures."""
    prepare_nanogpt()
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "exercise_3.txt").open("w", encoding="utf-8") as log:
        run_sample(
            "Course prompt, temperature 0.8",
            [
                "--start=Artificial intelligence will",
                "--num_samples=2",
                "--max_new_tokens=100",
                "--temperature=0.8",
                "--top_k=50",
            ],
            log,
        )
        # Keep the prompt and top-k fixed so temperature is the changing setting.
        for temperature in ("0.3", "1.2"):
            run_sample(
                f"Own prompt, temperature {temperature}",
                [
                    "--start=A scientist opened the mysterious box and",
                    "--num_samples=1",
                    "--max_new_tokens=100",
                    f"--temperature={temperature}",
                    "--top_k=50",
                ],
                log,
            )

        for number, line in enumerate(
            (REPO / "sample.py").read_text(encoding="utf-8").splitlines(), 1
        ):
            if "model.generate(" in line:
                message = f"\nGeneration call, sample.py:{number}: {line.strip()}\n"
                print(message)
                log.write(message)

    print("Review the saved samples for your written comparison.")


if __name__ == "__main__":
    main()
