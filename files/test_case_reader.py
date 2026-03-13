#!/usr/bin/env python3
"""
test_case_reader.py

Orchestrator: reads all .feature files and extracts action(s) + target(s)
from every numbered test step using all six NLP methods.

Each method lives in its own module and can also be run standalone:
    python3 method1_regex.py  …  python3 method6_ensemble.py

Outputs (written to the same directory as the .feature files):
    ground_truth.json          — manually annotated correct answers
    nlp_analysis_results.json  — full per-step breakdown across all methods
    nlp_results_table.md       — comparison table (ground truth vs each method)
    nlp_accuracy_report.md     — per-method accuracy scores
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

from nlp_common import (
    NLTK_AVAILABLE, SPACY_AVAILABLE,
    ActionTarget, StepResult,
    parse_feature_file,
)

from method1_regex      import analyse as m1
from method2_keyword    import analyse as m2
from method3_nltk_pos   import analyse as m3
from method4_nltk_chunk import analyse as m4
from method5_spacy_dep  import analyse as m5
from method6_ensemble   import analyse as m6

METHODS = [
    ('regex',      'M1 Regex',       m1),
    ('keyword',    'M2 Keyword',     m2),
    ('nltk_pos',   'M3 NLTK POS',   m3),
    ('nltk_chunk', 'M4 NLTK Chunk', m4),
    ('spacy_dep',  'M5 spaCy',      m5),
    ('ensemble',   'M6 Ensemble',   m6),
]

# ─── Accuracy helpers ─────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    return s.lower().strip()


def _target_match(extracted: str, truth: str) -> bool:
    """Relaxed match: one must be a substring of the other (normalised)."""
    e, t = _norm(extracted), _norm(truth)
    return e == t or e in t or t in e


def _pair_correct(extracted: ActionTarget, truth_pair: Dict) -> Tuple[bool, bool]:
    """Return (action_ok, full_pair_ok)."""
    action_ok = _norm(extracted.action) == _norm(truth_pair['action'])
    targets_ok = all(
        any(_target_match(et, gt) for et in extracted.targets)
        for gt in truth_pair['targets']
    ) if truth_pair['targets'] else (not extracted.targets)
    return action_ok, action_ok and targets_ok


def evaluate(results: List[Dict], truth_data: List[Dict]) -> Dict[str, Dict]:
    """Compare each method's output against ground_truth.json."""
    truth_index: Dict[Tuple[str, str], List[Dict]] = {}
    for tc in truth_data:
        for s in tc['steps']:
            truth_index[(tc['file'], s['step'])] = s['pairs']

    stats: Dict[str, Dict] = {mid: {'action_correct': 0, 'pair_correct': 0, 'total': 0}
                               for mid, _, _ in METHODS}

    for tc in results:
        for sr in tc['analysed_steps']:
            key = (tc['file'], sr['step'])
            truth_pairs = truth_index.get(key, [])
            if not truth_pairs:
                continue
            for mid, _, _ in METHODS:
                a_dict = next((a for a in sr['analyses'] if a['method'] == mid), None)
                if a_dict is None:
                    continue
                extracted = [ActionTarget(p['action'], p['targets']) for p in a_dict['pairs']]
                for i, tp in enumerate(truth_pairs):
                    stats[mid]['total'] += 1
                    ep = extracted[i] if i < len(extracted) else ActionTarget('', [])
                    a_ok, p_ok = _pair_correct(ep, tp)
                    if a_ok:
                        stats[mid]['action_correct'] += 1
                    if p_ok:
                        stats[mid]['pair_correct'] += 1

    for mid in stats:
        t = stats[mid]['total'] or 1
        stats[mid]['action_acc'] = round(stats[mid]['action_correct'] / t * 100, 1)
        stats[mid]['pair_acc']   = round(stats[mid]['pair_correct']   / t * 100, 1)
    return stats


# ─── Per-step analysis ────────────────────────────────────────────────────────

def _result_to_dict(r: StepResult) -> Dict:
    return {
        'method':     r.method,
        'confidence': round(r.confidence, 3),
        'notes':      r.notes,
        'pairs':      [{'action': p.action, 'targets': p.targets} for p in r.pairs],
    }


def analyse_step(step: str) -> Dict:
    results = [fn(step) for _, _, fn in METHODS]
    best = results[-1]
    return {
        'step':     step,
        'analyses': [_result_to_dict(r) for r in results],
        'best': {
            'pairs':      [{'action': p.action, 'targets': p.targets} for p in best.pairs],
            'confidence': round(best.confidence, 3),
        },
    }


# ─── Output: comparison table ─────────────────────────────────────────────────

def _fmt_pairs(pairs: List[Dict]) -> str:
    if not pairs:
        return '—'
    parts = []
    for p in pairs:
        a = p.get('action', '') or '—'
        t = ', '.join(p.get('targets', [])) or '—'
        parts.append(f'`{a}`: {t}')
    return ' ➜ '.join(parts)


