"""Core analyses for the Mir Titles paper. Writes tables to results/tables/ and prints a summary.

Input: data/master_classified.csv
"""
import csv, collections as C, json, os, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "tables")
os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "master_classified.csv"))))
for r in rows:
    r["downloads"] = int(r["downloads"])
    r["year"] = int(r["year"]) if r["year"] else None
    r["added_year"] = int(r["added_year"] or 0)
SCI = {"popular_science", "science_technical"}
DOMS = ["science_technical", "popular_science", "literature", "politics_society", "other"]
summary = {}


def write(name, header, data):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(data)


def gini(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0 or sum(xs) == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * sum(xs)) - (n + 1) / n


# 1. Composition: language x domain
langs = [l for l, _ in C.Counter(r["language"] for r in rows).most_common()]
tab = []
for l in langs:
    sub = [r for r in rows if r["language"] == l]
    c = C.Counter(r["domain"] for r in sub)
    sci = sum(c[d] for d in SCI)
    tab.append([l, len(sub)] + [c[d] for d in DOMS] + [round(100 * sci / len(sub), 1)])
write("t1_language_by_domain.csv", ["language", "items"] + DOMS + ["pct_science"], tab)
summary["n_items"] = len(rows)
summary["domain_counts"] = dict(C.Counter(r["domain"] for r in rows))
summary["n_languages"] = len([l for l in langs if l != "Unknown"])

# 2. Language groups: share science
groups = ["English", "Indian languages", "French", "Spanish", "Russian"]
g = {}
for grp in groups:
    sub = [r for r in rows if r["lang_group"] == grp]
    s = sum(1 for r in sub if r["domain"] in SCI)
    g[grp] = {"items": len(sub), "science": s, "pct_science": round(100 * s / len(sub), 1)}
summary["groups"] = g

