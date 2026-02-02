#!/usr/bin/env sh
set -e

VERSION="7.1.0"
FILE="fontawesome-free-${VERSION}-desktop"
ZIP="${FILE}.zip"
URL="https://use.fontawesome.com/releases/v${VERSION}/${ZIP}"
SHA256="42eb48ede199f7a9e4944398b6a4acf07e37897d99a634021e17574ad83590cf"
TARGET_DIR="lib/fontawesome"

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
cp -R "$TMP/$FILE/$FILE/." "$TARGET_DIR/"

echo "Script finished successfully."
