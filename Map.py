from RmxpData import MapData, MapInfo
import numpy as np

from ldtk.Classes import Level


class Map():
    tileset_id = None

    def __init__(self, map_data: MapData, map_info: MapInfo):
        # Info from map_info
        self.name = str(map_info.name)
        self.scroll_x = map_info.scroll_x
        self.scroll_y = map_info.scroll_y
        self.expanded = map_info.expanded
        self.order = map_info.order
        self.parent_id = map_info.parent_id
        
        # Info from map_data
        self.data = map_data.data
        self.height = map_data.height
        self.width = map_data.width
        self.tileset_id = map_data.tileset_id
        self.events = map_data.events
        self.encounter_step = map_data.encounter_step
        self.encounter_list = map_data.encounter_list
        self.bgm = map_data.bgm
        self.bgs = map_data.bgs
        self.autoplay_bgm = map_data.autoplay_bgm
        self.autoplay_bgs = map_data.autoplay_bgs

    def to_level(self):
        level = Level(
            identifier=self.name,

            # Convert size from tiles to pixels
            px_hei=self.height * 16,
            px_wid=self.width * 16,
        )
        return level
