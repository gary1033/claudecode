#!/usr/bin/env python3
"""
method3_nltk_pos.py — NLTK POS Tagging

Tokenises with nltk.word_tokenize and tags each token.  Calls
split_compound_step() first so compound steps are handled separately.
For each sub-step: the first VB* tag is the action; contiguous NN*/JJ/DT/CD
tokens after it form the target NP.  Quoted strings override the NP.
Coordinated objects (via CC tags) are also collected for multi-target steps.

Pros: linguistically grounded, handles morphological variants.
Cons: domain words may be mis-tagged, capitalised verbs tagged as NNP.

Run standalone:
    python3 method3_nltk_pos.py
"""

import re
from pathlib import Path
from typing import List, Tuple

from nlp_common import (
    NLTK_AVAILABLE, ActionTarget, StepResult,
    extract_targets, parse_feature_file, run_method_standalone, split_compound_step,
)

if NLTK_AVAILABLE:
    import nltk

_NP_TAGS = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'DT', 'CD'}


def _analyse_single(sub: str) -> Tuple[str, List[str], float, str]:
    if not NLTK_AVAILABLE:
        return '', [], 0.0, 'NLTK not available'

    tokens = nltk.word_tokenize(sub)
    tagged = nltk.pos_tag(tokens)

    action = ''
    np_words: List[str] = []
    found_verb = False
    in_np = False

    for word, tag in tagged:
        if not found_verb:
            if tag.startswith('VB'):
                action = word
                found_verb = True
        else:
            if tag in _NP_TAGS:
                np_words.append(word)
                in_np = True
            elif tag == 'CC' and in_np:       # coordinating conjunction: "and"
                np_words.append(word)         # keep for splitting later
            elif tag in ('IN', 'TO') and in_np:
                np_words.append(word)
            elif in_np:
                break

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", sub)
    if quoted and action:
        targets = [quoted[0]]
        confidence = 0.85
    else:
        raw = ' '.join(np_words)
        targets = extract_targets(raw)
        confidence = 0.70 if action else 0.20

    return action, targets, confidence, f"tagged={[(w, t) for w, t in tagged[:4]]}"


def analyse(step: str) -> StepResult:
    sub_steps = split_compound_step(step)
    pairs: List[ActionTarget] = []
    total_conf = 0.0
    for sub in sub_steps:
        action, targets, conf, _ = _analyse_single(sub)
        pairs.append(ActionTarget(action, targets))
        total_conf += conf
    return StepResult('nltk_pos', pairs, round(total_conf / len(sub_steps), 3),
                      f"sub_steps={len(sub_steps)}")


if __name__ == '__main__':
    run_method_standalone('nltk_pos', analyse)
