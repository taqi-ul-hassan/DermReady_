import numpy as np
from PIL import Image,ImageFilter,ImageEnhance
from src.quality_features import extract_quality_features,aggregate_quality_features


def test_quality_proxies_respond_to_controlled_changes():
    rng=np.random.default_rng(42)
    image=Image.fromarray(rng.integers(20,230,(256,256,3),dtype=np.uint8))
    original=extract_quality_features(image)
    blurred=extract_quality_features(image.filter(ImageFilter.GaussianBlur(3)))
    dark=extract_quality_features(ImageEnhance.Brightness(image).enhance(.3))
    assert blurred['blur_log_laplacian']<original['blur_log_laplacian']
    assert dark['brightness_mean']<original['brightness_mean']
    assert dark['dark_fraction']>=original['dark_fraction']


def test_case_aggregation_has_no_metadata_or_disease_features():
    a=extract_quality_features(Image.new('RGB',(100,200),'black'))
    b=extract_quality_features(Image.new('RGB',(100,200),'white'))
    result=aggregate_quality_features([a,b])
    assert result['image_count']==2
    assert result['min_brightness_mean']==0 and result['max_brightness_mean']==1
    assert abs(result['mean_brightness_mean']-.5)<1e-6
