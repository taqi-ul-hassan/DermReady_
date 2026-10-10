import numpy as np
from PIL import Image
from src.perturbations import degrade
from src.quality_features import extract_quality_features


def test_paired_degradations_preserve_input_and_response():
    image=Image.fromarray(np.random.default_rng(42).integers(30,180,(256,256,3),dtype=np.uint8))
    source=np.array(image).copy();original=extract_quality_features(image)
    assert np.array_equal(np.array(degrade(image,'original')),source)
    for condition in ['blur_2','blur_5','dark_035','bright_180']:
        changed=degrade(image,condition)
        assert changed.size==image.size and changed.mode==image.mode
        assert np.array_equal(np.array(image),source)
        features=extract_quality_features(changed)
        if condition.startswith('blur'):assert features['blur_log_laplacian']<original['blur_log_laplacian']
        if condition.startswith('dark'):assert features['brightness_mean']<original['brightness_mean']
        if condition.startswith('bright'):assert features['brightness_mean']>original['brightness_mean']
