"""
nlp_common.py

Shared types, vocabulary, and feature-file parser used by all method modules.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, NamedTuple

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

# ─── Result container ─────────────────────────────────────────────────────────

class StepAnalysis(NamedTuple):
    method:     str
    action:     str
    target:     str
    confidence: float   # 0.0–1.0
    notes:      str

# ─── Feature-file parser ──────────────────────────────────────────────────────

_STEP_RE = re.compile(r'^\d+\.\s+(.+)')

def parse_feature_file(path: Path) -> Dict:
    """
    Extracts URLs, title, and numbered steps from a .feature file.
    Ignores any embedded JSON blocks (present in some files).
    """
    raw = path.read_text(encoding='utf-8')
    text = raw.split('{')[0] if '{' in raw else raw

    urls: List[str] = []
    title = ''
    steps: List[str] = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith('urls = '):
            try:
                urls = json.loads(line[len('urls = '):])
            except json.JSONDecodeError:
                urls = re.findall(r'https?://[^\s\'"]+', line)
        elif line.startswith('Test Case'):
            title = line
        else:
            m = _STEP_RE.match(line)
            if m:
                steps.append(m.group(1).strip().rstrip())

    return {'file': path.name, 'urls': urls, 'title': title, 'steps': steps}
