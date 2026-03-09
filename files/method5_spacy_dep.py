#!/usr/bin/env python3
"""
method5_spacy_dep.py — spaCy Dependency Parsing

Uses spaCy's en_core_web_sm neural pipeline on each step.
The ROOT token (typically the main verb) is the action.
The direct object (dobj) or prepositional object (pobj) of the root is used
as the target, expanded to the full NP span via left_edge/right_edge.
Quoted strings override the parsed target when present.

Pros: most linguistically accurate, understands syntactic roles, full NP spans.
Cons: requires spaCy + model (~12 MB), slowest method, overkill for short BDD steps.

Run standalone:
    python3 method5_spacy_dep.py
"""

import re
from pathlib import Path

from nlp_common import NLP_MODEL, SPACY_AVAILABLE, StepAnalysis, parse_feature_file


def analyse(step: str) -> StepAnalysis:
    if not SPACY_AVAILABLE or NLP_MODEL is None:
        return StepAnalysis('spacy_dep', '', '', 0.0, 'spaCy/model not available')

    doc = NLP_MODEL(step)
    root = next((t for t in doc if t.dep_ == 'ROOT'), None)
    action = root.text if root else ''
    target = ''

    if root:
        dobj = next((t for t in root.children if t.dep_ == 'dobj'), None)
        if dobj:
            target = doc[dobj.left_edge.i: dobj.right_edge.i + 1].text
        else:
            for child in root.children:
                if child.dep_ == 'prep':
                    pobj = next((t for t in child.children if t.dep_ == 'pobj'), None)
                    if pobj:
                        target = doc[pobj.left_edge.i: pobj.right_edge.i + 1].text
                        break

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted and action:
        target = quoted[0]
        confidence = 0.90
    else:
        confidence = 0.80 if (action and target) else 0.50

    return StepAnalysis('spacy_dep', action, target, confidence,
                        f"root={action}, dep_labels={[t.dep_ for t in doc][:6]}")


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            print(f"      Action={r.action!r:20s} Target={r.target!r}")
