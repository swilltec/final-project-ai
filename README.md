# Final AI Project: Set F

This final AI project explores pretrained transformers and local language models through four exercises. It uses Hugging Face pipelines for sentiment analysis, masked-word prediction, and text generation; Ollama for local prompting; and nanoGPT to inspect generation and fine-tune GPT-2 on Shakespeare. The fourth exercise is an optional bonus.

The scripts use CPU by default. Initial setup needs an internet connection and several gigabytes of free space for dependencies and models. Model generation and fine-tuning may take time on a CPU.

## Getting started

Install Python 3, pip, and Git first. On Ubuntu, you also need `venv` and `curl`. Run the appropriate preparation script from the project root:

**Ubuntu**

```bash
bash prepare.sh
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.\prepare.ps1
.\.venv\Scripts\Activate.ps1
```

Preparation creates `.venv`, installs the Python dependencies, installs Ollama if it is missing, and starts its service if needed. It downloads the Hugging Face models, the Gemma 3 Ollama model, the project's pinned nanoGPT version, and the Tiny Shakespeare dataset. The Ubuntu Ollama installer may request your sudo password. On Windows, you may need to reopen your terminal if Ollama is not immediately available on `PATH`.

## Running the exercises

After activating the virtual environment, run all four exercises in order:

```bash
python main.py
```

The runner continues if an exercise fails and reports failures at the end. To run an exercise individually, use its script from the project root:

```bash
python exercises/excercise_1.py
python exercises/excercise_2.py
python exercises/excercise_3.py
python exercises/excercise_4.py
```

Each exercise saves its output to `exercises/results/`. A fresh run replaces that exercise's transcript; the exercise 4 `--sample-only` option appends to it. Review the actual output and prepare your own written answers and screenshot for submission.

### 1. Transformer pipelines

The first script classifies three sentences, including a sarcastic one; predicts three possible words for each of two masks; and generates continuations for two prompts. Use `exercises/results/exercise_1.txt` to assess whether the confidence reflects the sarcasm and compare the coherence and relevance of the generated text. In 4–5 sentences, connect the fill-mask predictions to attention and identify which context words might have helped. Those interpretations are hypotheses rather than measured attention weights.

### 2. Local language model

The Ollama script asks a factual question about Python, requests an explanation for a 12-year-old, and makes a creative request. Change the factual prompt in the script if another topic is more familiar. If `gemma3:1b` is too slow or needs too much memory, use the smaller alternative:

```bash
ollama pull qwen3:0.6b
python exercises/excercise_2.py --model qwen3:0.6b
```

Keep a screenshot showing Ollama running locally and identify a useful and a limited response from `exercises/results/exercise_2.txt`. In 3–5 sentences, discuss what the model did well and where it struggled, and state one privacy advantage of local inference.

### 3. nanoGPT generation

The third script generates two samples for the initial prompt and compares temperatures 0.3 and 1.2 on another prompt. The samples and the line that calls `model.generate` are saved in `exercises/results/exercise_3.txt`. Inspect `exercises/downloads/nanoGPT/sample.py` to see how the prompt and sampling settings are used. Compare the temperature outputs and, in 3–4 sentences, explain which interface is easier to use and which makes generation easier to inspect: nanoGPT or the Hugging Face pipeline.

### 4. Bonus: fine-tune on Shakespeare

The bonus script prepares Tiny Shakespeare, generates a baseline for `ROMEO:`, fine-tunes GPT-2 for 20 CPU iterations, and samples the checkpoint using the same prompt. The transcript and printed training and validation losses are saved in `exercises/results/exercise_4.txt`.

If training is interrupted after nanoGPT has saved a checkpoint, append a sample from it with:

```bash
python exercises/excercise_4.py --sample-only
```

If a checkpoint is available, training can be stopped after 10 iterations. To start a new training run, first move the existing `exercises/downloads/nanoGPT/out-shakespeare/ckpt.pt` elsewhere; the script will not overwrite it silently. Compare the baseline and fine-tuned samples for vocabulary, character names, formatting, and style. Record the final printed losses and explain the observed changes in 3–5 sentences, distinguishing broad pretraining from fine-tuning on a smaller dataset. A short run may show little change.

## Cleanup

Use a system Python, rather than the project's virtual environment, to run cleanup:

```bash
# Ubuntu
python3 cleanup.py
```

```powershell
# Windows
py -3 cleanup.py
```

The script separately asks whether to remove the project environment and downloads and whether to uninstall Ollama. Project cleanup also removes nanoGPT checkpoints. Exercise results and shared model caches are kept; uninstalling Ollama also keeps its shared model data. Standard Linux installations and Windows installations recognized by `winget` are supported; other installations may need to be removed through their package manager or Windows Settings.

## References

- [Introduction to Artificial Intelligence course materials](https://materiaalit.github.io/intro-to-ai/week5/)
- [Hugging Face Transformers pipeline documentation](https://huggingface.co/docs/transformers/main/en/main_classes/pipelines)
- [Ollama documentation](https://docs.ollama.com/) and [Gemma 3 model page](https://ollama.com/library/gemma3)
- [nanoGPT repository](https://github.com/karpathy/nanoGPT), used at commit `3adf61e1`
- [GPT-2 model card](https://huggingface.co/openai-community/gpt2)
- [Tiny Shakespeare dataset](https://github.com/karpathy/char-rnn/blob/master/data/tinyshakespeare/input.txt)
