#!/usr/bin/env sh
set -e

VERSION="7.5.0"
FILE="v${VERSION}"
ZIP="${FILE}.zip"
URL="https://github.com/lipis/flag-icons/archive/refs/tags/${ZIP}"
SHA256="7eafedfc07e16ce640dd53309fbe147be0dcfd36d027646cf3798aea79a18913"
TARGET_DIR="lib/flag-icons"

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
cp -R "$TMP/$FILE/flag-icons-$VERSION/flags/." "$TARGET_DIR/flags/"
cp "$TMP/$FILE/flag-icons-$VERSION/country.json" "$TARGET_DIR/country.json"

echo "Script finished successfully."
