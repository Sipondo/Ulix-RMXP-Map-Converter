import json
import os
from pathlib import Path
from ldtk.layerdefinition import LayerDefinition
from ldtk.ldtkjson import Definitions, LdtkJSON, World as WorldJson, ldtk_json_to_dict, IdentifierStyle, ImageExportMode
from ldtk.level import Level
from ldtk.tilesetdefinition import TilesetDefinition
from ldtk.ldtkjson import Level as LevelJson
from ldtk.ldtkjson import LayerDefinition as LayerDefinitionJson


class World():
    __next_uid = 10
    levels: list[Level] = []
    tilesets: list[TilesetDefinition] = []
    layers: list[LayerDefinition] = []
    
    @property
    def next_uid(self):
        uid = self.__next_uid
        self.__next_uid += 1
        return uid

    def add_level(self, level: Level):
        if not isinstance(level, Level):
              level = Level(level)
        self.levels.append(level)

    def add_tileset(self, tileset: TilesetDefinition):
        if not isinstance(tileset, TilesetDefinition):
              tileset = TilesetDefinition(tileset)
        self.tilesets.append(tileset)

    def add_layer(self, layer: LayerDefinition):
        if not isinstance(layer, LayerDefinition):
              layer = LayerDefinition(layer)
        self.layers.append(layer)

    def to_ldtk(self, path: Path):
        assets_dir = path / "assets"
        tileset_dir = assets_dir / "tilesets"
        os.makedirs(tileset_dir, exist_ok=True)

        # Init the world with default values
        ldtk_json = LdtkJSON(
            forced_refs=None,
            app_build_id=1.0,
            backup_limit=10,
            backup_on_save=True,
            backup_rel_path="backups",
            bg_color="",
            custom_commands=[],
            default_entity_height=1,
            default_entity_width=1,
            default_grid_size=16,
            default_level_bg_color="",
            default_level_height=25,
            default_level_width=25,
            default_pivot_x=0.0,
            default_pivot_y=0.0,
            defs=None, # Remember to set this after
            dummy_world_iid="",
            export_level_bg=True,
            export_png=None,
            export_tiled=False,
            external_levels=False,
            flags=[],
            identifier_style=IdentifierStyle.FREE,
            iid="",
            image_export_mode=ImageExportMode.ONE_IMAGE_PER_LEVEL,
            json_version="1.5.3",
            level_name_pattern="",
            levels=[],
            minify_json=False,
            next_uid=1,
            png_file_pattern=None,
            simplified_export=False,
            toc=[],
            tutorial_desc=None,
            world_grid_height=None,
            world_grid_width=None,
            world_layout=None,
            worlds=[]
        )
        ldtk_json.defs = Definitions(
            entities=[],
            enums=[],
            external_enums=[],
            layers=[],
            level_fields=[],
            tilesets=[]
        )

        for layer_definition in self.layers:
            layer_definition_json = layer_definition.to_ldtk(ldtk_json)
            layer_definition_json.uid = self.next_uid
            ldtk_json.defs.layers.append(layer_definition_json)
        
        for tileset in self.tilesets:
            tileset_path = tileset_dir / tileset.filename
            tileset.convert_tileset(tileset.image).save(tileset_path)

            tileset_json = tileset.to_ldtk(ldtk_json)
            tileset_json.rel_path = str(tileset_path.absolute())
            tileset_json.uid = self.next_uid
            ldtk_json.defs.tilesets.append(tileset_json)

        for level in self.levels:
            level_json = level.to_ldtk(ldtk_json)
            level_json.uid = self.next_uid
            for layer_instance in level_json.layer_instances:
                layer_instance.level_id = level_json.uid
            ldtk_json.levels.append(level_json)
            
        with open(path / "world.ldtk", "w", encoding="utf-8") as outfile:
            json.dump(ldtk_json_to_dict(ldtk_json), outfile, indent=4)

