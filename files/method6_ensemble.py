#!/usr/bin/env python3
"""
method6_ensemble.py — Ensemble Voting

Aggregates predictions from methods 1–5 using confidence-weighted voting.
Each method's action/target is weighted by its reported confidence score;
the candidate with the highest accumulated weight wins.

Domain priors applied:
  - BDD imperative prior: if the first token is in ACTION_VOCAB, +2.0 bonus.
  - Secondary vocab bonus: other ACTION_VOCAB candidates receive +0.30.

Final confidence = weighted average + 0.05 consensus bonus (capped at 1.0).

Pros: reduces individual method errors, degrades gracefully, highest overall precision.
Cons: inherits shared blind spots, confidence scores are heuristic, adds latency.

Run standalone:
    python3 method6_ensemble.py
"""

from collections import Counter
from pathlib import Path
from typing import Dict, List

from nlp_common import ACTION_VOCAB, StepAnalysis, parse_feature_file
from method1_regex import analyse as m1
from method2_keyword import analyse as m2
from method3_nltk_pos import analyse as m3
from method4_nltk_chunk import analyse as m4
from method5_spacy_dep import analyse as m5


def analyse(step: str) -> StepAnalysis:
    results = [m1(step), m2(step), m3(step), m4(step), m5(step)]
    valid = [r for r in results if r.action]
    if not valid:
        return StepAnalysis('ensemble', '', '', 0.0, 'no valid inputs')

    action_votes: Dict[str, float] = Counter()
    target_votes: Dict[str, float] = Counter()

    for r in valid:
        action_votes[r.action.lower()] += r.confidence
        if r.target:
            target_votes[r.target.lower()] += r.confidence

    # BDD imperative prior
    first_token = step.split()[0].lower().rstrip('.,') if step.split() else ''
    if first_token in ACTION_VOCAB:
        action_votes[first_token] += 2.0

    # Secondary vocab bonus
    for key in list(action_votes):
        if key != first_token and key in ACTION_VOCAB:
            action_votes[key] += 0.30

    best_action_key = max(action_votes, key=action_votes.__getitem__)
    best_action = next(r.action for r in valid if r.action.lower() == best_action_key)

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


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            print(f"      Action={r.action!r:20s} Target={r.target!r}")
