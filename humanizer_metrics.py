#!/usr/bin/env python3
"""
humanizer_metrics.py — local, offline proxy metrics for "does this read like AI?"

These metrics capture the BURSTINESS / LEXICAL-DIVERSITY axis that detectors use.
They do NOT capture perplexity (predictability) — for that you need a language
model. Treat the output as a structural smell-test, not a verdict.

Usage:
    python3 humanizer_metrics.py mytext.txt
    python3 humanizer_metrics.py mytext.txt --baseline human_sample.txt

Interpretation (rough, language-dependent — calibrate against a human sample):
    CV (coeff. of variation of sentence length): higher = more human.
        < 0.30  -> suspiciously uniform (AI-like)
        0.35-0.55 -> healthy human-like variation
    Goldstein burstiness (std-mean)/(std+mean): closer to 0 / positive = more human.
    TTR (type-token ratio): higher = richer vocabulary (but drops on long texts).
The single most reliable move is to ALWAYS compare against a real human sample
from the same genre/author, not against absolute thresholds.
"""
import re, sys, statistics as st

def sentences(text):
    # Hard sentence boundaries only: . ! ?  (Turkish "…" inside quotes is NOT a boundary)
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]

def analyze(name, text):
    sents = sentences(text)
    lens = [len(s.split()) for s in sents]
    words = re.findall(r"\w+", text.lower())
    if not lens or not words:
        print(f"=== {name} ===\n(empty)\n"); return
    mean = st.mean(lens)
    sd = st.pstdev(lens)
    cv = sd / mean if mean else 0
    burst = (sd - mean) / (sd + mean) if (sd + mean) else 0
    ttr = len(set(words)) / len(words)
    print(f"=== {name} ===")
    print(f"sentences: {len(sents)} | words: {len(words)}")
    print(f"sentence lengths: {lens}")
    print(f"mean sentence length: {mean:.1f} | min {min(lens)} / max {max(lens)}")
    print(f"std dev: {sd:.1f} | CV (variation): {cv:.2f}")
    print(f"Goldstein burstiness: {burst:.3f}  (more human -> closer to 0 / positive)")
    print(f"type-token ratio (TTR): {ttr:.3f}")
    # crude flags
    flags = []
    if cv < 0.30: flags.append("LOW burstiness -> sentences too uniform (AI smell)")
    if max(lens) - min(lens) < 12: flags.append("narrow sentence-length range -> add short + long sentences")
    if not flags: flags.append("structural variation looks healthy")
    print("notes: " + "; ".join(flags) + "\n")

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    baseline = None
    if "--baseline" in sys.argv:
        i = sys.argv.index("--baseline")
        baseline = sys.argv[i+1]
        args = [a for a in args if a != baseline]
    if not args:
        print(__doc__); sys.exit(1)
    with open(args[0], encoding="utf-8") as f:
        analyze(f"TARGET: {args[0]}", f.read())
    if baseline:
        with open(baseline, encoding="utf-8") as f:
            analyze(f"HUMAN BASELINE: {baseline}", f.read())

if __name__ == "__main__":
    main()
