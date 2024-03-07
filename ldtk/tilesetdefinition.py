from pathlib import Path
from ldtk.ldtkjson import TilesetDefinition as TilesetDefinitionJson
from PIL.Image import *
from ldtk.ldtkjson import LdtkJSON


class TilesetDefinition():

    def __init__(self, identifier: str, image_path: Path):
        self.identifier = identifier
        self.image_path = image_path
        self.image = open(image_path)

    @property
    def filename(self):
        return f"{self.identifier.split("\\")[-1].replace(" ", "_").lower()}.{self.image.format}"

    # # For normal tilesets, we basically only need to shrink the tileset by 2x
    def convert_tileset(self, image: Image) -> Image:
        width, height = (i // 2 for i in image.size)
        out = image.resize((width, height))
        
        # LDtk can't load tilesets higher than ~10000 pixels, so cut it in two
        # If one cut isn't enough, i'll say its the tilesets fault
        if out.size[1] > 8192:
            out = self._split_and_merge(out)
        return out

    def _split_and_merge(self, image: Image):
        # Get the width and height of the image
        width, height = image.size

        # Calculate the center of the image
        center = height // 2

        # Crop the top and bottom halves of the image
        top_half = image.crop((0, 0, width, center))
        bottom_half = image.crop((0, center, width, height))

        # Create a new image with double the width and the same height
        new_width = width * 2
        new_image = new('RGBA', (new_width, center))

        # Paste the top and bottom halves onto the new image side by side
        new_image.paste(top_half, (0, 0))
        new_image.paste(bottom_half, (width, 0))
        return new_image

    def to_ldtk(self, ldtk: LdtkJSON):
        image = self.convert_tileset(self.image)

        tileset_definition = TilesetDefinitionJson(
            c_hei = 0,
            c_wid = 0,
            cached_pixel_data = None,
            custom_data = [],
            embed_atlas = None,
            enum_tags = [],
            identifier = "",
            padding = 0,
            px_hei = 0,
            px_wid = 0,
            rel_path = None,
            saved_selections = [],
            spacing = 0,
            tags = [],
            tags_source_enum_uid = None,
            tile_grid_size = 0,
            uid = 0
        )
        width, height = image.size

        tileset_definition.identifier = self.identifier
        tileset_definition.px_wid = width
        tileset_definition.px_hei = height
        tileset_definition.tile_grid_size = 16

        return tileset_definition