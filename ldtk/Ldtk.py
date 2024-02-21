import json
from Map import Map
from ldtk.LdtkJson import *
from pathlib import Path
import os
import shutil


class Ldtk():
    def __init__(self, world_file: Path):
        self.world_file = world_file

        with open(world_file, "r", encoding="utf-8") as infile:
            data = dict(json.load(infile))
            self._json = ldtk_json_from_dict(data)
            

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
        return f"{i:0>4}-{level_name}.ldtkl"

    def save(self, path:Path|None=None):
        world_file_path = path if path else self.world_file
        if self._json.external_levels:
            if not path:
                raise Exception("If saving with external levels enabled, please provide a folder to save to")

            world_file_path = path / "world.ldtk"
            world_dir = path / "world"
            os.makedirs(path, exist_ok=True)
            os.makedirs(world_dir, exist_ok=True)

            for level in self._json.levels:
                with open(path / level.external_rel_path, "w", encoding="utf-8") as outfile:
                    json.dump(Level.to_dict(level), outfile, indent=4)

        with open(world_file_path, "w", encoding="utf-8") as outfile:
            json.dump(ldtk_json_to_dict(self._json), outfile, indent=4)

    def add_level(self, _map: Map, name: str):
        level = Level(
            px_hei=_map.height_px,
            px_wid=_map.height_px,
            identifier=name,
            bg_color="",
            bg_pivot_x=0.0,
            bg_pivot_y=0.0,
            bg_pos=None,
            bg_rel_path=None,
            external_rel_path="",
            field_instances=[],
            iid="",
            layer_instances=None,
            level_bg_color=None,
            level_bg_pos=None,
            neighbours=[],
            smart_color="",
            uid=self._next_uid,
            use_auto_identifier=False,
            world_depth=1,
            world_x=0,
            world_y=0,
        )
        
        if self._json.external_levels:
            filename = self._create_level_filename(level.identifier)
            level.external_rel_path = f"world/{filename}"
        self._json.levels.append(level)