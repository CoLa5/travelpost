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

cp -R "$TMP/ne/." "$TARGET_DIR/"
