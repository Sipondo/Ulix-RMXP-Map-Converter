from pathlib import Path
from ldtk.world import World
from ldtk.ldtkjson import TilesetDefinition
from rubymarshal.classes import RubyObject, RubyString
from rubymarshal.rmxptypes import Table
import os
from PIL.Image import *
from ldtk.tileset import Tileset as TilesetLdtk

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

    def to_ldtk(self):
        level = TilesetLdtk(
            identifier=self.name,
            image_path=self._get_image_fn(self.tileset_name)
        )
        return level

    # We need to rely on the loader outside to figure out where the actual image is
    # def add_to_ldtk(self, save_to_path: Path, world: World):
    #     img = open(self.image_path)
    #     converted_filename = self._create_filename(str(self.image_path))
    #     converted_path = save_to_path / converted_filename
    #     converted_img = self._convert_tileset(img, converted_path)

    #     # eg. world/assets/sometileset.png -> assets/sometileset.png
    #     rel_path = str(converted_path.relative_to(converted_path.parents[2]))
    #     tileset_definition = world.add_tileset_definition(
    #         identifier = self.name,
    #         rel_path = rel_path,
    #         px_hei = converted_img.height,
    #         px_wid = converted_img.width,
    #         tile_grid_size=16,
    #     )
    #     return tileset_definition