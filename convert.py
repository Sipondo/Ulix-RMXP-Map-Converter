from pathlib import Path
from PSDKDataLoader import PSDKDataLoader
from ldtk.Ldtk import Ldtk
import sys

WORLD_FILE = Path("ldtk/world.ldtk")
PROJECT_PATH = Path(sys.argv[1])

ldtk = Ldtk(WORLD_FILE)
ldtk._json.external_levels = True

loader = PSDKDataLoader(PROJECT_PATH)

l = loader.get_map_by_filename("Map004.rxdata")
ldtk.add_level(l, "testimappiuus")
ldtk.save(path=Path("world"))
# for id, level in loader.iter_maps():
#     print(id)
#     print(level.data)
