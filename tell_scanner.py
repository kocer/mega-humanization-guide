#!/usr/bin/env python3
"""
tell_scanner.py — scan a draft for the AI tells cataloged in MEGA_HUMANIZATION_GUIDE.md §4.

Regex/heuristic checks only: this surfaces *candidates* for human review, it does
not prove anything. Pair it with humanizer_metrics.py (burstiness axis) and run
the §11 QA gate by hand. Supports Turkish and English (auto-detected).

Usage:
    python3 tell_scanner.py draft.txt
    python3 tell_scanner.py draft.txt --lang tr
    python3 tell_scanner.py draft.txt --json
    python3 tell_scanner.py essay1.txt --siblings essay2.txt essay3.txt   # §4.13

Exit code: 0 = no FLAG findings, 1 = at least one FLAG (usable as a soft gate).
"""
import argparse, json, re, sys
from collections import Counter

TR_CHARS = re.compile(r"[ğüşıçöĞÜŞİÇÖ]")
ABBREVS = ["vb.", "vs.", "bkz.", "örn.", "yy.", "e.g.", "i.e.", "etc.",
           "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "s.", "p.", "pp.", "no.", "cf."]
# Whole-token only: bare "s." is the TR page abbrev, but "relationships." must still split.
ABBREV_RE = re.compile(r"(?<!\w)(" + "|".join(re.escape(a[:-1]) for a in ABBREVS) + r")\.")

ANTITHESIS = {
    "tr": [r"\bdeğil[,;]", r"\bdeğil\s+(?:ama|fakat)\b", r"\byerine\b",
           r"\bötesinde\b", r"\baksine\b", r"\bbilakis\b"],
    "en": [r"\bnot\s+(?:merely|simply|just|only)\b", r"\brather\s+than\b",
           r"\bnot\s+an?\s+\w+[^.!?]{0,30}\bbut\b"],
}
TRIAD = re.compile(r"\b\w+,\s+\w+,?\s+(?:ve|and)\s+\w+", re.IGNORECASE)
ROADMAP = {
    "tr": [r"Bu\s+(?:makalede|yazıda|çalışmada|denemede)[^.!?]*"
           r"(?:incelenecektir|ele alınacaktır|işlenecektir|incelenmektedir)"],
    "en": [r"\bIn this (?:essay|paper)\b", r"\bThis (?:essay|paper) will\b",
           r"\bwill be examined\b"],
}
APHORISM = {
    "tr": [r"ne kadar[^.!?]{3,60}o kadar",
           r"\w+(?:e|a)bilir[,;]?\s+(?:ama|fakat|ancak)\s+[^.!?]*?(?:maz|mez)\b"],
    "en": [r"\bthe more\b[^.!?]{3,60}\bthe more\b",
           r"\bcan\b[^.!?]{0,40}\bbut (?:it )?cannot\b"],
}
AI_VOCAB = {
    "tr": ["olgu", "bu bağlamda", "dolayısıyla", "nitekim", "vurgulamaktadır",
           "söz konusu", "niteliktedir", "olarak resmedilir", "gözler önüne"],
    "en": ["delve", "delves", "delving", "tapestry", "intricate", "multifaceted",
           "underscore", "underscores", "pivotal", "testament", "realm",
           "navigate", "navigating", "crucial", "vibrant", "it's worth noting",
           "in today's world", "stands as"],
}
HEDGES = {
    "tr": [r"araştırmalar göster", r"bilindiği üzere", r"birçok kişiye göre",
           r"uzmanlara göre"],
    "en": [r"\bstudies show\b", r"\bit is widely believed\b", r"\bmany argue\b",
           r"\bexperts (?:say|agree)\b", r"\bresearch suggests\b"],
}
INFLATED = {
    "tr": [r"\bbaşyapıt\b", r"\bölümsüz\b", r"\beşsiz\b", r"\bzamansız\b"],
    "en": [r"\bmasterpiece\b", r"\btimeless\b", r"\bprofound(?:ly)?\b",
           r"\btestament to\b", r"\bstands as a\b", r"\bhuman spirit\b"],
}
CONNECTIVE_OPENERS = {
    "tr": ["üstelik", "dolayısıyla", "nitekim", "ayrıca", "ancak", "oysa",
           "böylece", "kısacası", "bununla birlikte"],
    "en": ["furthermore", "moreover", "additionally", "however", "thus",
           "therefore", "consequently"],
}


def sentences(text):
    protected = ABBREV_RE.sub(lambda m: m.group(1) + "\x00", text)
    parts = re.split(r"(?<=[.!?])\s+", protected.strip())
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


def excerpt(s, n=80):
    s = re.sub(r"\s+", " ", s)
    return s if len(s) <= n else s[:n] + "…"


def finding(section, tell, severity, message, locations=None):
    return {"section": section, "tell": tell, "severity": severity,
            "message": message, "locations": locations or []}


def match_locations(sents, patterns, flags=re.IGNORECASE):
    locs = []
    for i, s in enumerate(sents, 1):
        for pat in patterns:
            if re.search(pat, s, flags):
                locs.append(f"s{i}: \"{excerpt(s)}\"")
                break
    return locs


def check_antithesis(text, sents, wc, lang):
    locs = match_locations(sents, ANTITHESIS[lang])
    allowed = max(1, round(wc / 250))
    if len(locs) > allowed:
        return [finding("§4.1", "stacked antithesis", "FLAG",
                        f"{len(locs)} matches; guide allows ~1 per 250 words (≈{allowed} here)", locs)]
    if locs:
        return [finding("§4.1", "stacked antithesis", "INFO",
                        f"{len(locs)} match(es), within budget (≈{allowed})", locs)]
    return []


def check_triads(text, sents, wc, lang):
    locs = []
    for i, s in enumerate(sents, 1):
        for m in TRIAD.finditer(s):
            locs.append(f"s{i}: \"{excerpt(m.group(0))}\"")
    if len(locs) >= 3:
        return [finding("§4.2", "rule of three", "FLAG",
                        f"{len(locs)} triads; keep only content-driven ones, cut to two or expand to four", locs)]
    if locs:
        return [finding("§4.2", "rule of three", "INFO",
                        f"{len(locs)} triad(s) — review whether content-driven", locs)]
    return []


def check_closings(text, sents, wc, lang):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    closers = []
    for p in paras:
        ps = sentences(p)
        if len(p.split()) < 15 or not ps:
            continue  # skip headings/short fragments
        last_word = re.sub(r"[^\w]+$", "", ps[-1].split()[-1]).lower()
        if last_word:
            closers.append((last_word, excerpt(ps[-1], 60)))
    counts = Counter(w for w, _ in closers)
    out = []
    for word, n in counts.items():
        if n >= 3:
            locs = [f"¶ ends: \"{e}\"" for w, e in closers if w == word]
            out.append(finding("§4.3", "formulaic paragraph closings", "FLAG",
                               f"{n} paragraphs end on the same word '{word}' — vary closing shapes", locs))
    return out


def check_roadmap(text, sents, wc, lang):
    locs = match_locations(sents, ROADMAP[lang], flags=0 if lang == "tr" else re.IGNORECASE)
    if locs:
        return [finding("§4.4", "templated thesis/roadmap", "INFO",
                        "stock roadmap phrasing found — keep the content, change the frame", locs)]
    return []


def check_aphorisms(text, sents, wc, lang):
    hit_idx = []
    for i, s in enumerate(sents, 1):
        if any(re.search(p, s, re.IGNORECASE) for p in APHORISM[lang]):
            hit_idx.append(i)
    locs = [f"s{i}: \"{excerpt(sents[i-1])}\"" for i in hit_idx]
    out = []
    if len(hit_idx) > 1:
        out.append(finding("§4.5", "balanced aphorisms", "FLAG",
                           f"{len(hit_idx)} aphorisms; allow at most one in the whole piece", locs))
        if any(b - a == 1 for a, b in zip(hit_idx, hit_idx[1:])):
            out.append(finding("§4.5", "back-to-back aphorisms", "FLAG",
                               "two balanced aphorisms in adjacent sentences — de-balance one", []))
    elif locs:
        out.append(finding("§4.5", "balanced aphorisms", "INFO", "one aphorism — that is the budget", locs))
    return out


def check_vocab(text, sents, wc, lang):
    low = text.lower()
    counts = {}
    for term in AI_VOCAB[lang]:
        pat = r"\b" + re.escape(term) + r"\b"
        n = len(re.findall(pat, low))
        if n:
            counts[term] = n
    if not counts:
        return []
    total = sum(counts.values())
    detail = ", ".join(f"{t}×{n}" for t, n in sorted(counts.items(), key=lambda x: -x[1]))
    heavy = [t for t, n in counts.items() if n >= 3]
    if heavy or total / max(wc, 1) * 1000 > 8:
        return [finding("§4.7", "AI vocabulary / essay-ese", "FLAG",
                        f"dense: {detail} ({total} hits in {wc} words) — swap a fraction for plainer synonyms", [])]
    return [finding("§4.7", "AI vocabulary / essay-ese", "INFO",
                    f"present but sparse: {detail}", [])]


def check_hedges(text, sents, wc, lang):
    locs = match_locations(sents, HEDGES[lang])
    if locs:
        return [finding("§4.8", "vague attribution / hedging", "FLAG",
                        "attribute to a specific source or state it plainly", locs)]
    return []


def check_inflated(text, sents, wc, lang):
    locs = match_locations(sents, INFLATED[lang])
    if locs:
        return [finding("§4.9", "inflated significance", "FLAG",
                        "delete superlatives; make claims specific and proportionate", locs)]
    return []


def check_dashes(text, sents, wc, lang):
    n = text.count("—") + text.count("–")
    if not n:
        return []
    density = n / max(wc, 1) * 1000
    if density > 3:
        return [finding("§4.10", "em-dash overuse", "FLAG",
                        f"{n} dashes ({density:.1f}/1000 words) — prefer commas/periods/parentheses "
                        "(exception: match the reference samples)", [])]
    return [finding("§4.10", "em-dash use", "INFO", f"{n} dash(es) — fine if genuine asides", [])]


def check_openers(text, sents, wc, lang):
    openers = []
    for s in sents:
        w = re.sub(r"^\W+|\W+$", "", s.split()[0]).lower() if s.split() else ""
        openers.append(w)
    out = []
    run_locs = []
    for i in range(len(openers) - 2):
        if openers[i] and openers[i] == openers[i + 1] == openers[i + 2]:
            run_locs.append(f"s{i+1}-s{i+3}: three sentences open with '{openers[i]}'")
    if run_locs:
        out.append(finding("§4.12", "repeated sentence openers", "FLAG",
                           "vary sentence openers", run_locs))
    conn_counts = Counter(o for o in openers if o in CONNECTIVE_OPENERS[lang])
    for w, n in conn_counts.items():
        if n >= 3:
            out.append(finding("§4.12", "mechanical transitions", "FLAG",
                               f"connective '{w}' opens {n} sentences — rotate the palette (§9)", []))
    return out


QUOTE_RE = re.compile(r"[“\"]([^”\"]{15,300})[”\"]")
PAGE_RE = re.compile(r"\b(?:s|p|pp)\.\s*\d+|\([A-ZĞÜŞİÇÖ]\w+,?\s*(?:s\.\s*)?\d+\)")


def check_siblings(main_text, main_name, sibling_files):
    out = []
    main_quotes = {re.sub(r"\s+", " ", q).strip().lower() for q in QUOTE_RE.findall(main_text)}
    main_pages = Counter(PAGE_RE.findall(main_text))
    for path in sibling_files:
        with open(path, encoding="utf-8") as f:
            sib = f.read()
        shared_q = main_quotes & {re.sub(r"\s+", " ", q).strip().lower() for q in QUOTE_RE.findall(sib)}
        shared_p = sorted((main_pages & Counter(PAGE_RE.findall(sib))).elements())
        if shared_q:
            out.append(finding("§4.13", "cross-document: shared quotes", "FLAG",
                               f"{len(shared_q)} identical quote(s) shared with {path} — re-quote from other passages",
                               [f"\"{excerpt(q)}\"" for q in sorted(shared_q)]))
        if len(shared_p) >= 2:
            out.append(finding("§4.13", "cross-document: shared page citations", "FLAG",
                               f"page citations overlap with {path}: {', '.join(shared_p)}", []))
    return out


CHECKS = [check_antithesis, check_triads, check_closings, check_roadmap,
          check_aphorisms, check_vocab, check_hedges, check_inflated,
          check_dashes, check_openers]


def scan(text, lang):
    sents = sentences(text)
    wc = len(re.findall(r"\w+", text))
    findings = []
    for check in CHECKS:
        findings.extend(check(text, sents, wc, lang))
    return findings, wc, len(sents)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="draft to scan ('-' for stdin)")
    ap.add_argument("--lang", choices=["tr", "en"], help="override language auto-detection")
    ap.add_argument("--siblings", nargs="+", default=[], metavar="FILE",
                    help="sibling essays on the same primary text (§4.13 cross-document check)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    text = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    lang = args.lang or ("tr" if len(TR_CHARS.findall(text)) > 5 else "en")
    findings, wc, ns = scan(text, lang)
    findings.extend(check_siblings(text, args.file, args.siblings))

    n_flag = sum(1 for f in findings if f["severity"] == "FLAG")
    n_info = len(findings) - n_flag

    if args.json:
        print(json.dumps({"file": args.file, "lang": lang, "words": wc,
                          "sentences": ns, "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        print(f"=== tell_scanner: {args.file} (lang={lang}, {wc} words, {ns} sentences) ===\n")
        if not findings:
            print("no tells matched — still run the §11 QA gate by hand.\n")
        for f in findings:
            print(f"[{f['severity']}] {f['section']} {f['tell']} — {f['message']}")
            for loc in f["locations"]:
                print(f"    {loc}")
            print()
        print(f"summary: {n_flag} FLAG, {n_info} INFO  ->  fixes in MEGA_HUMANIZATION_GUIDE.md §4")
    sys.exit(1 if n_flag else 0)


if __name__ == "__main__":
    main()
