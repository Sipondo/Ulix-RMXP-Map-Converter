from ldtk.world import Level
from rmxp.rmxpdata import MapData, MapInfo
from random import randint
import numpy as np


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
        self.data = map_data.data.to_array()
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
        
    @property
    def width_px(self):
        return self.width * 16

    @property
    def height_px(self):
        return self.height * 16

    def to_level(self):
        level = Level(
            identifier=self.name,
            px_hei=self.height_px,
            px_wid=self.width_px
        )
        return level

    # def _coord_to_int(self, coords, width):
    #     return coords[0] + coords[1] * width

    # def _t_to_src(self, value):
    #     x = value % 8 * 16
    #     y = value // 8 * 16
    #     return [x, y]

    # def _create_tile_instance(self, x: int, y: int, t: int, tileset: TilesetDefinition) -> TileInstance:
    #     # Adjust t in case the tileset needed to be cut in two
    #     if tileset.px_wid > 128:
    #         t = t + t // 8 * 8 
    #         if t > tileset.px_hei:
    #             t = t - tileset.px_hei + 8

    #     return TileInstance(
    #         # src is set by LDtk on project save. t is enough for tile data
    #         px = [self.width_px, self.height_px],
    #         t = t,
    #         d = [self._coord_to_int((x, y), self.width)]
    #     )

    # def _data_to_grid_tiles(self, tileset: TilesetDefinition = None) -> list[list[TileInstance]]:
    #     grid_tiles = []
    #     for (layer) in range(3):
    #         layer_data = []
    #         for x in range(self.width):
    #             for y in range(self.height):
    #                 t = int(self.data[layer, y, x]) 
    #                 if t == 0:
    #                    continue
    #                 # Adjust t to account for 384 RMXP autotiles and 8 empty ldtk tiles
    #                 # Add +8 if importing legacy tilesets (empty line on top)
    #                 t = t - 384

    #                 # Negative means an autotile
    #                 if t < 0:
    #                     # TODO: Implement autotiles
    #                     continue
    #                 else:
    #                     tile_instance = self._create_tile_instance(x, y, t, tileset)
    #                     layer_data.append(tile_instance)
    #         grid_tiles.append(layer_data)
    #     return grid_tiles

    # def add_to_ldtk(self, world: World, layers: list[LayerDefinition], tileset: TilesetDefinition = None):
    #     if len(layers) != 3:
    #         raise Exception("Please provide 3 LayerDefinitions as layers")

    #     level = world.add_level(
    #         identifier=self.name,
    #         px_hei=self.height_px,
    #         px_wid=self.width_px,
    #     )

    #     grid_tiles = self._data_to_grid_tiles(tileset)
    #     for i, layer in enumerate(layers):
    #         layer_instance = level.add_layer_instance(
    #             identifier = layer.identifier,
    #             layer_def_uid=layer.uid,
    #             override_tileset_uid=tileset.uid if tileset else None,
    #             seed=randint(1, 999999), # This range is arbitrarily chosen
    #         )
    #         if grid_tiles:
    #             layer_instance.grid_tiles = grid_tiles[i]
    #     return level
