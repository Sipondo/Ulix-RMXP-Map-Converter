from pathlib import Path
from typing import Generator
from Map import Map
from RmxpData import *
from abc import ABC, abstractmethod
from rubymarshal.ruby import readruby

class DataLoader(ABC):
    def __init__(self, project_path: Path):
        self.src = project_path
        self.dir_data = self.src / "Data"

        map_infos: dict[int] = readruby(self.dir_data / "MapInfos.rxdata")
        self.map_infos = {id: MapInfo(data) for id, data in map_infos.items()}
        self.maps = {id: self.get_map_by_id(id, info) for id, info in self.map_infos.items()}

    def get_map_by_filename(self, file_name: str, map_info: MapInfo):
        return self._get_map(self.dir_data / file_name, map_info)

    def get_map_by_id(self, id: int, map_info: MapInfo):
        return self._get_map(self.dir_data / f"Map{str(id).rjust(3, '0')}.rxdata", map_info)

    def _get_map(self, path: Path, map_info: MapInfo):
        map_data = MapData(readruby(path))
        return Map(map_data, map_info)
