from ldtk.LdtkJson import Level as LevelJson

###
### We extend the classes like this to set default values for all arguments
###

def filter_locals(locals: dict):
    locals.pop("self")
    locals.pop("__class__")
    return locals

class Level(LevelJson):
    def __init__(
        self,
        px_hei=0,
        px_wid=0,
        identifier="",
        bg_color="",
        bg_pivot_x=0.0,
        bg_pivot_y=0.0,
        bg_pos=None,
        bg_rel_path=None,
        external_rel_path="",
        field_instances=[],
        iid="",
        layer_instances=None,
        level_bg_color=None,
        level_bg_pos=None,
        neighbours=[],
        smart_color="",
        uid=0,
        use_auto_identifier=False,
        world_depth=1,
        world_x=0,
        world_y=0,
    ):
        args = filter_locals(locals())
        super().__init__(**args)