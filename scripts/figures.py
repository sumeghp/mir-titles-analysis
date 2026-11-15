"""Static figures for the Mir Titles paper (PNG 300 dpi + SVG) -> results/figures/

Colour scheme (emphasis pattern, validated with the dataviz palette checker):
  science/technical  #c0262d (Soviet red)
  popular science    #b07a00 (ochre)
  non-science        #c9c7c0 (neutral context grey)
"""
import csv, collections as C, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "figures")
os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "master_classified.csv"))))
for r in rows:
    r["downloads"] = int(r["downloads"])
    r["year"] = int(r["year"]) if r["year"] else None
    r["added_year"] = int(r["added_year"] or 0)

RED, OCHRE, GREY = "#c0262d", "#b07a00", "#c9c7c0"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
SURF = "#ffffff"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#c3c2b7", "axes.linewidth": 0.8,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left",
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
    "savefig.facecolor": SURF, "legend.frameon": False, "legend.fontsize": 8.5,
})
SCI = {"science_technical", "popular_science"}


def cat(r):
    return "tech" if r["domain"] == "science_technical" else "pop" if r["domain"] == "popular_science" else "non"


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".svg"), bbox_inches="tight")
    plt.close(fig)


def legend3(ax, loc="lower right", **kw):
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=RED, label="Science & technical"), Patch(color=OCHRE, label="Popular science"),
                       Patch(color=GREY, label="Literature, politics & other")], loc=loc, **kw)


# Fig 1: composition by language
langs = [l for l, n in C.Counter(r["language"] for r in rows).most_common() if l != "Unknown"][:16]
langs = langs[::-1]
fig, ax = plt.subplots(figsize=(7, 5.2))
for i, l in enumerate(langs):
    sub = [r for r in rows if r["language"] == l]
    c = C.Counter(cat(r) for r in sub)
    n = len(sub)
    left = 0
    for k, col in [("tech", RED), ("pop", OCHRE), ("non", GREY)]:
        w = 100 * c[k] / n
        if w > 0:
            ax.barh(i, w, left=left, color=col, height=0.62, edgecolor=SURF, linewidth=1.5)
        left += w
    ax.text(101.5, i, f"{n:,}", va="center", fontsize=8, color=INK2)
ax.set_yticks(range(len(langs)), langs)
ax.set_xlim(0, 100)
ax.set_xlabel("Share of items in the collection (%)")
ax.text(101.5, len(langs) - 0.35, "items", fontsize=8, color=MUTED)
ax.set_title("Fig. 1  What survives in each language: French and Spanish are almost all science;\nIndian languages are mostly literature", fontsize=10)
ax.xaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
legend3(ax, loc="upper center", bbox_to_anchor=(0.45, -0.1), ncol=3)
save(fig, "fig1_language_composition")

