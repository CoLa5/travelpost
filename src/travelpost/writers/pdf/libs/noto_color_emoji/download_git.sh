#!/usr/bin/env sh
set -e -x

OWNER="googlefonts"
REPO="noto-emoji"
SRC_DIRS=("svg" "third_party/region-flags/waved-svg")
REF="8998f5dd683424a73e2314a8c1f1e359c19e8742"  # v2.051
TAR_DIR="lib/noto_color_emoji"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Checkout (sparse) of https://github.com/$OWNER/$REPO.git"
git clone --depth 1 --filter=blob:none --sparse "https://github.com/$OWNER/$REPO.git" "$TMP"
git -C "$TMP" sparse-checkout set "${SRC_DIRS[@]}"
git -C "$TMP" checkout "$REF"

for src_dir in "${SRC_DIRS[@]}"; do
    DEST="$TAR_DIR/$src_dir"
    echo "Copying $src_dir to $DEST ..."
    mkdir -p "$DEST"
    cp -R "$TMP/$src_dir/." "$DEST/"
    echo "Copied $src_dir to $DEST"
done

echo "Creating emoji.json ..."
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
uv run python "$SCRIPT_DIR/__main__.py" --path="$DEST"
echo "Created emoji.json."
