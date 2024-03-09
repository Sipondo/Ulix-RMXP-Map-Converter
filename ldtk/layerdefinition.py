from ldtk.ldtkjson import LayerDefinition as LayerDefinitionJson, TypeEnum
from ldtk.ldtkjson import LdtkJSON
from ldtk.tilesetdefinition import TilesetDefinition


class LayerDefinition():
    identifier: str
    grid_size: int
    default_tileset: str | None
    """Identifier of the tileset definition that'll be used as the layer default"""

    def __init__(self, identifier: str, grid_size = 16):
        self.identifier = identifier
        self.grid_size = grid_size
        self.default_tileset = None

    def to_ldtk(self, ldtk: LdtkJSON):
        layer_instance_json =  LayerDefinitionJson(
            type = "",
            auto_rule_groups = [],
            auto_source_layer_def_uid = None,
            auto_tileset_def_uid = None,
            auto_tiles_killed_by_other_layer_uid = None,
            biome_field_uid = None,
            can_select_when_inactive = True,
            display_opacity = 1.0,
            doc = None,
            excluded_tags = [],
            grid_size = 0,
            guide_grid_hei = 0,
            guide_grid_wid = 0,
            hide_fields_when_inactive = True,
            hide_in_list = False,
            identifier = "",
            inactive_opacity = 1.0,
            int_grid_values = [],
            int_grid_values_groups = [],
            parallax_factor_x = 0.0,
            parallax_factor_y = 0.0,
            parallax_scaling = True,
            px_offset_x = 0,
            px_offset_y = 0,
            render_in_world_view = True,
            required_tags = [],
            tile_pivot_x = 0.0,
            tile_pivot_y = 0.0,
            tileset_def_uid = None,
            layer_definition_type = TypeEnum.TILES, # I just need to pick something
            ui_color = None,
            uid = 0,
            ui_filter_tags = [],
            use_async_render = False
        )
        layer_instance_json.identifier = self.identifier
        layer_instance_json.grid_size = self.grid_size
        
        if self.default_tileset:
            tileset_definition_json = next((x for x in ldtk.defs.tilesets if x.identifier == self.default_tileset), None)
            layer_instance_json.tileset_def_uid = tileset_definition_json.uid

        return layer_instance_json
        