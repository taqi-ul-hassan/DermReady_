"""Conservative score bands and supported, non-diagnostic capture suggestions."""
import math

SUITABLE='likely suitable for review'
RETAKE='may need a retake'
UNCERTAIN='uncertain'
NOTICE='Research prototype only; not a diagnosis or substitute for medical advice. No result guarantees clinical adequacy. Follow your clinician\'s instructions.'


def quality_flags(features,thresholds):
    flags=[]
    if features['blur_log_laplacian']<thresholds['blur_low']:flags.append('focus')
    if features['blur_log_laplacian']>thresholds.get('blur_high',float('inf')):flags.append('unusual_texture')
    if features['brightness_mean']<thresholds['brightness_low'] or features['dark_fraction']>thresholds['dark_fraction_high']:flags.append('dark')
    if features['brightness_mean']>thresholds['brightness_high'] or features['bright_fraction']>thresholds['bright_fraction_high']:flags.append('bright')
    if math.expm1(features['min_dimension_log'])<thresholds['minimum_short_side']:flags.append('resolution')
    return flags


def decide_state(score,policy,features,metadata,thresholds):
    flags=quality_flags(features,thresholds)
    # These checks identify unsupported formats/content extremes, not skin detection.
    unsupported=metadata.get('alpha_composited') or metadata.get('original_mode') not in ('RGB','RGBA') or features['aspect_ratio']>4
    if unsupported or 'unusual_texture' in flags or features['contrast_std']<.01 or score is None or not math.isfinite(score):
        return UNCERTAIN,flags
    if score<=policy['retake_below']:return RETAKE,flags
    if score>=policy['suitable_above']:
        return (UNCERTAIN if flags else SUITABLE),flags
    return UNCERTAIN,flags


def make_feedback(state,flags):
    suggestions=[]
    if 'unusual_texture' in flags:suggestions.append('The high-frequency texture signal is outside the reference range. This prototype cannot support an acceptance decision for this image.')
    if 'focus' in flags:suggestions.append('The focus proxy is low. Hold the camera steady, tap to focus, and check that the area is sharp.')
    if 'dark' in flags:suggestions.append('The exposure signal is low. Consider even, diffuse lighting and avoid shadows.')
    if 'bright' in flags:suggestions.append('The exposure signal is high. Avoid glare, direct flash, and overexposed areas.')
    if 'resolution' in flags:suggestions.append('The image is small. Upload the original photograph rather than a resized screenshot.')
    if state==RETAKE and not suggestions:suggestions.append('The case-trained estimate is low, but no specific capture defect was established. Check the image against your clinician\'s requested views; retaking may not resolve the issue.')
    if state==UNCERTAIN:suggestions.append('The prototype cannot make a supported acceptance decision. Follow your clinician\'s instructions.')
    if state==SUITABLE:suggestions.append('This image resembles accepted examples under the research policy. A clinician must still decide whether it is adequate.')
    suggestions.append('Framing is not assessed automatically. Include the views and context requested by your clinician.')
    return '\n\n'.join(suggestions)
