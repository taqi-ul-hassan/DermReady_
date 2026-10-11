import json
from pathlib import Path
import numpy as np
from src.feedback import decide_with_reason,decide_state,UNCERTAIN,SUITABLE,RETAKE,quality_flags

T={'blur_low':3.,'blur_high':8.,'brightness_low':.28,'brightness_high':.63,'dark_fraction_high':.27,'bright_fraction_high':.017,'minimum_short_side':256}
P={'retake_below':.67,'suitable_above':.92}
F={'blur_log_laplacian':5.,'brightness_mean':.5,'contrast_std':.2,'dark_fraction':0.,'bright_fraction':0.,'min_dimension_log':np.log1p(512),'aspect_ratio':1.}
M={'original_mode':'RGB','alpha_composited':False}


def test_uncertainty_reports_specific_causes():
    assert 'between' in decide_with_reason(.8,P,F,M,T)[2]
    assert 'block acceptance' in decide_with_reason(.99,P,{**F,'brightness_mean':.9},M,T)[2]
    assert 'color mode' in decide_with_reason(.8,P,F,{**M,'original_mode':'L'},T)[2]
    assert 'Transparency' in decide_with_reason(.8,P,F,{**M,'alpha_composited':True},T)[2]
    assert 'unavailable' in decide_with_reason(None,P,F,M,T)[2]


def test_frozen_rule_parity_including_bands_guards_and_modes():
    rng=np.random.default_rng(42)
    for _ in range(200):
        f={**F,'brightness_mean':float(rng.random()),'blur_log_laplacian':float(rng.uniform(0,10)),'contrast_std':float(rng.uniform(0,.3))}
        m={**M,'original_mode':rng.choice(['RGB','L']),'alpha_composited':bool(rng.integers(0,2))}
        score=float(rng.random());flags=quality_flags(f,T)
        if m['alpha_composited'] or m['original_mode'] not in ('RGB','RGBA') or f['aspect_ratio']>4 or 'unusual_texture' in flags or f['contrast_std']<.01:
            expected=UNCERTAIN
        elif score<=P['retake_below']:expected=RETAKE
        elif score>=P['suitable_above']:expected=UNCERTAIN if flags else SUITABLE
        else:expected=UNCERTAIN
        assert decide_state(score,P,f,m,T)==(expected,flags)
