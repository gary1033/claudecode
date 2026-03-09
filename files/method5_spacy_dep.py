#!/usr/bin/env python3
"""
method5_spacy_dep.py — spaCy Dependency Parsing

Uses spaCy's en_core_web_sm pipeline. Calls split_compound_step() first for
compound steps.  For each sub-step: the ROOT verb is the action; direct
objects (dobj) and their conjuncts, or prepositional objects (pobj), form
the target list.  Quoted strings override the parsed targets.

Pros: most linguistically accurate, finds conjunct objects automatically.
Cons: requires spaCy + model, slowest method, ROOT may be auxiliary verb.

Run standalone:
    python3 method5_spacy_dep.py
"""

import re
from pathlib import Path
from typing import List, Tuple

from nlp_common import (
    NLP_MODEL, SPACY_AVAILABLE, ActionTarget, StepResult,
    parse_feature_file, run_method_standalone, split_compound_step,
)


def _analyse_single(sub: str) -> Tuple[str, List[str], float, str]:
    if not SPACY_AVAILABLE or NLP_MODEL is None:
        return '', [], 0.0, 'spaCy/model not available'

    doc = NLP_MODEL(sub)
    root = next((t for t in doc if t.dep_ == 'ROOT'), None)
    action = root.text if root else ''
    targets: List[str] = []

    if root:
        # Collect direct objects + their conjuncts
        dobjs = [t for t in root.children if t.dep_ == 'dobj']
        for dobj in dobjs:
            targets.append(doc[dobj.left_edge.i: dobj.right_edge.i + 1].text)
            for conj in dobj.conjuncts:
                targets.append(doc[conj.left_edge.i: conj.right_edge.i + 1].text)

        if not targets:
            for child in root.children:
                if child.dep_ == 'prep':
                    for pobj in child.children:
                        if pobj.dep_ == 'pobj':
                            targets.append(doc[pobj.left_edge.i: pobj.right_edge.i + 1].text)
                            for conj in pobj.conjuncts:
                                targets.append(doc[conj.left_edge.i: conj.right_edge.i + 1].text)

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", sub)
    if quoted and action:
        targets = [quoted[0]]
        confidence = 0.90
    else:
        confidence = 0.80 if (action and targets) else 0.50

    return action, targets, confidence, f"root={action}, deps={[t.dep_ for t in doc][:6]}"


def analyse(step: str) -> StepResult:
    sub_steps = split_compound_step(step)
    pairs: List[ActionTarget] = []
    total_conf = 0.0
    for sub in sub_steps:
        action, targets, conf, _ = _analyse_single(sub)
        pairs.append(ActionTarget(action, targets))
        total_conf += conf
    return StepResult('spacy_dep', pairs, round(total_conf / len(sub_steps), 3),
                      f"sub_steps={len(sub_steps)}")


if __name__ == '__main__':
    run_method_standalone('spacy_dep', analyse)
