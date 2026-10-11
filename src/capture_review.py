"""Presentation helpers; never alter the frozen suitability policy."""
import json
from pathlib import Path
from PIL import ImageChops

from .preprocessing import load_image
from .quality_features import extract_quality_features

CAPTURE_CHECKLIST = [
    'I checked the views and context requested by my clinician.',
    'I checked visible sharpness at the area of interest.',
    'I checked whether shadows or glare hide detail.',
    'I am using an original photograph rather than a screenshot.',
]


def checklist_progress(selected):
    count = len(set(selected or ()) & set(CAPTURE_CHECKLIST))
    return f'{count} of {len(CAPTURE_CHECKLIST)} checks reviewed. These are your own checks; they do not change the research assessment.'


def indicator_rows(result, thresholds):
    f, m = result['features'], result['metadata']
    flags = set(result['flags'])
    available = bool(thresholds)
    def status(keys):
        if not available:return 'No reference available'
        return 'Inspect visually' if flags.intersection(keys) else 'No reference flag'
    return [
        ['Focus proxy', f"{f['blur_log_laplacian']:.2f}", status({'focus', 'unusual_texture'})],
        ['Mean brightness', f"{100*f['brightness_mean']:.1f}%", status({'dark', 'bright'})],
        ['Dark pixels', f"{100*f['dark_fraction']:.1f}%", status({'dark'})],
        ['Bright pixels', f"{100*f['bright_fraction']:.1f}%", status({'bright'})],
        ['Contrast proxy', f"{f['contrast_std']:.3f}", 'Inspect visually' if f['contrast_std'] < .01 else 'No validated defect threshold'],
        ['Resolution', f"{m['width']} × {m['height']} pixels", status({'resolution'})],
    ]


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
    first, first_metadata = load_image(original)
    second, second_metadata = load_image(retake)
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
    if first.size == second.size and ImageChops.difference(first, second).getbbox() is None:
        notes.append('Both uploads contain identical decoded pixels. Choose a newly captured photograph to compare a retake.')
    ratio_a, ratio_b = first.width / first.height, second.width / second.height
    if abs(ratio_a - ratio_b) / max(ratio_a, ratio_b) > .10:
        notes.append('Aspect ratio or orientation changed substantially. Framing may differ; do not interpret proxy changes as improvement.')
    area_a, area_b = first.width * first.height, second.width * second.height
    if max(area_a, area_b) / min(area_a, area_b) > 2:
        notes.append('Pixel count changed by more than twofold. Check for resizing or cropping and compare original-resolution files.')
    if any(m['alpha_composited'] or m['original_mode'] != 'RGB' for m in (first_metadata, second_metadata)):
        notes.append('At least one upload required color conversion or transparency compositing; pixel signals may reflect that conversion.')
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

