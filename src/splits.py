"""Deterministic case components and label-balanced grouped holdouts."""
import hashlib
import json
from collections import defaultdict
import numpy as np

SPLIT_NAMES = ('train', 'validation', 'test')


def connected_case_groups(records, inventory):
    """Connect all cases, including excluded cases, by shared path or object MD5."""
    parent = {r['case_id']: r['case_id'] for r in records}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    owners = {}
    for record in sorted(records, key=lambda r: r['case_id']):
        for path in record['image_paths']:
            keys = [('path', path)]
            digest = inventory.get(path, {}).get('md5Hash')
            if digest:
                keys.append(('md5', digest))
            for key in keys:
                if key in owners:
                    union(record['case_id'], owners[key])
                else:
                    owners[key] = record['case_id']
    components = defaultdict(list)
    for case_id in sorted(parent):
        components[find(case_id)].append(case_id)
    result = {}
    for members in components.values():
        digest = hashlib.sha256(json.dumps(members, separators=(',', ':')).encode()).hexdigest()
        for case_id in members:
            result[case_id] = digest
    return result


def assign_splits(records, fractions=(0.70, 0.15, 0.15), seed=42, attempts=512):
    """Select a grouped permutation by counts only; never use images/model outcomes."""
    fractions = np.asarray(fractions, dtype=float)
    if len(fractions) != 3 or not np.isfinite(fractions).all() or (fractions <= 0).any() or not np.isclose(fractions.sum(), 1):
        raise ValueError('Three positive split fractions must sum to 1')
    if attempts < 1:
        raise ValueError('attempts must be positive')
    by_group = defaultdict(list)
    for r in sorted(records, key=lambda r: r['case_id']):
        if r['label'] not in (0, 1):
            raise ValueError('Only binary eligible records may be split')
        by_group[r['group_id']].append(r)
    groups = sorted(by_group)
    if len(groups) < 3:
        raise ValueError('At least three independent case groups are required')
    counts = np.array([[sum(r['label'] == label for r in by_group[g]) for label in (0, 1)] for g in groups])
    totals = counts.sum(axis=0)
    if (totals < 3).any():
        raise ValueError('Each class needs at least three cases for three holdouts')
    target = fractions[:, None] * totals[None, :]
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(attempts):
        order = rng.permutation(len(groups))
        cumulative = np.cumsum(counts[order].sum(axis=1))
        cut1 = int(np.argmin(abs(cumulative[:-2] - fractions[0] * totals.sum()))) + 1
        possible = np.arange(cut1, len(groups)-1)
        cut2 = int(possible[np.argmin(abs(cumulative[possible] - fractions[:2].sum() * totals.sum()))]) + 1
        chunks = (order[:cut1], order[cut1:cut2], order[cut2:])
        observed = np.array([counts[chunk].sum(axis=0) for chunk in chunks])
        if (observed == 0).any():
            continue
        score = float((((observed-target)/np.maximum(target, 1))**2).sum())
        if best is None or score < best[0]:
            best = (score, chunks)
    if best is None:
        raise ValueError('Cannot form three grouped holdouts containing both classes')
    assignments = {}
    for name, chunk in zip(SPLIT_NAMES, best[1]):
        for index in chunk:
            for r in by_group[groups[index]]:
                assignments[r['case_id']] = name
    return assignments


def verify_splits(records, assignments, inventory):
    """Fail on missing assignments or case/component/path/content leakage."""
    ids = [r['case_id'] for r in records]
    if len(ids) != len(set(ids)) or set(ids) != set(assignments):
        raise ValueError('Duplicate cases or incomplete/extra split assignments')
    owners = {}
    for r in records:
        split = assignments[r['case_id']]
        if split not in SPLIT_NAMES:
            raise ValueError('Unknown split')
        keys = [('group', r['group_id'])]
        for path in r['image_paths']:
            if path not in inventory:
                raise ValueError('Eligible record references a missing image')
            keys.append(('path', path))
            if inventory[path].get('md5Hash'):
                keys.append(('md5', inventory[path]['md5Hash']))
        for key in keys:
            if key in owners and owners[key] != split:
                raise ValueError(f'Cross-split leakage detected for {key[0]}')
            owners[key] = split
    return {'case_overlap': 0, 'component_overlap': 0, 'image_path_overlap': 0, 'known_content_hash_overlap': 0}
