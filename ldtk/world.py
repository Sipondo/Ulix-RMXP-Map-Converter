import json
import os
from pathlib import Path
from ldtk.ldtkjson import Definitions, LdtkJSON, World as WorldJson, ldtk_json_to_dict, IdentifierStyle, ImageExportMode
from ldtk.ldtkjson import Level as LevelJson


class World():
    __next_uid = 10
    levels: list['Level'] = []
    
    @property
    def next_uid(self):
        uid = self.__next_uid
        self.__next_uid += 1
        return uid

    def add_level(self, level: 'Level'):
        if not isinstance(level, Level):
              level = Level(level)
        self.levels.append(level)

    def to_ldtk(self, path: Path):
        levels: list[LevelJson] = []
        for level in self.levels:
            level_json = level.to_ldtk()
            level_json.uid = self.next_uid
            levels.append(level_json)

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
        # Set enum data
        ldtk_json.defs = Definitions(
            entities=[],
            enums=[],
            external_enums=[],
            layers=[],
            level_fields=[],
            tilesets=[]
        )
        
        # Set data from the project
        ldtk_json.levels = levels
        
        os.makedirs(path, exist_ok=True)
        with open(path / "world.ldtk", "w", encoding="utf-8") as outfile:
            json.dump(ldtk_json_to_dict(ldtk_json), outfile, indent=4)


class Level():
    identifier: str
    px_hei: int
    px_wid: int

    def __init__(self, identifier: str, px_hei: int, px_wid: int):
        self.identifier = identifier
        self.px_hei = px_hei
        self.px_wid = px_wid

    def to_ldtk(self):
        level_json =  LevelJson(
            bg_color="",
            bg_pos=None,
            neighbours=[],
            smart_color="",
            level_bg_color=None,
            bg_pivot_x=0.0,
            bg_pivot_y=0.0,
            level_bg_pos=None,
            bg_rel_path=None,
            external_rel_path=None,
            field_instances=[],
            identifier="",
            iid="",
            layer_instances=None,
            px_hei=0,
            px_wid=0,
            uid=0,
            use_auto_identifier=False,
            world_depth=0,
            world_x=0,
            world_y=0
        )
        level_json.identifier = self.identifier
        level_json.px_hei = self.px_hei
        level_json.px_wid = self.px_wid

        return level_json