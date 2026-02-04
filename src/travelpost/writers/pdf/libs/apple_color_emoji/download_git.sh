#!/usr/bin/env sh
set -e -x

OWNER="samuelngs"
REPO="apple-emoji-linux"
SRC_DIR="png/160"
REF="562e944da37e11782844d066e02f31ccde99b5db"  # branch, commit, tag
TAR_DIR="lib/apple_color_emoji"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Checkout (sparse) of https://github.com/$OWNER/$REPO.git"
git clone --depth 1 --filter=blob:none --sparse "https://github.com/$OWNER/$REPO.git" "$TMP"
git -C "$TMP" sparse-checkout set "$SRC_DIR"
git -C "$TMP" checkout "$REF"

DEST="$TAR_DIR/$SRC_DIR"
echo "Copying $SRC_DIR to $DEST ..."
mkdir -p "$DEST"
cp -R "$TMP/$SRC_DIR/." "$DEST/"
echo "Copied $SRC_DIR to $DEST"

echo "Creating emoji.json ..."
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
uv run python "$SCRIPT_DIR/__main__.py" --path="$DEST"
echo "Created emoji.json."
