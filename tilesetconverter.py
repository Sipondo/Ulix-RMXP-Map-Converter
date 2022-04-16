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
    im.resize((width, height))
    im.save(f"{ROOT}/{source_img}", f"{im.format}")
