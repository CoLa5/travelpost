#!/usr/bin/env sh
set -e

VERSION="7.1.0"
URL="https://use.fontawesome.com/releases/v${VERSION}/fontawesome-free-${VERSION}-desktop.zip"
TARGET_DIR="lib/fontawesome"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TARGET_DIR"

curl -L "$URL" -o "$TMP/fa.zip"
unzip -q "$TMP/fa.zip" -d "$TMP"

cp -R "$TMP/fontawesome-free-${VERSION}-desktop/." "$TARGET_DIR/"
