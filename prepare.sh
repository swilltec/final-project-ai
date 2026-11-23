#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v ollama >/dev/null 2>&1; then
    if [[ "$(uname -s)" != "Linux" ]]; then
        echo 'Automatic Ollama installation is supported on Linux only. Install Ollama from https://ollama.com/download.' >&2
        exit 1
    fi
    echo 'Installing Ollama using its official Linux installer (sudo may be required)...'
    curl -fsSL https://ollama.com/install.sh | sh
    if ! command -v ollama >/dev/null 2>&1; then
        echo 'Ollama installation did not make the command available on PATH.' >&2
        exit 1
    fi
fi

# Reuse an existing service, or start one for this user when needed.
if ! ollama list >/dev/null 2>&1; then
    mkdir -p excecises/downloads
    ollama serve >excecises/downloads/ollama.log 2>&1 &
    ollama_pid=$!
    for attempt in {1..30}; do
        if ollama list >/dev/null 2>&1; then
            break
        fi
        if ! kill -0 "$ollama_pid" 2>/dev/null; then
            echo 'Ollama failed to start. See excecises/downloads/ollama.log.' >&2
            exit 1
        fi
        sleep 1
    done
    if ! ollama list >/dev/null 2>&1; then
        echo 'Ollama did not become ready. See excecises/downloads/ollama.log.' >&2
        exit 1
    fi
fi

python3 -m venv .venv
.venv/bin/python -m pip install 'torch==2.6.0' --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m excecises.utils
echo 'Ready. Activate with: source .venv/bin/activate'
