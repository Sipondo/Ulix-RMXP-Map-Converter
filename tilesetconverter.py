from PIL import Image
from pathlib import Path

ROOT = Path("resources/imported/graphics/tilesets")
ROOT.mkdir(parents=True, exist_ok=True)


def shrink_tileset(source_img):
    """
    @source_img: Source image to shrink 2x
    @returns: Shrinked image
    """
    im = Image.open(Path(source_img))
    width, height = (i // 2 for i in im.size)
    out = im.resize((width, height))
    filename = im.filename.split("\\")[-1].replace(" ", "_").lower()
    out.save(f"{ROOT}/{filename}", f"{im.format}")
    return filename


def get_image_size(source_img):
    im = Image.open(Path(f"{ROOT}/{source_img}"))
    return (im.width, im.height)