# Fig 2: small multiples by decade (publication year)
groups = ["English", "Indian languages", "French", "Spanish"]
decs = [1950, 1960, 1970, 1980, 1990]
fig, axes = plt.subplots(1, 4, figsize=(9, 2.8), sharey=False)
for ax, g in zip(axes, groups):
    sub = [r for r in rows if r["lang_group"] == g and r["year"] and 1950 <= r["year"] <= 1999]
    bottom = [0] * len(decs)
    for k, col in [("tech", RED), ("pop", OCHRE), ("non", GREY)]:
        vals = [sum(1 for r in sub if r["year"] // 10 * 10 == d and cat(r) == k) for d in decs]
        ax.bar(range(len(decs)), vals, bottom=bottom, color=col, width=0.7, edgecolor=SURF, linewidth=1.2)
        bottom = [a + b for a, b in zip(bottom, vals)]
    ax.set_xticks(range(len(decs)), ["50s", "60s", "70s", "80s", "90s"])
    ax.set_title(g, fontsize=9.5)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
axes[0].set_ylabel("Items by publication decade")
fig.suptitle("Fig. 2  Every language peaks in the 1970s–80s and collapses after 1991 (note different y-scales)",
             x=0.01, ha="left", fontsize=10, fontweight="bold", y=1.04)
legend3(axes[-1], loc="upper left", bbox_to_anchor=(-2.4, -0.18), ncol=3)
save(fig, "fig2_decades_small_multiples")

# Fig 3: two lives (two panels, own scales)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 2.9), gridspec_kw={"width_ratios": [42, 14]})
ys = list(range(1950, 1992))
for k, col in [("tech", RED), ("pop", OCHRE), ("non", GREY)]:
    pass
b = [0] * len(ys)
for k, col in [("tech", RED), ("pop", OCHRE), ("non", GREY)]:
    v = [sum(1 for r in rows if r["year"] == y and cat(r) == k and not (y == 1950 and r["publisher"] == "Foreign Languages Publishing House")) for y in ys]
    a1.bar(ys, v, bottom=b, color=col, width=0.85, edgecolor=SURF, linewidth=0.6)
    b = [x + y for x, y in zip(b, v)]
a1.set_title("Print life: items by publication year, 1950–1991", fontsize=9.5)
uy = list(range(2013, 2027))
b = [0] * len(uy)
for k, col in [("tech", RED), ("pop", OCHRE), ("non", GREY)]:
    v = [sum(1 for r in rows if r["added_year"] == y and cat(r) == k) for y in uy]
    a2.bar(uy, v, bottom=b, color=col, width=0.8, edgecolor=SURF, linewidth=0.6)
    b = [x + y for x, y in zip(b, v)]
a2.set_title("Digital life: uploads, 2013–2026*", fontsize=9.5)
a2.set_xticks([2013, 2017, 2021, 2025])
for a in (a1, a2):
    a.yaxis.grid(True, color=GRID, linewidth=0.8)
    a.set_axisbelow(True)
a1.set_ylabel("Items")
fig.suptitle("Fig. 6  Two lives of the books: Soviet print runs end in 1991; volunteer digitisation takes off after 2020",
             x=0.01, ha="left", fontsize=10, fontweight="bold", y=1.05)
fig.text(0.01, -0.12, "*2026 to mid-November. Panels use different y-scales. Publication year missing for 300 items; 116 undated\nForeign Languages Publishing House items recorded as 1950 (probably '195x') are left out of the left panel.", fontsize=7.5, color=MUTED)
legend3(a1, loc="upper left", ncol=1)
save(fig, "fig6_two_lives")

# Fig 4: items vs downloads + top 20
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw={"width_ratios": [1, 2.2], "wspace": 1.15})
tot_i, tot_d = len(rows), sum(r["downloads"] for r in rows)
for x, label, f in [(0, "Share of\nitems", lambda r: 1), (1, "Share of\ndownloads", lambda r: r["downloads"])]:
    base = sum(f(r) for r in rows)
    bot = 0
    for k, col in [("tech", RED), ("pop", OCHRE), ("non", GREY)]:
        v = 100 * sum(f(r) for r in rows if cat(r) == k) / base
        a1.bar(x, v, bottom=bot, color=col, width=0.6, edgecolor=SURF, linewidth=1.5)
        if v > 6:
            a1.text(x, bot + v / 2, f"{v:.0f}%", ha="center", va="center", color="white" if k != "non" else INK, fontsize=9, fontweight="bold")
        bot += v
a1.set_xticks([0, 1], ["Items", "Downloads"])
a1.set_ylim(0, 100)
a1.set_ylabel("%")
a1.set_title("Half the items,\n87% of the downloads", fontsize=9.5)
top = sorted(rows, key=lambda r: -r["downloads"])[:20][::-1]
cols = [RED if cat(r) == "tech" else OCHRE if cat(r) == "pop" else GREY for r in top]
a2.barh(range(20), [r["downloads"] / 1000 for r in top], color=cols, height=0.62)
a2.set_yticks(range(20), [(r["title"][:46] + ("…" if len(r["title"]) > 46 else "")) for r in top], fontsize=7.5)
a2.set_xlabel("Downloads (thousands)")
a2.set_xlim(0, 900)
a2.set_title("Top 20 most-downloaded items: all science, 11 are problem books", fontsize=9.5)
a2.xaxis.grid(True, color=GRID, linewidth=0.8)
a2.set_axisbelow(True)
for i, r in enumerate(top):
    a2.text(r["downloads"] / 1000 + 8, i, f"{r['downloads']/1000:,.0f}k", va="center", fontsize=7, color=INK2)
fig.suptitle("Fig. 3  Today's use is overwhelmingly about science, and especially about problem books",
             x=0.01, ha="left", fontsize=10, fontweight="bold", y=1.03)
legend3(a1, loc="upper left", bbox_to_anchor=(0, -0.12), ncol=3)
save(fig, "fig3_downloads")

# Fig 5: popular vs technical within science, by language group
fig, ax = plt.subplots(figsize=(6.5, 2.8))
g5 = ["English", "French", "Spanish", "Indian languages"][::-1]
for i, g in enumerate(g5):
    sub = [r for r in rows if r["lang_group"] == g and r["domain"] in SCI]
    n = len(sub)
    t = 100 * sum(1 for r in sub if r["domain"] == "science_technical") / n
    ax.barh(i, t, color=RED, height=0.6, edgecolor=SURF, linewidth=1.5)
    ax.barh(i, 100 - t, left=t, color=OCHRE, height=0.6, edgecolor=SURF, linewidth=1.5)
    if t > 8:
        ax.text(t / 2, i, f"{t:.0f}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    if 100 - t > 8:
        ax.text(t + (100 - t) / 2, i, f"{100-t:.0f}%", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    ax.text(101.5, i, f"n={n}", va="center", fontsize=8, color=INK2)
ax.set_yticks(range(len(g5)), g5)
ax.set_xlim(0, 100)
ax.set_xlabel("Share of science items (%)")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=RED, label="Science & technical (textbooks, monographs, problem books)"),
                   Patch(color=OCHRE, label="Popular science")], loc="upper center", bbox_to_anchor=(0.45, -0.28), ncol=1)
ax.set_title("Fig. 4  In Indian languages, Soviet science arrived as popularisation;\nin English, French and Spanish, mostly as textbooks", fontsize=10)
save(fig, "fig4_popular_vs_technical")

# Fig 6: uploads by language group, Indian languages emphasised
fig, ax = plt.subplots(figsize=(6.5, 3))
uy = list(range(2013, 2027))
ind = [sum(1 for r in rows if r["added_year"] == y and r["lang_group"] == "Indian languages") for y in uy]
oth = [sum(1 for r in rows if r["added_year"] == y and r["lang_group"] != "Indian languages") for y in uy]
ax.bar(uy, ind, color=RED, width=0.75, label="Indian languages", edgecolor=SURF, linewidth=1)
ax.bar(uy, oth, bottom=ind, color=GREY, width=0.75, label="All other languages", edgecolor=SURF, linewidth=1)
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_ylabel("Items uploaded")
ax.legend(loc="upper left")
ax.set_title("Fig. 7  The digital afterlife turns vernacular: Indian-language items\nrise from 5% of uploads (to 2020) to 31% (2021 onwards)", fontsize=10)
fig.text(0.01, -0.04, "2026 to mid-November.", fontsize=7.5, color=MUTED)
save(fig, "fig7_uploads_vernacular")
print("figures written to", OUT)
