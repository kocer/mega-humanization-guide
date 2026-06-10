# Mega Humanization Guide

🌍 **Languages / Diller:** [**Türkçe** (ana / main) →](README.md) · English (this file)

> **⚙️ How to use these files — give them to an AI.** This repo is written *to be
> fed to an AI* (ChatGPT, Claude, Gemini, etc.). Paste `MEGA_HUMANIZATION_GUIDE.md`
> — especially §4 (tell catalog), §10 (drop-in instruction block) and §11 (QA gate)
> — into the model's system/instruction prompt, hand it your draft, and it will
> reproduce the full humanization pass. You are the director; the AI is the editor.

A complete, reusable methodology for turning AI-drafted prose into writing that
reads as genuinely human — without destroying meaning, structure, or quality.

Hand the guide to an AI as a system/instruction prompt and it can reproduce a
high-quality humanization pass: detection-signal theory, a catalog of AI "tells"
with real before→after fixes, burstiness engineering, a local measurement harness,
targeted de-flagging, controlled imperfection, and source integrity. Language-
agnostic core plus a Turkish-specific appendix.

## Contents

- **[`MEGA_HUMANIZATION_GUIDE.md`](MEGA_HUMANIZATION_GUIDE.md)** — the full guide.
  Start at §0 (how to use), §1–§2 (mental model + voice calibration), §4 (the tell
  catalog), §10 (drop-in AI instruction block), §11 (QA gate).
- **[`humanizer_metrics.py`](humanizer_metrics.py)** — offline proxy metrics
  (sentence-length burstiness, coefficient of variation, type-token ratio). Does
  **not** measure perplexity — it's a structural smell-test, not a verdict.
  Supports `--strip-quotes` (body-only measurement), `--baseline` (delta against
  a human sample), `--json`.
- **[`tell_scanner.py`](tell_scanner.py)** — automated first-pass audit of the §4
  tell catalog (TR + EN, auto-detected): stacked antithesis, rule of three,
  formulaic closings, templated thesis, aphorisms, AI vocabulary, hedging,
  em-dashes, mechanical transitions, plus the §4.13 cross-document check via
  `--siblings` (shared quotes/page citations). Heuristic, not a verdict — the
  human audit decides.

## Quick start

Scan the draft, then measure it against a real human sample from the same genre:

```bash
python3 tell_scanner.py draft.txt                                # §4 tell candidates
python3 tell_scanner.py draft.txt --siblings classmate_essay.txt # §4.13 cross-document
python3 humanizer_metrics.py draft.txt --baseline human_sample.txt --strip-quotes
```

Then drive an AI through the loop in §3 of the guide, using §4 as hard rules and
§11 as the exit gate.

## Honest disclaimer

No automated step makes text *guaranteed* to pass any AI detector — dense academic
prose is naturally low-burstiness and can be flagged even when human-written.
Detector scores are evidence, not proof, in both directions. The only guaranteed
humanization is a human editing a few sentences in their own voice. The guide says
so repeatedly, on purpose.

## License

The Unlicense (public domain). Do whatever you want with it. Attribution
appreciated, not required.
