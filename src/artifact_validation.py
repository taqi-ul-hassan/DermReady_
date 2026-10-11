"""Validate fitted artifact structure before enabling learned decisions."""
import math
from numbers import Real
import numpy as np
from .quality_features import FEATURE_NAMES


def validate_thresholds(thresholds):
    if not isinstance(thresholds,dict):raise ValueError('Quality thresholds must be an object')
    keys=['blur_low','brightness_low','brightness_high','dark_fraction_high','bright_fraction_high','minimum_short_side']
    for key in keys:
        if isinstance(thresholds[key],bool) or not isinstance(thresholds[key],Real):raise ValueError('Thresholds must be numeric')
        if not math.isfinite(float(thresholds[key])):raise ValueError('Nonfinite quality threshold')
    if not 0<=thresholds['brightness_low']<=thresholds['brightness_high']<=1:raise ValueError('Invalid exposure range')
    if any(not 0<=thresholds[k]<=1 for k in ['dark_fraction_high','bright_fraction_high']):raise ValueError('Invalid pixel-fraction threshold')
    if thresholds['blur_low']<0 or thresholds['minimum_short_side']<=0:raise ValueError('Invalid focus/resolution threshold')
    if 'blur_high' in thresholds and (isinstance(thresholds['blur_high'],bool) or not isinstance(thresholds['blur_high'],Real) or not math.isfinite(float(thresholds['blur_high'])) or thresholds['blur_high']<=thresholds['blur_low']):raise ValueError('Invalid texture range')
    return thresholds


def validate_policy(policy):
    if not isinstance(policy,dict):raise ValueError('Policy must be an object')
    models=policy['models']
    if not isinstance(models,dict):raise ValueError('Policy models must be an object')
    if not models or not set(models).issubset({'cnn','quality_baseline'}):raise ValueError('Unsupported policy model')
    if policy['preferred_model'] not in models:raise ValueError('Preferred model has no policy')
    for bands in models.values():
        if not isinstance(bands,dict) or any(isinstance(bands[k],bool) or not isinstance(bands[k],Real) for k in ['retake_below','suitable_above']):raise ValueError('Decision bands must be numeric')
        low,high=float(bands['retake_below']),float(bands['suitable_above'])
        if not math.isfinite(low) or not math.isfinite(high) or not -.01<=low<high<=1.01:raise ValueError('Invalid decision bands')
    validate_thresholds(policy['quality_thresholds'])
    return policy


def validate_baseline(baseline):
    if not isinstance(baseline,dict):raise ValueError('Baseline must be an object')
    expected={f'{stat}_{name}' for stat in ['mean','min','max'] for name in FEATURE_NAMES}|{'image_count'}
    columns=baseline['columns']
    if len(columns)!=len(expected) or set(columns)!=expected:raise ValueError('Baseline columns do not match capture features')
    for key in ['mean','scale','coefficient']:
        if not isinstance(baseline[key],list) or any(isinstance(v,bool) or not isinstance(v,Real) for v in baseline[key]):raise ValueError('Baseline arrays must be numeric')
        values=np.asarray(baseline[key],dtype=float)
        if values.shape!=(len(columns),) or not np.isfinite(values).all():raise ValueError('Invalid baseline array')
    if isinstance(baseline['intercept'],bool) or not isinstance(baseline['intercept'],Real) or (np.asarray(baseline['scale'],dtype=float)<=0).any() or not math.isfinite(float(baseline['intercept'])):raise ValueError('Invalid baseline scale/intercept')
    return baseline

