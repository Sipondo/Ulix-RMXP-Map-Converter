from pathlib import Path
from ldtk.Ldtk import World
from ldtk.LdtkJson import TilesetDefinition
from rubymarshal.classes import RubyObject, RubyString
from rubymarshal.rmxptypes import Table
import os
from PIL.Image import *

class Tileset():
    def __init__(self, ruby_object: RubyObject, get_image_fn):
        self._get_image_fn = get_image_fn

        self.ruby_object = ruby_object
        self.class_name: str = ruby_object.ruby_class_name

        att = ruby_object.attributes
        self.panorama_hue: int = att["@panorama_hue"]
        self.terrain_tags: Table = att["@terrain_tags"]
        self.name: str = str(att["@name"])
        self.fog_sy: int = att["@fog_sy"]
        self.fog_opacity: int = att["@fog_opacity"]
        self.panorama_name: str = str(att["@panorama_name"])
        self.priorities: Table = att["@priorities"]
        self.fog_sx: int = att["@fog_sx"]
        self.fog_hue: int = att["@fog_hue"]
        self.autotile_names: list[RubyString] = att["@autotile_names"]
        self.passages: Table = att["@passages"]
        self.fog_zoom: int = att["@fog_zoom"]
        self.fog_name: str = str(att["@fog_name"])
        self.id: int = att["@id"]
        self.tileset_name: str = str(att["@tileset_name"]) # This is the actual file name
        self.battleback_name: str = str(att["@battleback_name"])
        self.fog_blend_type: int = att["@fog_blend_type"]


    @property
    def image_path(self):
        return self._get_image_fn(self.tileset_name)

    def _create_filename(self, filename: str):
        return filename.split("\\")[-1].replace(" ", "_").lower()

    # We need to rely on the loader outside to figure out where the actual image is
    def add_to_ldtk(self, save_to_path: Path, world: World):
        img = open(self.image_path)
        converted_filename = self._create_filename(str(self.image_path))
        converted_path = save_to_path / converted_filename
        converted_img = self._convert_tileset(img, converted_path)

        # eg. world/assets/sometileset.png -> assets/sometileset.png
        rel_path = str(converted_path.relative_to(converted_path.parents[2]))
        tileset_definition = world.add_tileset_definition(
            identifier = self.name,
            rel_path = rel_path,
            px_hei = converted_img.height,
            px_wid = converted_img.width,
            tile_grid_size=16,
        )
        return tileset_definition

    # For normal tilesets, we basically only need to shrink the tileset by 2x
    def _convert_tileset(self, image: Image, save_to: Path) -> Image:
        width, height = (i // 2 for i in image.size)
        out = image.resize((width, height))
        
        if out.size[1] > 8192:
        # while out.size[1] > 2048:
            out = self._split_and_merge(out)
        out.save(save_to)
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