def generate_results_table(all_cases: List[Dict], truth_data: List[Dict],
                            out_path: str = 'nlp_results_table.md') -> None:
    truth_index: Dict[Tuple[str, str], List[Dict]] = {}
    for tc in truth_data:
        for s in tc['steps']:
            truth_index[(tc['file'], s['step'])] = s['pairs']

    col_labels = [label for _, label, _ in METHODS]
    lines: List[str] = [
        '# NLP Method Comparison – Action & Target per Step',
        '',
        'Each cell shows `Action`: target(s).  Multi-pair steps use ➜ as separator.',
        '✓ = action correct AND all targets match.  ✗ = mismatch.',
        '',
        '---',
        '',
    ]

    for tc in all_cases:
        lines += [
            f"## {tc['file']}",
            f"**{tc['title']}**  ",
            f"URLs: {', '.join(tc['urls'])}",
            '',
        ]
        header = '| # | Step | Ground Truth |' + ''.join(f' {lb} |' for lb in col_labels)
        sep    = '|---|------|-------------|' + ''.join('---------|' for _ in col_labels)
        lines += [header, sep]

        for i, sr in enumerate(tc['analysed_steps'], 1):
            step        = sr['step'].replace('|', '\\|')
            key         = (tc['file'], sr['step'])
            truth_pairs = truth_index.get(key, [])
            gt_cell     = _fmt_pairs([{'action': p['action'], 'targets': p['targets']}
                                       for p in truth_pairs]).replace('|', '\\|')
            cells: List[str] = []
            for a_dict in sr['analyses']:
                extracted = [ActionTarget(p['action'], p['targets']) for p in a_dict['pairs']]
                correct = all(
                    _pair_correct(
                        extracted[j] if j < len(extracted) else ActionTarget('', []),
                        tp
                    )[1]
                    for j, tp in enumerate(truth_pairs)
                ) if truth_pairs else True
                mark = '✓' if correct else '✗'
                cell = f"{mark} {_fmt_pairs(a_dict['pairs'])}"
                cells.append(cell.replace('|', '\\|'))

            lines.append(f"| {i} | {step} | {gt_cell} |" +
                         ''.join(f' {c} |' for c in cells))
        lines += ['', '---', '']

    Path(out_path).write_text('\n'.join(lines), encoding='utf-8')
    print(f'Results table      → {out_path}')


# ─── Output: accuracy report ──────────────────────────────────────────────────

def generate_accuracy_report(stats: Dict[str, Dict],
                              out_path: str = 'nlp_accuracy_report.md') -> None:
    lines: List[str] = [
        '# NLP Method Accuracy Report',
        '',
        'Evaluated against `ground_truth.json`.',
        '',
        '**Action accuracy** = action verb correct / total pairs.',
        '**Pair accuracy**   = action correct AND all ground-truth targets matched (relaxed substring).',
        '',
        '| Method | Action Correct | Pair Correct | Total Pairs | Action Acc | Pair Acc |',
        '|--------|---------------|-------------|-------------|-----------|---------|',
    ]
    for mid, label, _ in METHODS:
        s = stats[mid]
        lines.append(
            f"| {label} | {s['action_correct']} | {s['pair_correct']} "
            f"| {s['total']} | **{s['action_acc']}%** | **{s['pair_acc']}%** |"
        )
    lines += [
        '',
        '---',
        '',
        '## Notes',
        '',
        '- Target matching is **relaxed**: extracted target passes if it is a',
        '  substring of the ground-truth target or vice versa (case-insensitive).',
        '- A pair is counted correct only when **both** action and **all** ground-truth targets match.',
        '- Compound steps (e.g., "Enter X and Click Y") count as separate pairs.',
        '',
        '_Report auto-generated by `test_case_reader.py`_',
    ]
    Path(out_path).write_text('\n'.join(lines), encoding='utf-8')
    print(f'Accuracy report    → {out_path}')


# ─── Output: per-method result files (CSV) ───────────────────────────────────

