# from ldtk.layerinstance import LayerInstance
from random import randint
from ldtk.ldtkjson import Level as LevelJson, LayerInstance
from ldtk.ldtkjson import LdtkJSON

class Level():
    identifier: str
    px_hei: int
    px_wid: int
    # layer_instances: list[LayerInstance] = []
    grid_tiles: dict[str, LayerInstance] = {}
    """A dict of grid_tiles data. Layer instance identifier as key, grid_tiles as value"""

    def __init__(self, identifier: str, px_hei: int, px_wid: int):
        self.identifier = identifier
        self.px_hei = px_hei
        self.px_wid = px_wid

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
            
            level_json.layer_instances.append(layer_instance)

        return level_json