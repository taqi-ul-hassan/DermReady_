"""Deterministic capture degradations; never change ground-truth case labels."""
from PIL import ImageEnhance, ImageFilter

CONDITIONS = {
    'original': {'kind': 'identity', 'value': 0},
    'blur_2': {'kind': 'gaussian_blur', 'value': 2},
    'blur_5': {'kind': 'gaussian_blur', 'value': 5},
    'dark_035': {'kind': 'brightness_multiplier', 'value': .35},
    'bright_180': {'kind': 'brightness_multiplier', 'value': 1.8},
}


def degrade(image, condition):
    config = CONDITIONS[condition]
    if config['kind'] == 'identity':
        return image.copy()
    if config['kind'] == 'gaussian_blur':
        return image.filter(ImageFilter.GaussianBlur(config['value']))
    return ImageEnhance.Brightness(image).enhance(config['value'])
