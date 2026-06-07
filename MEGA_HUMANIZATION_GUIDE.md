# The Mega Humanization Guide

> A complete, reusable methodology for turning AI-drafted prose into writing that
> reads as genuinely human — without destroying meaning, structure, or quality.
>
> Hand this whole file to an AI as a system/instruction prompt. It encodes every
> micro-step from a real humanization session: detection-signal theory, a catalog
> of AI "tells" with before→after fixes, burstiness engineering, a local
> measurement harness, targeted de-flagging, controlled imperfection, and source
> integrity. Language-agnostic core + a Turkish-specific appendix.

License: do whatever you want with it. Attribution appreciated, not required.

---

## 0. How to use this file

**If you are a human:** read §1–§2 for the mental model, then drive an AI through
the loop in §3. Use `humanizer_metrics.py` (ships alongside this file) to measure.

**If you are an AI given this file:** treat §4 (the tell catalog) and §11 (the
QA gate) as hard rules. Your job is to rewrite the supplied draft so it passes the
gate while preserving its argument, evidence, citations, word count, and required
structure. Do **not** invent facts or citations. When you finish, output (a) the
rewritten text and (b) a short diff log of every change keyed to the tell it fixes.

**Golden rule:** humanization is mostly just *good writing*. 90% of the work is
removing the things that make prose feel manufactured. The other 10% is matching
a specific human voice. Detector-gaming is a side effect of doing those two well —
not the goal.

---

## 1. Why AI text is detectable — the two-axis model

Every statistical detector, under the hood, is measuring two things:

1. **Perplexity** — how *predictable* the next token is. AI tends to pick the
   highest-probability word, so its text is low-perplexity (too predictable).
   Humans make locally "surprising" word choices.

2. **Burstiness** — how much sentence length and rhythm *vary*. AI tends to emit
   uniformly medium-length, evenly-built sentences. Humans write in bursts:
   a long winding sentence, then a short punch. Then another long one.

You cannot easily measure perplexity offline (needs a language model), but you can
**measure burstiness directly** (see §5) and you can **lower perplexity by hand**
by replacing predictable phrasings with less-expected, more specific ones (§4).

A third, non-statistical layer matters for human readers and for modern detectors
trained on stylistic features: **surface tells** — clichés, formulaic transitions,
rule-of-three, balanced antitheses, aphoristic conclusions. These are §4's core.

**Crucial caveat that keeps you honest:** dense academic prose in *any* language is
naturally low-burstiness and low-perplexity. A perfectly human academic paragraph
can score "likely AI." Detector percentages are **evidence, not proof**, in both
directions. Never promise a human a guaranteed pass. The only guaranteed
humanization is a human editing a few sentences in their own voice.

---

## 2. Calibrate to a real human voice BEFORE you edit

Generic "make it sound human" produces generic results. Anchor to samples.

1. **Collect 1–3 reference texts** in the exact genre/register/author you're
   imitating (e.g., the student's own past essays, sample essays from the same
   class, the target publication).
2. **Extract the voice fingerprint** from them, explicitly:
   - typical sentence length and how much it varies
   - favourite connectives and transition words
   - how they introduce quotes/evidence
   - verb register (plain vs. elevated)
   - paragraph opening and closing habits
   - *their* imperfections (run-ons, redundancy, a flat sentence here and there)
3. **Match the imperfections too.** Real human writing in a given context is rarely
   flawless. If the samples have occasional clumsy sentences, your output should not
   be glassily smooth — that smoothness is itself a tell.
4. **Do NOT copy their tells if those tells are also AI tells.** Humans and AI both
   use rule-of-three and "not only X but also Y." Match the *frequency* the humans
   use (usually 1–2 per essay), not zero, not ten.

> Lesson from the field: when we measured a real human sample (a graded student
> essay) it had CV 0.33 and burstiness −0.51. The humanized AI essay landed at
> CV 0.43 / burstiness −0.40 — i.e. *more* varied than the human baseline. Matching
> the human's actual numbers is the target, not maximizing variation forever.

---

## 3. The workflow loop

```
(1) Calibrate voice from reference samples            (§2)
(2) Draft or ingest the text
(3) AUDIT: list every tell, with location             (§4)
(4) REWRITE: fix tells, preserve meaning/structure     (§4)
(5) MEASURE: run humanizer_metrics.py vs. a baseline   (§5)
(6) If a detector flags a span -> TARGETED de-flag     (§6)
(7) QA GATE: run the checklist                          (§11)
(8) Stop. Recommend a human hand-edit of 2-3 sentences (§1 golden rule)
```

