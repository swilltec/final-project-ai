import gc
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TextIO

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPO = ROOT / "downloads" / "nanoGPT"
COURSE_COMMIT = "3adf61e1"


def record(message: str, log: TextIO) -> None:
    """Show a message and save it to the exercise transcript."""
    print(message, flush=True)
    print(message, file=log, flush=True)


def prepare_nanogpt() -> None:
    """Clone nanoGPT when needed and verify the course's fixed revision."""
    if not REPO.exists():
        REPO.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "https://github.com/karpathy/nanoGPT.git", str(REPO)],
            check=True,
        )
        subprocess.run(["git", "checkout", COURSE_COMMIT], cwd=REPO, check=True)
    if any(not (REPO / name).is_file() for name in ("sample.py", "train.py")):
        sys.exit("The nanoGPT checkout is incomplete; move it aside and try again.")
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()
    if not commit.startswith(COURSE_COMMIT):
        sys.exit(f"nanoGPT is not at course commit {COURSE_COMMIT}.")


def prepare_resources() -> None:
    """Download the models, tokenizer, and dataset used by the exercises."""
    import tiktoken
    from transformers import GPT2LMHeadModel, pipeline

    prepare_nanogpt()

    # Load the exact models used by the scripts so their weights and tokenizers
    # are available in the Hugging Face cache before the exercises run.
    for task, model in (
        (
            "sentiment-analysis",
            "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
        ),
        ("fill-mask", "FacebookAI/roberta-base"),
        ("text-generation", "openai-community/gpt2"),
    ):
        print(f"Preparing {model}...", flush=True)
        model_pipeline = pipeline(task, model=model, device=-1)
        del model_pipeline
        gc.collect()

    # nanoGPT requests GPT-2 under this separate Hugging Face model name.
    print("Preparing nanoGPT's GPT-2 checkpoint and tokenizer...", flush=True)
    gpt2 = GPT2LMHeadModel.from_pretrained("gpt2")
    del gpt2
    gc.collect()
    tiktoken.get_encoding("gpt2")

    # An interrupted download can leave an empty input file that nanoGPT reuses.
    dataset = REPO / "data" / "shakespeare"
    input_file = dataset / "input.txt"
    if input_file.exists() and input_file.stat().st_size == 0:
        sys.exit(
            "The Shakespeare input is empty. Move it aside before retrying preparation."
        )
    if any(
        not (dataset / name).is_file() or (dataset / name).stat().st_size == 0
        for name in ("train.bin", "val.bin")
    ):
        print("Preparing Tiny Shakespeare...", flush=True)
        subprocess.run(
            [sys.executable, "data/shakespeare/prepare.py"], cwd=REPO, check=True
        )
    if any(
        not (dataset / name).is_file() or (dataset / name).stat().st_size == 0
        for name in ("train.bin", "val.bin")
    ):
        sys.exit(
            "Shakespeare preparation produced an empty dataset; check the download."
        )

    if not shutil.which("ollama"):
        sys.exit(
            "Python resources are ready, but Ollama is not installed. Install it from "
            "https://ollama.com/download, start its service, and rerun prepare.sh."
        )
    print("Preparing Ollama's gemma3:1b model...", flush=True)
    subprocess.run(["ollama", "pull", "gemma3:1b"], check=True)


def run_logged(command: list[str], log: TextIO, *, cwd: Path | None = None) -> int:
    """Stream stdout and stderr to the terminal and transcript; return the exit code."""
    process = subprocess.Popen(
        command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    assert process.stdout is not None
    try:
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
        return process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        raise


if __name__ == "__main__":
    prepare_resources()
