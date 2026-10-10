import io
import numpy as np
from PIL import Image
import pytest
import torch
from src.preprocessing import load_image, model_transform, preprocess_for_inference


def test_invalid_tiny_and_animated_inputs():
    with pytest.raises(ValueError):load_image(b'not an image')
    with pytest.raises(ValueError):load_image(Image.new('RGB',(12,50)))
    blob=io.BytesIO();frames=[Image.new('RGB',(40,40),c) for c in ('red','blue')]
    frames[0].save(blob,format='GIF',save_all=True,append_images=frames[1:])
    with pytest.raises(ValueError):load_image(blob.getvalue())


def test_rgb_alpha_grayscale_and_orientation():
    image,info=load_image(Image.new('RGBA',(40,60),(255,0,0,0)))
    assert image.mode=='RGB' and info['alpha_composited'] and image.getpixel((0,0))==(255,255,255)
    assert load_image(Image.new('L',(40,60)))[0].mode=='RGB'
    source=Image.new('RGB',(40,60));exif=source.getexif();exif[274]=6
    blob=io.BytesIO();source.save(blob,format='JPEG',exif=exif)
    image,_=load_image(blob.getvalue())
    assert image.size==(60,40) and not image.info


def test_inference_matches_validation_and_preserves_input():
    image=Image.new('RGB',(80,160),'red');original=np.asarray(image).copy()
    output=preprocess_for_inference(image)
    assert output.shape==(3,224,224) and torch.isfinite(output).all()
    assert torch.equal(output,model_transform(False)(image))
    assert np.array_equal(original,np.asarray(image))
