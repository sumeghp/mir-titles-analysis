#!/usr/bin/env bash
# Download per-item metadata for every identifier in data/ids.txt into data/item_meta/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/data/item_meta"
fetch() { out="$ROOT/data/item_meta/$1.json"; [ -s "$out" ] || curl -s -m 60 --retry 3 "https://archive.org/metadata/$1" -o "$out"; }
export -f fetch; export ROOT
xargs -P 16 -n 1 -I{} bash -c 'fetch "$@"' _ {} < "$ROOT/data/ids.txt"
