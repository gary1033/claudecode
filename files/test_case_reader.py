#!/usr/bin/env python3
"""
test_case_reader.py

Orchestrator: reads all .feature files and extracts action + target from every
numbered test step by running all six NLP methods.

Each method lives in its own module and can also be run standalone:
    python3 method1_regex.py
    python3 method2_keyword.py
    python3 method3_nltk_pos.py
    python3 method4_nltk_chunk.py
    python3 method5_spacy_dep.py
    python3 method6_ensemble.py

Results are written to:
    nlp_analysis_results.json   — full per-step breakdown across all methods
    nlp_methods_comparison.md   — auto-generated pros/cons/examples report
"""

import json
from pathlib import Path
from typing import Dict, List

from nlp_common import (
    NLTK_AVAILABLE, SPACY_AVAILABLE,
    StepAnalysis, parse_feature_file,
)
from method1_regex    import analyse as m1
from method2_keyword  import analyse as m2
from method3_nltk_pos import analyse as m3
from method4_nltk_chunk import analyse as m4
from method5_spacy_dep  import analyse as m5
from method6_ensemble   import analyse as m6


# ─── Per-step analysis ────────────────────────────────────────────────────────

def analyse_step(step: str) -> Dict:
    """Run all six methods on a single step and return a structured dict."""
    results = [m1(step), m2(step), m3(step), m4(step), m5(step), m6(step)]
    best = results[-1]  # ensemble

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
            for r in results
        ],
        'best': {
            'action':     best.action,
            'target':     best.target,
            'confidence': round(best.confidence, 3),
        },
    }


# ─── Comparison report ────────────────────────────────────────────────────────

