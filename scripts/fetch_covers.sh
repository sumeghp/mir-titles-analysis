#!/usr/bin/env bash
# Download cover thumbnails for every identifier in data/ids.txt into data/covers/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/data/covers"
fetch() { out="$ROOT/data/covers/$1.jpg"; [ -s "$out" ] || curl -sL -m 60 --retry 3 "https://archive.org/services/img/$1" -o "$out"; }
export -f fetch; export ROOT
xargs -P 16 -n 1 -I{} bash -c 'fetch "$@"' _ {} < "$ROOT/data/ids.txt"
