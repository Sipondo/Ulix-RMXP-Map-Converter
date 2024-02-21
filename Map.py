from RmxpData import MapData, MapInfo
import numpy as np


class Map():
    tileset_id = None

    def __init__(self, width_tiles: int, height_tiles: int):
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.width_px = self.width_tiles * 16
        self.height_px = self.height_tiles * 16
        
        self.data = np.zeros((self.height_tiles, self.width_tiles))

    @staticmethod
    def from_map_data(map_data: MapData):
        m = Map(map_data.width, map_data.height)
        m.tileset_id = map_data.tileset_id
        m.data = map_data.data.to_array()
        return m
