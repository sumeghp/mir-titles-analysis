"""Rule-based domain classification for the Mir Titles master table.

Domains:
  popular_science     popular science, recreational maths, children's science, popular series
  science_technical   textbooks, monographs, problem books, handbooks, engineering, medicine
  literature          fiction, children's fiction, folk tales, poetry, drama, science fiction
  politics_society    Marxism-Leninism, politics, economics, history, philosophy, education theory
  other               anything not matched

Rules are applied in order (popular science > science > literature > politics).
Generic collection tags (e.g. "soviet literature", which is on most items) are ignored.

Input:  data/master.csv
Output: data/master_classified.csv, data/validation_sample.csv
"""
import csv, os, random, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

GENERIC = re.compile(
    r"^(soviet literature|soviet|russian literature|mir|mir books|mir titles|mirtitles|mir publishers|"
    r"soviet books|books|series|ussr|progress publishers|raduga|foreign languages publishing house|"
    r"pdf // djvu|a300|издательство \"мир\"|мир|"
    r"सोवियत साहित्य|सोव्हिएत साहित्य|सोव्हियेत साहित्य|রাশিয়ান সাহিত্য|সোভিয়েত সাহিত্য|"
    r"சோவியத் இலக்கியம்|సోవియట్ సాహిత్యం|ಸೋವಿಯತ್ ಸಾಹಿತ್ಯ|સોવિયેત સાહિત્ય|ସୋଭିଏଟ୍|literatura soviética|"
    r"telugu|tamil|hindi|bengali|marathi|kannada|gujarati|india|navakarnataka|ನವಕರ್ನಾಟಕ)$"
)

POPSCI = re.compile(
    r"popular science|science for everyone|physics for everyone|little mathematics library|"
    r"lecciones populares|ciencia popular|divulgaci[oó]n|recreational math|for entertainment|for fun|"
    r"can be fun|children'?s science|amusing|entertaining|puzzle|science soviétique|"
    r"física al alcance|los científicos a los escolares|scientists to school ?children|"
    r"लोकप्रिय विज्ञान|জনপ্রিয় বিজ্ঞান|ಜನಪ್ರಿಯ ವಿಜ್ಞಾನ|"
    r"interesting facts|stories about (chemistry|physics|mathematics)|how (people|man) discovered|"
    r"from (the )?bonfire to (the )?reactor|space adventures in your home|how man became a giant"
)

SCIENCE = re.compile(
    r"physic|mathemat|matem|chemi|chimi|qu[ií]mic|biolog|astronom|astrophys|geolog|engineer|mechanic|"
    r"m[ée]cani|thermodyn|electr|[ée]lectr|calcul|algebra|alg[eè]bre|[áa]lgebra|geometr|g[ée]om[ée]tr|"
    r"quantum|quantique|cu[aá]ntic|optic|nuclear|nucl[ée]aire|atom|cybernet|differential|diff[ée]rentiel|"
    r"diferencial|statistic|probabilit|radio|computer|ordinateur|electronic|semiconductor|laser|plasma|"
    r"relativity|relativit|metallurg|metal|alloy|material|crystal|medicine|medic|m[ée]dec|anatomy|"
    r"physiolog|zoolog|botan|genetic|ecolog|meteorolog|technolog|technique|t[ée]cnic|machine|rocket|"
    r"space travel|spaceship|space ship|cosmonaut|astronaut|satellite|planet|solar system|universe|"
    r"galax|cosmolog|energy|[ée]nergie|problems and solutions|problem book|problems in|handbook|"
    r"textbook|manual|course in|course of|fundamentals of|theory of|topolog|tensor|vector|matri|"
    r"function|fonction|funci|integral|int[ée]gral|equation|[ée]quation|ecuaci|analysis|analyse|"
    r"an[aá]lisis|series|fourier|first aid|nurs|obstetric|surgery|disease|agricultur|soil|"
    r"science|scien|cienc|f[ií]sic|hydro|aerodynam|elastic|heat|thermal|waves|oscillat|"
    r"विज्ञान|भौतिक|रसायन|गणित|बीजगणित|ज्यामिति|खगोल|প্রাথমিক চিকিৎসা|বিজ্ঞান|পদার্থ|রসায়ন|গণিত|"
    r"அறிவியல்|இயற்பியல்|வேதியியல்|கணிதம்|விலங்கியல்|நிலத்தியல்|విజ్ఞాన|భౌతిక|గణిత|రసాయన|"
    r"ವಿಜ್ಞಾನ|ಭೌತ|ಗಣಿತ|ಬೀಜಗಣಿತ|વિજ્ઞાન|ગણિત|ବିଜ୍ଞାନ|ଗଣିତ|"
    r"физик|хими|математ|биолог|наука|техник"
)

