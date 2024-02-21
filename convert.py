from pathlib import Path
from PSDKDataLoader import PSDKDataLoader
from ldtk.Ldtk import Ldtk
import sys

PROJECT_PATH = Path(sys.argv[1])

ldtk = Ldtk()
loader = PSDKDataLoader(PROJECT_PATH)

l = loader.get_map_by_filename("Map004.rxdata")
ldtk.add_level(l, "testimappiuus")
ldtk.save()
# for id, level in loader.iter_maps():
#     print(id)
#     print(level.data)
