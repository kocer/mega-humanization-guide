#!/usr/bin/env python3
"""
humanizer_metrics.py — local, offline proxy metrics for "does this read like AI?"

These metrics capture the BURSTINESS / LEXICAL-DIVERSITY axis that detectors use.
They do NOT capture perplexity (predictability) — for that you need a language
model. Treat the output as a structural smell-test, not a verdict.

Usage:
    python3 humanizer_metrics.py mytext.txt
    python3 humanizer_metrics.py mytext.txt --baseline human_sample.txt
    python3 humanizer_metrics.py mytext.txt --strip-quotes   # measure body only
    python3 humanizer_metrics.py mytext.txt --json
    cat mytext.txt | python3 humanizer_metrics.py -

Interpretation (rough, language-dependent — calibrate against a human sample):
    CV (coeff. of variation of sentence length): higher = more human.
        < 0.30  -> suspiciously uniform (AI-like)
        0.35-0.55 -> healthy human-like variation
    Goldstein burstiness (std-mean)/(std+mean): closer to 0 / positive = more human.
    TTR (type-token ratio): higher = richer vocabulary (but drops on long texts).
The single most reliable move is to ALWAYS compare against a real human sample
from the same genre/author, not against absolute thresholds.
"""
import argparse, json, re, statistics as st, sys

ABBREVS = ["vb.", "vs.", "bkz.", "örn.", "yy.", "e.g.", "i.e.", "etc.",
           "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "s.", "p.", "pp.", "no.", "cf."]
# Whole-token only: bare "s." is the TR page abbrev, but "relationships." must still split.
ABBREV_RE = re.compile(r"(?<!\w)(" + "|".join(re.escape(a[:-1]) for a in ABBREVS) + r")\.")
# Double quotes only — single quotes would eat apostrophes (TR kesme: George'un).
QUOTE_RE = re.compile(r"[“\"«][^”\"»]{0,500}[”\"»]")


def sentences(text):
    # Hard sentence boundaries only: . ! ?  — with common abbreviations protected.
    protected = ABBREV_RE.sub(lambda m: m.group(1) + "\x00", text)
    parts = re.split(r"(?<=[.!?])\s+", protected.strip())
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


def analyze(text):
    sents = sentences(text)
    lens = [len(s.split()) for s in sents]
    words = re.findall(r"\w+", text.lower())
    if not lens or not words:
        return None
    mean = st.mean(lens)
    sd = st.pstdev(lens)
    return {
        "sentences": len(sents), "words": len(words), "lengths": lens,
        "mean_len": round(mean, 1), "min_len": min(lens), "max_len": max(lens),
        "stdev": round(sd, 1),
        "cv": round(sd / mean, 2) if mean else 0,
        "burstiness": round((sd - mean) / (sd + mean), 3) if (sd + mean) else 0,
        "ttr": round(len(set(words)) / len(words), 3),
    }


def flags_for(m):
    flags = []
    if m["cv"] < 0.30:
        flags.append("LOW burstiness -> sentences too uniform (AI smell)")
    if m["max_len"] - m["min_len"] < 12:
        flags.append("narrow sentence-length range -> add short + long sentences")
    return flags or ["structural variation looks healthy"]


def report(name, m):
    print(f"=== {name} ===")
    print(f"sentences: {m['sentences']} | words: {m['words']}")
    print(f"sentence lengths: {m['lengths']}")
    print(f"mean sentence length: {m['mean_len']} | min {m['min_len']} / max {m['max_len']}")
    print(f"std dev: {m['stdev']} | CV (variation): {m['cv']}")
    print(f"Goldstein burstiness: {m['burstiness']}  (more human -> closer to 0 / positive)")
    print(f"type-token ratio (TTR): {m['ttr']}")
    print("notes: " + "; ".join(flags_for(m)) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="text to measure ('-' for stdin)")
    ap.add_argument("--baseline", metavar="FILE", help="real human sample to compare against")
    ap.add_argument("--strip-quotes", action="store_true",
                    help="remove double-quoted spans before measuring (body-only, as in §5 of the guide)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    def load(path):
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        return QUOTE_RE.sub("", text) if args.strip_quotes else text

    target = analyze(load(args.file))
    if target is None:
        sys.exit("empty input")
    baseline = analyze(load(args.baseline)) if args.baseline else None

    delta = None
    if baseline:
        delta = {k: round(target[k] - baseline[k], 3)
                 for k in ("mean_len", "cv", "burstiness", "ttr")}

    if args.json:
        out = {"target": target, "baseline": baseline, "delta": delta}
        for m in (target, baseline):
            if m:
                m["flags"] = flags_for(m)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    report(f"TARGET: {args.file}", target)
    if baseline:
        report(f"HUMAN BASELINE: {args.baseline}", baseline)
        print("=== DELTA (target - baseline) ===")
        print(f"mean len: {delta['mean_len']:+.1f} | CV: {delta['cv']:+.2f} | "
              f"burstiness: {delta['burstiness']:+.3f} | TTR: {delta['ttr']:+.3f}")
        print("target the baseline's numbers, not maximum variation (§2 of the guide)")


if __name__ == "__main__":
    main()
