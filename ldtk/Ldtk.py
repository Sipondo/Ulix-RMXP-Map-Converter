import json
from typing import Any
from pathlib import Path
import os
from ldtk.LdtkJson import BgPos, EmbedAtlas, EntityInstance, EnumTagValue, FieldInstance, IntGridValueInstance, LevelBackgroundPosition, NeighbourLevel, ldtk_json_from_dict, ldtk_json_to_dict, TileCustomMetadata
from ldtk.LdtkJson import Level as LevelJson
from ldtk.LdtkJson import  LayerInstance as LayerInstanceJson
from ldtk.LdtkJson import TileInstance as TileInstanceJson
from ldtk.LdtkJson import TilesetDefinition as TilesetDefinitionJson


def filter_locals(locals: dict):
    if "self" in locals: locals.pop("self")
    if "__class__" in locals: locals.pop("__class__")
    return locals

class World():
    def __init__(self, world_file: Path):
        self.world_file = world_file

        with open(world_file, "r", encoding="utf-8") as infile:
            data = dict(json.load(infile))
            self._json = ldtk_json_from_dict(data)

    def add_level(
        self,
        uid: int = 0, # This is set automatically
        px_hei: int = 0,
        px_wid: int = 0,
        identifier: str = "",
        bg_color: str = "",
        bg_pivot_x: float = 0.0,
        bg_pivot_y: float = 0.0,
        bg_pos: LevelBackgroundPosition|None = None,
        bg_rel_path: str|None = None,
        external_rel_path: str|None = "",
        field_instances: list[FieldInstance] = None,
        iid: str = "",
        layer_instances: list['LayerInstance']|None = None,
        level_bg_color: str|None = None,
        level_bg_pos: BgPos|None = None,
        neighbours: list[NeighbourLevel] = None,
        smart_color: str = "",
        use_auto_identifier: bool = False,
        world_depth: int = 1,
        world_x: int = 0,
        world_y: int = 0,
    ):
        if neighbours is None: neighbours = []
        if layer_instances is None: layer_instances = []
        if field_instances is None: field_instances = []

        level = Level(**filter_locals(locals()))
        level.uid = self._next_uid

        if self._json.external_levels:
            filename = self._create_level_filename(level.identifier)
            level.external_rel_path = f"world/{filename}"

        level._world = self
        self._json.levels.append(level)
        return level

    def add_tileset_definition(
        self,
        c_hei: int = 0,
        c_wid: int = 0,
        cached_pixel_data: dict[str, Any] | None = None,
        custom_data: list[TileCustomMetadata] = None,
        embed_atlas: EmbedAtlas | None = None,
        enum_tags: list[EnumTagValue] = None,
        identifier: str = "",
        padding: int = 0,
        px_hei: int = 0,
        px_wid: int = 0,
        rel_path: str | None = None,
        saved_selections: list[dict[str, Any]] = None,
        spacing: int = 0,
        tags: list[str] = None,
        tags_source_enum_uid: int | None = None,
        tile_grid_size: int = 0,
        uid: int = 0,
    ):
        if tags is None: tags = []
        if saved_selections is None: saved_selections = []
        if enum_tags is None: enum_tags = []
        if custom_data is None: custom_data = []
        if cached_pixel_data is None: cached_pixel_data = {}
            
        
        tileset_definition = TilesetDefinition(**filter_locals(locals()))
        tileset_definition.uid = self._next_uid

        tileset_definition._world = self
        self._json.defs.tilesets.append(tileset_definition)
        return tileset_definition
            
    @property
    def _next_uid(self):
        uid = self._json.next_uid
        self._json.next_uid += 1
        return uid
        
    def _create_level_filename(self, level_name: str) -> str:
        i = 0
        if self._json.levels:
            file_index = lambda l : int(l.external_rel_path.split("/")[1].split("-")[0])
            i = max([file_index(l) for l in self._json.levels]) + 1
        level_name = level_name.replace(" ", "_")
        filename =  f"{i:0>4}-{level_name}.ldtkl"
        return filename

    def save(self, path:Path|None=None):
        world_file_path = path if path else self.world_file

        # Cleanup and fix level data
        for level in self._json.levels:
            for li in level.layer_instances:
                li.level_id = level.uid

        if self._json.external_levels:
            if not path:
                raise Exception("If saving with external levels enabled, please provide a folder to save to")

            world_file_path = path / "world.ldtk"
            world_dir = path / "world"
            os.makedirs(path, exist_ok=True)
            os.makedirs(world_dir, exist_ok=True)

            levels_done = 0
            total_levels = len(self._json.levels)
            for level in self._json.levels:
                # Create the separate level files, then clear the "heavy" data from the main file
                with open(path / level.external_rel_path, "w", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(Level.to_dict(level)))
                level.layer_instances = []

                levels_done += 1
                print(f"{levels_done}/{total_levels} written to file")

        with open(world_file_path, "w", encoding="utf-8") as outfile:
            json.dump(ldtk_json_to_dict(self._json), outfile, indent=4)

class Level(LevelJson):
    _world: World

    def add_layer_instance(
        self,
        level_id: int = 0, # This is handled automatically
        c_hei: int = 0,
        c_wid: int = 0,
        grid_size: int = 0,
        identifier: str = "",
        opacity: float = 1.0,
        px_total_offset_x: int = 0,
        px_total_offset_y: int = 0,
        tileset_def_uid: int|None = None,
        tileset_rel_path: str|None = None,
        type: str = "",
        auto_layer_tiles: list['TileInstance'] = None,
        entity_instances: list[EntityInstance] = None,
        grid_tiles: list['TileInstance'] = None,
        iid: str = "",
        int_grid: list[IntGridValueInstance]|None = None, # This attribute is deprecated by LDtk
        int_grid_csv: list[int] = None,
        layer_def_uid: int = 0,
        optional_rules: list[int] = None,
        override_tileset_uid: int|None = None,
        px_offset_x: int = 0,
        px_offset_y: int = 0,
        seed: int = 0,
        visible: bool = True,
    ):
        if auto_layer_tiles is None: auto_layer_tiles = []
        if entity_instances is None: entity_instances = []
        if grid_tiles is None: grid_tiles = []
        if int_grid is None: int_grid = []
        if int_grid_csv is None: int_grid_csv = []
        if optional_rules is None: optional_rules = []

        layer_instance = LayerInstance(**filter_locals(locals()))
        layer_instance.level_id = self.uid
        
        layer_instance._level = self
        self.layer_instances.append(layer_instance)
        return layer_instance

class LayerInstance(LayerInstanceJson):
    _level: Level

class TilesetDefinition(TilesetDefinitionJson):
    _world: World


#
# LDtk classes not dependant on the world
#
class TileInstance(TileInstanceJson):
    def __init__(
        self,
        a: float = 1.0,
        d: list[int] = None,
        f: int = 0,
        px: list[int] = None,
        src: list[int] = None,
        t: int = 0,
    ):
        if d is None: d = []
        if px is None: px = []
        if src is None: src = []

        args = filter_locals(locals())
        super().__init__(**args)
