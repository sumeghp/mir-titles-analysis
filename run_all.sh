#!/usr/bin/env bash
# Reproduce the analysis from the committed snapshot (data/ia.json).
# To refresh from the Internet Archive first, run scripts/fetch_search_export.sh.
set -euo pipefail
cd "$(dirname "$0")"
bash scripts/fetch_item_metadata.sh      # ~55 MB, skips files already present
python3 scripts/build_master.py
python3 scripts/classify.py
python3 scripts/analyse_core.py > /dev/null
python3 scripts/network.py > /dev/null
python3 scripts/figures.py
echo "Done. Tables in results/tables, figures in results/figures."
