#!/usr/bin/env sh
set -e

VERSION="7.5.0"
URL="https://github.com/lipis/flag-icons/archive/refs/tags/v$VERSION.zip"
TARGET_DIR="lib/flag-icons"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TARGET_DIR"

curl -L "$URL" -o "$TMP/fi.zip"
unzip -q "$TMP/fi.zip" -d "$TMP"

cp -R "$TMP/flag-icons-$VERSION/flags/." "$TARGET_DIR/flags/"
cp "$TMP/flag-icons-$VERSION/country.json" "$TARGET_DIR/country.json"
