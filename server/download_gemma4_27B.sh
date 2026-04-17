#!/bin/bash
# Download Gemma 4 26B-A4B UD-Q5_K_M from Unsloth (public repo, no token needed)
# ~21.2 GB — run on login node (has internet access)

set -e

DEST=~/.cache/llama.cpp
mkdir -p "$DEST"
OUT="$DEST/unsloth_gemma-4-26B-A4B-it-GGUF_UD-Q5_K_M.gguf"
URL="https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/resolve/main/gemma-4-26B-A4B-it-UD-Q5_K_M.gguf"

if [ -f "$OUT" ]; then
    echo "Already downloaded: $OUT"
    ls -lh "$OUT"
    exit 0
fi

echo "Downloading Gemma 4 26B-A4B UD-Q5_K_M (~21.2 GB) ..."
echo "Source: unsloth/gemma-4-26B-A4B-it-GGUF (public)"
echo ""
wget -c "$URL" -O "$OUT" --progress=dot:giga 2>&1

echo ""
echo "Done: $OUT"
ls -lh "$OUT"
