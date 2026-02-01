#!/usr/bin/env sh
set -e

VERSION="5.1.2"
URL="https://naciscdn.org/naturalearth/${VERSION}/10m/cultural/ne_10m_admin_0_countries.zip"
TARGET_DIR="lib/natural_earth_data"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TARGET_DIR"

curl -L "$URL" -o "$TMP/ne.zip"
unzip -q "$TMP/ne.zip" -d "$TMP/ne"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
uv run python "$SCRIPT_DIR/creator/__main__.py" \
  --export-all \
  --height=600 \
  --padding=16 \
  --oversampling=4 \
  --shp-path="$TMP/ne/ne_10m_admin_0_countries.shp" \
  --out="$TARGET_DIR"
