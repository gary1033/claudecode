#!/usr/bin/env python3
"""
method2_keyword.py — Keyword + Pattern Heuristics

Applies an ordered list of compiled regex patterns, each tuned to a specific
BDD phrasing (navigate to url, click on 'X', verify 'X' is visible, ...).
Falls back to a generic VERB + TARGET pattern.

Pros: very precise for known patterns, no external dependencies, easy to extend.
Cons: brittle for novel phrasings, order-sensitive, generic fallback is weaker.

Run standalone:
    python3 method2_keyword.py
"""

import re
from pathlib import Path
from typing import List

from nlp_common import StepAnalysis, parse_feature_file

_PATTERNS: List[tuple] = [
    (re.compile(r"^(navigate)\s+to\s+url\s+['\"]([^'\"]+)['\"]", re.I), 2),
    (re.compile(r"^(click)\s+(?:on\s+)?['\"]([^'\"]+)['\"]", re.I), 2),
    (re.compile(r"^(verify)\s+(?:that\s+|text\s+|error\s+|success\s+message\s+)?['\"]([^'\"]+)['\"]", re.I), 2),
    (re.compile(r"^(enter)\s+(.+?)\s+(?:in|into|and)\s+", re.I), 2),
    (re.compile(r"^(scroll)\s+(?:down\s+)?(?:to\s+)?(.+)", re.I), 2),
    (re.compile(r"^(launch)\s+(.+)", re.I), 2),
    (re.compile(r"^(verify)\s+that\s+(.+?)\s+(?:is|are)\b", re.I), 2),
    # Generic fallback
    (re.compile(r"^(\w+)\s+(?:on\s+|to\s+|in\s+|at\s+|that\s+)?(.+?)(?:\s+is\s+|\s+are\s+|$)", re.I), 2),
]
_GENERIC_PATTERN = _PATTERNS[-1][0].pattern


def analyse(step: str) -> StepAnalysis:
    for pattern, grp in _PATTERNS:
        m = pattern.match(step)
        if m:
            action = m.group(1)
            raw_target = m.group(grp) if grp <= len(m.groups()) else ''
            target = re.sub(r"['\"]", '', raw_target).strip()
            is_named = pattern.pattern != _GENERIC_PATTERN
            confidence = 0.90 if is_named else 0.65
            return StepAnalysis('keyword', action, target, confidence,
                                f"pattern={'named' if is_named else 'generic'}")

    tokens = step.split()
    return StepAnalysis('keyword',
                        tokens[0] if tokens else '',
                        ' '.join(tokens[1:]),
                        0.30, 'no_pattern_matched')


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            print(f"      Action={r.action!r:20s} Target={r.target!r}")
