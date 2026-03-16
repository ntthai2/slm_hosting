#!/usr/bin/env bash
# Download model once — run this BEFORE docker compose up
# Usage: bash scripts/download_model.sh

set -euo pipefail

MODEL_ID="Qwen/Qwen2.5-1.5B-Instruct-AWQ"
TARGET_DIR="./models/Qwen2.5-1.5B-Instruct-AWQ"

echo "==> Checking huggingface_hub..."
if ! python -c "import huggingface_hub" &>/dev/null; then
    echo "Installing huggingface_hub..."
    pip install -q huggingface_hub
fi

if [ -d "$TARGET_DIR" ] && [ "$(ls -A "$TARGET_DIR")" ]; then
    echo "==> Model already exists at $TARGET_DIR — skipping download."
    exit 0
fi

echo "==> Downloading $MODEL_ID to $TARGET_DIR ..."
mkdir -p ./models
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='$MODEL_ID',
    local_dir='$TARGET_DIR',
    local_dir_use_symlinks=False
)
"

echo "==> Download complete: $TARGET_DIR"
ls -lh "$TARGET_DIR"