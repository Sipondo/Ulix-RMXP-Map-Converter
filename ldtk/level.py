# from ldtk.layerinstance import LayerInstance
from random import randint
from ldtk.ldtkjson import Level as LevelJson, LayerInstance, TileInstance
from ldtk.ldtkjson import LdtkJSON
import numpy as np

class Level():
    identifier: str
    px_hei: int
    px_wid: int
    grid_tiles: dict[str, np.ndarray]
    """A dict of grid_tiles data. Layer identifier as key, tile id array as value"""
    tileset: str
    """Identifier of the tileset definition that'll be used"""

    def __init__(self, identifier: str, px_hei: int, px_wid: int):
        self.identifier = identifier
        self.px_hei = px_hei
        self.px_wid = px_wid
        self.grid_tiles = {}
        self.tileset = ""

    @property
    def tiles_hei(self):
        return self.px_hei // 16

    @property
    def tiles_wid(self):
        return self.px_wid // 16

    def add_grid_tiles(self, identifier: str):
        a = np.empty((self.tiles_hei, self.tiles_wid))
        a.fill(-1)
        self.grid_tiles[identifier] = a
        return a

    def _coord_to_int(self, coords: tuple[int, int], width: int):
        return coords[0] + coords[1] * width

    def _array_to_tile_instances(self, array: np.ndarray):
        tile_instances: list[TileInstance] = []
        height, width = array.shape
        for y in range(height):
            for x in range(width):
                t = int(array[y, x])
                if t == -1:
                    continue
                tile_instance = TileInstance(
                    # t and d and the only values that are needed to load the map
                    t = t,
                    d = [self._coord_to_int((x, y), width)],
                    a = 1.0,
                    f = 0,
                    px = [],
                    src = [],
                )
                tile_instances.append(tile_instance)
        return tile_instances
        
        
    def to_ldtk(self, ldtk: LdtkJSON):
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
            layer_instances=[],
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
        
        for layer_definition in ldtk.defs.layers:
            layer_instance = LayerInstance(
                level_id = 0,
                c_hei = 0,
                c_wid = 0,
                grid_size = 0,
                identifier = "",
                opacity = 1.0,
                px_total_offset_x = 0,
                px_total_offset_y = 0,
                tileset_def_uid = None,
                tileset_rel_path = None,
                type = "",
                auto_layer_tiles = [],
                entity_instances = [],
                grid_tiles = [],
                iid = "",
                int_grid = [], # This attribute is deprecated by LDtk
                int_grid_csv = [],
                layer_def_uid = 0,
                optional_rules = [],
                override_tileset_uid = None,
                px_offset_x = 0,
                px_offset_y = 0,
                seed = 0,
                visible = True,
            )
            layer_instance.identifier = layer_definition.identifier
            layer_instance.layer_def_uid = layer_definition.uid
            layer_instance.seed = randint(1, 999999) # This range is arbitrarily chosen
            layer_instance.grid_tiles = self._array_to_tile_instances(self.grid_tiles[layer_definition.identifier])
            
            if self.tileset:
                tileset_definition_json = next((x for x in ldtk.defs.tilesets if x.identifier == self.tileset), None)
                layer_instance.override_tileset_uid = tileset_definition_json.uid if tileset_definition_json else None
            
            level_json.layer_instances.append(layer_instance)

        return level_json