"""Capture-quality proxies, measured on the oriented image, not the model tensor."""
import cv2
import numpy as np
from PIL import ImageOps, Image

FEATURE_NAMES = ('blur_log_laplacian', 'brightness_mean', 'contrast_std', 'dark_fraction',
                 'bright_fraction', 'min_dimension_log', 'megapixels_log', 'aspect_ratio')


def extract_quality_features(image):
    # Fixed measurement scale reduces dependence of focus proxy on camera resolution.
    focus_image = ImageOps.contain(image, (256, 256), Image.Resampling.BILINEAR)
    focus_gray = cv2.cvtColor(np.asarray(focus_image), cv2.COLOR_RGB2GRAY)
    exposure_image = ImageOps.contain(image, (1024, 1024), Image.Resampling.BILINEAR)
    gray = cv2.cvtColor(np.asarray(exposure_image), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    lap = float(cv2.Laplacian(focus_gray, cv2.CV_64F).var())
    width, height = image.size
    return {'blur_log_laplacian': float(np.log1p(lap)), 'brightness_mean':float(gray.mean()),
            'contrast_std':float(gray.std()), 'dark_fraction':float((gray <= .05).mean()),
            'bright_fraction':float((gray >= .95).mean()), 'min_dimension_log':float(np.log1p(min(width,height))),
            'megapixels_log':float(np.log1p(width*height/1e6)), 'aspect_ratio':float(max(width,height)/min(width,height))}


def aggregate_quality_features(image_features):
    if not image_features:raise ValueError('At least one image is required')
    matrix=np.array([[r[name] for name in FEATURE_NAMES] for r in image_features],dtype=float)
    result={f'{stat}_{name}':float(values[i]) for stat,values in
            [('mean',matrix.mean(0)),('min',matrix.min(0)),('max',matrix.max(0))]
            for i,name in enumerate(FEATURE_NAMES)}
    result['image_count']=len(image_features)
    return result
