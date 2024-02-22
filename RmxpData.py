from rubymarshal.classes import RubyObject, RubyString
from rubymarshal.rmxptypes import Table

class MapInfo():
    def __init__(self, ruby_object: RubyObject):
        self.ruby_object = ruby_object
        self.class_name: str = ruby_object.ruby_class_name
        att = ruby_object.attributes
        self.name: RubyString = att["@name"]
        self.scroll_x: int = att["@scroll_x"]
        self.scroll_y: int = att["@scroll_y"]
        self.expanded: bool = att["@expanded"]
        self.order: int = att["@order"]
        self.parent_id: int = att["@parent_id"]

class BGX():
    def __init__(self, ruby_object: RubyObject):
        self.ruby_object = ruby_object
        self.class_name: str = ruby_object.ruby_class_name
        att = ruby_object.attributes
        self.name: RubyString = att["@name"]
        self.volume: int = att["@volume"]
        self.pitch: int = att["@pitch"]

class MapData():
    def __init__(self, ruby_object: RubyObject):
        self.ruby_object = ruby_object
        self.class_name: str = ruby_object.ruby_class_name
        att = ruby_object.attributes
        self.data: Table = att["@data"]
        self.height: int = att["@height"]
        self.width: int = att["@width"]
        self.tileset_id: int = att["@tileset_id"]
        self.events = att["@events"]
        self.encounter_step: int = att["@encounter_step"]
        self.encounter_list = att["@encounter_list"]
        self.bgm = BGX(att["@bgm"])
        self.bgs = BGX(att["@bgs"])
        self.autoplay_bgm: bool = att["@autoplay_bgm"]
        self.autoplay_bgs: bool = att["@autoplay_bgs"]