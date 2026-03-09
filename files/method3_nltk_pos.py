#!/usr/bin/env python3
"""
method3_nltk_pos.py — NLTK POS Tagging

Tokenises with nltk.word_tokenize and tags each token using the averaged
perceptron tagger.  The first VB* tag is the action; the contiguous sequence
of NN*, JJ, DT, CD tokens that follows is collected as the target noun phrase.
Quoted strings override the NP target when present.

Pros: linguistically grounded, handles morphological variants, small footprint.
Cons: domain words may be mis-tagged, NP heuristic breaks for complex NPs.

Run standalone:
    python3 method3_nltk_pos.py
"""

import re
from pathlib import Path
from typing import List

from nlp_common import NLTK_AVAILABLE, StepAnalysis, parse_feature_file

if NLTK_AVAILABLE:
    import nltk


def analyse(step: str) -> StepAnalysis:
    if not NLTK_AVAILABLE:
        return StepAnalysis('nltk_pos', '', '', 0.0, 'NLTK not available')

    tokens = nltk.word_tokenize(step)
    tagged = nltk.pos_tag(tokens)

    action = ''
    target_tokens: List[str] = []
    found_verb = False
    in_np = False

    for word, tag in tagged:
        if not found_verb:
            if tag.startswith('VB'):
                action = word
                found_verb = True
        else:
            if tag in ('NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'DT', 'CD'):
                target_tokens.append(word)
                in_np = True
            elif tag in ('IN', 'TO') and in_np:
                target_tokens.append(word)
            elif in_np:
                break

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted and action:
        target = quoted[0]
        confidence = 0.85
    else:
        target = ' '.join(target_tokens)
        confidence = 0.70 if action else 0.20

    return StepAnalysis('nltk_pos', action, target, confidence,
                        f"tagged={[(w, t) for w, t in tagged[:5]]}")


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            print(f"      Action={r.action!r:20s} Target={r.target!r}")
