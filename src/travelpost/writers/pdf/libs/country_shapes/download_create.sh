#!/usr/bin/env sh
set -e

SCALE=10m
THEME="cultural"
VERSION="5.1.2"
FILE="ne_${SCALE}_admin_0_countries"
ZIP="${FILE}.zip"
URL="https://naciscdn.org/naturalearth/${VERSION}/${SCALE}/${THEME}/${ZIP}"
SHA256="ce1ac7036499a0edd641fbc093cd209a98f96a49d2eca8480aaacad35138a7f6"
TARGET_DIR="lib/natural_earth_data"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TARGET_DIR"

echo "Downloading $ZIP ..."
curl -L "$URL" -o "$TMP/$ZIP"

echo "Verifying hash ..."
ACTUAL_SHA256=$(sha256sum "$TMP/$ZIP" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$SHA256" ]; then
    echo "Hash mismatch, file may be corrupted!"
    exit 1
fi
echo "Hash verified successfully."

echo "Unzipping $ZIP ..."
unzip -q "$TMP/$ZIP" -d "$TMP/$FILE"

echo "Copying files ..."
cp -R "$TMP/$FILE/." "$TARGET_DIR/"

echo "Creating SVGs ..."
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
uv run python "$SCRIPT_DIR/creator/__main__.py" \
  --export-all \
  --height=600 \
  --padding=16 \
  --oversampling=4 \
  --shp-path="$TARGET_DIR/$FILE.shp" \
  --out="$TARGET_DIR"
echo "Created SVGs."