Iterate (3)→(6) at most 2–3 times. Beyond that you hit diminishing returns and
risk over-editing the text into something choppy and unnatural. Know when to stop.

---

## 4. The AI Tell Catalog — detect & fix

For each tell: what it is, how to spot it, the fix rule, and a real before→after
pair from the session (Turkish, with English gloss).

### 4.1 Stacked negative parallelism / antithesis ("not X, but Y")
**The single biggest tell.** AI loves the construction "*not* a simple X, *but*
rather a profound Y." One is fine and human. Three or four in one piece scream AI.

- **Spot:** count occurrences of `değil/yerine/ötesinde/rather than/not merely`.
  More than ~1 per 250 words → reduce.
- **Fix:** convert most into plain declaratives. Keep at most one, ideally in the
  thesis where the contrast earns its place.

> BEFORE: "yalnızlığın **bireysel bir kusur değil**, toplumsal koşulların dayattığı
> **bir kader** olduğunu gösterir." (×4 such across the essay)
> AFTER: "Bu yalnızlık, romanda düzenin işçilere dayattığı bir sonuç olarak
> resmedilir." (declarative; antithesis removed)

### 4.2 Rule of three
AI compulsively groups in threes: "X, Y, and Z." Triads feel rhetorical and
manufactured when overused.

- **Spot:** lists of exactly three adjectives/nouns/clauses, especially abstract.
- **Fix:** cut to two, or expand to four, or make them concrete. Keep triads that
  are *content-driven* (e.g. three actual characters) — those are unavoidable.

> BEFORE: "ırk, cinsiyet, yaş ve sınıf farkı gözetmeksizin"
> AFTER: "ırk cinsiyet ve yaş ayrımı tanımadan" (trimmed; note: comma also dropped
> here as a *deliberate* human-error — see §7)

### 4.3 Formulaic paragraph closings
AI ends every paragraph with the same generalizing template: "Thus, the author
shows that…" Repeated identically, it's a fingerprint.

- **Spot:** every body paragraph closing with the same verb/shape ("ortaya koyar",
  "gösterir", "demonstrates", "highlights").
- **Fix:** vary the closing verb and structure. Let one paragraph end on a concrete
  image, another on a short declarative, another on the summarizing move.

> BEFORE: every paragraph ended "Böylece Steinbeck … ortaya koyar."
> AFTER: "…herkese uzanır." / "…kırılgan bir tesellidir." / "…karşılıksız
> bıraktığını gösterir." (three different shapes)

### 4.4 Templated thesis/roadmap announcements
"In this essay, X will be examined through the lenses of A and B." Required by many
rubrics, so you can't delete the *content* — but the exact stock phrasing is a tell.

- **Fix:** keep the required information (state both sub-theses), change the frame.
  A colon-list often reads more naturally than "…will be examined through…".

> BEFORE: "Bu makalede yalnızlık olgusu, … yan tezleri üzerinden incelenecektir."
> AFTER: "Bu yazıda söz konusu yalnızlık iki açıdan ele alınacaktır: … ve …"

### 4.5 Aphoristic, perfectly-balanced conclusions
AI closes essays with a tidy maxim: "the more X, the more Y." Polished to the point
of artificiality, especially two such closers back-to-back.

- **Spot:** "ne kadar X … o kadar Y", "X-ebilir ama Y-amaz", "as much … as".
- **Fix:** allow at most one balanced aphorism in the whole piece. De-balance the
  rest into plain statements.

