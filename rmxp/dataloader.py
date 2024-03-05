from pathlib import Path
from typing import Generator
from rmxp.map import Map
from rmxp.rmxpdata import *
from abc import ABC, abstractmethod
from rmxp.tileset import Tileset
from rubymarshal.ruby import readruby
from PIL.Image import Image

class DataLoader(ABC):
    # Framework specific attributes
    dir_tilesets: Path = None 

    def __init__(self, project_path: Path):
        self.src = project_path
        self.dir_data = self.src / "Data"

        map_infos: dict[int] = readruby(self.dir_data / "MapInfos.rxdata")
        self.map_infos = {id: MapInfo(data) for id, data in map_infos.items()}
        self.maps = {id: self.get_map_by_id(id, info) for id, info in self.map_infos.items()}
        
        # Some tilesets are None in the tileset List
        tilesets = [Tileset(t, self.get_tileset) for t in readruby(self.dir_data / "Tilesets.rxdata") if t is not None]
        self.tilesets = {t.id: t for t in tilesets}

    def get_map_by_filename(self, file_name: str, map_info: MapInfo):
        return self._get_map(self.dir_data / file_name, map_info)

    def get_map_by_id(self, id: int, map_info: MapInfo):
        return self._get_map(self.dir_data / f"Map{str(id).rjust(3, '0')}.rxdata", map_info)

    def _get_map(self, path: Path, map_info: MapInfo):
        map_data = MapData(readruby(path))
        return Map(map_data, map_info)

    @abstractmethod
    def get_tileset(self, tileset_name: str) -> Path:
        pass
    