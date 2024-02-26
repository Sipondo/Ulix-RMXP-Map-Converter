from ldtk.LdtkJson import BgPos, EntityInstance, FieldInstance, IntGridValueInstance, Level as LevelJson, NeighbourLevel, LevelBackgroundPosition, TileInstance
from ldtk.LdtkJson import TileInstance as TileInstanceJson
from ldtk.LdtkJson import LayerInstance as LayerInstanceJson

###
### We extend the classes like this to set default values for all arguments
###

def filter_locals(locals: dict):
    if "self" in locals: locals.pop("self")
    if "__class__" in locals: locals.pop("__class__")
    return locals

class LayerInstance(LayerInstanceJson):
    def __init__(
        self,
        c_hei: int = 0,
        c_wid: int = 0,
        grid_size: int = 0,
        identifier: str = "",
        opacity: float = 1.0,
        px_total_offset_x: int = 0,
        px_total_offset_y: int = 0,
        tileset_def_uid: int|None = None,
        tileset_rel_path: str|None = None,
        type: str = "",
        auto_layer_tiles: list[TileInstance] = None,
        entity_instances: list[EntityInstance] = None,
        grid_tiles: list[TileInstance] = None,
        iid: str = "",
        int_grid: list[IntGridValueInstance]|None = None, #This attribute is deprecated by LDtk
        int_grid_csv: list[int] = None,
        layer_def_uid: int = 0,
        level_id: int = 0,
        optional_rules: list[int] = None,
        override_tileset_uid: int|None = None,
        px_offset_x: int = 0,
        px_offset_y: int = 0,
        seed: int = 0,
        visible: bool = True,
    ):
        if auto_layer_tiles is None: auto_layer_tiles = []
        if entity_instances is None: entity_instances = []
        if grid_tiles is None: grid_tiles = []
        if int_grid is None: int_grid = []
        if int_grid_csv is None: int_grid_csv = []
        if optional_rules is None: optional_rules = []

        args = filter_locals(locals())
        super().__init__(**args)

class TileInstance(TileInstanceJson):
    def __init__(
        self,
        a: float = 1.0,
        d: list[int] = None,
        f: int = 0,
        px: list[int] = None,
        src: list[int] = None,
        t: int = 0,
    ):
        if d is None: d = []
        if px is None: px = []
        if src is None: src = []

        args = filter_locals(locals())
        super().__init__(**args)

class Level(LevelJson):
    def __init__(
        self,
        px_hei: int = 0,
        px_wid: int = 0,
        identifier: str = "",
        bg_color: str = "",
        bg_pivot_x: float = 0.0,
        bg_pivot_y: float = 0.0,
        bg_pos: LevelBackgroundPosition|None = None,
        bg_rel_path: str|None = None,
        external_rel_path: str|None = "",
        field_instances: list[FieldInstance] = None,
        iid: str = "",
        layer_instances: list[LayerInstance]|None = None,
        level_bg_color: str|None = None,
        level_bg_pos: BgPos|None = None,
        neighbours: list[NeighbourLevel] = None,
        smart_color: str = "",
        uid: int = 0,
        use_auto_identifier: bool = False,
        world_depth: int = 1,
        world_x: int = 0,
        world_y: int = 0,
    ):
        if neighbours is None: neighbours = []
        if layer_instances is None: layer_instances = []
        if field_instances is None: field_instances = []

        args = filter_locals(locals())
        super().__init__(**args)