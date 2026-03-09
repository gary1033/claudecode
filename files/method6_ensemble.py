#!/usr/bin/env python3
"""
method6_ensemble.py — Ensemble Voting

Aggregates predictions from methods 1–5 using confidence-weighted voting.
Since split_compound_step() is deterministic, all methods produce the same
number of pairs; the ensemble votes independently on each pair index.

BDD imperative prior: if the first token of a sub-step is in ACTION_VOCAB,
it receives a +2.0 bonus, preventing auxiliary verbs from winning.

Pros: highest overall precision, degrades gracefully without optional libs.
Cons: adds latency of all methods combined, inherits their shared blind spots.

Run standalone:
    python3 method6_ensemble.py
"""

from collections import Counter
from pathlib import Path
from typing import Dict, List

from nlp_common import (
    ACTION_VOCAB, ActionTarget, StepResult,
    parse_feature_file, split_compound_step,
)
from method1_regex     import analyse as m1
from method2_keyword   import analyse as m2
from method3_nltk_pos  import analyse as m3
from method4_nltk_chunk import analyse as m4
from method5_spacy_dep  import analyse as m5


def analyse(step: str) -> StepResult:
    all_results = [m1(step), m2(step), m3(step), m4(step), m5(step)]
    sub_steps   = split_compound_step(step)
    n_pairs     = len(sub_steps)   # deterministic; same for every method

    ensemble_pairs: List[ActionTarget] = []

    for idx in range(n_pairs):
        sub        = sub_steps[idx]
        first_tok  = sub.split()[0].lower().rstrip('.,') if sub.split() else ''

        action_votes: Dict[str, float] = Counter()
        target_votes: Dict[str, float] = Counter()

        for r in all_results:
            if idx < len(r.pairs):
                pair = r.pairs[idx]
                if pair.action:
                    action_votes[pair.action.lower()] += r.confidence
                for t in pair.targets:
                    if t:
                        target_votes[t.lower()] += r.confidence

        # BDD imperative prior
        if first_tok in ACTION_VOCAB:
            action_votes[first_tok] += 2.0
        for key in list(action_votes):
            if key != first_tok and key in ACTION_VOCAB:
                action_votes[key] += 0.30

        if not action_votes:
            ensemble_pairs.append(ActionTarget('', []))
            continue

        best_action_key = max(action_votes, key=action_votes.__getitem__)
        best_action = next(
            (r.pairs[idx].action for r in all_results
             if idx < len(r.pairs) and r.pairs[idx].action.lower() == best_action_key),
            best_action_key,
        )

        # Target voting: pick the expected number of targets (majority vote on count)
        if target_votes:
            count_votes = Counter(
                len(r.pairs[idx].targets) for r in all_results if idx < len(r.pairs)
            )
            expected_n = count_votes.most_common(1)[0][0]
            top_targets = sorted(target_votes.items(), key=lambda x: x[1], reverse=True)
            best_targets: List[str] = []
            for tkey, _ in top_targets[:max(expected_n, 1)]:
                original = next(
                    (t for r in all_results if idx < len(r.pairs)
                       for t in r.pairs[idx].targets if t.lower() == tkey),
                    tkey,
                )
                best_targets.append(original)
        else:
            best_targets = []

        ensemble_pairs.append(ActionTarget(best_action, best_targets))

    avg_conf = sum(r.confidence for r in all_results) / len(all_results)
    return StepResult('ensemble', ensemble_pairs, min(round(avg_conf + 0.05, 3), 1.0),
                      f"n_pairs={n_pairs}, n_methods={len(all_results)}")


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            for p in r.pairs:
                print(f"      Action={p.action!r:20s} Targets={p.targets}")
