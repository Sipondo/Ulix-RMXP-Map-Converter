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

        # {id_in_level: level_info}
        map_infos: dict = readruby(self.dir_data / "MapInfos.rxdata")
        self.map_infos = {k: MapInfo(v) for k, v in map_infos.items()}

        # {id_in_filename: level_data}
        self._maps = {}
        for file in (self.dir_data).glob("Map???.rxdata"):
            id = int(file.name.split("p")[1][:3])
            self._maps[id] = self.get_map_by_filename(file.name)

    def iter_maps(self) -> Generator[tuple[int, Map], None, None]:
        for k, v in self._maps.items():
            yield k, v

    def get_map_by_filename(self, file_name: str):
        return self._get_map(self.dir_data / file_name)

    def get_map_by_id(self, id: int):
        return self._get_map(self.dir_data / f"Map{str(id).rjust(3, '0')}.rxdata")

    def _get_map(self, path: Path):
        map_data = MapData(readruby(path))
        return Map.from_map_data(map_data)
