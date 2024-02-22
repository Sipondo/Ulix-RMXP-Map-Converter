import json
from Map import Map
from ldtk.Classes import Level
from pathlib import Path
import os
from ldtk.LdtkJson import ldtk_json_from_dict, ldtk_json_to_dict


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
                # Create the separate level files, then clear the "heavy" data from the main file
                with open(path / level.external_rel_path, "w", encoding="utf-8") as outfile:
                    json.dump(Level.to_dict(level), outfile, indent=4)
                level.layer_instances = []

        with open(world_file_path, "w", encoding="utf-8") as outfile:
            json.dump(ldtk_json_to_dict(self._json), outfile, indent=4)

    def add_level(self, level: Level):
        level.uid = self._next_uid
        if self._json.external_levels:
            filename = self._create_level_filename(level.identifier)
            level.external_rel_path = f"world/{filename}"
        self._json.levels.append(level)
