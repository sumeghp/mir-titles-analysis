"""Match the same work across English and Indian-language editions and build a language network.

Indian-language items in the collection usually carry the English title in brackets,
e.g. "... (All About The Telescope In Tamil)". We normalise that bracketed English title and
the titles of English items, and treat identical normalised titles as the same work.
French, Spanish and other titles are not matched (they carry no English title).

Outputs: results/tables/t10_multilingual_works.csv, t11_language_pairs.csv,
         results/figures/fig5_language_network.{png,svg}, results/summary_network.json
"""
import csv, collections as C, itertools, json, math, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "master_classified.csv"))))
INDIAN = {"Hindi", "Bengali", "Tamil", "Marathi", "Telugu", "Gujarati", "Kannada", "Odia", "Urdu",
          "Malayalam", "Punjabi", "Assamese", "Nepali"}
GENERIC = {"stories", "stories for children", "story", "selected works", "selected stories", "collected stories",
           "three tales", "friends", "picture stories", "short novels and stories"}


def key(r):
    t = r["title"]
    if r["language"] != "English":
        m = re.findall(r"\(([^()]*[A-Za-z][^()]*)\)", t)
        if not m:
            return None
        t = m[-1]
    t = t.lower()
    t = re.sub(r"\b(in|en)\s+(hindi|bengali|bangla|tamil|telugu|marathi|gujarati|kannada|odia|oriya|urdu|"
               r"malayalam|punjabi|assamese|nepali)\b", "", t)
    t = re.sub(r"\s[–-]\s.*$", "", t)
    t = re.sub(r"\b(volume|vol|part|book)\s*\d+\b", "", t)
    t = re.sub(r"^(the|a)\s+", "", t)
    t = re.sub(r"[^a-z ]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) > 6 and t not in GENERIC else None


works = C.defaultdict(set)
dom = {}
for r in rows:
    if r["language"] in INDIAN or r["language"] == "English":
        k = key(r)
        if k:
            works[k].add(r["language"])
            dom.setdefault(k, set()).add(r["domain"])
multi = {k: v for k, v in works.items() if len(v) > 1 and (v & INDIAN)}
SCI = {"popular_science", "science_technical"}
is_sci = {k: bool(dom[k] & SCI) for k in multi}

tdir = os.path.join(ROOT, "results", "tables")
with open(os.path.join(tdir, "t10_multilingual_works.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["work_key", "n_languages", "languages", "science"])
    for k, v in sorted(multi.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        w.writerow([k, len(v), "; ".join(sorted(v)), int(is_sci[k])])
E = C.Counter()
for k, v in multi.items():
    for a, b in itertools.combinations(sorted(v), 2):
        E[(a, b)] += 1
with open(os.path.join(tdir, "t11_language_pairs.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["lang_a", "lang_b", "shared_works"])
    for (a, b), n in E.most_common():
        w.writerow([a, b, n])

summ = {
    "multilingual_works": len(multi),
    "science_share_pct": round(100 * sum(is_sci.values()) / len(multi), 1),
    "mean_languages": round(sum(len(v) for v in multi.values()) / len(multi), 2),
    "top_science_works": [(k, len(v)) for k, v in sorted(multi.items(), key=lambda kv: -len(kv[1])) if is_sci[k]][:8],
    "top_works": [(k, len(v)) for k, v in sorted(multi.items(), key=lambda kv: -len(kv[1]))][:8],
    "top_pairs": [(a + "–" + b, n) for (a, b), n in E.most_common(8)],
}
json.dump(summ, open(os.path.join(ROOT, "results", "summary_network.json"), "w"), indent=2)
print(json.dumps(summ, indent=2))

# Figure: circular language network, edge width = shared works, node size = works in that language
langs = sorted({l for v in multi.values() for l in v}, key=lambda l: -sum(1 for v in multi.values() if l in v))
deg = {l: sum(1 for v in multi.values() if l in v) for l in langs}
n = len(langs)
pos = {l: (math.cos(2 * math.pi * i / n + math.pi / 2), math.sin(2 * math.pi * i / n + math.pi / 2)) for i, l in enumerate(langs)}
fig, ax = plt.subplots(figsize=(6.4, 6.4))
mx = max(E.values())
for (a, b), c in sorted(E.items(), key=lambda kv: kv[1]):
    xa, ya = pos[a]
    xb, yb = pos[b]
    ax.plot([xa, xb], [ya, yb], color="#c0262d", alpha=0.15 + 0.75 * c / mx, linewidth=0.4 + 5 * c / mx,
            solid_capstyle="round", zorder=1)
for l in langs:
    x, y = pos[l]
    ax.scatter([x], [y], s=40 + deg[l] * 6, color="#0b0b0b" if l == "English" else "#52514e", zorder=3,
               edgecolors="white", linewidths=1.5)
    ax.text(x * 1.3, y * 1.3, f"{l}\n{deg[l]}", ha="center", va="center", fontsize=8.5, color="#0b0b0b")
ax.set_xlim(-1.55, 1.55)
ax.set_ylim(-1.55, 1.6)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(f"Fig. 5  Shared works across English and Indian languages\n({len(multi)} works found in two or more languages; "
             "line weight = works shared by a pair;\nnumber = multilingual works in that language)",
             fontsize=9.5, loc="left", fontweight="bold")
fdir = os.path.join(ROOT, "results", "figures")
fig.savefig(os.path.join(fdir, "fig5_language_network.png"), dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(os.path.join(fdir, "fig5_language_network.svg"), bbox_inches="tight", facecolor="white")
