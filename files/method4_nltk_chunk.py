#!/usr/bin/env python3
"""
method4_nltk_chunk.py — NLTK Shallow Chunking

Parses POS-tagged tokens with nltk.RegexpParser using a hand-crafted CFG
grammar. Calls split_compound_step() first for compound steps.
For each sub-step: the first VP chunk gives the action; the first NP gives
the primary target.  Subsequent NPs joined by CC are also collected.

Pros: captures multi-word verb phrases, transparent grammar.
Cons: grammar needs manual tuning, misses long-distance dependencies.

Run standalone:
    python3 method4_nltk_chunk.py
"""

import re
from pathlib import Path
from typing import List, Tuple

from nlp_common import (
    NLTK_AVAILABLE, ActionTarget, StepResult,
    parse_feature_file, run_method_standalone, split_compound_step,
)

if NLTK_AVAILABLE:
    import nltk

_GRAMMAR = r"""
    VP: {<VB.*><RP|IN|TO>?<RB>?}
    NP: {<DT>?<JJ.*>*<NN.*>+}
"""


def _analyse_single(sub: str) -> Tuple[str, List[str], float, str]:
    if not NLTK_AVAILABLE:
        return '', [], 0.0, 'NLTK not available'

    tokens = nltk.word_tokenize(sub)
    tagged = nltk.pos_tag(tokens)
    tree = nltk.RegexpParser(_GRAMMAR).parse(tagged)

    action = ''
    targets: List[str] = []
    vp_found = False

    for subtree in tree:
        if hasattr(subtree, 'label'):
            label = subtree.label()
            words = ' '.join(w for w, _ in subtree.leaves())
            if label == 'VP' and not vp_found:
                action = words
                vp_found = True
            elif label == 'NP' and vp_found:
                targets.append(words)           # collect all NPs after VP
        else:
            word, tag = subtree
            if tag.startswith('VB') and not action:
                action = word
                vp_found = True

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", sub)
    if quoted and action:
        targets = [quoted[0]]
        confidence = 0.85
    else:
        confidence = 0.75 if (action and targets) else 0.40

    chunk_labels = [s.label() if hasattr(s, 'label') else s[1] for s in tree]
    return action, targets, confidence, f"chunks={chunk_labels[:6]}"


def analyse(step: str) -> StepResult:
    sub_steps = split_compound_step(step)
    pairs: List[ActionTarget] = []
    total_conf = 0.0
    for sub in sub_steps:
        action, targets, conf, _ = _analyse_single(sub)
        pairs.append(ActionTarget(action, targets))
        total_conf += conf
    return StepResult('nltk_chunk', pairs, round(total_conf / len(sub_steps), 3),
                      f"sub_steps={len(sub_steps)}")


if __name__ == '__main__':
    run_method_standalone('nltk_chunk', analyse)
