#!/usr/bin/env python3
"""
method1_regex.py — Rule-based Regex

Extracts action(s) and target(s) from a BDD test step by:
  1. Calling split_compound_step() to handle "Enter X and Click Y" patterns.
  2. For each sub-step: matching the first token against ACTION_VOCAB.
  3. Using quoted strings as the preferred target(s).
  4. Falling back to noun-phrase extraction with compound-object splitting.

Pros: zero dependencies, deterministic, microsecond speed.
Cons: blind to grammar, degrades without quoted strings, needs manual vocab upkeep.

Run standalone:
    python3 method1_regex.py
"""

import re
from pathlib import Path
from typing import List, Tuple

from nlp_common import (
    ACTION_VOCAB, SKIP_WORDS, ActionTarget, StepResult,
    extract_targets, parse_feature_file, split_compound_step,
)


def _analyse_single(sub: str) -> Tuple[str, List[str], float, str]:
    """Return (action, targets, confidence, note) for one non-compound sub-step."""
    tokens = sub.split()
    if not tokens:
        return '', [], 0.0, 'empty'

    first = tokens[0].lower().rstrip('.,')
    in_vocab = first in ACTION_VOCAB
    action = tokens[0]
    confidence = 0.80 if in_vocab else 0.30

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", sub)
    if quoted:
        targets = [quoted[0]]
        confidence = min(confidence + 0.10, 1.0)
    else:
        rest = tokens[1:]
        while rest and rest[0].lower() in SKIP_WORDS:
            rest = rest[1:]
        trimmed: List[str] = []
        for t in rest:
            if t.lower() in ('is', 'are', 'was', 'were'):
                break
            trimmed.append(t)
        targets = extract_targets(' '.join(trimmed))

    return action, targets, confidence, f"verb_in_vocab={in_vocab}"


def analyse(step: str) -> StepResult:
    sub_steps = split_compound_step(step)
    pairs: List[ActionTarget] = []
    total_conf = 0.0
    for sub in sub_steps:
        action, targets, conf, _ = _analyse_single(sub)
        pairs.append(ActionTarget(action, targets))
        total_conf += conf
    avg_conf = round(total_conf / len(sub_steps), 3)
    return StepResult('regex', pairs, avg_conf, f"sub_steps={len(sub_steps)}")


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            for p in r.pairs:
                print(f"      Action={p.action!r:20s} Targets={p.targets}")
