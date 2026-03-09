"""
nlp_common.py

Shared types, vocabulary, compound-step splitter, and feature-file parser
used by all method modules.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple

# ─── NLP library detection ────────────────────────────────────────────────────

try:
    import nltk
    for _pkg, _kind in [
        ('punkt_tab',                     'tokenizers'),
        ('averaged_perceptron_tagger_eng', 'taggers'),
        ('maxent_ne_chunker_tab',          'chunkers'),
        ('words',                          'corpora'),
    ]:
        try:
            nltk.data.find(f'{_kind}/{_pkg}')
        except LookupError:
            nltk.download(_pkg, quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import spacy
    NLP_MODEL = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    NLP_MODEL = None

# ─── Shared vocabulary ────────────────────────────────────────────────────────

ACTION_VOCAB = {
    'launch', 'navigate', 'verify', 'click', 'enter', 'scroll', 'fill',
    'select', 'check', 'submit', 'wait', 'search', 'type', 'press',
    'hover', 'drag', 'drop', 'upload', 'download', 'open', 'close',
    'refresh', 'filter', 'register', 'login', 'logout', 'add', 'delete', 'edit',
}

SKIP_WORDS = {'on', 'to', 'in', 'at', 'into', 'with', 'that', 'down', 'the', 'a', 'an'}

# ─── Result types ─────────────────────────────────────────────────────────────

class ActionTarget(NamedTuple):
    """One (action, targets) pair extracted from a step or sub-step."""
    action:  str
    targets: List[str]   # may have multiple targets for compound objects


class StepResult(NamedTuple):
    """Full result for one step: possibly multiple action-target pairs."""
    method:     str
    pairs:      List[ActionTarget]
    confidence: float    # 0.0–1.0
    notes:      str

# ─── Compound-step splitter ───────────────────────────────────────────────────

# Matches " and VERB" where VERB is a known action (e.g., "…and click…")
# Uses a lookahead so the verb itself is kept at the start of the next part.
_ACTION_ALT = '|'.join(re.escape(v) for v in sorted(ACTION_VOCAB, key=len, reverse=True))
_COMPOUND_RE = re.compile(rf'\s+and\s+(?=(?:{_ACTION_ALT})\b)', re.I)


def split_compound_step(step: str) -> List[str]:
    """
    Split "Enter email and click arrow" → ["Enter email", "click arrow"].
    Does NOT split "Enter name and email" because "email" is not in ACTION_VOCAB.
    """
    parts = _COMPOUND_RE.split(step)
    return [p.strip() for p in parts if p.strip()]


def extract_targets(raw: str) -> List[str]:
    """
    Split compound-object strings into a list of individual targets.
      "email address"               → ["email address"]
      "name and email address"      → ["name", "email address"]
      "name, email, subject"        → ["name", "email", "subject"]
      "Title, Name, Email, Password"→ ["Title", "Name", "Email", "Password"]
    Quoted targets (already clean single strings) pass through unchanged.
    """
    if not raw:
        return []
    parts = re.split(r',\s*|\s+and\s+', raw)
    return [p.strip() for p in parts if p.strip()]

# ─── Standalone output helper ────────────────────────────────────────────────

def save_method_results(method_id: str, all_cases: List[Dict]) -> str:
    """
    Write a JSON file named  results_<method_id>.json  containing the
    action-target pairs extracted by that method for every step.
    Returns the output filename.
    """
    output = []
    for tc in all_cases:
        tc_entry = {
            'file':  tc['file'],
            'title': tc['title'],
            'urls':  tc['urls'],
            'steps': [],
        }
        for sr in tc['steps_results']:
            tc_entry['steps'].append({
                'step':  sr['step'],
                'pairs': [{'action': p.action, 'targets': p.targets}
                           for p in sr['result'].pairs],
                'confidence': round(sr['result'].confidence, 3),
            })
        output.append(tc_entry)

    out_path = f'results_{method_id}.json'
    Path(out_path).write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    return out_path


def run_method_standalone(method_id: str, analyse_fn) -> None:
    """
    Standard __main__ body for every method file:
      - reads all .feature files
      - prints results to stdout
      - saves results_<method_id>.json
    """
    feature_files = sorted(Path('.').glob('*.feature'))
    all_cases = []

    for fp in feature_files:
        tc = parse_feature_file(fp)
        print(f"\n{'='*60}\n{tc['title']}")
        steps_results = []
        for i, step in enumerate(tc['steps'], 1):
            r = analyse_fn(step)
            steps_results.append({'step': step, 'result': r})
            print(f"  {i:2d}. {step}")
            for p in r.pairs:
                tstr = ', '.join(p.targets) if p.targets else '(none)'
                print(f"      Action={p.action!r:20s} Targets={tstr}")
        all_cases.append({**tc, 'steps_results': steps_results})

    out = save_method_results(method_id, all_cases)
    print(f"\n→ Saved: {out}")


# ─── Feature-file parser ──────────────────────────────────────────────────────

_STEP_RE = re.compile(r'^\d+\.\s+(.+)')


def parse_feature_file(path: Path) -> Dict:
    """
    Extracts URLs, title, and numbered steps from a .feature file.
    Ignores embedded JSON blocks and duplicate step sections.
    """
    raw = path.read_text(encoding='utf-8')
    text = raw.split('{')[0] if '{' in raw else raw

    urls:  List[str] = []
    title = ''
    steps: List[str] = []
    seen_title = False

    for line in text.splitlines():
        line = line.strip()
        if line.startswith('urls = '):
            if not seen_title:          # only the first URL block
                try:
                    urls = json.loads(line[len('urls = '):])
                except json.JSONDecodeError:
                    urls = re.findall(r'https?://[^\s\'"]+', line)
        elif line.startswith('Test Case'):
            if not seen_title:
                title = line
                seen_title = True
        else:
            m = _STEP_RE.match(line)
            if m:
                steps.append(m.group(1).strip().rstrip())

    # Deduplicate consecutive identical steps (TestCase3 has the list twice)
    deduped: List[str] = []
    for s in steps:
        if not deduped or s != deduped[-1]:
            deduped.append(s)
    # If the second half is a repeat of the first, keep only the first half
    n = len(deduped)
    if n % 2 == 0:
        half = deduped[:n // 2]
        if half == deduped[n // 2:]:
            deduped = half

    return {'file': path.name, 'urls': urls, 'title': title, 'steps': deduped}
