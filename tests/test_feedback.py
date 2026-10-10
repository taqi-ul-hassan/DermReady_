import math
from src.feedback import SUITABLE,RETAKE,UNCERTAIN,decide_state,make_feedback
from scripts.select_policy import select_thresholds

T={'blur_low':1.,'brightness_low':.1,'brightness_high':.9,'dark_fraction_high':.5,'bright_fraction_high':.5,'minimum_short_side':256}
F={'blur_log_laplacian':4.,'brightness_mean':.5,'contrast_std':.2,'dark_fraction':0.,'bright_fraction':0.,'min_dimension_log':math.log1p(512),'aspect_ratio':1.}
M={'original_mode':'RGB','alpha_composited':False}
P={'retake_below':.3,'suitable_above':.8}


def test_three_states_and_boundaries():
    assert decide_state(.3,P,F,M,T)[0]==RETAKE
    assert decide_state(.8,P,F,M,T)[0]==SUITABLE
    assert decide_state(.5,P,F,M,T)[0]==UNCERTAIN
    assert decide_state(float('nan'),P,F,M,T)[0]==UNCERTAIN


def test_capture_flag_blocks_acceptance_and_unsupported_input_is_uncertain():
    low_focus={**F,'blur_log_laplacian':0.}
    state,flags=decide_state(.99,P,low_focus,M,T)
    assert state==UNCERTAIN and 'focus' in flags
    assert 'focus' in make_feedback(state,flags)
    assert decide_state(.99,P,F,{**M,'alpha_composited':True},T)[0]==UNCERTAIN
    assert decide_state(None,P,F,M,T)[0]==UNCERTAIN


def test_threshold_selector_disables_acceptance_for_unseparated_scores():
    policy=select_thresholds([0]*12+[1]*12,[.5]*24)
    assert not policy['suitable_enabled'] and policy['suitable_above']>1
    assert policy['retake_below']<policy['suitable_above']


def test_threshold_selector_meets_documented_empirical_constraints():
    labels=[0]*20+[1]*40
    scores=[.1]*18+[.6]*2+[.9]*40
    policy=select_thresholds(labels,scores)
    assert policy['false_acceptance_rate_all_ungradable']<=.1
    assert policy['false_rejection_rate_all_gradable']<=.35


def test_out_of_range_texture_is_uncertain():
    state,flags=decide_state(.99,P,{**F,'blur_log_laplacian':20.},M,{**T,'blur_high':8.})
    assert state==UNCERTAIN and 'unusual_texture' in flags