> BEFORE (end of body ¶): "dostluk yalnızlığı bir süre dindire**bilir, ama** onu
> büsbütün ortadan kaldıra**maz**." + (conclusion) "ne kadar güçlü … ama
> karşılıksız …" — two twin aphorisms in a row.
> AFTER: body ¶ ends declaratively ("…ancak bir süreliğine sığınılabilen kırılgan
> bir tesellidir."), leaving the single aphorism in the conclusion only.

### 4.6 Uniform sentence length (low burstiness)
Covered fully in §5. The fix is mechanical: inject short sentences (4–8 words)
between long ones.

> ADDED: "Üstelik bazı karakterler için durum daha da ağırdır." (7 words) and
> "geriye yine herkes gibi yalnız kalmış bir işçi kalır." — short beats among
> 25–30-word analytical sentences.

### 4.7 Elevated, uniform diction / "AI vocabulary"
Words AI overuses: *delve, tapestry, intricate, multifaceted, underscore, pivotal,
testament, realm, navigate, crucial, vibrant*. In Turkish: an unrelenting register
of *olgu, bağlam, dolayısıyla, nitekim, vurgulamaktadır* with no plain words ever.

- **Fix:** swap a fraction for plainer synonyms; let register dip occasionally.
  Add one or two colloquial-but-correct verbs ("diye çıkışır", "savrulan").

### 4.8 Vague attributions & hedging
"Studies show", "it is widely believed", "many argue". AI uses these to sound
authoritative without committing.

- **Fix:** attribute to a specific, real source (§8) or delete the hedge and state
  it plainly.

### 4.9 Inflated significance / promotional tone
"This profound masterpiece stands as a timeless testament to the human spirit."
- **Fix:** delete superlatives; make claims specific and proportionate.

### 4.10 Em-dash overuse and curly-quote uniformity
AI sprinkles em dashes — like this — everywhere, and uses perfectly consistent
typographic quotes.
- **Fix:** prefer commas/periods/parentheses; reserve dashes for genuine asides.
  **Exception:** match the reference samples — if the human samples use curly
  quotes “ ” consistently (as in Turkish typeset essays), keep them. Voice-match
  beats the generic rule.

### 4.11 Quote/evidence integration that's too clean
AI drops quotes with identical scaffolding every time.
- **Fix:** vary how evidence enters. Mirror the reference samples. A colon
  introduction reads naturally: *"George şu sözlerle anlatır: '…'"*; alternate with
  inline integration and post-quote analysis ("Bu alıntıdan da anlaşılacağı üzere…").

### 4.12 Even, mechanical transitions
Starting every paragraph/sentence with "Furthermore, Moreover, Additionally."
- **Fix:** use the *reference's* connectives and vary them: in TR — "Üstelik",
  "Ne var ki", "Nitekim", "Kısacası", "Bununla birlikte", "Oysa", "Demek ki".

---

## 5. Burstiness engineering (the concrete part)

Target a sentence-length sequence that *oscillates*. After rewriting, the lengths
(in words) should look like a heartbeat, not a flat line.

- Aim for **CV ≥ 0.35** (coefficient of variation of sentence length).
- Ensure **max − min ≥ 12 words** (you have both short punches and long builds).
- Concretely: for every 2–3 long analytical sentences (20–32 words), plant one
  short sentence (4–9 words).

Run the bundled measurer:

```
python3 humanizer_metrics.py target.txt --baseline human_sample.txt
```

Real numbers from the session (essay body, quotes excluded):

| metric                | humanized AI | human baseline | reading                |
|-----------------------|-------------:|---------------:|------------------------|
| mean sentence length  | 16.9         | 20.4           | fine                   |
| CV (variation)        | **0.43**     | 0.33           | AI text *more* varied  |
| Goldstein burstiness  | **−0.40**    | −0.51          | AI text *more* human   |
| min / max sentence    | 6 / 32       | 8 / 29         | wide, healthy range    |
| TTR                   | 0.68         | 0.71           | ~equal                 |

Interpretation: structurally, the humanized text matched or beat a real human
sample. That is the bar. **But** this only proves the burstiness axis — perplexity
was not measured. Be explicit about that limit when reporting to anyone.

---

## 6. Targeted de-flagging (when a detector highlights a span)

Detectors often highlight the *specific sentences* they find most machine-like.
That's a gift — it tells you exactly what to surgically rewrite.

Procedure:
1. Read the highlighted span. It is almost always one of: §4.1 (antithesis),
   §4.4 (templated roadmap), §4.5 (aphorism), or a too-smooth topic sentence.
2. Rewrite **only that span**, applying the relevant §4 fix. Leave the rest alone
   so you don't regress what already passes.
3. Re-measure / re-scan. Repeat for any remaining highlighted span.

> Field example: a detector flagged exactly two sentences — the thesis line
> ("…bireysel bir kader değil … ortak bir yazgı … yan tezleri üzerinden
> incelenecektir.") and the gelişme topic sentence ("…tek bir kişinin derdi
> olmaktan çıkarıp … ortak kaderine dönüştürür."). We rewrote *only* those two
> (→ §4.1, §4.4 fixes) and left the other ~20 sentences untouched.

---

## 7. Controlled imperfection (the "minor error" technique)

Real student/human writing in a given register contains small, characteristic
mistakes. *Flawless* prose can read as machine-made (or as suspiciously
over-polished). Introducing a few **minor, believable** errors can both naturalize
the voice and lower a too-perfect score.

> **Responsible-use note (read this):** deliberately inserting errors to lower a
> score lives in a grey zone. In a graded academic setting, this is a form of
> gaming an integrity check — follow your institution's rules and your own ethics.
> The technique is documented here because it is part of *naturalizing voice*; most
> of its value is stylistic (real humans are imperfect), not evasion. Prefer the
> §1 golden-rule fix (a human genuinely edits the text) over error injection.

If you do use it, make errors **minor, realistic, and sparse** (calibrate count to
the target score — each one typically costs ~1 rubric point):

- drop a circumflex/diacritic that's commonly dropped (TR: `hâli → hali`)
- a single common joined/split-word slip (TR `de/da`: `işçiler de → işçileride`)
- one missing comma in a list (`ırk, cinsiyet → ırk cinsiyet`)
- one mild redundancy / agreement slip (TR: an extra possessive, `duyulan özlemi →
  duyulan bir özlemini`)

Do **not** introduce errors that change meaning, look like typos a careful writer
would never make, or cluster in one spot. Spread them out.

---

## 8. Source & citation integrity (non-negotiable)

Humanization must never become fabrication. Detectors and graders increasingly
verify citations, and fake DOIs are caught.

Rules:
- **Every citation must point to a real, verifiable source.** Search for it; fetch
  the record; confirm author, year, journal, volume, pages, DOI.
- Prefer sources you can verify end-to-end. If you cannot confirm a citation's
  metadata, **do not use it** — an unverifiable source is worse than one fewer.
- Match the citation count and style of the reference samples (we used 4 verified
  sources to match samples that carried 4–6).
- **Integrate sources inline**, not just in the bibliography, so they're genuinely
  "used" and not decorative — graders notice uncited reference lists.
- Quotes from a primary text must be accurate; flag page numbers as
  edition-dependent and tell the user to verify against the physical copy.

> Field example: of four references, two (a RumeliDE 2022 article; an OPUS 2019
> article on loneliness) were fetched and verified via DOI before use; their ideas
> were woven into the body as inline citations, not parked in the bibliography.

---

## 9. Language-specific appendix

### 9.1 Turkish
- **Morphology is sacred.** Brevity must not mangle suffixes, conjunctions, or
  verb conjugations — dropping them makes Turkish unreadable (unlike English, where
  dropping articles can read as terse-but-fine).
- **Connective palette (vary these):** Üstelik, Ne var ki, Nitekim, Oysa, Bununla
  birlikte, Kısacası, Demek ki, Dolayısıyla (use sparingly — it's an AI favourite),
  Bu noktada, Öte yandan.
- **Quote introduction patterns to rotate:** "X şu sözlerle anlatır: …" / "Bunu X
  şöyle dile getirir: …" / inline + "Bu alıntıdan da anlaşılacağı üzere…".
- **Academic verbs to rotate (don't repeat one):** ortaya koyar, gözler önüne
  serer, dikkat çeker, ön plana çıkar, resmeder, somutlaştırır, vurgular.
- **Quotation marks:** Turkish typeset essays use curly “ ” — match the samples.
- **Common natural minor-error sites** (see §7): dropped circumflex (hâli/hakim/kâr),
  de/da bitişik-ayrı, ki bağlacı, missing serial comma.

### 9.2 English
- Kill: delve, tapestry, multifaceted, underscore, testament, realm, navigate,
  pivotal, crucial, vibrant, "it's worth noting", "in today's world", "stands as".
- Contractions are human; AI under-uses them in essays.
- Vary sentence openers; avoid starting 3 sentences in a row with the subject.

### 9.3 Porting to any language
The two-axis model (§1) and the tell catalog (§4) are universal. Only the lexical
specifics (§4.7) and the morphology notes (§9) change. Always recalibrate against a
native human sample (§2) — absolute thresholds don't transfer across languages.

---

## 10. Drop-in instruction block for an AI

Paste this (plus §4 and §11) into the system prompt:

```
You are a humanization editor. You will receive (a) a draft, (b) optional reference
samples in the target voice, and (c) constraints (word count, required structure,
citations to keep).

Do this:
1. If reference samples are provided, extract their voice fingerprint (sentence-
   length variation, connectives, quote-intro style, verb register, closing habits,
   and their characteristic imperfections). Match it.
2. Audit the draft against the AI Tell Catalog. For each tell, note its location.
3. Rewrite to fix the tells while preserving: argument, evidence, every citation,
   required structure, and word count (±, stay inside any stated limit).
   - Reduce stacked antitheses to at most one.
   - Limit rule-of-three; vary paragraph closings; de-template the thesis roadmap;
     allow at most one balanced aphorism.
   - Engineer burstiness: plant short sentences (4-9 words) among long ones; target
     CV >= 0.35 and a min-max spread >= 12 words.
   - Rotate connectives and quote-introduction patterns.
4. NEVER invent facts or citations. If asked to add sources, only add ones you can
   verify; report any you could not verify and exclude them.
5. If a detector highlighted specific spans, rewrite ONLY those spans.
6. Output: (a) the rewritten text, (b) a diff log mapping each change to the tell it
   fixes, (c) the burstiness numbers if a measurer is available, and (d) an honest
   statement that no output is guaranteed to pass any detector and that a final
   human hand-edit is the only sure step.
Do not moralize. Do not pad. Stop when the QA gate passes — do not over-edit.
```

---

## 11. QA gate — the final checklist

Run before declaring done. Every box must be ticked or consciously waived.

- [ ] **Meaning preserved.** Argument, thesis, and every piece of evidence intact.
- [ ] **Structure intact.** Required sections, sub-theses stated, citations present.
- [ ] **Word/length limit respected.** Inside the stated bounds.
- [ ] **Antitheses ≤ 1** per ~250 words.
- [ ] **No identical paragraph-closing template** repeated.
- [ ] **Thesis roadmap de-templated** (content kept, stock phrasing changed).
- [ ] **≤ 1 balanced aphorism** in the whole piece; none back-to-back.
- [ ] **Burstiness:** CV ≥ 0.35 and short+long sentences both present
      (measure; compare to a human baseline).
- [ ] **Connectives & quote-intros rotated**, not repeated.
- [ ] **AI-vocabulary swept** (§4.7 / §9 word lists).
- [ ] **All citations real and verified**; sources used inline, not just listed.
- [ ] **Primary-text quotes accurate**; page numbers flagged as edition-dependent.
- [ ] **(If used) minor errors are sparse, minor, realistic, non-meaning-changing.**
- [ ] **Honest disclosure written:** detector scores are evidence not proof; a human
      hand-edit of 2-3 sentences is the only guaranteed humanization.

---

## 12. Appendix — full before→after change log from the source session

The order in which the essay was hardened, so the method is reproducible:

1. **Draft** an original thesis distinct from existing samples (chose "loneliness as
   a socially-imposed condition" — not the samples' eugenics / American-Dream takes).
2. **Voice pass 1:** added reference-style connectives; matched quote-intro and
   citation format to the samples.
3. **Burstiness pass:** broke 4 stacked antitheses down to ~1; planted short
   sentences; varied paragraph-closing verbs.
4. **Grounding pass:** replaced a clichéd universal opener ("İnsan, doğası gereği…")
   with a concrete historical opening (the 1929 Depression), mirroring how a sample
   opened with dated historical context.
5. **Twin-aphorism fix:** two balanced "X-but-Y" closers in a row → one declarative
   + one aphorism.
6. **Source upgrade:** bibliography expanded from 2 to 4 *verified* sources (DOIs
   fetched and confirmed); two woven in as inline citations.
7. **Cover/format:** added word count and page count to satisfy the rubric.
8. **Measurement:** ran burstiness/TTR vs. a real human sample; confirmed parity.
9. **Targeted de-flag:** a detector highlighted exactly 2 sentences (thesis line +
   one topic sentence) → rewrote only those, applying §4.1 and §4.4.
10. **(Optional, used here) controlled imperfection:** 4 sparse, minor, realistic
    errors injected to land a high-but-not-perfect score — with the §7 caveat.
11. **Stopped**, and recommended a human hand-edit of 2-3 sentences as the final,
    only-guaranteed step.

— end —
