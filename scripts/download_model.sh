#!/usr/bin/env bash
# Download model once — run this BEFORE docker compose up
# Usage: bash scripts/download_model.sh

set -euo pipefail

MODEL_ID="Qwen/Qwen2.5-1.5B-Instruct-AWQ"
TARGET_DIR="./models/Qwen2.5-1.5B-Instruct-AWQ"

echo "==> Checking huggingface-cli..."
if ! command -v huggingface-cli &>/dev/null; then
    echo "Installing huggingface_hub..."
    pip install -q huggingface_hub
fi

if [ -d "$TARGET_DIR" ] && [ "$(ls -A "$TARGET_DIR")" ]; then
    echo "==> Model already exists at $TARGET_DIR — skipping download."
    exit 0
fi

echo "==> Downloading $MODEL_ID to $TARGET_DIR ..."
mkdir -p ./models
huggingface-cli download "$MODEL_ID" \
    --local-dir "$TARGET_DIR" \
    --local-dir-use-symlinks False

echo "==> Download complete: $TARGET_DIR"
ls -lh "$TARGET_DIR"