def save_per_method_results(all_cases: List[Dict], out_dir: str = '.') -> None:
    """Write one results_<method_id>.csv per method.

    Columns: file, title, step_number, step, action, targets, confidence
    Compound steps (multiple pairs) produce multiple rows with the same step_number.
    """
    for method_id, label, _ in METHODS:
        out_path = Path(out_dir) / f'results_{method_id}.csv'
        with out_path.open('w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(['file', 'title', 'step_number', 'step', 'action', 'targets', 'confidence'])
            for tc in all_cases:
                for step_num, sr in enumerate(tc['analysed_steps'], 1):
                    a_dict = next((a for a in sr['analyses'] if a['method'] == method_id), None)
                    if a_dict is None:
                        continue
                    pairs = a_dict['pairs']
                    if pairs:
                        for p in pairs:
                            writer.writerow([
                                tc['file'], tc['title'], step_num, sr['step'],
                                p['action'], ', '.join(p['targets']), a_dict['confidence'],
                            ])
                    else:
                        writer.writerow([
                            tc['file'], tc['title'], step_num, sr['step'],
                            '', '', a_dict['confidence'],
                        ])
        print(f'Per-method result  → {out_path}  ({label})')


# ─── Output: unified comparison CSV ──────────────────────────────────────────

def generate_combined_csv(all_cases: List[Dict], truth_data: List[Dict],
                          out_path: str = 'nlp_comparison.csv') -> None:
    """Write one row per ground-truth pair with ground truth and all 6 method outputs.

    Columns: file, title, step_number, step,
             gt_action, gt_targets,
             m1_action, m1_targets, m1_correct,
             m2_action, m2_targets, m2_correct,
             ... (same for m3–m6)
    """
    truth_index: Dict[Tuple[str, str], List[Dict]] = {}
    for tc in truth_data:
        for s in tc['steps']:
            truth_index[(tc['file'], s['step'])] = s['pairs']

    method_ids = [mid for mid, _, _ in METHODS]
    method_short = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']

    header = ['file', 'title', 'step_number', 'step', 'gt_action', 'gt_targets']
    for short in method_short:
        header += [f'{short}_action', f'{short}_targets', f'{short}_correct']

    with open(out_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(header)

        for tc in all_cases:
            for step_num, sr in enumerate(tc['analysed_steps'], 1):
                key = (tc['file'], sr['step'])
                truth_pairs = truth_index.get(key, [])

                # Build per-method extracted pairs lookup
                method_pairs: Dict[str, List[ActionTarget]] = {}
                for a_dict in sr['analyses']:
                    mid = a_dict['method']
                    method_pairs[mid] = [ActionTarget(p['action'], p['targets']) for p in a_dict['pairs']]

                # One row per ground-truth pair (or one row if no ground truth)
                if not truth_pairs:
                    row = [tc['file'], tc['title'], step_num, sr['step'], '', '']
                    for mid in method_ids:
                        extracted = method_pairs.get(mid, [])
                        ep = extracted[0] if extracted else ActionTarget('', [])
                        row += [ep.action, ', '.join(ep.targets), '']
                    writer.writerow(row)
                    continue

                for pair_idx, tp in enumerate(truth_pairs):
                    gt_action = tp['action']
                    gt_targets = ', '.join(tp['targets'])
                    row = [tc['file'], tc['title'], step_num, sr['step'], gt_action, gt_targets]
                    for mid in method_ids:
                        extracted = method_pairs.get(mid, [])
                        ep = extracted[pair_idx] if pair_idx < len(extracted) else ActionTarget('', [])
                        _, pair_ok = _pair_correct(ep, tp)
                        row += [ep.action, ', '.join(ep.targets), 'TRUE' if pair_ok else 'FALSE']
                    writer.writerow(row)

    print(f'Combined comparison → {out_path}')


# ─── Main ─────────────────────────────────────────────────────────────────────

def run(files_dir: str = '.') -> List[Dict]:
    feature_files = sorted(Path(files_dir).glob('*.feature'))
    print(f'Found {len(feature_files)} .feature file(s)')
    print(f'NLTK  : {"available" if NLTK_AVAILABLE  else "unavailable"}')
    print(f'spaCy : {"available" if SPACY_AVAILABLE else "unavailable"}')
    print()

    all_cases: List[Dict] = []
    for fp in feature_files:
        tc = parse_feature_file(fp)
        print(f"{'='*70}")
        print(f"File : {tc['file']}")
        print(f"Title: {tc['title']}")
        print()

        analysed_steps: List[Dict] = []
        for i, step in enumerate(tc['steps'], 1):
            result = analyse_step(step)
            analysed_steps.append(result)
            print(f"  Step {i:2d}: {step}")
            for p in result['best']['pairs']:
                tstr = ', '.join(p['targets']) if p['targets'] else '(none)'
                print(f"          Action → {p['action'] or '(none)':<20s} Targets → {tstr}")
        print()
        all_cases.append({**tc, 'analysed_steps': analysed_steps})

    return all_cases


if __name__ == '__main__':
    truth_data = json.loads(Path('ground_truth.json').read_text(encoding='utf-8'))

    results = run('.')

    with open('nlp_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('Full results       → nlp_analysis_results.json')

    save_per_method_results(results, '.')
    generate_combined_csv(results, truth_data, 'nlp_comparison.csv')

    stats = evaluate(results, truth_data)
    generate_results_table(results, truth_data, 'nlp_results_table.md')
    generate_accuracy_report(stats, 'nlp_accuracy_report.md')
