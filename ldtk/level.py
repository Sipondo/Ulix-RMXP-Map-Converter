from ldtk.ldtkjson import Level as LevelJson

class Level():
    identifier: str
    px_hei: int
    px_wid: int

    def __init__(self, identifier: str, px_hei: int, px_wid: int):
        self.identifier = identifier
        self.px_hei = px_hei
        self.px_wid = px_wid

    def to_ldtk(self):
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
            layer_instances=None,
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

        return level_json