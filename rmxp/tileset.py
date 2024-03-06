from rubymarshal.classes import RubyObject, RubyString
from rubymarshal.rmxptypes import Table
from PIL.Image import *
from ldtk.tilesetdefinition import TilesetDefinition

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
        level = TilesetDefinition(
            identifier=self.name,
            image_path=self._get_image_fn(self.tileset_name)
        )
        return level