_METHOD_META = [
    {
        'id': 'regex', 'title': 'Method 1 – Rule-based Regex',
        'file': 'method1_regex.py',
        'desc': (
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
        'id': 'keyword', 'title': 'Method 2 – Keyword + Pattern Heuristics',
        'file': 'method2_keyword.py',
        'desc': (
            'Applies an ordered list of compiled regex patterns, each tuned '
            'to a specific BDD phrasing (navigate to url, click on \'X\', '
            'verify \'X\' is visible, …). Falls back to a generic VERB + TARGET pattern.'
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
        'id': 'nltk_pos', 'title': 'Method 3 – NLTK POS Tagging',
        'file': 'method3_nltk_pos.py',
        'desc': (
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
        'id': 'nltk_chunk', 'title': 'Method 4 – NLTK Shallow Chunking',
        'file': 'method4_nltk_chunk.py',
        'desc': (
            'Parses POS-tagged tokens with `nltk.RegexpParser` using a '
            'hand-crafted CFG grammar that defines VP (verb phrases) and '
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
        'id': 'spacy_dep', 'title': 'Method 5 – spaCy Dependency Parsing',
        'file': 'method5_spacy_dep.py',
        'desc': (
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
        'id': 'ensemble', 'title': 'Method 6 – Ensemble Voting',
        'file': 'method6_ensemble.py',
        'desc': (
            'Aggregates predictions from methods 1–5 using confidence-weighted '
            'voting.  Applies a BDD imperative prior (+2.0 for first-token in '
            'ACTION_VOCAB) to prevent auxiliary verbs from winning. Final '
            'confidence = weighted average + 0.05 consensus bonus (≤ 1.0).'
        ),
        'pros': [
            'Reduces the impact of individual method errors.',
            'BDD imperative prior prevents auxiliary verb mis-labelling.',
            'Degrades gracefully when optional libraries are unavailable.',
            'Generally higher precision than any single method alone.',
        ],
        'cons': [
            'Inherits shared blind spots across all constituent methods.',
            'Confidence scores are heuristic, not empirically calibrated.',
            'Adds latency equal to the sum of all constituent methods.',
            'May "average out" a correct minority prediction.',
        ],
    },
]


def _collect_examples(all_cases: List[Dict]) -> Dict[str, List[Dict]]:
    examples: Dict[str, List[Dict]] = {m['id']: [] for m in _METHOD_META}
    for tc in all_cases:
        for sr in tc.get('analysed_steps', []):
            for a in sr['analyses']:
                mid = a['method']
                if mid in examples and len(examples[mid]) < 3 and a['action']:
                    examples[mid].append({
                        'step':   sr['step'],
                        'action': a['action'],
                        'target': a['target'],
                        'conf':   a['confidence'],
                    })
    return examples


def generate_comparison_report(all_cases: List[Dict],
                                out_path: str = 'nlp_methods_comparison.md') -> None:
    examples = _collect_examples(all_cases)
    lines: List[str] = [
        '# NLP Methods Comparison Report',
        '',
        'Records every NLP approach used to extract **action** and **target**',
        'from `.feature` test steps, with pros, cons, and real output examples.',
        '',
        '> Each method also has its own standalone Python file (listed below).',
        '',
        '---',
        '',
        '## Overview',
        '',
        '| # | Method | File | Requires | Speed | Typical Confidence |',
        '|---|--------|------|----------|-------|-------------------|',
        '| 1 | Rule-based Regex | `method1_regex.py` | stdlib only | ★★★★★ | 0.80–0.90 |',
        '| 2 | Keyword + Pattern Heuristics | `method2_keyword.py` | stdlib only | ★★★★★ | 0.65–0.92 |',
        '| 3 | NLTK POS Tagging | `method3_nltk_pos.py` | NLTK | ★★★★☆ | 0.70–0.85 |',
        '| 4 | NLTK Shallow Chunking | `method4_nltk_chunk.py` | NLTK | ★★★☆☆ | 0.75–0.85 |',
        '| 5 | spaCy Dependency Parsing | `method5_spacy_dep.py` | spaCy + model | ★★☆☆☆ | 0.80–0.90 |',
        '| 6 | Ensemble Voting | `method6_ensemble.py` | all above | ★★☆☆☆ | 0.80–0.95 |',
        '',
        '---',
        '',
    ]

    for meta in _METHOD_META:
        mid = meta['id']
        lines += [
            f"## {meta['title']}",
            '',
            f"**File:** `{meta['file']}`",
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
        lines += ['---', '']

    lines += [
        '## Recommendations',
        '',
        '- **No-install environment**: Method 2 (Keyword Heuristics) as primary, Method 1 as fallback.',
        '- **Best single-method accuracy**: Method 5 (spaCy) when the model is available.',
        '- **Highest overall precision**: Method 6 (Ensemble) combining all methods.',
        '- **Extending coverage**: add patterns to `method2_keyword.py` and verbs to `ACTION_VOCAB` in `nlp_common.py`.',
        '',
        '---',
        '',
        '_Report auto-generated by `test_case_reader.py`_',
    ]

    Path(out_path).write_text('\n'.join(lines), encoding='utf-8')
    print(f'Comparison report  → {out_path}')


# ─── Main ─────────────────────────────────────────────────────────────────────

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
            print(f"  Step {i:2d}: {step}")
            print(f"          Action → {best['action'] or '(none)':<22s} Target → {best['target'] or '(none)'}")

        print()
        all_cases.append({**tc, 'analysed_steps': analysed_steps})

    return all_cases


def generate_results_table(all_cases: List[Dict],
                            out_path: str = 'nlp_results_table.md') -> None:
    """Write a per-step comparison table showing action/target for every method."""
    _COLS = [
        ('regex',      'M1 Regex'),
        ('keyword',    'M2 Keyword'),
        ('nltk_pos',   'M3 NLTK POS'),
        ('nltk_chunk', 'M4 NLTK Chunk'),
        ('spacy_dep',  'M5 spaCy'),
        ('ensemble',   'M6 Ensemble'),
    ]

    lines: List[str] = [
        '# NLP Method Comparison – Action & Target per Step',
        '',
        'Each cell shows **Action / Target** extracted by that method.',
        'Empty cells (—) mean the method returned no result.',
        '',
        '---',
        '',
    ]

    for tc in all_cases:
        lines += [
            f"## {tc['file']}",
            f"**{tc['title']}**  ",
            f"URLs: {', '.join(tc['urls'])}",
            '',
        ]
        header = '| # | Step |' + ''.join(f' {label} |' for _, label in _COLS)
        sep    = '|---|------|' + ''.join('---------|' for _ in _COLS)
        lines += [header, sep]

        for i, sr in enumerate(tc['analysed_steps'], 1):
            step   = sr['step'].replace('|', '\\|')
            lookup = {a['method']: a for a in sr['analyses']}
            cells  = []
            for mid, _ in _COLS:
                a      = lookup.get(mid, {})
                action = a.get('action', '')
                target = a.get('target', '')
                if action and target:
                    cell = f"`{action}` / {target}"
                elif action:
                    cell = f"`{action}`"
                else:
                    cell = '—'
                cells.append(cell.replace('|', '\\|'))
            lines.append(f"| {i} | {step} |" + ''.join(f' {c} |' for c in cells))

        lines += ['', '---', '']

    Path(out_path).write_text('\n'.join(lines), encoding='utf-8')
    print(f'Results table      → {out_path}')


if __name__ == '__main__':
    results = run('.')

    out_json = 'nlp_analysis_results.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'Full results       → {out_json}')

    generate_comparison_report(results, 'nlp_methods_comparison.md')
    generate_results_table(results, 'nlp_results_table.md')
