"""Presentation helpers; never alter the frozen suitability policy."""
import json
from pathlib import Path

from .preprocessing import load_image
from .quality_features import extract_quality_features


def primary_action(result):
    if result['model'] == 'features_only':
        return 'Review capture indicators; no fitted suitability decision is available.'
    actions = {
        'unusual_texture': 'Use an original photograph; this texture is outside the reference range.',
        'focus': 'Hold the camera steady and tap to focus on the area of interest.',
        'dark': 'Inspect shadows and visible detail; low brightness alone does not establish underexposure.',
        'bright': 'Inspect glare and visible detail; high brightness alone does not establish overexposure.',
        'resolution': 'Use the full-resolution original instead of a screenshot.',
    }
    for flag, action in actions.items():
        if flag in result['flags']:
            return action
    return 'Follow your clinician’s requested views; this prototype cannot guarantee adequacy.'


def compare_captures(original, retake):
    """Compare measured signals, not clinical adequacy or model probabilities."""
    if not original or not retake:
        raise ValueError('Choose both the original photograph and a new capture.')
    first, _ = load_image(original)
    second, _ = load_image(retake)
    a, b = map(extract_quality_features, (first, second))
    rows = []
    for label, key, scale in [
        ('Focus proxy', 'blur_log_laplacian', 1),
        ('Mean brightness (%)', 'brightness_mean', 100),
        ('Dark pixels (%)', 'dark_fraction', 100),
        ('Bright pixels (%)', 'bright_fraction', 100),
        ('Contrast proxy', 'contrast_std', 1),
    ]:
        before, after = a[key] * scale, b[key] * scale
        rows.append([label, round(before, 3), round(after, 3), round(after - before, 3)])
    notes = []
    if b['blur_log_laplacian'] > a['blur_log_laplacian']:
        notes.append('The focus proxy increased; texture and lighting can also cause this change.')
    else:
        notes.append('The focus proxy did not increase. Check sharpness at the area of interest.')
    if b['dark_fraction'] < a['dark_fraction']:
        notes.append('The proportion of very dark pixels decreased.')
    if b['bright_fraction'] > a['bright_fraction']:
        notes.append('The proportion of very bright pixels increased; check for glare or clipping.')
    notes.append('Higher brightness or contrast is not automatically better. Different framing makes these measurements less comparable. No clinical improvement or suitability is established; check the new capture separately and follow your clinician’s instructions.')
    return first, second, rows, '\n\n'.join(notes)


def evidence_summary(report_path):
    """Read historical evaluation, keeping it separate from live upload results."""
    try:
        report = json.loads(Path(report_path).read_text())
        rows = []
        for name, result in report['single_image_weak_proxy'].items():
            metrics = result['pipeline']
            rows.append([
                name,
                f"{100 * metrics['false_acceptance_rate_all_ungradable']:.1f}%",
                f"{100 * metrics['false_rejection_rate_all_gradable']:.1f}%",
                f"{100 * metrics['decision_coverage']:.1f}%",
                f"{100 * metrics['uncertainty_fraction']:.1f}%",
            ])
        return rows
    except (OSError, ValueError, KeyError, TypeError):
        return []
