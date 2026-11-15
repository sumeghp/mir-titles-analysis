# Mir Publishers and Science Popularisation in the Global South

Data, code and working paper for a digital-humanities study of the **Mir Titles** collection on the Internet Archive: 4,566 digitised Soviet books (Mir, Progress, Raduga, Foreign Languages Publishing House and others, mostly 1950–1991) in 25 languages, uploaded by volunteers between 2013 and 2026.

**Working paper:** [`paper/paper.pdf`](paper/paper.pdf) (version 0.1, 15 November 2026)
**Author:** Sumegh P, Independent researcher · ORCID [0000-0003-0709-2174](https://orcid.org/0000-0003-0709-2174)

## Main findings

| | |
|---|---|
| Science share of items / of downloads | 50% / 87% of 9.2 million downloads |
| Problem books | 4.9% of items, 25.1% of downloads; 11 of the top 20 titles |
| Science share by language | French 99%, Spanish 97%, English 55%, Indian languages 18% |
| Popular science as a share of science | Indian languages 70%, English 15% |
| Indian-language share of uploads | 4.8% (to 2020) → 30.9% (2021 onwards) |
| Works found in English and Indian languages | 226 multilingual works |

See [`results/findings.md`](results/findings.md) for details and caveats.

## Repository layout

```
data/
  ia.json                  Internet Archive search export for collection mir-titles (snapshot, 15 Nov 2026)
  ids.txt                  item identifiers
  master.csv               cleaned table (language, publisher, year, translators, scan credits, downloads, …)
  master_classified.csv    master table + domain classification
  validation_sample.csv    stratified 200-item sample for manual checking of the classification
scripts/
  fetch_search_export.sh   refresh ia.json and ids.txt from the Internet Archive
  fetch_item_metadata.sh   download per-item metadata (data/item_meta/, not committed)
  fetch_covers.sh          download cover thumbnails (data/covers/, not committed)
  build_master.py          build data/master.csv
  classify.py              rule-based domain classification + validation sample
  analyse_core.py          core analyses → results/tables, results/summary.json
  network.py               cross-language matching and network figure
  figures.py               paper figures → results/figures (PNG 300 dpi + SVG)
results/                   tables, figures, summaries, findings note
paper/                     working paper (Markdown source and PDF)
run_all.sh                 reproduce everything from the committed snapshot
```

## Reproduce

Requires Python 3.9+ with `matplotlib`, plus `curl` and `bash`.

```bash
./run_all.sh
```

This downloads the per-item metadata (about 55 MB) if it isn't already present, then rebuilds all tables and figures. To rebuild the PDF: `cd paper && pandoc paper.md -o paper.pdf --pdf-engine=xelatex --resource-path=.:..`

## Caveats

The collection is a curated volunteer archive (98% uploaded by one account). It records what has survived and been shared, not what was originally published. Download counts are global and specific to the Internet Archive. The classification is rule-based (about 94% accurate for science on a spot-check); formal validation is in progress. See section 6 of the paper.

## Licences

- Code (`scripts/`, `run_all.sh`): MIT, see [`LICENSE`](LICENSE)
- Derived data, figures and paper text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Source metadata: Internet Archive, collection [`mir-titles`](https://archive.org/details/mir-titles). The digitised books themselves are not included here.

## Citation

See [`CITATION.cff`](CITATION.cff).
