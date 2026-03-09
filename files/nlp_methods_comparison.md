# NLP Methods Comparison Report

This document records every NLP approach used in `test_case_reader.py`
to extract **action** and **target** from `.feature` test steps,
along with their strengths, weaknesses, and real output examples.

---

## Overview

| # | Method | Requires | Speed | Typical Confidence |
|---|--------|----------|-------|-------------------|
| 1 | Rule-based Regex | stdlib only | ★★★★★ | 0.80–0.90 |
| 2 | Keyword + Pattern Heuristics | stdlib only | ★★★★★ | 0.65–0.92 |
| 3 | NLTK POS Tagging | NLTK | ★★★★☆ | 0.70–0.85 |
| 4 | NLTK Shallow Chunking | NLTK | ★★★☆☆ | 0.75–0.85 |
| 5 | spaCy Dependency Parsing | spaCy + model | ★★☆☆☆ | 0.80–0.90 |
| 6 | Ensemble Voting | all above | ★★☆☆☆ | 0.80–0.95 |

---

## Method 1 – Rule-based Regex

**Description:** Splits the step text on whitespace. The first token is matched against a predefined `ACTION_VOCAB` set. Quoted strings are preferred as targets; otherwise the noun phrase after stripping leading prepositions is used.

### Pros
- Zero external dependencies – runs everywhere.
- Deterministic and fully explainable.
- Extremely fast (microseconds per step).
- High accuracy for steps that follow strict BDD conventions.

### Cons
- Blind to grammar – treats every first token as a potential verb.
- Target extraction degrades when no quoted string is present.
- Requires manual maintenance of `ACTION_VOCAB`.
- Cannot handle complex or nested clauses.

### Example Output

| Step | Action | Target | Confidence |
|------|--------|--------|-----------|
| Launch browser | `Launch` | browser | 0.8 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.9 |
| Verify that home page is visible successfully | `Verify` | home page | 0.8 |

---

## Method 2 – Keyword + Pattern Heuristics

**Description:** Applies an ordered list of compiled regex patterns, each tuned to a specific BDD phrasing (e.g., "navigate to url", "click on 'X' button", "verify 'X' is visible"). Falls back to a generic VERB + TARGET pattern.

### Pros
- Very precise for the patterns it covers.
- Distinguishes action type (NAVIGATE, CLICK, VERIFY, …).
- No external dependencies.
- Patterns are easy to audit and extend.

### Cons
- Coverage is limited to hand-written patterns.
- Order-sensitive: early patterns shadow later ones.
- Generic fallback pattern has lower confidence.
- Does not understand sentence structure beyond surface form.

### Example Output

| Step | Action | Target | Confidence |
|------|--------|--------|-----------|
| Launch browser | `Launch` | browser | 0.9 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.9 |
| Verify that home page is visible successfully | `Verify` | home page | 0.9 |

---

## Method 3 – NLTK POS Tagging

**Description:** Tokenises with `nltk.word_tokenize` and tags each token using the averaged perceptron tagger. The first `VB*` tag is the action; the contiguous sequence of `NN*`, `JJ`, `DT`, `CD` tokens that follows is collected as the target noun phrase.

### Pros
- Linguistically grounded – not dependent on surface word order alone.
- Handles morphological variants (clicks, clicking, clicked).
- Freely available; small download footprint.
- Quoted-string override adds robustness for quoted targets.

### Cons
- Domain vocabulary (e.g., "footer", "arrow") may be mis-tagged.
- Simple NP heuristic breaks for PP-attached or coordinated NPs.
- Slower than pure regex.
- Requires NLTK data download at first run.

### Example Output

| Step | Action | Target | Confidence |
|------|--------|--------|-----------|
| Navigate to url 'http://automationexercise.com' | `url` | http://automationexercise.com | 0.85 |
| Verify that home page is visible successfully | `Verify` | that home page | 0.7 |
| Scroll down to footer | `footer` | *(none)* | 0.7 |

