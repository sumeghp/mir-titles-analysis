#!/usr/bin/env bash
# Re-download the collection search export (data/ia.json) and identifier list (data/ids.txt)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
curl -s -m 300 "https://archive.org/advancedsearch.php?q=collection%3Amir-titles&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=creator&fl%5B%5D=date&fl%5B%5D=year&fl%5B%5D=language&fl%5B%5D=subject&fl%5B%5D=publisher&fl%5B%5D=downloads&fl%5B%5D=addeddate&fl%5B%5D=description&rows=10000&output=json" -o "$ROOT/data/ia.json"
python3 -c "import json,sys;[print(d['identifier']) for d in json.load(open(sys.argv[1]))['response']['docs']]" "$ROOT/data/ia.json" > "$ROOT/data/ids.txt"
