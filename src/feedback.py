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


def decide_with_reason(score,policy,features,metadata,thresholds):
    """Same frozen decision rules, with a specific explanation for the output."""
    flags=quality_flags(features,thresholds)
    if metadata.get('alpha_composited'):
        return UNCERTAIN,flags,'Transparency was composited onto white; this input is outside the validated color-photo path.'
    if metadata.get('original_mode') not in ('RGB','RGBA'):
        return UNCERTAIN,flags,'The original image color mode is outside the validated RGB-photo path.'
    if features['aspect_ratio']>4:
        return UNCERTAIN,flags,'The image has an extreme aspect ratio outside the validated input range.'
    if 'unusual_texture' in flags:
        return UNCERTAIN,flags,'The texture signal is above the reference range; the model cannot support acceptance.'
    if features['contrast_std']<.01:
        return UNCERTAIN,flags,'The image is nearly uniform, so there is too little measured contrast for a supported assessment.'
    if score is None or not math.isfinite(score):
        return UNCERTAIN,flags,'A valid fitted-model score is unavailable.'
    if score<=policy['retake_below']:
        return RETAKE,flags,'The research score is in the retake band; this does not establish a specific photographic defect.'
    if score>=policy['suitable_above']:
        if flags:
            return UNCERTAIN,flags,'The score reaches the acceptance band, but capture indicators block acceptance: '+', '.join(flags)+'.'
        return SUITABLE,flags,'The score reaches the acceptance band and no capture guard is triggered; clinical adequacy is not established.'
    return UNCERTAIN,flags,'The research score is between the retake and acceptance thresholds; the model does not support either decision.'


def decide_state(score,policy,features,metadata,thresholds):
    state,flags,_=decide_with_reason(score,policy,features,metadata,thresholds)
    return state,flags


def make_feedback(state,flags):
    suggestions=[]
    if 'unusual_texture' in flags:suggestions.append('The high-frequency texture signal is outside the reference range. This prototype cannot support an acceptance decision for this image.')
    if 'focus' in flags:suggestions.append('The focus proxy is low; lighting, texture, and smooth surfaces can also affect it. Check visible sharpness before retaking; hold the camera steady and tap to focus if needed.')
    if 'dark' in flags:suggestions.append('The brightness signal is below the reference range. Skin tone and background can affect it; this does not establish underexposure. If shadows hide detail, consider even, diffuse lighting.')
    if 'bright' in flags:suggestions.append('Brightness or the bright-pixel signal is above the reference range; background can affect it. If glare washes out detail, avoid direct flash and overexposed areas.')
    if 'resolution' in flags:suggestions.append('The image is small. Upload the original photograph rather than a resized screenshot.')
    if state==RETAKE and not suggestions:suggestions.append('The case-trained estimate is low, but no specific capture defect was established. Check the image against your clinician\'s requested views; retaking may not resolve the issue.')
    if state==UNCERTAIN:suggestions.append('The prototype cannot make a supported acceptance decision. Follow your clinician\'s instructions.')
    if state==SUITABLE:suggestions.append('This image resembles accepted examples under the research policy. A clinician must still decide whether it is adequate.')
    suggestions.append('Framing is not assessed automatically. Include the views and context requested by your clinician.')
    return '\n\n'.join(suggestions)
