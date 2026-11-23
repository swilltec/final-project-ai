import argparse
import sys
from typing import TextIO

from utils import REPO, RESULTS, prepare_nanogpt, record, run_logged

CHECKPOINT = REPO / "out-shakespeare" / "ckpt.pt"
DATASET = REPO / "data" / "shakespeare"


def run_step(title: str, arguments: list[str], log: TextIO) -> None:
    """Run a nanoGPT step and save its output."""
    record(f"\n=== {title} ===\n", log)
    if run_logged([sys.executable, "-u", *arguments], log, cwd=REPO) != 0:
        sys.exit(f"{title} failed; see results/exercise_4.txt.")


def main() -> None:
    """Fine-tune GPT-2 and compare samples from before and after training."""
    parser = argparse.ArgumentParser(description="Fine-tune GPT-2 on Tiny Shakespeare.")
    parser.add_argument(
        "--sample-only",
        action="store_true",
        help="Sample an existing checkpoint after an interrupted training run",
    )
    args = parser.parse_args()
    prepare_nanogpt()
    RESULTS.mkdir(exist_ok=True)

    # Refuse to mix a new baseline and training log with an older checkpoint.
    if not args.sample_only and CHECKPOINT.exists():
        sys.exit(
            "An existing Shakespeare checkpoint was found. Move it aside or use --sample-only."
        )
    input_file = DATASET / "input.txt"
    if not args.sample_only and input_file.exists() and input_file.stat().st_size == 0:
        sys.exit(
            "The Shakespeare download is empty. Move its input.txt aside and retry."
        )

    # Append after an interrupted run so its baseline and training losses are preserved.
    mode = "a" if args.sample_only else "w"
    with (RESULTS / "exercise_4.txt").open(mode, encoding="utf-8") as log:
        if not args.sample_only:
            run_step("Prepare Tiny Shakespeare", ["data/shakespeare/prepare.py"], log)
            if any(
                not (DATASET / name).is_file() or (DATASET / name).stat().st_size == 0
                for name in ("train.bin", "val.bin")
            ):
                sys.exit(
                    "Shakespeare preparation produced an empty dataset; check the download."
                )
            # Use the same prompt for the baseline and fine-tuned sample below.
            run_step(
                "Baseline",
                [
                    "sample.py",
                    "--init_from=gpt2",
                    "--device=cpu",
                    "--dtype=float32",
                    "--start=ROMEO:",
                    "--num_samples=1",
                    "--max_new_tokens=100",
                ],
                log,
            )
            # The course's small batch and short run make CPU fine-tuning practical.
            run_step(
                "Fine-tuning and losses",
                [
                    "train.py",
                    "config/finetune_shakespeare.py",
                    "--init_from=gpt2",
                    "--device=cpu",
                    "--compile=False",
                    "--dtype=float32",
                    "--block_size=128",
                    "--batch_size=1",
                    "--gradient_accumulation_steps=1",
                    "--max_iters=20",
                    "--eval_interval=10",
                    "--eval_iters=10",
                ],
                log,
            )
        if not CHECKPOINT.is_file():
            sys.exit(
                "No checkpoint found. Run training until nanoGPT saves one before sampling."
            )
        run_step(
            "Fine-tuned sample",
            [
                "sample.py",
                "--out_dir=out-shakespeare",
                "--device=cpu",
                "--dtype=float32",
                "--start=ROMEO:",
                "--num_samples=1",
                "--max_new_tokens=100",
            ],
            log,
        )
    print("Review the saved samples and losses for your written comparison.")


if __name__ == "__main__":
    main()
