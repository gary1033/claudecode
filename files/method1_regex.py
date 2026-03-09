#!/usr/bin/env python3
"""
method1_regex.py — Rule-based Regex

Extracts action and target from a BDD test step by:
  1. Matching the first token against ACTION_VOCAB.
  2. Using the first quoted string as the preferred target.
  3. Falling back to the noun phrase after stripping leading prepositions.

Pros: zero dependencies, deterministic, microsecond speed.
Cons: blind to grammar, degrades without quoted strings, needs manual vocab upkeep.

Run standalone:
    python3 method1_regex.py
"""

import re
from pathlib import Path
from typing import List

from nlp_common import ACTION_VOCAB, SKIP_WORDS, StepAnalysis, parse_feature_file


def analyse(step: str) -> StepAnalysis:
    tokens = step.split()
    if not tokens:
        return StepAnalysis('regex', '', '', 0.0, 'empty step')

    first = tokens[0].lower().rstrip('.,')
    in_vocab = first in ACTION_VOCAB
    action = tokens[0]
    confidence = 0.80 if in_vocab else 0.30

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted:
        target = quoted[0]
        confidence = min(confidence + 0.10, 1.0)
    else:
        rest = tokens[1:]
        while rest and rest[0].lower() in SKIP_WORDS:
            rest = rest[1:]
        trimmed: List[str] = []
        for t in rest:
            if t.lower() in ('and', 'is', 'are', 'was', 'were'):
                break
            trimmed.append(t)
        target = ' '.join(trimmed)

    return StepAnalysis('regex', action, target, round(confidence, 3),
                        f"verb_in_vocab={in_vocab}")


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            print(f"      Action={r.action!r:20s} Target={r.target!r}")
