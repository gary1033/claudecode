#!/usr/bin/env python3
"""
test_case_reader.py

Reads all .feature files and extracts the **action** and **target** from every
numbered test step using six NLP methods:

  1. Rule-based Regex
  2. Keyword + Pattern Heuristics
  3. NLTK POS Tagging
  4. NLTK Shallow Chunking (NP/VP grammar)
  5. spaCy Dependency Parsing
  6. Ensemble Voting (combines methods 1-5)

Results are written to:
  - nlp_analysis_results.json   (full per-step breakdown)
  - nlp_methods_comparison.md   (method descriptions, pros/cons, examples)
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

# ─── Optional NLP library detection ──────────────────────────────────────────

try:
    import nltk
    for _pkg, _kind in [
        ('punkt_tab',                    'tokenizers'),
        ('averaged_perceptron_tagger_eng','taggers'),
        ('maxent_ne_chunker_tab',         'chunkers'),
        ('words',                         'corpora'),
    ]:
        try:
            nltk.data.find(f'{_kind}/{_pkg}')
        except LookupError:
            nltk.download(_pkg, quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import spacy
    _NLP = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    _NLP = None


# ─── Shared vocabulary ───────────────────────────────────────────────────────

ACTION_VOCAB = {
    'launch', 'navigate', 'verify', 'click', 'enter', 'scroll', 'fill',
    'select', 'check', 'submit', 'wait', 'search', 'type', 'press',
    'hover', 'drag', 'drop', 'upload', 'download', 'open', 'close',
    'refresh', 'filter', 'register', 'login', 'logout', 'add', 'delete', 'edit',
}

SKIP_WORDS = {'on', 'to', 'in', 'at', 'into', 'with', 'that', 'down', 'the', 'a', 'an'}


# ─── Result container ────────────────────────────────────────────────────────

class StepAnalysis(NamedTuple):
    method:     str
    action:     str
    target:     str
    confidence: float   # 0.0–1.0
    notes:      str


# ─────────────────────────────────────────────────────────────────────────────
# METHOD 1 – Rule-based Regex
# ─────────────────────────────────────────────────────────────────────────────

def method_regex(step: str) -> StepAnalysis:
    """
    Matches the first token against a known action vocabulary.
    Uses quoted strings as the preferred target; otherwise takes the
    noun phrase that follows after stripping leading prepositions.
    """
    tokens = step.split()
    if not tokens:
        return StepAnalysis('regex', '', '', 0.0, 'empty step')

    first = tokens[0].lower().rstrip('.,')
    in_vocab = first in ACTION_VOCAB
    action = tokens[0]
    confidence = 0.80 if in_vocab else 0.30

    # Prefer any quoted string as the target
    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted:
        target = quoted[0]
        confidence = min(confidence + 0.10, 1.0)
    else:
        rest = tokens[1:]
        # Skip leading prepositions / determiners
        while rest and rest[0].lower() in SKIP_WORDS:
            rest = rest[1:]
        # Cut off at secondary clause markers
        trimmed: List[str] = []
        for t in rest:
            if t.lower() in ('and', 'is', 'are', 'was', 'were'):
                break
            trimmed.append(t)
        target = ' '.join(trimmed)

    return StepAnalysis('regex', action, target, round(confidence, 3),
                        f"verb_in_vocab={in_vocab}")


# ─────────────────────────────────────────────────────────────────────────────
# METHOD 2 – Keyword + Pattern Heuristics
# ─────────────────────────────────────────────────────────────────────────────

_PATTERNS: List[tuple] = [
    # Navigate to url '...'
    (re.compile(r"^(navigate)\s+to\s+url\s+['\"]([^'\"]+)['\"]", re.I), 2),
    # Click on/Click 'X' [button/link/...]
    (re.compile(r"^(click)\s+(?:on\s+)?['\"]([^'\"]+)['\"]", re.I), 2),
    # Verify [that/text/error/success message] 'X' [is ...]
    (re.compile(r"^(verify)\s+(?:that\s+|text\s+|error\s+|success\s+message\s+)?['\"]([^'\"]+)['\"]", re.I), 2),
    # Enter X in/into/and
    (re.compile(r"^(enter)\s+(.+?)\s+(?:in|into|and)\s+", re.I), 2),
    # Scroll down to X
    (re.compile(r"^(scroll)\s+(?:down\s+)?(?:to\s+)?(.+)", re.I), 2),
    # Launch X
    (re.compile(r"^(launch)\s+(.+)", re.I), 2),
    # Verify that X is visible ...
    (re.compile(r"^(verify)\s+that\s+(.+?)\s+(?:is|are)\b", re.I), 2),
    # Generic: VERB [prep] TARGET [is/are ...]
    (re.compile(r"^(\w+)\s+(?:on\s+|to\s+|in\s+|at\s+|that\s+)?(.+?)(?:\s+is\s+|\s+are\s+|$)", re.I), 2),
]

def method_keyword_heuristic(step: str) -> StepAnalysis:
    """
    Ordered regex pattern set tuned to common BDD web-test phrasings.
    Quoted strings are extracted as high-confidence targets when present.
    """
    for pattern, grp in _PATTERNS:
        m = pattern.match(step)
        if m:
            action = m.group(1)
            raw_target = m.group(grp) if grp <= len(m.groups()) else ''
            target = re.sub(r"['\"]", '', raw_target).strip()
            is_named = grp == 2 and pattern.pattern != _PATTERNS[-1][0].pattern
            confidence = 0.90 if is_named else 0.65
            return StepAnalysis('keyword', action, target, confidence,
                                f"pattern={'named' if is_named else 'generic'}")

    tokens = step.split()
    return StepAnalysis('keyword',
                        tokens[0] if tokens else '',
                        ' '.join(tokens[1:]),
                        0.30, 'no_pattern_matched')


# ─────────────────────────────────────────────────────────────────────────────
# METHOD 3 – NLTK POS Tagging
# ─────────────────────────────────────────────────────────────────────────────

def method_nltk_pos(step: str) -> StepAnalysis:
    """
    POS-tags all tokens with NLTK's averaged perceptron tagger.
    The first VB* token becomes the action; the contiguous noun phrase
    immediately following (NN*, JJ, DT, CD) becomes the target.
    Quoted strings override the extracted NP as target.
    """
    if not NLTK_AVAILABLE:
        return StepAnalysis('nltk_pos', '', '', 0.0, 'NLTK not available')

    tokens  = nltk.word_tokenize(step)
    tagged  = nltk.pos_tag(tokens)

    action = ''
    target_tokens: List[str] = []
    found_verb = False
    in_np = False

    for word, tag in tagged:
        if not found_verb:
            if tag.startswith('VB'):
                action = word
                found_verb = True
        else:
            if tag in ('NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'DT', 'CD'):
                target_tokens.append(word)
                in_np = True
            elif tag in ('IN', 'TO') and in_np:
                target_tokens.append(word)   # include prepositions inside NP
            elif in_np:
                break                        # NP ended

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted and action:
        target = quoted[0]
        confidence = 0.85
    else:
        target = ' '.join(target_tokens)
        confidence = 0.70 if action else 0.20

    first5 = [(w, t) for w, t in tagged[:5]]
    return StepAnalysis('nltk_pos', action, target, confidence,
                        f"tagged={first5}")


# ─────────────────────────────────────────────────────────────────────────────
# METHOD 4 – NLTK Shallow Chunking
# ─────────────────────────────────────────────────────────────────────────────

_CHUNK_GRAMMAR = r"""
    VP: {<VB.*><RP|IN|TO>?<RB>?}
    NP: {<DT>?<JJ.*>*<NN.*>+}
