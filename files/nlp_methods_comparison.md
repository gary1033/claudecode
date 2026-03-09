# NLP Methods Comparison Report

Records every NLP approach used to extract **action** and **target**
from `.feature` test steps, with pros, cons, and real output examples.

> Each method also has its own standalone Python file (listed below).

---

## Overview

| # | Method | File | Requires | Speed | Typical Confidence |
|---|--------|------|----------|-------|-------------------|
| 1 | Rule-based Regex | `method1_regex.py` | stdlib only | ★★★★★ | 0.80–0.90 |
| 2 | Keyword + Pattern Heuristics | `method2_keyword.py` | stdlib only | ★★★★★ | 0.65–0.92 |
| 3 | NLTK POS Tagging | `method3_nltk_pos.py` | NLTK | ★★★★☆ | 0.70–0.85 |
| 4 | NLTK Shallow Chunking | `method4_nltk_chunk.py` | NLTK | ★★★☆☆ | 0.75–0.85 |
| 5 | spaCy Dependency Parsing | `method5_spacy_dep.py` | spaCy + model | ★★☆☆☆ | 0.80–0.90 |
| 6 | Ensemble Voting | `method6_ensemble.py` | all above | ★★☆☆☆ | 0.80–0.95 |

---

## Method 1 – Rule-based Regex

**File:** `method1_regex.py`

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

**File:** `method2_keyword.py`

**Description:** Applies an ordered list of compiled regex patterns, each tuned to a specific BDD phrasing (navigate to url, click on 'X', verify 'X' is visible, …). Falls back to a generic VERB + TARGET pattern.

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

**File:** `method3_nltk_pos.py`

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

**File:** `method4_nltk_chunk.py`

**Description:** Parses POS-tagged tokens with `nltk.RegexpParser` using a hand-crafted CFG grammar that defines VP (verb phrases) and NP (noun phrases). The first VP chunk gives the full action phrase; the first NP chunk after it gives the target.

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

**File:** `method5_spacy_dep.py`

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

**File:** `method6_ensemble.py`

**Description:** Aggregates predictions from methods 1–5 using confidence-weighted voting.  Applies a BDD imperative prior (+2.0 for first-token in ACTION_VOCAB) to prevent auxiliary verbs from winning. Final confidence = weighted average + 0.05 consensus bonus (≤ 1.0).

### Pros
- Reduces the impact of individual method errors.
- BDD imperative prior prevents auxiliary verb mis-labelling.
- Degrades gracefully when optional libraries are unavailable.
- Generally higher precision than any single method alone.

### Cons
- Inherits shared blind spots across all constituent methods.
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

- **No-install environment**: Method 2 (Keyword Heuristics) as primary, Method 1 as fallback.
- **Best single-method accuracy**: Method 5 (spaCy) when the model is available.
- **Highest overall precision**: Method 6 (Ensemble) combining all methods.
- **Extending coverage**: add patterns to `method2_keyword.py` and verbs to `ACTION_VOCAB` in `nlp_common.py`.

---

_Report auto-generated by `test_case_reader.py`_