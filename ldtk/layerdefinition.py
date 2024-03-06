from ldtk.ldtkjson import LayerDefinition as LayerDefinitionJson, TypeEnum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ldtk.world import World


class LayerDefinition():
    identifier: str
    grid_size: int

    def __init__(self, identifier: str, grid_size = 16):
        self.identifier = identifier
        self.grid_size = grid_size

    def to_ldtk(self, world: 'World'):
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

        return layer_instance_json
        