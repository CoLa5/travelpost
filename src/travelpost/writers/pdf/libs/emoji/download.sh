#!/usr/bin/env sh
set -e

OWNER="samuelngs"
REPO="apple-emoji-linux"
SRC_DIR="png/160"
REF="562e944da37e11782844d066e02f31ccde99b5db"  # branch, commit, tag
TAR_DIR="lib/emoji"

URL="https://api.github.com/repos/$OWNER/$REPO/contents/$SRC_DIR?ref=$REF"

DEST="$TAR_DIR/$SRC_DIR"
mkdir -p "$DEST"

curl -s "$URL" | \
  awk -F'"' '/"download_url":/ { print $4 }' | \
  while read -r url; do
    curl -L "$url" -o "$DEST/$(basename "$url")"
  done

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
uv run python "$SCRIPT_DIR/__main__.py" --path="$DEST"
