"""Bounded image decoding and shared aspect-preserving model transforms."""
import io
from pathlib import Path
import warnings
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
import torch
from torchvision import transforms

MAX_BYTES = 20 * 1024 * 1024
MAX_PIXELS = 24_000_000
SUPPORTED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def load_image(source):
    """Decode without trusting extensions; return EXIF-oriented original RGB + metadata."""
    if isinstance(source, Image.Image):
        image = source.copy()
        original_format = source.format
        if getattr(source, 'n_frames', 1) != 1:
            raise ValueError('Upload a single still photograph, not an animation.')
    else:
        if isinstance(source, (str, Path)):
            path = Path(source)
            if path.stat().st_size > MAX_BYTES:
                raise ValueError('Image file exceeds the 20 MB limit.')
            blob = path.read_bytes()
        elif isinstance(source, bytes):
            blob = source
        else:
            raise ValueError('Choose a PNG, JPEG, or WebP photograph.')
        if len(blob) > MAX_BYTES:
            raise ValueError('Image file exceeds the 20 MB limit.')
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(blob)) as probe:
                    if probe.format not in SUPPORTED_FORMATS:
                        raise ValueError('Supported formats: PNG, JPEG, and still WebP.')
                    if getattr(probe, 'n_frames', 1) != 1:
                        raise ValueError('Upload a single still photograph, not an animation.')
                    if probe.width * probe.height > MAX_PIXELS:
                        raise ValueError('Image exceeds the 24 megapixel limit.')
                    probe.verify()
                image = Image.open(io.BytesIO(blob))
                image.load()
                original_format = image.format
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise ValueError('The file is corrupt, unreadable, or too large. Choose another image.') from exc
    if image.width * image.height > MAX_PIXELS:
        raise ValueError('Image exceeds the 24 megapixel limit.')
    if min(image.size) < 32:
        raise ValueError('Image is too small: each dimension must be at least 32 pixels.')
    if max(image.size) / min(image.size) > 12:
        raise ValueError('Image aspect ratio is too extreme for this prototype.')
    original_mode = image.mode
    alpha = 'A' in image.getbands() or 'transparency' in image.info
    image = ImageOps.exif_transpose(image)
    if alpha:
        rgba = image.convert('RGBA')
        canvas = Image.new('RGBA', rgba.size, (255, 255, 255, 255))
        image = Image.alpha_composite(canvas, rgba).convert('RGB')
    else:
        image = image.convert('RGB')
    metadata = {'original_mode': original_mode, 'format': original_format,
                'alpha_composited': alpha, 'width': image.width, 'height': image.height}
    image.info.clear()  # Do not propagate EXIF into UI preview/cache.
    return image, metadata


class Letterbox:
    """Keep the entire image, with aspect ratio preserved; no lesion crop."""
    def __init__(self, size=224):
        self.size = size
    def __call__(self, image):
        resized = ImageOps.contain(image, (self.size, self.size), Image.Resampling.BICUBIC)
        canvas = Image.new('RGB', (self.size, self.size), tuple(round(v*255) for v in MEAN))
        canvas.paste(resized, ((self.size-resized.width)//2, (self.size-resized.height)//2))
        return canvas


def model_transform(training=False, size=224):
    pipeline = [Letterbox(size)]
    if training:
        # No blur/exposure/compression augmentations that change the quality task.
        pipeline.append(transforms.RandomHorizontalFlip(p=0.5))
    pipeline.extend([transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    return transforms.Compose(pipeline)


def preprocess_for_inference(image, size=224):
    return model_transform(False, size)(image)