# 3. Decades by language group, science only and all
dec = list(range(1930, 2030, 10))
tab = []
for grp in groups:
    for dom_set, label in [(SCI, "science"), (None, "all")]:
        sub = [r for r in rows if r["lang_group"] == grp and r["year"] and (dom_set is None or r["domain"] in dom_set)]
        c = C.Counter(r["year"] // 10 * 10 for r in sub)
        tab.append([grp, label] + [c[d] for d in dec])
write("t2_decade_by_group.csv", ["group", "set"] + [str(d) for d in dec], tab)
yr = [r["year"] for r in rows if r["year"]]
summary["year_coverage"] = {"with_year": len(yr), "1950_1991": sum(1 for y in yr if 1950 <= y <= 1991),
                            "post_1991": sum(1 for y in yr if y > 1991)}

# 4. Downloads: by domain, concentration
tot = sum(r["downloads"] for r in rows)
tab = []
for d in DOMS:
    sub = [r["downloads"] for r in rows if r["domain"] == d]
    tab.append([d, len(sub), sum(sub), round(100 * sum(sub) / tot, 1), int(st.median(sub)), round(st.mean(sub))])
write("t3_downloads_by_domain.csv", ["domain", "items", "downloads", "pct_downloads", "median", "mean"], tab)
sci_dl = sum(r["downloads"] for r in rows if r["domain"] in SCI)
srt = sorted(rows, key=lambda r: -r["downloads"])
top20 = srt[:20]
summary["downloads"] = {
    "total": tot,
    "science_pct_items": round(100 * sum(1 for r in rows if r["domain"] in SCI) / len(rows), 1),
    "science_pct_downloads": round(100 * sci_dl / tot, 1),
    "median_science": int(st.median([r["downloads"] for r in rows if r["domain"] in SCI])),
    "median_nonscience": int(st.median([r["downloads"] for r in rows if r["domain"] not in SCI])),
    "gini_all": round(gini([r["downloads"] for r in rows]), 3),
    "top1pct_share": round(100 * sum(r["downloads"] for r in srt[: len(srt) // 100]) / tot, 1),
    "top10pct_share": round(100 * sum(r["downloads"] for r in srt[: len(srt) // 10]) / tot, 1),
    "top20_science": sum(1 for r in top20 if r["domain"] in SCI),
}
write("t4_top50_downloads.csv", ["rank", "title", "language", "domain", "publisher", "year", "downloads", "added_year"],
      [[i + 1, r["title"], r["language"], r["domain"], r["publisher"], r["year"], r["downloads"], r["added_year"]]
       for i, r in enumerate(srt[:50])])
# downloads per year online (controls for upload date)
for r in rows:
    yrs_online = max(1, 2026 - r["added_year"] + 1) if r["added_year"] else None
    r["dl_per_year"] = r["downloads"] / yrs_online if yrs_online else None
for d in DOMS:
    vals = [r["dl_per_year"] for r in rows if r["domain"] == d and r["dl_per_year"] is not None]
    summary.setdefault("median_dl_per_year_online", {})[d] = round(st.median(vals))
# downloads by language group, science only
summary["science_downloads_by_group"] = {
    grp: {"items": sum(1 for r in rows if r["lang_group"] == grp and r["domain"] in SCI),
          "median_dl_per_year": round(st.median([r["dl_per_year"] for r in rows if r["lang_group"] == grp and r["domain"] in SCI and r["dl_per_year"]] or [0]))}
    for grp in groups}

# 5. Uploads by year x domain (digital afterlife)
ys = sorted({r["added_year"] for r in rows if r["added_year"]})
tab = []
for y in ys:
    c = C.Counter(r["domain"] for r in rows if r["added_year"] == y)
    cl = C.Counter(r["lang_group"] for r in rows if r["added_year"] == y)
    tab.append([y, sum(c.values())] + [c[d] for d in DOMS] + [cl["English"], cl["Indian languages"], cl["French"], cl["Spanish"]])
write("t5_uploads_by_year.csv", ["year", "items"] + DOMS + ["English", "Indian languages", "French", "Spanish"], tab)
up = C.Counter(r["uploader"] for r in rows)
summary["uploaders"] = {"n": len(up), "top_share_pct": round(100 * up.most_common(1)[0][1] / len(rows), 1)}
early = [r for r in rows if r["added_year"] and r["added_year"] <= 2020]
late = [r for r in rows if r["added_year"] >= 2021]
summary["upload_shift"] = {
    "to_2020": {"items": len(early), "pct_science": round(100 * sum(1 for r in early if r["domain"] in SCI) / len(early), 1),
                "pct_indian": round(100 * sum(1 for r in early if r["lang_group"] == "Indian languages") / len(early), 1)},
    "from_2021": {"items": len(late), "pct_science": round(100 * sum(1 for r in late if r["domain"] in SCI) / len(late), 1),
                  "pct_indian": round(100 * sum(1 for r in late if r["lang_group"] == "Indian languages") / len(late), 1)},
}

# 6. Publishers x domain
pubs = [p for p, _ in C.Counter(r["publisher"] for r in rows).most_common()]
write("t6_publisher_by_domain.csv", ["publisher", "items"] + DOMS,
      [[p, sum(1 for r in rows if r["publisher"] == p)] + [sum(1 for r in rows if r["publisher"] == p and r["domain"] == d) for d in DOMS] for p in pubs])

# 7. Translators and scanning volunteers
tr = C.Counter(t for r in rows for t in r["translators"].split("; ") if t)
tr_sci = C.Counter(t for r in rows if r["domain"] in SCI for t in r["translators"].split("; ") if t)
write("t7_translators.csv", ["translator", "items", "science_items"], [[t, n, tr_sci[t]] for t, n in tr.most_common()])
sc = C.Counter(t for r in rows for t in r["scan_credits"].split("; ") if t)
write("t8_scan_credits.csv", ["credited_scanner", "items"], sc.most_common())
summary["translators"] = {"items_with_translator": sum(1 for r in rows if r["translators"]), "distinct": len(tr)}
summary["scan_credits"] = {"items_credited": sum(1 for r in rows if r["scan_credits"]), "distinct": len(sc)}

# 8. Indian-language science editions
ind = [r for r in rows if r["lang_group"] == "Indian languages" and r["domain"] in SCI]
write("t9_indian_language_science.csv", ["language", "year", "title", "domain", "publisher", "downloads"],
      sorted([[r["language"], r["year"], r["title"], r["domain"], r["publisher"], r["downloads"]] for r in ind], key=lambda x: (x[0], x[1] or 0)))
summary["indian_science"] = {"items": len(ind), "languages": len({r["language"] for r in ind}),
                             "by_language": dict(C.Counter(r["language"] for r in ind).most_common()),
                             "pct_1980s": round(100 * sum(1 for r in ind if r["year"] and 1980 <= r["year"] <= 1989) / max(1, sum(1 for r in ind if r["year"])), 1),
                             "popular_share_pct": round(100 * sum(1 for r in ind if r["domain"] == "popular_science") / len(ind), 1)}
eng_sci = [r for r in rows if r["lang_group"] == "English" and r["domain"] in SCI]
summary["english_science_popular_share_pct"] = round(100 * sum(1 for r in eng_sci if r["domain"] == "popular_science") / len(eng_sci), 1)

# 9. Series
summary["series"] = dict(C.Counter(r["series"] for r in rows if r["series"]))

# 10. Problem books
import re
PB = re.compile(r"problem|problemas|probl[eè]mes|exercis|olympiad|solving|questions|задач", re.I)
pb = [r for r in rows if PB.search(r["title"])]
summary["problem_books"] = {"items": len(pb), "pct_items": round(100 * len(pb) / len(rows), 1),
                            "pct_downloads": round(100 * sum(r["downloads"] for r in pb) / tot, 1),
                            "in_top20": sum(1 for r in top20 if PB.search(r["title"]))}

json.dump(summary, open(os.path.join(ROOT, "results", "summary.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(summary, indent=2, ensure_ascii=False))
