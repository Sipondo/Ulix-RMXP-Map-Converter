from PIL import Image
from pathlib import Path

ROOT = Path("resources/imported/graphics/tilesets")
ROOT.mkdir(parents=True, exist_ok=True)


def shrink_tileset(source_img):
    """
    @source_img: Source image to shrink 2x
    @returns: Shrinked image
    """
    im = Image.open(source_img)
    width, height = (i // 2 for i in im.size)
    out = im.resize((width, height))
    filename = im.filename.split("\\")[-1]
    out.save(f"{ROOT}/{filename}", f"{im.format}")


def get_image_size(source_img):
    im = Image.open(source_img)
    return (im.width, im.height)
