#!/usr/bin/env python3
"""
method4_nltk_chunk.py — NLTK Shallow Chunking

Parses POS-tagged tokens with nltk.RegexpParser using a hand-crafted CFG
grammar that defines VP (verb phrases) and NP (noun phrases).
The first VP chunk gives the action phrase; the first NP after it gives the target.
Quoted strings override the NP target when present.

Pros: captures multi-word verb phrases, transparent grammar, no GPU needed.
Cons: grammar needs manual tuning, misses long-distance dependencies.

Run standalone:
    python3 method4_nltk_chunk.py
"""

import re
from pathlib import Path

from nlp_common import NLTK_AVAILABLE, StepAnalysis, parse_feature_file

if NLTK_AVAILABLE:
    import nltk

_GRAMMAR = r"""
    VP: {<VB.*><RP|IN|TO>?<RB>?}
    NP: {<DT>?<JJ.*>*<NN.*>+}
"""


def analyse(step: str) -> StepAnalysis:
    if not NLTK_AVAILABLE:
        return StepAnalysis('nltk_chunk', '', '', 0.0, 'NLTK not available')

    tokens = nltk.word_tokenize(step)
    tagged = nltk.pos_tag(tokens)
    tree = nltk.RegexpParser(_GRAMMAR).parse(tagged)

    action = ''
    target = ''
    vp_found = False

    for subtree in tree:
        if hasattr(subtree, 'label'):
            label = subtree.label()
            words = ' '.join(w for w, _ in subtree.leaves())
            if label == 'VP' and not vp_found:
                action = words
                vp_found = True
            elif label == 'NP' and vp_found and not target:
                target = words
        else:
            word, tag = subtree
            if tag.startswith('VB') and not action:
                action = word
                vp_found = True

    quoted = re.findall(r"['\"]([^'\"]+)['\"]", step)
    if quoted and action:
        target = quoted[0]
        confidence = 0.85
    else:
        confidence = 0.75 if (action and target) else 0.40

    chunk_labels = [s.label() if hasattr(s, 'label') else s[1] for s in tree]
    return StepAnalysis('nltk_chunk', action, target, confidence,
                        f"chunk_labels={chunk_labels[:6]}")


if __name__ == '__main__':
    for fp in sorted(Path('.').glob('*.feature')):
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        for i, step in enumerate(tc['steps'], 1):
            r = analyse(step)
            print(f"  {i:2d}. {step}")
            print(f"      Action={r.action!r:20s} Target={r.target!r}")
