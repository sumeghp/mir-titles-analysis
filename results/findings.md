# Mir Titles analysis: first findings

Data: the Internet Archive `mir-titles` collection, 4,566 items, metadata downloaded 15 Nov 2026. All numbers below come from `scripts/analyse_core.py` (output in `results/summary.json` and `results/tables/`).

## The corpus
- 4,566 items in 25 languages. 3,906 are dated 1950–1991.
- 98.2% were uploaded by a single account (mirtitles). This is one curated volunteer project, not a random sample of what was published.
- Publishers (normalised): Mir 1,231, Progress 757, Raduga 546, Foreign Languages Publishing House 351. Another 1,235 items have no publisher recorded.

## Finding 1: Use concentrates on science, especially problem books
- Science (technical plus popular) is **50% of the items but 87% of the 9.19 million downloads**.
- The median science item has 1,293 downloads, against 260 for non-science. Controlling for time online, the median is 371 downloads a year for technical science against 84 for literature.
- **All of the top 20** most-downloaded items are science. Irodov's *Problems in General Physics* alone has about 787,000.
- **Problem books are 4.9% of items but take 25.1% of all downloads**, and 11 of the top 20 are problem books.
- Downloads are highly unequal: the Gini coefficient is 0.75, the top 1% of items take 25% of downloads and the top 10% take 64%.

## Finding 2: Each language survives differently
- French (99%) and Spanish (97%) holdings are almost entirely science. English is 55% science. Indian languages are 18% science (226 of 1,250 items).
- The Indian-language holdings are mostly literature and children's books (Raduga and Progress).

## Finding 3: In Indian languages, science came as popularisation
- **70% of Indian-language science items are popular science, against 15% in English** (38% in Spanish, about 0% in French).
- Indian-language science titles span 12 languages: Hindi 61, Tamil 53, Bengali 32, Marathi 24, Telugu 22, Kannada 19 and others. 69% of the dated ones are from the 1980s.
- In other words, English editions delivered Soviet textbooks to Indian students, while Indian-language editions delivered *popularisation* (*Physics for Everyone*, *How Man Became a Giant*, *From the Bonfire to the Reactor*). This bears directly on the paper's science-popularisation question.

## Finding 4: Two lives
- Print: titles in every language peak in the 1970s–80s and collapse after 1991.
- Digital: uploads grow from fewer than 250 a year before 2021 to 1,143 in 2025.
- **The digital afterlife is turning vernacular: Indian-language items were 4.8% of uploads to 2020 and 30.9% from 2021 onwards.**

## Finding 5: The people (to develop)
- Translator names are recorded for 1,287 items: 575 distinct translators. The top names are Margaret Wettlin, Irina Zheleznova, George Yankovsky, Olga Shartse, Leonid Levant and Fainna Glagoleva.
- Scanning volunteers are credited on 156 items (15 distinct), led by Guptaji (50), Anil Battula (45), Srujanika Publications (28) and Daniel Baker (21).
- This supports a "people" figure or network: Moscow translators in the print era, volunteer scanners in the digital era.

## Caveats (state these in the paper)
1. **Survival bias:** the collection shows what collectors kept, scanned and uploaded, not what was published. Findings 2 and 3 describe surviving holdings. They are consistent with the publishing history (Mir handled science, Raduga literature), but they can't establish original print shares without a publication baseline (Mir catalogues, WorldCat holdings or Soviet book-chamber statistics).
2. **Downloads** are global, carry no location, and count only Internet Archive traffic. Older uploads have had longer to collect them; per-year medians partly correct for this.
3. **Classification** is rule-based. A quick spot-check suggests the science/non-science split is about 94% accurate (science-fiction novels are the main error). The 200-row `data/validation_sample.csv` needs filling in by hand to get a formal accuracy figure.
4. **Dates:** 300 items have no year, and 116 undated Foreign Languages Publishing House items are recorded as 1950 (shown as an artefact in Fig. 3).
5. **Language:** 62 items have no detectable language. 162 were assigned from the OCR language detection.

## Figures (results/figures/, PNG 300 dpi + SVG)
1. Language composition: share science vs non-science by language
2. Decades: small multiples by language group
3. Two lives: print by publication year vs digital uploads
4. Downloads: items vs downloads share, plus the top 20
5. Popular vs technical science by language group
6. Uploads by year, Indian languages emphasised

## Next
- Check `validation_sample.csv` by hand (about an hour) and report accuracy.
- Look for a publication baseline (WorldCat or library catalogues) to test survival bias, at least for one series such as Science for Everyone.
- Draft the methods and results sections around Findings 1, 3 and 4.