"""

def method_nltk_chunk(step: str) -> StepAnalysis:
    """
    Applies a hand-crafted CFG grammar with NLTK's RegexpParser to identify
    VP (verb phrases) and NP (noun phrases).  The first VP gives the action
    and the first NP that follows gives the target.
    Quoted strings override the NP target.
    """
    if not NLTK_AVAILABLE:
        return StepAnalysis('nltk_chunk', '', '', 0.0, 'NLTK not available')

    tokens = nltk.word_tokenize(step)
    tagged = nltk.pos_tag(tokens)

    cp   = nltk.RegexpParser(_CHUNK_GRAMMAR)
    tree = cp.parse(tagged)

    action   = ''
    target   = ''
    vp_found = False

    for subtree in tree:
        if hasattr(subtree, 'label'):
            label = subtree.label()
            words = ' '.join(w for w, _ in subtree.leaves())
            if label == 'VP' and not vp_found:
                action   = words
                vp_found = True
            elif label == 'NP' and vp_found and not target:
                target = words
        else:
            # Bare token (not chunked)
            word, tag = subtree
            if tag.startswith('VB') and not action:
                action   = word
                vp_found = True

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted and action:
        target     = quoted[0]
        confidence = 0.85
    else:
        confidence = 0.75 if (action and target) else 0.40

    chunk_labels = [
        s.label() if hasattr(s, 'label') else s[1]
        for s in tree
    ]
    return StepAnalysis('nltk_chunk', action, target, confidence,
                        f"chunk_labels={chunk_labels[:6]}")


# ─────────────────────────────────────────────────────────────────────────────
# METHOD 5 – spaCy Dependency Parsing
# ─────────────────────────────────────────────────────────────────────────────

def method_spacy_dep(step: str) -> StepAnalysis:
    """
    Uses spaCy's en_core_web_sm model to find the ROOT verb (action) and
    its direct object (dobj) or prepositional object (pobj) as the target.
    Full noun-phrase spans are recovered via token.left_edge / right_edge.
    Quoted strings override the parsed target.
    """
    if not SPACY_AVAILABLE or _NLP is None:
        return StepAnalysis('spacy_dep', '', '', 0.0, 'spaCy/model not available')

    doc    = _NLP(step)
    root   = next((t for t in doc if t.dep_ == 'ROOT'), None)
    action = root.text if root else ''
    target = ''

    if root:
        # Prefer direct object
        dobj = next((t for t in root.children if t.dep_ == 'dobj'), None)
        if dobj:
            target = doc[dobj.left_edge.i: dobj.right_edge.i + 1].text
        else:
            # Fall back to prepositional object
            for child in root.children:
                if child.dep_ == 'prep':
                    pobj = next((t for t in child.children if t.dep_ == 'pobj'), None)
                    if pobj:
                        target = doc[pobj.left_edge.i: pobj.right_edge.i + 1].text
                        break

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted and action:
        target     = quoted[0]
        confidence = 0.90
    else:
        confidence = 0.80 if (action and target) else 0.50

    dep_labels = [t.dep_ for t in doc][:6]
    return StepAnalysis('spacy_dep', action, target, confidence,
                        f"root={action}, dep_labels={dep_labels}")


# ─────────────────────────────────────────────────────────────────────────────
# METHOD 6 – Ensemble Voting
# ─────────────────────────────────────────────────────────────────────────────

def method_ensemble(step: str, results: List[StepAnalysis]) -> StepAnalysis:
    """
    Aggregates predictions from methods 1-5 using confidence-weighted voting.
    The action/target receiving the highest total weight wins.
    Confidence is the weighted average plus a small consensus bonus (capped at 1.0).
    """
    valid = [r for r in results if r.action]
    if not valid:
        return StepAnalysis('ensemble', '', '', 0.0, 'no valid inputs')

    action_votes: Dict[str, float] = Counter()
    target_votes: Dict[str, float] = Counter()

    for r in valid:
        action_votes[r.action.lower()] += r.confidence
        if r.target:
            target_votes[r.target.lower()] += r.confidence

    # BDD imperative prior: in BDD steps the first token is always the action verb.
    # Give it a strong bonus so auxiliary verbs (is/are) from NLP parsers don't win.
    first_token = step.split()[0].lower().rstrip('.,') if step.split() else ''
    if first_token in ACTION_VOCAB:
        action_votes[first_token] += 2.0

    # Secondary bonus: any ACTION_VOCAB word gets a smaller boost to beat auxiliaries.
    for key in list(action_votes):
        if key != first_token and key in ACTION_VOCAB:
            action_votes[key] += 0.30

    best_action_key = max(action_votes, key=action_votes.__getitem__)
    best_action = next(
        r.action for r in valid if r.action.lower() == best_action_key
    )

    best_target = ''
    if target_votes:
        best_target_key = max(target_votes, key=target_votes.__getitem__)
        best_target = next(
            (r.target for r in valid if r.target.lower() == best_target_key),
            best_target_key,
        )

    avg_conf = sum(r.confidence for r in valid) / len(valid)
    confidence = min(avg_conf + 0.05, 1.0)

    return StepAnalysis(
        'ensemble', best_action, best_target, round(confidence, 3),
        f"votes_action={dict(action_votes)}, n_methods={len(valid)}",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Feature-file parser
# ─────────────────────────────────────────────────────────────────────────────

_STEP_RE = re.compile(r'^\d+\.\s+(.+)')

def parse_feature_file(path: Path) -> Dict:
    """
    Extracts URLs, title, and numbered steps from a .feature file.
    Ignores any embedded JSON blocks (present in some files).
    """
    raw = path.read_text(encoding='utf-8')
    # Discard everything from the first '{' onwards (JSON residue)
    text = raw.split('{')[0] if '{' in raw else raw

    urls: List[str] = []
    title = ''
    steps: List[str] = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith('urls = '):
            try:
                urls = json.loads(line[len('urls = '):])
            except json.JSONDecodeError:
                urls = re.findall(r'https?://[^\s\'"]+', line)
        elif line.startswith('Test Case'):
            title = line
        else:
            m = _STEP_RE.match(line)
            if m:
                steps.append(m.group(1).strip().rstrip())

    return {'file': path.name, 'urls': urls, 'title': title, 'steps': steps}


# ─────────────────────────────────────────────────────────────────────────────
# Per-step analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyse_step(step: str) -> Dict:
    """Run all six methods on a single step and return a structured dict."""
    r1 = method_regex(step)
    r2 = method_keyword_heuristic(step)
    r3 = method_nltk_pos(step)
    r4 = method_nltk_chunk(step)
    r5 = method_spacy_dep(step)
    r6 = method_ensemble(step, [r1, r2, r3, r4, r5])

    return {
        'step': step,
        'analyses': [
            {
                'method':     r.method,
                'action':     r.action,
                'target':     r.target,
                'confidence': round(r.confidence, 3),
                'notes':      r.notes,
            }
            for r in (r1, r2, r3, r4, r5, r6)
        ],
        'best': {
            'action':     r6.action,
            'target':     r6.target,
            'confidence': round(r6.confidence, 3),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Comparison report generator
# ─────────────────────────────────────────────────────────────────────────────

def _collect_examples(all_cases: List[Dict]) -> Dict[str, List[Dict]]:
    """Pick up to 3 illustrative step results per method."""
    examples: Dict[str, List[Dict]] = {
        m: [] for m in ('regex', 'keyword', 'nltk_pos', 'nltk_chunk', 'spacy_dep', 'ensemble')
    }
    for tc in all_cases:
        for sr in tc.get('analysed_steps', []):
            for a in sr['analyses']:
                m = a['method']
                if len(examples[m]) < 3 and a['action']:
                    examples[m].append({
                        'step':   sr['step'],
                        'action': a['action'],
                        'target': a['target'],
                        'conf':   a['confidence'],
                    })
    return examples


_METHOD_META = [
    {
        'id':    'regex',
        'title': 'Method 1 – Rule-based Regex',
        'desc':  (
            'Splits the step text on whitespace. The first token is matched '
            'against a predefined `ACTION_VOCAB` set. Quoted strings are '
            'preferred as targets; otherwise the noun phrase after stripping '
            'leading prepositions is used.'
        ),
        'pros': [
            'Zero external dependencies – runs everywhere.',
            'Deterministic and fully explainable.',
            'Extremely fast (microseconds per step).',
            'High accuracy for steps that follow strict BDD conventions.',
        ],
        'cons': [
            'Blind to grammar – treats every first token as a potential verb.',
            'Target extraction degrades when no quoted string is present.',
            'Requires manual maintenance of `ACTION_VOCAB`.',
            'Cannot handle complex or nested clauses.',
        ],
    },
    {
        'id':    'keyword',
        'title': 'Method 2 – Keyword + Pattern Heuristics',
        'desc':  (
            'Applies an ordered list of compiled regex patterns, each tuned '
            'to a specific BDD phrasing (e.g., "navigate to url", '
            '"click on \'X\' button", "verify \'X\' is visible"). '
            'Falls back to a generic VERB + TARGET pattern.'
        ),
        'pros': [
            'Very precise for the patterns it covers.',
            'Distinguishes action type (NAVIGATE, CLICK, VERIFY, …).',
            'No external dependencies.',
            'Patterns are easy to audit and extend.',
        ],
        'cons': [
            'Coverage is limited to hand-written patterns.',
            'Order-sensitive: early patterns shadow later ones.',
            'Generic fallback pattern has lower confidence.',
            'Does not understand sentence structure beyond surface form.',
        ],
    },
    {
        'id':    'nltk_pos',
        'title': 'Method 3 – NLTK POS Tagging',
        'desc':  (
            'Tokenises with `nltk.word_tokenize` and tags each token using '
            'the averaged perceptron tagger. The first `VB*` tag is the action; '
            'the contiguous sequence of `NN*`, `JJ`, `DT`, `CD` tokens that '
            'follows is collected as the target noun phrase.'
        ),
        'pros': [
            'Linguistically grounded – not dependent on surface word order alone.',
            'Handles morphological variants (clicks, clicking, clicked).',
            'Freely available; small download footprint.',
            'Quoted-string override adds robustness for quoted targets.',
        ],
        'cons': [
            'Domain vocabulary (e.g., "footer", "arrow") may be mis-tagged.',
            'Simple NP heuristic breaks for PP-attached or coordinated NPs.',
            'Slower than pure regex.',
            'Requires NLTK data download at first run.',
        ],
    },
    {
        'id':    'nltk_chunk',
        'title': 'Method 4 – NLTK Shallow Chunking',
        'desc':  (
            'Parses POS-tagged tokens with `nltk.RegexpParser` using a '
            'hand-written CFG grammar that defines VP (verb phrases) and '
            'NP (noun phrases). The first VP chunk gives the full action '
            'phrase; the first NP chunk after it gives the target.'
        ),
        'pros': [
            'Captures multi-word action phrases (e.g., "scroll down to").',
            'Grammar rules are transparent and adjustable.',
            'Produces richer action labels than single-verb extraction.',
            'Still usable without GPU or large model.',
        ],
        'cons': [
            'CFG grammar requires manual tuning per domain.',
            'Shallow parsing misses long-distance dependencies.',
            'Performance degrades when POS tags are incorrect.',
            'More complex to debug than flat regex.',
        ],
    },
    {
        'id':    'spacy_dep',
        'title': 'Method 5 – spaCy Dependency Parsing',
        'desc':  (
            'Runs spaCy\'s `en_core_web_sm` neural pipeline on each step. '
            'The ROOT token (typically the main verb) is the action. '
            'The direct object (`dobj`) or, failing that, the prepositional '
            'object (`pobj`) of the root is used as the target, expanded '
            'to its full noun-phrase span via `left_edge`/`right_edge`.'
        ),
        'pros': [
            'Most linguistically accurate – understands syntactic roles.',
            'Handles complex sentences with subordinate clauses.',
            'Full NP spans include determiners and adjectives.',
            'Quoted-string override keeps precision high for BDD steps.',
        ],
        'cons': [
            'Requires spaCy and the `en_core_web_sm` model (~12 MB).',
            'Slowest method (~5–20× slower than regex).',
            'Neural model may produce unexpected parses for unusual phrasings.',
            'Overkill for simple imperative sentences typical in BDD.',
        ],
    },
    {
        'id':    'ensemble',
        'title': 'Method 6 – Ensemble Voting',
        'desc':  (
            'Collects the action and target from methods 1–5 and runs '
            'confidence-weighted voting: each method\'s prediction is '
            'weighted by its reported confidence score. The candidate '
            'with the highest accumulated weight wins. Final confidence '
            'is the weighted average plus a small consensus bonus (≤ 1.0).'
        ),
        'pros': [
            'Reduces the impact of individual method errors.',
            'Naturally degrades gracefully when some methods are unavailable.',
            'Self-documenting: shows how much each method agreed.',
            'Generally higher precision than any single method alone.',
        ],
        'cons': [
            'Inherits all methods\' shared blind spots (e.g., all prefer quoted strings).',
            'Confidence scores are heuristic, not empirically calibrated.',
            'Adds latency equal to the sum of all constituent methods.',
            'May "average out" a correct minority prediction.',
        ],
    },
]


def generate_comparison_report(
    all_cases: List[Dict],
    out_path: str = 'nlp_methods_comparison.md',
) -> None:
    """Write a Markdown report comparing all six NLP methods with examples."""
    examples = _collect_examples(all_cases)
    lines: List[str] = []

    lines += [
        '# NLP Methods Comparison Report',
        '',
        'This document records every NLP approach used in `test_case_reader.py`',
        'to extract **action** and **target** from `.feature` test steps,',
        'along with their strengths, weaknesses, and real output examples.',
        '',
        '---',
        '',
        '## Overview',
        '',
        '| # | Method | Requires | Speed | Typical Confidence |',
        '|---|--------|----------|-------|-------------------|',
        '| 1 | Rule-based Regex | stdlib only | ★★★★★ | 0.80–0.90 |',
        '| 2 | Keyword + Pattern Heuristics | stdlib only | ★★★★★ | 0.65–0.92 |',
        '| 3 | NLTK POS Tagging | NLTK | ★★★★☆ | 0.70–0.85 |',
        '| 4 | NLTK Shallow Chunking | NLTK | ★★★☆☆ | 0.75–0.85 |',
        '| 5 | spaCy Dependency Parsing | spaCy + model | ★★☆☆☆ | 0.80–0.90 |',
        '| 6 | Ensemble Voting | all above | ★★☆☆☆ | 0.80–0.95 |',
        '',
        '---',
        '',
    ]

    for meta in _METHOD_META:
        mid = meta['id']
        lines += [
            f"## {meta['title']}",
            '',
            f"**Description:** {meta['desc']}",
            '',
            '### Pros',
            *[f'- {p}' for p in meta['pros']],
            '',
            '### Cons',
            *[f'- {c}' for c in meta['cons']],
            '',
        ]

        exs = examples.get(mid, [])
        if exs:
            lines += [
                '### Example Output',
                '',
                '| Step | Action | Target | Confidence |',
                '|------|--------|--------|-----------|',
            ]
            for e in exs:
                step   = e['step'].replace('|', '\\|')
                action = e['action'].replace('|', '\\|')
                target = e['target'].replace('|', '\\|') if e['target'] else '*(none)*'
                lines.append(f"| {step} | `{action}` | {target} | {e['conf']} |")
            lines.append('')

        lines.append('---')
        lines.append('')

    lines += [
        '## Recommendations',
        '',
        '- **Production / no-install environment**: Use Method 2 (Keyword Heuristics)',
        '  as primary, with Method 1 as fallback. Both run on stdlib only.',
        '',
        '- **Best single-method accuracy**: Use Method 5 (spaCy) when the',
        '  `en_core_web_sm` model is available. It understands syntax rather than',
        '  pattern-matching surface forms.',
        '',
        '- **Highest overall precision**: Use Method 6 (Ensemble). It combines',
        '  the strengths of all other methods and degrades gracefully when',
        '  optional libraries are missing.',
        '',
        '- **Extending coverage**: Add new regex patterns to `_PATTERNS` in',
        '  Method 2 and new verbs to `ACTION_VOCAB` for Method 1/3/4.',
        '',
        '---',
        '',
        '_Report auto-generated by `test_case_reader.py`_',
    ]

    Path(out_path).write_text('\n'.join(lines), encoding='utf-8')
    print(f'Comparison report  → {out_path}')


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def run(files_dir: str = '.') -> List[Dict]:
    feature_files = sorted(Path(files_dir).glob('*.feature'))
    print(f'Found {len(feature_files)} .feature file(s)')
    print(f'NLTK  : {"available" if NLTK_AVAILABLE  else "unavailable"}')
    print(f'spaCy : {"available" if SPACY_AVAILABLE else "unavailable"}')
    print()

    all_cases: List[Dict] = []

    for fp in feature_files:
        tc = parse_feature_file(fp)
        print(f"{'='*70}")
        print(f"File : {tc['file']}")
        print(f"Title: {tc['title']}")
        print(f"URLs : {tc['urls']}")
        print()

        analysed_steps: List[Dict] = []
        for i, step in enumerate(tc['steps'], 1):
            result = analyse_step(step)
            analysed_steps.append(result)
            best = result['best']
            action_str = best['action'] or '(none)'
            target_str = best['target'] or '(none)'
            print(f"  Step {i:2d}: {step}")
            print(f"          Action → {action_str:<22s} Target → {target_str}")

        print()
        all_cases.append({**tc, 'analysed_steps': analysed_steps})

    return all_cases


if __name__ == '__main__':
    results = run('.')

    # Save full JSON results
    out_json = 'nlp_analysis_results.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'Full results       → {out_json}')

    # Generate comparison markdown
    generate_comparison_report(results, 'nlp_methods_comparison.md')
