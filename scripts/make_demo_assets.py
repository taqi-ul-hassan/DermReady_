"""Create original synthetic capture targets, never patient or dataset photographs."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from PIL import Image, ImageDraw
from src.perturbations import degrade


def main():
    folder=Path('assets/demo');folder.mkdir(parents=True,exist_ok=True)
    image=Image.new('RGB',(640,480),(178,194,203));draw=ImageDraw.Draw(image)
    for x in range(40,620,40):draw.line((x,40,x,440),fill=(65,90,115),width=3)
    for y in range(40,460,40):draw.line((40,y,600,y),fill=(65,90,115),width=3)
    draw.ellipse((220,140,420,340),fill=(214,136,58),outline=(35,50,70),width=6)
    draw.rectangle((270,190,370,290),fill=(245,241,225))
    draw.text((42,15),'SYNTHETIC CAPTURE TARGET - NOT A PATIENT IMAGE',fill=(20,35,50))
    for filename,condition in [('synthetic_original.png','original'),('synthetic_blur.png','blur_5'),('synthetic_dark.png','dark_035')]:
        degrade(image,condition).save(folder/filename)
    tile=np.random.default_rng(42).integers(20,230,(20,20,3),dtype=np.uint8)
    Image.fromarray(np.tile(tile,(20,20,1))).save(folder/'synthetic_noise.png')
    print('Created four synthetic targets under assets/demo/')

if __name__=='__main__':main()