LITERATURE = re.compile(
    r"literat|novel|roman\b|stor(y|ies)|tale|fairy|folk|child|picture|poem|poetry|verse|rhyme|drama|"
    r"play|fable|fiction|fantasy|adventure|illustrated|cuento|conte|po[eé]s|"
    r"साहित्य|कहानी|कहानियां|उपन्यास|कविता|किताबें|पुस्तके|কাহিনী|গল্প|উপন্যাস|সাহিত্য|ছবির বই|শিশু|রূপকথা|"
    r"இலக்கியம்|கதை|நாவல்|సాహిత్య|కథ|ಸಾಹಿತ್ಯ|ಕಥೆ|ಮಕ್ಕಳ|ಪುಸ್ತಕ|સાહિત્ય|વાર્તા|ସାହିତ୍ୟ|ଶିଶୁ|ଗଳ୍ପ|"
    r"کہانی|ادب|ناول"
)

STRONG_POL = re.compile(r"marx|lenin|dialectic|historical materialism|philosoph|aesthetic|methodology of history|"
                        r"social psychology|political economy|scientific communism|atheis|socialist|capitalis|imperialis")

POLITICS = re.compile(
    r"marx|lenin|politic|econom|socialis|communis|philosoph|dialectic|materialism|history|histoire|"
    r"historia|revolution|war\b|world war|army|society|soviet life|soviet people|peace|pedagog|"
    r"education|propaganda|ideolog|capitalis|imperialis|class struggle|law|constitution|"
    r"इतिहास|दर्शन|मार्क्स|लेनिन|ইতিহাস|দর্শন"
)


def classify(row):
    subj = [s.strip().lower() for s in row["subjects"].split(";") if s.strip()]
    subj = [s for s in subj if not GENERIC.match(s)]
    text = " ".join(subj) + " || " + row["title"].lower() + " " + row["series"].lower()
    pub = row["publisher"]
    if row["series"] or POPSCI.search(text):
        return "popular_science", "popsci-keyword"
    if STRONG_POL.search(text) and pub != "Mir":
        return "politics_society", "strong-politics-keyword"
    sci = SCIENCE.search(text)
    lit = LITERATURE.search(text)
    if sci and not (lit and pub in ("Raduga", "Malysh")):
        return "science_technical", "science-keyword"
    if pub == "Mir" and not lit:
        return "science_technical", "publisher-mir"
    if pub == "Western technical translation":
        return "science_technical", "publisher-technical"
    if lit or pub in ("Raduga", "Malysh"):
        return "literature", "literature-keyword-or-publisher"
    if POLITICS.search(text):
        return "politics_society", "politics-keyword"
    return "other", "unmatched"


def main():
    rows = list(csv.DictReader(open(os.path.join(D, "master.csv"))))
    for r in rows:
        r["domain"], r["domain_rule"] = classify(r)
        r["science_any"] = "1" if r["domain"] in ("popular_science", "science_technical") else "0"
    out = os.path.join(D, "master_classified.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Stratified validation sample: 40 per domain (or all if fewer), fixed seed
    random.seed(42)
    sample = []
    for dom in ["popular_science", "science_technical", "literature", "politics_society", "other"]:
        pool = [r for r in rows if r["domain"] == dom]
        sample += random.sample(pool, min(40, len(pool)))
    random.shuffle(sample)
    with open(os.path.join(D, "validation_sample.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "url", "title", "language", "publisher", "subjects", "predicted_domain",
                    "correct_domain (fill in)", "notes"])
        for r in sample:
            w.writerow([r["id"], "https://archive.org/details/" + r["id"], r["title"], r["language"],
                        r["publisher"], r["subjects"][:200], r["domain"], "", ""])
    print(f"wrote {out} and validation_sample.csv ({len(sample)} rows)")


if __name__ == "__main__":
    main()
