"""Validate fitted artifact structure before enabling learned decisions."""
import math
import numpy as np
from .quality_features import FEATURE_NAMES


def validate_thresholds(thresholds):
    keys=['blur_low','brightness_low','brightness_high','dark_fraction_high','bright_fraction_high','minimum_short_side']
    for key in keys:
        if not math.isfinite(float(thresholds[key])):raise ValueError('Nonfinite quality threshold')
    if not 0<=thresholds['brightness_low']<=thresholds['brightness_high']<=1:raise ValueError('Invalid exposure range')
    if any(not 0<=thresholds[k]<=1 for k in ['dark_fraction_high','bright_fraction_high']):raise ValueError('Invalid pixel-fraction threshold')
    if thresholds['blur_low']<0 or thresholds['minimum_short_side']<=0:raise ValueError('Invalid focus/resolution threshold')
    if 'blur_high' in thresholds and (not math.isfinite(float(thresholds['blur_high'])) or thresholds['blur_high']<=thresholds['blur_low']):raise ValueError('Invalid texture range')
    return thresholds


def validate_policy(policy):
    models=policy['models']
    if not models or not set(models).issubset({'cnn','quality_baseline'}):raise ValueError('Unsupported policy model')
    if policy['preferred_model'] not in models:raise ValueError('Preferred model has no policy')
    for bands in models.values():
        low,high=float(bands['retake_below']),float(bands['suitable_above'])
        if not math.isfinite(low) or not math.isfinite(high) or not -.01<=low<high<=1.01:raise ValueError('Invalid decision bands')
    validate_thresholds(policy['quality_thresholds'])
    return policy


def validate_baseline(baseline):
    expected={f'{stat}_{name}' for stat in ['mean','min','max'] for name in FEATURE_NAMES}|{'image_count'}
    columns=baseline['columns']
    if len(columns)!=len(expected) or set(columns)!=expected:raise ValueError('Baseline columns do not match capture features')
    for key in ['mean','scale','coefficient']:
        values=np.asarray(baseline[key],dtype=float)
        if values.shape!=(len(columns),) or not np.isfinite(values).all():raise ValueError('Invalid baseline array')
    if (np.asarray(baseline['scale'],dtype=float)<=0).any() or not math.isfinite(float(baseline['intercept'])):raise ValueError('Invalid baseline scale/intercept')
    return baseline
