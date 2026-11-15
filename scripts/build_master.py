"""Build the master table for the Mir Titles collection.

Inputs:  data/ia.json (search export), data/item_meta/*.json (per-item metadata)
Output:  data/master.csv
"""
import csv, glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

L = lambda v: v if isinstance(v, list) else ([] if v in (None, "") else [v])

LANG = {
    "eng": "English", "english": "English", "en": "English",
    "english (translated from the russian)": "English",
    "hin": "Hindi", "hindi": "Hindi", "hi": "Hindi",
    "fre": "French", "fra": "French", "french": "French", "fr": "French",
    "ben": "Bengali", "bn": "Bengali", "spa": "Spanish", "es": "Spanish",
    "tam": "Tamil", "ta": "Tamil", "mar": "Marathi", "mr": "Marathi",
    "tel": "Telugu", "te": "Telugu", "rus": "Russian", "russian": "Russian", "ru": "Russian",
    "guj": "Gujarati", "gu": "Gujarati", "kan": "Kannada", "kn": "Kannada",
    "ori": "Odia", "or": "Odia", "urd": "Urdu", "ur": "Urdu", "ita": "Italian", "it": "Italian",
    "mal": "Malayalam", "ml": "Malayalam", "pan": "Punjabi", "pa": "Punjabi",
    "nep": "Nepali", "ne": "Nepali", "asm": "Assamese", "as": "Assamese",
    "por": "Portuguese", "pt": "Portuguese", "per": "Persian", "fa": "Persian",
    "rum": "Romanian", "ro": "Romanian", "hun": "Hungarian", "hu": "Hungarian",
    "german": "German", "de": "German", "vie": "Vietnamese", "swa": "Swahili", "sw": "Swahili",
}
INDIAN = {"Hindi", "Bengali", "Tamil", "Marathi", "Telugu", "Gujarati", "Kannada", "Odia",
          "Urdu", "Malayalam", "Punjabi", "Assamese", "Nepali"}
# Title suffixes like "(... In Hindi)" are reliable language markers in this collection
TITLE_LANG = re.compile(r"\bin (hindi|bengali|bangla|tamil|telugu|marathi|gujarati|kannada|odia|oriya|"
                        r"urdu|malayalam|punjabi|assamese|nepali|french|spanish)\b", re.I)
TL_MAP = {"bangla": "Bengali", "oriya": "Odia"}


def norm_pub(p):
    p = p.lower()
    if re.search(r"\bmir\b|мир|मीर|ediciones mir|editorial mir|[éè]ditions mir|edizioni mir", p):
        return "Mir"
    if re.search(r"raduga|रादुगा|радуга", p):
        return "Raduga"
    if re.search(r"progress|प्रगति|प्रगती|прогресс", p):
        return "Progress"
    if "foreign languages publishing" in p:
        return "Foreign Languages Publishing House"
    if "malysh" in p:
        return "Malysh"
    if "foreign languages press" in p or "beijing" in p or "dolphin" in p:
        return "Foreign Languages Press (Beijing)"
    if re.search(r"nasa|israel program|ipst|foreign technology division", p):
        return "Western technical translation"
    if re.search(r"people.?s publishing|पीपुल्स|navakarnataka|visalaandhra|nchb|prabhat", p):
        return "Indian co-publisher"
    if "mir titles" in p:
        return "Mir Titles project"
    if not p.strip():
        return "Unknown"
    return "Other"


def clean_text(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


TRANS = re.compile(r"[Tt]ranslated (?:from (?:the )?[Rr]ussian )?by ((?:(?:[A-Z][a-z'\-]+|[A-Z]\.)\s?){1,4}?[A-Z][a-z'\-]+)")
STOP = re.compile(r"\s+(Originally|Edited|Designed|Illustrated|First|Published|Revised|Translated)$")
SCAN = re.compile(r"(?:many )?thanks to ([A-Z][\w.\- ]{2,50}?) for (?:the )?(?:original |raw )?(?:scans?|2-in-1)", re.I)


def main():
    search = {d["identifier"]: d for d in json.load(open(os.path.join(D, "ia.json")))["response"]["docs"]}
    rows = []
    for ident, s in search.items():
        mp = os.path.join(D, "item_meta", ident + ".json")
        m = json.load(open(mp)).get("metadata", {}) if os.path.exists(mp) else {}
        title = s.get("title") or m.get("title") or ""
        meta_lang = [LANG.get(x.strip().lower(), x.strip()) for x in L(s.get("language") or m.get("language"))]
        ocr_lang = LANG.get(str(m.get("ocr_detected_lang", "")).lower())
        tl = TITLE_LANG.search(title)
        title_lang = (TL_MAP.get(tl.group(1).lower(), tl.group(1).title())) if tl else None
        # Priority: explicit title marker > catalogue metadata > OCR detection
        if title_lang:
            lang, lang_src = title_lang, "title"
        elif meta_lang:
            lang, lang_src = meta_lang[0], "metadata"
        elif ocr_lang:
            lang, lang_src = ocr_lang, "ocr"
        else:
            lang, lang_src = "Unknown", "none"
        y = str(s.get("year") or m.get("year") or m.get("date") or "")
        yr = int(y[:4]) if re.match(r"^\d{4}", y) and 1900 <= int(y[:4]) <= 2026 else None
        pubs = L(s.get("publisher") or m.get("publisher"))
        pub_raw = "; ".join(pubs)
        pub = norm_pub(pub_raw)
        desc = clean_text(m.get("description") or s.get("description") or "")
        tr = [STOP.sub("", t).strip() for t in TRANS.findall(desc)]
        tr += [t for t in L(m.get("translator"))]
        sc = SCAN.findall(desc)
        subj = [x.strip() for x in L(s.get("subject")) if x.strip()]
        series = ""
        st = (title + " " + " ".join(subj)).lower()
        for name, pat in [("Science for Everyone", r"science for everyone"),
                          ("Little Mathematics Library", r"little mathematics library"),
                          ("Physics for Everyone", r"physics for everyone"),
                          ("Men of Russian Science", r"men of russian science"),
                          ("Higher Mathematics", r"higher mathematics series")]:
            if re.search(pat, st):
                series = name
                break
        rows.append({
            "id": ident,
            "title": title,
            "language": lang,
            "lang_source": lang_src,
            "lang_group": "Indian languages" if lang in INDIAN else lang,
            "script": m.get("ocr_detected_script", "") if isinstance(m.get("ocr_detected_script", ""), str) else "|".join(m.get("ocr_detected_script")),
            "year": yr,
            "decade": (yr // 10 * 10) if yr else None,
            "publisher_raw": pub_raw,
            "publisher": pub,
            "creator": "; ".join(L(s.get("creator"))),
            "translators": "; ".join(sorted(set(t.strip() for t in tr if t.strip()))),
            "scan_credits": "; ".join(sorted(set(re.sub(r"\s+(garu|ji)$", "", c.strip(), flags=re.I).title() for c in sc if c.strip()))),
            "series": series,
            "subjects": "; ".join(subj),
            "downloads": int(s.get("downloads") or 0),
            "added_year": int(str(s.get("addeddate") or m.get("addeddate") or "0000")[:4] or 0),
            "uploader": m.get("uploader", ""),
            "image_count": m.get("imagecount", ""),
        })
    out = os.path.join(D, "master.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