---

## Method 4 – NLTK Shallow Chunking

**Description:** Parses POS-tagged tokens with `nltk.RegexpParser` using a hand-written CFG grammar that defines VP (verb phrases) and NP (noun phrases). The first VP chunk gives the full action phrase; the first NP chunk after it gives the target.

### Pros
- Captures multi-word action phrases (e.g., "scroll down to").
- Grammar rules are transparent and adjustable.
- Produces richer action labels than single-verb extraction.
- Still usable without GPU or large model.

### Cons
- CFG grammar requires manual tuning per domain.
- Shallow parsing misses long-distance dependencies.
- Performance degrades when POS tags are incorrect.
- More complex to debug than flat regex.

### Example Output

| Step | Action | Target | Confidence |
|------|--------|--------|-----------|
| Navigate to url 'http://automationexercise.com' | `url` | http://automationexercise.com | 0.85 |
| Verify that home page is visible successfully | `Verify` | that home page | 0.75 |
| Scroll down to footer | `footer` | *(none)* | 0.4 |

---

## Method 5 – spaCy Dependency Parsing

**Description:** Runs spaCy's `en_core_web_sm` neural pipeline on each step. The ROOT token (typically the main verb) is the action. The direct object (`dobj`) or, failing that, the prepositional object (`pobj`) of the root is used as the target, expanded to its full noun-phrase span via `left_edge`/`right_edge`.

### Pros
- Most linguistically accurate – understands syntactic roles.
- Handles complex sentences with subordinate clauses.
- Full NP spans include determiners and adjectives.
- Quoted-string override keeps precision high for BDD steps.

### Cons
- Requires spaCy and the `en_core_web_sm` model (~12 MB).
- Slowest method (~5–20× slower than regex).
- Neural model may produce unexpected parses for unusual phrasings.
- Overkill for simple imperative sentences typical in BDD.

### Example Output

| Step | Action | Target | Confidence |
|------|--------|--------|-----------|
| Launch browser | `browser` | *(none)* | 0.5 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.9 |
| Verify that home page is visible successfully | `is` | *(none)* | 0.5 |

---

## Method 6 – Ensemble Voting

**Description:** Collects the action and target from methods 1–5 and runs confidence-weighted voting: each method's prediction is weighted by its reported confidence score. The candidate with the highest accumulated weight wins. Final confidence is the weighted average plus a small consensus bonus (≤ 1.0).

### Pros
- Reduces the impact of individual method errors.
- Naturally degrades gracefully when some methods are unavailable.
- Self-documenting: shows how much each method agreed.
- Generally higher precision than any single method alone.

### Cons
- Inherits all methods' shared blind spots (e.g., all prefer quoted strings).
- Confidence scores are heuristic, not empirically calibrated.
- Adds latency equal to the sum of all constituent methods.
- May "average out" a correct minority prediction.

### Example Output

| Step | Action | Target | Confidence |
|------|--------|--------|-----------|
| Launch browser | `Launch` | browser | 0.783 |
| Navigate to url 'http://automationexercise.com' | `Navigate` | http://automationexercise.com | 0.93 |
| Verify that home page is visible successfully | `Verify` | home page | 0.78 |

---

## Recommendations

- **Production / no-install environment**: Use Method 2 (Keyword Heuristics)
  as primary, with Method 1 as fallback. Both run on stdlib only.

- **Best single-method accuracy**: Use Method 5 (spaCy) when the
  `en_core_web_sm` model is available. It understands syntax rather than
  pattern-matching surface forms.

- **Highest overall precision**: Use Method 6 (Ensemble). It combines
  the strengths of all other methods and degrades gracefully when
  optional libraries are missing.

- **Extending coverage**: Add new regex patterns to `_PATTERNS` in
  Method 2 and new verbs to `ACTION_VOCAB` for Method 1/3/4.

---

_Report auto-generated by `test_case_reader.py`_